import json
import os
from collections import OrderedDict
from typing import Callable, Dict, List, Optional

import click
import lsjsonclasses
import pydash
from lsrestclient import LsRestClient
from pydantic import BaseModel
from pydantic_db_backend_common.pagination import pagination_convert_response_list
from pydantic_db_backend_common.pydantic import PaginationResponseModel

from eventix import __version__
from eventix.pydantic.task import TEventixTask


class CLIContext(BaseModel):
    client: LsRestClient
    namespace: Optional[str]

    class Config:
        arbitrary_types_allowed = True


@click.group()
@click.version_option(__version__)
@click.option("-s", "--server", help="server url")
@click.option("-n", "--namespace", help="namespace")
@click.option("--test-client", is_flag=True, default=False)
@click.pass_context
def cli(ctx, server: str = None, namespace: str = None, test_client: bool = False):
    if not test_client:
        LsRestClient(base_url=server, name="eventix")
    ctx.obj = CLIContext(namespace=namespace, client=LsRestClient.client("eventix"))


# noinspection PyUnusedLocal
@cli.group("get")
@click.pass_context
def cli_get(ctx):
    pass


@cli_get.command("tasks")
@click.option("--limit", "limit", default=10, type=int)
@click.option("--skip", "skip", default=0, type=int)
@click.option("--status", "status", default="scheduled", type=str)
@click.pass_context
def cli_get_tasks(ctx, skip: int, limit: int, status: str | None = None):
    namespace = ctx.obj.namespace

    body = dict(skip=skip, limit=limit)

    if status is not None:
        body |= dict(status=status)

    if namespace is not None:
        body |= dict(namespace=namespace)

    # pprint(body)

    r = ctx.obj.client.put("/tasks/by_status", body=body)
    if r.status_code == 200:
        response = PaginationResponseModel.model_validate(r.json())
        tasks = pagination_convert_response_list(response, TEventixTask)

        # pv = r.json()
        # max_result = pydash.default_to(pydash.get(pv, "max_results"), 0)

        start = response.skip + 1
        end = (response.skip * response.limit) + response.limit
        if response.max_results < end:
            end = response.max_results

        pagination_result = f"{start}-{end} of {response.max_results}"

        if len(tasks) != 0:
            entries = [
                OrderedDict(
                    NAMESPACE=task.namespace,
                    UID=task.uid,
                    TASK=task.task,
                    STATUS=task.status,
                    IDENTIFIER="",
                )
                for task in tasks
            ]
            print_table(entries, click.echo)

            click.echo(f"Results {pagination_result}")
        else:
            click.echo("No result")

    else:
        raise click.ClickException(r.content)


@cli_get.command("task")
@click.option("--error-only", is_flag=True, default=False)
@click.argument("uid")
@click.pass_context
def cli_get_task(ctx, uid: str, error_only: bool):
    r = ctx.obj.client.get("/task/{uid}", params=dict(uid=uid))
    if r.status_code == 200:
        data = r.json()
        status = data.get("status", None)
        if error_only and status in ["retry", "error"]:
            result = pydash.get(data, "result", None)
            if isinstance(result, dict):
                error_class = pydash.get(result, "error_class", None)
            else:
                error_class = None

            click.echo(f"ERROR_CLASS: {error_class}")
            if error_class == "LSoftException":
                error_dict = lsjsonclasses.LSoftJSONDecoder.loads(result["error_message"])
                error = pydash.get(error_dict, "detail.ERROR", None)
                traceback_str = pydash.get(error_dict, "detail.TRACEBACK", None)
                click.echo("ERROR:")
                click.echo(error)
                click.echo("TRACEBACK:")
                click.echo(traceback_str)
            else:
                print_dict_to_json(result, click.echo)

        else:
            print_dict_to_json(data, click.echo)

    else:
        raise click.ClickException(r.content)


# noinspection PyUnusedLocal
@cli.group("reschedule")
@click.pass_context
def cli_reschedule(ctx):
    pass


@cli_reschedule.command("task")
@click.argument("uid")
# @click.option("--eta") look https://www.markhneedham.com/blog/2019/07/29/python-click-date-parameter-type/
@click.pass_context
def cli_reschedule_task(ctx, uid: str):
    r = ctx.obj.client.get("/task/{uid}/reschedule", params=dict(uid=uid))
    if r.status_code == 200:
        click.echo(f"Rescheduled task {uid}")
    else:
        raise click.ClickException(r.content)


# noinspection PyUnusedLocal
@cli.group("delete")
@click.pass_context
def cli_delete(ctx):
    pass


@cli_delete.command("task")
@click.argument("uid")
@click.pass_context
def cli_delete_task(ctx, uid: str):
    r = ctx.obj.client.delete("/task/{uid}", params=dict(uid=uid))
    if r.status_code == 200:
        click.echo(f"Deleted task {uid}")
    else:
        raise click.ClickException(r.content)


@cli.command("dump")
@click.argument("output_directory", required=True)
@click.pass_context
def cli_dump(ctx, output_directory: str):
    os.makedirs(output_directory, exist_ok=True)
    click.echo(f"Dumping to {output_directory}")
    idx = 0
    while True:
        r = ctx.obj.client.put("/tasks/dump", body=dict(limit=10, skip=idx))

        if r.status_code == 200:
            response = PaginationResponseModel.model_validate(r.json())

            if len(response.data) == 0:
                break
            for task in pagination_convert_response_list(response, TEventixTask):
                idx += 1
                click.echo(f"[{idx}] Exporting {task.uid}... ", nl=False)
                fname = os.path.join(output_directory, f"{task.uid}.json")
                # click.echo(f"{fname}...")
                with open(fname, "w", encoding="utf8") as fd:
                    json.dump(
                        task.model_dump(),
                        fd,
                        indent=2,
                        cls=lsjsonclasses.LSoftJSONEncoder,
                    )
                click.echo("done.")
        else:
            raise click.ClickException(r.content)


@cli.command("restore")
@click.argument("input_directory", required=True)
@click.option("--delete-processed", is_flag=True, default=False)
@click.pass_context
def cli_restore(ctx, input_directory: str, delete_processed: bool | None = False):
    click.echo(f"Restoring from {input_directory}")
    filenames = os.listdir(input_directory)
    num_max = len(filenames)
    for idx, filename in enumerate(filenames):
        fpath = os.path.join(input_directory, filename)
        with open(fpath, "r", encoding="utf8") as fd:
            data = json.load(fd, cls=lsjsonclasses.LSoftJSONDecoder)

        click.echo(f"[{idx + 1}/{num_max}] Restoring task {data['uid']} ...", nl=False)
        r = ctx.obj.client.put("/task/{uid}", params=dict(uid=data["uid"]), body=data)
        if r.status_code == 200:
            click.echo("done.")
            if delete_processed:
                os.unlink(fpath)
        else:
            raise click.ClickException(r.content)


def print_dict_to_json(data: dict, print_func: Callable = print):
    j = lsjsonclasses.LSoftJSONEncoder.dumps(data, indent=2)
    print_func(j)


def print_table(tdata: List[Dict[str, str]], print_func: Callable = print):
    if len(tdata) == 0:
        return

    keys = list(tdata[0].keys())
    sizes = {}
    lines = []
    for key in keys:
        sizes[key] = max(pydash.concat([len(key)], [len(x[key]) for x in tdata]))

    tdata = pydash.concat([{k: k for k in keys}], tdata)
    for td in tdata:
        line = ""
        for key in keys:
            line += "{text:{width}} ".format(text=td[key], width=sizes[key])
        lines.append(line.strip())

    for line in lines:
        print_func(line)


if __name__ == "__main__":
    cli()

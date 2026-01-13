import os

import pydash
import pytest
from click.testing import CliRunner

from eventix.cli import cli
from eventix.pydantic.task import TEventixTask
from tests.fixtures.app_client import cli_client
from tests.fixtures.backend import cleanup

base_params = ["-s", "http://localhost:9000", "--test-client"]


@cli_client
@pytest.mark.parametrize("params", [([]), (["--status", "retry"])])
def test_cli_get_tasks(client, params):
    with cleanup(client):
        t1 = TEventixTask(task="demotask")
        client.post_instance(t1)
        runner = CliRunner()
        # noinspection PyTypeChecker
        result = runner.invoke(cli, pydash.concat(base_params, ["get", "tasks"], params))
        print(result.output)
        assert result.exit_code == 0


@cli_client
@pytest.mark.parametrize(
    "params",
    [
        # ([]),
        (["--error-only"]),
    ],
)
def test_cli_get_task(client, params):
    with cleanup(client):
        t1 = TEventixTask(task="demotask")
        client.post_instance(t1)
        runner = CliRunner()
        # noinspection PyTypeChecker
        result = runner.invoke(cli, pydash.concat(base_params, ["get", "task", t1.uid], params))
        print(result.output)
        assert result.exit_code == 0


@cli_client
def test_cli_delete_task(client):
    with cleanup(client):
        t1 = TEventixTask(task="demotask")
        client.post_instance(t1)

        runner = CliRunner()
        # noinspection PyTypeChecker
        result = runner.invoke(cli, pydash.concat(base_params, ["delete", "task", t1.uid]))
        print(result.output)
        assert result.exit_code == 0


@cli_client
def test_cli_reschedule_task(client):
    with cleanup(client):
        t1 = TEventixTask(task="demotask", status="error")
        client.post_instance(t1)
        runner = CliRunner()
        # noinspection PyTypeChecker
        result = runner.invoke(cli, pydash.concat(base_params, ["reschedule", "task", t1.uid]))
        print(result.output)
        assert result.exit_code == 0


@cli_client
def test_cli_dump(client, generate_many_tasks, tmp_path):
    with cleanup(client):
        generate_many_tasks(
            client,
            {
                "done": 20,
                "error": 3,
                "scheduled": 10,
                "retry": 5,
                "processing": 2,
            },
        )
        runner = CliRunner()
        # noinspection PyTypeChecker
        result = runner.invoke(cli, pydash.concat(base_params, ["dump", str(tmp_path)]))
        print(result.output)
        assert result.exit_code == 0


@cli_client
def test_cli_restore(client, generate_many_tasks, tmp_path):
    with cleanup(client):
        generate_many_tasks(
            client,
            {
                "done": 20,
                "error": 3,
                "scheduled": 10,
                "retry": 5,
                "processing": 2,
            },
        )
        runner = CliRunner()
        # noinspection PyTypeChecker
        result = runner.invoke(cli, pydash.concat(base_params, ["dump", str(tmp_path)]))
        print(result.output)
        assert result.exit_code == 0

    with cleanup(client):
        result = runner.invoke(
            cli,
            pydash.concat(base_params, ["restore", str(tmp_path), "--delete-processed"]),
        )
        print(result.output)
        assert result.exit_code == 0

    filenames = os.listdir(tmp_path)
    assert len(filenames) == 0

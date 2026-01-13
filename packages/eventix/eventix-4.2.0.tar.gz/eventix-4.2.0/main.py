import logging
import sys
from contextlib import asynccontextmanager
from pprint import pprint

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from eventix import __version__
from eventix.functions.event import init_triggers
from eventix.functions.fastapi import ErrorMiddleware, init_backend
from eventix.functions.relay import init_relay
from eventix.pydantic.settings import EventixServerSettings
from eventix.router import default, event, metrics, task, tasks, namespaces

log = logging.getLogger(__name__)

# disable log of: Using selector: EpollSelector
logging.getLogger("asyncio").setLevel(logging.WARNING)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="[%(levelname)8s] %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("init...")
    init_backend()
    init_relay()
    init_triggers()
    yield


app = FastAPI(lifespan=lifespan)
app.title = "eventix-api"
app.version = __version__

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    ErrorMiddleware,
)

app.include_router(task.router)
app.include_router(tasks.router)
app.include_router(event.router)
app.include_router(metrics.router)
app.include_router(namespaces.router)
app.include_router(default.router)

if __name__ == "__main__":
    load_dotenv(".env.local")
    settings = EventixServerSettings()
    port = settings.eventix_api_port
    pprint(dict(settings), indent=2, compact=True)
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=True)

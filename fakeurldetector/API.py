import time

from fastapi import FastAPI, Request, Security
from fastapi.middleware.cors import CORSMiddleware

from fakeurldetector import DATABASE, __version__

from .helpers.api_auth import verify_api_key
from .routers import *
from fakeurldetector import Config, LOGGER


FakeURLDetection = FastAPI(
    title="Fake URL Detection",
    version=__version__,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/fake_url.json",
    dependencies=[Security(verify_api_key)],
)


@FakeURLDetection.on_event("startup")
async def database_dir_init():
    if Config.OPEN_PAGE_RANK_API_KEY == -1 or Config.OPEN_PAGE_RANK_API_KEY is None:
        LOGGER.error("Cant Start the Program Without the Open Page Rank API Key")
        exit(1)
    await DATABASE.connect()


@FakeURLDetection.on_event("shutdown")
async def database_close():
    await DATABASE.disconnect()


#
@FakeURLDetection.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 3)) + " ms"
    return response


FakeURLDetection.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
FakeURLDetection.include_router(UsersRouter)
FakeURLDetection.include_router(FakeDetectionRouter)

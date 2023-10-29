from uuid import UUID, uuid4

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from fakeurldetector import DATABASE
from ..helpers.database import users
from ..helpers.models import UserCreationIn, UserCreationResponse, UserGet, UsersGetAll

UsersRouter = APIRouter(
    prefix="/users",
    tags=["User Sessions"],
    responses={404: {"error": "Not found"}},
)


@UsersRouter.post(
    "/create", response_class=ORJSONResponse, response_model=UserCreationResponse
)
async def create_user(user_config: UserCreationIn):
    try:
        _uuid = uuid4()
        _q = users.insert().values(
            uuid=str(_uuid),
            name=user_config.name,
            client=user_config.client,
            bot_token=user_config.bot_token,
            telegram_user_id=user_config.telegram_user_id
        )
        await DATABASE.execute(_q)
        return ORJSONResponse(content={"user_uuid": _uuid})
    except Exception as e:
        print(e)


@UsersRouter.delete(
    "/delete/{uuid}",
    response_class=ORJSONResponse,
    response_model=UserCreationResponse,
)
async def delete_user(uuid: UUID):
    try:
        _q = users.delete().where(users.c.uuid == str(uuid))
        await DATABASE.execute(_q)
        return ORJSONResponse(content={"user_uuid": uuid})
    except Exception as e:
        print(e)


@UsersRouter.get(
    "/get/{uuid}", response_class=ORJSONResponse, response_model=UserGet
)
async def get_user(uuid: UUID):
    try:
        _session_q = users.select().where(users.c.uuid == str(uuid))
        _session = await DATABASE.fetch_one(_session_q)
        return ORJSONResponse(content=jsonable_encoder({_session}))
    except Exception as e:
        print(e)


@UsersRouter.get("/all", response_class=ORJSONResponse, response_model=UsersGetAll)
async def get_all_users():
    try:
        _all = users.select()
        _data = await DATABASE.fetch_all(_all)
        return ORJSONResponse(
            content={"sessions_available": [jsonable_encoder(data) for data in _data]}
        )
    except Exception as e:
        print(e)


@UsersRouter.delete("/all", response_class=ORJSONResponse)
async def delete_all_sessions():
    try:
        _q = users.delete()
        await DATABASE.execute(_q)
        return ORJSONResponse(content={"result": "Deleted all the sessions"})
    except Exception as e:
        print(e)
from tooi.api import statuses
from tooi.entities import Status, StatusSource, Translation
from tooi.utils.from_dict import from_response


async def get(status_id: str) -> Status:
    response = await statuses.get(status_id)
    return await from_response(Status, response)


async def favourite(status_id: str) -> Status:
    response = await statuses.favourite(status_id)
    return await from_response(Status, response)


async def unfavourite(status_id: str) -> Status:
    response = await statuses.unfavourite(status_id)
    return await from_response(Status, response)


async def boost(status_id: str) -> Status:
    response = await statuses.boost(status_id)
    return await from_response(Status, response)


async def unboost(status_id: str) -> Status:
    response = await statuses.unboost(status_id)
    return await from_response(Status, response)


async def source(status_id: str) -> StatusSource:
    response = await statuses.source(status_id)
    return await from_response(StatusSource, response)


async def translate(status_id: str) -> Translation:
    response = await statuses.translate(status_id)
    return await from_response(Translation, response)

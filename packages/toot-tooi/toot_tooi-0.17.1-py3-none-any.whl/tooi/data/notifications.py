from tooi.api import notifications
from tooi.entities import Notification
from tooi.utils.from_dict import from_response


async def get(notification_id: str) -> Notification:
    response = await notifications.get(notification_id)
    return await from_response(Notification, response)

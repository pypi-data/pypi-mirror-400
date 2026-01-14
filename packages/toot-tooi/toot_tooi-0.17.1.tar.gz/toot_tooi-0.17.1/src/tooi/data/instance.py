import logging
from asyncio import gather
from dataclasses import dataclass
from typing import Any

from tooi.api import instance
from tooi.entities import ExtendedDescription, Instance, InstanceV2, InstanceV2ConfigurationStatuses
from tooi.utils.from_dict import from_response

logger = logging.getLogger(__name__)

UserPreferences = dict[str, Any]


@dataclass
class InstanceInfo:
    instance: Instance
    instance_v2: InstanceV2 | None
    extended_description: ExtendedDescription | None
    user_preferences: UserPreferences

    @property
    def status_config(self) -> InstanceV2ConfigurationStatuses:
        if self.instance_v2:
            return self.instance_v2.configuration.statuses
        else:
            # Mastodon default values
            return InstanceV2ConfigurationStatuses(
                max_characters=500,
                max_media_attachments=4,
                characters_reserved_per_url=23,
            )

    def get_federated(self) -> bool | None:
        """
        posting:default:federation is used by Hometown's local-only
        (unfederated) posts feature. We treat this as a 3-way switch; if it's
        not present, the instance doesn't support local-only posts at all,
        otherwise it indicates if the post should be federated by default.
        """
        return self.user_preferences.get("posting:default:federation")

    def get_default_visibility(self) -> str:
        """Returns the default visibility from user's preferences."""
        return self.user_preferences.get("posting:default:visibility", "public")

    def get_always_show_sensitive(self) -> bool:
        """
        User's preference whether sensitive posts should be expanded by defualt.
        """
        return self.user_preferences.get("reading:expand:spoilers", False)

    @property
    def streaming_url(self) -> str | None:
        if self.instance_v2:
            return self.instance_v2.configuration.urls.streaming

        if self.instance:
            return self.instance.urls.streaming_api


async def get_instance_info() -> InstanceInfo:
    instance_v1, instance_v2, extended_description, user_preferences = await gather(
        _get_instance_v1(),
        _get_instance_v2(),
        _get_extended_description(),
        _get_user_preferences(),
    )

    return InstanceInfo(
        instance_v1,
        instance_v2,
        extended_description,
        user_preferences,
    )


async def _get_instance_v1() -> Instance:
    # Instance v1 should be implemented by all clients
    # Throw if it's not available
    response = await instance.server_information()
    response.raise_for_status()
    return await from_response(Instance, response)


async def _get_instance_v2() -> InstanceV2 | None:
    try:
        response = await instance.server_information_v2()
        response.raise_for_status()
        return await from_response(InstanceV2, response)
    except Exception:
        logger.exception("Failed loading instance v2")


async def _get_extended_description() -> ExtendedDescription | None:
    try:
        response = await instance.extended_description()
        response.raise_for_status()
        return await from_response(ExtendedDescription, response)
    except Exception:
        logger.exception("Failed loading extended description")


async def _get_user_preferences() -> UserPreferences:
    try:
        response = await instance.user_preferences()
        response.raise_for_status()
        return await response.json()
    except Exception:
        logger.exception("Failed loading user preferences")
        return {}

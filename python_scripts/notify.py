ATTR_ANDROID = "android"
ATTR_IOS = "ios"
ATTR_SERVICE = "service"
ATTR_TYPE = "type"

USER_EDYTA = "edyta"
USER_MACIEK = "maciek"

USERS = [USER_EDYTA, USER_MACIEK]

NOTIFY_SERVICE_EDYTA = "notify.mobile_app_iphone_8_plus"
NOTIFY_SERVICE_MACIEK = "notify.mobile_app_oneplus_6"

SERVICES = {
    USER_EDYTA: {ATTR_TYPE: ATTR_IOS, ATTR_SERVICE: NOTIFY_SERVICE_EDYTA},
    USER_MACIEK: {ATTR_TYPE: ATTR_ANDROID, ATTR_SERVICE: NOTIFY_SERVICE_MACIEK},
}

CONF_ACTIONS = "actions"
CONF_IMAGE = "image"
CONF_MESSAGE = "message"
CONF_PRIORITY = "priority"
CONF_TAG = "tag"
CONF_TITLE = "title"
CONF_URL = "url"

PRIORITY_NORMAL = "normal"
PRIORITY_HIGH = "high"

PRIORITIES = [PRIORITY_NORMAL, PRIORITY_HIGH]

priority = PRIORITY_NORMAL
if data.get(CONF_PRIORITY):
    priority = data.get(CONF_PRIORITY)
if not priority in PRIORITIES:
    raise ValueError("Wrong value for priority argument")

image = data.get(CONF_IMAGE)
message = data.get(CONF_MESSAGE)
tag = data.get(CONF_TAG)
title = data.get(CONF_TITLE)
url = data.get(CONF_URL)
actions = data.get(CONF_ACTIONS)

if not title:
    raise ValueError("Title argument is empty")
if not message:
    raise ValueError("Message argument is empty")

for user in USERS:
    notify_user = False
    if data.get(user):
        notify_user = data.get(user)
    if not isinstance(notify_user, bool):
        raise ValueError(f"Wrong value for {user} argument")

    if notify_user:
        if SERVICES[user][ATTR_TYPE] == ATTR_IOS:
            service_data = {"title": title, "message": message}
            if image:
                if not service_data.get("data"):
                    service_data["data"] = {}
                service_data["data"]["attachment"] = {}
                service_data["data"]["attachment"]["url"] = image
                service_data["data"]["attachment"]["content-type"] = "jpg"
                service_data["data"]["attachment"]["hide-thumbnail"] = "false"
            if tag:
                if not service_data.get("data"):
                    service_data["data"] = {}
                service_data["data"]["apns_headers"] = {}
                service_data["data"]["apns_headers"]["apns-collapse-id"] = tag

            logger.debug(
                f"service: {SERVICES[user][ATTR_SERVICE]}, data: {service_data}"
            )

            hass.services.call(
                SERVICES[user][ATTR_SERVICE].split(".")[0],
                SERVICES[user][ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

        if SERVICES[user][ATTR_TYPE] == ATTR_ANDROID:
            service_data = {
                "title": title,
                "message": message,
                "data": {"priority": priority},
            }
            if actions:
                service_data["data"]["actions"] = actions
            if tag:
                service_data["data"]["tag"] = tag
            if url:
                service_data["data"]["url"] = url
            if image:
                service_data["data"]["image"] = image

            logger.debug(
                f"service: {SERVICES[user][ATTR_SERVICE]}, data: {service_data}"
            )

            hass.services.call(
                SERVICES[user][ATTR_SERVICE].split(".")[0],
                SERVICES[user][ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

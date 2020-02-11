ATTR_ANDROID = "android"
ATTR_FRONTEND = "frontend"
ATTR_IOS = "ios"
ATTR_SMS = "sms"
ATTR_SERVICE = "service"
ATTR_TYPE = "type"

CONF_ACTIONS = "actions"
CONF_DEVELOP = "develop"
CONF_IMAGE = "image"
CONF_MESSAGE = "message"
CONF_PRIORITY = "priority"
CONF_RECIPIENT = "recipient"
CONF_SERVICES = "services"
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
services = data.get(CONF_SERVICES)
# if not isinstance(services, list):
#     raise ValueError(f"Argument services should be a list")
develop = False
if data.get(CONF_DEVELOP) == True:
    develop = data.get(CONF_DEVELOP)

if not title:
    raise ValueError("Title argument is empty")
if not message:
    raise ValueError("Message argument is empty")

for item in services:
    if item[ATTR_TYPE] == ATTR_IOS:
        service_data = {"title": title, "message": message}
        if image:
            if not service_data.get("data"):
                service_data["data"] = {}
            service_data["data"]["attachment"] = {}
            service_data["data"]["attachment"]["url"] = image
            if "jpg" in image or "jpeg" in image:
                service_data["data"]["attachment"]["content-type"] = "jpg"
            if "png" in image:
                service_data["data"]["attachment"]["content-type"] = "png"
            service_data["data"]["attachment"]["hide-thumbnail"] = "false"
        if tag:
            if not service_data.get("data"):
                service_data["data"] = {}
            service_data["data"]["apns_headers"] = {}
            service_data["data"]["apns_headers"]["apns-collapse-id"] = tag

        logger.error(
            f"service: {item[ATTR_SERVICE]}, data: {service_data}"
        )

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

    if item[ATTR_TYPE] == ATTR_ANDROID:
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

        logger.error(
            f"service: {item[ATTR_SERVICE]}, data: {service_data}"
        )

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

    if item[ATTR_TYPE] == ATTR_FRONTEND:
        service_data = {"title": title, "message": message}
        if tag:
            service_data["notification_id"] = tag

        logger.error(
            f"service: {item[ATTR_SERVICE]}, data: {service_data}"
        )

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

    if item[ATTR_TYPE] == ATTR_SMS:
        service_data = {"message": message, "recipient": item[CONF_RECIPIENT]}

        logger.error(
            f"service: {item[ATTR_SERVICE]}, data: {service_data}"
        )

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

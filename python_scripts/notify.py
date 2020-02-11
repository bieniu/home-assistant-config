NOTIFY_SERVICE_EDYTA = "notify.mobile_app_iphone_8_plus"
NOTIFY_SERVICE_MACIEK = "notify.mobile_app_oneplus_6"

CONF_ACTIONS = "actions"
CONF_IMAGE = "image"
CONF_MESSAGE = "message"
CONF_PRIORITY = "priority"
CONF_TAG = "tag"
CONF_TITLE = "title"
CONF_URL = "url"

USER_EDYTA = "edyta"
USER_MACIEK = "maciek"

PRIORITIES = ["normal", "high"]

priority = "normal"
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

edyta = False
if data.get(USER_EDYTA):
    edyta = data.get(USER_EDYTA)
if not isinstance(edyta, bool):
    raise ValueError("Wrong value for edyta argument")

maciek = False
if data.get(USER_MACIEK):
    maciek = data.get(USER_MACIEK)
if not isinstance(maciek, bool):
    raise ValueError("Wrong value for maciek argument")

if edyta:
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

    logger.debug(f"service: {NOTIFY_SERVICE_EDYTA}, data: {service_data}")

    hass.services.call(
        NOTIFY_SERVICE_EDYTA.split(".")[0],
        NOTIFY_SERVICE_EDYTA.split(".")[1],
        service_data,
        False,
    )

if maciek:
    service_data = {"title": title, "message": message, "data": {"priority": priority}}
    if actions:
        service_data["data"]["actions"] = actions
    # if tag:
    #     service_data["data"]["tag"] = tag
    if url:
        service_data["data"]["url"] = url
    if image:
        service_data["data"]["image"] = image

    logger.debug(f"service: {NOTIFY_SERVICE_MACIEK}, data: {service_data}")

    hass.services.call(
        NOTIFY_SERVICE_MACIEK.split(".")[0],
        NOTIFY_SERVICE_MACIEK.split(".")[1],
        service_data,
        False,
    )

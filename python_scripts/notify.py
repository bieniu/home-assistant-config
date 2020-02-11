"""
service: python_script.notify
data:
  title: "Notification title"
  tag: "unique-tag"
  message: "Notification message"
  image: "https://test.xy/image.png"
  services:
    - service: notify.mobile_app_iphone
      type: "ios"
    - service: notify.mobile_app_oneplus
      type: "android"
    - service: persistent_notification.create
      type: "frontend"
    - service: notify.sms
      type: "sms"
      recipient: "+48123456789"
"""
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

title = data.get(CONF_TITLE)
message = data.get(CONF_MESSAGE)
if not title:
    raise ValueError("`title` argument is empty")
if not message:
    raise ValueError("`message` argument is empty")

services = data.get(CONF_SERVICES)
if not services:
    raise ValueError("Argument `services` should be a list")
if len(services) < 1:
    raise ValueError("Argument `services` should be a list")

priority = PRIORITY_NORMAL
if data.get(CONF_PRIORITY):
    priority = data.get(CONF_PRIORITY)
if not priority in PRIORITIES:
    raise ValueError("Wrong value for `priority` argument")

actions = data.get(CONF_ACTIONS)
image = data.get(CONF_IMAGE)
tag = data.get(CONF_TAG)
url = data.get(CONF_URL)

develop = False
if data.get(CONF_DEVELOP) == True:
    develop = data.get(CONF_DEVELOP)

for item in services:
    if item[ATTR_TYPE] == ATTR_IOS:
        service_data = {"title": title, "message": message}
        if image:
            if not service_data.get("data"):
                service_data["data"] = {}
            service_data["data"]["attachment"] = {}
            service_data["data"]["attachment"]["url"] = image
            service_data["data"]["attachment"]["hide-thumbnail"] = "false"
        if tag:
            if not service_data.get("data"):
                service_data["data"] = {}
            service_data["data"]["apns_headers"] = {}
            service_data["data"]["apns_headers"]["apns-collapse-id"] = tag

        logger.debug(f"service: {item[ATTR_SERVICE]}, data: {service_data}")

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

        logger.debug(f"service: {item[ATTR_SERVICE]}, data: {service_data}")

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

        logger.debug(f"service: {item[ATTR_SERVICE]}, data: {service_data}")

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

    if item[ATTR_TYPE] == ATTR_SMS:
        recipient = item.get(CONF_RECIPIENT)
        if not recipient:
            raise ValueError("`recipient` argument is empty")
        service_data = {"message": message, "recipient": recipient}

        logger.debug(f"service: {item[ATTR_SERVICE]}, data: {service_data}")

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

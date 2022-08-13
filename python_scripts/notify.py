"""
service: python_script.notify
data:
  title: "Notification title"
  message: "Notification message"
  tag: "unique-tag"
  image: "https://test.xy/image.png"
  color: "red"
  url: "https://example.com"
  priority: "high"
  group: "group-1"
  actions:
    - title: "Action title"
      action: "ACTION"
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
ATTR_ACTIONS = "actions"
ATTR_ANDROID = "android"
ATTR_BADGE = "badge"
ATTR_APNS_COLLAPSE_ID = "apns-collapse-id"
ATTR_APNS_HEADERS = "apns_headers"
ATTR_ATTACHMENT = "attachment"
ATTR_CLICK_ACTION = "clickAction"
ATTR_COLOR = "color"
ATTR_DATA = "data"
ATTR_ENTITY_ID = "entity_id"
ATTR_FALSE = False
ATTR_FRONTEND = "frontend"
ATTR_HIDE_THUMBNAIL = "hide-thumbnail"
ATTR_GROUP = "group"
ATTR_IMAGE = "image"
ATTR_IOS = "ios"
ATTR_MESSAGE = "message"
ATTR_NOTIFICATION_ID = "notification_id"
ATTR_PRIORITY = "priority"
ATTR_PUSH = "push"
ATTR_RECIPIENT = "recipient"
ATTR_SMS = "sms"
ATTR_SERVICE = "service"
ATTR_SOUND = "sound"
ATTR_TAG = "tag"
ATTR_THREAD_ID = "thread-id"
ATTR_TITLE = "title"
ATTR_TTL = "ttl"
ATTR_TYPE = "type"
ATTR_URL = "url"

CONF_ACTIONS = "actions"
CONF_COLOR = "color"
CONF_DEVELOP = "develop"
CONF_ENTITY_ID = "entity_id"
CONF_GROUP = "group"
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
group = data.get(CONF_GROUP)
image = data.get(CONF_IMAGE)
entity_id = data.get(CONF_ENTITY_ID)
tag = data.get(CONF_TAG)
url = data.get(CONF_URL)
color = data.get(CONF_COLOR)

develop = False
if data.get(CONF_DEVELOP) == True:
    develop = data.get(CONF_DEVELOP)

for item in services:
    if item[ATTR_TYPE] == ATTR_IOS:
        service_data = {ATTR_TITLE: title, ATTR_MESSAGE: message}
        service_data[ATTR_DATA] = {}
        service_data[ATTR_DATA][ATTR_PUSH] = {}
        service_data[ATTR_DATA][ATTR_PUSH][ATTR_BADGE] = 1
        service_data[ATTR_DATA][ATTR_PUSH][ATTR_SOUND] = "Warsaw_Haptic.caf"

        if image:
            service_data[ATTR_DATA][ATTR_ATTACHMENT] = {}
            service_data[ATTR_DATA][ATTR_ATTACHMENT][ATTR_URL] = image
            service_data[ATTR_DATA][ATTR_ATTACHMENT][ATTR_HIDE_THUMBNAIL] = ATTR_FALSE
        if group:
            service_data[ATTR_DATA][ATTR_PUSH][ATTR_THREAD_ID] = group
        if tag:
            service_data[ATTR_DATA][ATTR_APNS_HEADERS] = {}
            service_data[ATTR_DATA][ATTR_APNS_HEADERS][ATTR_APNS_COLLAPSE_ID] = tag
        if url:
            service_data[ATTR_DATA][ATTR_URL] = url
        if entity_id:
            service_data[ATTR_DATA][ATTR_ENTITY_ID] = entity_id

        logger.debug(f"service: {item[ATTR_SERVICE]}, data: {service_data}")

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

    if item[ATTR_TYPE] == ATTR_ANDROID:
        service_data = {ATTR_TITLE: title, ATTR_MESSAGE: message}
        if priority == PRIORITY_HIGH:
            if not service_data.get(ATTR_DATA):
                service_data[ATTR_DATA] = {}
            service_data[ATTR_DATA][ATTR_PRIORITY] = priority
            service_data[ATTR_DATA][ATTR_TTL] = 0
        if actions:
            if not service_data.get(ATTR_DATA):
                service_data[ATTR_DATA] = {}
            service_data[ATTR_DATA][ATTR_ACTIONS] = actions
        if group:
            if not service_data.get(ATTR_DATA):
                service_data[ATTR_DATA] = {}
            service_data[ATTR_DATA][ATTR_GROUP] = group
        if tag:
            if not service_data.get(ATTR_DATA):
                service_data[ATTR_DATA] = {}
            service_data[ATTR_DATA][ATTR_TAG] = tag
        if url:
            if not service_data.get(ATTR_DATA):
                service_data[ATTR_DATA] = {}
            service_data[ATTR_DATA][ATTR_CLICK_ACTION] = url
        if color:
            if not service_data.get(ATTR_DATA):
                service_data[ATTR_DATA] = {}
            service_data[ATTR_DATA][ATTR_COLOR] = color
        if image:
            if not service_data.get(ATTR_DATA):
                service_data[ATTR_DATA] = {}
            service_data[ATTR_DATA][ATTR_IMAGE] = image

        logger.debug(f"service: {item[ATTR_SERVICE]}, data: {service_data}")

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

    if item[ATTR_TYPE] == ATTR_FRONTEND:
        if image:
            message = message + " "
            message = message + image
        if url:
            message = message + " "
            message = message + url
        service_data = {ATTR_TITLE: title, ATTR_MESSAGE: message}
        if tag:
            service_data[ATTR_NOTIFICATION_ID] = tag

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
        if image:
            message = message + " "
            message = message + image
        if url:
            message = message + " "
            message = message + url
        service_data = {ATTR_MESSAGE: message, ATTR_RECIPIENT: recipient}

        logger.debug(f"service: {item[ATTR_SERVICE]}, data: {service_data}")

        if not develop:
            hass.services.call(
                item[ATTR_SERVICE].split(".")[0],
                item[ATTR_SERVICE].split(".")[1],
                service_data,
                False,
            )

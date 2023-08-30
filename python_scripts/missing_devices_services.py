"""Prepare notification about missing devices/services."""
EMPTY_VALUES = ("", "None")

raw_data = data.get("entities")
entities = []

for item in raw_data.split("|"):
    if not item:
        continue
    elements = item.strip().split("&")
    entities.append({"device_name": elements[0], "area": elements[1]})

message_elements = {}

for entity in entities:
    device_name = entity["device_name"]
    area = entity["area"]
    if device_name not in EMPTY_VALUES:
        if device_name in message_elements:
            continue
        if area in EMPTY_VALUES:
            message_elements[device_name] = f" - {device_name}"
        else:
            message_elements[device_name] = f" - {device_name}, {area}"

if message_elements:
    message = "\n".join(message_elements.values())
    service_data = {
        "title": "Niedostępne urządzenia/usługi",
        "message": f"Następujące urządzenia/usługi są niedostępne:\n{message}",
        "tag": "notification-watchman-missing-entities",
        "group": "other",
        "priority": "high",
        "services": [{"service": "notify.mobile_app_iphone_13", "type": "ios"}],
    }

    hass.services.call("python_script", "notify", service_data, False)

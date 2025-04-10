"""Prepare notification about unavailable devices/services."""
EMPTY_VALUES = ("", "None", None)
ENTRY_NAME = "entry_name"
AREA = "area"

raw_data = data.get("entries")
entries = []

for item in raw_data.split("|"):
    if not item:
        continue
    elements = item.strip().split("@")
    entries.append({ENTRY_NAME: elements[0], AREA: elements[1]})

message_elements = {}

for entity in entries:
    entry_name = entity[ENTRY_NAME]
    area = entity[AREA]
    if entry_name not in EMPTY_VALUES:
        if entry_name in message_elements:
            continue
        if area in EMPTY_VALUES:
            message_elements[entry_name] = f" - {entry_name}"
        else:
            message_elements[entry_name] = f" - {entry_name}, {area.lower()}"

if message_elements:
    message = "\n".join(message_elements.values())
    service_data = {
        "title": "Niedostępne urządzenia/usługi",
        "message": f"Następujące urządzenia/usługi są niedostępne:\n{message}",
        "tag": "notification-missing-entries",
        "group": "other",
        "priority": "high",
        "services": [{"service": "notify.mobile_app_iphone_13", "type": "ios"}],
    }

    hass.services.call("python_script", "notify", service_data, False)

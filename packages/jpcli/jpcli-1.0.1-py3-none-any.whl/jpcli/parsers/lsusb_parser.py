import json
import re


def parse(command_output):
    lines = command_output.strip().split("\n")
    usb_data = []

    for line in lines:
        # Regex to capture bus, device, ID, and description
        match = re.match(r"Bus (\d+) Device (\d+): ID ([0-9a-fA-F]{4}:[0-9a-fA-F]{4}) (.+)", line)
        if match:
            entry = {
                "bus": match.group(1),
                "device": match.group(2),
                "id": match.group(3),
                "description": match.group(4)
            }
            usb_data.append(entry)
        else:
            # If line doesn't match, keep it raw
            usb_data.append({"raw": line})

    return json.dumps(usb_data, indent=2)

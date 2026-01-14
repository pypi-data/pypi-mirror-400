import json


def parse(command_output):
    lines = command_output.strip().split("\n")
    if not lines:
        return json.dumps([], indent=2)

    headers = lines[0].split()
    block_devices = []

    for line in lines[1:]:
        values = line.split(None, len(headers) - 1)  # Split only into len(headers) parts
        entry = {headers[i]: values[i] if i < len(values) else "N/A" for i in range(len(headers))}
        block_devices.append(entry)

    return json.dumps(block_devices, indent=2)

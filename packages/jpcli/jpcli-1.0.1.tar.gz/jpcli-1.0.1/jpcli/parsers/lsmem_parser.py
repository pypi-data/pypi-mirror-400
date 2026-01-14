import json


def parse(command_output):
    lines = command_output.splitlines()
    memory_blocks = []
    headers = []
    summary = {}

    # Extract headers from the first line
    if lines:
        headers = [header.strip() for header in lines[0].split() if header.strip()]
        lines = lines[1:]

    for line in lines:
        if not line.strip():  # Skip empty lines
            continue

        # Check if the line contains summary information
        if ':' in line:
            key, value = line.split(':')
            summary[key.strip().lower().replace(' ', '_')] = value.strip()
        else:
            values = [value.strip() for value in line.split() if value.strip()]
            if len(values) == len(headers):
                entry = {headers[i].lower(): values[i] for i in range(len(headers))}
                memory_blocks.append(entry)

    result = {
        "memory_blocks": memory_blocks,
        **summary
    }

    return json.dumps(result, indent=2)

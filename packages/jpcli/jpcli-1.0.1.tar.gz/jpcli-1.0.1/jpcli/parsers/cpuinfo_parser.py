import json


def parse(command_output):
    processors = []
    current_processor = {}

    lines = command_output.splitlines()
    for line in lines:
        if line.strip():  # Check if line is not empty
            key, value = line.split(':')
            key = key.strip().replace(' ', '_').lower()
            value = value.strip()
            if key == 'processor' and current_processor:
                # When a new processor block starts, append the previous one
                processors.append(current_processor)
                current_processor = {}
            current_processor[key] = value
        else:
            # Empty line indicates the end of one processor's info
            if current_processor:
                processors.append(current_processor)
                current_processor = {}

    # Append the last processor if exists
    if current_processor:
        processors.append(current_processor)

    return json.dumps(processors, indent=2)

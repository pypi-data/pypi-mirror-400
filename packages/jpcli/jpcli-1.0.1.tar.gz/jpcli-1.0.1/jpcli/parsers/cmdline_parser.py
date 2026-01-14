import json


def parse(command_output):
    # Split the command line output into individual parameters
    params = command_output.strip().split()

    # Create a dictionary to hold the parsed key-value pairs
    cmdline_dict = {}

    for param in params:
        if '=' in param:
            key, value = param.split('=', 1)
        else:
            key, value = param, None  # Handle flags with no value (e.g., "quiet")
        cmdline_dict[key] = value

    # Convert the dictionary to a JSON-formatted string
    return json.dumps(cmdline_dict, indent=2)

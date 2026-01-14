import json


def parse(command_output):
    """
    Parses the output of the lscpu command into a dictionary.

    Args:
    command_output (str): The string output from the lscpu command.

    Returns:
    dict: A dictionary with CPU properties as keys and their corresponding values.
    """
    cpu_info = {}
    lines = command_output.splitlines()
    for line in lines:
        if line.strip():  # Ensure the line is not empty
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                cpu_info[key] = value
    return json.dumps(cpu_info, indent=2)

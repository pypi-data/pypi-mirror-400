import json


def parse(command_output):
    """
    Parses the output of the uname -a command into a dictionary.

    Args:
    command_output (str): The string output from the uname -a command.

    Returns:
    str: A JSON-formatted string with system information.
    """
    uname_info = {}
    parts = command_output.split()

    if len(parts) >= 6:
        uname_info['system'] = parts[0]  # Kernel name
        uname_info['node'] = parts[1]    # Network node hostname
        uname_info['kernel'] = parts[2]  # Kernel release
        uname_info['kernel_version'] = parts[3]  # Kernel version
        uname_info['architecture'] = parts[4]  # Machine hardware name
        uname_info['processor'] = parts[5]  # Processor type

        # Additional fields if available
        if len(parts) > 6:
            uname_info['platform'] = parts[6]  # Platform type (e.g., GNU/Linux)
        if len(parts) > 7:
            uname_info['additional_info'] = ' '.join(parts[7:])  # Any remaining info

    return json.dumps(uname_info, indent=2)

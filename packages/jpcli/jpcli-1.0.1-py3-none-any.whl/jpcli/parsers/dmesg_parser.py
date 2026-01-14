import json


def parse(dmesg_output):
    """
    Parse the contents of dmesg output.
    """
    try:
        dmesg_lines = dmesg_output.strip().split('\n')
        dmesg_list = [{"message": line} for line in dmesg_lines]
        return json.dumps(dmesg_list, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "message": "Failed to parse dmesg output"}, indent=2)

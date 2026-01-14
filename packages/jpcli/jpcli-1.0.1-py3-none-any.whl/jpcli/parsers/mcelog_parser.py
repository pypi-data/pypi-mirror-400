import json


def parse(mcelog_output):
    """
    Parse the contents of mcelog output.
    """
    try:
        mcelog_lines = mcelog_output.strip().split('\n')
        mcelog_list = []
        for line in mcelog_lines:
            mcelog_list.append(line)
        return json.dumps(mcelog_list, indent=2)
    except Exception as e:
        return {"error": str(e), "message": "Failed to parse mcelog output"}

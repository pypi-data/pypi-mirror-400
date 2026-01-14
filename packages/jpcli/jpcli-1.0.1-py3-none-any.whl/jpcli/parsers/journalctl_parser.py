import json


def parse(journalctl_output):
    """
    Parse the contents of journalctl output.
    """
    try:
        # Split the output into individual lines
        journalctl_lines = journalctl_output.strip().split('\n')

        # Initialize a list to store JSON objects
        journalctl_list = []

        # Process each line
        for line in journalctl_lines:
            if line:  # Skip empty lines
                # Parse each line as JSON and append to the list
                journalctl_list.append(json.loads(line))

        # Convert the list of JSON objects to a pretty-printed JSON string
        return json.dumps(journalctl_list, indent=2)

    except json.JSONDecodeError as e:
        return json.dumps({"error": str(e), "message": "Failed to parse JSON from journalctl output"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "message": "Failed to parse journalctl output"}, indent=2)

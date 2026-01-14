import json


def parse(command_output):
    lines = command_output.splitlines()
    data = []
    headers = [header.strip() for header in lines[0].split()]

    for line in lines[1:]:
        if not line.strip():
            continue
        values = line.split()
        if len(values) < len(headers):
            # Handle lines with missing values
            values.extend([''] * (len(headers) - len(values)))
        entry = {headers[i]: values[i] for i in range(len(headers))}
        data.append(entry)

    return json.dumps(data, indent=2)

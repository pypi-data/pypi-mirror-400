import json


def parse(command_output):
    lines = command_output.strip().split("\n")
    headers = lines[0].split()
    memory_data = []

    for line in lines[1:]:
        values = line.split()
        category = values[0].strip(":")  # Extract "Mem" or "Swap"
        values = values[1:]  # Remove category from values

        # Ensure proper key-value matching
        if len(values) == len(headers):
            entry = {headers[i]: values[i] for i in range(len(headers))}
        else:
            entry = {headers[i]: values[i] if i < len(values) else "N/A" for i in range(len(headers))}

        entry["category"] = category  # Add category name separately
        memory_data.append(entry)

    return json.dumps(memory_data, indent=2)

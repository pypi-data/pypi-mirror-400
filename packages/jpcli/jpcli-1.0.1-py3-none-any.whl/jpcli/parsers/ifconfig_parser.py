import re
import json


def parse(ifconfig_output):
    """
    Parse the output of the `ifconfig` command.
    """
    interfaces = {}
    current_interface = None

    for line in ifconfig_output.splitlines():
        if not line.startswith(' '):
            if current_interface:
                interfaces[current_interface['name']] = current_interface
            match = re.match(r'(\S+): flags=.*', line)
            if match:
                current_interface = {
                    'name': match.group(1),
                    'inet': [],
                    'inet6': [],
                    'ether': None
                }
        elif current_interface:
            if 'inet ' in line:
                match = re.search(r'inet (\S+)', line)
                if match:
                    current_interface['inet'].append(match.group(1))
            elif 'inet6 ' in line:
                match = re.search(r'inet6 (\S+)', line)
                if match:
                    current_interface['inet6'].append(match.group(1))
            elif 'ether ' in line:
                match = re.search(r'ether (\S+)', line)
                if match:
                    current_interface['ether'] = match.group(1)

    if current_interface:
        interfaces[current_interface['name']] = current_interface

    return json.dumps(interfaces, indent=2)

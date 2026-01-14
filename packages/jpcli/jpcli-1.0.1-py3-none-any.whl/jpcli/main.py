
import argparse
import subprocess
import sys
from .parsers import lsmem_parser, free_parser, df_parser, lshw_parser, lscpu_parser, cpuinfo_parser, uname_parser, ifconfig_parser, cmdline_parser, os_release_parser, dmesg_parser, journalctl_parser, mcelog_parser, lsusb_parser, lsblk_parser


def run_command(command):

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"Command '{command}' failed with error: {result.stderr.decode()}")
    return result.stdout.decode()


def parse_command_output(command_output, parser_name):

    parsers = {
        'lsmem': lsmem_parser.parse,
        'free': free_parser.parse,
        'df': df_parser.parse,
        'lshw': lshw_parser.parse,
        'lscpu': lscpu_parser.parse,
        'cpuinfo': cpuinfo_parser.parse,
        'uname': uname_parser.parse,
        'ifconfig': ifconfig_parser.parse,
        'cmdline': cmdline_parser.parse,
        'os-release': os_release_parser.parse,
        'dmesg': dmesg_parser.parse,
        'journalctl': journalctl_parser.parse,
        'mcelog': mcelog_parser.parse,
        'lsusb': lsusb_parser.parse,
        'lsblk': lsblk_parser.parse,
    }
    if parser_name in parsers:
        return parsers[parser_name](command_output)
    else:
        raise ValueError(f"No parser found for {parser_name}")


def main():

    parser = argparse.ArgumentParser(description="Parse Linux command outputs into JSON")
    parser.add_argument('parser_name', help='The name of the parser to use')
    parser.add_argument('command', nargs='?', default=None, help='The Linux command to run (optional, reads from stdin if omitted)')
    args = parser.parse_args()

    if not args.command and not args.parser_name:
        print("Error: Parser is required when reading from stdin or command for stdout", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if args.command is None:
        args.command = args.parser_name

    result = jpcli(args.parser_name, args.command)
    print(result)


def jpcli(parser_name, command):

    if sys.stdin.isatty():
        # Not receiving piped data, execute the command
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            sys.exit(result.returncode)
        command_output = result.stdout
    else:
        command_output = sys.stdin.read()
        parser_name = command  # Use the command as the parser name

    return parse_command_output(command_output, parser_name)


if __name__ == '__main__':
    main()

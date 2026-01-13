import argparse

from reqst.client import Reqst


def parse_args():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "-f", 
        "--file",
        type=str,
        required=True,
        help="The JSON/YAML/YML file to read the request from.",
    )
    parser.add_argument(
        "-c",
        "--colorize",
        action='store_true',
        help="Colorize the output (stdout and stderr)."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    reqst = Reqst(args.colorize)
    reqst.send_request(args.file)
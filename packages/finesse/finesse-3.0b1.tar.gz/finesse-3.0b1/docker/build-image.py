#!/bin/python3

import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-cache",
        help="Disable using cache for building the docker image",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "PYTHON_VERSION",
        help="The python version to build the image with.",
        choices=["3.10", "3.11", "3.12"],
    )
    parser.add_argument(
        "FINESSE_REF",
        help="Optional argument specifying the finesse git reference. Defaults to 'develop'",
        nargs="?",
        default="develop",
    )
    args = parser.parse_args()
    print(
        f"Building finesse cython debugging image for Python {args.PYTHON_VERSION} and finesse reference {args.FINESSE_REF}"
    )
    cmd1 = f"docker build -t gdb-with-python:{args.PYTHON_VERSION} --build-arg PYTHON_VERSION={args.PYTHON_VERSION} -f gdb_python.Dockerfile ."
    print(cmd1)
    subprocess.run(cmd1, shell=True, check=True)
    cmd2 = f"docker build {'--no-cache' if args.no_cache else ''} -t finesse-cython-debug:{args.PYTHON_VERSION} --build-arg PYTHON_VERSION={args.PYTHON_VERSION} --build-arg FINESSE_REF={args.FINESSE_REF} ."
    print(cmd2)
    subprocess.run(cmd2, shell=True, check=True)


if __name__ == "__main__":
    main()

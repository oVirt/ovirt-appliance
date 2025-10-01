#!/usr/bin/python3

import os
import yaml
import argparse


def main():
    parser = argparse.ArgumentParser(prog="renderks")
    parser.add_argument("--data-dir", default="./data",
                        help="jinja2 environment directory")
    parser.add_argument("DISTRO", help="distro name")
    args = parser.parse_args()

    with open(os.path.join(args.data_dir, "distro-defs.yml")) as f:
        data = yaml.load(f)[args.DISTRO]

    print(data['boot-iso-url'])


if __name__ == '__main__':
    main()

import argparse
from pyfetchmath.init import init_project
from pyfetchmath.add import add_component

def main():
    parser = argparse.ArgumentParser("pyfetchmath")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init")

    add = sub.add_parser("add")
    add.add_argument("component")

    args = parser.parse_args()

    if args.command == "init":
        init_project()
    elif args.command == "add":
        add_component(args.component)
    else:
        parser.print_help()

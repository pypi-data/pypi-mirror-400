import argparse
from pygen_modules.generator import generate_project

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("name")
    args = parser.parse_args()

    if args.command == "start":
        generate_project(args.name)

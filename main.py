#!/usr/bin/env python3
import argparse
import sys
from core.runner import run
from core.utils import list_engines

def main():
    parser = argparse.ArgumentParser(description="SSTInator")

    parser.add_argument(
        "-e", "--engines",
        type=str,
        help="Comma-separated list of template engines to use (e.g., -e ejs,twig)"
    )
    parser.add_argument(
        "-l", "--lang",
        type=str,
        help="Target language (e.g., node, php, ruby, python, java)"
    )
    parser.add_argument(
        "-g", "--guess",
        action="store_true",
        help="Run engine guess before evaluating templates"
    )
    parser.add_argument(
        "-L", "--list-engines",
        action="store_true",
        help="List all available template engines per language"
    )

    args = parser.parse_args()

    if args.list_engines:
        list_engines(args.lang)
        sys.exit(0)

    run(
        engines_arg=args.engines,
        lang_arg=args.lang,
        do_discriminate=args.guess
    )

if __name__ == "__main__":
    main()

import sys


def main():
    from .cli import pipeline_cli

    sys.exit(pipeline_cli())

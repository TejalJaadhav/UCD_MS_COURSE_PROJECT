"""Prepare a separate worksheet for revised test predictions."""

import argparse
from pathlib import Path

from src.evaluation import prepare_component_matching as matching


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    matching.REPORT = args.report
    matching.OUTPUT = (
        matching.ROOT
        / "outputs/annotation_pilot/component_matching_verified.json"
    )
    matching.main()


if __name__ == "__main__":
    main()
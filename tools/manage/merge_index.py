import argparse
import json
import logging
import os
import sys

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(here))

from utils.matrix import download_index_file  # noqa

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

"""
This script merges multiple index.json files into a single index.json file.
"""


def to_file(d, target):
    with open(target, "w") as f:
        json.dump(d, f, indent=4)


def check_file(target, ref_num):
    with open(target) as f:
        db = json.load(f)
        assert len(db["matrix"]) == ref_num, f"{len(db['matrix'])} != {ref_num}"


def merge(input_dir, result_file, system_file=None, dry_run=False):
    db_res = {}
    total_num = 0
    if system_file is not None:
        with open(system_file) as f:
            db_res = json.load(f)
            total_num = len(db_res["matrix"])
        LOG.info(f"system index file: {system_file} number of entries={total_num}")

    LOG.info("load index file")
    # for f in os.scandir(input_dir):
    #     if f.is_dir() and f.name.startswith("matrices_"):
    #         index_file = os.path.join(f.path, "index.json")
    #         with open(index_file) as f:
    #             db = json.load(f)
    #             n = len(db["matrix"])
    #             total_num += n
    #             if not db_res:
    #                 db_res = db
    #             else:
    #                 db_res["matrix"].update(db["matrix"])
    #             LOG.info(f" loaded index file: {index_file} number of entries={n}")

    index_file = os.path.join(input_dir, "index.json")
    with open(index_file) as f:
        db = json.load(f)
        n = len(db["matrix"])
        total_num += n
        if not db_res:
            db_res = db
        else:
            db_res["matrix"].update(db["matrix"])
        LOG.info(f" loaded index file: {index_file} number of entries={n}")

    LOG.info(f"final index file: {result_file} number of entries={total_num}")
    if not dry_run:
        to_file(db_res, result_file)
        check_file(result_file, total_num)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["local", "system"],
        default="local",
        help="merge mode",
    )

    parser.add_argument(
        "--input-dir", default="", type=str, help="input root directory path"
    )
    parser.add_argument(
        "--output-dir", default="", type=str, help="output directory path"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="perform test run without data processing",
    )

    # get args
    args = parser.parse_args()
    LOG.info(f"args={args}")

    if args.dry_run:
        LOG.warn("Running in dry-run mode!")

    if args.mode not in ["local", "system"]:
        raise ValueError(f"Invalid mode: {args.mode}")

    if not os.path.exists(args.input_dir):
        raise ValueError(f"input directory: {args.input_dir} doest not exist!")

    if args.output_dir == "":
        raise ValueError(f"Invalid output directory: {args.output_dir}")

    result_file = os.path.join(args.output_dir, "index.json")
    os.makedirs(os.path.dirname(result_file), exist_ok=True)

    if args.mode == "local":
        merge(args.input_dir, result_file, dry_run=args.dry_run)

    elif args.mode == "system":
        # fetch remote system index.json
        system_file = os.path.join(args.output_dir, "index.json.remote")
        download_index_file(system_file)
        merge(
            args.input_dir, result_file, system_file=system_file, dry_run=args.dry_run
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOG.debug("Exception=KeyboardInterrupt")
        sys.exit(0)

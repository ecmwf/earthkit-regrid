# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import argparse
import json
import logging
import os
import sys

import yaml

from earthkit.regrid.db import SYS_DB as DB

LOG = logging.getLogger(__name__)


"""Build a local matrix inventory by subsetting the default (remotely hosted) inventory."""


def subset_remote_db(
    conf_file, out_dir, strict=True, fail_on_missing=True, dry_run=False
):
    index_file = os.path.join(out_dir, "index.json")

    if not dry_run:
        os.makedirs(out_dir, exist_ok=True)
        if strict:
            if len(os.listdir(out_dir)) > 0:
                raise Exception("out_dir must be empty when strict=True")

    with open(conf_file) as f:
        items = yaml.safe_load(f)

    # res = dict(matrix={})
    # entries = []
    # inter = {}

    index = DB.subset_index(items, fail_on_missing=fail_on_missing)

    # copy matrices
    for _, entry in index.items():
        matrix_path = DB.copy_matrix_file(
            entry, out_dir, exist_ok=(not strict), dry_run=dry_run
        )

        LOG.info(f"  matrix_file: {os.path.relpath(matrix_path, out_dir)}")
        LOG.info("  matrix copied to out_dir")

    # save index file
    index_file = os.path.join(out_dir, "index.json")
    if not dry_run:
        with open(index_file, "w") as f:
            json.dump(index.to_raw(), f, indent=4)

    LOG.info(f"Index data saved to {index_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", default="", type=str, help="configuration file path")
    parser.add_argument("--out-dir", default="", type=str, help="output directory path")

    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="do not fail when a required grid combination is not supported",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when out_dir is not empty",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="perform test run without data processing",
    )

    parser.add_argument(
        "--log-level",
        dest="log_level",
        choices=["debug", "info", "warn", "error", "critical"],
        default="info",
        help="set the logging level (default=info)",
    )

    # get args
    args = parser.parse_args()

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    logging.basicConfig(
        level=log_levels[args.log_level], format="%(levelname)s: %(message)s"
    )

    # basic checks
    if not os.path.exists(args.conf):
        LOG.error(
            f"Config file path={args.conf} cannot be accessed! Use --conf to specify a valid path!"
        )
        sys.exit(1)

    if args.out_dir == "":
        LOG.error("No output directory specified! Use --out-dir to specify a path!")
        sys.exit(1)

    LOG.info(f"args={args}")

    subset_remote_db(
        args.conf,
        args.out_dir,
        strict=args.strict,
        fail_on_missing=not args.allow_missing,
        dry_run=args.dry_run,
    )

    LOG.info("DONE")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOG.debug("Exception=KeyboardInterrupt")
        sys.exit(0)

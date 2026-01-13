#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# author: ak1ra
# date: 2025-01-24

import argparse
import time
from pathlib import Path

import argcomplete
from chaos_utils.logging import setup_json_logger
from lunar_python import Lunar, Solar

from lunar_birthday_ical.calendar import LunarCalendarApp

logger = setup_json_logger(__name__, file_logging=True)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Generate iCal events and reminders for lunar birthday and cycle days."
    )
    parser.add_argument(
        "config_files",
        type=Path,
        nargs="*",
        metavar="config.yaml",
        help="config file for iCal, checkout config/example-lunar-birthday.yaml for example.",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-L",
        "--lunar-to-solar",
        type=int,
        nargs=3,
        metavar=("YYYY", "MM", "DD"),
        help="Convert lunar date to solar date, add minus sign before leap lunar month.",
    )
    group.add_argument(
        "-S",
        "--solar-to-lunar",
        type=int,
        nargs=3,
        metavar=("YYYY", "MM", "DD"),
        help="Convert solar date to lunar date.",
    )
    return parser


def handle_lunar_to_solar(ymd: list[int]) -> None:
    """Handle lunar to solar conversion.

    Args:
        ymd: List containing [year, month, day].
    """
    lunar = Lunar.fromYmd(*ymd)
    solar = lunar.getSolar()
    logger.info("Lunar date %s is Solar %s", lunar.toString(), solar.toString())


def handle_solar_to_lunar(ymd: list[int]) -> None:
    """Handle solar to lunar conversion.

    Args:
        ymd: List containing [year, month, day].
    """
    solar = Solar.fromYmd(*ymd)
    lunar = solar.getLunar()
    logger.info("Solar date %s is Lunar %s", solar.toString(), lunar.toString())


def process_config_files(config_files: list[Path]) -> None:
    """Process list of configuration files.

    Args:
        config_files: List of paths to configuration files.
    """
    for file in config_files:
        config_path = Path(file)
        logger.debug("loading config file %s", config_path)
        start = time.perf_counter()

        app = LunarCalendarApp(config_path)
        app.generate()
        output_file = app.save()
        app.upload(output_file)

        elapsed = time.perf_counter() - start
        logger.debug("iCal generation elapsed at %.6fs for %s", elapsed, config_path)


def main() -> None:
    """Run the application."""
    parser = create_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.lunar_to_solar:
        handle_lunar_to_solar(args.lunar_to_solar)
        parser.exit()

    if args.solar_to_lunar:
        handle_solar_to_lunar(args.solar_to_lunar)
        parser.exit()

    if len(args.config_files) == 0:
        parser.print_help()
        parser.exit()

    process_config_files(args.config_files)

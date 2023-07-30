#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import argparse

from sysplant.utils.loggerSingleton import LoggerSingleton
from sysplant.constants import DESC_HEADER, FANCY_HEADER
from sysplant.sysplant import Sysplant

if __name__ == "__main__":
    # Set default level
    log_level = logging.INFO

    # Init logger Singleton
    logger = LoggerSingleton(log_level)

    parser = argparse.ArgumentParser(description=DESC_HEADER)

    ##################### VERBOSITY OPTIONS #####################
    output_options = parser.add_argument_group("Output options")
    shout_level = output_options.add_mutually_exclusive_group()
    shout_level.add_argument(
        "--debug", action="store_true", help="Display all DEBUG messages upon execution"
    )
    shout_level.add_argument(
        "--verbose",
        action="store_true",
        help="Display all INFO messages upon execution",
    )
    shout_level.add_argument(
        "--quiet",
        action="store_true",
        help="Remove all messages upon execution",
    )

    ##################### ACTIONS OPTIONS #####################
    actions = parser.add_subparsers(dest="action")
    actions.required = True

    action_list = actions.add_parser("list")
    action_generate = actions.add_parser("generate")

    ################## LIST ACTION ########################
    action_list.add_argument(
        "path", help="Path to search for NtFunction, could be a file or a directory"
    )

    ################## GENERATE ACTION ########################
    subparsers = action_generate.add_subparsers(dest="generation")
    subparsers.required = True

    parser_hell = subparsers.add_parser("hell")
    parser_halo = subparsers.add_parser("halo")
    parser_tartarus = subparsers.add_parser("tartarus")
    parser_freshy = subparsers.add_parser("freshy")
    parser_syswhispers = subparsers.add_parser("syswhispers")
    parser_syswhispers3 = subparsers.add_parser("syswhispers3")
    parser_canterlot = subparsers.add_parser("canterlot")
    parser_custom = subparsers.add_parser("custom")

    ###################### ARCH OPTIONS #######################
    arch_options = action_generate.add_argument_group("Architecture options")
    arch = arch_options.add_mutually_exclusive_group()
    arch.add_argument(
        "-x86", action="store_true", help="Set mode to 32bits", default=False
    )
    arch.add_argument(
        "-wow",
        action="store_true",
        help="Set mode to WoW64 (execution of 32bits on 64bits)",
        default=False,
    )
    arch.add_argument(
        "-x64",
        action="store_true",
        help="Set mode to 64bits (Default True)",
        default=True,
    )

    ###################### LANGUAGE OPTIONS #######################
    lang_options = action_generate.add_argument_group("Language options")
    language = lang_options.add_mutually_exclusive_group()
    language.add_argument(
        "-nim", action="store_false", help="Generate NIM code (Default: true)", default=True
    )
    language.add_argument(
        "-c", action="store_true", help="Generate C code", default=False
    )

    ##################### CUSTOM OPTIONS #####################
    parser_custom.add_argument(
        "-i",
        "--iterator",
        help="Select syscall iterator (Default: canterlot)",
        choices=[
            "hell",
            "halo",
            "tartarus",
            "freshy",
            "syswhispers",
            "syswhispers3",
            "canterlot",
        ],
        default="canterlot",
    )
    parser_custom.add_argument(
        "-r",
        "--resolver",
        help="Select syscall resolver (Default: basic)",
        choices=["basic", "random"],
        default="basic",
    )
    parser_custom.add_argument(
        "-s",
        "--stub",
        help="Select syscall stub (Default: indirect)",
        choices=["direct", "indirect"],
        default="direct",
    )

    ##################### SYSCALL OPTIONS #####################
    syscalls_options = action_generate.add_argument_group("Syscall options")
    syscalls = syscalls_options.add_mutually_exclusive_group()
    syscalls.add_argument(
        "-p",
        "--preset",
        help="Preset functions to generate (Default: common)",
        choices=["all", "donut", "common"],
        required=False,
        default="common",
    )
    syscalls.add_argument(
        "-f", "--functions", help="Comma-separated functions", required=False
    )

    ##################### GENERATE OPTIONS #####################
    action_generate.add_argument(
        "-x",
        "--scramble",
        help="Randomize internal function names to evade static analysis",
        action="store_true",
    )

    action_generate.add_argument(
        "-o",
        "--output",
        help="Output path for NIM generated file",
        required=True,
    )

    args = parser.parse_args()

    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    if args.quiet:
        log_level = logging.CRITICAL

    # Update log level if necessary
    logger.log_level = log_level
    logger.info(FANCY_HEADER, stripped=True)

    if args.action == "generate":
        # Set architecture
        arch = "x86" if args.x86 else "x64"

        # Preset infos when necessary
        if args.generation == "hell":
            iterator = "hell"
            resolver = "basic"
            stub = "direct"
        elif args.generation == "halo":
            iterator = "halo"
            resolver = "basic"
            stub = "direct"
        elif args.generation == "tartarus":
            iterator = "tartarus"
            resolver = "basic"
            stub = "direct"
        elif args.generation == "freshy":
            iterator = "freshy"
            resolver = "basic"
            stub = "direct"
        elif args.generation == "syswhispers":
            iterator = "syswhispers"
            resolver = "basic"
            stub = "direct"
        elif args.generation == "syswhispers3":
            iterator = "syswhispers3"
            resolver = "random"
            stub = "indirect"
        elif args.generation == "canterlot":
            iterator = "canterlot"
            resolver = "random"
            stub = "indirect"
        elif args.generation == "custom":
            iterator = args.iterator
            resolver = args.resolver
            stub = args.stub

        try:
            # Override default condition (preset: common) if funcitons are set
            if args.functions:
                args.syscalls = args.functions.split(",")
            # Set syscall to generate
            else:
                args.syscalls = args.preset

            # Set language mode
            lang_set = "nim" # Default option
            if args.c:
                lang_set = "c"
            
            engine = Sysplant(arch=arch, language=lang_set)
            engine.generate(
                iterator=iterator, resolver=resolver, stub=stub, syscalls=args.syscalls
            )
            engine.scramble(args.scramble)
            engine.output(args.output)
        except Exception as err:
            logger.critical(err)
    else:
        try:
            engine = Sysplant()
            found = engine.list(args.path)
            if len(found) > 0:
                logger.info(f"{len(found)} NtFunctions found:")
                logger.output(",".join(found))
            else:
                logger.info("No NtFunctions found")
        except Exception as err:
            logger.critical(err)

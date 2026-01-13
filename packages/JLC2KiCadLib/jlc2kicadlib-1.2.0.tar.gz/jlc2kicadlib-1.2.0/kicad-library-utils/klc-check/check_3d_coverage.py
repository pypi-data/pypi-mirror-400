#!/usr/bin/env python3


import argparse
import os
import sys
from glob import glob  # enable windows wildcards

common = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, "common")
)
if common not in sys.path:
    sys.path.insert(0, common)

from kicad_mod import KicadMod
from print_color import PrintColor


class Config:
    def __init__(self):
        # Set default argument values
        self.verbose = False
        self.print_color = True
        self.summary = False
        self.library = []
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.parse_arguments()

    def model_dir_path(self, library_name):
        return os.path.join(self.model_root, library_name + ".3dshapes")

    def footprint_dir_path(self, library_name):
        return os.path.join(self.library_root, library_name + ".pretty")

    def valid_library_names(self):
        if self.library:
            spec = self.library[0] + ".pretty"
        else:
            spec = "*.pretty"
        try:
            libs = sorted(
                [
                    os.path.splitext(os.path.basename(f))[0]
                    for f in glob(os.path.join(self.library_root, spec))
                    if os.path.isdir(f)
                ]
            )
        except FileNotFoundError:
            logger.fatal(
                f"EXIT: problem reading from footprint root: {self.library_root:s}"
            )
            sys.exit(1)
        if self.library:
            if not libs:
                logger.fatal(f"EXIT: footprint library not found: {self.library[0]:s}")
                sys.exit(1)
        return libs

    def valid_models(self, library_name):
        if os.path.exists(self.model_dir_path(library_name)):
            try:
                return sorted(
                    [
                        model
                        for model in os.listdir(self.model_dir_path(library_name))
                        if model.endswith(("wrl", "step", "stp"))
                    ]
                )
            except FileNotFoundError:
                logger.error(
                    f"- problem reading from 3D model directory: {self.model_dir_path(library_name):s}"
                )
                return None
        else:
            logger.error(
                f"- 3D model directory does not exist: {self.model_dir_path(library_name):s}"
            )
            return None

    def valid_footprints(self, library_name):
        dir_name = self.footprint_dir_path(library_name)
        try:
            return sorted(
                [
                    f
                    for f in os.listdir(dir_name)
                    if os.path.isfile(os.path.join(dir_name, f))
                    and f.endswith(".kicad_mod")
                ]
            )
        except FileNotFoundError:
            logger.fatal(
                f"EXIT: problem reading from footprint directory: {dir_name:s}"
            )
            sys.exit(1)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(
            description=(
                "Checks that KiCad footprint files (.kicad_mod) reference 3D model"
                " files that exist in the KiCad library."
            )
        )
        parser.add_argument(
            "library",
            help=(
                "name of footprint library to check (e.g. Housings_SOIC) (default is"
                " all libraries)"
            ),
            type=str,
            nargs="*",
        )
        parser.add_argument(
            "-m",
            "--models",
            help="path to KiCad 3d models folder (default is ../../kicad-packages3D)",
            type=str,
        )
        parser.add_argument(
            "-f",
            "--footprints",
            help="path to KiCad footprint folder (default is ../../kicad-footprints)",
            type=str,
        )
        parser.add_argument(
            "-r",
            "--root",
            help="path to root KiCad folder (default is ../../)",
            type=str,
        )
        parser.add_argument(
            "-v", "--verbose", help="enable verbose output", action="store_true"
        )
        parser.add_argument(
            "--nocolor", help="do not use color text in output", action="store_true"
        )
        parser.add_argument("--summary", help="print summary only", action="store_true")
        args = parser.parse_args()
        if args.verbose:
            self.verbose = True
        if args.nocolor:
            self.print_color = False
        if args.library:
            self.library.append(str(args.library[0]))
        if args.root:
            self.root = str(args.root)
        self.library_root = os.path.join(self.root, "kicad-footprints")
        self.model_root = os.path.join(self.root, "kicad-packages3D")
        if args.footprints:
            self.library_root = str(args.footprints)
        if args.models:
            self.model_root = str(args.models)
        if args.summary:
            self.summary = True


class Logger:
    def __init__(self, printer, verbose=False, summary=False):
        self.printer = printer
        self.verbose = verbose
        self.summary = summary
        self.warning_count = 0
        self.error_count = 0

    def status(self, s):
        self.printer.regular(s)

    def info(self, s):
        if self.verbose:
            self.printer.green(s)

    def warning(self, s):
        self.warning_count += 1
        if not self.summary:
            self.printer.yellow(s)

    def error(self, s):
        self.error_count += 1
        if not self.summary:
            self.printer.red(s)

    def fatal(self, s):
        self.printer.red(s)

    def reset(self):
        self.error_count = 0
        self.warning_count = 0


class LibraryChecker:
    def __init__(self):
        self.num_footprints = 0
        self.no_3dshape_folder = 0
        self.no_model_specified = 0
        self.model_not_found = 0
        self.model_found = 0
        self.invalid_model_path = 0
        self.unused_wrl = 0

    def parse_footprint(self, filename):
        # logger.info('Footprint: {f:s}'.format(f=os.path.basename(filename)))
        try:
            footprint = KicadMod(filename)
        except FileNotFoundError:
            logger.fatal(f"EXIT: problem reading footprint file {filename:s}")
            sys.exit(1)

        try:
            long_reference = footprint.models[0]["file"]
        except IndexError:
            if footprint.is_virtual:
                # count as model found
                self.model_found += 1
            else:
                logger.warning(
                    f"- No model file specified in {os.path.basename(filename):s}"
                )
                self.no_model_specified += 1
            return None

        try:
            # Accept both forward and backward slash characters in path
            long_reference = "/".join(long_reference.split("\\"))
            return os.path.basename(long_reference)
        # TODO: determine, which specific problem could happen above ("ValueError" is just a guess)
        except ValueError:
            logger.warning(f"- Invalid model reference {long_reference:s}")
            self.invalid_model_path += 1
            return None

    def find_name_in_list(self, _list, name, case_sensitive=True):
        if case_sensitive:
            return name in _list
        else:
            name_lower = name.lower()
            for n in _list:
                if name_lower == n.lower():
                    return True
            return False

    def check_footprint_library(self, library_name):
        logger.reset()
        logger.status(
            f"\r\nChecking {library_name:s} (contains {len(config.valid_footprints(library_name)):d} footprints)"
        )

        footprint_names = config.valid_footprints(library_name)
        models = config.valid_models(library_name)

        if not os.path.exists(config.model_dir_path(library_name)):
            self.no_3dshape_folder += 1

        if models:
            unused = models[:]

        for footprint in footprint_names:
            self.num_footprints += 1
            model_ref = self.parse_footprint(
                os.path.join(config.footprint_dir_path(library_name), footprint)
            )
            if model_ref:
                if models:
                    if self.find_name_in_list(models, model_ref, True):
                        self.model_found += 1
                        logger.info(f"Found 3D model {model_ref:s}")
                        if model_ref in unused:
                            unused.remove(model_ref)
                    else:
                        self.model_not_found += 1
                        if self.find_name_in_list(models, model_ref, False):
                            logger.warning(
                                f"- 3D model not found {model_ref:s} in {footprint:s} (wrong case)"
                            )
                        else:
                            logger.warning(
                                f"- 3D model not found {model_ref:s} in {footprint:s}"
                            )
                else:
                    self.model_not_found += 1

        footprint_warnings = logger.warning_count
        unused_models = []

        if models:
            unused_models = [model for model in unused if model.endswith(".wrl")]
            self.unused_wrl += len(unused_models)
            for model in unused_models:
                logger.warning(
                    f"- Unused .wrl model {library_name:s}.3dshapes/{model:s}"
                )

        if logger.warning_count > 0:
            logger.status(f"- {footprint_warnings:d} footprint warnings")

        if logger.error_count > 0:
            logger.status(f"- {logger.error_count:d} footprint errors")

        if unused_models:
            logger.status(f"- {len(unused_models):d} unused model warnings")

    def check_libraries(self):
        lib_names = config.valid_library_names()
        for library in lib_names:
            self.check_footprint_library(library)

        logger.status("")
        logger.status("-" * 80)
        logger.status("Summary")
        logger.status("")
        logger.status(f"Libraries scanned       {len(lib_names)}")
        logger.status(f"Footprints              {self.num_footprints}")
        logger.status(f"No model file specified {self.no_model_specified}")
        logger.status(f"3D Model not found      {self.model_not_found}")
        logger.status(f"No 3D Model folder      {self.no_3dshape_folder}")
        logger.status(f"3D Model found          {self.model_found}")
        logger.status(f"Unused wrl file         {self.unused_wrl}")


# main program

if __name__ == "__main__":
    config = Config()

    printer = PrintColor(use_color=config.print_color)
    logger = Logger(printer, config.verbose, config.summary)

    logger.info(f"Library root: {config.library_root:s}")
    logger.info(f"Model root:  {config.model_root:s}")

    checker = LibraryChecker()
    checker.check_libraries()

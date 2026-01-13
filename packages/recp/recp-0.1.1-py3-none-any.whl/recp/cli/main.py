import os
import sys
import argparse
from datetime import datetime
from importlib.metadata import version
from ..utils.recipe import Recipe
from ..utils.config import PackageConfig


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="run command line tools recp",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False
    )
    subparser = parser.add_subparsers(dest="action")

    # Run parser
    run_parser = subparser.add_parser(
        "run",
        description="run recipes in .yaml format",
        help="run recipes in .yaml format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False
    )
    run_parser.add_argument(
        "recipe",
        type=str,
        help="recipe .yaml file"
    )
    run_parser.add_argument(
        "-t", "--tag",
        nargs="*",
        type=str,
        help="include only steps matching a specific tag"
    )
    run_parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="show the sequence of commands to be run without running them"
    )
    run_parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="ignore and skip steps that resulted in errors"
    )
    run_parser.add_argument(
        "--unsafe",
        action="store_true",
        help="enable unsafe !expr constructor in recipe files"
    )

    # Config parser
    config_parser = subparser.add_parser(
        "config", # Show available recipes too
        description="configure recp",
        help="configure recp",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False
    )
    config_parser_option_group = config_parser.add_mutually_exclusive_group()
    config_parser_option_group.add_argument(
        "--set",
        type=str,
        nargs=2,
        help="set parameter",
    )
    config_parser_option_group.add_argument(
        "--add",
        type=str,
        help="add a recipe",
    )
    return parser


def main() -> None:
    # Version print
    if (
        len(sys.argv) == 1
        or (len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"))
    ):
        print(
            f"recp version {version('recp')} developed by Esteban Gómez 2025-"
            f"{datetime.now().year} (Speech Interaction Technology, Aalto "
            "University)"
        )
        sys.exit(0)
    
    # Parse args
    parser = get_parser()
    args = parser.parse_args()

    match args.action:
        case "config":
            config = PackageConfig(app_name="recp", app_author="Esteban Gómez")

            if args.set:
                config.set_param(param=args.set[0], value=args.set[1])
            
            elif args.add:
                config.add_recipe(args.add)

            else:
                config.print_params()
        
        case "run":
            # Check if recipe is a preset
            if not args.recipe.endswith(".yaml"):
                config = PackageConfig(
                    app_name="recp",
                    app_author="Esteban Gómez"
                )

                if os.path.isfile(
                    os.path.join(config.recipes_dir, args.recipe + ".yaml")
                ):
                    args.recipe = os.path.join(
                        config.recipes_dir,
                        args.recipe + ".yaml"
                    )
                
                else:
                    raise FileNotFoundError(
                        f"Recipe {args.recipe!r} not found in recipes folder "
                        f"{config.recipes_dir!r}"
                    )

            # Create and run recipe
            recipe = Recipe(file=args.recipe, allow_expr=args.unsafe)
            recipe.run(
                tag=args.tag,
                ignore_errors=args.ignore_errors,
                dry_run=args.dry_run
            )
        
        case _:
            raise AssertionError


if __name__ == "__main__":
    main()

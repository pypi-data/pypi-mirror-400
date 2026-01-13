"""CLI entry point for qparameterize."""

import argparse
from pathlib import Path
from typing import Any

from .qparameterize import clean, parameterize, record_output


def parse_pair(s: str) -> tuple[str, str]:
    """
    Parse a KEY:VALUE string into a tuple.

    Parameters
    ----------
    s
        String in "KEY:VALUE" format.

    Returns
    -------
        Tuple of (key, value) with whitespace stripped.

    Raises
    ------
    argparse.ArgumentTypeError
        If string doesn't contain ':' or key is empty.
    """
    if ":" not in s:
        raise argparse.ArgumentTypeError("Expected NAME:VALUE")
    k, v = s.split(":", 1)
    k, v = k.strip(), v.strip()
    if not k:
        raise argparse.ArgumentTypeError("Parameter name cannot be empty")
    return k, v


def parse_yaml(filename: str) -> list[tuple[str, Any]]:
    """
    Parse a YAML file into a list of key-value tuples.

    Parameters
    ----------
    s
        Path to the YAML file.

    Returns
    -------
        List of (key, value) tuples from the YAML mapping.

    Raises
    ------
    argparse.ArgumentTypeError
        If file not found, invalid YAML, or not a mapping.
    """
    import yaml

    path = Path(filename)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"YAML file not found: {path}")

    try:
        data: dict[str, Any] = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise argparse.ArgumentTypeError(f"Invalid YAML in {path}: {e}")

    if not isinstance(data, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise argparse.ArgumentTypeError(
            f"YAML file must contain a mapping, got {type(data).__name__}"
        )

    return list(data.items())


def main() -> None:
    """CLI entry point for qparameterize."""
    parser = argparse.ArgumentParser(
        prog="qparameterize",
        description="Parameterise a quarto document",
        epilog="""
Parameterize Quarto documents for batch rendering with multiple parameter sets for
the jupyter engine.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("filename", nargs="?", help="Input .qmd file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output filename (default: auto-generated from parameters)",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-P",
        "--execute-param",
        action="append",
        type=parse_pair,
        default=[],
        help="Repeatable KEY:VALUE (e.g. -P key1:value1 -P key2:42)",
    )
    group.add_argument(
        "--execute-params",
        action="store",
        type=parse_yaml,
        default=[],
        help="YAML file with parameter values",
    )
    group.add_argument(
        "--clean",
        action="store_true",
        help="Delete all previously generated parameterized files",
    )

    args = parser.parse_args()

    # Handle --clean
    if args.clean:
        _ = clean()
        return

    # Handle parameterization - filename is required
    if not args.filename:
        parser.error("filename is required for parameterization")

    params = {}
    if args.execute_param:
        for name, value in args.execute_param:
            if name in params:
                raise SystemExit(f"Duplicate parameter: {name}")
            params[name] = value
    else:
        params = {name: value for name, value in args.execute_params}

    output_path = parameterize(args.filename, params, output=args.output)
    record_output(output_path)


if __name__ == "__main__":
    main()

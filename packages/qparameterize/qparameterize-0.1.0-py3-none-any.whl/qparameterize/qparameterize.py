"""
Quarto file parameterization utility.

This module provides functionality to parameterize Quarto (.qmd) files by
substituting parameter values and adding labels to code blocks.
"""

from __future__ import annotations

import re
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


# Regex patterns for matching Python parameter assignments
PARAMETER_PATTERNS = [
    # string: name = "value" or name = 'value'
    re.compile(r'(?P<name>\w+)\s*=\s*(?P<quote>["\'])(?P<value>[^"\']*)(?P=quote)'),
    # number: name = 42 or name = 3.14
    re.compile(r"(?P<name>\w+)\s*=\s*(?P<value>-?\d+\.?\d*)"),
    # bool: name = True or name = False
    re.compile(r"(?P<name>\w+)\s*=\s*(?P<value>True|False)"),
]
# Path to the tracking file
TRACKING_FILE = Path(".quarto") / "qparameterize.txt"


@dataclass
class QuartoCodeBlock:
    """
    Represents a Quarto code block with its options.

    Attributes
    ----------
    start_pos
        Starting position in the document.
    end_pos
        Ending position in the document.
    language
        The language of the code block.
    full_text
        The complete text of the code block including fences.
    content
        Content inside the block (options + code).
    options
        Parsed options from #| directives.
    code
        Pure code without options.
    """

    start_pos: int
    end_pos: int
    language: str
    full_text: str
    content: str
    options: dict[str, Any]
    code: str

    def __str__(self):
        options = "\n".join(f"#| {k}: {v}" for k, v in self.options.items())
        options_section = f"{options}\n" if options else ""
        return f"```{{{self.language}}}\n{options_section}{self.code}\n```"

    def __copy__(self):
        from dataclasses import replace

        return replace(self, options=self.options.copy())

    @property
    def tags(self) -> str | list[str]:
        """
        Get the block tags.

        Returns
        -------
            The tags value, parsed as a list if in bracket notation.
        """
        value = self.options.get("tags", "")
        # Handle lists like "[parameters]"
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",")]
        return value


def parse_code_blocks(content: str) -> list[QuartoCodeBlock]:
    """
    Parse all Python code blocks in the Quarto document.

    Parameters
    ----------
    content
        The Quarto document content.

    Returns
    -------
        List of parsed code blocks.
    """
    blocks: list[QuartoCodeBlock] = []
    # Pattern to match ```{python} ... ```
    pattern = re.compile(r"```\{python\}(.*?)```", flags=re.DOTALL)

    for match in pattern.finditer(content):
        block_content = match.group(1)
        options, code = parse_options(block_content)

        block = QuartoCodeBlock(
            start_pos=match.start(),
            end_pos=match.end(),
            language="python",
            full_text=match.group(0),
            content=block_content,
            options=options,
            code=code,
        )
        blocks.append(block)

    return blocks


def parse_options(block_content: str) -> tuple[dict[str, Any], str]:
    """
    Parse Quarto options from code block content.

    Options are lines starting with #| at the top of the block.

    Parameters
    ----------
    block_content
        The content inside a code block.

    Returns
    -------
        A tuple of (options dict, pure code string).
    """
    lines = block_content.split("\n")[1:-1]
    options: dict[str, Any] = {}
    code_start = 0
    # Multline values appear on a line without a key. They are associated with the
    # previous key and we  keep track of it.
    previous_key = None

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("#|"):
            break

        parts = stripped[2:].split(":", 1)
        if len(parts) == 2:
            key, value = parts[0].strip(), parts[1].strip()
            previous_key = key
        elif previous_key is None:
            break  # Malformed option line, treat as code
        else:
            key, value = previous_key, f"{options[previous_key]}\n{line}"

        options[key] = value
        code_start += 1

    # Code starts
    code = "\n".join(lines[code_start:])
    return options, code


def find_parameters_block(blocks: list[QuartoCodeBlock]) -> QuartoCodeBlock | None:
    """
    Find the code block with #| tags: [parameters] option.

    Parameters
    ----------
    blocks
        List of code blocks to search.

    Returns
    -------
        The parameters block, or None if not found.

    Raises
    ------
    ValueError
        If multiple parameter blocks are found.
    """
    param_blocks: list[QuartoCodeBlock] = []
    for block in blocks:
        if isinstance(block.tags, list) and "parameters" in block.tags:
            param_blocks.append(block)

    if len(param_blocks) == 0:
        return None
    elif len(param_blocks) > 1:
        raise ValueError("Multiple parameters blocks found. Only one is allowed.")

    return param_blocks[0]


def substitute_parameters(
    code_block: QuartoCodeBlock, params: Mapping[str, Any]
) -> QuartoCodeBlock:
    """
    Substitute parameter definitions in the parameters block using regex.

    Parameters
    ----------
    code_block
        The parameters code block.
    params
        Parameter key-value pairs to substitute.

    Returns
    -------
        A new block with the custom parameter definitions.
    """

    def substitute(match: re.Match[str]):
        d = match.groupdict()
        name = match.group("name")
        value = params.get(name, d["value"])
        quote = d.get("quote", "")
        return f"{name} = {quote}{value}{quote}"

    new_block = copy(code_block)
    for pattern in PARAMETER_PATTERNS:
        new_block.code = pattern.sub(substitute, new_block.code)

    return new_block


def get_default_parameters(code_block: QuartoCodeBlock) -> dict[str, Any]:
    """
    Get default parameter values from a parameters block in declaration order.

    Parameters
    ----------
    code_block
        The parameters code block.

    Returns
    -------
        Dictionary mapping parameter names to their default values,
        ordered by declaration order in the code.
    """
    defaults: dict[str, Any] = {}

    # Process line by line to preserve declaration order
    for line in code_block.code.split("\n"):
        for pattern in PARAMETER_PATTERNS:
            match = pattern.search(line)
            if match and match.group("name") not in defaults:
                defaults[match.group("name")] = match.group("value")
                break

    return defaults


def set_parameters(content: str, params: Mapping[str, str | float | bool]) -> str:
    """
    Substitute parameter values in the parameters block.

    Parameters
    ----------
    content
        The Quarto document content.
    params
        Parameter key-value pairs to substitute.

    Returns
    -------
        Modified content with parameters substituted.

    Raises
    ------
    ValueError
        If no Python code blocks or parameters block is found.
    """
    # Parse code blocks
    blocks = parse_code_blocks(content)

    if not blocks:
        raise ValueError("No Python code blocks found in file")

    # Find parameters block
    params_block = find_parameters_block(blocks)

    if params_block is None:
        raise ValueError(
            "No parameters block found. Add a code block with #| tags: [parameters]"
        )

    params_block = substitute_parameters(params_block, params)

    # Replace in content
    before = content[: params_block.start_pos]
    after = content[params_block.end_pos :]
    modified_content = f"{before}{params_block}{after}"
    return modified_content


def add_labels(content: str, base_label: str) -> str:
    """
    Add label option to all Python code blocks.

    Parameters
    ----------
    content
        The Quarto document content.
    base_label
        The base label to add to all blocks.

    Returns
    -------
        Modified content with labels added to all blocks.
    """
    # Parse code blocks
    blocks = parse_code_blocks(content)

    if not blocks:
        return content  # No blocks to label

    # Add labels to all the blocks
    for idx, block in enumerate(blocks, 1):
        # Check if block has existing label and append if present
        existing_label = block.options.get("label")
        if existing_label:
            label = f"{existing_label}--{base_label}--{idx}"
        else:
            label = f"{base_label}--{idx}"
        block.options["label"] = label

    # Rebuild content from the bottom up so that the start and end
    # positions of the blocks remain valid during the process
    modified_content = content
    for block in blocks[::-1]:
        # Replace in content
        before = modified_content[: block.start_pos]
        after = modified_content[block.end_pos :]
        modified_content = f"{before}{block}{after}"

    return modified_content


def make_output_filename(base_filename: Path, label: str) -> Path:
    """
    Make output filename from parameters.

    Parameters
    ----------
    base_filename
        The original filename.
    label
        The label to append.

    Returns
    -------
        New filename with label appended (e.g., file.qmd -> file--elephant-7.qmd).
    """
    path = Path(base_filename)
    new_name = Path(f"{path.stem}--{label}{path.suffix}")

    if path.parent.name:
        return path.parent / new_name
    else:
        return new_name


def compute_base_label(content: str, params: Mapping[str, Any]) -> str:
    """
    Compute the base label from document content and parameter overrides.

    Parameters
    ----------
    content
        The Quarto document content.
    params
        Parameter key-value pairs to substitute.

    Returns
    -------
        A label string with parameter values in declaration order.

    Raises
    ------
    ValueError
        If parameters block not found or unknown parameters passed.
    """
    blocks = parse_code_blocks(content)
    params_block = find_parameters_block(blocks)
    if params_block is None:
        raise ValueError(
            "No parameters block found. Add a code block with #| tags: [parameters]"
        )

    default_params = get_default_parameters(params_block)

    unknown = set(params.keys()) - set(default_params.keys())
    if unknown:
        raise ValueError(f"Unknown parameters: {', '.join(sorted(unknown))}")

    merged = {name: params.get(name, value) for name, value in default_params.items()}
    return "-".join(str(v) for v in merged.values())


def parameterize(
    filename: str,
    params: Mapping[str, str | int | float | bool],
    output: str | None = None,
) -> str:
    """
    Parameterize a Quarto document by substituting parameter values and adding labels.

    This is a convenience function that orchestrates both set_parameters()
    and add_labels().

    Parameters
    ----------
    filename
        Path to the .qmd file.
    params
        Parameter name-value pairs to substitute.
    output
        Output filename. If None, auto-generated from parameters.

    Returns
    -------
        Path to the generated output file.

    Raises
    ------
    FileNotFoundError
        If input file doesn't exist.
    ValueError
        If parameters block not found or invalid.
    """
    filepath = Path(filename)
    content = filepath.read_text()

    base_label = compute_base_label(content, params)
    content = set_parameters(content, params)
    content = add_labels(content, base_label)

    # Write output file
    if output:
        output_filename = Path(output)
    else:
        output_filename = make_output_filename(filepath, base_label)
    output_filename.write_text(content)

    return str(output_filename)


def record_output(output_path: str) -> None:
    """
    Record a generated output file in the tracking file.

    Parameters
    ----------
    output_path
        Path to the generated file.
    """
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Read existing entries to avoid duplicates
    existing: set[str] = set()
    if TRACKING_FILE.exists():
        existing = set(TRACKING_FILE.read_text().strip().split("\n"))
        existing.discard("")  # Remove empty strings

    # Add new entry if not already present
    if output_path not in existing:
        with TRACKING_FILE.open("a") as f:
            f.write(f"{output_path}\n")


def clean() -> list[str]:
    """
    Delete all tracked parameterized files and clear the tracking file.

    Returns
    -------
        List of deleted file paths.
    """
    deleted: list[str] = []

    if not TRACKING_FILE.exists():
        return deleted

    # Read and delete each tracked file
    for line in TRACKING_FILE.read_text().strip().split("\n"):
        if not line:
            continue
        path = Path(line)
        if path.exists():
            path.unlink()
            deleted.append(line)

    # Clear the tracking file
    TRACKING_FILE.write_text("")

    return deleted

"""Tests for qparameterize.py."""

import pytest
from pathlib import Path

from qparameterize import (
    QuartoCodeBlock,
    parse_code_blocks,
    parse_options,
    find_parameters_block,
    substitute_parameters,
    get_default_parameters,
    parameterize,
)


# =============================================================================
# Test Fixtures
# =============================================================================

SIMPLE_QMD = """
---
title: Test
---

```{python}
#| tags: [parameters]
name = "default"
count = 10
```

```{python}
print(f"Hello {name}, count is {count}")
```
""".strip()

MULTI_BLOCK_QMD = """
---
title: Multi Block Test
---

```{python}
#| tags: [parameters]
animal = "cat"
```

```{python}
#| label: first-block
print(animal)
```

```{python}
#| label: second-block
print(animal.upper())
```

```{python}
print("done")
```
""".strip()

NO_PARAMS_QMD = """
---
title: No Parameters
---

```{python}
x = 1
```

```{python}
y = 2
```
""".strip()


# =============================================================================
# parse_code_blocks tests
# =============================================================================


class TestParseCodeBlocks:
    def test_single_code_block(self):
        content = """
```{python}
x = 1
```
""".strip()
        blocks = parse_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0].language == "python"

    def test_multiple_code_blocks(self):
        content = """
```{python}
x = 1
```

```{python}
y = 2
```
""".strip()
        blocks = parse_code_blocks(content)
        assert len(blocks) == 2

    def test_no_code_blocks(self):
        content = "Just some text without code blocks"
        blocks = parse_code_blocks(content)
        assert blocks == []

    def test_code_block_with_options(self):
        content = """
```{python}
#| label: foo
x = 1
```
""".strip()
        blocks = parse_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0].options.get("label") == "foo"

    def test_code_block_without_options(self):
        content = """
```{python}
x = 1
```
""".strip()
        blocks = parse_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0].options == {}

    def test_preserves_positions(self):
        content = """
prefix
```{python}
x = 1
```
suffix
""".strip()
        blocks = parse_code_blocks(content)
        assert blocks[0].start_pos == 7  # After "prefix\n"
        assert (
            content[blocks[0].start_pos : blocks[0].end_pos]
            == """
```{python}
x = 1
```
""".strip()
        )


# =============================================================================
# parse_options tests
# =============================================================================


class TestParseOptions:
    def test_single_option(self):
        block_content = """
#| label: foo
x = 1
"""
        options, code = parse_options(block_content)
        assert options == {"label": "foo"}
        assert code == "x = 1"

    def test_multiple_options(self):
        block_content = """
#| label: foo
#| echo: false
x = 1
"""
        options, code = parse_options(block_content)
        assert options == {"label": "foo", "echo": "false"}
        assert code == "x = 1"

    def test_multiline_option_value(self):
        block_content = """
#| fig-cap:
#|   This is a long
#|   caption
x = 1
"""
        options, _ = parse_options(block_content)
        assert "fig-cap" in options
        assert "long" in options["fig-cap"]

    def test_no_options(self):
        block_content = """
x = 1
y = 2
"""
        options, code = parse_options(block_content)
        assert options == {}
        assert "x = 1" in code

    def test_malformed_option_no_colon(self):
        # Line starting with #| but no colon should be treated as code
        block_content = """
#| this has no colon
x = 1
"""
        options, _ = parse_options(block_content)
        assert options == {}


# =============================================================================
# find_parameters_block tests
# =============================================================================


class TestFindParametersBlock:
    def test_finds_parameters_block(self):
        blocks = parse_code_blocks(SIMPLE_QMD)
        param_block = find_parameters_block(blocks)
        assert param_block is not None
        assert "parameters" in param_block.tags

    def test_no_parameters_block(self):
        blocks = parse_code_blocks(NO_PARAMS_QMD)
        param_block = find_parameters_block(blocks)
        assert param_block is None

    def test_multiple_parameters_blocks_raises(self):
        content = """
```{python}
#| tags: [parameters]
x = 1
```

```{python}
#| tags: [parameters]
y = 2
```
""".strip()
        blocks = parse_code_blocks(content)
        with pytest.raises(ValueError, match="Multiple parameters blocks"):
            find_parameters_block(blocks)


# =============================================================================
# substitute_parameters tests
# =============================================================================


class TestSubstituteParameters:
    def _make_block(self, code: str) -> QuartoCodeBlock:
        return QuartoCodeBlock(
            start_pos=0,
            end_pos=100,
            language="python",
            full_text=f"""
```{{python}}
{code}
```
""".strip(),
            content=f"\n{code}\n",
            options={},
            code=code,
        )

    def test_string_substitution(self):
        block = self._make_block('name = "default"')
        result = substitute_parameters(block, {"name": "custom"})
        assert 'name = "custom"' in result.code

    def test_number_substitution(self):
        block = self._make_block("count = 10")
        result = substitute_parameters(block, {"count": 42})
        assert "count = 42" in result.code

    def test_boolean_substitution(self):
        block = self._make_block("flag = False")
        result = substitute_parameters(block, {"flag": True})
        assert "flag = True" in result.code

    def test_keeps_original_if_not_in_params(self):
        block = self._make_block('name = "default"')
        result = substitute_parameters(block, {"other": "value"})
        assert 'name = "default"' in result.code

    def test_returns_new_block_no_mutation(self):
        block = self._make_block('name = "default"')
        original_code = block.code
        result = substitute_parameters(block, {"name": "custom"})
        # Original should be unchanged
        assert block.code == original_code
        # Result should be different
        assert result.code != original_code
        assert result is not block


# =============================================================================
# extract_default_parameters tests
# =============================================================================


class TestExtractDefaultParameters:
    def _make_block(self, code: str) -> QuartoCodeBlock:
        return QuartoCodeBlock(
            start_pos=0,
            end_pos=100,
            language="python",
            full_text=f"""
```{{python}}
{code}
```
""".strip(),
            content=f"\n{code}\n",
            options={},
            code=code,
        )

    def test_string_parameter(self):
        block = self._make_block('name = "default"')
        defaults = get_default_parameters(block)
        assert defaults == {"name": "default"}

    def test_number_parameter(self):
        block = self._make_block("count = 42")
        defaults = get_default_parameters(block)
        assert defaults == {"count": "42"}

    def test_boolean_parameter(self):
        block = self._make_block("flag = True")
        defaults = get_default_parameters(block)
        assert defaults == {"flag": "True"}

    def test_multiple_parameters_preserves_order(self):
        block = self._make_block('name = "default"\ncount = 10\nflag = False')
        defaults = get_default_parameters(block)
        assert list(defaults.keys()) == ["name", "count", "flag"]
        assert defaults == {"name": "default", "count": "10", "flag": "False"}

    def test_single_quoted_string(self):
        block = self._make_block("name = 'default'")
        defaults = get_default_parameters(block)
        assert defaults == {"name": "default"}

    def test_float_parameter(self):
        block = self._make_block("rate = 3.14")
        defaults = get_default_parameters(block)
        assert defaults == {"rate": "3.14"}


# =============================================================================
# Integration tests
# =============================================================================


class TestParameterizeIntegration:
    def test_full_workflow(self, tmp_path: Path):
        # Create input file
        input_file = tmp_path / "test.qmd"
        input_file.write_text(SIMPLE_QMD)

        # Run parameterize
        params = {"name": "elephant", "count": 7}
        output_path = parameterize(str(input_file), params)

        # Check output file exists
        output_file = Path(output_path)
        assert output_file.exists()

        # Check filename pattern
        assert "elephant-7" in output_file.name

        # Check content
        content = output_file.read_text()
        assert 'name = "elephant"' in content
        assert "count = 7" in content

    def test_labels_added_to_all_blocks(self, tmp_path: Path):
        input_file = tmp_path / "test.qmd"
        input_file.write_text(MULTI_BLOCK_QMD)

        output_path = parameterize(str(input_file), {"animal": "dog"})
        content = Path(output_path).read_text()

        # All blocks should have labels with the parameter value
        assert "#| label:" in content
        assert "dog" in content

    def test_existing_labels_preserved(self, tmp_path: Path):
        input_file = tmp_path / "test.qmd"
        input_file.write_text(MULTI_BLOCK_QMD)

        output_path = parameterize(str(input_file), {"animal": "dog"})
        content = Path(output_path).read_text()

        # Existing labels should be incorporated
        assert "first-block" in content
        assert "second-block" in content

    def test_output_filename_pattern(self, tmp_path: Path):
        input_file = tmp_path / "myfile.qmd"
        input_file.write_text(SIMPLE_QMD)

        output_path = parameterize(str(input_file), {"name": "test", "count": 1})

        assert output_path == str(tmp_path / "myfile--test-1.qmd")

    def test_output_filename_includes_defaults(self, tmp_path: Path):
        # Only override count, name should use default
        input_file = tmp_path / "myfile.qmd"
        input_file.write_text(SIMPLE_QMD)

        output_path = parameterize(str(input_file), {"count": 42})

        # Should include default "default" for name, and overridden 42 for count
        assert output_path == str(tmp_path / "myfile--default-42.qmd")

    def test_output_filename_declaration_order(self, tmp_path: Path):
        # Even when params passed in different order, filename should follow declaration order
        input_file = tmp_path / "myfile.qmd"
        input_file.write_text(SIMPLE_QMD)

        # Pass count before name (opposite of declaration order)
        output_path = parameterize(str(input_file), {"count": 1, "name": "test"})

        # Filename should still be name-count order (declaration order)
        assert output_path == str(tmp_path / "myfile--test-1.qmd")

    def test_unknown_parameter_raises_error(self, tmp_path: Path):
        input_file = tmp_path / "myfile.qmd"
        input_file.write_text(SIMPLE_QMD)

        with pytest.raises(ValueError, match="Unknown parameters"):
            parameterize(str(input_file), {"name": "test", "unknown": "value"})

    def test_custom_output_filename(self, tmp_path: Path):
        input_file = tmp_path / "test.qmd"
        input_file.write_text(SIMPLE_QMD)
        custom_output = tmp_path / "custom_name.qmd"

        output_path = parameterize(
            str(input_file), {"name": "x", "count": 1}, output=str(custom_output)
        )

        assert output_path == str(custom_output)
        assert custom_output.exists()

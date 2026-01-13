from unittest.mock import patch

from mark2pdf.core.core import convert_from_string
from mark2pdf.core.options import ConversionOptions


def test_force_filename_option(tmp_path):
    # Setup
    content = """---
exportFilename: my_custom_name.pdf
---
# Hello World
"""
    options = ConversionOptions(force_filename=True, overwrite=True)
    output_path = tmp_path / "original_name.pdf"

    # Mock execute_in_sandbox to avoid real conversion
    with patch("mark2pdf.core.core.execute_in_sandbox") as mock_execute:
        # 模拟转换成功，返回预期的输出路径
        mock_execute.side_effect = lambda *args, **kwargs: kwargs.get("output_path") and (
            kwargs["output_path"].touch() or kwargs["output_path"]
        )

        # Execute
        result_path = convert_from_string(
            content=content, output_path=output_path, options=options, config=None
        )

        # Verify
        assert result_path is not None
        assert result_path.name == "original_name.pdf"
        assert result_path.exists()


def test_without_force_filename_option(tmp_path):
    # Setup
    content = """---
exportFilename: my_custom_name.pdf
---
# Hello World
"""
    options = ConversionOptions(force_filename=False, overwrite=True)
    output_path = tmp_path / "original_name.pdf"

    # Mock execute_in_sandbox to avoid real conversion
    with patch("mark2pdf.core.core.execute_in_sandbox") as mock_execute:
        # 模拟转换成功，返回预期的输出路径
        mock_execute.side_effect = lambda *args, **kwargs: kwargs.get("output_path") and (
            kwargs["output_path"].touch() or kwargs["output_path"]
        )

        # Execute
        result_path = convert_from_string(
            content=content, output_path=output_path, options=options, config=None
        )

        # Verify
        assert result_path is not None
        assert result_path.name == "my_custom_name.pdf"
        assert result_path.exists()

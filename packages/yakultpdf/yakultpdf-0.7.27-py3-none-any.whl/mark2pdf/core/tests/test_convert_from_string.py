from pathlib import Path

from mark2pdf.core import ConversionOptions, convert_from_string


def test_convert_from_string_uses_output_path_and_images_dir(tmp_path, monkeypatch):
    output_path_base = Path("out") / "result"
    images_dir = tmp_path / "assets" / "images"
    images_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("mark2pdf.core.core.check_pandoc_typst", lambda: None)

    captured = {}

    def fake_execute_in_sandbox(
        *,
        content,
        temp_filename,
        output_path,
        images_source_dir,
        tmp_dir,
        sandbox_prefix,
        options,
        config=None,
        frontmatter=None,
    ):
        captured["output_path"] = output_path
        captured["images_source_dir"] = images_source_dir
        return output_path

    monkeypatch.setattr("mark2pdf.core.core.execute_in_sandbox", fake_execute_in_sandbox)

    result = convert_from_string(
        content="# Hello",
        output_path=output_path_base,
        options=ConversionOptions(),
        images_dir=images_dir,
    )

    expected_output = (tmp_path / output_path_base).with_suffix(".pdf")
    assert result == captured["output_path"]
    assert captured["output_path"] == expected_output
    assert captured["output_path"].is_absolute()
    assert captured["images_source_dir"] == images_dir.parent
    assert (tmp_path / output_path_base.parent).exists()

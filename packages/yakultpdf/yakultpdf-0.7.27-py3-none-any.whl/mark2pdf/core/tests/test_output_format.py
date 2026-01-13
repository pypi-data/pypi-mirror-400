from pathlib import Path

from mark2pdf.core import convert_file


def test_convert_file_output_path_and_call_args(tmp_path, monkeypatch):
    """
    Test that convert_file computes an output path under outdir and passes
    a relative input filename into run_pandoc_typst.
    """
    tmp_path = tmp_path.resolve()

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    tmp_dir = tmp_path / "tmp"
    in_dir.mkdir()
    out_dir.mkdir()
    tmp_dir.mkdir()

    config_content = """
[paths]
in = "in"
out = "out"
tmp = "tmp"
"""
    (tmp_path / "mark2pdf.config.toml").write_text(config_content)

    input_file = in_dir / "test.md"
    input_file.write_text("# Test\nContent")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("mark2pdf.core.core.check_pandoc_typst", lambda: None)

    captured = {}

    def fake_run_pandoc_typst(
        *,
        input_file,
        output_file,
        template_path,
        pandoc_workdir,
        verbose,
        to_typst,
        **kwargs,
    ):
        captured["input_file"] = input_file
        captured["output_file"] = Path(output_file)
        return True

    monkeypatch.setattr("mark2pdf.core.core.run_pandoc_typst", fake_run_pandoc_typst)

    result = convert_file(
        input_file="test.md",
        indir=str(in_dir),
        outdir=str(out_dir),
    )

    assert result == captured["output_file"]
    assert captured["input_file"] == "test.md"
    assert captured["output_file"] == out_dir / "test.pdf"
    assert captured["output_file"].is_absolute()

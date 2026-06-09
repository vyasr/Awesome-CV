import filecmp
import subprocess
import sys
from pathlib import Path

import pytest

from cvgen.loader import load_cv_config, load_professional_data
from cvgen.render import render_all, render_section, SECTION_TITLES, OUTPUT_FILENAMES


class TestSchemaValidation:
    def test_professional_data_loads(self, data_path):
        data = load_professional_data(data_path)
        assert data.schema_version == "1.0"
        assert data.personal_info.name == "Vyas Ramasubramani"
        assert len(data.education) >= 3

    def test_cv_config_loads(self, config_path):
        config = load_cv_config(config_path)
        assert config.schema_version == "1.0"
        assert config.citations.mode in ("selectedpubs", "all", "none", "combinepubs")

    def test_config_sections_reference_valid_ids(self, data_path, config_path):
        """All entry IDs in config must exist in data."""
        from cvgen.loader import resolve_section

        data = load_professional_data(data_path)
        config = load_cv_config(config_path)
        for section_name in SECTION_TITLES:
            section_cfg = getattr(config.sections, section_name, None)
            if section_cfg is not None:
                entries = resolve_section(data, config, section_name)
                assert len(entries) == len(section_cfg.entries)


class TestSectionCompleteness:
    def test_all_configured_sections_generate_files(self, data_path, config_path, tmp_output):
        data = load_professional_data(data_path)
        config = load_cv_config(config_path)
        generated = render_all(data, config, tmp_output)
        generated_names = {p.name for p in generated}
        # citations.tex and selected_pubs.tex always generated
        assert "citations.tex" in generated_names
        assert "selected_pubs.tex" in generated_names
        # At least education must be there
        assert "education.tex" in generated_names

    def test_generated_section_files_non_empty(self, data_path, config_path, tmp_output):
        data = load_professional_data(data_path)
        config = load_cv_config(config_path)
        generated = render_all(data, config, tmp_output)
        for p in generated:
            assert p.stat().st_size > 0, f"{p.name} is empty"

    def test_selected_pubs_contains_configured_citekeys(self, data_path, config_path, tmp_output):
        data = load_professional_data(data_path)
        config = load_cv_config(config_path)
        render_all(data, config, tmp_output)
        selected_pubs = (tmp_output / "selected_pubs.tex").read_text()
        for key in config.citations.selected:
            assert key in selected_pubs, f"Missing cite key: {key}"


class TestIdempotency:
    def test_generation_is_idempotent(self, data_path, config_path, tmp_path):
        """Running generator twice produces identical output."""
        data = load_professional_data(data_path)
        config = load_cv_config(config_path)

        out1 = tmp_path / "run1"
        out2 = tmp_path / "run2"

        render_all(data, config, out1)
        render_all(data, config, out2)

        # Compare all files
        comparison = filecmp.dircmp(str(out1), str(out2))
        assert comparison.diff_files == [], f"Non-identical files: {comparison.diff_files}"
        assert len(list(out1.iterdir())) == len(list(out2.iterdir()))


class TestCompilation:
    @pytest.mark.slow
    def test_generated_files_compile_to_pdf(self, data_path, config_path, tmp_path):
        """Full compilation test: generate .tex and compile with xelatex."""
        import shutil
        from pathlib import Path

        data = load_professional_data(data_path)
        config = load_cv_config(config_path)

        # Generate to temp output
        gen_dir = tmp_path / "cv_output"
        render_all(data, config, gen_dir)

        # Set up a temporary copy of mycv/ with generated files
        mycv_dir = Path(__file__).parent.parent
        tmp_cv_dir = tmp_path / "mycv_copy"
        shutil.copytree(
            str(mycv_dir),
            str(tmp_cv_dir),
            ignore=shutil.ignore_patterns("__pycache__", "*.egg-info", "cv_generated"),
        )

        # Copy generated files to cv/ in the temp copy
        for src in gen_dir.iterdir():
            dst = tmp_cv_dir / "cv" / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(src), str(dst))

        # Run latexmk
        result = subprocess.run(
            ["latexmk", "-xelatex", "-interaction=nonstopmode", "cv.tex"],
            cwd=str(tmp_cv_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, (
            f"latexmk failed (exit {result.returncode}):\n"
            f"STDOUT: {result.stdout[-2000:]}\n"
            f"STDERR: {result.stderr[-500:]}"
        )

        pdf_path = tmp_cv_dir / "cv.pdf"
        assert pdf_path.exists(), "cv.pdf was not produced"
        assert pdf_path.stat().st_size > 1000, "cv.pdf appears too small"

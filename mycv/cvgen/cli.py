from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from .loader import load_cv_config, load_professional_data
from .render import render_all, render_section


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cvgen",
        description="Generate LaTeX CV section files from YAML data",
    )
    _ = parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/professional.yaml"),
        help="Path to professional data YAML (default: data/professional.yaml)",
    )
    _ = parser.add_argument(
        "--config",
        type=Path,
        default=Path("cv_config.yaml"),
        help="Path to CV config YAML (default: cv_config.yaml)",
    )
    _ = parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("cv_generated"),
        help="Output directory for generated .tex files (default: cv_generated/)",
    )
    _ = parser.add_argument(
        "--section",
        type=str,
        default=None,
        help="Render only this section (optional)",
    )

    args = parser.parse_args()
    data_path = cast(Path, args.data)
    config_path = cast(Path, args.config)
    output_dir = cast(Path, args.output_dir)
    section = cast(str | None, args.section)

    try:
        data = load_professional_data(data_path)
        config = load_cv_config(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if section:
            content = render_section(section, data, config)
            filename = section + ".tex"
            out_path = output_dir / filename
            output_dir.mkdir(parents=True, exist_ok=True)
            _ = out_path.write_text(content)
            print(str(out_path))
        else:
            generated = render_all(data, config, output_dir)
            for path in generated:
                print(str(path))
    except Exception as e:
        print(f"Error generating output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

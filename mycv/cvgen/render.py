from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .escape import escape_field, escape_latex
from .loader import resolve_section
from .models import (
    Affiliation,
    CVConfigRoot,
    Grant,
    Honor,
    ProfessionalData,
    Service,
    Skill,
)

TEMPLATES_DIR = Path(__file__).parent / "templates"

SECTION_TITLES = {
    "education": "Education",
    "research_experience": "Research Experience",
    "work_experience": "Work Experience",
    "projects": "Selected Projects",
    "honors": r"Honors \& Awards",
    "service_leadership": "Service and Leadership",
    "teaching_experience": "Teaching Experience",
    "grants": "Grants",
    "extracurricular": "Extracurricular Activity",
    "affiliations": "Professional Affiliations",
    "skills": "Skills",
    "wetlab_skills": "Wet Lab Skills",
}

OUTPUT_FILENAMES = {
    "research_experience": "researchexperience.tex",
    "work_experience": "workexperience.tex",
    "teaching_experience": "teachingexperience.tex",
    "service_leadership": "serviceleadership.tex",
    "wetlab_skills": "wetlabskills.tex",
    "citations": "citations.tex",
    "selected_pubs": "selected_pubs.tex",
}

CVHONORS_WIDTH = {
    "service_leadership": "1.5cm",
    "affiliations": "1.5cm",
}

ENTRY_TEMPLATE = {
    "education": "entry_cventry_education.tex.j2",
    "research_experience": "entry_cventry.tex.j2",
    "work_experience": "entry_cventry.tex.j2",
    "teaching_experience": "entry_cventry.tex.j2",
    "extracurricular": "entry_cventry.tex.j2",
    "projects": "entry_cventry_project.tex.j2",
    "grants": "entry_cventry_grant.tex.j2",
    "honors": "entry_cvhonor.tex.j2",
    "service_leadership": "entry_cvhonor.tex.j2",
    "affiliations": "entry_cvhonor.tex.j2",
    "skills": "entry_cvskill.tex.j2",
    "wetlab_skills": "entry_cvskill.tex.j2",
}

SECTION_TEMPLATE = {
    "education": "section_cventries.tex.j2",
    "research_experience": "section_cventries.tex.j2",
    "work_experience": "section_cventries.tex.j2",
    "teaching_experience": "section_cventries.tex.j2",
    "extracurricular": "section_cventries.tex.j2",
    "projects": "section_cventries.tex.j2",
    "grants": "section_cventries.tex.j2",
    "honors": "section_cvhonors.tex.j2",
    "service_leadership": "section_cvhonors.tex.j2",
    "affiliations": "section_cvhonors.tex.j2",
    "skills": "section_cvskills.tex.j2",
    "wetlab_skills": "section_cvskills.tex.j2",
}


def _make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _build_honor_context(
    entry: Honor | Service | Affiliation,
    entry_config: object,
    env: Environment,
) -> str:
    """Render a single cvhonor entry, handling field name differences."""
    if isinstance(entry, Honor):
        title = escape_field(entry, "title")
        issuer = escape_field(entry, "issuer") if entry.issuer else ""
        location = escape_field(entry, "location") if entry.location else ""
        date = escape_field(entry, "date") if entry.date else ""
    elif isinstance(entry, Service):
        title = escape_field(entry, "role")
        issuer = escape_field(entry, "organization")
        location = escape_field(entry, "location") if entry.location else ""
        date = escape_field(entry, "date") if entry.date else ""
    else:
        title = escape_field(entry, "role") if entry.role else ""
        issuer = escape_field(entry, "organization")
        location = ""
        date = escape_field(entry, "date") if entry.date else ""

    tmpl = env.get_template("entry_cvhonor.tex.j2")
    return tmpl.render(
        entry=entry,
        entry_config=entry_config,
        honor_title=title,
        honor_issuer=issuer,
        honor_location=location,
        honor_date=date,
        escape_field=escape_field,
        escape_latex=escape_latex,
    )


def _get_skill_items(entry: Skill) -> str:
    formatted = entry.formatted
    if isinstance(formatted, Mapping):
        items_override = formatted.get("items")
        if isinstance(items_override, Mapping):
            latex_value = items_override.get("latex")
            if isinstance(latex_value, str):
                return latex_value
    return ", ".join(entry.items)


def _get_grant_date(entry: Grant) -> str:
    if entry.start and entry.end:
        return f"{entry.start} - {entry.end}"
    if entry.start:
        return entry.start
    if entry.end:
        return entry.end
    return ""


def render_section(
    section_name: str,
    data: ProfessionalData,
    config: CVConfigRoot,
    env: Environment | None = None,
) -> str:
    """Render one CV section to LaTeX string."""
    if env is None:
        env = _make_env()

    section_config = getattr(config.sections, section_name, None)
    if section_config is None:
        return ""

    entries = resolve_section(data, config, section_name)
    entries_rendered: list[str] = []

    entry_tmpl_name = ENTRY_TEMPLATE[section_name]

    for entry, entry_config in entries:
        if section_name in ("honors", "service_leadership", "affiliations"):
            if not isinstance(entry, Honor | Service | Affiliation):
                raise TypeError(f"Invalid entry type for section '{section_name}'")
            rendered = _build_honor_context(entry, entry_config, env)
        elif section_name in ("skills", "wetlab_skills"):
            if not isinstance(entry, Skill):
                raise TypeError(f"Invalid entry type for section '{section_name}'")
            entry_tmpl = env.get_template(entry_tmpl_name)
            rendered = entry_tmpl.render(
                entry=entry,
                entry_config=entry_config,
                skill_items=_get_skill_items(entry),
                escape_field=escape_field,
                escape_latex=escape_latex,
            )
        else:
            entry_tmpl = env.get_template(entry_tmpl_name)
            rendered = entry_tmpl.render(
                entry=entry,
                entry_config=entry_config,
                date_str=_get_grant_date(entry) if isinstance(entry, Grant) else "",
                escape_field=escape_field,
                escape_latex=escape_latex,
            )
        entries_rendered.append(rendered)

    section_tmpl = env.get_template(SECTION_TEMPLATE[section_name])
    return section_tmpl.render(
        section_title=SECTION_TITLES[section_name],
        entries_rendered=entries_rendered,
        cvhonors_width=CVHONORS_WIDTH.get(section_name),
    )


def render_citations(config: CVConfigRoot, env: Environment | None = None) -> str:
    _ = config
    if env is None:
        env = _make_env()
    tmpl = env.get_template("citations.tex.j2")
    return tmpl.render()


def render_selected_pubs(config: CVConfigRoot, env: Environment | None = None) -> str:
    if env is None:
        env = _make_env()
    tmpl = env.get_template("selected_pubs.tex.j2")
    return tmpl.render(cite_keys=config.citations.selected)


def render_all(
    data: ProfessionalData,
    config: CVConfigRoot,
    output_dir: Path,
) -> list[Path]:
    """Render all sections and write .tex files. Returns list of generated paths."""
    env = _make_env()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []

    for section_name in SECTION_TITLES:
        section_config = getattr(config.sections, section_name, None)
        if section_config is None:
            continue

        content = render_section(section_name, data, config, env)
        filename = OUTPUT_FILENAMES.get(section_name, f"{section_name}.tex")
        out_path = output_dir / filename
        _ = out_path.write_text(content)
        generated.append(out_path)

    citations_content = render_citations(config, env)
    citations_path = output_dir / "citations.tex"
    _ = citations_path.write_text(citations_content)
    generated.append(citations_path)

    selected_pubs_content = render_selected_pubs(config, env)
    selected_pubs_path = output_dir / "selected_pubs.tex"
    _ = selected_pubs_path.write_text(selected_pubs_content)
    generated.append(selected_pubs_path)

    return generated

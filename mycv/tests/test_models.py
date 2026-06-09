from pathlib import Path
from typing import Literal, TypeAlias

import pytest
from pydantic import ValidationError

from cvgen.loader import load_cv_config, load_professional_data, resolve_section
from cvgen.models import (
    Affiliation,
    CVConfigRoot,
    Education,
    EntryConfig,
    Experience,
    Grant,
    Honor,
    ProfessionalData,
    Project,
    Service,
    Skill,
)

DATA_PATH = Path(__file__).parent.parent / "data" / "professional.yaml"
CONFIG_PATH = Path(__file__).parent.parent / "cv_config.yaml"
Payload: TypeAlias = dict[str, object]
CitationMode: TypeAlias = Literal["selectedpubs", "all", "none", "combinepubs"]


def professional_data_payload() -> Payload:
    return {
        "schema_version": "1.0",
        "personal_info": {"name": "Example Person", "email": "person@example.com"},
    }


def cv_config_payload() -> Payload:
    return {
        "schema_version": "1.0",
        "citations": {"mode": "none"},
        "sections": {"education": {"entries": [{"id": "edu-1"}]}},
    }


def test_professional_data_has_required_fields_and_lists():
    data = ProfessionalData.model_validate(professional_data_payload())

    assert data.schema_version == "1.0"
    assert data.personal_info.name == "Example Person"
    assert data.education == []
    assert data.research_experience == []
    assert data.work_experience == []
    assert data.skills == []
    assert data.projects == []
    assert data.honors == []
    assert data.service_leadership == []
    assert data.teaching_experience == []
    assert data.grants == []
    assert data.extracurricular == []
    assert data.affiliations == []
    assert data.wetlab_skills == []
    assert data.summary is None
    assert data.publications == []
    assert data.presentations == []


@pytest.mark.parametrize(
    "entry",
    [
        Education(
            id="edu-1",
            institution="University",
            degree="PhD",
            area="Computer Science",
            start="2020",
            end="2024",
            location="Remote",
        ),
        Experience(
            id="exp-1",
            organization="Lab",
            role="Researcher",
            start="2020",
            end="2024",
            location="Remote",
        ),
        Project(id="proj-1", name="Project"),
        Honor(id="honor-1", title="Award"),
        Service(id="svc-1", role="Chair", organization="Org"),
        Skill(id="skill-1", category="Languages", items=["Python"]),
        Grant(id="grant-1", title="Grant", funder="NSF", role="PI"),
        Affiliation(id="aff-1", organization="Society"),
    ],
)
def test_entry_models_have_id_field(
    entry: Education | Experience | Project | Honor | Service | Skill | Grant | Affiliation,
):
    assert entry.id


def test_schema_version_1_validates():
    data = ProfessionalData.model_validate(professional_data_payload())

    assert data.schema_version == "1.0"


def test_schema_version_2_raises_validation_error():
    payload = professional_data_payload() | {"schema_version": "2.0"}

    with pytest.raises(ValidationError):
        _ = ProfessionalData.model_validate(payload)


def test_extra_fields_on_education_rejected():
    payload = {
        "id": "edu-1",
        "institution": "University",
        "degree": "PhD",
        "area": "Computer Science",
        "start": "2020",
        "end": "2024",
        "location": "Remote",
        "unexpected": "nope",
    }

    with pytest.raises(ValidationError):
        _ = Education.model_validate(payload)


def test_cv_config_root_validates_with_citations_and_sections():
    config = CVConfigRoot.model_validate(cv_config_payload())

    assert config.schema_version == "1.0"
    assert config.citations.mode == "none"
    assert config.sections.education is not None
    assert config.sections.education.entries[0].id == "edu-1"



def test_entry_config_extra_fields_rejected():
    with pytest.raises(ValidationError):
        _ = EntryConfig.model_validate({"id": "entry-1", "outdated": True})


@pytest.mark.skipif(not DATA_PATH.exists(), reason="data files not yet present")
def test_load_real_professional_data():
    data = load_professional_data(DATA_PATH)

    assert data.schema_version == "1.0"
    assert data.personal_info.name


@pytest.mark.skipif(not CONFIG_PATH.exists(), reason="data files not yet present")
def test_load_real_cv_config():
    config = load_cv_config(CONFIG_PATH)

    assert config.schema_version == "1.0"
    assert config.sections.model_fields_set


def test_resolve_section_returns_entries_in_config_order():
    data = ProfessionalData.model_validate(
        professional_data_payload()
        | {
            "education": [
                {
                    "id": "edu-1",
                    "institution": "First",
                    "degree": "BS",
                    "area": "CS",
                    "start": "2010",
                    "end": "2014",
                    "location": "A",
                },
                {
                    "id": "edu-2",
                    "institution": "Second",
                    "degree": "MS",
                    "area": "CS",
                    "start": "2014",
                    "end": "2016",
                    "location": "B",
                },
            ]
        }
    )
    config = CVConfigRoot.model_validate(
        cv_config_payload()
        | {
            "sections": {
                "education": {"entries": [{"id": "edu-2"}, {"id": "edu-1"}]}
            }
        }
    )

    resolved = resolve_section(data, config, "education")

    assert [entry_config.id for _, entry_config in resolved] == ["edu-2", "edu-1"]
    assert resolved[0][0] == data.education[1]
    assert resolved[1][0] == data.education[0]


def test_resolve_section_raises_on_unknown_section_name():
    data = ProfessionalData.model_validate(professional_data_payload())
    config = CVConfigRoot.model_validate(cv_config_payload())

    with pytest.raises(ValueError, match="Section 'projects' not found in config"):
        _ = resolve_section(data, config, "projects")


def test_resolve_section_raises_on_unknown_entry_id():
    data = ProfessionalData.model_validate(professional_data_payload())
    config = CVConfigRoot.model_validate(cv_config_payload())

    with pytest.raises(ValueError, match="Entry ID 'edu-1' not found"):
        _ = resolve_section(data, config, "education")


@pytest.mark.parametrize("mode", ["selectedpubs", "all", "none", "combinepubs"])
def test_citations_config_validates_mode_options(mode: CitationMode):
    payload = cv_config_payload() | {"citations": {"mode": mode}}
    config = CVConfigRoot.model_validate(payload)

    assert config.citations.mode == mode


def test_citations_config_rejects_unknown_mode():
    payload = cv_config_payload() | {"citations": {"mode": "invalid"}}

    with pytest.raises(ValidationError):
        _ = CVConfigRoot.model_validate(payload)


# --- CVOptions and CVTheme tests ---

from cvgen.models import CVOptions, CVTheme  # noqa: E402 (appended)


def test_cv_config_root_defaults_options_and_theme():
    config = CVConfigRoot.model_validate(cv_config_payload())

    assert config.options.font_size == "11pt"
    assert config.options.paper_size == "a4paper"
    assert config.options.compact is False
    assert config.theme.color == "awesome-emerald"
    assert config.theme.section_color_highlight is True


def test_cv_options_accepts_valid_values():
    payload = cv_config_payload() | {
        "options": {
            "font_size": "10pt",
            "paper_size": "letterpaper",
            "compact": True,
        }
    }
    config = CVConfigRoot.model_validate(payload)

    assert config.options.font_size == "10pt"
    assert config.options.paper_size == "letterpaper"
    assert config.options.compact is True


def test_cv_theme_accepts_valid_color():
    payload = cv_config_payload() | {"theme": {"color": "awesome-skyblue"}}
    config = CVConfigRoot.model_validate(payload)

    assert config.theme.color == "awesome-skyblue"


def test_cv_theme_rejects_invalid_color():
    payload = cv_config_payload() | {"theme": {"color": "awesome-purple"}}

    with pytest.raises(ValidationError):
        _ = CVConfigRoot.model_validate(payload)


def test_cv_options_rejects_invalid_font_size():
    payload = cv_config_payload() | {"options": {"font_size": "14pt"}}

    with pytest.raises(ValidationError):
        _ = CVConfigRoot.model_validate(payload)


def test_cv_options_rejects_extra_fields():
    with pytest.raises(ValidationError):
        _ = CVOptions.model_validate({"unknown_field": "x"})


@pytest.mark.parametrize(
    "color",
    [
        "awesome-emerald",
        "awesome-skyblue",
        "awesome-red",
        "awesome-pink",
        "awesome-orange",
        "awesome-nephritis",
        "awesome-concrete",
        "awesome-darknight",
    ],
)
def test_cv_theme_accepts_all_valid_colors(color: str):
    payload = cv_config_payload() | {"theme": {"color": color}}
    config = CVConfigRoot.model_validate(payload)

    assert config.theme.color == color

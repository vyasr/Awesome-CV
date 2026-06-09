"""Tests for render_cv_tex — verifying personal info, options, and theme are correctly passed to the template."""
from __future__ import annotations

import pytest

from professional_data.schema import PersonalInfo, ProfessionalData
from cvgen.models import CVConfigRoot
from cvgen.render import render_cv_tex


def _minimal_data(
    *,
    first_name: str = "Test",
    last_name: str = "User",
    name: str = "Test User",
    email: str = "test@example.com",
    **kwargs: object,
) -> ProfessionalData:
    return ProfessionalData(
        schema_version="1.0",
        personal_info=PersonalInfo(
            name=name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            **kwargs,  # type: ignore[arg-type]
        ),
    )


def _minimal_config(**overrides: object) -> CVConfigRoot:
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "citations": {"mode": "none"},
        "sections": {},
    }
    payload.update(overrides)
    return CVConfigRoot.model_validate(payload)


class TestRenderPersonalInfo:
    def test_name_renders_correctly(self) -> None:
        data = _minimal_data(first_name="Vyas", last_name="Ramasubramani", name="Vyas Ramasubramani")
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\name{Vyas}{Ramasubramani}" in result

    def test_email_always_rendered(self) -> None:
        data = _minimal_data(email="vyas@example.com")
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\email{vyas@example.com}" in result

    def test_github_rendered_when_present(self) -> None:
        data = _minimal_data(github="vyasr")
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\github{vyasr}" in result

    def test_github_absent_when_not_set(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\github" not in result

    def test_gitlab_rendered_when_present(self) -> None:
        data = _minimal_data(gitlab="vyasr")
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\gitlab{vyasr}" in result

    def test_gitlab_absent_when_not_set(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\gitlab" not in result

    def test_stackexchange_renders_id_and_name(self) -> None:
        data = _minimal_data(stackexchange={"id": "2575105", "name": "Vyas"})
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\stackexchange{2575105}{Vyas}" in result

    def test_stackexchange_absent_when_not_set(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\stackexchange" not in result

    def test_googlescholar_renders_id_and_name(self) -> None:
        data = _minimal_data(googlescholar={"id": "vyLxpbkAAAAJ", "name": "Vyas"})
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\googlescholar{vyLxpbkAAAAJ}{Vyas}" in result

    def test_googlescholar_absent_when_not_set(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\googlescholar" not in result

    def test_mobile_rendered_when_present(self) -> None:
        data = _minimal_data(phone="(+1) 408-421-2162")
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\mobile{(+1) 408-421-2162}" in result

    def test_mobile_absent_when_not_set(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\mobile" not in result

    def test_homepage_rendered_when_present(self) -> None:
        data = _minimal_data(website="vyasr.com")
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\homepage{vyasr.com}" in result

    def test_homepage_absent_when_not_set(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\homepage" not in result

    def test_footer_contains_full_name(self) -> None:
        data = _minimal_data(name="Vyas Ramasubramani")
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert "Vyas Ramasubramani" in result


class TestRenderOptions:
    def test_default_font_and_paper_size(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        docclass_line = next(l for l in result.split("\n") if r"\documentclass" in l)
        assert "11pt" in docclass_line
        assert "a4paper" in docclass_line

    def test_custom_font_size(self) -> None:
        data = _minimal_data()
        config = _minimal_config(options={"font_size": "10pt"})
        result = render_cv_tex(config, [], data=data)
        docclass_line = next(l for l in result.split("\n") if r"\documentclass" in l)
        assert "10pt" in docclass_line

    def test_compact_option_in_documentclass(self) -> None:
        data = _minimal_data()
        config = _minimal_config(options={"compact": True})
        result = render_cv_tex(config, [], data=data)
        docclass_line = next(l for l in result.split("\n") if r"\documentclass" in l)
        assert "compact" in docclass_line

    def test_compact_absent_by_default(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        docclass_line = next(l for l in result.split("\n") if r"\documentclass" in l)
        assert "compact" not in docclass_line
    def test_citations_mode_in_documentclass(self) -> None:
        data = _minimal_data()
        config = _minimal_config(citations={"mode": "all"})
        result = render_cv_tex(config, [], data=data)
        docclass_line = next(l for l in result.split("\n") if r"\documentclass" in l)
        assert "citations=all" in docclass_line


class TestRenderTheme:
    def test_default_color(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\colorlet{awesome}{awesome-emerald}" in result

    def test_custom_color(self) -> None:
        data = _minimal_data()
        config = _minimal_config(theme={"color": "awesome-skyblue"})
        result = render_cv_tex(config, [], data=data)
        assert r"\colorlet{awesome}{awesome-skyblue}" in result

    def test_section_color_highlight_true(self) -> None:
        data = _minimal_data()
        config = _minimal_config()
        result = render_cv_tex(config, [], data=data)
        assert r"\setbool{acvSectionColorHighlight}{true}" in result

    def test_section_color_highlight_false(self) -> None:
        data = _minimal_data()
        config = _minimal_config(theme={"section_color_highlight": False})
        result = render_cv_tex(config, [], data=data)
        assert r"\setbool{acvSectionColorHighlight}{false}" in result

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
    def test_all_valid_colors_render(self, color: str) -> None:
        data = _minimal_data()
        config = _minimal_config(theme={"color": color})
        result = render_cv_tex(config, [], data=data)
        assert rf"\colorlet{{awesome}}{{{color}}}" in result

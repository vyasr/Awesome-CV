from types import SimpleNamespace

from cvgen.escape import escape_field, escape_latex, is_raw_latex


class TestEscapeLatex:
    def test_ampersand(self):
        assert escape_latex("&") == "\\&"

    def test_percent(self):
        assert escape_latex("%") == "\\%"

    def test_dollar(self):
        assert escape_latex("$") == "\\$"

    def test_hash(self):
        assert escape_latex("#") == "\\#"

    def test_underscore(self):
        assert escape_latex("_") == "\\_"

    def test_open_brace(self):
        assert escape_latex("{") == "\\{"

    def test_close_brace(self):
        assert escape_latex("}") == "\\}"

    def test_tilde(self):
        assert escape_latex("~") == "\\textasciitilde{}"

    def test_caret(self):
        assert escape_latex("^") == "\\textasciicircum{}"

    def test_backslash(self):
        assert escape_latex("\\") == "\\textbackslash{}"

    def test_empty_string(self):
        assert escape_latex("") == ""

    def test_no_special_chars(self):
        assert escape_latex("Hello World") == "Hello World"

    def test_multiple_special_chars(self):
        result = escape_latex("50% off & save $10")
        assert "\\%" in result
        assert "\\&" in result
        assert "\\$" in result

    def test_no_double_escape_backslash(self):
        result = escape_latex("a\\b")
        assert "\\textbackslash{}" in result
        assert result.count("\\textbackslash{}") == 1

    def test_periods_and_commas_not_escaped(self):
        text = "D.C. Energy, LLC: Finance"
        assert escape_latex(text) == text


class TestEscapeField:
    def test_without_formatted_override(self):
        entry = SimpleNamespace(name="D.C. Energy & Associates", formatted=None)
        result = escape_field(entry, "name")
        assert "\\&" in result

    def test_with_formatted_latex_override(self):
        entry = SimpleNamespace(
            name="signac",
            formatted={"name": {"latex": "signac ({\\tiny github.com/glotzerlab/signac})"}},
        )
        result = escape_field(entry, "name")
        assert "\\tiny" in result
        assert "\\&" not in result

    def test_formatted_none_falls_through(self):
        entry = SimpleNamespace(name="50% discount", formatted=None)
        result = escape_field(entry, "name")
        assert "\\%" in result

    def test_formatted_wrong_field_falls_through(self):
        entry = SimpleNamespace(name="50% discount", formatted={"other_field": {"latex": "something"}})
        result = escape_field(entry, "name")
        assert "\\%" in result

    def test_formatted_no_latex_key_falls_through(self):
        entry = SimpleNamespace(name="50% discount", formatted={"name": {"text": "no latex key"}})
        result = escape_field(entry, "name")
        assert "\\%" in result


class TestIsRawLatex:
    def test_detects_latex_command(self):
        assert is_raw_latex("\\textsc{expert}") is True

    def test_detects_backslash_command(self):
        assert is_raw_latex("\\tiny url") is True

    def test_plain_text_returns_false(self):
        assert is_raw_latex("Hello World") is False

    def test_empty_string_returns_false(self):
        assert is_raw_latex("") is False

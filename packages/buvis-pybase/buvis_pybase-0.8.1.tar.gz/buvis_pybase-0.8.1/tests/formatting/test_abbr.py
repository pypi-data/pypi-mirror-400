from __future__ import annotations

from buvis.pybase.formatting.string_operator.abbr import Abbr


class TestAbbr:
    def test_replaces_with_provided_abbreviations(self) -> None:
        result = Abbr.replace_abbreviations(
            "Use the API and CLI",
            abbreviations=[
                {"API": "Application Programming Interface"},
                {"CLI": "Command Line Interface"},
            ],
            level=1,
        )

        assert (
            result
            == "Use the Application Programming Interface and Command Line Interface"
        )

    def test_no_abbreviations_returns_original_text(self) -> None:
        result = Abbr.replace_abbreviations("Use the API", level=1)

        assert result == "Use the API"

    def test_empty_abbreviations_list_is_ignored(self) -> None:
        result = Abbr.replace_abbreviations(
            "Use the API",
            abbreviations=[],
            level=1,
        )

        assert result == "Use the API"

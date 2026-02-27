# -*- encoding: utf-8 -*-

"""Unit tests for email header parsing functions."""

from apps.gmail.services.sync import parse_email_addresses, parse_display_name


def test_parse_single_email():
    assert parse_email_addresses("foo@bar.com") == ["foo@bar.com"]


def test_parse_display_name_email():
    result = parse_email_addresses('"John Doe" <john@example.com>')
    assert result == ["john@example.com"]


def test_parse_multiple_emails():
    result = parse_email_addresses("a@b.com, c@d.com, Foo <e@f.com>")
    assert result == ["a@b.com", "c@d.com", "e@f.com"]


def test_parse_case_normalization():
    assert parse_email_addresses("FOO@BAR.COM") == ["foo@bar.com"]


def test_parse_empty_string():
    assert parse_email_addresses("") == []


def test_parse_none():
    assert parse_email_addresses(None) == []


def test_parse_complex_header():
    header = '"Alice Smith" <alice@company.com>, bob@example.org, "Charlie" <charlie@test.co>'
    result = parse_email_addresses(header)
    assert len(result) == 3
    assert "alice@company.com" in result
    assert "bob@example.org" in result
    assert "charlie@test.co" in result


def test_parse_display_name_simple():
    assert parse_display_name('"John Doe" <john@example.com>') == "John Doe"


def test_parse_display_name_without_quotes():
    result = parse_display_name('Alice Smith <alice@example.com>')
    assert result == "Alice Smith"


def test_parse_display_name_email_only():
    result = parse_display_name('john@example.com')
    assert result is None


def test_parse_display_name_none():
    assert parse_display_name(None) is None


def test_parse_display_name_empty():
    assert parse_display_name("") is None

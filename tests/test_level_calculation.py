# -*- encoding: utf-8 -*-

"""Unit tests for contact level calculation."""

from datetime import datetime, timedelta
from apps.gmail.services.level import calculate_level


def test_no_interaction():
    assert calculate_level(0, 0, None) == -1


def test_level_0_outbound_only():
    now = datetime.utcnow()
    assert calculate_level(0, 3, now, now) == 0


def test_level_0_inbound_only():
    now = datetime.utcnow()
    assert calculate_level(2, 0, now, now) == 0


def test_level_1_bidirectional_minimum():
    now = datetime.utcnow()
    assert calculate_level(1, 1, now, now) == 1


def test_level_1_bidirectional_more():
    now = datetime.utcnow()
    assert calculate_level(1, 5, now, now) == 1


def test_level_2_stable_recent():
    now = datetime.utcnow()
    recent = now - timedelta(days=100)
    assert calculate_level(2, 2, recent, now) == 2


def test_level_2_stable_boundary():
    now = datetime.utcnow()
    boundary = now - timedelta(days=900)
    assert calculate_level(2, 2, boundary, now) == 2


def test_level_2_too_old():
    now = datetime.utcnow()
    old = now - timedelta(days=901)
    assert calculate_level(2, 2, old, now) == 1


def test_level_3_active():
    now = datetime.utcnow()
    recent = now - timedelta(days=30)
    assert calculate_level(5, 4, recent, now) == 3


def test_level_3_boundary():
    now = datetime.utcnow()
    boundary = now - timedelta(days=180)
    assert calculate_level(3, 3, boundary, now) == 3


def test_level_3_minimum_counts():
    now = datetime.utcnow()
    recent = now - timedelta(days=10)
    assert calculate_level(3, 3, recent, now) == 3


def test_level_3_too_old_falls_to_2():
    now = datetime.utcnow()
    semi_old = now - timedelta(days=200)
    assert calculate_level(3, 3, semi_old, now) == 2


def test_level_3_not_enough_inbound():
    now = datetime.utcnow()
    recent = now - timedelta(days=10)
    assert calculate_level(2, 5, recent, now) == 2


def test_level_3_not_enough_outbound():
    now = datetime.utcnow()
    recent = now - timedelta(days=10)
    assert calculate_level(5, 2, recent, now) == 2


def test_level_progression():
    """Test that levels correctly progress upward."""
    now = datetime.utcnow()
    recent = now - timedelta(days=10)

    assert calculate_level(0, 0, None, now) == -1
    assert calculate_level(1, 0, recent, now) == 0
    assert calculate_level(0, 1, recent, now) == 0
    assert calculate_level(1, 1, recent, now) == 1
    assert calculate_level(2, 2, recent, now) == 2
    assert calculate_level(3, 3, recent, now) == 3


def test_high_counts_old_date():
    """Many emails but very old interaction should cap at Level 1."""
    now = datetime.utcnow()
    very_old = now - timedelta(days=1000)
    assert calculate_level(100, 100, very_old, now) == 1

"""Tests for the netconvert module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from osm_to_xodr.netconvert import (
    NetconvertNotFoundError,
    NetconvertResult,
    check_netconvert_available,
    find_netconvert,
)


def test_netconvert_result_dataclass() -> None:
    """Test NetconvertResult dataclass."""
    result = NetconvertResult(
        success=True,
        command=["netconvert", "--version"],
        stdout="SUMO netconvert Version 1.20.0",
        stderr="",
        returncode=0,
    )

    assert result.success is True
    assert result.returncode == 0
    assert "netconvert" in result.command


def test_find_netconvert_system() -> None:
    """Test finding system netconvert."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/netconvert"
        cmd = find_netconvert()
        assert cmd == ["netconvert"]


def test_find_netconvert_flatpak() -> None:
    """Test finding Flatpak netconvert."""
    with (
        patch("shutil.which") as mock_which,
        patch("subprocess.run") as mock_run,
    ):
        # System netconvert not found, but Flatpak is
        mock_which.side_effect = lambda x: None if x == "netconvert" else "/usr/bin/flatpak"
        mock_run.return_value = MagicMock(stdout="org.eclipse.sumo\t1.20.0")

        cmd = find_netconvert()
        assert cmd == ["flatpak", "run", "--command=netconvert", "org.eclipse.sumo"]


def test_find_netconvert_not_found() -> None:
    """Test NetconvertNotFoundError when not available."""
    import pytest

    with patch("shutil.which") as mock_which:
        mock_which.return_value = None

        with pytest.raises(NetconvertNotFoundError, match="netconvert not found"):
            find_netconvert()


def test_check_netconvert_available_true() -> None:
    """Test check_netconvert_available returns True when available."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/netconvert"
        assert check_netconvert_available() is True


def test_check_netconvert_available_false() -> None:
    """Test check_netconvert_available returns False when not available."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = None
        assert check_netconvert_available() is False

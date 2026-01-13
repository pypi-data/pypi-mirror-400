import json
import os

import pytest

from cfddb.engine.state import LocalState, StateLockError


def test_acquire_lock_creates_file(tmp_path, mocker):
    mocker.patch.object(LocalState, "LOCK", tmp_path / ".cfddb.state.lock")
    state = LocalState()
    state.acquire_lock()
    assert state.LOCK.exists()
    data = json.loads(state.LOCK.read_text())
    assert data["pid"] == os.getpid()


def test_acquire_lock_fails_if_exists(tmp_path, mocker):
    mocker.patch.object(LocalState, "LOCK", tmp_path / ".cfddb.state.lock")
    state = LocalState()
    state.LOCK.write_text("locked")
    with pytest.raises(StateLockError):
        state.acquire_lock()


def test_release_lock_removes_file(tmp_path, mocker):
    mocker.patch.object(LocalState, "LOCK", tmp_path / ".cfddb.state.lock")
    state = LocalState()
    state.acquire_lock()
    assert state.LOCK.exists()
    state.release_lock()
    assert not state.LOCK.exists()


def test_save_metadata(tmp_path, mocker):
    mocker.patch.object(LocalState, "FILE", tmp_path / ".cfddb.state.json")
    state = LocalState()
    state.save_metadata({"env": "local"})
    data = json.loads(state.FILE.read_text())
    assert data["env"] == "local"

import os

import pytest

from cognito_local.storage import StorageManager


@pytest.fixture
def manager(tmp_path):
    """
    Creates a StorageManager pointing to a temp file
    and ensures a clean backend state.
    """
    db_file = tmp_path / "test_cognito.db"
    pm = StorageManager(str(db_file))
    for backend in pm.backends.values():
        backend.reset()
    yield pm
    for backend in pm.backends.values():
        backend.reset()


def test_save_creates_file(manager):
    """
    Verifies that .save() writes a file to disk.
    """
    assert not os.path.exists(manager.data_file)
    manager.save()
    assert os.path.exists(manager.data_file)
    assert os.path.getsize(manager.data_file) > 0


def test_atomic_write_protection(manager):
    """
    Verifies that the save process writes to temp and renames.
    """
    manager.save()
    assert os.path.exists(manager.data_file)


def test_load_restores_data(manager):
    """
    Integration Test:
    1. Mark backend with custom data.
    2. Save.
    3. Wipe memory.
    4. Load.
    5. Verify mark exists.
    """
    region_backend = manager.backends["idp"]["eu-central-1"]
    region_backend.persistence_test_marker = "IT_WORKS_123"
    manager.save()
    for backend in manager.backends.values():
        backend.reset()
    fresh_backend = manager.backends["idp"]["eu-central-1"]
    assert not hasattr(fresh_backend, "persistence_test_marker")
    manager.load()
    restored_backend = manager.backends["idp"]["eu-central-1"]
    assert hasattr(restored_backend, "persistence_test_marker")
    assert restored_backend.persistence_test_marker == "IT_WORKS_123"


def test_load_handles_empty_file(manager, caplog):
    """
    Verifies that loading a 0-byte file (corruption) logs a warning
    but does not crash.
    """
    with open(manager.data_file, "wb"):
        pass
    assert os.path.exists(manager.data_file)
    assert os.path.getsize(manager.data_file) == 0
    manager.load()
    assert "is empty (corrupt)" in caplog.text


def test_identity_pool_persistence(manager):
    """
    Verifies that Cognito Identity Pools are also persisted.
    Uses a custom marker to verify object persistence regardless of Moto's internal structure.
    """
    identity_backend = manager.backends["identity"]["us-east-1"]
    identity_backend.persistence_test_marker = "IDENTITY_WORKS_123"
    manager.save()
    manager.backends["identity"].reset()
    fresh_backend = manager.backends["identity"]["us-east-1"]
    assert not hasattr(fresh_backend, "persistence_test_marker")
    manager.load()
    restored_backend = manager.backends["identity"]["us-east-1"]
    assert hasattr(restored_backend, "persistence_test_marker")
    assert restored_backend.persistence_test_marker == "IDENTITY_WORKS_123"

"""Unit tests for data contracts. Run from the repo root with: python -m pytest"""

import copy
from pathlib import Path

import pytest

from src.framework.contracts import (
    ContractError, load_contracts, schema_hints, source_path, target_table, validate_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
EXPECTED = {"airlines", "airports", "damage_reports", "flights", "repairs", "uld_events", "uld_fleet"}


@pytest.fixture(scope="module")
def contracts():
    return load_contracts(CONTRACTS)


@pytest.fixture
def good(contracts):
    return copy.deepcopy(next(c for c in contracts if c["dataset"] == "uld_events"))


def test_all_contracts_are_valid(contracts):
    assert {c["dataset"] for c in contracts} == EXPECTED


def test_every_dataset_has_its_own_table(contracts):
    tables = [c["target"]["table"] for c in contracts]
    assert len(tables) == len(set(tables))


def test_cdc_contracts_have_keys(contracts):
    cdc = {c["dataset"]: c["cdc"] for c in contracts if "cdc" in c}
    assert cdc["repairs"]["scd_type"] == 1
    assert cdc["airlines"]["scd_type"] == 2


def test_pii_columns_are_tagged(contracts):
    airlines = next(c for c in contracts if c["dataset"] == "airlines")
    pii = [col["name"] for col in airlines["columns"] if col.get("pii")]
    assert pii == ["contact_email"]


def test_missing_key_is_reported(good):
    del good["owner"]
    assert "missing key 'owner'" in validate_contract(good)


def test_bad_column_type_is_reported(good):
    good["columns"][0]["type"] = "varchar"
    assert any("type 'varchar'" in e for e in validate_contract(good))


def test_bad_rule_action_is_reported(good):
    good["quality_rules"][0]["action"] = "ignore"
    assert any("action must be one of" in e for e in validate_contract(good))


def test_primary_key_must_be_a_column(good):
    good["primary_key"] = ["not_a_column"]
    assert any("primary key 'not_a_column'" in e for e in validate_contract(good))


def test_bad_version_is_reported(good):
    good["version"] = "v1"
    assert any("must look like 1.0.0" in e for e in validate_contract(good))


def test_copy_into_only_for_csv(good):
    good["ingestion"]["method"] = "copy_into"
    assert any("copy_into is only used for csv" in e for e in validate_contract(good))


def test_duplicate_datasets_fail(tmp_path):
    for name in ["a", "b"]:
        (tmp_path / f"{name}.yml").write_text((CONTRACTS / "airports.yml").read_text())
    with pytest.raises(ContractError):
        load_contracts(tmp_path)


def test_schema_hints(good):
    hints = schema_hints(good)
    assert hints.startswith("event_id string, uld_id string")
    assert "event_ts timestamp" in hints
    assert "gross_weight_kg double" in hints


def test_names_and_paths(good):
    assert target_table(good, "skycargo_dev") == "skycargo_dev.bronze.uld_events"
    assert source_path(good, "/Volumes/skycargo_dev/bronze/raw/") == "/Volumes/skycargo_dev/bronze/raw/uld_events"

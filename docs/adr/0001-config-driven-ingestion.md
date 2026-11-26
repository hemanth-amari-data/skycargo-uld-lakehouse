# ADR 0001: Config-driven ingestion with data contracts

**Status:** Accepted
**Date:** 2026-11-22

## Context
SkyCargo receives data from seven sources with different formats: JSON events, CSV schedules,
a CDC feed, master data, reference files and text documents. Writing one notebook per source
leads to copied code, different patterns per source, and no single place that says what each
source should look like or who owns it.

## Decision
- Every source has a **data contract** (`contracts/<dataset>.yml`). It holds the schema, owner,
  SLA, tags, PII flags, CDC keys and quality rules.
- One **framework** (`src/framework`) reads the contracts and loads bronze tables.
  - JSON and files: **Auto Loader**, incremental, with schema evolution (`addNewColumns`)
    and a rescued data column.
  - CSV: **COPY INTO**, which is idempotent and skips files it has already loaded.
- The framework copies descriptions, tags and properties from the contract to each table.
- The framework compares each table with its contract and logs differences (**contract drift**)
  to `ops.contract_drift`.
- Every run is logged to `ops.ingestion_log`.
- Contracts are validated in unit tests, so a broken contract fails CI before deployment.

## Consequences
- Adding a source means adding a YAML file, not writing code.
- The contract is the single source of truth for documentation, governance and quality.
- The framework is more complex than one notebook per source, and needs tests.
- Quality rules live in the contract but are enforced in silver (Phase 3), not in bronze.

# ADR 0002: Bronze keeps data as it arrived

**Status:** Accepted
**Date:** 2026-11-22

## Context
Source data contains bad rows: missing ids, unknown airports, future timestamps and duplicates.
Sources also add new columns without warning.

## Decision
- Bronze does **not** filter, fix or de-duplicate rows. It is an exact, replayable copy of the source.
- Every bronze row gets audit columns: `_source_file`, `_file_modified_at`, `_ingested_at`, `_ingest_run_id`.
- JSON sources use **schema hints** from the contract, so columns that start as NULL
  (for example `actual_cost_usd`) still get the right type. Values that do not fit go to `_rescued_data`.
- CSV sources are loaded as **strings**. CSV has no types, so we do not guess. Types are applied in silver.
- New source columns are **added automatically** and reported as contract drift, instead of failing the load.

## Consequences
- Silver can always be rebuilt from bronze.
- Any row can be traced back to its source file and ingestion run.
- Data quality problems stay visible in bronze and are handled in one place (silver).
- Bronze tables use more storage, because nothing is removed.

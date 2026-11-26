# SkyCargo ULD Lakehouse

**A real-time ULD control tower for a Dubai-based air cargo network, built end to end on Databricks.**

Airlines own thousands of ULDs (Unit Load Devices: the containers and pallets that carry air cargo).
ULDs get stuck at the wrong airport, sit idle, get damaged or go missing, and every one of these costs money.
SkyCargo tracks every ULD across 17 airports and answers four questions:

1. **Where is every ULD right now?**
2. **Which ULDs are idle, damaged or missing, and what does it cost?**
3. **Which airports will run short of ULDs next week?**
4. **Can anyone ask in plain English and get a trusted answer?** (Genie and a RAG chatbot)

> All data is synthetic. All airline names are fictional.

## Architecture

```
Sources                 Ingestion              Bronze -> Silver -> Gold            Serving
ULD scan events  --->  Auto Loader       --->  Raw  -> Clean + DQ -> Star schema --> AI/BI dashboards, Genie
Flights (CSV)    --->  COPY INTO               + quarantine         + metric views --> Lakebase + Databricks App
Repairs (CDC)    --->  Config-driven     --->  CDC / SCD2 -> Features             --> Delta Sharing
Airlines (SCD2)        framework (YAML)                                           --> Model Serving
Damage reports   --->  AI Functions      --->  Vector index -> RAG agent          --> Chatbot

Across everything: Unity Catalog, data contracts, observability, Asset Bundles + CI/CD, tests
```

## Project status

| Phase | Focus | Status |
|---|---|---|
| 1 | Unity Catalog setup and synthetic source system | Done |
| 2 | Data contracts and config-driven bronze ingestion | Done |
| 3 | Silver: data quality, quarantine, CDC, SCD Type 2, late data | Next |
| 4 | Gold: star schema and metric views | Planned |
| 5 | Orchestration, backfills and replay | Planned |
| 6 | Scale (100M+ events) and performance benchmarks | Planned |
| 7 | Governance: ABAC, row filters, column masks | Planned |
| 8 | DevOps: Asset Bundles, CI/CD, tests | Planned |
| 9 | Observability and cost | Planned |
| 10 | Analytics: AI/BI dashboards and Genie | Planned |
| 11 | ML: ULD demand forecast | Planned |
| 12 | RAG knowledge base and Vector Search | Planned |
| 13 | AI agent with tools, tracing and evaluation | Planned |
| 14 | Chatbot app with Lakebase and user-level security | Planned |
| 15 | Delta Sharing, demo video and write-up | Planned |

## Repository layout

```
contracts/                 Data contracts, one YAML per source
src/
  setup/                   Unity Catalog setup (catalog, schemas, volume)
  data_generator/          Synthetic source system (stateful simulator)
  framework/               Reusable Python: contract loader and bronze ingestion
  ingestion/               Notebooks that run the framework and explore bronze
tests/                     Unit tests (run with: python -m pytest)
docs/adr/                  Architecture Decision Records
```

## Data sources (simulated)

| Source | Format | Pattern it teaches |
|---|---|---|
| ULD scan events | JSON lines | Streaming with Auto Loader, schema evolution, bad data |
| Flight schedule | CSV per day | Idempotent batch load with COPY INTO |
| Repair system | JSON CDC feed | INSERT / UPDATE / DELETE, SCD Type 1 |
| Airline master | JSON changes | Full history with SCD Type 2, PII |
| Airports, ULD fleet | CSV | Reference data |
| Damage reports | Text files | Unstructured data for AI and RAG |

## How to run

1. `src/setup/01_unity_catalog_setup` - creates the catalog, schemas and landing Volume
2. `src/data_generator/02_generate_reference_data` - run once
3. `src/data_generator/03_generate_daily_data` - run as often as you like, one day per run
4. `src/ingestion/01_run_bronze_ingestion` - loads all sources into bronze
5. `src/ingestion/02_explore_bronze` - checks and examples

Run tests locally:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Key design decisions

- [ADR 0001: Config-driven ingestion with data contracts](docs/adr/0001-config-driven-ingestion.md)
- [ADR 0002: Bronze keeps data as it arrived](docs/adr/0002-raw-bronze-layer.md)

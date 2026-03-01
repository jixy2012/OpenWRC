# OpenWRC

A local data sink and query toolkit for WRC (World Rally Championship) event data.

OpenWRC fetches data from the official WRC API and stores it in a local SQLite database, then exposes clean Python interfaces for exploring it — either programmatically via a session object or interactively via a terminal CLI.

---

## Architecture

The project is split into two layers:

### `src/openwrc/` — Core library

The core package handles everything related to data: fetching, storing, and querying.

**Data sink** — `WrcApiClient` pulls event data from the WRC API. `DataStoreService` maps the API responses into local DB models and persists them via SQLAlchemy. The local database (`wrc.db`) is a SQLite file that acts as a cache of WRC event data.

**Session interface** — `WrcSession` is the main entry point for working with stored data. It resolves an event and rally once at creation time, then exposes query methods that use those resolved IDs automatically. Callers never have to manage IDs directly.

```python
session = await WrcSession.create(name="monte carlo", year=2026)

standings = await session.rally_standings()
split_times = await session.split_times(stage_number=3)
entries = await session.entries()
stages = await session.stages()
```

Before creating a session, two class methods let you discover what's available in the local DB:

```python
years = await WrcSession.list_available_years()
events = await WrcSession.list_events_for_year(2026)
```

### `src/cli/` — Interactive CLI

A terminal interface built on top of the session. Guides the user through year → event → data type selection using arrow-key menus, then displays results as formatted tables.

```
$ python -m cli
```

---

## Setup

**Install dependencies:**
```bash
uv pip install -e .
```

**Populate the local database** by running the data store service for the events you want. See `src/openwrc/storage/data_store_service.py`.

---

```markdown
# FluxDB Python Driver

![PyPI Version](https://img.shields.io/pypi/v/fluxdb-driver)
![License](https://img.shields.io/pypi/l/fluxdb-driver)
![Python](https://img.shields.io/pypi/pyversions/fluxdb-driver)

The official Python client for **FluxDB**, a high-performance, in-memory NoSQL database featuring adaptive indexing and real-time pub/sub capabilities.

## 🚀 Features

* **Hybrid Storage**: Combines in-memory speed with WAL (Write-Ahead Log) durability.
* **Adaptive Indexing**: Automatically creates Hash or B-Tree indexes based on your query patterns.
* **Real-Time Pub/Sub**: Built-in lightweight messaging system for event-driven apps.
* **Smart Querying**: Rich support for operators like `$gt`, `$lt`, `$ne`, and range queries.
* **Time-To-Live (TTL)**: Auto-expire documents for caching or temporary data.

## 📦 Installation

```bash
pip install fluxdb-driver

```

## ⚡ Quick Start

### Connecting

By default, FluxDB runs on `localhost:8080`.

```python
from fluxdb import FluxDB

# Connect with authentication (default password: 'flux_admin')
db = FluxDB(host='127.0.0.1', port=8080, password='flux_admin')

# Create or switch to a database
db.use("game_data")

```

### CRUD Operations

```python
# 1. Insert a document
hero_id = db.insert({
    "username": "DragonSlayer",
    "level": 50,
    "inventory": ["sword", "shield"]
})
print(f"Created Hero ID: {hero_id}")

# 2. Find (Smart Query)
# Find players with level > 20
high_level_players = db.find({"level": {"$gt": 20}})

# 3. Update
db.update(hero_id, {"level": 51})

# 4. Get by ID
doc = db.get(hero_id)

# 5. Delete
db.delete(hero_id)

```

### 🧠 Advanced Features

#### Adaptive Indexing

Turn on adaptive mode to let the database optimize itself based on query misses.

```python
db.toggle_adaptive(True)

```

#### Pub/Sub Messaging

FluxDB can act as a message broker.

```python
def on_news(msg):
    print(f"Received: {msg}")

# Subscribe (Blocking)
# Run this in a separate thread or process
db.subscribe("news_channel", on_news)

# Publish (from another client)
db.publish("news_channel", "Maintenance in 5 minutes!")

```

#### Time-To-Live (TTL)

Set a document to auto-delete after a specific time (in seconds).

```python
cache_id = db.insert({"session_key": "abc-123"})
db.expire(cache_id, 3600) # Expires in 1 hour

```

## 📋 Requirements

* Python 3.7+
* A running instance of [FluxDB Server](https://github.com/PranavKndpl/FluxDB)

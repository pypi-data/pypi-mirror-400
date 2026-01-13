# SpaceData

**SpaceData** is a high-performance, asynchronous Python SDK for NASA's open APIs. It provides a type-safe interface for retrieving astronomical data, near-Earth objects, and space weather information.

## Purpose

To simplify access to NASA's complex data structures by providing a unified, developer-friendly client with built-in utilities for data analysis and media handling.

## Installation

```bash
pip install spacedata
```

**API Key**: While the SDK works with the default `DEMO_KEY`, we recommend getting a free API key from [NASA](https://api.nasa.gov) for higher rate limits and production use.

## Features

- **Async Support**: Efficient non-blocking I/O using `httpx`
- **Type Safety**: Full Pydantic integration for validation and autocompletion
- **Smart Automation**: 
  - Automatic pagination handling
  - Date-range splitting for large queries
  - Media file downloading
- **Data Science Ready**: 
  - Convert results to Pandas, Polars, or PyArrow
  - Export directly to DataFrames for analysis
- **Performance**: 
  - Built-in caching (in-memory or DuckDB)
  - Automatic retry with exponential backoff

## Examples

### 1. Astronomy Picture of the Day
```python
import asyncio
from spacedata import SpaceDataClient

async def main():
    async with SpaceDataClient() as client:
        result = await client.planetary.apod(start_date="2025-01-01", end_date="2025-01-05")
        async for item in result:
            print(f"{item.date}: {item.title}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Near-Earth Objects (NEO) Lookup
```python
import asyncio
from spacedata import SpaceDataClient

async def main():
    async with SpaceDataClient() as client:
        result = await client.neo.lookup(asteroid_ids=[3542519])
        async for asteroid in result:
            print(f"Asteroid: {asteroid.name} (Hazardous: {asteroid.is_potentially_hazardous_asteroid})")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Convert to DataFrame for Analysis
```python
import asyncio
from spacedata import SpaceDataClient

async def main():
    async with SpaceDataClient() as client:
        result = await client.neo.feed(start_date="2025-01-01", end_date="2025-01-31")
        df = await result.to_pandas()
        print(f"Found {len(df)} asteroids")
        print(df[['name', 'is_potentially_hazardous_asteroid']].head())

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

### Core
- [Client & Configuration](./docs/client.md)
- [Settings & Configuration](./docs/settings.md)
- [SpaceDataResult Object](./docs/result_object.md)

### Resources

#### Planetary
| Resource | Description | Docs |
| :--- | :--- | :--- |
| **APOD** | Astronomy Picture of the Day | [View](./docs/planetary/apod.md) |

#### Near-Earth Objects (NEO)
| Resource | Description | Docs |
| :--- | :--- | :--- |
| **NEO Feed** | Near-Earth Objects by date range | [View](./docs/neo/feed.md) |
| **NEO Lookup** | Specific NEO details by ID | [View](./docs/neo/lookup.md) |
| **NEO Browse** | Full Near-Earth Object database | [View](./docs/neo/browse.md) |

#### InSight
| Resource | Description | Docs |
| :--- | :--- | :--- |
| **Mars Weather** | Mars atmospheric data from InSight lander | [View](./docs/insight/weather.md) |

#### DONKI (Space Weather Events)
| Resource | Description | Docs |
| :--- | :--- | :--- |
| **CME** | Coronal Mass Ejections events | [View](./docs/donki/cme.md) |
| **CME Analysis** | CME analysis with ENLIL simulations | [View](./docs/donki/cme_analysis.md) |
| **FLR** | Solar Flare events | [View](./docs/donki/flr.md) |
| **GST** | Geomagnetic Storm events | [View](./docs/donki/gst.md) |
| **HSS** | High Speed Stream events | [View](./docs/donki/hss.md) |
| **IPS** | Interplanetary Shock events | [View](./docs/donki/ips.md) |
| **MPC** | Magnetopause Crossing events | [View](./docs/donki/mpc.md) |
| **RBE** | Radiation Belt Enhancement events | [View](./docs/donki/rbe.md) |
| **SEP** | Solar Energetic Particle events | [View](./docs/donki/sep.md) |
| **WSA** | WSA+ENLIL solar wind simulations | [View](./docs/donki/wsa.md) |
| **Notifications** | Space weather notification messages | [View](./docs/donki/notifications.md) |




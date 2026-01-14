# Sorcerer Forecasts

A Python library for fetching and processing weather forecast data with automatic caching and region selection. Designed for simulations and applications that need efficient access to spatio-temporal forecast data.

## Features

- **Automatic Forecast Management**: The service automatically determines when to fetch new forecast data based on your query location and time
- **Local Caching**: Downloaded forecasts are cached locally as NetCDF files for fast repeated access
- **Smart Region Selection**: Automatically selects the appropriate forecast region based on query coordinates
- **4D Querying**: Query forecasts at specific points in space (latitude, longitude, altitude) and time
- **Simulation-Friendly**: Ideal for running simulations - no need to manually check if new data is needed

## Installation

```bash
pip install sorcerer-forecasts
```

## Quick Start

```python
from datetime import datetime
from sorcerer_forecasts import ForecastService
from sorcerer_forecasts.sources import Stratocast

# Initialize the forecast source with your API key
source = Stratocast(api_key='YOUR_API_KEY')

# Create the forecast service with local caching
forecast_service = ForecastService(source=source, cache_dir='./.cache')

# Query forecast data at a specific 4D point
forecast = forecast_service.get({
    'time': datetime.fromisoformat('2025-08-26T00:00:00Z'),
    'latitude': 40,
    'longitude': 30,
    'altitude': 14625  # meters
})

# Access forecast variables
if forecast:
    print(f"Pressure: {forecast['pres']}")
    print(f"U wind: {forecast['u']}")
    print(f"V wind: {forecast['v']}")
    print(f"Height: {forecast['h']}")
```

## How It Works

### Automatic Forecast Management

The `ForecastService` intelligently manages forecast data:

1. **First Request**: When you query a point, the service checks if it has the relevant forecast in memory
2. **Cache Check**: If not in memory, it checks the local cache directory for a saved NetCDF file
3. **Fetch if Needed**: Only fetches from the remote source if the data isn't available locally
4. **Reuse Loaded Data**: Subsequent queries within the same forecast region and time period use the already-loaded data

This makes it perfect for simulations where a vehicle might be moving through space and time - the service will:

- Reuse the same forecast data when the vehicle moves within one time step
- Automatically fetch new forecasts only when crossing into a new time period or region
- Keep multiple forecasts in memory when needed

### Example: Running a Simulation

```python
from time import time
from datetime import datetime, timedelta

source = Stratocast(api_key='API_KEY')
forecast_service = ForecastService(source=source, cache_dir='./.cache')

# Simulate 10 time steps
base_time = datetime.fromisoformat('2025-08-26T00:00:00Z')

for i in range(10):
    start = time()

    # Query moves slightly in space and time
    forecast = forecast_service.get({
        'time': base_time + timedelta(minutes=i*15),
        'latitude': 40 + i * 0.1,
        'longitude': 30 + i * 0.1,
        'altitude': 14625
    })

    end = time()
    print(f"Step {i}: {end - start:.3f}s")
    # First query will be slower (fetching), subsequent queries within
    # the same forecast will be nearly instant
```

## Download a Forecast Region

Sometimes you need the full forecast region (xarray Dataset) for a given time and location—for example to analyze offline or save to disk. Use `get_region`:

```python
from datetime import datetime
from sorcerer_forecasts import ForecastService
from sorcerer_forecasts.sources import Stratocast

source = Stratocast(api_key='YOUR_API_KEY')
forecast_service = ForecastService(source=source, cache_dir='./.cache')

region = forecast_service.get_region({
    'time': datetime.fromisoformat('2025-09-12T00:00:00Z'),
    'latitude': 37.77,
    'longitude': -122.39,
    'altitude': 22
})

if region:
    # Save the full dataset wherever you like
    region['dataset'].to_netcdf(f"./tmp/{region['forecast_id']}.nc")
```

Notes:

- The `location` determines which forecast region is fetched; the service downloads the region that contains the point.
- If you don't have access/permissions for that region, `get_region` returns `None`.
- If a matching cached NetCDF exists, it is loaded from disk.
- Otherwise the dataset is fetched and, if `cache_dir` is set, written to the cache.

## Supported Regions

The library automatically selects the appropriate forecast region based on your coordinates (requires proper permissions):

- **CONUS**: Continental United States
- **EU-Central**: Central Europe
- **AF-East**: Eastern Africa
- **Region4**: Extended North America
- **Global**: Worldwide coverage

## Caching

Cached forecasts are stored as NetCDF files in the specified cache directory. The cache structure is:

```
cache_dir/
  - YYYYMMDD.tHHz.stratocast.0p25.ml80.wind.{region}.nc
```

Cache files persist between sessions, so restarting your application won't require re-downloading previously fetched forecasts.

## API Reference

### ForecastService

```python
ForecastService(source: ForecastSource, cache_dir: str | None = None)
```

- `source`: A forecast source implementation (e.g., `Stratocast`)
- `cache_dir`: Directory for caching forecast files (optional)

#### Methods

- `get(location: Point4) -> ForecastData | None`: Retrieve forecast data at a 4D point
  - Returns `None` if the location is outside available forecast bounds
- `get_region(location: Point4) -> ForecastRegion | None`: Retrieve the full forecast dataset and its identifier
  - Region is chosen based on the provided `location` (point-in-region lookup)
  - Returns `None` if the dataset cannot be fetched
  - Returns `None` if you don't have access/permissions for that region
  - Uses cache when available; writes to cache when `cache_dir` is set

### Point4 Dictionary Structure

```python
{
    'time': datetime,      # UTC datetime
    'latitude': float,     # Degrees
    'longitude': float,    # Degrees
    'altitude': float      # Meters
}
```

### ForecastRegion Dictionary Structure

```python
{
    'forecast_id': str,        # Cache-friendly identifier used in filenames
    'dataset': xarray.Dataset   # Full forecast region dataset
}
```

## License

See LICENSE file for details.

import os
from datetime import datetime
from sorcerer_forecasts.sources import Stratocast
from sorcerer_forecasts import ForecastService
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('STRATOCAST_API_KEY')
if api_key is None:
  raise ValueError('STRATOCAST_API_KEY is not set')

source = Stratocast(api_key=api_key)
forecast_service = ForecastService(source=source)

# Fetch the forecast variables for the given time and location
print('Fetching forecast...')
forecast = forecast_service.get({'time': datetime.fromisoformat('2025-09-12T00:00:00Z'), 'latitude': 37.77, 'longitude': -122.39, 'altitude': 22})
print(forecast)

# Fetch the forecast region for the given time. Location is used to determine the forecast region.
print('Fetching region...')
region = forecast_service.get_region({'time': datetime.fromisoformat('2025-09-12T00:00:00Z'), 'latitude': 37.77, 'longitude': -122.39, 'altitude': 22})
print(region)

# Save the region to a file
if region is not None:
  region['dataset'].to_netcdf(f'./tmp/{region['forecast_id']}.nc')

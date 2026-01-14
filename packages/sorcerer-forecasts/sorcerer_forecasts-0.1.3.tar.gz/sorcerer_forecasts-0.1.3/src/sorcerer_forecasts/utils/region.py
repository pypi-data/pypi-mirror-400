from sorcerer_forecasts.entity.geo import Region, Point2
from dataclasses import dataclass


@dataclass
class ForecastRegion(Region):
  name: str


regions = [
    ForecastRegion(
        name="conus",
        bottom_left=Point2(latitude=24.396308, longitude=-125.0),
        top_right=Point2(latitude=49.3457868, longitude=-66.93457)
    ),
    ForecastRegion(
        name="region4",
        bottom_left=Point2(latitude=7.0, longitude=-130.0),
        top_right=Point2(latitude=60.0, longitude=-60.0)
    ),
    ForecastRegion(
        name="eu-central",
        bottom_left=Point2(latitude=21.0, longitude=-16.0),
        top_right=Point2(latitude=61.0, longitude=41.0)
    ),
    ForecastRegion(
        name="af-east",
        bottom_left=Point2(latitude=-20.0, longitude=8.0),
        top_right=Point2(latitude=20.0, longitude=82.0)
    ),
    ForecastRegion(
        name="global",
        bottom_left=Point2(latitude=-90.0, longitude=-180.0),
        top_right=Point2(latitude=90.0, longitude=180.0)
    )
]


def get_region(location: Point2):
  for region in regions:
    if region.contains(location):
      return region

  raise ValueError(f"Invalid location: {location}")

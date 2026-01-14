from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict


class Point2(TypedDict):
  latitude: float
  longitude: float


class Point3(Point2):
  altitude: float


class Point4(Point3):
  time: datetime


@dataclass
class Region:
  bottom_left: Point2
  top_right: Point2

  def contains(self, location: Point2) -> bool:
    return self.bottom_left['latitude'] <= location['latitude'] <= self.top_right['latitude'] and self.bottom_left['longitude'] <= location['longitude'] <= self.top_right['longitude']

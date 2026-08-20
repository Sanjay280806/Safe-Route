from sqlalchemy.orm import Session

from app.config import settings
from app.models import Node
from app.utils.geo_math import haversine_m, lon_lat_key


def get_or_create_node(db: Session, lon: float, lat: float) -> Node:
    key = lon_lat_key(lon, lat)
    node = db.query(Node).filter(Node.lon_lat_key == key).one_or_none()
    if node is not None:
        return node
    node = Node(lat=lat, lon=lon, lon_lat_key=key)
    db.add(node)
    db.flush()
    return node


def nearest_node(db: Session, lat: float, lon: float, radius_m: float | None = None) -> Node | None:
    max_distance = float(radius_m if radius_m is not None else settings.snap_radius_meters)
    nearest: Node | None = None
    nearest_distance = max_distance
    for node in db.query(Node).all():
        distance = haversine_m(lat, lon, node.lat, node.lon)
        if distance <= nearest_distance:
            nearest = node
            nearest_distance = distance
    return nearest

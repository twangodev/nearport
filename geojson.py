import logging
from typing import Optional, List, Dict, Any

from fs import write_json_file

logger = logging.getLogger(__name__)

def wrap_as_feature_collection(
        geojson_geoms: List[dict],
        properties_list: Optional[List[dict]] = None
) -> dict:
    if properties_list is None:
        properties_list = [{} for _ in geojson_geoms]
    else:
        # pad with empty dicts if needed
        props = list(properties_list)
        props.extend([{}] * (len(geojson_geoms) - len(props)))
        properties_list = props

    features = []
    for geom, props in zip(geojson_geoms, properties_list):
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": props or {}
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


def write_geojson_file(geojson: Dict[str, Any]) -> None:
    logger.debug(f"Writing geojson file: {geojson}")
    write_json_file("./zones.geojson", geojson)

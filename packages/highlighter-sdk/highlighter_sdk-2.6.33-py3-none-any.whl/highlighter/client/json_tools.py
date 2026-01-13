import json
from datetime import datetime
from queue import Queue
from typing import Any, List
from uuid import UUID

from shapely.geometry.base import BaseGeometry
from shapely.wkt import loads as wkt_loads

__all__ = ["HLJSONEncoder", "HLJSONDecoder"]


class HLJSONEncoder(json.JSONEncoder):

    def default(self, o):
        from highlighter.client.evaluation import EvaluationMetricResult
        from highlighter.core.data_models.data_sample import DataSample
        from highlighter.core.database.database import Database

        if isinstance(o, UUID):
            return str(o)
        elif isinstance(o, datetime):
            return o.isoformat()
        elif serialize_fn := getattr(o, "serialize", None):
            return serialize_fn()
        elif isinstance(o, Database):
            return str(o)
        elif isinstance(o, Queue):
            return str(o)
        elif isinstance(o, DataSample):
            return o.model_dump()
        elif isinstance(o, BaseGeometry):
            return o.wkt
        elif isinstance(o, EvaluationMetricResult):
            return o.model_dump()
        return super().default(o)

    def _encode_dict_keys(self, d):
        """
        Recursively traverses a nested dictionary and casts any UUID keys to strings.

        Args:
            d (dict): A dictionary that may contain UUID keys.

        Returns:
            dict: A new dictionary with UUID keys converted to strings.
        """
        if isinstance(d, dict):
            new_dict = {}
            for key, value in d.items():
                # Check if the key is a UUID, and if so, cast it to a string
                if isinstance(key, UUID):
                    new_key = str(key)
                else:
                    new_key = key

                # Recursively process the value if it's a nested dict or list
                if isinstance(value, dict):
                    new_dict[new_key] = self._encode_dict_keys(value)
                elif isinstance(value, list):
                    new_dict[new_key] = [
                        self._encode_dict_keys(item) if isinstance(item, dict) else item for item in value
                    ]
                else:
                    new_dict[new_key] = value
            return new_dict

        elif isinstance(d, (list, tuple)):
            return [self._encode_dict_keys(e) for e in d]
        return d

    def encode(self, obj):
        _obj = self._encode_dict_keys(obj)
        return super().encode(_obj)


class HLJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.dict_to_object, *args, **kwargs)
        self.WKT_INDICATORS = ("POLYGON", "MULTIPOLYGON", "POINT", "LINESTRING")

    def dict_to_object(self, d: dict) -> dict:
        if (
            ("value" in d)
            and isinstance(d["value"], str)
            and (d["value"].split(" ")[0] in self.WKT_INDICATORS)
        ):
            d["value"] = wkt_loads(d["value"])
        return d


def find_valid_json(json_string: str) -> List[Any]:
    """
    Finds a valid json string within a string and decodes it
    """
    decoder = json.JSONDecoder()
    pos = 0
    results = []

    while pos < len(json_string):
        try:
            obj, index = decoder.raw_decode(json_string, pos)
            results.append(obj)
            pos = index
        except json.JSONDecodeError:
            pos += 1

    return results

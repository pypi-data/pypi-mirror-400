import logging
from datetime import datetime
from typing import Dict, NamedTuple, Optional, Set, Union
from uuid import UUID, uuid4

import celpy
from pydantic import BaseModel, Field, field_validator

from highlighter.core.enums import ContentTypeEnum
from highlighter.core.labeled_uuid import LabeledUUID

# ToDo: Consolidate this work with the data layer
# ToDo: Consolidate this work with the Entities object and Agents
# ToDo: Consolidate this work with Datasets

__all__ = ["ObservationsTable"]

logger = logging.getLogger(__name__)


class DotDict(dict):
    """
    Dictionary with dot notation access and recursive conversion.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __repr__(self):
        return f"Attribtues({dict.__repr__(self)})"


class ObservationsTable:
    class Row(BaseModel):

        model_config = {"arbitrary_types_allowed": True}

        class Stream(BaseModel):
            id: str

        class Entity(BaseModel):
            id: UUID

        class DataSample(BaseModel):
            recorded_at: datetime
            content_type: ContentTypeEnum
            stream_frame_index: int
            media_frame_index: int
            width: Optional[int] = None
            height: Optional[int] = None

        class Annotation(BaseModel):

            class Location(BaseModel):
                wkt: str
                xmin: int
                ymin: int
                xmax: int
                ymax: int

                @property
                def area(self):
                    return (self.xmax - self.xmin) * (self.ymax - self.ymin)

            id: UUID
            location: Optional[Location] = None

        class Attribute(BaseModel):

            class Category(BaseModel):
                id: UUID
                name: str

            value: Union[int, float, str, Category]
            occurred_at: datetime
            confidence: Optional[float] = None

            @field_validator("value", mode="before")
            def handel_labeled_uuid(cls, v):
                if isinstance(v, LabeledUUID):
                    return cls.Category(id=v, name=v.label)
                if isinstance(v, UUID):
                    return cls.Category(id=v, name="__UNDEFINED__")
                return v

        # class _NullAttribute(dict):
        #    """A safe null object that returns None for any key access"""

        #    def __getitem__(self, key):
        #        return None

        #    def __getattr__(self, key):
        #        return None

        #    def get(self, key, default=None):
        #        return default

        # class SafeAttributes(dict):

        #    def __init__(self, attributes):
        #        # Convert Pydantic models to dicts for CEL
        #        self._attributes = {}
        #        for k, v in attributes.items():
        #            attr = ObservationsTable.Row.Attribute(**v)
        #            # Store as dict for CEL field selection support
        #            self._attributes[k] = {
        #                "value": attr.value,
        #                "occurred_at": attr.occurred_at,
        #                "confidence": attr.confidence,
        #            }
        #        # Initialize dict with the attributes
        #        super().__init__(self._attributes)

        #    def __getattr__(self, k):
        #        val = self._attributes.get(k, None)
        #        if val and isinstance(val, dict):
        #            # Convert back to Attribute for Python attribute access
        #            return ObservationsTable.Row.Attribute(**val)
        #        return val

        #    def __getitem__(self, k):
        #        """Support dict-like access for CEL, returns safe null object for missing keys"""
        #        val = self._attributes.get(k, None)
        #        if val is None:
        #            return ObservationsTable.Row._NullAttribute()
        #        return val

        #    def get(self, k, default=None):
        #        """Support dict.get() for CEL"""
        #        return self._attributes.get(k, default)

        entity: Optional[Entity]
        stream: Stream
        data_sample: DataSample
        annotation: Optional[Annotation]
        attribute: DotDict
        id: UUID = Field(default_factory=uuid4)

        @field_validator("attribute", mode="before")
        @classmethod
        def convert_attribute_dict(cls, v):
            if isinstance(v, dict) or isinstance(v, DotDict):
                return DotDict(**{key: cls.Attribute(**value) for key, value in v.items()})
            return v

        def to_cel_ctx_dict(self, all_attr_keys: Set[str]):
            attributes = {k: {"value": None, "occurred_at": None, "confidence": None} for k in all_attr_keys}
            for k, v in self.attribute.items():
                attributes[k] = v.model_dump(mode="json")

            return {
                "id": str(self.id),
                "entity": self.entity.model_dump(mode="json") if self.entity else None,
                "stream": self.stream.model_dump(mode="json"),
                "data_sample": self.data_sample.model_dump(mode="json"),
                "annotation": self.annotation.model_dump(mode="json") if self.annotation else None,
                "attribute": attributes,
            }

    def __init__(self, rows: Dict[str, Row] = {}):
        self._rows = rows

    def __getitem__(self, key):
        """Support indexing for CEL"""
        return self._rows[key]

    def __iter__(self):
        """Support iteration for CEL"""
        return iter(self._rows)

    def __len__(self):
        """Support len() for CEL"""
        return len(self._rows)

    def clear(self):
        """Remove all rows once they've been consumed."""
        self._rows.clear()

    @classmethod
    def from_row_records(cls, records):

        rows = {}
        for r in records:
            row = ObservationsTable.Row(**r)
            rows[str(row.id)] = row
        return cls(rows)

    def get_cel_ctx_rows(self):
        # Collect all attribute keys across all rows
        all_attr_keys = set()
        for r in self._rows.values():
            all_attr_keys.update(r.attribute.keys())

        for r in self._rows.values():
            yield celpy.json_to_cel(r.to_cel_ctx_dict(all_attr_keys))

    def filter(self, expr):
        env = celpy.Environment()
        ast = env.compile(expr)
        program = env.program(ast)

        # Evaluate each row individually and catch errors
        result = []
        for row_ctx in self.get_cel_ctx_rows():
            try:
                # Evaluate expression with row fields directly in context
                matches = program.evaluate(row_ctx)
                if matches:
                    result.append(self._rows[str(row_ctx["id"])])
            except (celpy.evaluation.CELEvalError, TypeError):
                # If evaluation fails (e.g., None comparison), treat as non-matching
                pass

        return result

    def any(self, expr):
        """
        Check if any row matches the given CEL expression.

        Args:
            expr: A CEL expression to evaluate against each row

        Returns:
            bool: True if at least one row matches, False otherwise
        """
        env = celpy.Environment()
        ast = env.compile(expr)
        program = env.program(ast)

        for row_ctx in self.get_cel_ctx_rows():
            try:
                matches = program.evaluate(row_ctx)
                if matches:
                    return True
            except (celpy.evaluation.CELEvalError, TypeError):
                # If evaluation fails, treat as non-matching
                pass

        return False

    def all(self, expr):
        """
        Check if all rows match the given CEL expression.

        Args:
            expr: A CEL expression to evaluate against each row

        Returns:
            bool: True if all rows match, False otherwise
        """
        env = celpy.Environment()
        ast = env.compile(expr)
        program = env.program(ast)

        for row_ctx in self.get_cel_ctx_rows():
            try:
                matches = program.evaluate(row_ctx)
                if not matches:
                    return False
            except (celpy.evaluation.CELEvalError, TypeError):
                # If evaluation fails, treat as non-matching
                return False

        return True

    def show(self, log_extra=None):
        """Log a tabular representation of the rows"""
        if not self._rows:
            logger.info("Empty Observations Table", extra=log_extra)
            return

        # Collect all attribute keys across all rows
        all_attr_keys = sorted(set(key for row in self._rows.values() for key in row.attribute.keys()))

        # Define columns: id, entity_id, stream_id, recorded_at, then attributes
        columns = ["id", "entity_id", "stream_id", "recorded_at"] + all_attr_keys

        # Calculate column widths
        col_widths = {col: len(col) for col in columns}

        def get_attr_value_str(attr) -> str:
            attr_val = attr["value"] if isinstance(attr, dict) else attr.value

            if isinstance(attr_val, float):
                value_str = f"{attr_val:.3f}"
            else:
                value_str = str(attr_val)
            return value_str

        # Update widths based on data
        for row in self._rows.values():
            col_widths["id"] = max(col_widths["id"], len(str(row.id)[:8]))
            entity_id_str = str(row.entity.id)[:8] if row.entity else "None"
            col_widths["entity_id"] = max(col_widths["entity_id"], len(entity_id_str))
            col_widths["stream_id"] = max(col_widths["stream_id"], len(row.stream.id))
            col_widths["recorded_at"] = max(
                col_widths["recorded_at"], len(row.data_sample.recorded_at.strftime("%Y-%m-%d %H:%M"))
            )

            for attr_key in all_attr_keys:
                attr = row.attribute.get(attr_key)
                if attr:
                    value_str = get_attr_value_str(attr)

                    col_widths[attr_key] = max(col_widths[attr_key], len(value_str))

        # Build header
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        separator = "-" * len(header)

        # Build all rows
        rows_output = []
        for row in self._rows.values():
            row_data = []
            row_data.append(str(row.id)[:8].ljust(col_widths["id"]))
            entity_id_str = str(row.entity.id)[:8] if row.entity else "None"
            row_data.append(entity_id_str.ljust(col_widths["entity_id"]))
            row_data.append(row.stream.id.ljust(col_widths["stream_id"]))
            row_data.append(
                row.data_sample.recorded_at.strftime("%Y-%m-%d %H:%M").ljust(col_widths["recorded_at"])
            )

            for attr_key in all_attr_keys:
                attr = row.attribute.get(attr_key)
                if attr:
                    value_str = get_attr_value_str(attr)
                    row_data.append(value_str.ljust(col_widths[attr_key]))
                else:
                    row_data.append("".ljust(col_widths[attr_key]))

            rows_output.append(" | ".join(row_data))

        # Log the entire table as a single message
        table_output = "\n".join([header, separator] + rows_output[-5:])
        logger.info(f"Observations Table (tail 5 of {len(self._rows)}):\n{table_output}", extra=log_extra)

    def add_entity(self, entity, data_sample, stream_id):
        new_rows = [
            ObservationsTable.Row(**r)
            for r in ObservationsTable.row_data_from_entity(entity, data_sample, stream_id)
        ]
        self._rows.update({str(r.id): r for r in new_rows})

    @staticmethod
    def row_data_from_entity(entity, data_sample, stream_id):
        rows = []
        # Process each annotation as a separate row
        if len(entity.annotations) > 0:
            for annotation in entity.annotations:
                # Build attribute dict from annotation observations
                attributes = {}
                for obs in annotation.observations:
                    attr_label = (
                        obs.attribute_id.label
                        if hasattr(obs.attribute_id, "label")
                        else str(obs.attribute_id)
                    )
                    attributes[attr_label] = {
                        "value": obs.value,
                        "occurred_at": obs.occurred_at,
                        "confidence": obs.datum_source.confidence,
                    }

                # Add global observations to attributes
                for obs in entity.global_observations:
                    attr_label = (
                        obs.attribute_id.label
                        if hasattr(obs.attribute_id, "label")
                        else str(obs.attribute_id)
                    )
                    attributes[attr_label] = {
                        "value": obs.value,
                        "occurred_at": obs.occurred_at,
                        "confidence": obs.datum_source.confidence,
                    }

                # Get location bounds if location exists
                location_dict = None
                if annotation.location is not None:
                    xmin, ymin, xmax, ymax = annotation.location.bounds
                    location_dict = {
                        "wkt": annotation.location.wkt,
                        "xmin": int(xmin),
                        "ymin": int(ymin),
                        "xmax": int(xmax),
                        "ymax": int(ymax),
                    }

                # Build row data
                row_data = {
                    "entity": {"id": entity.id},
                    "stream": {"id": stream_id if stream_id else "unknown"},
                    "data_sample": {
                        "recorded_at": data_sample.recorded_at,
                        "content_type": data_sample.content_type,
                        "stream_frame_index": data_sample.stream_frame_index,
                        "media_frame_index": data_sample.media_frame_index,
                    },
                    "annotation": {
                        "id": annotation.id,
                    },
                    "attribute": attributes,
                }

                # Add location to annotation if it exists
                if location_dict is not None:
                    row_data["annotation"]["location"] = location_dict

                rows.append(row_data)

        # If entity has no annotations but has global observations, create a row
        elif len(entity.global_observations) > 0:
            # Build attribute dict from global observations only
            attributes = {}
            for obs in entity.global_observations:
                attr_label = (
                    obs.attribute_id.label if hasattr(obs.attribute_id, "label") else str(obs.attribute_id)
                )
                attributes[attr_label] = {
                    "value": obs.value,
                    "occurred_at": obs.occurred_at,
                    "confidence": obs.datum_source.confidence,
                }

            # Build row data without annotation location
            row_data = {
                "entity": {"id": entity.id},
                "stream": {"id": stream_id if stream_id else "unknown"},
                "data_sample": {
                    "recorded_at": data_sample.recorded_at,
                    "content_type": data_sample.content_type,
                    "stream_frame_index": data_sample.stream_frame_index,
                    "media_frame_index": data_sample.media_frame_index,
                },
                "annotation": {
                    # ToDo: How do we get an AnnotationId from global observation
                    # the current setup is "Annotation has-many Observations"
                    # so global_observations, simply dont have an Annotation instance to refer to
                    "id": UUID(int=0),  # Placeholder annotation ID
                },
                "attribute": attributes,
            }

            rows.append(row_data)

        # Note: We no longer create placeholder rows here.
        # Empty entity cases are handled at the ObservationsTable level
        # to allow data_sample expression evaluation without fake entities.
        return rows

import logging
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Union
from uuid import UUID

from highlighter.core.enums import ContentTypeEnum
from highlighter.core.gql_base_model import GQLBaseModel

from .entity import Entity

logger = logging.getLogger(__name__)


class Entities(GQLBaseModel):
    """Entity container

    Enables erganomic management of a set of entities.
    Entities can be looked-up by ID:
        `entity = entities[entity_id]`
    Entities can be added:
        `entities[entity_id] = entity`
        `entities.add(entity)`
        `entities.update(other_entities)`
    Entities can be queried (not yet implemented):
        `specific_entities = entities.where(object_class=object_class_id)`
        `specific_entities = entities.where(has_attribute=attribute_id)`
        `specific_entities = entities.where(has_attribute_value=enum_id)`
    """

    def __init__(self, entities: Optional[Dict[UUID, Entity]] = None):
        super().__init__()
        self._entities = entities or {}

    def add(self, entity: Entity):
        self[entity.id] = entity

    def _clear_old_entities(self, sunset: datetime):
        """Remove stale Entities/Annotations/Observations

        conditions:
          - If Entity.annotations[i].observations[j].occurred_at is too old it is removed
          - If Entity.annotations[i] has no observations and .occurred_at is too old it is removed
          - If Entity.global_observations[i].occurred_at is too old it is removed
          - If an Entity has no .annotations or .global_observations it is removed

        """
        entities_to_remove = []

        for entity_id, entity in self._entities.items():
            # Clean up observations within annotations
            for annotation in list(entity.annotations):
                # Remove old observations from this annotation
                observations_to_remove = [obs for obs in annotation.observations if obs.occurred_at < sunset]
                for obs in observations_to_remove:
                    annotation.observations.remove(obs)

                # Remove annotation if it has no observations and is too old
                if (
                    len(annotation.observations) == 0
                    and annotation.occurred_at
                    and annotation.occurred_at < sunset
                ):
                    entity.annotations.remove(annotation)

            # Clean up global observations
            global_observations_to_remove = [
                obs for obs in entity.global_observations if obs.occurred_at < sunset
            ]
            for obs in global_observations_to_remove:
                entity.global_observations.remove(obs)

            # Mark entity for removal if it has no data left
            if len(entity.annotations) == 0 and len(entity.global_observations) == 0:
                entities_to_remove.append(entity_id)

        # Remove empty entities
        for entity_id in entities_to_remove:
            del self._entities[entity_id]

    def clear(self, sunset: Optional[datetime] = None):
        if sunset:
            self._clear_old_entities(sunset)
        else:
            self._entities.clear()

    def values(self):
        return self._entities.values()

    def items(self):
        return self._entities.items()

    def keys(self):
        return self._entities.keys()

    def __getitem__(self, key: UUID | int):
        if isinstance(key, int):
            return list(self._entities.values())[key]
        return self._entities[key]

    def __delitem__(self, key: UUID):
        return self._entities.__delitem__(key)

    def remove(self, entity: Entity):
        del self[entity.id]

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self):
        return iter(list(self._entities.values()))

    def get(self, key: UUID, default: Entity | None = None):
        return self._entities.get(key, default)

    def __setitem__(self, entity_id: UUID, entity: Entity):
        if isinstance(entity, Entity):
            self._entities[entity_id] = entity
        else:
            raise ValueError(f"Expected an Entity, got {type(entity).__qualname__}: {entity}")

    def update(self, *args, **kwargs):
        # Handles both dicts and iterable of pairs
        if args:
            other = args[0]
            if hasattr(other, "items"):
                for k, v in other.items():
                    self[k] = v  # goes through __setitem__
            else:
                for value in other:
                    if isinstance(value, Entity):
                        self.add(value)
                    else:
                        k, v = value
                        self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __ior__(self, other):
        self.update(other)
        return self

    def __or__(self, other):
        new = type(self)(entities=self._entities.copy())
        new.update(other)
        return new

    def __contains__(self, key):
        return key in self._entities

    def __repr__(self):
        return self._entities.__repr__()

    def to_json_serializable_dict(self):
        return {str(id): entity.to_json() for id, entity in self._entities.items()}

    def to_data_sample(self) -> "DataSample":
        from highlighter.core.data_models.data_sample import DataSample

        if len(self._entities) == 0:
            return DataSample(content=self, content_type=ContentTypeEnum.ENTITIES)
        some_annotations = list(self._entities.values())[0].annotations
        if len(some_annotations) == 0:
            raise ValueError("Cannot convert Entities to DataSample if there are no annotations")
        annotation = some_annotations[0]
        if annotation.data_file_id is None:
            raise ValueError("Cannot convert Entities to DataSample if annotation.data_file_id is None")
        return DataSample(
            content=self,
            content_type=ContentTypeEnum.ENTITIES,
            recorded_at=annotation.occurred_at,
            stream_frame_index=annotation.datum_source.frame_id,
            media_frame_index=annotation.datum_source.frame_id,  # FIXME
        )

    def all_observations(self) -> Iterator["Observation"]:
        for entity in self._entities.values():
            yield from entity.all_observations()

    def to_observations_table(self, stream_id: str, data_sample: "DataSample"):
        """
        Convert Entities to an ObservationsTable.

        Creates one row per annotation (entity + annotation pair). For entities with
        global observations but no annotations, creates one row per entity with a
        placeholder annotation.

        Args:
            stream_id: Optional stream identifier to include in the table

        Returns:
            ObservationsTable instance
        """
        from highlighter.agent.observations_table import ObservationsTable

        rows = []

        for entity in self._entities.values():
            row_data = ObservationsTable.row_data_from_entity(entity, data_sample, stream_id)
            rows.extend(row_data)

        return ObservationsTable.from_row_records(rows)

    def merge(self, others: Union["Entities", Dict], strategy="append"):
        for e in others.values():
            if e.id in self:
                self[e.id].merge(e, strategy=strategy)
            else:
                self.add(e)

    def hydrate_with_data_samples(self, data_samples: List["DataSample"]) -> "Entities":
        for entity in self:
            for annotation in entity.annotations:
                for data_sample in data_samples:
                    # TODO: Use annotation.data_source_id and annotation.occurred_at to resolve data sample
                    if (
                        data_sample.data_file_id == annotation.data_file_id
                        and data_sample.media_frame_index == annotation.datum_source.frame_id
                    ):
                        annotation.data_sample = data_sample
                        break
                else:
                    logger.warning(f"Annotation {annotation.id} has no associated data sample")
        return self

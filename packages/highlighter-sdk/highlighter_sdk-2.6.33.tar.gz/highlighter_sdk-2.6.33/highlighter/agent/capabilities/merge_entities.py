from typing import Tuple

from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.client.base_models.entities import Entities

__all__ = ["MergeEntities"]


class MergeEntities(Capability):

    class InitParameters(Capability.InitParameters):
        pass

    class StreamParameters(InitParameters):
        pass

    def process_frame(self, stream, data_samples, **kwargs) -> Tuple[StreamEvent, dict]:
        merged_entities = Entities()
        for entities in kwargs.values():
            if not isinstance(entities, (Entities, dict)):
                continue

            merged_entities.merge(entities)
        return StreamEvent.OKAY, {"data_samples": data_samples, "entities": merged_entities}

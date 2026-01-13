import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np

from highlighter.agent.capabilities.base_capability import Capability, StreamEvent
from highlighter.client.base_models import Entity
from highlighter.client.gql_client import HLClient
from highlighter.client.training_runs import TrainingRunArtefactType
from highlighter.core.data_models import DataSample
from highlighter.datasets.cropping import CropArgs
from highlighter.predictors.onnx_yolov8 import OnnxYoloV8
from highlighter.predictors.output_category_descriptor import OutputCategoryDescriptor

__all__ = ["YoloBoxClassifier"]

logger = logging.getLogger(__name__)


class YoloBoxClassifier(Capability):
    """
    A box classifier capability that uses YOLO to classify existing bounding boxes.

    This capability takes entities with bounding box or polygon annotations from upstream
    (e.g., from an object detector) and classifies each box using a YOLO classifier model.
    The classification results are added as observations to the existing annotations.
    """

    class InitParameters(Capability.InitParameters):
        onnx_file: Optional[str] = None
        training_run_artefact_id: Optional[UUID] = None
        num_classes: int
        class_lookup: Optional[Dict[int | str, OutputCategoryDescriptor]] = None
        conf_thresh: float = 0.1
        nms_iou_thresh: float = 0.5
        is_absolute: bool = True
        cropper: Optional[CropArgs] = None

    def __init__(self, context):
        super().__init__(context)

        onnx_file = self.init_parameters.onnx_file
        if onnx_file is None:
            training_run_artefact_id = self.init_parameters.training_run_artefact_id
            if training_run_artefact_id is None:
                raise ValueError("Must provide `onnx_file` or `training_run_artefact_id`")
            training_run_artefact = HLClient.get_client().trainingRunArtefact(
                return_type=TrainingRunArtefactType, id=training_run_artefact_id
            )
            onnx_file = training_run_artefact.file_url

        artefact_cache_dir = Path.home() / ".cache" / "highlighter" / "agents" / "artefacts"
        self._predictor = OnnxYoloV8(
            onnx_file,
            self.init_parameters.num_classes,
            class_lookup=self.init_parameters.class_lookup,
            conf_thresh=self.init_parameters.conf_thresh,
            nms_iou_thresh=self.init_parameters.nms_iou_thresh,
            is_absolute=self.init_parameters.is_absolute,
            artefact_cache_dir=artefact_cache_dir,
        )

    def process_frame(
        self, stream, data_samples: List[DataSample], entities: Dict[UUID, Entity]
    ) -> Tuple[StreamEvent, Dict]:
        start = time.perf_counter()

        annotations = []
        crop_data_samples = []
        for entity in entities.values():
            for annotation in entity.annotations:
                annotations.append(annotation)
                crop = annotation.crop_image(crop_args=self.init_parameters.cropper)
                crop_data_sample = annotation.data_sample.model_copy()
                crop_data_sample.content = crop
                crop_data_samples.append(crop_data_sample)

        # YOLO classifiers return whole-image annotations
        classification_annotations = self._predictor.predict(crop_data_samples)
        for orig_annotation, class_annotations in zip(annotations, classification_annotations):
            for class_annotation in class_annotations:
                for observation in class_annotation.observations:
                    # Associate the observation with the original annotation
                    observation.annotation = None
                    observation.annotation = orig_annotation

        end = time.perf_counter()
        self.logger.debug(f"YoloBoxClassifier processed in {end - start:.6f} seconds")

        return StreamEvent.OKAY, {"entities": entities}

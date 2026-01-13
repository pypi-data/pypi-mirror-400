import logging
from abc import abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from highlighter.client.evaluation import EvaluationMetricResult
from highlighter.client.gql_client import HLClient
from highlighter.client.training_config import TrainingConfigType
from highlighter.core.labeled_uuid import LabeledUUID
from highlighter.datasets.dataset import Dataset


class BaseTrainer:

    def __init__(
        self,
        training_run_dir: Path,
        highlighter_training_config: TrainingConfigType,
    ):
        self._logger = logging.getLogger(__name__)
        self._training_run_dir = training_run_dir
        self._hl_training_config = highlighter_training_config

    @property
    def _hl_cache_dir(self):
        d = self._training_run_dir / ".hl"
        d.mkdir(exist_ok=True, parents=True)
        return d

    @property
    def _hl_cache_dataset_dir(self):
        d = self._hl_cache_dir / "datasets"
        d.mkdir(exist_ok=True, parents=True)
        return d

    @staticmethod
    def hl_training_config_path(training_run_dir: Path):
        d = training_run_dir / "training_config.yaml"
        return d

    def generate_boilerplate(self):
        """Puts the standard boilerplate files and makes directories required
        by in the Trainer in the training_run_dir. Downloads as caches
        the dataset annotations
        """
        self._hl_training_config.dump("yaml", BaseTrainer.hl_training_config_path(self._training_run_dir))

    @property
    @abstractmethod
    def training_data_dir(self) -> Path:
        """Path to data used to store training data"""
        pass

    @abstractmethod
    def generate_trainer_specific_dataset(self, hl_dataset: Dataset):
        pass

    @abstractmethod
    def train(self) -> Any:
        """Trains the Model, return the trained model instance"""
        pass

    @abstractmethod
    def evaluate(
        self, checkpoint: Path, cfg_path: Optional[Path] = None
    ) -> Dict[str, EvaluationMetricResult]:
        """Evaluate a model given a Path to a checkpoint, onnx_file or model instance"""
        pass

    @abstractmethod
    def export_to_onnx(self, trained_model) -> Path:
        """Export the trained model to onnx

        Return:
            Path to the onnx model
        """
        pass

    @abstractmethod
    def make_artefact(self, onnx_file_path: Path) -> Path:
        """Create a Highlighter training run artefact give the input checkpoint

        Return:
            Path to the artefact.yaml
        """
        pass

    @property
    def training_run_id(self) -> int:
        return self._hl_training_config.training_run_id

    @property
    def research_plan_id(self) -> int:
        return self._hl_training_config.evaluation_id

    def get_datasets(self, client: HLClient, page_size=20) -> Dataset:
        """Returns a Highlighter SDK Dataset object containing data from each
        split in the one object. `dataset.data_files_id.split` identifies the
        which split each data_file belongs to.
        """
        datasets = Dataset.read_training_config(
            client, self._hl_training_config, self._hl_cache_dataset_dir, page_size=page_size
        )
        return self._combine_hl_datasets(datasets)

    def _combine_hl_datasets(self, datasets):
        # When creating a training run in Highlighter the train split is required
        # but a user can supply either a test or dev set, or both. If not both we
        # duplicate the one that exists here
        if "test" not in datasets:
            datasets["test"] = deepcopy(datasets["dev"])
            datasets["test"].data_files_df.split = "test"
        if "dev" not in datasets:
            datasets["dev"] = deepcopy(datasets["test"])
            datasets["dev"].data_files_df.split = "dev"

        combined_ds = datasets["train"]
        combined_ds.append([datasets["dev"], datasets["test"]])

        return combined_ds

    def filter_dataset(self, dataset: Dataset) -> Dataset:
        """Optionally add some code to filter the Highlighter Datasets as required.
        The YoloWriter will only use entities with both a pixel_location attribute
        and a 'category_attribute_id' attribute when converting to the Yolo dataset format.
        It will the unique values for the object_class attribute as the detection
        categories.

        For example, if you want to train a detector that finds Apples and Bananas,
        and your taxonomy looks like this:

            - object_class: Apple
            - object_class: Orange
            - object_class: Banana

        Then you may do something like this:

            adf = combined_ds.annotations_df
            ddf = combined_ds.data_files_df

            orange_entity_ids = adf[(adf.attribute_id == OBJECT_CLASS_ATTRIBUTE_UUID) &
                                   (adf.value == "Orange")].entity_id.unique()

            # Filter out offending entities
            adf = adf[adf.entity_id.isin(orange_entity_ids)]

            # clean up images that are no longer needed
            ddf = ddf[ddf.data_file_id.isin(adf.data_file_id)]

            combined_ds.annotations_df = adf
        """
        return dataset

    def _train(self, hl_dataset: Dataset):

        self.generate_trainer_specific_dataset(hl_dataset)

        trained_model = self.train()
        onnx_model_path = self.export_to_onnx(trained_model)
        artefact_path = self.make_artefact(onnx_model_path)
        eval_metric_results = self.evaluate(onnx_model_path)
        return trained_model, artefact_path.absolute(), onnx_model_path, eval_metric_results

    def get_categories(self) -> List[Tuple[LabeledUUID, LabeledUUID]]:
        """Return a list of attribute_id, value tuples representing the
        unique categories for training
        """
        head_outputs = self._hl_training_config.input_output_schema.get_head_model_outputs(
            self._hl_training_config.head_idx
        )
        return [
            (
                LabeledUUID(o.taxon[-1].entity_attribute_id, label=o.taxon[-1].entity_attribute_name),
                LabeledUUID(
                    o.taxon[-1].entity_attribute_enum_id, label=o.taxon[-1].entity_attribute_enum_value
                ),
            )
            for o in head_outputs
        ]

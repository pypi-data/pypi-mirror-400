import logging
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple, Union
from uuid import UUID
from warnings import warn

import numpy as np
import pandas as pd
import yaml
from PIL.Image import Image
from pydantic import BaseModel
from pydantic.types import UuidVersion
from shapely import geometry as geom

from highlighter.client.io import _pil_open_image_path
from highlighter.core import (
    OBJECT_CLASS_ATTRIBUTE_UUID,
    PIXEL_LOCATION_ATTRIBUTE_UUID,
    LabeledUUID,
)
from highlighter.datasets.cropping import CropArgs, crop_rect_from_poly
from highlighter.datasets.formats.coco.common import (
    segmentation_to_bbox,
    shapely_to_segmentation,
)
from highlighter.datasets.interfaces import IWriter

__all__ = ["YoloWriter"]

PathLike = Union[str, Path]
logger = logging.getLogger(__name__)


@lru_cache()
def _read_image_lru(image_path) -> Image:
    return _pil_open_image_path(image_path)


def convert_to_uuid_if_possible(value):
    if isinstance(value, UUID):
        return value
    elif isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            return value
    else:
        return value


class Category(BaseModel):
    attribute_id: UUID
    value: UUID


class YoloWriter(IWriter):
    format_name = "yolo"
    annotation_count = -1
    image_count = -1

    class TASK(str, Enum):
        DETECT = "detect"
        SEGMENT = "segment"
        CLASSIFY = "classify"

    def __init__(
        self,
        output_dir: PathLike,
        image_cache_dir: PathLike,
        categories: List[Union[Tuple[UUID, UUID], Category]],
        task: Union[str, TASK] = TASK.DETECT,
        crop_args: Optional[CropArgs] = None,
    ):
        """Save a Highlighter Dataset object as a YoloV8 Detection dataset

        The Highlighter Dataset object must have at least the split names
        "train" and "test" and optionally "val". If "val" is not a split
        "test" will be duplicated in the data.yaml

        Args:
            output_dir: Root level directory for the output dataset
            categories: The attribute_id and the values used for training categories
            image_cache_dir: Directory of locally stored images. The yolo
            <train|val|test>/images directories will contain symlinks to these files.
        """
        self.output_dir = Path(output_dir)
        self.categories = []
        for c in categories:
            if isinstance(c, Category):
                self.categories.append(c)
            else:
                self.categories.append(Category(attribute_id=c[0], value=c[1]))
        self.enum_id_to_output_index = {
            category.value: index for index, category in enumerate(self.categories)
        }

        self.image_cache_dir = Path(image_cache_dir).absolute()
        self.task = self.TASK(task)
        self.crop_args = crop_args

    @staticmethod
    def generate_data_config_dict(
        root_dir: Path,
        train_image_dir: Path,
        val_image_dir: Path,
        test_image_dir: Optional[Path],
        categories: List[Category],
    ) -> dict:
        config = {
            "path": str(root_dir),
            "train": str(train_image_dir.relative_to(root_dir)),
            "val": str(val_image_dir.relative_to(root_dir)),
            "names": {i: str(c.value) for i, c in enumerate(categories)},
            "nc": len(categories),
        }
        if test_image_dir is not None:
            config["test"] = str(test_image_dir.relative_to(root_dir))

        return config

    def _to_classify_label(
        self,
        category: Union[str, UUID],
        pixel_location: geom.Polygon,
        source_image_path: Path,
        split_dir: Path,
    ):
        image_pil = _read_image_lru(source_image_path)
        crop = crop_rect_from_poly(image_pil, pixel_location, crop_args=self.crop_args)
        l, t, r, b = [int(p) for p in pixel_location.bounds]
        output_index = self.enum_id_to_output_index[category]
        category_dir = f"{output_index}_{category}"
        dest_image_path = (
            split_dir
            / category_dir
            / f"{source_image_path.stem}-{l}-{t}-{r}-{b}{source_image_path.suffix.lower()}"
        )
        dest_image_path.parent.mkdir(exist_ok=True, parents=True)
        crop.save(dest_image_path)

    def _to_detect_label(self, cat_idx, pixel_location, scale_wh):
        box_left, box_top, box_right, box_bottom = pixel_location.bounds
        box_w = box_right - box_left
        box_h = box_bottom - box_top
        im_w, im_h = scale_wh

        box_cen_x = (box_left + box_w / 2) / im_w
        box_cen_y = (box_top + box_h / 2) / im_h
        box_w /= im_w
        box_h /= im_h
        return f"{cat_idx} {box_cen_x} {box_cen_y} {box_w} {box_h}"

    def _to_segment_label(self, cat_idx, pixel_location, scale_wh):
        segmentation = shapely_to_segmentation(pixel_location, fill_interiors=True)
        if len(segmentation) > 1:
            warn("YoloWriter only supports " "single polygon, not multipolygon.")
        segmentation_arr = np.array(segmentation[0])
        scale = 1 / np.array(scale_wh * (segmentation_arr.shape[0] // 2))
        scaled_segmentation = (segmentation_arr * scale).tolist()
        segmentation_str = " ".join([str(s) for s in scaled_segmentation])
        return f"{cat_idx} {segmentation_str}"

    def _assert_is_image_dataset(self, dataset):
        images_exts = (".jpg", ".jpeg", ".png")
        if any([Path(f).suffix.lower() not in images_exts for f in dataset.data_files_df.filename.unique()]):
            raise ValueError(
                "Dataset contains non image filenames. If you have a video dataset with keyframes use Dataset.interpolate_from_keyframes to convert to an image dataset"
            )

    def _assert_all_categories_present(self, adf):
        filter_df = pd.DataFrame([c.model_dump() for c in self.categories])
        cat_adf = adf.merge(filter_df, on=["attribute_id", "value"])

        if not np.isin(filter_df.value.values, cat_adf.value.unique()).all():
            raise ValueError(
                "All categories must appear in the source dataset "
                f"got: categories = {self.categories} and "
                f"source dataset categories = {cat_adf.attribute_id.unique()}"
            )

    def _assert_correct_split_names(self, unique_splits):
        if not all([s in unique_splits for s in ("train", "val")]):
            raise ValueError(
                "data_files_df must have at split names "
                "['train', 'val'] optionally 'test'. Got: "
                f"{unique_splits}"
            )

    def write(
        self,
        dataset: "Dataset",
    ):

        self._assert_is_image_dataset(dataset)

        unique_splits = dataset.data_files_df.split.unique()
        self._assert_correct_split_names(unique_splits)

        adf = dataset.annotations_df.copy()
        # Ensure attribute_id are UUID and values are UUID if they're UUID strs
        adf["attribute_id"] = adf["attribute_id"].apply(convert_to_uuid_if_possible)
        adf["value"] = adf["value"].apply(convert_to_uuid_if_possible)
        self._assert_all_categories_present(adf)

        def to_yolo_annotation(grp):
            try:
                data = grp.set_index("entity_id").to_dict("index")
                data_file_id = grp.name

                labels = []
                entities = grp.set_index("entity_id").to_dict("index")
                for entity_id, data in entities.items():
                    pixel_location = data.get(PIXEL_LOCATION_ATTRIBUTE_UUID, None)
                    if pixel_location is None:
                        logger.warning(
                            f"each entity must have a {PIXEL_LOCATION_ATTRIBUTE_UUID} attribute, got: {data} for entity_id {entity_id}"
                        )
                        continue

                    # If an entity has more than on of the desired attributes
                    # take the first one as defined in self.categories
                    category = None
                    for cat_idx, c in enumerate(self.categories):
                        if data.get(c.attribute_id, None) == c.value:
                            category = data[c.attribute_id]
                            break

                    if category is None:
                        logger.warning(
                            f"Entity must one attribute of {self.categories}, got: {data} for entity_id {entity_id}. Skipping."
                        )
                        continue

                    im_w = data["width"]
                    im_h = data["height"]

                    split_name = grp.split.values[0]
                    source_filename = Path(grp.filename.values[0])
                    source_filename = f"{source_filename.stem}{source_filename.suffix.lower()}"

                    if self.task in (self.TASK.DETECT, self.TASK.SEGMENT):
                        labels_dir = self.output_dir / "labels"
                        labels_dir.mkdir(parents=True, exist_ok=True)
                        to_label_fn = (
                            self._to_detect_label if self.task == self.TASK.DETECT else self._to_segment_label
                        )
                        labels.append(to_label_fn(cat_idx, pixel_location, (im_w, im_h)))
                        labels_path = labels_dir / split_name / f"{data_file_id}.txt"
                        labels_path.parent.mkdir(exist_ok=True)
                        with labels_path.open("w") as f:
                            f.write("\n".join(labels))

                        image_symlink: Path = self.output_dir / "images" / split_name / source_filename
                        image_symlink.parent.mkdir(parents=True, exist_ok=True)
                        if not image_symlink.exists():
                            image_symlink.symlink_to(self.image_cache_dir / source_filename)
                            assert image_symlink.exists(), f"{image_symlink} is a broken symlink"

                    elif self.task == self.TASK.CLASSIFY:
                        split_dir = self.output_dir / split_name
                        source_image_path = self.image_cache_dir / source_filename
                        self._to_classify_label(category, pixel_location, source_image_path, split_dir)
            except Exception as e:
                logger.warning(f"Error making yolo annotation for data_file: {grp.name} -- {e}")

        for split_name in dataset.data_files_df.split.unique():

            ddf = dataset.data_files_df[dataset.data_files_df.split == split_name]
            # Drop duplicate assessments on the same image
            ddf = ddf.drop_duplicates(subset=["data_file_id", "split"], keep="first")
            split_ids = ddf.data_file_id.unique()
            split_adf = adf[adf.data_file_id.isin(split_ids)]

            split_adf = split_adf.drop_duplicates(
                subset=["data_file_id", "entity_id", "attribute_id", "value"], keep="first"
            )

            pix_df = split_adf[split_adf.attribute_id == PIXEL_LOCATION_ATTRIBUTE_UUID]
            cat_df = pd.concat(
                [
                    split_adf[((split_adf.attribute_id == cat.attribute_id) & (split_adf.value == cat.value))]
                    for cat in self.categories
                ]
            )

            pix_cat_df = pd.concat([pix_df, cat_df])
            # Add width, height and split columns annotations_df
            df = pd.merge(
                pix_cat_df,
                ddf[["data_file_id", "width", "height", "split", "filename"]],
                on="data_file_id",
                how="left",
            )

            # Ensure all attribute_id are str, sometimes they can be UUID or LabeledUUID
            # df.loc[:, "attribute_id"] = df.attribute_id.map(lambda a: str(a))

            # Because entity_id can be the same from frame-to-frame as an entity
            # is tracked we need to pivot the DataFrame ('entity_id', 'data_file_id')
            # this assumes the same entity cannot appear twice in a single image.
            pivoted_df = df.pivot(index=["entity_id", "data_file_id"], columns="attribute_id", values="value")

            # Reset the index to make 'id' a column again
            pivoted_df = pivoted_df.reset_index()

            # Fill missing values with None
            pivoted_df = pivoted_df.where(pd.notnull(pivoted_df), None)

            pivoted_df = pivoted_df.merge(
                df[
                    ["data_file_id", "width", "height", "split", "filename"]
                ].drop_duplicates(),  # Select only needed columns and remove duplicates
                on="data_file_id",  # Merge key
                how="left",  # Keep all rows from pivoted_df
            )
            pivoted_df.groupby("data_file_id").apply(to_yolo_annotation)

        if self.task == self.TASK.CLASSIFY:
            images_dir = self.output_dir
        else:
            images_dir = self.output_dir / "images"

        config_dict = self.generate_data_config_dict(
            self.output_dir,
            images_dir / "train",
            images_dir / "val",
            images_dir / "test" if "test" in unique_splits else None,
            self.categories,
        )
        with (self.output_dir / "data.yaml").open("w") as f:
            yaml.dump(config_dict, f)

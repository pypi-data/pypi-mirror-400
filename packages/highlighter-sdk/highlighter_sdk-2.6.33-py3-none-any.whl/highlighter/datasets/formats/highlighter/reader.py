import mimetypes
from pathlib import Path
from typing import List, Tuple
from uuid import UUID
from warnings import warn

from shapely.geometry import box as shapely_box
from shapely.wkt import loads as wkt_loads

from ....client import PixelLocationAttributeValue, read_avro_file_from_url
from ....core import (
    OBJECT_CLASS_ATTRIBUTE_UUID,
    PIXEL_LOCATION_ATTRIBUTE_UUID,
    try_make_polygon_valid_if_invalid,
)
from ...base_models import AttributeRecord, ImageRecord
from ...interfaces import IReader

__all__ = [
    "HighlighterAssessmentsReader",
]


class HighlighterAssessmentsReader(IReader):
    format_name = "highlighter_assessments"

    def __init__(self, assessments_gen):
        self.assessments_gen = assessments_gen

    def _process_avro_entities(self, avro_entities: List, attribute_records: List[AttributeRecord]):
        """Helper method to process avro entities and add them to attribute_records"""
        for entity in avro_entities:
            entity_id = UUID(entity["id"])
            object_class_uuid = entity["object_class"]

            for track in entity.get("tracks", []):
                # Process detections (bounding boxes/geometries)
                data_file_id = track["data_file_id"]
                for detection in track.get("detections", []):

                    frame_id = detection["frame_id"]
                    frame_id = 0 if frame_id is None else frame_id
                    confidence = detection.get("confidence", 1.0)

                    # Create object_class AttributeRecord
                    attribute_records.append(
                        AttributeRecord(
                            data_file_id=data_file_id,
                            entity_id=entity_id,
                            attribute_id=str(OBJECT_CLASS_ATTRIBUTE_UUID),
                            attribute_name=OBJECT_CLASS_ATTRIBUTE_UUID.label,
                            value=object_class_uuid,
                            frame_id=frame_id,
                            confidence=confidence,
                        )
                    )

                    # Create pixel_location AttributeRecord from bounds or wkt
                    geometry = None
                    if detection.get("bounds") is not None:
                        bounds = detection["bounds"]
                        min_pt = bounds["min"]
                        max_pt = bounds["max"]
                        # Create box geometry from bounds
                        geometry = shapely_box(min_pt["x"], min_pt["y"], max_pt["x"], max_pt["y"])
                    elif detection.get("wkt") is not None:
                        try:
                            geometry = wkt_loads(detection["wkt"])
                            geometry = try_make_polygon_valid_if_invalid(geometry)
                        except Exception as e:
                            warn(f"Invalid WKT in avro detection: {e}")
                            continue

                    if geometry is not None:
                        pixel_location_attribute_value = PixelLocationAttributeValue.from_geom(
                            geometry, confidence=confidence
                        )
                        attribute_records.append(
                            AttributeRecord.from_attribute_value(
                                data_file_id,
                                pixel_location_attribute_value,
                                entity_id=entity_id,
                                frame_id=frame_id,
                            )
                        )

                # Process eavts (entity attribute values)
                for eavt in track.get("eavts", []):
                    # Skip eavts with null values as they don't provide useful information
                    if eavt.get("value") is None:
                        continue

                    entity_datum_source = eavt.get("entityDatumSource")
                    if entity_datum_source:
                        conf = entity_datum_source.get("confidence", 1.0)
                        eavt_frame_id = entity_datum_source.get("frameId")
                    else:
                        conf = 1.0
                        eavt_frame_id = None

                    # Ensure frame_id is always an integer (0 for images/missing frameId)
                    if eavt_frame_id is None:
                        eavt_frame_id = 0

                    attribute_records.append(
                        AttributeRecord(
                            data_file_id=data_file_id,
                            entity_id=UUID(eavt["entityId"]),
                            attribute_id=eavt["entityAttributeId"],
                            attribute_name=eavt[
                                "entityAttributeId"
                            ],  # Use ID as name since we don't have name in avro
                            value=eavt["value"],
                            confidence=conf,
                            frame_id=eavt_frame_id,
                        )
                    )

    def read(self) -> Tuple[List[AttributeRecord], List[ImageRecord]]:
        attribute_records = []
        data_file_records = []
        for assessment in self.assessments_gen:
            assessment_id = assessment.id
            hash_signature = assessment.hash_signature

            # Find the media data_file (video or image). Fall back to the first
            # available file if content_type metadata is missing so legacy
            # assessments still load.
            data_file_id = None
            media_data_files = []
            for df in assessment.data_files:
                if hasattr(df, "content_type") and df.content_type in ("video", "image"):
                    media_data_files.append(df)

            if not media_data_files and getattr(assessment, "data_files", None):
                media_data_files = [assessment.data_files[0]]

            if len(media_data_files) > 1:
                # TODO: Add annotation_id &| data_file_id to entity_attribute_value in HL Web
                raise NotImplementedError("We currently only support 1 media_data_file per submission")
            if len(media_data_files) == 0:
                raise ValueError(f"Assessment {assessment_id} has no media_data_file")

            for media_data_file in media_data_files:
                raw_id = getattr(media_data_file, "uuid", getattr(media_data_file, "id", None))
                if raw_id is None:
                    continue

                data_file_id = str(raw_id)
                filename_original = Path(media_data_file.original_source_url)

                ext = filename_original.suffix.lower()
                if ext == "":
                    ext = mimetypes.guess_extension(media_data_file.mime_type)
                    assert isinstance(ext, str)
                    ext = ext.lower()

                filename = f"{data_file_id}{ext}"

                data_file_records.append(
                    ImageRecord(
                        data_file_id=data_file_id,
                        width=media_data_file.width,
                        height=media_data_file.height,
                        filename=filename,
                        extra_fields={"filename_original": str(filename_original)},
                        assessment_id=assessment_id,
                        hash_signature=hash_signature,
                    )
                )

            # Collect all avro URLs to load
            avro_urls = []

            # Add background_info_layer_file if present
            if (
                hasattr(assessment, "background_info_layer_file_cacheable_url")
                and assessment.background_info_layer_file_cacheable_url
            ):
                avro_urls.append(assessment.background_info_layer_file_cacheable_url)

            # Add entity data_files
            for df in assessment.data_files:
                if hasattr(df, "content_type") and df.content_type == "entities":
                    if hasattr(df, "cacheable_url") and df.cacheable_url:
                        avro_urls.append(df.cacheable_url)

            # Load and process all avro files
            for avro_url in avro_urls:
                try:
                    # Load avro entities from URL
                    avro_entities = read_avro_file_from_url(avro_url)
                    # Process entities and add to attribute_records
                    self._process_avro_entities(avro_entities, attribute_records)
                except Exception as e:
                    warn(f"Failed to load avro file {avro_url} for assessment {assessment_id}: {e}")

            raw_id = getattr(media_data_files[0], "uuid", getattr(media_data_files[0], "id", None))
            if raw_id is not None:
                data_file_id = str(raw_id)
            for eavt in assessment.entity_attribute_values:
                value = eavt.value
                if value is None:
                    value = eavt.entity_attribute_enum.id

                datum_source = eavt.entity_datum_source
                if datum_source is None:
                    conf = 1.0
                    frame_id = 0
                else:
                    conf = datum_source.confidence
                    frame_id = eavt.entity_datum_source.frame_id

                attribute_records.append(
                    AttributeRecord(
                        data_file_id=data_file_id,
                        entity_id=eavt.entity_id,
                        attribute_id=eavt.entity_attribute.id,
                        attribute_name=eavt.entity_attribute.name,
                        value=value,
                        frame_id=frame_id,
                        confidence=conf,
                    )
                )

            for annotation in assessment.annotations:
                if annotation.location is None:
                    warn("Null value found in location. Get it together bro.")
                    continue

                confidence = getattr(annotation, "confidence", None)
                try:
                    geometry = wkt_loads(annotation.location)
                    geometry = try_make_polygon_valid_if_invalid(geometry)
                    pixel_location_attribute_value = PixelLocationAttributeValue.from_geom(
                        geometry, confidence=confidence
                    )
                except Exception as e:
                    print(
                        f"Invalid Polygon, assessment: {assessment_id}, annotation: {annotation.id}, data_file: {data_file_id} "
                    )
                    continue

                if str(annotation.data_file_id) != str(data_file_id):
                    raise ValueError(
                        f"annotation.data_file_id:{annotation.data_file_id} != media_data_file_id:{data_file_id}"
                    )

                object_class = annotation.object_class
                attribute_records.append(
                    AttributeRecord(
                        data_file_id=str(annotation.data_file_id),
                        entity_id=annotation.entity_id,
                        attribute_id=str(OBJECT_CLASS_ATTRIBUTE_UUID),
                        attribute_name=OBJECT_CLASS_ATTRIBUTE_UUID.label,
                        value=str(object_class.uuid),
                        frame_id=annotation.frame_id,
                        confidence=confidence,
                    )
                )

                attribute_records.append(
                    AttributeRecord.from_attribute_value(
                        str(annotation.data_file_id),
                        pixel_location_attribute_value,
                        entity_id=annotation.entity_id,
                        frame_id=annotation.frame_id,
                    )
                )

        return data_file_records, attribute_records

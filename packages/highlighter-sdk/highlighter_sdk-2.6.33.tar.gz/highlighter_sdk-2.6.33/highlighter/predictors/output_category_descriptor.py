from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from highlighter.core.const import OBJECT_CLASS_ATTRIBUTE_UUID


class ObjectClassDescriptor(BaseModel):
    """
    ObjectClassDescriptor([object_class_uuid, object_class_label])
    """

    uuid: UUID
    label: str

    @model_validator(mode="before")
    def validate(cls, v):
        if isinstance(v, dict):
            return v
        elif len(v) == 2:
            return dict(zip(["uuid", "label"], v))
        else:
            raise ValueError(f"Unkonwn {cls.__name__} args: {v}")


class ObjectClassDescriptorWithConfidenceThreshold(BaseModel):
    """
    ObjectClassDescriptorWithConfidenceThreshold(
        [object_class_uuid, object_class_label, confidence_threshold])
    """

    uuid: UUID
    label: str
    confidence_threshold: float = Field(ge=0, le=1)

    @model_validator(mode="before")
    def validate(cls, v):
        if isinstance(v, dict):
            return v
        elif len(v) == 3:
            return dict(zip(["uuid", "label", "confidence_threshold"], v))
        else:
            raise ValueError(f"Unkonwn {cls.__name__} args: {v}")


class EnumDescriptor(BaseModel):
    """
    EnumDescriptor([attribute_id, attribute_label, enum_id, enum_label])
    """

    attribute_id: UUID
    attribute_label: str
    enum_id: UUID
    enum_label: str

    @model_validator(mode="before")
    def validate(cls, v):
        if isinstance(v, dict):
            return v
        elif len(v) == 4:
            return dict(zip(["attribute_id", "attribute_label", "enum_id", "enum_label"], v))
        else:
            raise ValueError(f"Unkonwn {cls.__name__} args: {v}")


class EnumDescriptorWithConfidenceThreshold(BaseModel):
    """
    EnumDescriptorWithConfidenceThreshold(
        [attribute_id, attribute_label, enum_id, enum_label, confidence_threshold])
    """

    attribute_id: UUID
    attribute_label: str
    enum_id: UUID
    enum_label: str
    confidence_threshold: float = Field(ge=0, le=1)

    @model_validator(mode="before")
    def validate(cls, v):
        if isinstance(v, dict):
            return v
        elif len(v) == 5:
            return dict(
                zip(["attribute_id", "attribute_label", "enum_id", "enum_label", "confidence_threshold"], v)
            )
        else:
            raise ValueError(f"Unkonwn {cls.__name__} args: {v}")

    @classmethod
    def from_output_category_descriptor(
        cls, output_category_descriptor: "OutputCategoryDescriptor", default_confidence_threshold: float = 0.0
    ):
        if isinstance(output_category_descriptor, ObjectClassDescriptor):
            return cls(
                attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
                attribute_label="object_class",
                enum_id=output_category_descriptor.uuid,
                enum_label=output_category_descriptor.label,
                confidence_threshold=default_confidence_threshold,
            )
        if isinstance(output_category_descriptor, ObjectClassDescriptorWithConfidenceThreshold):
            return cls(
                attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
                attribute_label="object_class",
                enum_id=output_category_descriptor.uuid,
                enum_label=output_category_descriptor.label,
                confidence_threshold=output_category_descriptor.confidence_threshold,
            )
        if isinstance(output_category_descriptor, EnumDescriptor):
            return cls(
                **output_category_descriptor.model_dump(), confidence_threshold=default_confidence_threshold
            )
        if isinstance(output_category_descriptor, EnumDescriptorWithConfidenceThreshold):
            return output_category_descriptor


OutputCategoryDescriptor = (
    ObjectClassDescriptor
    | ObjectClassDescriptorWithConfidenceThreshold
    | EnumDescriptor
    | EnumDescriptorWithConfidenceThreshold
)

# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import (
    Generic,
    TypeVar,
    get_type_hints,
)

from google.protobuf.message import Message

from luminarycloud._proto.base import base_pb2 as basepb
from luminarycloud.types import Vector3
from luminarycloud.types.adfloat import _from_ad_proto, _to_ad_proto
from luminarycloud.types.vector3 import _to_vector3_ad_proto

P = TypeVar("P", bound=Message)
C = TypeVar("C")


class ProtoConvertible(Generic[P]):
    """
    Abstract mixin to satisfy the type checker when using `@proto_decorator`.
    Declares statically that `_to_proto` and `_from_proto` will be added by the decorator.
    """

    def _to_proto(self) -> P: ...

    def _from_proto(self, proto: P) -> None: ...


class proto_decorator(Generic[P]):
    """
    A decorator that adds `_to_proto` and `_from_proto` methods to instances of a class and a
    `from_proto` method to the class.

    NOTE: only works for primitive, Vector3, AdFloatType, and AdVector3 fields right now.
    """

    proto_type: type[P]

    def __init__(decorator, proto_type: type[P]):
        decorator.proto_type = proto_type

    def __call__(decorator, cls: type[C]) -> type[C]:
        type_hints = get_type_hints(cls)
        fields = decorator.proto_type.DESCRIPTOR.fields

        def _to_proto(self: type[C]) -> P:
            proto = decorator.proto_type()
            for field in fields:
                _type = type_hints.get(field.name, None)
                if _type:
                    value = getattr(self, field.name)
                    proto_value = getattr(proto, field.name)
                    if issubclass(_type, float) and isinstance(proto_value, basepb.AdFloatType):
                        proto_value.CopyFrom(_to_ad_proto(value))
                    elif issubclass(_type, Vector3):
                        if isinstance(proto_value, basepb.AdVector3):
                            proto_value.CopyFrom(_to_vector3_ad_proto((value.x, value.y, value.z)))
                        else:
                            proto_value.x = value.x
                            proto_value.y = value.y
                            proto_value.z = value.z
                    else:
                        setattr(proto, field.name, value)
            return proto

        setattr(cls, "_to_proto", _to_proto)

        def _from_proto(self: type[C], proto: type[P]) -> None:
            for field in fields:
                _type = type_hints.get(field.name, None)
                if _type:
                    proto_value = getattr(proto, field.name)
                    if isinstance(proto_value, basepb.AdFloatType):
                        setattr(self, field.name, _from_ad_proto(proto_value))
                    elif issubclass(_type, Vector3):
                        vec = getattr(self, field.name)
                        if isinstance(proto_value, basepb.Vector3):
                            vec._from_proto(proto_value)
                        elif isinstance(proto_value, basepb.AdVector3):
                            vec._from_ad_proto(proto_value)
                    else:
                        setattr(self, field.name, proto_value)
            return None

        setattr(cls, "_from_proto", _from_proto)

        return cls

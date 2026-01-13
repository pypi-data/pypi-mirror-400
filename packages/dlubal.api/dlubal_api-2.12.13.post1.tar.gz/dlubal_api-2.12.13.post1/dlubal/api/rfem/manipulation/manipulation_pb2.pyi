from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class DirectionThrough(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIRECTION_THROUGH_UNSPECIFIED: _ClassVar[DirectionThrough]
    DIRECTION_THROUGH_DISPLACEMENT_VECTOR: _ClassVar[DirectionThrough]
    DIRECTION_THROUGH_PARALLEL_TO_AXIS: _ClassVar[DirectionThrough]

class CoordinateAxis(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COORDINATE_AXIS_UNSPECIFIED: _ClassVar[CoordinateAxis]
    COORDINATE_AXIS_X: _ClassVar[CoordinateAxis]
    COORDINATE_AXIS_Y: _ClassVar[CoordinateAxis]
    COORDINATE_AXIS_Z: _ClassVar[CoordinateAxis]

class RotationAxisSpecificationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROTATION_AXIS_SPECIFICATION_TYPE_UNSPECIFIED: _ClassVar[RotationAxisSpecificationType]
    ROTATION_AXIS_SPECIFICATION_TYPE_POINT_AND_PARALLEL_AXIS: _ClassVar[RotationAxisSpecificationType]
    ROTATION_AXIS_SPECIFICATION_TYPE_TWO_POINTS: _ClassVar[RotationAxisSpecificationType]
DIRECTION_THROUGH_UNSPECIFIED: DirectionThrough
DIRECTION_THROUGH_DISPLACEMENT_VECTOR: DirectionThrough
DIRECTION_THROUGH_PARALLEL_TO_AXIS: DirectionThrough
COORDINATE_AXIS_UNSPECIFIED: CoordinateAxis
COORDINATE_AXIS_X: CoordinateAxis
COORDINATE_AXIS_Y: CoordinateAxis
COORDINATE_AXIS_Z: CoordinateAxis
ROTATION_AXIS_SPECIFICATION_TYPE_UNSPECIFIED: RotationAxisSpecificationType
ROTATION_AXIS_SPECIFICATION_TYPE_POINT_AND_PARALLEL_AXIS: RotationAxisSpecificationType
ROTATION_AXIS_SPECIFICATION_TYPE_TWO_POINTS: RotationAxisSpecificationType

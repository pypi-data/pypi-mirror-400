from dlubal.api.common import common_pb2 as _common_pb2
from dlubal.api.rfem import referenced_object_pb2 as _referenced_object_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceCellSet(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "set_type", "surface_cells", "area", "volume", "mass", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "center_of_gravity", "center_point_x", "center_point_y", "center_point_z", "center_point", "id_for_export_import", "metadata_for_export_import")
    class SetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SET_TYPE_CONTINUOUS: _ClassVar[SurfaceCellSet.SetType]
        SET_TYPE_GROUP: _ClassVar[SurfaceCellSet.SetType]
    SET_TYPE_CONTINUOUS: SurfaceCellSet.SetType
    SET_TYPE_GROUP: SurfaceCellSet.SetType
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    SET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SURFACE_CELLS_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_Z_FIELD_NUMBER: _ClassVar[int]
    CENTER_POINT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    set_type: SurfaceCellSet.SetType
    surface_cells: _containers.RepeatedScalarFieldContainer[int]
    area: float
    volume: float
    mass: float
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    center_of_gravity: _common_pb2.Vector3d
    center_point_x: float
    center_point_y: float
    center_point_z: float
    center_point: _common_pb2.Vector3d
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., set_type: _Optional[_Union[SurfaceCellSet.SetType, str]] = ..., surface_cells: _Optional[_Iterable[int]] = ..., area: _Optional[float] = ..., volume: _Optional[float] = ..., mass: _Optional[float] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_point_x: _Optional[float] = ..., center_point_y: _Optional[float] = ..., center_point_z: _Optional[float] = ..., center_point: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

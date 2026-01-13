from google.protobuf import empty_pb2 as _empty_pb2
from dlubal.api.common import common_pb2 as _common_pb2
from dlubal.api.common import model_id_pb2 as _model_id_pb2
from dlubal.api.common import common_messages_pb2 as _common_messages_pb2
from dlubal.api.rsection import base_data_pb2 as _base_data_pb2
from dlubal.api.rsection.manipulation import manipulation_pb2 as _manipulation_pb2
from dlubal.api.rsection import object_type_pb2 as _object_type_pb2
from dlubal.api.rsection import object_id_pb2 as _object_id_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetObjectIdListRequest(_message.Message):
    __slots__ = ("object_type", "parent_no", "model_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARENT_NO_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: _object_type_pb2.ObjectType
    parent_no: int
    model_id: _model_id_pb2.ModelId
    def __init__(self, object_type: _Optional[_Union[_object_type_pb2.ObjectType, str]] = ..., parent_no: _Optional[int] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class BaseDataRequest(_message.Message):
    __slots__ = ("base_data", "model_id")
    BASE_DATA_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    base_data: _base_data_pb2.BaseData
    model_id: _model_id_pb2.ModelId
    def __init__(self, base_data: _Optional[_Union[_base_data_pb2.BaseData, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class SaveModelAsRequest(_message.Message):
    __slots__ = ("model_id", "path", "printout_reports")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    PRINTOUT_REPORTS_FIELD_NUMBER: _ClassVar[int]
    model_id: _model_id_pb2.ModelId
    path: str
    printout_reports: bool
    def __init__(self, model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ..., path: _Optional[str] = ..., printout_reports: bool = ...) -> None: ...

class MoveObjectsRequest(_message.Message):
    __slots__ = ("objects", "direction_through", "displacement_vector", "axis", "create_copy", "number_of_steps", "spacing")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_THROUGH_FIELD_NUMBER: _ClassVar[int]
    DISPLACEMENT_VECTOR_FIELD_NUMBER: _ClassVar[int]
    AXIS_FIELD_NUMBER: _ClassVar[int]
    CREATE_COPY_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_STEPS_FIELD_NUMBER: _ClassVar[int]
    SPACING_FIELD_NUMBER: _ClassVar[int]
    objects: _common_messages_pb2.ObjectList
    direction_through: _manipulation_pb2.DirectionThrough
    displacement_vector: _common_pb2.Vector2d
    axis: _manipulation_pb2.CoordinateAxis
    create_copy: bool
    number_of_steps: int
    spacing: float
    def __init__(self, objects: _Optional[_Union[_common_messages_pb2.ObjectList, _Mapping]] = ..., direction_through: _Optional[_Union[_manipulation_pb2.DirectionThrough, str]] = ..., displacement_vector: _Optional[_Union[_common_pb2.Vector2d, _Mapping]] = ..., axis: _Optional[_Union[_manipulation_pb2.CoordinateAxis, str]] = ..., create_copy: bool = ..., number_of_steps: _Optional[int] = ..., spacing: _Optional[float] = ...) -> None: ...

class RotateObjectsRequest(_message.Message):
    __slots__ = ("objects", "rotation_angle", "point_1", "create_copy", "number_of_steps")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    POINT_1_FIELD_NUMBER: _ClassVar[int]
    CREATE_COPY_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_STEPS_FIELD_NUMBER: _ClassVar[int]
    objects: _common_messages_pb2.ObjectList
    rotation_angle: float
    point_1: _common_pb2.Vector2d
    create_copy: bool
    number_of_steps: int
    def __init__(self, objects: _Optional[_Union[_common_messages_pb2.ObjectList, _Mapping]] = ..., rotation_angle: _Optional[float] = ..., point_1: _Optional[_Union[_common_pb2.Vector2d, _Mapping]] = ..., create_copy: bool = ..., number_of_steps: _Optional[int] = ...) -> None: ...

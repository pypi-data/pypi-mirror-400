from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from dlubal.api.common import common_pb2 as _common_pb2
from dlubal.api.common import model_id_pb2 as _model_id_pb2
from dlubal.api.common import table_data_pb2 as _table_data_pb2
from dlubal.api.common import common_messages_pb2 as _common_messages_pb2
from dlubal.api.rfem import base_data_pb2 as _base_data_pb2
from dlubal.api.rfem import design_addons_pb2 as _design_addons_pb2
from dlubal.api.rfem.manipulation import manipulation_pb2 as _manipulation_pb2
from dlubal.api.rfem import object_type_pb2 as _object_type_pb2
from dlubal.api.rfem import object_id_pb2 as _object_id_pb2
from dlubal.api.rfem.mesh import mesh_settings_pb2 as _mesh_settings_pb2
from dlubal.api.rfem.results import result_table_pb2 as _result_table_pb2
from dlubal.api.rfem.results import results_query_pb2 as _results_query_pb2
from dlubal.api.rfem.results.settings import result_settings_pb2 as _result_settings_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class GlobalSettingsTreeTable(_message.Message):
    __slots__ = ("rows",)
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[GlobalSettingsRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[GlobalSettingsRow, _Mapping]]] = ...) -> None: ...

class GlobalSettingsRow(_message.Message):
    __slots__ = ("key", "caption", "symbol", "value", "unit", "rows")
    KEY_FIELD_NUMBER: _ClassVar[int]
    CAPTION_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    key: str
    caption: str
    symbol: str
    value: _common_pb2.Value
    unit: str
    rows: _containers.RepeatedCompositeFieldContainer[GlobalSettingsRow]
    def __init__(self, key: _Optional[str] = ..., caption: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., unit: _Optional[str] = ..., rows: _Optional[_Iterable[_Union[GlobalSettingsRow, _Mapping]]] = ...) -> None: ...

class GetDesignSettingsRequest(_message.Message):
    __slots__ = ("addon", "model_id")
    ADDON_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    addon: _design_addons_pb2.DesignAddons
    model_id: _model_id_pb2.ModelId
    def __init__(self, addon: _Optional[_Union[_design_addons_pb2.DesignAddons, str]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class SetDesignSettingsRequest(_message.Message):
    __slots__ = ("addon", "global_settings_tree_table", "model_id")
    ADDON_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_SETTINGS_TREE_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    addon: _design_addons_pb2.DesignAddons
    global_settings_tree_table: GlobalSettingsTreeTable
    model_id: _model_id_pb2.ModelId
    def __init__(self, addon: _Optional[_Union[_design_addons_pb2.DesignAddons, str]] = ..., global_settings_tree_table: _Optional[_Union[GlobalSettingsTreeTable, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class HasResultsRequest(_message.Message):
    __slots__ = ("loading", "model_id")
    LOADING_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    loading: _object_id_pb2.ObjectId
    model_id: _model_id_pb2.ModelId
    def __init__(self, loading: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class GetResultTableRequest(_message.Message):
    __slots__ = ("table", "loading", "model_id", "member_axes_system", "support_coordinate_system")
    TABLE_FIELD_NUMBER: _ClassVar[int]
    LOADING_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_AXES_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    table: _result_table_pb2.ResultTable
    loading: _object_id_pb2.ObjectId
    model_id: _model_id_pb2.ModelId
    member_axes_system: _result_settings_pb2.MemberAxesSystem
    support_coordinate_system: _result_settings_pb2.CoordinateSystem
    def __init__(self, table: _Optional[_Union[_result_table_pb2.ResultTable, str]] = ..., loading: _Optional[_Union[_object_id_pb2.ObjectId, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ..., member_axes_system: _Optional[_Union[_result_settings_pb2.MemberAxesSystem, str]] = ..., support_coordinate_system: _Optional[_Union[_result_settings_pb2.CoordinateSystem, str]] = ...) -> None: ...

class CalculateSpecificRequest(_message.Message):
    __slots__ = ("loadings", "skip_warnings", "model_id")
    LOADINGS_FIELD_NUMBER: _ClassVar[int]
    SKIP_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    loadings: _containers.RepeatedCompositeFieldContainer[_object_id_pb2.ObjectId]
    skip_warnings: bool
    model_id: _model_id_pb2.ModelId
    def __init__(self, loadings: _Optional[_Iterable[_Union[_object_id_pb2.ObjectId, _Mapping]]] = ..., skip_warnings: bool = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class SetMeshSettingsRequest(_message.Message):
    __slots__ = ("mesh_settings", "model_id")
    MESH_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    mesh_settings: _mesh_settings_pb2.MeshSettings
    model_id: _model_id_pb2.ModelId
    def __init__(self, mesh_settings: _Optional[_Union[_mesh_settings_pb2.MeshSettings, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class GenerateMeshRequest(_message.Message):
    __slots__ = ("skip_warnings", "model_id")
    SKIP_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    skip_warnings: bool
    model_id: _model_id_pb2.ModelId
    def __init__(self, skip_warnings: bool = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class SaveModelAsRequest(_message.Message):
    __slots__ = ("model_id", "path", "results", "fe_mesh", "printout_reports")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    FE_MESH_FIELD_NUMBER: _ClassVar[int]
    PRINTOUT_REPORTS_FIELD_NUMBER: _ClassVar[int]
    model_id: _model_id_pb2.ModelId
    path: str
    results: bool
    fe_mesh: bool
    printout_reports: bool
    def __init__(self, model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ..., path: _Optional[str] = ..., results: bool = ..., fe_mesh: bool = ..., printout_reports: bool = ...) -> None: ...

class MoveObjectsRequest(_message.Message):
    __slots__ = ("objects", "direction_through", "displacement_vector", "axis", "coordinate_system", "create_copy", "number_of_steps", "spacing", "copy_including_loading", "copy_including_imperfections", "connect_lines_members_surfaces")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_THROUGH_FIELD_NUMBER: _ClassVar[int]
    DISPLACEMENT_VECTOR_FIELD_NUMBER: _ClassVar[int]
    AXIS_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    CREATE_COPY_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_STEPS_FIELD_NUMBER: _ClassVar[int]
    SPACING_FIELD_NUMBER: _ClassVar[int]
    COPY_INCLUDING_LOADING_FIELD_NUMBER: _ClassVar[int]
    COPY_INCLUDING_IMPERFECTIONS_FIELD_NUMBER: _ClassVar[int]
    CONNECT_LINES_MEMBERS_SURFACES_FIELD_NUMBER: _ClassVar[int]
    objects: _common_messages_pb2.ObjectList
    direction_through: _manipulation_pb2.DirectionThrough
    displacement_vector: _common_pb2.Vector3d
    axis: _manipulation_pb2.CoordinateAxis
    coordinate_system: int
    create_copy: bool
    number_of_steps: int
    spacing: float
    copy_including_loading: bool
    copy_including_imperfections: bool
    connect_lines_members_surfaces: bool
    def __init__(self, objects: _Optional[_Union[_common_messages_pb2.ObjectList, _Mapping]] = ..., direction_through: _Optional[_Union[_manipulation_pb2.DirectionThrough, str]] = ..., displacement_vector: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., axis: _Optional[_Union[_manipulation_pb2.CoordinateAxis, str]] = ..., coordinate_system: _Optional[int] = ..., create_copy: bool = ..., number_of_steps: _Optional[int] = ..., spacing: _Optional[float] = ..., copy_including_loading: bool = ..., copy_including_imperfections: bool = ..., connect_lines_members_surfaces: bool = ...) -> None: ...

class RotateObjectsRequest(_message.Message):
    __slots__ = ("objects", "rotation_angle", "rotation_axis", "point_1", "point_2", "axis", "coordinate_system", "create_copy", "number_of_steps", "copy_including_loading", "copy_including_imperfections", "connect_lines_members_surfaces", "rotate_local_coordinate_systems_of_lines_members", "adjust_loading_nodal_loads")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_AXIS_FIELD_NUMBER: _ClassVar[int]
    POINT_1_FIELD_NUMBER: _ClassVar[int]
    POINT_2_FIELD_NUMBER: _ClassVar[int]
    AXIS_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    CREATE_COPY_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_STEPS_FIELD_NUMBER: _ClassVar[int]
    COPY_INCLUDING_LOADING_FIELD_NUMBER: _ClassVar[int]
    COPY_INCLUDING_IMPERFECTIONS_FIELD_NUMBER: _ClassVar[int]
    CONNECT_LINES_MEMBERS_SURFACES_FIELD_NUMBER: _ClassVar[int]
    ROTATE_LOCAL_COORDINATE_SYSTEMS_OF_LINES_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ADJUST_LOADING_NODAL_LOADS_FIELD_NUMBER: _ClassVar[int]
    objects: _common_messages_pb2.ObjectList
    rotation_angle: float
    rotation_axis: _manipulation_pb2.RotationAxisSpecificationType
    point_1: _common_pb2.Vector3d
    point_2: _common_pb2.Vector3d
    axis: _manipulation_pb2.CoordinateAxis
    coordinate_system: int
    create_copy: bool
    number_of_steps: int
    copy_including_loading: bool
    copy_including_imperfections: bool
    connect_lines_members_surfaces: bool
    rotate_local_coordinate_systems_of_lines_members: bool
    adjust_loading_nodal_loads: bool
    def __init__(self, objects: _Optional[_Union[_common_messages_pb2.ObjectList, _Mapping]] = ..., rotation_angle: _Optional[float] = ..., rotation_axis: _Optional[_Union[_manipulation_pb2.RotationAxisSpecificationType, str]] = ..., point_1: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., point_2: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., axis: _Optional[_Union[_manipulation_pb2.CoordinateAxis, str]] = ..., coordinate_system: _Optional[int] = ..., create_copy: bool = ..., number_of_steps: _Optional[int] = ..., copy_including_loading: bool = ..., copy_including_imperfections: bool = ..., connect_lines_members_surfaces: bool = ..., rotate_local_coordinate_systems_of_lines_members: bool = ..., adjust_loading_nodal_loads: bool = ...) -> None: ...

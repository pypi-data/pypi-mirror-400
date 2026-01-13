from dlubal.api.rsection import object_type_pb2 as _object_type_pb2
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
REFERENCED_OBJECTS_FIELD_NUMBER: _ClassVar[int]
referenced_objects: _descriptor.FieldDescriptor

class ReferencedObject(_message.Message):
    __slots__ = ("object_type", "object_message_name")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_MESSAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    object_type: _object_type_pb2.ObjectType
    object_message_name: str
    def __init__(self, object_type: _Optional[_Union[_object_type_pb2.ObjectType, str]] = ..., object_message_name: _Optional[str] = ...) -> None: ...

from conveyor.pb.buf.validate import validate_pb2 as _validate_pb2
from google.api import annotations_pb2 as _annotations_pb2
from conveyor.pb.tagger import tagger_pb2 as _tagger_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagColor(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    magenta: _ClassVar[TagColor]
    red: _ClassVar[TagColor]
    volcano: _ClassVar[TagColor]
    orange: _ClassVar[TagColor]
    gold: _ClassVar[TagColor]
    lime: _ClassVar[TagColor]
    green: _ClassVar[TagColor]
    cyan: _ClassVar[TagColor]
    blue: _ClassVar[TagColor]
    geekblue: _ClassVar[TagColor]
    purple: _ClassVar[TagColor]
magenta: TagColor
red: TagColor
volcano: TagColor
orange: TagColor
gold: TagColor
lime: TagColor
green: TagColor
cyan: TagColor
blue: TagColor
geekblue: TagColor
purple: TagColor

class ResourceTag(_message.Message):
    __slots__ = ("id", "name", "description", "color")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    color: TagColor
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., color: _Optional[_Union[TagColor, str]] = ...) -> None: ...

class CreateTagRequest(_message.Message):
    __slots__ = ("name", "description", "color")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    color: TagColor
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., color: _Optional[_Union[TagColor, str]] = ...) -> None: ...

class UpdateTagRequest(_message.Message):
    __slots__ = ("tag_id", "name", "description", "color")
    TAG_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    tag_id: str
    name: str
    description: str
    color: TagColor
    def __init__(self, tag_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., color: _Optional[_Union[TagColor, str]] = ...) -> None: ...

class DeleteTagRequest(_message.Message):
    __slots__ = ("tag_id",)
    TAG_ID_FIELD_NUMBER: _ClassVar[int]
    tag_id: str
    def __init__(self, tag_id: _Optional[str] = ...) -> None: ...

class GetTagRequest(_message.Message):
    __slots__ = ("tag_id",)
    TAG_ID_FIELD_NUMBER: _ClassVar[int]
    tag_id: str
    def __init__(self, tag_id: _Optional[str] = ...) -> None: ...

class GetTagsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListTagsResponse(_message.Message):
    __slots__ = ("tags",)
    TAGS_FIELD_NUMBER: _ClassVar[int]
    tags: _containers.RepeatedCompositeFieldContainer[ResourceTag]
    def __init__(self, tags: _Optional[_Iterable[_Union[ResourceTag, _Mapping]]] = ...) -> None: ...

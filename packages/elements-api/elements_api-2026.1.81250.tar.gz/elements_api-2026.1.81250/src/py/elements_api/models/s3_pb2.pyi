import common_models_pb2 as _common_models_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
from common_models_pb2 import Pagination as Pagination

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateS3PresignedUrlsPostRequest(_message.Message):
    __slots__ = ("container", "object_paths", "expiration_in_seconds", "user_id")
    CONTAINER_FIELD_NUMBER: _ClassVar[int]
    OBJECT_PATHS_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    container: str
    object_paths: _containers.RepeatedScalarFieldContainer[str]
    expiration_in_seconds: float
    user_id: str
    def __init__(self, container: _Optional[str] = ..., object_paths: _Optional[_Iterable[str]] = ..., expiration_in_seconds: _Optional[float] = ..., user_id: _Optional[str] = ...) -> None: ...

class PresignedPostData(_message.Message):
    __slots__ = ("url", "fields")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URL_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    url: str
    fields: _containers.ScalarMap[str, str]
    def __init__(self, url: _Optional[str] = ..., fields: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GenerateS3PresignedUrlsPostResponse(_message.Message):
    __slots__ = ("uploads",)
    class UploadsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PresignedPostData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PresignedPostData, _Mapping]] = ...) -> None: ...
    UPLOADS_FIELD_NUMBER: _ClassVar[int]
    uploads: _containers.MessageMap[str, PresignedPostData]
    def __init__(self, uploads: _Optional[_Mapping[str, PresignedPostData]] = ...) -> None: ...

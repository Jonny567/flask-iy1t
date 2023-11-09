"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Copyright 2009 Google Inc. All Rights Reserved."""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class OuterMessage(google.protobuf.message.Message):
    """OuterMessage - base outer message type used in the protocol."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _Status:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _StatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[OuterMessage._Status.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        STATUS_OK: OuterMessage._Status.ValueType  # 200
        STATUS_ERROR: OuterMessage._Status.ValueType  # 400
        STATUS_BAD_CONFIGURATION: OuterMessage._Status.ValueType  # 401
        STATUS_BAD_SECRET: OuterMessage._Status.ValueType  # 402

    class Status(_Status, metaclass=_StatusEnumTypeWrapper):
        """Protocol status states."""

    STATUS_OK: OuterMessage.Status.ValueType  # 200
    STATUS_ERROR: OuterMessage.Status.ValueType  # 400
    STATUS_BAD_CONFIGURATION: OuterMessage.Status.ValueType  # 401
    STATUS_BAD_SECRET: OuterMessage.Status.ValueType  # 402

    PROTOCOL_VERSION_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    PAIRING_REQUEST_FIELD_NUMBER: builtins.int
    PAIRING_REQUEST_ACK_FIELD_NUMBER: builtins.int
    OPTIONS_FIELD_NUMBER: builtins.int
    CONFIGURATION_FIELD_NUMBER: builtins.int
    CONFIGURATION_ACK_FIELD_NUMBER: builtins.int
    SECRET_FIELD_NUMBER: builtins.int
    SECRET_ACK_FIELD_NUMBER: builtins.int
    protocol_version: builtins.int
    status: global___OuterMessage.Status.ValueType
    """Protocol status. Any status other than STATUS_OK implies a fault."""
    @property
    def pairing_request(self) -> global___PairingRequest:
        """Initialization phase"""
    @property
    def pairing_request_ack(self) -> global___PairingRequestAck: ...
    @property
    def options(self) -> global___Options:
        """Configuration phase"""
    @property
    def configuration(self) -> global___Configuration: ...
    @property
    def configuration_ack(self) -> global___ConfigurationAck: ...
    @property
    def secret(self) -> global___Secret:
        """Pairing phase"""
    @property
    def secret_ack(self) -> global___SecretAck: ...
    def __init__(
        self,
        *,
        protocol_version: builtins.int | None = ...,
        status: global___OuterMessage.Status.ValueType | None = ...,
        pairing_request: global___PairingRequest | None = ...,
        pairing_request_ack: global___PairingRequestAck | None = ...,
        options: global___Options | None = ...,
        configuration: global___Configuration | None = ...,
        configuration_ack: global___ConfigurationAck | None = ...,
        secret: global___Secret | None = ...,
        secret_ack: global___SecretAck | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["configuration", b"configuration", "configuration_ack", b"configuration_ack", "options", b"options", "pairing_request", b"pairing_request", "pairing_request_ack", b"pairing_request_ack", "protocol_version", b"protocol_version", "secret", b"secret", "secret_ack", b"secret_ack", "status", b"status"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["configuration", b"configuration", "configuration_ack", b"configuration_ack", "options", b"options", "pairing_request", b"pairing_request", "pairing_request_ack", b"pairing_request_ack", "protocol_version", b"protocol_version", "secret", b"secret", "secret_ack", b"secret_ack", "status", b"status"]) -> None: ...

global___OuterMessage = OuterMessage

@typing_extensions.final
class PairingRequest(google.protobuf.message.Message):
    """
    Initialization messages
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SERVICE_NAME_FIELD_NUMBER: builtins.int
    CLIENT_NAME_FIELD_NUMBER: builtins.int
    service_name: builtins.str
    """String name of the service to pair with.  The name used should be an
    established convention of the application protocol.
    """
    client_name: builtins.str
    """Descriptive name of the client."""
    def __init__(
        self,
        *,
        service_name: builtins.str | None = ...,
        client_name: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["client_name", b"client_name", "service_name", b"service_name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["client_name", b"client_name", "service_name", b"service_name"]) -> None: ...

global___PairingRequest = PairingRequest

@typing_extensions.final
class PairingRequestAck(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SERVER_NAME_FIELD_NUMBER: builtins.int
    server_name: builtins.str
    """Descriptive name of the server."""
    def __init__(
        self,
        *,
        server_name: builtins.str | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["server_name", b"server_name"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["server_name", b"server_name"]) -> None: ...

global___PairingRequestAck = PairingRequestAck

@typing_extensions.final
class Options(google.protobuf.message.Message):
    """
    Configuration messages
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _RoleType:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _RoleTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[Options._RoleType.ValueType], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        ROLE_TYPE_UNKNOWN: Options._RoleType.ValueType  # 0
        ROLE_TYPE_INPUT: Options._RoleType.ValueType  # 1
        ROLE_TYPE_OUTPUT: Options._RoleType.ValueType  # 2

    class RoleType(_RoleType, metaclass=_RoleTypeEnumTypeWrapper): ...
    ROLE_TYPE_UNKNOWN: Options.RoleType.ValueType  # 0
    ROLE_TYPE_INPUT: Options.RoleType.ValueType  # 1
    ROLE_TYPE_OUTPUT: Options.RoleType.ValueType  # 2

    @typing_extensions.final
    class Encoding(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        class _EncodingType:
            ValueType = typing.NewType("ValueType", builtins.int)
            V: typing_extensions.TypeAlias = ValueType

        class _EncodingTypeEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[Options.Encoding._EncodingType.ValueType], builtins.type):
            DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
            ENCODING_TYPE_UNKNOWN: Options.Encoding._EncodingType.ValueType  # 0
            ENCODING_TYPE_ALPHANUMERIC: Options.Encoding._EncodingType.ValueType  # 1
            ENCODING_TYPE_NUMERIC: Options.Encoding._EncodingType.ValueType  # 2
            ENCODING_TYPE_HEXADECIMAL: Options.Encoding._EncodingType.ValueType  # 3
            ENCODING_TYPE_QRCODE: Options.Encoding._EncodingType.ValueType  # 4

        class EncodingType(_EncodingType, metaclass=_EncodingTypeEnumTypeWrapper): ...
        ENCODING_TYPE_UNKNOWN: Options.Encoding.EncodingType.ValueType  # 0
        ENCODING_TYPE_ALPHANUMERIC: Options.Encoding.EncodingType.ValueType  # 1
        ENCODING_TYPE_NUMERIC: Options.Encoding.EncodingType.ValueType  # 2
        ENCODING_TYPE_HEXADECIMAL: Options.Encoding.EncodingType.ValueType  # 3
        ENCODING_TYPE_QRCODE: Options.Encoding.EncodingType.ValueType  # 4

        TYPE_FIELD_NUMBER: builtins.int
        SYMBOL_LENGTH_FIELD_NUMBER: builtins.int
        type: global___Options.Encoding.EncodingType.ValueType
        symbol_length: builtins.int
        def __init__(
            self,
            *,
            type: global___Options.Encoding.EncodingType.ValueType | None = ...,
            symbol_length: builtins.int | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing_extensions.Literal["symbol_length", b"symbol_length", "type", b"type"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing_extensions.Literal["symbol_length", b"symbol_length", "type", b"type"]) -> None: ...

    INPUT_ENCODINGS_FIELD_NUMBER: builtins.int
    OUTPUT_ENCODINGS_FIELD_NUMBER: builtins.int
    PREFERRED_ROLE_FIELD_NUMBER: builtins.int
    @property
    def input_encodings(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Options.Encoding]:
        """List of encodings this endpoint accepts when serving as an input device."""
    @property
    def output_encodings(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___Options.Encoding]:
        """List of encodings this endpoint can generate as an output device."""
    preferred_role: global___Options.RoleType.ValueType
    """Preferred role, if any."""
    def __init__(
        self,
        *,
        input_encodings: collections.abc.Iterable[global___Options.Encoding] | None = ...,
        output_encodings: collections.abc.Iterable[global___Options.Encoding] | None = ...,
        preferred_role: global___Options.RoleType.ValueType | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["preferred_role", b"preferred_role"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["input_encodings", b"input_encodings", "output_encodings", b"output_encodings", "preferred_role", b"preferred_role"]) -> None: ...

global___Options = Options

@typing_extensions.final
class Configuration(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ENCODING_FIELD_NUMBER: builtins.int
    CLIENT_ROLE_FIELD_NUMBER: builtins.int
    @property
    def encoding(self) -> global___Options.Encoding:
        """The encoding to be used in this session."""
    client_role: global___Options.RoleType.ValueType
    """The role of the client (ie, the one initiating pairing). This implies the
    peer (server) acts as the complementary role.
    """
    def __init__(
        self,
        *,
        encoding: global___Options.Encoding | None = ...,
        client_role: global___Options.RoleType.ValueType | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["client_role", b"client_role", "encoding", b"encoding"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["client_role", b"client_role", "encoding", b"encoding"]) -> None: ...

global___Configuration = Configuration

@typing_extensions.final
class ConfigurationAck(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___ConfigurationAck = ConfigurationAck

@typing_extensions.final
class Secret(google.protobuf.message.Message):
    """
    Pairing messages
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SECRET_FIELD_NUMBER: builtins.int
    secret: builtins.bytes
    def __init__(
        self,
        *,
        secret: builtins.bytes | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["secret", b"secret"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["secret", b"secret"]) -> None: ...

global___Secret = Secret

@typing_extensions.final
class SecretAck(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SECRET_FIELD_NUMBER: builtins.int
    secret: builtins.bytes
    def __init__(
        self,
        *,
        secret: builtins.bytes | None = ...,
    ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal["secret", b"secret"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal["secret", b"secret"]) -> None: ...

global___SecretAck = SecretAck

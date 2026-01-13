from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import (
    Any,
    Generic,
    Literal,
    Protocol,
    Required,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
    overload,
    runtime_checkable,
)

from typing_extensions import TypeVar as ExtTypeVar

# Note: Using Union instead of | for recursive type aliases (forward references don't work with | at runtime)
JSONValue: TypeAlias = dict[str, Union[str, int, float, bool, "JSONValue", list["JSONValue"]]]
"""JSON value type - represents any valid JSON value."""

JSONObject: TypeAlias = dict[str, JSONValue]
"""JSON object type - a record of string keys to JSON values."""

JSONArray: TypeAlias = list[JSONValue]
"""JSON array type - an array of JSON values."""

Path = list[int | str] | int | str
"""Path type for accessing nested configuration values."""

PluginConfig = dict[str, Any]
"""Plugin configuration type."""

OnSetCallback = (
    Callable[[Any, Any], None | Any]
    | Callable[[Any, Any], Awaitable[None | Any]]
    | Callable[[Any, Any], Coroutine[Any, Any, None | Any]]
)
"""Callback type for onSet handlers."""

OnGetCallback = (
    Callable[[], None | Any]
    | Callable[[], Awaitable[None | Any]]
    | Callable[[], Coroutine[Any, Any, None | Any]]
)
"""Callback type for onGet handlers."""

JsonSchemaType = Literal["string", "number", "boolean", "array", "button", "submit"]
"""Available schema field types for configuration UI."""

StringFormat = Literal[
    "date-time", "date", "time", "email", "uuid", "ipv4", "ipv6", "password", "qrCode", "image"
]
"""String format types for validation/display."""

ButtonColor = Literal["success", "info", "warn", "danger"]
"""Button color variants."""

T = TypeVar(
    "T",
    str,
    int,
    float,
    bool,
    list[str],
    list[int],
    list[float],
    list[bool],
    str | list[str],
)
"""Generic type variable for schema default values."""

V1 = ExtTypeVar("V1", default=str)
"""TypeVar for generic getValue return type."""

V2 = ExtTypeVar("V2", default=dict[str, Any])
"""TypeVar for generic storage values type."""


class JsonFactorySchema(TypedDict):
    """
    Base schema interface for all schema types.
    Contains common fields like type, key, title, description.
    """

    type: JsonSchemaType
    """Field type."""

    key: str
    """Unique field identifier."""

    title: str
    """Display title."""

    description: str
    """Field description/help text."""


class JsonBaseSchemaWithoutCallbacks(JsonFactorySchema, Generic[T], total=False):
    """
    Base schema without callbacks - used for nested schemas.
    Extends factory schema with common display options.
    """

    group: str
    """Optional group name for organizing fields."""

    hidden: bool
    """Hide field from UI."""

    required: bool
    """Mark field as required."""

    readonly: bool
    """Make field read-only."""

    placeholder: str
    """Placeholder text for empty fields."""

    defaultValue: T
    """Default value when not set."""


class JsonBaseSchema(JsonBaseSchemaWithoutCallbacks[T], Generic[T], total=False):
    """
    Base schema with callbacks - full schema interface.
    Adds storage and callback options for dynamic behavior.
    """

    store: bool
    """Whether to persist this field to storage."""

    onSet: OnSetCallback
    """Callback when value changes."""

    onGet: OnGetCallback
    """Callback to get computed value."""


class JsonStringSchema(TypedDict, total=False):
    """String-specific schema options."""

    type: Literal["string"]

    format: StringFormat
    """String format for validation/display."""

    minLength: int
    """Minimum string length."""

    maxLength: int
    """Maximum string length."""


class JsonNumberSchema(TypedDict, total=False):
    """Number-specific schema options."""

    type: Literal["number"]

    minimum: int | float
    """Minimum value."""

    maximum: int | float
    """Maximum value."""

    step: int | float
    """Step increment for number input."""


class JsonBooleanSchema(TypedDict):
    """Boolean-specific schema options."""

    type: Literal["boolean"]


class JsonEnumSchema(TypedDict, total=False):
    """Enum/select schema options."""

    type: Literal["string"]

    enum: list[str]
    """Available options."""

    multiple: bool
    """Allow multiple selection."""


class JsonArraySchema(TypedDict, total=False):
    """Array schema options."""

    type: Literal["array"]

    opened: bool
    """Whether array items are expanded by default."""

    items: JsonSchemaWithoutCallbacks
    """Schema for array items."""


class JsonSchemaString(JsonBaseSchema[str], total=False):
    """Complete string schema with callbacks."""

    type: Required[Literal["string"]]  # type: ignore[misc]

    format: StringFormat
    """String format for validation/display."""

    minLength: int
    """Minimum string length."""

    maxLength: int
    """Maximum string length."""


class JsonSchemaStringWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[str], total=False):
    """String schema without callbacks (for nested use)."""

    type: Required[Literal["string"]]  # type: ignore[misc]

    format: StringFormat

    minLength: int

    maxLength: int


class JsonSchemaNumber(JsonBaseSchema[int | float], total=False):
    """Complete number schema with callbacks."""

    type: Required[Literal["number"]]  # type: ignore[misc]

    minimum: int | float

    maximum: int | float

    step: int | float


class JsonSchemaNumberWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[int | float], total=False):
    """Number schema without callbacks (for nested use)."""

    type: Required[Literal["number"]]  # type: ignore[misc]

    minimum: int | float

    maximum: int | float

    step: int | float


class JsonSchemaBoolean(JsonBaseSchema[bool], total=False):
    """Complete boolean schema with callbacks."""

    type: Required[Literal["boolean"]]  # type: ignore[misc]


class JsonSchemaBooleanWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[bool], total=False):
    """Boolean schema without callbacks (for nested use)."""

    type: Required[Literal["boolean"]]  # type: ignore[misc]


class JsonSchemaEnum(JsonBaseSchema[str | list[str]], total=False):
    """Complete enum schema with callbacks."""

    type: Required[Literal["string"]]  # type: ignore[misc]

    enum: Required[list[str]]

    multiple: bool


class JsonSchemaEnumWithoutCallbacks(JsonBaseSchemaWithoutCallbacks[str | list[str]], total=False):
    """Enum schema without callbacks (for nested use)."""

    type: Required[Literal["string"]]  # type: ignore[misc]

    enum: Required[list[str]]

    multiple: bool


class JsonSchemaArray(JsonBaseSchema[list[str] | list[int] | list[float] | list[bool]], total=False):  # pyright: ignore[reportInvalidTypeArguments]
    """Complete array schema with callbacks."""

    type: Required[Literal["array"]]  # type: ignore[misc]

    opened: bool

    items: JsonSchemaWithoutCallbacks


class JsonSchemaArrayWithoutCallbacks(
    JsonBaseSchemaWithoutCallbacks[list[str] | list[int] | list[float] | list[bool]],  # pyright: ignore[reportInvalidTypeArguments]
    total=False,
):
    """Array schema without callbacks (for nested use)."""

    type: Required[Literal["array"]]  # type: ignore[misc]

    opened: bool

    items: JsonSchemaWithoutCallbacks


class JsonSchemaButton(TypedDict, total=False):
    """Button schema - triggers an action without storing a value."""

    type: Required[Literal["button"]]

    key: Required[str]

    title: Required[str]

    description: Required[str]

    onSet: Callable[[], Awaitable[None]] | Callable[[], None]
    """Click handler."""

    group: str

    color: ButtonColor
    """Button color variant."""


class JsonSchemaSubmit(TypedDict, total=False):
    """Submit button schema - submits form data and can return updated schema."""

    type: Required[Literal["submit"]]

    key: Required[str]

    title: Required[str]

    description: Required[str]

    onClick: Required[Callable[[Any], Awaitable[FormSubmitResponse | None]]]
    """Submit handler - receives form values, can return toast/schema updates."""

    group: str

    color: ButtonColor


JsonSchema = (
    JsonSchemaString
    | JsonSchemaNumber
    | JsonSchemaBoolean
    | JsonSchemaEnum
    | JsonSchemaArray
    | JsonSchemaButton
    | JsonSchemaSubmit
)
"""Union type of all schema types with callbacks. Use this for top-level schema definitions."""

JsonSchemaWithoutKey = (
    JsonSchemaStringWithoutCallbacks
    | JsonSchemaNumberWithoutCallbacks
    | JsonSchemaBooleanWithoutCallbacks
    | JsonSchemaEnumWithoutCallbacks
)
"""Schema type without key field."""

JsonSchemaWithoutCallbacks = (
    JsonSchemaStringWithoutCallbacks
    | JsonSchemaNumberWithoutCallbacks
    | JsonSchemaBooleanWithoutCallbacks
    | JsonSchemaEnumWithoutCallbacks
    | JsonSchemaArrayWithoutCallbacks
)
"""Union type of schemas without callbacks. Use this for nested schemas (e.g., array items)."""


class ToastMessage(TypedDict):
    """Toast notification message."""

    type: Literal["info", "success", "warning", "error"]
    """Notification type."""

    message: str
    """Message text."""


class FormSubmitSchema(TypedDict):
    """Form submit input data."""

    config: dict[str, Any]
    """Form configuration values."""


class FormSubmitResponse(TypedDict, total=False):
    """Form submit response - returned by submit handlers."""

    toast: ToastMessage
    """Optional toast notification to show."""

    schema: list[JsonSchemaWithoutCallbacks]
    """Optional schema updates to apply."""


class SchemaConfig(TypedDict):
    """
    Schema configuration bundle.
    Contains both schema definitions and current values.
    """

    schema: list[JsonSchema]
    """Schema definitions."""

    config: dict[str, Any]
    """Current configuration values."""


@runtime_checkable
class DeviceStorage(Protocol, Generic[V2]):
    """
    Device storage interface for plugin/camera configuration.

    Provides methods to read/write configuration values and manage schemas.
    Each plugin and camera can have its own storage instance.

    Example:
        ```python
        # Get a value with default
        threshold = await storage.getValue("motionThreshold", 50)

        # Set a value
        await storage.setValue("motionThreshold", 75)

        # Add a new schema field
        await storage.addSchema(
            {
                "type": "number",
                "key": "sensitivity",
                "title": "Sensitivity",
                "description": "Detection sensitivity (0-100)",
                "minimum": 0,
                "maximum": 100,
                "defaultValue": 50,
            }
        )
        ```
    """

    schemas: list[JsonSchema]
    """Current schema definitions."""

    values: V2
    """Current configuration values."""

    @overload
    async def getValue(self, key: str) -> V1 | None: ...
    @overload
    async def getValue(self, key: str, default_value: V1) -> V1: ...
    async def getValue(self, key: str, default_value: V1 | None = None) -> V1 | None:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default_value: Default value if key doesn't exist

        Returns:
            The configuration value or default
        """
        ...

    async def setValue(self, key: str, new_value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            new_value: New value to set
        """
        ...

    async def submitValue(self, key: str, new_value: Any) -> FormSubmitResponse | None:
        """
        Submit a value (for submit-type schemas).

        Args:
            key: Schema key
            new_value: Submitted value

        Returns:
            Optional response with toast/schema updates
        """
        ...

    def hasValue(self, key: str) -> bool:
        """
        Check if a configuration value exists.

        Args:
            key: Configuration key
        """
        ...

    async def getConfig(self) -> SchemaConfig:
        """
        Get the full schema configuration.

        Returns:
            Schema definitions and current values
        """
        ...

    async def setConfig(self, new_config: V2) -> None:
        """
        Set the full configuration.

        Args:
            new_config: New configuration values
        """
        ...

    async def addSchema(self, schema: JsonSchema) -> None:
        """
        Add a new schema field.

        Args:
            schema: Schema definition to add
        """
        ...

    def removeSchema(self, key: str) -> None:
        """
        Remove a schema field.

        Args:
            key: Schema key to remove
        """
        ...

    async def changeSchema(self, key: str, new_schema: dict[str, Any]) -> None:
        """
        Update an existing schema field.

        Args:
            key: Schema key to update
            new_schema: Partial schema with updated fields
        """
        ...

    def getSchema(self, key: str) -> JsonSchema | None:
        """
        Get a schema definition by key.

        Args:
            key: Schema key

        Returns:
            Schema or None
        """
        ...

    def hasSchema(self, key: str) -> bool:
        """
        Check if a schema exists.

        Args:
            key: Schema key
        """
        ...

    def save(self) -> None:
        """Persist all changes to storage."""
        ...


@runtime_checkable
class StorageController(Protocol):
    """
    Storage controller interface for creating storage instances.

    Accessed via `api.storageController` in plugins.

    Example:
        ```python
        # Create camera-specific storage
        camera_storage = api.storageController.createCameraStorage(
            self,
            camera.id,
            [{"type": "number", "key": "threshold", "title": "Threshold", "description": "..."}],
        )

        # Create plugin-level storage
        plugin_storage = api.storageController.createPluginStorage(self, schemas)
        ```
    """

    def createCameraStorage(
        self, instance: Any, cameraId: str, schemas: list[JsonSchema] | None = None
    ) -> DeviceStorage[Any]:
        """
        Create storage for a specific camera.

        Args:
            instance: Plugin instance (usually `self`)
            cameraId: Camera ID
            schemas: Optional initial schemas

        Returns:
            Device storage instance
        """
        ...

    def createPluginStorage(
        self, instance: Any, schemas: list[JsonSchema] | None = None
    ) -> DeviceStorage[Any]:
        """
        Create plugin-level storage.

        Args:
            instance: Plugin instance (usually `self`)
            schemas: Optional initial schemas

        Returns:
            Device storage instance
        """
        ...

    def getCameraStorage(self, camera_id: str) -> DeviceStorage[Any] | None:
        """
        Get existing camera storage.

        Args:
            camera_id: Camera ID

        Returns:
            Storage instance or None
        """
        ...

    def getPluginStorage(self) -> DeviceStorage[Any] | None:
        """
        Get existing plugin storage.

        Returns:
            Storage instance or None
        """
        ...


__all__ = [
    # JSON types
    "JSONValue",
    "JSONObject",
    "JSONArray",
    "Path",
    "PluginConfig",
    # Callback types
    "OnSetCallback",
    "OnGetCallback",
    # Schema type literals
    "JsonSchemaType",
    "StringFormat",
    "ButtonColor",
    # Type variables
    "V1",
    "V2",
    # Base schemas
    "JsonFactorySchema",
    "JsonBaseSchemaWithoutCallbacks",
    "JsonBaseSchema",
    # Type-specific schemas
    "JsonStringSchema",
    "JsonNumberSchema",
    "JsonBooleanSchema",
    "JsonEnumSchema",
    "JsonArraySchema",
    # Combined schema types (with callbacks)
    "JsonSchemaString",
    "JsonSchemaNumber",
    "JsonSchemaBoolean",
    "JsonSchemaEnum",
    "JsonSchemaArray",
    "JsonSchemaButton",
    "JsonSchemaSubmit",
    # Combined schema types (without callbacks)
    "JsonSchemaStringWithoutCallbacks",
    "JsonSchemaNumberWithoutCallbacks",
    "JsonSchemaBooleanWithoutCallbacks",
    "JsonSchemaEnumWithoutCallbacks",
    "JsonSchemaArrayWithoutCallbacks",
    # Union types
    "JsonSchema",
    "JsonSchemaWithoutKey",
    "JsonSchemaWithoutCallbacks",
    # Response types
    "ToastMessage",
    "FormSubmitSchema",
    "FormSubmitResponse",
    "SchemaConfig",
    # Storage interfaces
    "DeviceStorage",
    "StorageController",
]

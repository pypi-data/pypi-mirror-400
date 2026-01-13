from __future__ import annotations

import asyncio
import contextlib
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    NotRequired,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeVar,
    runtime_checkable,
)
from uuid import uuid4

from ..utils import is_equal

if TYPE_CHECKING:
    from ..storage import DeviceStorage, JsonSchema
    from .audio import AudioProperty
    from .battery import BatteryCapability, BatteryProperty
    from .classifier import ClassifierProperty
    from .contact import ContactProperty
    from .doorbell import DoorbellProperty
    from .face import FaceProperty
    from .license_plate import LicensePlateProperty
    from .light import LightCapability, LightProperty
    from .motion import MotionProperty
    from .object import ObjectProperty
    from .ptz import PTZCapability, PTZProperty
    from .security_system import SecuritySystemProperty
    from .siren import SirenCapability, SirenProperty
    from .spec import ModelSpec
    from .switch import SwitchProperty

SensorPropertyType: TypeAlias = (
    AudioProperty
    | BatteryProperty
    | ClassifierProperty
    | ContactProperty
    | DoorbellProperty
    | FaceProperty
    | LicensePlateProperty
    | LightProperty
    | MotionProperty
    | ObjectProperty
    | PTZProperty
    | SecuritySystemProperty
    | SirenProperty
    | SwitchProperty
)

SensorCapability: TypeAlias = PTZCapability | LightCapability | SirenCapability | BatteryCapability


class SensorType(str, Enum):
    Motion = "motion"
    Object = "object"
    Audio = "audio"
    Face = "face"
    LicensePlate = "licensePlate"
    Classifier = "classifier"
    Contact = "contact"
    Light = "light"
    Siren = "siren"
    Switch = "switch"
    PTZ = "ptz"
    SecuritySystem = "securitySystem"
    Doorbell = "doorbell"
    Battery = "battery"


class SensorCategory(str, Enum):
    Sensor = "sensor"
    Control = "control"
    Trigger = "trigger"
    Info = "info"


class PropertyChangedEvent(TypedDict):
    cameraId: str
    sensorId: str
    sensorType: SensorType
    property: SensorPropertyType
    value: object
    previousValue: NotRequired[object]
    timestamp: int


PropertyUpdateFn = Callable[[str, Any], None]
PropertyChangeListener = Callable[[PropertyChangedEvent], None]
CapabilityUpdateFn = Callable[[list[str]], None]


@runtime_checkable
class SensorLike(Protocol):
    @property
    def id(self) -> str: ...
    @property
    def type(self) -> SensorType: ...
    @property
    def name(self) -> str: ...
    @property
    def pluginId(self) -> str | None: ...
    @property
    def capabilities(self) -> list[str]: ...

    @property
    def displayName(self) -> str: ...
    @displayName.setter
    def displayName(self, value: str) -> None: ...

    def getPropertyValue(self, property: str) -> Any | None: ...
    def getAllPropertyValues(self) -> dict[str, Any]: ...
    async def setPropertyValue(self, property: str, value: Any) -> None: ...
    def onPropertyChanged(self, callback: Callable[[str, Any], None]) -> Callable[[], None]: ...
    def onCapabilitiesChanged(self, callback: Callable[[list[str]], None]) -> Callable[[], None]: ...
    def hasCapability(self, capability: str) -> bool: ...


class SensorJSON(TypedDict):
    id: str
    type: SensorType
    name: str
    displayName: str
    category: SensorCategory
    cameraId: str
    pluginId: NotRequired[str]
    properties: dict[str, Any]
    capabilities: NotRequired[list[str]]
    requiresFrames: NotRequired[bool]
    modelSpec: NotRequired[ModelSpec]


TProperties = TypeVar("TProperties", bound=Mapping[str, Any])
TStorage = TypeVar("TStorage", bound=dict[str, Any])
TCapability = TypeVar("TCapability", bound=str)


class PropertiesProxy(Generic[TProperties]):
    _store: dict[str, Any]
    _on_change: Callable[[str, Any, Any], None]

    def __init__(
        self,
        store: dict[str, Any],
        on_change: Callable[[str, Any, Any], None],
    ) -> None:
        object.__setattr__(self, "_store", store)
        object.__setattr__(self, "_on_change", on_change)

    def __getattr__(self, key: str) -> Any:
        store: dict[str, Any] = object.__getattribute__(self, "_store")
        if key.startswith("_"):
            return object.__getattribute__(self, key)
        return store.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            object.__setattr__(self, key, value)
            return

        store: dict[str, Any] = object.__getattribute__(self, "_store")
        on_change: Callable[[str, Any, Any], None] = object.__getattribute__(self, "_on_change")

        old_value = store.get(key)
        if not is_equal(old_value, value, True):
            store[key] = value
            on_change(key, value, old_value)

    def __getitem__(self, key: str) -> Any:
        store: dict[str, Any] = object.__getattribute__(self, "_store")
        return store.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__setattr__(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        store: dict[str, Any] = object.__getattribute__(self, "_store")
        return store.get(key, default)


class Sensor(ABC, Generic[TProperties, TStorage, TCapability]):
    _requires_frames: bool = False

    def __init__(self, name: str) -> None:
        self._camera_id: str | None = None
        self._name = name
        self._id = str(uuid4())
        self._display_name = name
        self._plugin_id: str | None = None
        self._capabilities: list[TCapability] = []
        self._property_listeners: list[Callable[[str, Any], None]] = []
        self._detailed_listeners: set[PropertyChangeListener] = set()
        self._capabilities_listeners: list[Callable[[list[str]], None]] = []
        self._assignment_listeners: list[Callable[[bool], None]] = []
        self._update_fn: Callable[[str, Any], None] | None = None
        self._capabilities_change_fn: Callable[[list[str]], None] | None = None
        self._restart_fn: Callable[[], Any] | None = None
        self._storage: DeviceStorage | None = None
        self._is_assigned: bool = False
        self._properties_store: dict[str, Any] = {}
        self._properties_proxy: PropertiesProxy[TProperties] = PropertiesProxy(
            self._properties_store,
            self._on_property_change,
        )

    @property
    @abstractmethod
    def type(self) -> SensorType: ...

    @property
    @abstractmethod
    def category(self) -> SensorCategory: ...

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def displayName(self) -> str:
        return self._display_name

    @displayName.setter
    def displayName(self, value: str) -> None:
        self._display_name = value

    @property
    def pluginId(self) -> str | None:
        return self._plugin_id

    @property
    def cameraId(self) -> str | None:
        return self._camera_id

    @property
    def capabilities(self) -> list[TCapability]:
        return self._capabilities.copy()

    @capabilities.setter
    def capabilities(self, value: list[TCapability]) -> None:
        self._capabilities = list(dict.fromkeys(value))
        caps_list: list[str] = [str(c) for c in self._capabilities]
        if self._capabilities_change_fn:
            self._capabilities_change_fn(caps_list)
        for listener in self._capabilities_listeners:
            with contextlib.suppress(Exception):
                listener(caps_list)

    @property
    def requiresFrames(self) -> bool:
        return self._requires_frames

    @property
    def schema(self) -> list[JsonSchema]:
        return []

    @property
    def storage(self) -> DeviceStorage | None:
        return self._storage

    @property
    def isAssigned(self) -> bool:
        return self._is_assigned

    @property
    def props(self) -> PropertiesProxy[TProperties]:
        return self._properties_proxy

    @property
    def rawProps(self) -> dict[str, Any]:
        return self._properties_store

    def _notify_metadata_update(self, property: str, value: Any) -> None:
        if self._update_fn:
            self._update_fn(property, value)

    def _on_property_change(self, key: str, value: Any, old_value: Any) -> None:
        if self._update_fn:
            self._update_fn(key, value)
        self._notifyListeners(key, value, old_value)

    def _setStorage(self, storage: DeviceStorage) -> None:
        self._storage = storage

    def _setAssigned(self, assigned: bool) -> None:
        if self._is_assigned != assigned:
            self._is_assigned = assigned
            for listener in self._assignment_listeners:
                listener(assigned)

    def onAssignmentChanged(self, callback: Callable[[bool], None]) -> Callable[[], None]:
        self._assignment_listeners.append(callback)
        return lambda: self._assignment_listeners.remove(callback)

    def toJSON(self) -> SensorJSON:
        result: SensorJSON = {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "displayName": self.displayName or self.name,
            "category": self.category,
            "cameraId": self._camera_id or "",
            "properties": self._getProperties(),
            "capabilities": [str(c) for c in self.capabilities],
            "requiresFrames": self._requires_frames,
        }
        if self._plugin_id:
            result["pluginId"] = self._plugin_id
        return result

    def _setPropertyInternal(self, key: str, value: Any) -> None:
        old_value = self._properties_store.get(key)
        if old_value != value:
            self._properties_store[key] = value
            self._notifyListeners(key, value, old_value)

    def _onBackendPropertyChanged(self, property: str, value: Any) -> None:
        self._setPropertyInternal(property, value)

    def getPropertyValue(self, property: str) -> Any | None:
        return self._properties_store.get(property)

    def getAllPropertyValues(self) -> dict[str, Any]:
        return self._properties_store.copy()

    async def setPropertyValue(self, property: str, value: Any) -> None:
        method_name = f"set{property[0].upper()}{property[1:]}"
        method = getattr(self, method_name, None)

        if callable(method):
            result = method(value)
            if asyncio.iscoroutine(result):
                await result
        else:
            if self._properties_store.get(property) != value:
                setattr(self._properties_proxy, property, value)

    def hasCapability(self, capability: TCapability | str) -> bool:
        return capability in self._capabilities

    def onPropertyChanged(self, callback: Callable[[str, Any], None]) -> Callable[[], None]:
        self._property_listeners.append(callback)
        return lambda: self._property_listeners.remove(callback)

    def onPropertyChangedDetailed(self, callback: PropertyChangeListener) -> Callable[[], None]:
        self._detailed_listeners.add(callback)
        return lambda: self._detailed_listeners.discard(callback)

    def _notifyListeners(self, property: str, value: Any, previousValue: Any) -> None:
        if not self._camera_id:
            return

        if self._detailed_listeners:
            event: PropertyChangedEvent = {
                "cameraId": self._camera_id,
                "sensorId": self._id,
                "sensorType": self.type,
                "property": property,  # type: ignore[typeddict-item]
                "value": value,
                "previousValue": previousValue,
                "timestamp": int(time.time() * 1000),
            }
            for detailed_listener in self._detailed_listeners:
                with contextlib.suppress(Exception):
                    detailed_listener(event)
        for simple_listener in self._property_listeners:
            with contextlib.suppress(Exception):
                simple_listener(property, value)

    def onCapabilitiesChanged(self, callback: Callable[[list[str]], None]) -> Callable[[], None]:
        self._capabilities_listeners.append(callback)
        return lambda: self._capabilities_listeners.remove(callback)

    def _setCameraId(self, camera_id: str) -> None:
        self._camera_id = camera_id

    def _setPluginId(self, plugin_id: str) -> None:
        self._plugin_id = plugin_id

    def _init(self, update_fn: PropertyUpdateFn) -> None:
        self._update_fn = update_fn

    def _initCapabilities(self, update_fn: CapabilityUpdateFn) -> None:
        self._capabilities_change_fn = update_fn

    def _initRestartFn(self, restart_fn: Callable[[], Any]) -> None:
        self._restart_fn = restart_fn

    async def requestRestart(self) -> None:
        if self._restart_fn:
            result = self._restart_fn()
            if asyncio.iscoroutine(result):
                await result

    def _cleanup(self) -> None:
        self._update_fn = None
        self._capabilities_change_fn = None
        self._restart_fn = None
        self._storage = None
        self._is_assigned = False
        self._assignment_listeners.clear()
        self._detailed_listeners.clear()
        self._property_listeners.clear()
        self._capabilities_listeners.clear()

    def _getProperties(self) -> dict[str, Any]:
        return self._properties_store.copy()

from __future__ import annotations

from typing import Any, cast

from ..sensor import (
    SensorType,
)
from .contract import PluginContract, PluginInterface, PluginRole


def get_contract_validation_errors(contract: object) -> list[str]:
    """
    Validate a plugin contract and return validation errors.

    Args:
        contract: Contract object to validate

    Returns:
        Array of error messages (empty if valid)

    Example:
        ```python
        errors = get_contract_validation_errors(my_contract)
        if errors:
            print(f"Invalid contract: {errors}")
        ```
    """
    errors: list[str] = []

    if not contract or not isinstance(contract, dict):
        errors.append(
            f"Contract must be an object. Got: {'null' if contract is None else type(contract).__name__}"
        )
        return errors

    c = cast(Any, contract)
    valid_roles = [r.value for r in PluginRole]
    valid_sensor_types = [s.value for s in SensorType]

    # Check role
    if "role" not in c:
        errors.append('Missing required field: "role"')
    elif not isinstance(c.get("role"), str):
        role_value = c.get("role")
        errors.append(f'Field "role" must be a string. Got: {type(role_value).__name__}')
    elif c["role"] not in valid_roles:
        errors.append(f'Invalid role "{c["role"]}". Valid roles: {", ".join(valid_roles)}')

    # Check name
    if "name" not in c:
        errors.append('Missing required field: "name"')
    elif not isinstance(c["name"], str):
        errors.append(f'Field "name" must be a string. Got: {type(c["name"]).__name__}')
    elif len(c["name"]) == 0:
        errors.append('Field "name" cannot be empty')

    # Check provides
    if "provides" not in c:
        errors.append('Missing required field: "provides"')
    elif not isinstance(c["provides"], list):
        errors.append(f'Field "provides" must be an array. Got: {type(c["provides"]).__name__}')
    else:
        for sensor_type in c["provides"]:
            if sensor_type not in valid_sensor_types:
                errors.append(
                    f'Invalid sensor type in "provides": "{sensor_type}". Valid types: {", ".join(valid_sensor_types)}'
                )

    # Check consumes
    if "consumes" not in c:
        errors.append('Missing required field: "consumes"')
    elif not isinstance(c["consumes"], list):
        errors.append(f'Field "consumes" must be an array. Got: {type(c["consumes"]).__name__}')
    else:
        for sensor_type in c["consumes"]:
            if sensor_type not in valid_sensor_types:
                errors.append(
                    f'Invalid sensor type in "consumes": "{sensor_type}". Valid types: {", ".join(valid_sensor_types)}'
                )

    # Check interfaces
    valid_interfaces = [i.value for i in PluginInterface]
    if "interfaces" not in c:
        errors.append('Missing required field: "interfaces"')
    elif not isinstance(c["interfaces"], list):
        errors.append(f'Field "interfaces" must be an array. Got: {type(c["interfaces"]).__name__}')
    else:
        for iface in c["interfaces"]:
            if iface not in valid_interfaces:
                errors.append(
                    f'Invalid interface in "interfaces": "{iface}". Valid interfaces: {", ".join(valid_interfaces)}'
                )

    # Check optional pythonVersion
    if "pythonVersion" in c and c["pythonVersion"] not in ["3.11", "3.12"]:
        errors.append(f'Invalid pythonVersion "{c["pythonVersion"]}". Valid versions: 3.11, 3.12')

    # Check optional dependencies
    if "dependencies" in c and not isinstance(c["dependencies"], list):
        errors.append(f'Field "dependencies" must be an array. Got: {type(c["dependencies"]).__name__}')

    return errors


def validate_contract(contract: object) -> bool:
    """
    Check if a contract is valid.

    Args:
        contract: Contract to validate

    Returns:
        True if valid
    """
    return len(get_contract_validation_errors(contract)) == 0


def validate_contract_consistency(contract: PluginContract, plugin_name: str | None = None) -> None:
    """
    Validate contract consistency rules.

    Throws an error if the contract violates role-specific rules.

    Args:
        contract: Plugin contract
        plugin_name: Optional plugin name for error messages

    Raises:
        ValueError: If contract is inconsistent
    """
    prefix = f'Plugin "{plugin_name}": ' if plugin_name else ""

    match contract["role"]:
        case PluginRole.Hub:
            if len(contract["provides"]) > 0:
                raise ValueError(f"{prefix}Hub plugins cannot provide sensors.")
            if len(contract["consumes"]) == 0:
                raise ValueError(f"{prefix}Hub plugins must consume at least one sensor type.")

        case PluginRole.SensorProvider:
            if len(contract["provides"]) == 0:
                raise ValueError(f"{prefix}SensorProvider plugins must provide at least one sensor type.")

        case PluginRole.CameraAndSensorProvider:
            if len(contract["provides"]) == 0:
                raise ValueError(
                    f"{prefix}CameraAndSensorProvider plugins must provide at least one sensor type."
                )

        case PluginRole.CameraController:
            # CameraController can have empty or filled provides array
            pass


def is_provider(contract: PluginContract) -> bool:
    """
    Check if plugin provides sensors.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin provides at least one sensor type
    """
    return len(contract["provides"]) > 0


def is_consumer(contract: PluginContract) -> bool:
    """
    Check if plugin consumes sensors.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin consumes at least one sensor type
    """
    return len(contract["consumes"]) > 0


def is_hub(contract: PluginContract) -> bool:
    """
    Check if plugin is a hub.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin role is Hub
    """
    return contract["role"] == PluginRole.Hub


def provides_sensor(contract: PluginContract, sensor_type: SensorType) -> bool:
    """
    Check if plugin provides a specific sensor type.

    Args:
        contract: Plugin contract
        sensor_type: Sensor type to check

    Returns:
        True if plugin provides the sensor type
    """
    return sensor_type in contract["provides"]


def consumes_sensor(contract: PluginContract, sensor_type: SensorType) -> bool:
    """
    Check if plugin consumes a specific sensor type.

    Args:
        contract: Plugin contract
        sensor_type: Sensor type to check

    Returns:
        True if plugin consumes the sensor type
    """
    return sensor_type in contract["consumes"]


def can_provide_sensors_to_any_cameras(contract: PluginContract) -> bool:
    """
    Check if plugin can provide sensors to any camera (not just its own).

    Args:
        contract: Plugin contract

    Returns:
        True if role is SensorProvider or CameraAndSensorProvider
    """
    return contract["role"] in (PluginRole.SensorProvider, PluginRole.CameraAndSensorProvider)


def is_camera_controller(contract: PluginContract) -> bool:
    """
    Check if plugin is a camera controller.

    Args:
        contract: Plugin contract

    Returns:
        True if plugin can create cameras
    """
    return can_create_cameras(contract)


def is_qualified_contract(contract: PluginContract) -> bool:
    """
    Check if contract has a valid role.

    Args:
        contract: Plugin contract

    Returns:
        True if role is a valid PluginRole
    """
    return contract["role"] in PluginRole


def can_create_cameras(contract: PluginContract) -> bool:
    """
    Check if plugin can create cameras.

    Args:
        contract: Plugin contract

    Returns:
        True if role is CameraController or CameraAndSensorProvider
    """
    return contract["role"] in (PluginRole.CameraController, PluginRole.CameraAndSensorProvider)


def has_interface(contract: PluginContract, iface: PluginInterface) -> bool:
    """
    Check if plugin implements a specific interface.

    Args:
        contract: Plugin contract
        iface: Plugin interface to check

    Returns:
        True if plugin implements the interface
    """
    return iface in contract["interfaces"]

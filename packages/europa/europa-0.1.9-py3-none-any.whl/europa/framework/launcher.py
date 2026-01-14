import importlib
import importlib.util
from pathlib import Path
import argparse
import sys
import traceback
from typing import Optional, Type, Any

from europa.framework.service import _BaseService

# Custom exceptions for better error handling
class ServiceError(Exception):
    """Base class for service-related errors."""

class ServiceNotFoundError(ServiceError):
    """Raised when a service class is not found."""

class DirectoryScanError(ServiceError):
    """Raised when scanning a directory fails."""

# Centralized error messages
ERROR_MESSAGES = {
    "module_not_found": (
        "❌ Module '{module}' not found.\n"
        "Check:\n"
        "1. Module path spelling\n"
        "2. Package installation\n"
        "Original error: {error}"
    ),
    "service_not_found": (
        "🔴 Service '{service}' not found in {context} '{location}'.\n"
        "Available services: {available}\n"
        "Verify:\n"
        "1. Class exists in {context}\n"
        "2. Inherits from _BaseService\n"
        "3. Imported correctly"
    ),
    "directory_not_found": "Directory '{directory}' does not exist",
    "directory_scan_failed": (
        "❌ Directory search failed: {error}\n"
        "Check:\n"
        "1. Directory contains service files\n"
        "2. Service class naming\n"
        "3. Class inheritance"
    ),
    "invalid_arguments": "❌ Must specify either --module OR --directory, not both/none",
}

def launch_service(
    service_name: str,
    port: int,
    services_module: Optional[str] = None,
    services_dir: Optional[str] = None
) -> None:
    """
    Launches a service using EITHER module-based or directory-based discovery.
    
    Args:
        service_name: Name of the service class to launch.
        port: Port number to run the service on.
        services_module: Python module path containing service classes.
        services_dir: Directory containing service files.
    
    Raises:
        ValueError: If both or neither of `services_module` and `services_dir` are provided.
    """
    if not (bool(services_module) ^ bool(services_dir)):
        raise ValueError(ERROR_MESSAGES["invalid_arguments"])

    service_class = (
        _find_service_in_module(service_name, services_module)
        if services_module
        else _find_service_in_directory(service_name, services_dir)
    )
    
    _execute_launch(service_class, port)

def _find_service_in_module(service_name: str, module_path: str) -> Type[_BaseService]:
    """Find and return the service class from the specified module."""
    try:
        print(f"🔍 Scanning module: {module_path}")
        module = importlib.import_module(module_path)
        
        valid_services = [
            attr for attr in dir(module)
            if _is_valid_service(getattr(module, attr))
        ]
        
        if service_name in valid_services:
            print(f"✅ Found {service_name} in module")
            return getattr(module, service_name)

        raise ServiceNotFoundError(
            ERROR_MESSAGES["service_not_found"].format(
                service=service_name,
                context="module",
                location=module_path,
                available=", ".join(valid_services) or "None"
            )
        )

    except ModuleNotFoundError as e:
        raise ServiceError(
            ERROR_MESSAGES["module_not_found"].format(module=module_path, error=e)
        ) from e

def _find_service_in_directory(service_name: str, directory: str) -> Type[_BaseService]:
    """Find and return the service class from the specified directory."""

    print(f"🔍 Scanning directory: {directory}")

    directory_path = Path(directory)
    
    if not directory_path.is_dir():
        raise DirectoryScanError(ERROR_MESSAGES["directory_not_found"].format(directory=directory))

    
    
    for file_path in directory_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        try:
            module = _load_module_from_file(file_path)
            if hasattr(module, service_name):
                cls = getattr(module, service_name)
                if _is_valid_service(cls):
                    print(f"✅ Found {service_name} in directory")
                    return cls
        except ImportError as e:
            print(f"⚠️ Import error in {file_path.name}: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error in {file_path.name}: {e}")

    raise ServiceNotFoundError(
        ERROR_MESSAGES["service_not_found"].format(
            service=service_name,
            context="directory",
            location=directory,
            available="None"
        )
    )

def _load_module_from_file(file_path: Path):
    """Load a Python module from a file path."""
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(f"{file_path.parent.name}.{module_name}", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _execute_launch(cls: Type[_BaseService], port: int) -> None:
    """Common launch execution."""
    print("=" * 56)
    print(f"🚀 Launching {cls.__name__} on port {port}")
    print("=" * 56)
    cls().launch(port)

def _is_valid_service(attr: Any) -> bool:
    """Checks if an attribute is a valid service class."""
    return isinstance(attr, type) and issubclass(attr, _BaseService) and attr is not _BaseService

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Launch Europa framework microservices",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--module", type=str, help="Python module path containing service classes")
    group.add_argument("-d", "--directory", type=str, help="Directory to search for service classes")
    
    parser.add_argument("-s", "--service", type=str, required=True, help="Name of the service class to launch (case-sensitive)")
    parser.add_argument("-p", "--port", type=int, default=5173, help="Port number to use (default 5173)")

    try:
        args = parser.parse_args()
        print("=" * 56)
        launch_service(
            service_name=args.service,
            port=args.port,
            services_module=args.module,
            services_dir=args.directory
        )
    except ServiceError as e:
        print(f"\n💥 Launch failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()

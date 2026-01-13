"""
Device utilities for PEARL - supports CUDA, MPS, and CPU.
"""
import torch
from typing import Union


def get_device(device: Union[str, torch.device, None] = None) -> torch.device:
    """
    Get the best available device, with intelligent fallback.

    Priority:
    1. If device is specified, use it (with validation)
    2. CUDA if available
    3. MPS (Metal Performance Shaders) if available (Apple Silicon)
    4. CPU as fallback

    Args:
        device: Device specification. Can be:
            - None: Auto-detect best device
            - 'auto': Auto-detect best device
            - 'cuda': Use CUDA GPU
            - 'mps': Use Apple Silicon GPU
            - 'cpu': Use CPU
            - torch.device object

    Returns:
        torch.device object

    Examples:
        >>> device = get_device()  # Auto-detect
        >>> device = get_device('cuda')  # Force CUDA
        >>> device = get_device('mps')  # Force MPS
    """
    if device is None or device == 'auto':
        # Auto-detect best available device
        if torch.cuda.is_available():
            return torch.device('cuda')
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return torch.device('mps')
        else:
            return torch.device('cpu')

    if isinstance(device, torch.device):
        return device

    if isinstance(device, str):
        device = device.lower()

        if device == 'cuda':
            if not torch.cuda.is_available():
                print("Warning: CUDA requested but not available. Falling back to MPS/CPU.")
                return get_device('auto')
            return torch.device('cuda')

        elif device == 'mps':
            if not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
                print("Warning: MPS requested but not available. Falling back to CUDA/CPU.")
                return get_device('auto')
            return torch.device('mps')

        elif device == 'cpu':
            return torch.device('cpu')

        else:
            # Try to parse as torch.device string
            try:
                return torch.device(device)
            except:
                raise ValueError(
                    f"Invalid device: {device}. Use 'auto', 'cuda', 'mps', 'cpu', or None."
                )

    raise TypeError(f"Device must be str, torch.device, or None. Got {type(device)}")


def get_device_info() -> dict:
    """
    Get information about available devices.

    Returns:
        Dictionary with device availability and info
    """
    info = {
        'cuda_available': torch.cuda.is_available(),
        'mps_available': hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(),
        'best_device': str(get_device('auto')),
    }

    if info['cuda_available']:
        info['cuda_version'] = torch.version.cuda
        info['cuda_device_count'] = torch.cuda.device_count()
        info['cuda_device_name'] = torch.cuda.get_device_name(0)

    if info['mps_available']:
        info['mps_backend'] = 'available'

    return info


def print_device_info():
    """Print detailed device information."""
    info = get_device_info()

    print("=" * 60)
    print("DEVICE INFORMATION")
    print("=" * 60)

    print(f"Best available device: {info['best_device']}")
    print()

    print(f"CUDA available: {info['cuda_available']}")
    if info['cuda_available']:
        print(f"  CUDA version: {info['cuda_version']}")
        print(f"  GPU count: {info['cuda_device_count']}")
        print(f"  GPU name: {info['cuda_device_name']}")

    print()
    print(f"MPS available: {info['mps_available']}")
    if info['mps_available']:
        print("  Apple Silicon GPU acceleration enabled")

    print("=" * 60)


def move_to_device(obj, device: torch.device):
    """
    Move tensor or model to device with MPS-specific handling.

    Args:
        obj: Tensor, model, or dict of tensors/models
        device: Target device

    Returns:
        Object moved to device
    """
    if isinstance(obj, dict):
        return {k: move_to_device(v, device) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(move_to_device(item, device) for item in obj)
    elif hasattr(obj, 'to'):
        return obj.to(device)
    else:
        return obj


def is_mps_device(device: Union[str, torch.device]) -> bool:
    """Check if device is MPS."""
    if isinstance(device, str):
        return device.lower() == 'mps'
    elif isinstance(device, torch.device):
        return device.type == 'mps'
    return False


def is_cuda_device(device: Union[str, torch.device]) -> bool:
    """Check if device is CUDA."""
    if isinstance(device, str):
        return device.lower() == 'cuda'
    elif isinstance(device, torch.device):
        return device.type == 'cuda'
    return False

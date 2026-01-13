"""
HDQS Quantum Computing Library
Hyper-Dimensional Quantum System Client

Default Server: 31.97.239.213:8000
"""

__version__ = "1.0.0"
__author__ = "Sia Software Innovations Private Limited"
__server_ip__ = "31.97.239.213"
__server_port__ = 8000
__default_url__ = f"http://{__server_ip__}:{__server_port__}"

from .hdqs import (
    HDQSClient,
    LocalHDQSClient,
    HDQSError,
    connect,
    hdqs,
    call,
    create_circuit,
    run_circuit,
    measure,
    analyze,
    run_demo,
    create_hyper_system,
    DEFAULT_SERVER_IP,
    DEFAULT_SERVER_PORT,
    DEFAULT_BASE_URL
)

# Import core modules if available
try:
    from . import qbt
    from . import vqram
    from . import ntt
    from . import els
except ImportError:
    pass

__all__ = [
    "HDQSClient",
    "LocalHDQSClient",
    "HDQSError",
    "connect",
    "hdqs",
    "call",
    "create_circuit",
    "run_circuit",
    "measure",
    "analyze",
    "run_demo",
    "create_hyper_system",
    "DEFAULT_SERVER_IP",
    "DEFAULT_SERVER_PORT",
    "DEFAULT_BASE_URL",
    "qbt",
    "vqram"
]
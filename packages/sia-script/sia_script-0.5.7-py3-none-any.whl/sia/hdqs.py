"""
HDQS Client Library
PyPI package for interacting with HDQS Quantum Server
"""

import json
import requests
import warnings
import base64
import io
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from datetime import datetime
import numpy as np

# Default server IP (IPv4)
DEFAULT_SERVER_IP = "31.97.239.213"
DEFAULT_SERVER_PORT = 8000
DEFAULT_BASE_URL = f"http://{DEFAULT_SERVER_IP}:{DEFAULT_SERVER_PORT}"

# Try to import core modules for local testing
try:
    from . import qbt
    from . import vqram
    LOCAL_MODE_AVAILABLE = True
except ImportError:
    LOCAL_MODE_AVAILABLE = False
    qbt = None
    vqram = None


class HDQSClient:
    """
    Client for HDQS Quantum Server
    
    Handles communication with the server, authentication,
    and provides convenient methods for quantum operations
    """
    
    def __init__(self, 
                 base_url: str = DEFAULT_BASE_URL,
                 api_key: Optional[str] = None,
                 timeout: int = 30,
                 verify_ssl: bool = True):
        """
        Initialize HDQS client
        
        Args:
            base_url: Base URL of HDQS server (default: http://31.97.239.213:8000)
            api_key: API key for authentication (can be set later)
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Client state tracking
        self._current_state_id = None  # Track active quantum state
        self._has_active_circuit = False  # Track if circuit exists
        
        # ✅ NEW: Session ID tracking for stateful workflows
        self._session_id = None  # Track server session ID
        
        # Headers for all requests
        self.session.headers.update({
            "User-Agent": "HDQS-Python-Client/1.0.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Update API key header if provided
        if api_key:
            self.session.headers["X-API-Key"] = api_key
        
        # Test connection
        try:
            self._test_connection()
        except:
            warnings.warn(f"Could not connect to HDQS server at {self.base_url}. "
                         f"Server may be offline or IP may have changed.")
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set or update API key
        
        Args:
            api_key: New API key
        """
        self.api_key = api_key
        self.session.headers["X-API-Key"] = api_key
    
    def _test_connection(self) -> None:
        """Test connection to server"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            print(f"✓ Connected to HDQS server at {self.base_url}")
        except requests.exceptions.RequestException as e:
            warnings.warn(f"Failed to connect to HDQS server at {self.base_url}: {str(e)}")
    
    def call(self,
             op: str,
             payload: Optional[Dict[str, Any]] = None,
             save_to: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Call an HDQS operation
        
        Args:
            op: Operation name (e.g., "qbt_create", "vqram_save_state")
            payload: Operation parameters
            save_to: Optional path to save file if operation returns one
            
        Returns:
            Operation result as dict
            
        Raises:
            HDQSError: If operation fails
        """
        # Prepare request
        request_data = {
            "op": op,
            "payload": payload or {}
        }
        
        # ✅ NEW: Inject session_id into every outgoing payload
        if self._session_id:
            request_data["payload"]["session_id"] = self._session_id
        
        try:
            # Make request
            response = self.session.post(
                f"{self.base_url}/hdqs",
                json=request_data,
                timeout=self.timeout,
                verify=self.verify_ssl,
                stream=save_to is not None  # Stream if saving file
            )
            
            # Check for file response
            content_type = response.headers.get("Content-Type", "")
            
            if "application/octet-stream" in content_type and save_to:
                # Handle file download
                result = self._handle_file_response(response, save_to, op)
                
                # ✅ NEW: Capture session_id from file response headers
                session_id = response.headers.get("X-HDQS-Session-ID")
                if session_id:
                    self._session_id = session_id
                    result["session_id"] = session_id
                
                return result
            
            # Handle JSON response
            response.raise_for_status()
            result = response.json()
            
            # Check for success
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                raise HDQSError(f"Operation '{op}' failed: {error_msg}")
            
            # ✅ NEW: Capture session_id after every successful call
            if "session_id" in result:
                self._session_id = result["session_id"]
            
            return result
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('detail', str(e))
                except:
                    error_msg = str(e)
                raise HDQSError(f"Server error ({e.response.status_code}): {error_msg}")
            raise HDQSError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise HDQSError(f"Invalid response from server: {str(e)}")
    
    def _handle_file_response(self, 
                            response: requests.Response, 
                            save_to: Union[str, Path],
                            operation: str) -> Dict[str, Any]:
        """
        Handle file download response
        
        Args:
            response: HTTP response
            save_to: Path to save file
            operation: Original operation name
            
        Returns:
            Result dict with metrics
        """
        save_path = Path(save_to)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        try:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Extract metrics from headers
            metrics = {
                "operation": operation,
                "file_saved": True,
                "file_path": str(save_path),
                "file_size": save_path.stat().st_size,
                "server_metrics": {
                    "success": response.headers.get("X-HDQS-Success") == "true",
                    "session_id": response.headers.get("X-HDQS-Session-ID"),
                    "server_ip": DEFAULT_SERVER_IP
                }
            }
            
            return {
                "success": True,
                "operation": operation,
                "result": metrics,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HDQSError(f"Failed to save file: {str(e)}")
    
    # ==================== QUANTUM DATA SERIALIZATION ====================
    
    @staticmethod
    def serialize_quantum_data(data: Any) -> Dict[str, Any]:
        """
        Serialize quantum data for transmission
        
        Args:
            data: Quantum data (numpy array, qbt object, etc.)
            
        Returns:
            Serialized representation
        """
        if isinstance(data, np.ndarray):
            # Serialize numpy array
            buffer = io.BytesIO()
            np.save(buffer, data, allow_pickle=False)
            buffer.seek(0)
            return {
                "type": "numpy_array",
                "data": base64.b64encode(buffer.read()).decode('ascii'),
                "dtype": str(data.dtype),
                "shape": data.shape
            }
        elif hasattr(data, '__dict__') and hasattr(data, 'rho'):
            # qbt object
            buffer = io.BytesIO()
            np.save(buffer, data.rho, allow_pickle=False)
            buffer.seek(0)
            return {
                "type": "qbt_circuit",
                "num_qubits": data.num_qubits,
                "rho_data": base64.b64encode(buffer.read()).decode('ascii'),
                "has_statevector": data.statevector is not None
            }
        else:
            raise ValueError(f"Cannot serialize data type: {type(data)}")
    
    @staticmethod
    def deserialize_quantum_data(data_dict: Dict[str, Any]) -> Any:
        """
        Deserialize quantum data received from server
        
        Args:
            data_dict: Serialized data dictionary
            
        Returns:
            Deserialized quantum data
        """
        data_type = data_dict.get("type")
        
        if data_type == "numpy_array":
            data_bytes = base64.b64decode(data_dict["data"])
            buffer = io.BytesIO(data_bytes)
            return np.load(buffer)
        elif data_type == "qbt_circuit":
            if not LOCAL_MODE_AVAILABLE:
                raise HDQSError("Cannot deserialize qbt circuit: qbt module not available locally")
            
            num_qubits = data_dict.get("num_qubits", 1)
            circuit = qbt(num_qubits)
            
            if "rho_data" in data_dict:
                data_bytes = base64.b64decode(data_dict["rho_data"])
                buffer = io.BytesIO(data_bytes)
                circuit.rho = np.load(buffer)
            
            return circuit
        else:
            raise ValueError(f"Unknown data type: {data_type}")
    
    # ==================== CONVENIENCE METHODS ====================
    
    # QBT Operations
    
    def qbt_create(self, 
                   num_qubits: int,
                   explain_steps: bool = False,
                   random_seed: Optional[int] = None,
                   print_metrics: bool = False) -> Dict[str, Any]:
        """
        Create quantum circuit
        
        Args:
            num_qubits: Number of qubits
            explain_steps: Explain each step
            random_seed: Random seed for reproducibility
            print_metrics: Print circuit metrics
            
        Returns:
            Operation result
        """
        payload = {
            "num_qubits": num_qubits,
            "explain_steps": explain_steps,
            "print_metrics": print_metrics
        }
        
        if random_seed is not None:
            payload["random_seed"] = random_seed
        
        # qbt_create must RECORD the session's active state
        resp = self.call("qbt_create", payload)
        
        # remember that a circuit now exists
        self._current_state_id = "current"
        self._has_active_circuit = True
        
        return resp
    
    def qbt_run(self,
                circuit: List[str],
                state_id: Optional[str] = None,
                num_qubits: Optional[int] = None,
                return_file: bool = False,
                save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Run quantum circuit operations
        
        Args:
            circuit: List of gate operations (e.g., ["h 0", "cnot 0 1"])
            state_id: Optional existing state ID to continue from (default: "current")
            num_qubits: Number of qubits if creating new circuit
            return_file: Whether to return a file with the result
            save_to: Path to save file if return_file is True
            
        Returns:
            Operation result
        """
        payload = {"circuit": circuit, "return_file": return_file}
        
        # qbt_run must ALWAYS send state_id="current"
        # Force state_id to "current" if not specified
        payload["state_id"] = state_id if state_id is not None else "current"
        
        # Update client state tracking
        self._current_state_id = payload["state_id"]
        self._has_active_circuit = True
        
        if num_qubits:
            payload["num_qubits"] = num_qubits
        
        return self.call("qbt_run", payload, save_to=save_to)
    
    def qbt_measure(self,
                    qubits: Union[int, List[int]],
                    state_id: Optional[str] = None,
                    collapse: bool = True,
                    return_file: bool = False,
                    save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform quantum measurement
        
        Args:
            qubits: Qubit index or list of indices to measure
            state_id: Optional state ID to measure (default: "current")
            collapse: Whether to collapse state
            return_file: Whether to return a file with measurements
            save_to: Path to save file if return_file is True
            
        Returns:
            Measurement results
        """
        # qbt_measure must REQUIRE a prior run
        if not self._has_active_circuit:
            raise HDQSError("No active circuit. Call qbt_create and qbt_run first.")
        
        # Use "current" state if not specified
        if state_id is None:
            state_id = "current"
        
        payload = {
            "qubits": qubits if isinstance(qubits, list) else [qubits],
            "state_id": state_id,
            "collapse": collapse,
            "return_file": return_file
        }
        
        return self.call("qbt_measure", payload, save_to=save_to)
    
    def qbt_analyze(self,
                    state_id: Optional[str] = None,
                    plot: bool = False,
                    return_file: bool = False,
                    save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze quantum state
        
        Args:
            state_id: State ID to analyze (default: "current")
            plot: Whether to generate plots
            return_file: Whether to return a file with analysis
            save_to: Path to save file if return_file is True
            
        Returns:
            Analysis results
        """
        # Use "current" state if not specified
        if state_id is None:
            state_id = "current"
        
        payload = {
            "state_id": state_id,
            "plot": plot,
            "return_file": return_file
        }
        
        return self.call("qbt_analyze", payload, save_to=save_to)
    
    def qbt_demo(self, 
                 name: str = "bell",
                 return_file: bool = False,
                 save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a demo quantum circuit
        
        Args:
            name: Demo name ("bell", "grover", "teleportation", "qml_demo", etc.)
            return_file: Whether to return a file with demo results
            save_to: Path to save file if return_file is True
            
        Returns:
            Demo results
        """
        payload = {"name": name, "return_file": return_file}
        
        # Demo creates its own circuit, update client state
        resp = self.call("qbt_demo", payload, save_to=save_to)
        self._has_active_circuit = True
        self._current_state_id = "demo"
        
        return resp
    
    def qbt_define_chunk(self,
                         state_id: Optional[str] = None,
                         chunk_id: str = None,
                         qubit_indices: List[int] = None) -> Dict[str, Any]:
        """
        Define quantum chunk
        
        Args:
            state_id: State ID containing the circuit (default: "current")
            chunk_id: Unique chunk identifier
            qubit_indices: List of qubit indices in chunk
            
        Returns:
            Operation result
        """
        if not chunk_id:
            raise ValueError("chunk_id is required")
        if not qubit_indices:
            raise ValueError("qubit_indices is required")
        
        # Use "current" state if not specified
        if state_id is None:
            state_id = "current"
        
        return self.call("qbt_define_chunk", {
            "state_id": state_id,
            "chunk_id": chunk_id,
            "qubit_indices": qubit_indices
        })
    
    def qbt_get_chunk_features(self,
                               state_id: Optional[str] = None,
                               chunk_id: str = None,
                               return_file: bool = False,
                               save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Get features of a quantum chunk
        
        Args:
            state_id: State ID containing the chunk (default: "current")
            chunk_id: Chunk identifier
            return_file: Whether to return a file with features
            save_to: Path to save file if return_file is True
            
        Returns:
            Chunk features
        """
        if not chunk_id:
            raise ValueError("chunk_id is required")
        
        # Use "current" state if not specified
        if state_id is None:
            state_id = "current"
        
        payload = {
            "state_id": state_id,
            "chunk_id": chunk_id,
            "return_file": return_file
        }
        
        return self.call("qbt_get_chunk_features", payload, save_to=save_to)
    
    # vQRAM Operations - NO changes needed here
    # These are persistent storage operations, not runtime operations
    
    def vqram_save_state(self,
                         state_id: str,
                         quantum_data: Any,
                         description: str = "",
                         tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Save quantum state to vQRAM
        
        Args:
            state_id: Unique state identifier
            quantum_data: Quantum data to save (numpy array or qbt object)
            description: Optional description
            tags: Optional tags
            
        Returns:
            Save operation result
        """
        # Serialize quantum data
        serialized_data = self.serialize_quantum_data(quantum_data)
        
        payload = {
            "state_id": state_id,
            "quantum_data": serialized_data,
            "description": description
        }
        
        if tags:
            payload["tags"] = tags
        
        return self.call("vqram_save_state", payload)
    
    def vqram_load_state(self, 
                         state_id: str,
                         return_file: bool = False,
                         save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Load quantum state from vQRAM
        
        Args:
            state_id: State ID to load
            return_file: Whether to return a file with the state
            save_to: Path to save file if return_file is True
            
        Returns:
            Load operation result
        """
        payload = {
            "state_id": state_id,
            "return_file": return_file
        }
        
        return self.call("vqram_load_state", payload, save_to=save_to)
    
    def vqram_list_states(self, 
                          tag: Optional[str] = None,
                          return_file: bool = False,
                          save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        List available quantum states
        
        Args:
            tag: Optional tag filter
            return_file: Whether to return a file with the list
            save_to: Path to save file if return_file is True
            
        Returns:
            List of states
        """
        payload = {"return_file": return_file}
        if tag:
            payload["tag"] = tag
        
        return self.call("vqram_list_states", payload, save_to=save_to)
    
    def vqram_get_info(self, 
                       state_id: str,
                       return_file: bool = False,
                       save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about quantum state
        
        Args:
            state_id: State ID
            return_file: Whether to return a file with info
            save_to: Path to save file if return_file is True
            
        Returns:
            State information
        """
        payload = {
            "state_id": state_id,
            "return_file": return_file
        }
        
        return self.call("vqram_get_info", payload, save_to=save_to)
    
    def vqram_create_hyper_system(self,
                                  total_qubits: int,
                                  chunk_size: int,
                                  hyper_qubit_config: Dict[str, int],
                                  hyper_dimensions: int = 4,
                                  data: Optional[np.ndarray] = None,
                                  return_file: bool = False,
                                  save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Create hyper-dimensional quantum system
        
        Args:
            total_qubits: Total number of virtual qubits
            chunk_size: Qubits per chunk
            hyper_qubit_config: Configuration of hyper-qubit types
            hyper_dimensions: Number of hyper-dimensions
            data: Optional initial data (numpy array)
            return_file: Whether to return a file with system info
            save_to: Path to save file if return_file is True
            
        Returns:
            Hyper system creation result
        """
        payload = {
            "total_qubits": total_qubits,
            "chunk_size": chunk_size,
            "hyper_qubit_config": hyper_qubit_config,
            "hyper_dimensions": hyper_dimensions,
            "return_file": return_file
        }
        
        if data is not None:
            # Serialize numpy data
            payload["data"] = self.serialize_quantum_data(data)
        
        return self.call("vqram_create_hyper_system", payload, save_to=save_to)
    
    def vqram_run_hyper_operation(self,
                                  system_id: str,
                                  operation: str,
                                  return_file: bool = False,
                                  save_to: Optional[str] = None,
                                  **params) -> Dict[str, Any]:
        """
        Run operation on hyper system
        
        Args:
            system_id: Hyper system ID
            operation: Operation name
            return_file: Whether to return a file with results
            save_to: Path to save file if return_file is True
            **params: Operation parameters
            
        Returns:
            Operation result
        """
        payload = {
            "system_id": system_id,
            "operation": operation,
            "params": params,
            "return_file": return_file
        }
        
        return self.call("vqram_run_hyper_operation", payload, save_to=save_to)
    
    def vqram_teleport(self,
                       system_id: str,
                       source_chunk: int,
                       target_chunk: int,
                       return_file: bool = False,
                       save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform quantum teleportation between chunks
        
        Args:
            system_id: Hyper system ID
            source_chunk: Source chunk index
            target_chunk: Target chunk index
            return_file: Whether to return a file with results
            save_to: Path to save file if return_file is True
            
        Returns:
            Teleportation result
        """
        payload = {
            "system_id": system_id,
            "source_chunk": source_chunk,
            "target_chunk": target_chunk,
            "return_file": return_file
        }
        
        return self.call("vqram_teleport", payload, save_to=save_to)
    
    def vqram_evolve_state(self,
                           initial_state_id: str,
                           new_state_id: str,
                           evolution_name: str = "hadamard_all",
                           description: str = "",
                           return_file: bool = False,
                           save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Evolve quantum state
        
        Args:
            initial_state_id: Initial state ID
            new_state_id: New state ID for evolved state
            evolution_name: Evolution type ("hadamard_all" or "entangle_pairs")
            description: Optional description
            return_file: Whether to return a file with evolved state
            save_to: Path to save file if return_file is True
            
        Returns:
            Evolution result
        """
        payload = {
            "initial_state_id": initial_state_id,
            "new_state_id": new_state_id,
            "evolution_name": evolution_name,
            "description": description,
            "return_file": return_file
        }
        
        return self.call("vqram_evolve_state", payload, save_to=save_to)
    
    def vqram_state_similarity(self,
                               state_id1: str,
                               state_id2: str,
                               return_file: bool = False,
                               save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare two quantum states
        
        Args:
            state_id1: First state ID
            state_id2: Second state ID
            return_file: Whether to return a file with similarity
            save_to: Path to save file if return_file is True
            
        Returns:
            Similarity results
        """
        payload = {
            "state_id1": state_id1,
            "state_id2": state_id2,
            "return_file": return_file
        }
        
        return self.call("vqram_state_similarity", payload, save_to=save_to)
    
    # Utility Operations
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return self.call("metrics")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return self.call("status")
    
    def health_check(self) -> bool:
        """Check server health"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5,
                verify=self.verify_ssl
            )
            return response.status_code == 200
        except:
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        try:
            response = self.session.get(
                f"{self.base_url}/",
                timeout=5,
                verify=self.verify_ssl
            )
            return response.json()
        except:
            return {"server": "Unknown", "ip": DEFAULT_SERVER_IP, "status": "offline"}
    
    # Client state management
    
    def reset_circuit(self):
        """Reset client circuit state"""
        self._current_state_id = None
        self._has_active_circuit = False
    
    def get_active_circuit_state(self) -> Optional[str]:
        """Get current active circuit state ID"""
        return self._current_state_id
    
    def has_active_circuit(self) -> bool:
        """Check if client has an active circuit"""
        return self._has_active_circuit
    
    # ✅ NEW: Session management methods
    def get_session_id(self) -> Optional[str]:
        """Get current session ID"""
        return self._session_id
    
    def reset_session(self):
        """Reset session (start fresh)"""
        self._session_id = None
        self.reset_circuit()
    
    # ==================== CONTEXT MANAGER ====================
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close client session"""
        self.session.close()


class HDQSError(Exception):
    """HDQS client error"""
    pass


# ==================== LOCAL MODE ====================

class LocalHDQSClient:
    """
    Local mode client for testing without server
    Uses local sia.qbt and sia.vqram modules directly
    """
    
    def __init__(self):
        if not LOCAL_MODE_AVAILABLE:
            raise HDQSError("Local modules not available. Install sia package locally.")
        
        self.qbt = qbt
        self.vqram = vqram
        self._states = {}
        self._current_state_id = None
        self._has_active_circuit = False
        # ✅ NEW: Session ID for local mode consistency
        self._session_id = "local-session"
    
    def call(self, op: str, payload: Optional[Dict] = None, **kwargs):
        """Local implementation of operations"""
        payload = payload or {}
        
        if op == "qbt_create":
            return self._qbt_create(payload)
        elif op == "qbt_run":
            return self._qbt_run(payload)
        elif op == "qbt_measure":
            return self._qbt_measure(payload)
        elif op == "qbt_analyze":
            return self._qbt_analyze(payload)
        elif op == "qbt_demo":
            return self._qbt_demo(payload)
        else:
            raise HDQSError(f"Local mode does not support operation: {op}")
    
    def _qbt_create(self, payload):
        num_qubits = payload.get("num_qubits", 2)
        explain_steps = payload.get("explain_steps", False)
        random_seed = payload.get("random_seed")
        print_metrics = payload.get("print_metrics", False)
        
        circuit = self.qbt(num_qubits, explain_steps, random_seed, print_metrics)
        
        if "circuit" in payload:
            # Apply gates
            for gate_str in payload["circuit"]:
                parts = gate_str.split()
                if len(parts) >= 2:
                    gate = parts[0].lower()
                    target = int(parts[1])
                    
                    if gate == "h":
                        circuit.h(target)
                    elif gate == "x":
                        circuit.x(target)
                    elif gate == "cnot":
                        if len(parts) >= 3:
                            control = int(parts[2])
                            circuit.cnot(control, target)
        
        circuit.run()
        
        # Track state
        self._current_state_id = "current"
        self._has_active_circuit = True
        self._states["current"] = circuit
        
        return {
            "success": True,
            "operation": "qbt_create",
            "result": {
                "num_qubits": num_qubits,
                "circuit_created": True
            },
            "metrics": {"local_mode": True},
            "session_id": self._session_id,  # Include session_id
            "timestamp": datetime.now().isoformat()
        }
    
    def _qbt_run(self, payload):
        # Simplified local implementation
        self._current_state_id = payload.get("state_id", "current")
        self._has_active_circuit = True
        
        return {
            "success": True,
            "operation": "qbt_run",
            "result": {"local_execution": True},
            "metrics": {"local_mode": True},
            "session_id": self._session_id  # Include session_id
        }
    
    def _qbt_measure(self, payload):
        # Check for active circuit
        if not self._has_active_circuit:
            raise HDQSError("No active circuit. Call qbt_create and qbt_run first.")
        
        # Simplified local implementation
        return {
            "success": True,
            "operation": "qbt_measure",
            "result": {"measurement": "0", "local_mode": True},
            "metrics": {"local_mode": True},
            "session_id": self._session_id  # Include session_id
        }
    
    def _qbt_analyze(self, payload):
        # Simplified local implementation
        return {
            "success": True,
            "operation": "qbt_analyze",
            "result": {"purity": 1.0, "entropy": 0.0, "local_mode": True},
            "metrics": {"local_mode": True},
            "session_id": self._session_id  # Include session_id
        }
    
    def _qbt_demo(self, payload):
        name = payload.get("name", "bell")
        
        circuit = self.qbt(2)
        circuit.demo(name)
        circuit.run()
        
        # Track demo state
        self._current_state_id = "demo"
        self._has_active_circuit = True
        self._states["demo"] = circuit
        
        return {
            "success": True,
            "operation": "qbt_demo",
            "result": {"demo_name": name, "executed": True},
            "metrics": {"local_mode": True},
            "session_id": self._session_id  # Include session_id
        }


# ==================== FACTORY FUNCTIONS ====================

def connect(base_url: str = DEFAULT_BASE_URL, 
           api_key: Optional[str] = None,
           local_mode: bool = False,
           **kwargs) -> Union[HDQSClient, LocalHDQSClient]:
    """
    Connect to HDQS server or create local client
    
    Args:
        base_url: Server base URL (default: http://31.97.239.213:8000)
        api_key: API key for authentication
        local_mode: Use local mode without server
        **kwargs: Additional client parameters
        
    Returns:
        HDQS client instance
    """
    if local_mode:
        if not LOCAL_MODE_AVAILABLE:
            warnings.warn("Local modules not available, falling back to server mode")
        else:
            print("⚠️ Using LOCAL mode - No server connection")
            return LocalHDQSClient()
    
    print(f"🔗 Connecting to HDQS server at: {base_url}")
    return HDQSClient(base_url, api_key, **kwargs)


# ==================== SIMPLE API ====================

_client_instance = None

def get_client(base_url: str = DEFAULT_BASE_URL,
              api_key: Optional[str] = None,
              **kwargs) -> HDQSClient:
    """
    Get or create a global client instance
    
    Args:
        base_url: Server base URL (default: http://31.97.239.213:8000)
        api_key: API key
        **kwargs: Additional parameters
        
    Returns:
        HDQS client
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = connect(base_url, api_key, **kwargs)
    elif api_key and _client_instance.api_key != api_key:
        _client_instance.set_api_key(api_key)
    
    return _client_instance


def call(op: str, payload: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Quick call to HDQS operation using global client
    
    Args:
        op: Operation name
        payload: Operation parameters
        **kwargs: Additional call parameters
        
    Returns:
        Operation result
    """
    client = get_client()
    return client.call(op, payload, **kwargs)


# Common operations as direct functions
def create_circuit(num_qubits: int, **kwargs) -> Dict[str, Any]:
    """Create quantum circuit"""
    return call("qbt_create", {"num_qubits": num_qubits, **kwargs})

def run_circuit(circuit: List[str], **kwargs) -> Dict[str, Any]:
    """Run quantum circuit"""
    return call("qbt_run", {"circuit": circuit, **kwargs})

def measure(qubits: Union[int, List[int]], **kwargs) -> Dict[str, Any]:
    """Measure qubits"""
    return call("qbt_measure", {"qubits": qubits, **kwargs})

def analyze(state_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Analyze quantum state"""
    payload = kwargs.copy()
    if state_id:
        payload["state_id"] = state_id
    return call("qbt_analyze", payload)

def run_demo(name: str = "bell", **kwargs) -> Dict[str, Any]:
    """Run quantum demo"""
    return call("qbt_demo", {"name": name, **kwargs})

def create_hyper_system(total_qubits: int, chunk_size: int, hyper_qubit_config: Dict, **kwargs) -> Dict[str, Any]:
    """Create hyper-dimensional system"""
    return call("vqram_create_hyper_system", {
        "total_qubits": total_qubits,
        "chunk_size": chunk_size,
        "hyper_qubit_config": hyper_qubit_config,
        **kwargs
    })


# ==================== MAIN HDQS FUNCTION ====================

def hdqs(base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        local_mode: bool = False,
        **kwargs):
    """
    Main HDQS interface
    
    Example:
        from sia import hdqs
        
        # Server mode (connects to 31.97.239.213:8000 by default)
        q = hdqs(api_key="TOKEN")
        result = q.qbt_create(num_qubits=4)
        
        # Local mode  
        q = hdqs(local_mode=True)
        result = q.qbt_demo("bell")
        
        # Custom server
        q = hdqs(base_url="http://custom-ip:8000")
    """
    return connect(base_url, api_key, local_mode, **kwargs)


# Make HDQS available as both function and module
hdqs.connect = connect
hdqs.call = call
hdqs.HDQSError = HDQSError
hdqs.serialize_quantum_data = HDQSClient.serialize_quantum_data
hdqs.deserialize_quantum_data = HDQSClient.deserialize_quantum_data

# Quick access functions
hdqs.qbt_create = create_circuit
hdqs.qbt_run = run_circuit
hdqs.qbt_measure = measure
hdqs.qbt_analyze = analyze
hdqs.qbt_demo = run_demo
hdqs.vqram_create_hyper_system = create_hyper_system
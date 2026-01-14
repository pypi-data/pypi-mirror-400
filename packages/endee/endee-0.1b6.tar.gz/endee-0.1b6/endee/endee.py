import os
import requests
import httpx
import secrets
import json
from endee.exceptions import raise_exception
from endee.index import Index
from endee.user import User
from endee.crypto import get_checksum
from endee.utils import is_valid_index_name
from functools import lru_cache

SUPPORTED_REGIONS = ["us-west", "india-west", "local"]

class SessionManager:
    """Centralized session manager with a shared requests.Session"""
    def __init__(self, pool_connections: int = 1, pool_maxsize: int = 10, max_retries: int = 3, pool_block: bool = True):
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.max_retries = max_retries
        self.pool_block = pool_block
        # self._local = threading.local()
        self._session: requests.Session | None = None
        self._pid = None

    def __getstate__(self):
        state = self.__dict__.copy()
        # state["_client"] = None
        state["_session"] = None
        state["_pid"] = None
        return state
    
    def get_session(self) -> requests.Session:
        """Get or create the shared session."""
        pid = os.getpid()
        if self._session is None or self._pid != pid:
            session = requests.Session()
            
            # Configure adapter with connection pooling and retries
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=self.pool_connections,
                pool_maxsize=self.pool_maxsize,
                max_retries=requests.adapters.Retry(
                    total=self.max_retries,
                    backoff_factor=0.5,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
                ),
                pool_block=self.pool_block
            )
            
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            self._session = session
            self._pid = pid
        
        return self._session
    
    def close_session(self):
        """Close the shared session."""
        if self._session is not None:
            self._session.close()
            self._session = None
            self._pid = None

class ClientManager:
    """Centralized client manager with a shared httpx.Client"""
    def __init__(self, max_connections: int = 1, max_keepalive_connections: int = 10, max_retries: int = 3, timeout: float = 30.0, http2: bool = False):
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.max_retries = max_retries
        self.timeout = timeout
        self.http2 = http2
        # self._local = threading.local()
        self._client: httpx.Client | None = None
        self._pid = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_client"] = None
        # state["_session"] = None
        state["_pid"] = None
        return state

    def get_client(self) -> httpx.Client:
        pid = os.getpid()

        if self._client is None or self._pid != pid:
            limits = httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
            )

            transport = httpx.HTTPTransport(
                retries=self.max_retries
            )

            self._client = httpx.Client(
                http2=self.http2,
                limits=limits,
                transport=transport,
                timeout=self.timeout,
            )
            self._pid = pid

        return self._client
    
    def close_client(self):
        if self._client is not None:
            self._client.close()
            self._client = None
            self._pid = None

class Endee:
    def __init__(self, token:str|None=None, http_library: str = "requests"):
        self.token = token
        self.region = "local"
        self.base_url = "http://127.0.0.1:8080/api/v1"
        # Token will be of the format user:token:region
        if token:
            token_parts = self.token.split(":")
            if len(token_parts) > 2:
                self.base_url = f"https://{token_parts[2]}.endee.io/api/v1"
                self.token = f"{token_parts[0]}:{token_parts[1]}"
        self.version = 1
        self.library = http_library

        if self.library == "requests":
            # Centralized session manager - shared across all Index objects
            self.session_manager = SessionManager(
                pool_connections=10,
                pool_maxsize=10,
                max_retries=3
            )
        elif self.library == "httpx1.1":
            # httpx.Client based manager
            self.client_manager = ClientManager(
                max_connections=10,
                max_keepalive_connections=10,
                max_retries=3
            )
        elif self.library == "httpx2":
            # httpx.Client based manager
            self.client_manager = ClientManager(
                http2=True,
                max_connections=10,
                max_keepalive_connections=10,
                max_retries=3
            )
        else:
            raise ValueError(
                "Unsupported library. Only 'requests', 'httpx1.1' and 'httpx2' are supported."
            )

    def _get_session(self) -> requests.Session:
        """Get session from the centralized session manager."""
        return self.session_manager.get_session()
    
    def close_session(self):
        """Close the thread-local session."""
        self.session_manager.close_session()

    def _get_client(self) -> httpx.Client:
        """Get session from the centralized session manager."""
        return self.client_manager.get_client()
    
    def close_client(self):
        """Close the thread-local session."""
        self.client_manager.close_client()

    def __str__(self):
        return self.token

    def set_token(self, token:str):
        self.token = token
        self.region = self.token.split (":")[1]
    
    def set_base_url(self, base_url:str):
        self.base_url = base_url
    
    def generate_key(self)->str:
        # Generate a random hex key of length 32 (256 bit)
        key = secrets.token_hex(32) 
        print("Store this encryption key in a secure location. Loss of the key will result in the irreversible loss of associated vector data.\nKey: ",key)
        return key

    def create_index(self, name:str, dimension:int, space_type:str, M:int=16, key:str|None=None, ef_con:int=128, precision:str|None="int8d", version:int=None, sparse_dim:int=0):
        if is_valid_index_name(name) == False:
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and should be less than 48 characters")
        if dimension > 10000:
            raise ValueError("Dimension cannot be greater than 10,000")
        if sparse_dim < 0:
            raise ValueError("sparse_dim cannot be negative")
        space_type = space_type.lower()
        if space_type not in ["cosine", "l2", "ip"]:
            raise ValueError(f"Invalid space type: {space_type}")
        if precision not in ["binary", "float16", "float32", "int16d", "int4d", "int8d"]:
            raise ValueError(f"Invalid precision:{precision}. Must be one of: binary, float16, float32, int16d, int4d, int8d")
        
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'index_name': name,
            'dim': dimension,
            'space_type': space_type,
            'M':M,
            'ef_con': ef_con,
            'checksum': get_checksum(key),
            'precision': precision,
            'version': version
        }

        if sparse_dim > 0:
            data['sparse_dim'] = sparse_dim

        if self.library == "requests":
            session = self._get_session()
            response = session.post(f'{self.base_url}/index/create', headers=headers, json=data)
        else:  # httpx1.1 or httpx2
            client = self._get_client()
            response = client.post(f'{self.base_url}/index/create', headers=headers, json=data)

        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return "Index created successfully"


    def list_indexes(self):
        headers = {
            'Authorization': f'{self.token}',
        }

        if self.library == "requests":
            session = self._get_session()
            response = session.get(f'{self.base_url}/index/list', headers=headers)
        else:  # httpx1.1 or httpx2
            client = self._get_client()
            response = client.get(f'{self.base_url}/index/list', headers=headers)

        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        indexes = response.json()
        return indexes
    
    # TODO - Delete the index cache if the index is deleted
    def delete_index(self, name:str):
        headers = {
            'Authorization': f'{self.token}',
        }
        
        if self.library == "requests":
            session = self._get_session()
            response = session.delete(f'{self.base_url}/index/{name}/delete', headers=headers)
        else:  # httpx1.1 or httpx2
            client = self._get_client()
            response = client.delete(f'{self.base_url}/index/{name}/delete', headers=headers)

        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return f'Index {name} deleted successfully'


    # Keep in lru cache for sometime
    @lru_cache(maxsize=10)
    def get_index(self, name:str, key:str|None=None):
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        # Get index details from the server
        if self.library == "requests":
            session = self._get_session()
            response = session.get(f'{self.base_url}/index/{name}/info', headers=headers)
        else:  # httpx1.1 or httpx2
            client = self._get_client()
            response = client.get(f'{self.base_url}/index/{name}/info', headers=headers)

        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        data = response.json()
        #print(data)
        #print(data)
        # Raise error if checksum does not match
        checksum = get_checksum(key)
        if checksum != data['checksum']:
            raise_exception(403, "Checksum does not match. Please check the key.")
        # Pass appropriate manager to Index
        if self.library == "requests":
            idx = Index(name=name, key=key, token=self.token, url=self.base_url, version=self.version, params=data, session_client_manager=self.session_manager)
        else:
            idx = Index(name=name, key=key, token=self.token, url=self.base_url, version=self.version, params=data, session_client_manager=self.client_manager)

        return idx

    
    def get_user(self):
        if self.library == "requests":
             return User(self.base_url, self.token,  session_client_manager=self.session_manager)
        else:
             return User(self.base_url, self.token,  session_client_manager=self.client_manager)
        
    def __del__(self):
        """Cleanup sessions or client on object deletion."""
        try:
            if self.library == "requests":
                self.close_session()
            else:
                self.close_client()        
        except Exception:
            pass


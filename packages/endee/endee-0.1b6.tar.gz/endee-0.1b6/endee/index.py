import requests, json, zlib
import numpy as np
import msgpack
from .crypto import get_checksum, json_zip, json_unzip
from .exceptions import raise_exception

class Index:
    def __init__(self, name:str, key:str, token:str, url:str, version:int=1, params=None, session_client_manager=None):
        self.name = name
        self.key = key
        self.token = token
        self.url = url
        self.version = version
        self.checksum = get_checksum(self.key)
        self.lib_token = params["lib_token"]
        self.count = params["total_elements"]
        self.space_type = params["space_type"]
        self.dimension = params["dimension"]
        self.precision = params.get("precision")
        self.M = params["M"]
        self.sparse_dim = params.get("sparse_dim", 0)

        # Use shared http manager from Endee client
        self.session_client_manager = session_client_manager


    def _get_session_client(self) -> requests.Session:
        """Get either session or client based on manager type."""
        if hasattr(self.session_client_manager, 'get_session'):
            return self.session_client_manager.get_session()
        elif hasattr(self.session_client_manager, 'get_client'):
            return self.session_client_manager.get_client()
        else:
            raise ValueError("Manager must have either get_session or get_client method. An Endee Client object needs to be initialised first  and the existing indexes can be initialised using Endee_client_object.get_index(index_name)")


    @property
    def is_hybrid(self):
        return self.sparse_dim > 0

    def __str__(self):
        return self.name
    
    def _normalize_vector(self, vector):
        # Convert to numpy array if not already
        vector = np.array(vector, dtype=np.float32)
        # Check dimension of the vector
        if vector.ndim != 1 or vector.shape[0] != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {vector.shape[0]}")
        # Normalize only if using cosine distance
        if self.space_type != "cosine":
            return vector, 1.0
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector, 1.0
        normalized_vector = vector / norm
        return normalized_vector, float(norm)

    def upsert(self, input_array):
        if len(input_array) > 1000:
            raise ValueError("Cannot insert more than 1000 vectors at a time")

        vector_batch = []

        vectors = []
        norms = []
        for item in input_array:
            vector, norm = self._normalize_vector(item['vector'])
            vectors.append(vector)
            norms.append(norm)

        vectors = np.vstack(vectors).astype(np.float32)  # shape: (N, dim)

        for i, item in enumerate(input_array):
            # Get sparse data if present
            sparse_indices = item.get('sparse_indices')
            sparse_values = item.get('sparse_values')
            has_sparse = sparse_indices is not None or sparse_values is not None

            # Validation: Cannot insert sparse data into dense-only index
            if has_sparse and not self.is_hybrid:
                raise ValueError("Cannot insert sparse data into a dense-only index. Create index with sparse_dim > 0 for hybrid support.")

            # Validation: Hybrid index requires sparse data
            if self.is_hybrid and not has_sparse:
                raise ValueError("Hybrid index requires sparse_indices and sparse_values for each vector.")

            # Validation: Both sparse_indices and sparse_values must be provided together
            if self.is_hybrid:
                if sparse_indices is None or sparse_values is None:
                    raise ValueError("Both sparse_indices and sparse_values must be provided for hybrid vectors.")
                if len(sparse_indices) != len(sparse_values):
                    raise ValueError(f"sparse_indices and sparse_values must have the same length. Got {len(sparse_indices)} indices and {len(sparse_values)} values.")
                # Validate indices are within bounds
                for idx in sparse_indices:
                    if idx < 0 or idx >= self.sparse_dim:
                        raise ValueError(f"Sparse index {idx} is out of bounds. Must be in range [0, {self.sparse_dim}).")

            meta_data = json_zip(dict=item.get('meta', {}), key=self.key)

            # Build vector object - format depends on whether it's hybrid or dense
            if self.is_hybrid:
                vector_obj = [
                    str(item.get('id', '')),
                    meta_data,
                    json.dumps(item.get('filter', {})),
                    float(norms[i]),
                    vectors[i].tolist(),
                    list(sparse_indices),
                    [float(v) for v in sparse_values]
                ]
            else:
                vector_obj = [
                    str(item.get('id', '')),
                    meta_data,
                    json.dumps(item.get('filter', {})),
                    float(norms[i]),
                    vectors[i].tolist()
                ]
            vector_batch.append(vector_obj)

        serialized_data = msgpack.packb(vector_batch, use_bin_type=True, use_single_float=True)
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/msgpack'
        }

        http_client = self._get_session_client()
        response = http_client.post(
            f'{self.url}/index/{self.name}/vector/insert', 
            headers=headers, 
            data=serialized_data
        )

        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        return "Vectors inserted successfully"

    def query(self, vector=None, top_k=10, filter=None, ef=128, include_vectors=False, log=False, sparse_indices=None, sparse_values=None):
        if top_k > 512 or top_k <= 0:
            raise ValueError("top_k cannot be greater than 512 and top_k cannot be less than 1")
        if ef > 1024:
            raise ValueError("ef search cannot be greater than 1024")

        # Validate sparse query parameters
        has_sparse = sparse_indices is not None or sparse_values is not None
        has_dense = vector is not None

        # At least one query type must be provided
        if not has_dense and not has_sparse:
            raise ValueError("At least one of 'vector' or 'sparse_indices'/'sparse_values' must be provided.")

        # Cannot use sparse query on dense-only index
        if has_sparse and not self.is_hybrid:
            raise ValueError("Cannot perform sparse search on a dense-only index. Create index with sparse_dim > 0 for hybrid support.")

        # If one sparse parameter is provided, both must be provided
        if has_sparse:
            if sparse_indices is None or sparse_values is None:
                raise ValueError("Both sparse_indices and sparse_values must be provided together.")
            if len(sparse_indices) != len(sparse_values):
                raise ValueError(f"sparse_indices and sparse_values must have the same length. Got {len(sparse_indices)} indices and {len(sparse_values)} values.")

        # Prepare search request
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }

        data = {
            'k': top_k,
            'ef': ef,
            'include_vectors': include_vectors
        }

        # Add dense vector if provided
        if has_dense:
            # Normalize query vector if using cosine
            normalized_vector, norm = self._normalize_vector(vector)
            data['vector'] = normalized_vector.tolist()

        # Add sparse query if provided
        if has_sparse:
            data['sparse_indices'] = list(sparse_indices)
            data['sparse_values'] = [float(v) for v in sparse_values]

        if filter:
            data['filter'] = json.dumps(filter)

        http_client = self._get_session_client()
        response = http_client.post(
            f'{self.url}/index/{self.name}/search',
            headers=headers,
            json=data
        )


        if response.status_code != 200:
            raise_exception(response.status_code, response.text)

        results = msgpack.unpackb(response.content, raw=False)

        # [similarity, id, meta, filter, norm, vector]
        processed_results = []

        results = results[:top_k]

        for result in results:
            similarity = result[0]
            vector_id = result[1]
            meta_data = result[2]
            filter_str = result[3]
            norm_value = result[4]
            vector_data = result[5] if len(result) > 5 else []

            processed = {
                'id': vector_id,
                'similarity': similarity,
                'distance': 1.0 - similarity,
                'meta': json_unzip(meta_data, self.key),
                'norm': norm_value
            }

            if filter_str:
                processed['filter'] = json.loads(filter_str)

            if include_vectors and vector_data:
                processed['vector'] = list(vector_data)
            else:
                processed['vector'] = []
            processed_results.append(processed)

        return processed_results

    
    def delete_vector(self, id):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
        }
        http_client = self._get_session_client()
        response = http_client.delete(f'{self.url}/index/{self.name}/vector/{id}/delete', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        return response.text + " rows deleted"
    
    # Delete multiple vectors based on a filter
    def delete_with_filter(self, filter):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {"filter": filter}
        print(filter)
        http_client = self._get_session_client()
        response = http_client.delete(f'{self.url}/index/{self.name}/vectors/delete', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return response.text

    
    # Get a single vector by id
    def get_vector(self, id):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }

        # Use POST method with the ID in the request body
        http_client = self._get_session_client()
        response = http_client.post(
            f'{self.url}/index/{self.name}/vector/get',
            headers=headers,
            json={'id': id}
        )

        if response.status_code != 200:
            raise_exception(response.status_code, response.text)

        # Parse the msgpack response
        vector_obj = msgpack.unpackb(response.content, raw=False)

        result = {
            'id': vector_obj[0],
            'meta': json_unzip(vector_obj[1], self.key),
            'filter': vector_obj[2],
            'norm': vector_obj[3],
            'vector': list(vector_obj[4])
        }

        # Include sparse data if present (for hybrid indexes)
        if len(vector_obj) > 5:
            result['sparse_indices'] = list(vector_obj[5]) if vector_obj[5] else []
        if len(vector_obj) > 6:
            result['sparse_values'] = list(vector_obj[6]) if vector_obj[6] else []

        return result

    def describe(self):
        data = {
            "name": self.name,
            "space_type": self.space_type,
            "dimension": self.dimension,
            "sparse_dim": self.sparse_dim,
            "is_hybrid": self.is_hybrid,
            "count": self.count,
            "precision": self.precision,
            "M": self.M,
        }
        return data
# Endee - High-Performance Vector Database

Endee is a high-performance vector database designed for speed and efficiency. It enables rapid Approximate Nearest Neighbor (ANN) searches for applications requiring robust vector search capabilities with advanced filtering, metadata support, and hybrid search combining dense and sparse vectors.

## Key Features

- **Fast ANN Searches**: Efficient similarity searches on vector data using HNSW algorithm
- **Hybrid Search**: Combine dense and sparse vectors for powerful semantic + keyword search
- **Multiple Distance Metrics**: Support for cosine, L2, and inner product distance metrics
- **Metadata Support**: Attach and search with metadata and filters
- **Advanced Filtering**: Powerful query filtering with operators like `$eq`, `$in`, and `$range`
- **High Performance**: Optimized for speed and efficiency
- **Scalable**: Handle millions of vectors with ease
- **Configurable Precision**: Multiple precision levels for memory/accuracy tradeoffs

## Installation

```bash
pip install endee
```

## Quick Start

```python
from endee import Endee

# Initialize client with your API token
client = Endee(token="your-token-here")

# List existing indexes
indexes = client.list_indexes()

# Create a new index
client.create_index(
    name="my_vectors",
    dimension=1536,       # Your vector dimension
    space_type="cosine",  # Distance metric (cosine, l2, ip)
    precision="int8"      # Default precision level
)

# Get index reference
index = client.get_index(name="my_vectors")

# Insert vectors
index.upsert([
    {
        "id": "doc1",
        "vector": [0.1, 0.2, 0.3, ...],  # Your vector data
        "meta": {"text": "Example document", "category": "reference"},
        "filter": {"category": "reference", "tags": "important"}
    }
])

# Query similar vectors with filtering
results = index.query(
    vector=[0.2, 0.3, 0.4, ...],  # Query vector
    top_k=10,
    filter=[{"category": {"$eq": "reference"}}]  # Structured filter
)

# Process results
for item in results:
    print(f"ID: {item['id']}, Similarity: {item['similarity']}")
    print(f"Metadata: {item['meta']}")
```

## Basic Usage

To interact with the Endee platform, you'll need to authenticate using an API token. This token is used to securely identify your workspace and authorize all actions — including index creation, vector upserts, and queries.

### 🔐 Generate Your API Token

You can create and manage your authentication tokens from the **Endee Dashboard** under the **API Keys** section.

- Each token is tied to your workspace and should be kept private
- Once you have your token, you're ready to initialize the client and begin using the SDK

### Initializing the Client

The Endee client acts as the main interface for all vector operations — such as creating indexes, upserting vectors, and running similarity queries. You can initialize the client in just a few lines:

```python
from endee.endee import Endee

# Initialize with your API token
client = Endee(token="your-token-here")
```

### Listing All Indexes

The `client.list_indexes()` method returns a list of all the indexes currently available in your environment or workspace. This is useful for managing, debugging, or programmatically selecting indexes for vector operations like upsert or search.

```python
from endee.endee import Endee

client = Endee(token="your-token-here")

# List all indexes in your workspace
indexes = client.list_indexes()
```

### Create an Index

The `client.create_index()` method initializes a new vector index with customizable parameters such as dimensionality, distance metric, graph construction settings, and precision level. These configurations determine how the index stores and retrieves high-dimensional vector data.

```python
from endee.endee import Endee

client = Endee(token="your-token-here")

# Create an index with custom parameters
client.create_index(
    name="my_custom_index",
    dimension=768,
    space_type="cosine",
    M=16,              # Graph connectivity parameter (default = 16)
    ef_con=128,        # Construction-time parameter (default = 128)
    precision="int8d",   # Precision level (recommended)
)
```

**Parameters:**

- `name`: Unique name for your index (alphanumeric + underscores, max 48 chars)
- `dimension`: Vector dimensionality (must match your embedding model's output, max 10000)
- `space_type`: Distance metric - `"cosine"`, `"l2"`, or `"ip"` (inner product)
- `M`: HNSW graph connectivity parameter - higher values increase recall but use more memory (default: 16)
- `ef_con`: HNSW construction parameter - higher values improve index quality but slow down indexing (default: 128)
- `precision`: Vector precision level - `"int8d"` (default), `"binary"`, `"int4d"`, `"int16d"`, `"float16"`, or `"float32"`
- `key`: Optional encryption key for client-side encryption (if None, index is not encrypted)
- `version`: Optional version parameter for index versioning
- `sparse_dim`: Optional sparse vector dimension for hybrid search (e.g., 30000 for BM25/SPLADE)

**Precision Levels:**

The `precision` parameter controls how vectors are stored internally, affecting memory usage and search accuracy.

| Precision | Quantization | Data Type | Memory Usage | Accuracy | Use Case |
|-----------|--------------|-----------|--------------|----------|----------|
| `"float32"` | 32-bit | FP32 | Highest | Maximum | When accuracy is absolutely critical |
| `"float16"` | 16-bit | FP16 | ~50% less | Very good | Good accuracy with half precision |
| `"int16d"` | 16-bit | INT16 | ~50% less | Very good | Integer quantization with good accuracy |
| `"int8d"` | 8-bit | INT8 | ~75% less | Good | **Default** - great for most use cases |
| `"int4d"` | 4-bit | INT4 | ~87.5% less | Fair | Maximum compression for memory-constrained scenarios |
| `"binary"` | 1-bit | Binary | ~96.9% less | Lower | Extreme compression for large-scale similarity search |

**Choosing the Right Precision:**

- **`"int8d"`**: **Default and recommended for most use cases** - provides good accuracy with significant memory savings using 8-bit integer quantization
- **`"int16d"` / `"float16"`**: Better accuracy with moderate memory savings (16-bit precision)
- **`"float32"`**: Maximum accuracy using full 32-bit floating point (highest memory usage)
- **`"int4d"`**: Aggressive compression for memory-constrained environments where some accuracy loss is acceptable
- **`"binary"`**: Extreme compression for very large-scale deployments where memory is critical and lower accuracy is tolerable

### Get an Index

The `client.get_index()` method retrieves a reference to an existing index. This is required before performing vector operations like upsert, query, or delete.

```python
from endee import Endee

client = Endee(token="your-token-here")

# Get reference to an existing index
index = client.get_index(name="my_custom_index")

# Now you can perform operations on the index
print(index.describe())
```

**Parameters:**

- `name`: Name of the index to retrieve
- `key`: Encryption key used when creating the index (required if index was created with encryption, pass `None` for unencrypted indexes)

**Returns:** An `Index` instance configured with server parameters

> **Note:** The key must match the key used when creating the index. If the checksum doesn't match, an error will be raised.

### Ingestion of Data

The `index.upsert()` method is used to add or update vectors (embeddings) in an existing index. Each vector is represented as an object containing a unique identifier, the vector data itself, optional metadata, and optional filter fields for future querying.

```python
from endee.endee import Endee

client = Endee(token="your-token-here")

# Accessing the index
index = client.get_index(name="your-index-name")

# Insert multiple vectors in a batch
index.upsert([
    {
        "id": "vec1",
        "vector": [...],  # Your vector
        "meta": {"title": "First document"},
        "filter": {"tags": "important"}  # Optional filter values
    },
    {
        "id": "vec2",
        "vector": [...],  # Another vector
        "meta": {"title": "Second document"},
        "filter": {"visibility": "public", "tags": "important"}
    }
])
```

**Vector Object Fields:**

- `id`: Unique identifier for the vector (required)
- `vector`: Array of floats representing the embedding (required)
- `meta`: Arbitrary metadata object for storing additional information (optional)
- `filter`: Key-value pairs for structured filtering during queries (optional)

> **Note:** Maximum batch size is 1000 vectors per upsert call.

### Querying the Index

The `index.query()` method performs a similarity search in the index using a given query vector. It returns the closest vectors (based on the index's distance metric) along with optional metadata and vector data.

```python
from endee.endee import Endee

client = Endee(token="your-token-here")

# Accessing the index
index = client.get_index(name="your-index-name")

# Query with custom parameters
results = index.query(
    vector=[...],         # Query vector
    top_k=5,              # Number of results to return (max 512)
    ef=128,               # Runtime parameter for search quality (max 1024)
    include_vectors=True  # Include vector data in results
)
```

**Query Parameters:**

- `vector`: Query vector (must match index dimension)
- `top_k`: Number of nearest neighbors to return (max 512, default: 10)
- `ef`: Runtime search parameter - higher values improve recall but increase latency (max 1024, default: 128)
- `include_vectors`: Whether to return the actual vector data in results (default: False)
- `filter`: Optional filter criteria (array of filter objects)
- `log`: Optional logging parameter for debugging (default: False)

**Result Fields:**

- `id`: Vector identifier
- `similarity`: Similarity score
- `distance`: Distance score (1.0 - similarity)
- `meta`: Metadata dictionary
- `norm`: Vector norm
- `vector`: Vector data (if `include_vectors=True`)

## Hybrid Search

Hybrid search combines dense vector embeddings (semantic similarity) with sparse vectors (keyword/term matching) to provide more powerful and flexible search capabilities. This is particularly useful for applications that need both semantic understanding and exact term matching, such as:

- RAG (Retrieval-Augmented Generation) systems
- Document search with keyword boosting
- Multi-modal search combining different ranking signals
- BM25 + neural embedding fusion

### Creating a Hybrid Index

To enable hybrid search, specify the `sparse_dim` parameter when creating an index. This defines the dimensionality of the sparse vector space (typically the vocabulary size for BM25 or SPLADE models).

```python
import time

start = time.perf_counter()

client.create_index(
    name="hybridtest1",
    dimension=384,          # dense vector dimension
    sparse_dim=30000,       # sparse vector dimension (BM25 / SPLADE etc.)
    space_type="cosine",
)

end = time.perf_counter()
print(f"Index creation latency: {end - start}s")

# Get reference to the hybrid index
index = client.get_index(name="hybridtest1")
```

### Upserting Hybrid Vectors

When upserting vectors to a hybrid index, you must provide both dense vectors and sparse vector representations. Sparse vectors are defined using two parallel arrays: `sparse_indices` (positions) and `sparse_values` (weights).

```python
import numpy as np
import random

np.random.seed(42)
random.seed(42)

TOTAL_VECTORS = 2000
BATCH_SIZE = 1000
DIM = 384
SPARSE_DIM = 30000

batch = []
start = time.perf_counter()

for i in range(TOTAL_VECTORS):
    # Dense vector (semantic embedding)
    dense_vec = np.random.rand(DIM).astype(float).tolist()
    
    # Sparse vector (e.g., BM25 term weights)
    # Example: 20 non-zero terms
    nnz = 20
    sparse_indices = random.sample(range(SPARSE_DIM), nnz)
    sparse_values = np.random.rand(nnz).astype(float).tolist()
    
    item = {
        "id": f"hybrid_vec_{i+1}",
        "vector": dense_vec,
        
        # Required for hybrid search
        "sparse_indices": sparse_indices,
        "sparse_values": sparse_values,
        
        "meta": {
            "title": f"Hybrid Document {i+1}",
            "index": i,
        },
        "filter": {
            "visibility": "public" if i % 2 == 0 else "private"
        }
    }
    
    batch.append(item)
    
    if len(batch) == BATCH_SIZE or i + 1 == TOTAL_VECTORS:
        index.upsert(batch)
        print(f"Upserted {len(batch)} hybrid vectors")
        batch = []

end = time.perf_counter()
print(f"Hybrid upsert latency: {end - start}s")
```

**Hybrid Vector Fields:**

- `id`: Unique identifier (required)
- `vector`: Dense embedding vector (required)
- `sparse_indices`: List of non-zero term positions in sparse vector (required for hybrid)
- `sparse_values`: List of weights corresponding to sparse_indices (required for hybrid)
- `meta`: Metadata dictionary (optional)
- `filter`: Filter fields for structured filtering (optional)

> **Note:** The lengths of `sparse_indices` and `sparse_values` must match. Values in `sparse_indices` must be within [0, sparse_dim).

### Querying with Hybrid Search

Hybrid queries combine dense and sparse vector similarity to rank results. Provide both a dense query vector and sparse query representation.

```python
import numpy as np
import random

np.random.seed(123)
random.seed(123)

DIM = 384
SPARSE_DIM = 30000

# Dense query vector (semantic)
dense_query = np.random.rand(DIM).astype(float).tolist()

# Sparse query (e.g., BM25 scores for query terms)
nnz = 15
sparse_indices = random.sample(range(SPARSE_DIM), nnz)
sparse_values = np.random.rand(nnz).astype(float).tolist()

start = time.perf_counter()

results = index.query(
    vector=dense_query,              # dense part
    sparse_indices=sparse_indices,    # sparse part
    sparse_values=sparse_values,
    top_k=5,
    ef=128,
    include_vectors=True
)

end = time.perf_counter()

# Process results
for result in results:
    print(f"ID: {result['id']}")
    print(f"Similarity: {result['similarity']}")
    print(f"Metadata: {result['meta']}")
    print("---")

print(f"Hybrid query latency: {end - start}s")
```

**Hybrid Query Parameters:**

- `vector`: Dense query vector (required)
- `sparse_indices`: Non-zero term positions in sparse query (required for hybrid)
- `sparse_values`: Weights for sparse query terms (required for hybrid)
- `top_k`: Number of results to return (max 512, default: 10)
- `ef`: Search quality parameter (max 1024, default: 128)
- `include_vectors`: Include vector data in results (default: False)
- `filter`: Optional filter criteria

### Hybrid Search Use Cases

**1. BM25 + Neural Embeddings**
```python
# Combine traditional keyword search (BM25) with semantic embeddings
# sparse_indices: term IDs from BM25
# sparse_values: BM25 scores
# vector: neural embedding from model like BERT
```

**2. SPLADE + Dense Retrieval**
```python
# Use learned sparse representations (SPLADE) with dense embeddings
# sparse_indices/values: SPLADE model output
# vector: dense embedding from same or different model
```

**3. Multi-Signal Ranking**
```python
# Combine multiple ranking signals
# sparse: user behavior signals, click-through rates
# dense: content similarity embedding
```

## Filtered Querying

The `index.query()` method also supports structured filtering using the `filter` parameter. This allows you to restrict search results based on metadata conditions, in addition to vector similarity.

To apply multiple filter conditions, pass an array of filter objects, where each object defines a separate condition. **All filters are combined with logical AND** — meaning a vector must match all specified conditions to be included in the results.

```python
index = client.get_index(name="your-index-name")

# Query with multiple filter conditions (AND logic)
filtered_results = index.query(
    vector=[...],         # Query vector
    top_k=5,              # Number of results to return
    ef=128,               # Runtime parameter for search quality
    include_vectors=True, # Include vector data in results
    filter=[
        {"tags": {"$eq": "important"}},
        {"visibility": {"$eq": "public"}}
    ]
)
```

### Filtering Operators

The `filter` parameter in `index.query()` supports a range of comparison operators to build structured queries. These operators allow you to include or exclude vectors based on metadata or custom fields.

| Operator | Description | Supported Type | Example Usage |
|----------|-------------|----------------|---------------|
| `$eq` | Matches values that are equal | String, Number | `{"status": {"$eq": "published"}}` |
| `$in` | Matches any value in the provided list | String | `{"tags": {"$in": ["ai", "ml"]}}` |
| `$range` | Matches values between a start and end value, inclusive | Number | `{"score": {"$range": [70, 95]}}` |

**Important Notes:**

- Operators are **case-sensitive** and must be prefixed with a `$`
- Filters operate on fields provided under the `filter` key during vector upsert
- The `$range` operator supports values only within the range **[0 – 999]**. If your data exceeds this range (e.g., timestamps, large scores), you should normalize or scale your values to fit within [0, 999] prior to upserting or querying

### Filter Examples

```python
# Equal operator - exact match
filter=[{"status": {"$eq": "published"}}]

# In operator - match any value in list
filter=[{"tags": {"$in": ["ai", "ml", "data-science"]}}]

# Range operator - numeric range (inclusive)
filter=[{"score": {"$range": [70, 95]}}]

# Combined filters (AND logic)
filter=[
    {"status": {"$eq": "published"}},
    {"tags": {"$in": ["ai", "ml"]}},
    {"score": {"$range": [80, 100]}}
]
```

## Deletion Methods

The system supports two types of deletion operations — **vector deletion** and **index deletion**. These allow you to remove specific vectors or entire indexes from your workspace, giving you full control over lifecycle and storage.

### Vector Deletion

Vector deletion is used to remove specific vectors from an index using their unique `id`. This is useful when:

- A document is outdated or revoked
- You want to update a vector by first deleting its old version
- You're cleaning up test data or low-quality entries

```python
from endee.endee import Endee

client = Endee(token="your-token-here")
index = client.get_index(name="your-index-name")

# Delete a single vector by ID
index.delete_vector("vec1")
```

### Filtered Deletion

In cases where you don't know the exact vector `id`, but want to delete vectors based on filter fields, you can use filtered deletion. This is especially useful for:

- Bulk deleting vectors by tag, type, or timestamp
- Enforcing access control or data expiration policies

```python
from endee.endee import Endee

client = Endee(token="your-token-here")
index = client.get_index(name="your-index-name")

# Delete all vectors matching filter conditions
index.delete_with_filter([{"tags": {"$eq": "important"}}])
```

### Index Deletion

Index deletion permanently removes the entire index and all vectors associated with it. This should be used when:

- The index is no longer needed
- You want to re-create the index with a different configuration
- You're managing index rotation in batch pipelines

```python
from endee.endee import Endee

client = Endee(token="your-token-here")

# Delete an entire index
client.delete_index("your-index-name")
```

> ⚠️ **Caution:** Deletion operations are **irreversible**. Ensure you have the correct `id` or index name before performing deletion, especially at the index level.

## Additional Operations

### Get Vector by ID

The `index.get_vector()` method retrieves a specific vector from the index by its unique identifier.

```python
# Retrieve a specific vector by its ID
vector = index.get_vector("vec1")

# The returned object contains:
# - id: Vector identifier
# - meta: Metadata dictionary
# - filter: Filter fields dictionary
# - norm: Vector norm value
# - vector: Vector data array
```

### Describe Index

```python
# Get index statistics and configuration info
info = index.describe()
```

---

## API Reference

### Endee Class

| Method | Description |
|--------|-------------|
| `__init__(token=None)` | Initialize client with optional API token |
| `set_token(token)` | Set or update API token |
| `set_base_url(base_url)` | Set custom API endpoint |
| `create_index(name, dimension, space_type, M, ef_con, precision, sparse_dim)` | Create a new vector index (sparse_dim optional for hybrid) |
| `list_indexes()` | List all indexes in workspace |
| `delete_index(name)` | Delete a vector index |
| `get_index(name, key)` | Get reference to a vector index |
| `get_user()` | Get user management instance |
| `generate_key()` | Generate a secure encryption key for client-side encryption |

### Index Class

| Method | Description |
|--------|-------------|
| `upsert(input_array)` | Insert or update vectors (max 1000 per batch) |
| `query(vector, top_k, filter, ef, include_vectors, sparse_indices, sparse_values)` | Search for similar vectors (sparse params optional for hybrid) |
| `delete_vector(id)` | Delete a vector by ID |
| `delete_with_filter(filter)` | Delete vectors matching a filter |
| `get_vector(id)` | Get a specific vector by ID |
| `describe()` | Get index statistics and configuration |

### User Class

The `User` class provides methods for user management, token generation, and administrative operations. Access it via `client.get_user()`.

| Method | Description |
|--------|-------------|
| `set_token(token)` | Set or update user token |
| `generate_root_token()` | Generate a root token (can only be done once) |
| `create_user(username, root_token)` | Create a new user (requires root token) |
| `delete_user(username)` | Delete a user and all associated data (requires root) |
| `deactivate_user(username)` | Deactivate a user and delete all tokens (requires root) |
| `generate_token(name)` | Generate a new API token for the authenticated user |
| `list_tokens()` | List all tokens for the authenticated user |
| `delete_token(token_name)` | Delete a specific token |
| `get_user_info(username)` | Get detailed information about a user |
| `get_user_type(username)` | Get the user type (Free, Starter, or Pro) |
| `set_user_type(username, user_type)` | Set user type (requires root) |
| `get_all_indices()` | Get list of all indices across all users (requires root) |

## License

MIT License
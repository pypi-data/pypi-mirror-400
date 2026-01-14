# Vector Integration

A comprehensive guide to Timber's vector search integration, explaining how semantic search, embeddings, and vector databases work together to provide powerful content discovery and similarity matching.

---

## Executive Summary

Timber's **vector integration** enables semantic search capabilities through automatic embedding generation and vector database integration. By simply enabling vector search in a model's YAML configuration, Timber automatically generates embeddings for specified content fields and stores them in a vector database, making semantic search and similarity matching trivial to implement.

**Core Innovation:** Configuration-driven vector search + automatic embedding generation + integrated vector storage = Zero-code semantic search.

---

## What is Vector Search?

### Traditional Keyword Search

```sql
-- Traditional SQL search
SELECT * FROM documents 
WHERE content LIKE '%machine learning%'

-- Problems:
-- ❌ Only finds exact matches
-- ❌ Misses synonyms (ML, artificial intelligence)
-- ❌ No understanding of context
-- ❌ Can't find similar concepts
```

**Example:**
- Query: "machine learning"
- Finds: Documents with exact phrase "machine learning"
- Misses: Documents about "neural networks", "deep learning", "AI models"

### Vector/Semantic Search

```python
# Vector search
results = vector_service.search(
    query="machine learning",
    limit=10
)

# Returns:
# ✅ Documents about machine learning
# ✅ Documents about neural networks
# ✅ Documents about deep learning
# ✅ Documents about AI models
# ✅ Ranked by semantic similarity
```

**How it works:**
1. Text → Numerical vector (embedding)
2. Vectors capture semantic meaning
3. Similar concepts = similar vectors
4. Search by vector similarity

---

## Architecture Overview

### Complete Flow

```
┌────────────────────────────────────────────────────┐
│  1. Model Configuration (YAML)                     │
│     vector_search:                                 │
│       enabled: true                                │
│       content_field: content                       │
└────────────────────────────────────────────────────┘
                      │
                      ↓
┌────────────────────────────────────────────────────┐
│  2. Application Creates Record                     │
│     research = Research(content="AI research...")  │
└────────────────────────────────────────────────────┘
                      │
                      ↓
┌────────────────────────────────────────────────────┐
│  3. Feature Orchestrator Intercepts                │
│     • Detects vector_search enabled                │
│     • Triggers embedding generation                │
└────────────────────────────────────────────────────┘
                      │
                      ↓
┌────────────────────────────────────────────────────┐
│  4. Embedding Service                              │
│     • Extracts content text                        │
│     • Generates embedding vector                   │
│     • Uses: BAAI/bge-small-en-v1.5                │
│     • Output: 384-dimensional vector               │
└────────────────────────────────────────────────────┘
                      │
                      ↓
┌────────────────────────────────────────────────────┐
│  5. PostgreSQL Storage                             │
│     • Saves record to table                        │
│     • ID, content, metadata, timestamps            │
└────────────────────────────────────────────────────┘
                      │
                      ↓
┌────────────────────────────────────────────────────┐
│  6. Vector Database Storage                        │
│     • Qdrant/Weaviate/Pinecone                    │
│     • Stores: ID + embedding vector + metadata     │
│     • Indexed for fast similarity search           │
└────────────────────────────────────────────────────┘
                      │
                      ↓
┌────────────────────────────────────────────────────┐
│  7. Search Ready                                   │
│     results = vector_service.search("AI research") │
└────────────────────────────────────────────────────┘
```

### System Components

```
┌──────────────────────────────────────────────────────┐
│              Timber Application Layer                 │
│                                                       │
│  model = Research(content="Financial analysis...")   │
│  session.add(model)                                  │
│  session.commit()  ← Triggers automatic processing   │
└──────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         ↓                                 ↓
┌──────────────────────┐        ┌──────────────────────┐
│  PostgreSQL          │        │  Vector Database     │
│  (Primary Storage)   │        │  (Vector Storage)    │
│                      │        │                      │
│  • ID                │        │  • ID (reference)    │
│  • Content           │        │  • Embedding vector  │
│  • Metadata          │        │  • Metadata copy     │
│  • Timestamps        │        │  • Indexed for       │
│                      │        │    similarity        │
└──────────────────────┘        └──────────────────────┘
         │                                 │
         │                                 │
         └─────────────┬───────────────────┘
                       ↓
         ┌──────────────────────────────────┐
         │    Embedding Model                │
         │    (Sentence Transformer)         │
         │                                   │
         │  BAAI/bge-small-en-v1.5          │
         │  • 384 dimensions                 │
         │  • Fast inference                 │
         │  • Good accuracy                  │
         └──────────────────────────────────┘
```

---

## Configuration

### Enable Vector Search in YAML

```yaml
version: "1.0.0"

models:
  - name: ResearchDocument
    table_name: research_documents
    
    # Enable vector search
    vector_search:
      enabled: true
      content_field: content              # Field to embed
      embedding_model: BAAI/bge-small-en-v1.5
      vector_dimension: 384
      metadata_fields: [title, author, created_at]  # Store with vector
      collection_name: research_docs      # Vector DB collection name
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      
      - name: title
        type: String(255)
        nullable: false
      
      - name: content
        type: Text
        nullable: false
        description: Content that will be embedded for semantic search
      
      - name: author
        type: String(100)
      
      - name: created_at
        type: DateTime
        default: utcnow
```

### Model Configuration Options

```yaml
vector_search:
  # Required
  enabled: true                    # Enable vector search
  content_field: content           # Field to generate embedding from
  
  # Optional
  embedding_model: BAAI/bge-small-en-v1.5  # Embedding model (default)
  vector_dimension: 384            # Vector dimensions (default: 384)
  collection_name: custom_name     # Vector DB collection (default: table_name)
  metadata_fields: [field1, field2] # Fields to store as metadata
  batch_size: 100                  # Batch processing size
  auto_update: true                # Auto-update on content change
  similarity_metric: cosine        # Similarity metric (cosine, euclidean, dot)
```

---

## Vector Search Service

### Core Implementation

```python
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging
from typing import List, Dict, Any, Optional

class VectorSearchService:
    """
    Provides semantic search capabilities via vector embeddings
    
    Features:
    - Automatic embedding generation
    - Vector database integration (Qdrant, Weaviate, Pinecone)
    - Semantic similarity search
    - Hybrid search (vector + keyword)
    """
    
    def __init__(self, vector_store_url: str, 
                 embedding_model: str = 'BAAI/bge-small-en-v1.5'):
        """
        Initialize vector search service
        
        Args:
            vector_store_url: URL of vector database
            embedding_model: Sentence transformer model name
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize embedding model
        self.logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vector_dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize vector store client
        self.logger.info(f"Connecting to vector store: {vector_store_url}")
        self.client = QdrantClient(url=vector_store_url)
        
        # Cache for collections
        self._collections = set()
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            return embedding.tolist()
        
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient)
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embedding_model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=True,
                batch_size=32
            )
            
            return embeddings.tolist()
        
        except Exception as e:
            self.logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    def create_collection(self, collection_name: str, 
                         vector_dimension: int = None,
                         distance: str = 'cosine'):
        """
        Create a collection in vector database
        
        Args:
            collection_name: Name of collection
            vector_dimension: Dimension of vectors (default: model dimension)
            distance: Distance metric (cosine, euclidean, dot)
        """
        if collection_name in self._collections:
            return  # Already exists
        
        try:
            # Map distance metric
            distance_map = {
                'cosine': Distance.COSINE,
                'euclidean': Distance.EUCLID,
                'dot': Distance.DOT
            }
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_dimension or self.vector_dimension,
                    distance=distance_map.get(distance, Distance.COSINE)
                )
            )
            
            self._collections.add(collection_name)
            self.logger.info(f"Created collection: {collection_name}")
        
        except Exception as e:
            if "already exists" not in str(e).lower():
                self.logger.error(f"Failed to create collection: {e}")
                raise
            self._collections.add(collection_name)
    
    def ingest_document(self, model_instance, model_config: dict):
        """
        Automatically ingest document for vector search
        
        Called by feature orchestrator when model has vector_search enabled
        
        Args:
            model_instance: SQLAlchemy model instance
            model_config: Model configuration from YAML
        """
        vector_config = model_config.get('vector_search', {})
        
        if not vector_config.get('enabled'):
            return
        
        try:
            # Extract configuration
            content_field = vector_config['content_field']
            collection_name = vector_config.get(
                'collection_name', 
                model_config['table_name']
            )
            metadata_fields = vector_config.get('metadata_fields', [])
            
            # Get content
            content = getattr(model_instance, content_field, '')
            if not content:
                self.logger.warning(f"No content in {content_field}")
                return
            
            # Ensure collection exists
            self.create_collection(
                collection_name,
                vector_config.get('vector_dimension')
            )
            
            # Generate embedding
            embedding = self.generate_embedding(content)
            
            # Build metadata payload
            payload = {
                'content': content[:1000],  # Store excerpt
                'model_name': model_config['name'],
                'table_name': model_config['table_name']
            }
            
            # Add metadata fields
            for field in metadata_fields:
                value = getattr(model_instance, field, None)
                if value is not None:
                    # Convert datetime to string
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    payload[field] = value
            
            # Store in vector database
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=model_instance.id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            self.logger.info(
                f"Ingested document {model_instance.id} into {collection_name}"
            )
        
        except Exception as e:
            self.logger.error(f"Failed to ingest document: {e}")
            # Don't fail the entire operation if vector ingest fails
    
    def search(self, query: str, collection_name: str,
              limit: int = 10,
              filter_dict: Optional[Dict] = None,
              score_threshold: float = 0.0) -> List[Dict]:
        """
        Semantic search using vector similarity
        
        Args:
            query: Search query text
            collection_name: Collection to search
            limit: Maximum results
            filter_dict: Optional metadata filters
            score_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of search results with scores
        """
        try:
            # Generate query embedding
            query_vector = self.generate_embedding(query)
            
            # Build filter if provided
            search_filter = None
            if filter_dict:
                search_filter = self._build_filter(filter_dict)
            
            # Search vector database
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            self.logger.info(
                f"Search '{query}' in {collection_name}: {len(formatted_results)} results"
            )
            
            return formatted_results
        
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
    
    def find_similar(self, document_id: str, collection_name: str,
                    limit: int = 10) -> List[Dict]:
        """
        Find documents similar to a given document
        
        Args:
            document_id: ID of reference document
            collection_name: Collection name
            limit: Maximum results
        
        Returns:
            List of similar documents
        """
        try:
            # Get document vector
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=[document_id]
            )
            
            if not result:
                raise ValueError(f"Document {document_id} not found")
            
            # Search using document's vector
            similar = self.client.search(
                collection_name=collection_name,
                query_vector=result[0].vector,
                limit=limit + 1  # +1 to exclude self
            )
            
            # Filter out the document itself
            formatted_results = []
            for doc in similar:
                if doc.id != document_id:
                    formatted_results.append({
                        'id': doc.id,
                        'score': doc.score,
                        'payload': doc.payload
                    })
            
            return formatted_results[:limit]
        
        except Exception as e:
            self.logger.error(f"Find similar failed: {e}")
            raise
    
    def hybrid_search(self, query: str, collection_name: str,
                     keyword_boost: float = 0.3,
                     limit: int = 10) -> List[Dict]:
        """
        Hybrid search combining vector and keyword search
        
        Args:
            query: Search query
            collection_name: Collection name
            keyword_boost: Weight for keyword matching (0-1)
            limit: Maximum results
        
        Returns:
            Combined search results
        """
        # Get vector search results
        vector_results = self.search(query, collection_name, limit=limit*2)
        
        # Score boost for keyword matches
        query_words = set(query.lower().split())
        
        for result in vector_results:
            content = result['payload'].get('content', '').lower()
            content_words = set(content.split())
            
            # Calculate keyword overlap
            overlap = len(query_words & content_words) / len(query_words)
            
            # Boost score
            result['score'] = (
                result['score'] * (1 - keyword_boost) +
                overlap * keyword_boost
            )
        
        # Re-sort by boosted score
        vector_results.sort(key=lambda x: x['score'], reverse=True)
        
        return vector_results[:limit]
    
    def update_document(self, document_id: str, collection_name: str,
                       new_content: str,
                       metadata: Optional[Dict] = None):
        """
        Update document embedding and metadata
        
        Args:
            document_id: Document ID
            collection_name: Collection name
            new_content: Updated content
            metadata: Updated metadata
        """
        try:
            # Generate new embedding
            embedding = self.generate_embedding(new_content)
            
            # Build payload
            payload = {
                'content': new_content[:1000]
            }
            if metadata:
                payload.update(metadata)
            
            # Update in vector database
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=document_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            self.logger.info(f"Updated document {document_id}")
        
        except Exception as e:
            self.logger.error(f"Update document failed: {e}")
            raise
    
    def delete_document(self, document_id: str, collection_name: str):
        """
        Delete document from vector database
        
        Args:
            document_id: Document ID
            collection_name: Collection name
        """
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=[document_id]
            )
            
            self.logger.info(f"Deleted document {document_id}")
        
        except Exception as e:
            self.logger.error(f"Delete document failed: {e}")
            raise
    
    def _build_filter(self, filter_dict: Dict) -> Dict:
        """Build Qdrant filter from simple dict"""
        # Example: {'author': 'John', 'year': 2024}
        # Converts to Qdrant filter format
        must_conditions = []
        
        for key, value in filter_dict.items():
            must_conditions.append({
                'key': key,
                'match': {'value': value}
            })
        
        return {
            'must': must_conditions
        }
```

---

## Usage Examples

### Basic Search

```python
from timber.common.services.vector import vector_service

# Simple semantic search
results = vector_service.search(
    query="machine learning algorithms",
    collection_name="research_documents",
    limit=10
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Title: {result['payload']['title']}")
    print(f"Content: {result['payload']['content'][:200]}...")
    print("---")
```

### Find Similar Documents

```python
# Find documents similar to a specific document
similar_docs = vector_service.find_similar(
    document_id="doc-123",
    collection_name="research_documents",
    limit=5
)

print("Documents similar to doc-123:")
for doc in similar_docs:
    print(f"  - {doc['payload']['title']} (score: {doc['score']:.3f})")
```

### Filtered Search

```python
# Search with metadata filters
results = vector_service.search(
    query="financial analysis",
    collection_name="research_documents",
    limit=10,
    filter_dict={
        'author': 'John Doe',
        'year': 2024
    }
)
```

### Hybrid Search

```python
# Combine vector and keyword search
results = vector_service.hybrid_search(
    query="Python programming tutorial",
    collection_name="articles",
    keyword_boost=0.3,  # 30% weight on keyword matching
    limit=10
)
```

---

## Integration with Services

### Research Service with Vector Search

```python
class ResearchService(BaseService):
    """Research service with semantic search"""
    
    def __init__(self, db_manager, vector_service):
        super().__init__(db_manager)
        self.vector = vector_service
    
    def save_research(self, session_id: str, content: dict,
                     research_type: str) -> str:
        """Save research with automatic vector indexing"""
        try:
            Research = self._get_model('ResearchData')
            model_config = self._get_model_config(Research)
            
            with self.db.session_scope() as session:
                # Create research record
                research = Research(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    research_type=research_type,
                    content=content
                )
                
                session.add(research)
                session.commit()
                
                # Auto-ingest for vector search (if enabled)
                self.vector.ingest_document(research, model_config)
                
                return research.id
        
        except Exception as e:
            self._handle_error(e, "Failed to save research")
    
    def search_research(self, query: str, 
                       research_type: Optional[str] = None,
                       limit: int = 10) -> List[Dict]:
        """
        Semantic search across research documents
        
        Args:
            query: Search query
            research_type: Optional type filter
            limit: Maximum results
        
        Returns:
            List of research results with scores
        """
        try:
            # Build filter
            filter_dict = {}
            if research_type:
                filter_dict['research_type'] = research_type
            
            # Vector search
            vector_results = self.vector.search(
                query=query,
                collection_name='research_data',
                limit=limit,
                filter_dict=filter_dict if filter_dict else None
            )
            
            # Fetch full records from PostgreSQL
            result_ids = [r['id'] for r in vector_results]
            
            Research = self._get_model('ResearchData')
            with self.db.session_scope() as session:
                records = session.query(Research)\
                    .filter(Research.id.in_(result_ids))\
                    .all()
            
            # Combine vector scores with full records
            results = []
            score_map = {r['id']: r['score'] for r in vector_results}
            
            for record in records:
                results.append({
                    'research': record,
                    'similarity_score': score_map[record.id]
                })
            
            # Sort by score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return results
        
        except Exception as e:
            self._handle_error(e, "Research search failed")
```

---

## Embedding Models

### Available Models

```python
# Small, fast models (good for most use cases)
'BAAI/bge-small-en-v1.5'      # 384 dims, English
'sentence-transformers/all-MiniLM-L6-v2'  # 384 dims

# Medium models (better accuracy)
'BAAI/bge-base-en-v1.5'       # 768 dims, English
'sentence-transformers/all-mpnet-base-v2'  # 768 dims

# Large models (best accuracy, slower)
'BAAI/bge-large-en-v1.5'      # 1024 dims, English
'sentence-transformers/all-roberta-large-v1'  # 1024 dims

# Multilingual models
'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'  # 384 dims
'BAAI/bge-m3'                 # Multilingual, 1024 dims
```

### Model Selection Guide

```
Use Case                  | Recommended Model           | Dimensions
──────────────────────────|────────────────────────────|───────────
General purpose (English) | BAAI/bge-small-en-v1.5     | 384
High accuracy needed      | BAAI/bge-large-en-v1.5     | 1024
Multilingual              | paraphrase-multilingual... | 384
Production (speed)        | all-MiniLM-L6-v2          | 384
Production (accuracy)     | all-mpnet-base-v2         | 768
```

### Custom Model Configuration

```yaml
models:
  - name: Document
    vector_search:
      enabled: true
      embedding_model: BAAI/bge-large-en-v1.5  # Custom model
      vector_dimension: 1024                    # Match model dims
```

---

## Vector Databases

### Qdrant (Recommended)

```python
# Setup Qdrant
from qdrant_client import QdrantClient

client = QdrantClient(
    url="http://localhost:6333",
    # Or hosted:
    # url="https://xxx.qdrant.io",
    # api_key="your-api-key"
)

# Features:
# ✅ Open source
# ✅ Fast performance
# ✅ Rich filtering
# ✅ Easy deployment
# ✅ Python SDK
```

### Weaviate

```python
# Setup Weaviate
import weaviate

client = weaviate.Client(
    url="http://localhost:8080",
    # Or hosted:
    # url="https://xxx.weaviate.network",
    # auth_client_secret=weaviate.AuthApiKey(api_key="key")
)

# Features:
# ✅ GraphQL API
# ✅ Schema-based
# ✅ Hybrid search built-in
# ✅ Good documentation
```

### Pinecone

```python
# Setup Pinecone
import pinecone

pinecone.init(
    api_key="your-api-key",
    environment="us-west1-gcp"
)

# Features:
# ✅ Fully managed
# ✅ Highly scalable
# ✅ Simple API
# ❌ Paid service only
```

---

## Performance Optimization

### Batch Ingestion

```python
# Bad: One at a time
for document in documents:
    vector_service.ingest_document(document, model_config)
    # Slow! Each embedding computed separately

# Good: Batch processing
def batch_ingest_documents(documents, model_config, batch_size=100):
    """Ingest documents in batches"""
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        
        # Extract content
        contents = [getattr(doc, config['content_field']) 
                   for doc in batch]
        
        # Generate embeddings in batch (faster)
        embeddings = vector_service.generate_embeddings_batch(contents)
        
        # Upsert batch
        points = [
            PointStruct(
                id=doc.id,
                vector=embedding,
                payload={...}
            )
            for doc, embedding in zip(batch, embeddings)
        ]
        
        vector_service.client.upsert(
            collection_name=collection_name,
            points=points
        )
```

### Caching Embeddings

```python
class CachedVectorService(VectorSearchService):
    """Vector service with embedding cache"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embedding_cache = {}
    
    def generate_embedding(self, text: str):
        """Generate embedding with caching"""
        # Create cache key
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Generate and cache
        embedding = super().generate_embedding(text)
        self.embedding_cache[cache_key] = embedding
        
        return embedding
```

### Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncVectorService(VectorSearchService):
    """Vector service with async processing"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def ingest_document_async(self, model_instance, model_config):
        """Ingest document asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run in thread pool
        await loop.run_in_executor(
            self.executor,
            self.ingest_document,
            model_instance,
            model_config
        )
    
    async def search_async(self, query: str, collection_name: str, **kwargs):
        """Search asynchronously"""
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            self.executor,
            self.search,
            query,
            collection_name,
            **kwargs
        )
```

---

## Best Practices

### 1. Content Preparation

```python
# Good: Clean content before embedding
def prepare_content_for_embedding(content: str) -> str:
    """Prepare content for optimal embedding"""
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Remove excessive whitespace
    content = ' '.join(content.split())
    
    # Truncate if very long (models have token limits)
    max_tokens = 512
    content = content[:max_tokens * 4]  # Rough char estimate
    
    return content

# Use in model
columns:
  - name: content
    type: Text
  
  - name: embedding_content  # Cleaned version for embedding
    type: Text
    computed: true
    expression: "prepare_content_for_embedding(content)"
```

### 2. Metadata Strategy

```yaml
# Store useful metadata for filtering
vector_search:
  enabled: true
  content_field: content
  metadata_fields:
    - title
    - author
    - category
    - created_at
    - tags           # Array field for multi-tag filtering
    - language
    - word_count
```

### 3. Similarity Thresholds

```python
# Set appropriate score thresholds
results = vector_service.search(
    query="...",
    collection_name="...",
    score_threshold=0.7  # Only return highly similar results
)

# Threshold guidelines:
# 0.9+ : Nearly identical
# 0.8-0.9 : Very similar
# 0.7-0.8 : Similar
# 0.6-0.7 : Somewhat related
# < 0.6 : Weakly related
```

### 4. Update Strategy

```python
# Update embeddings when content changes
def update_research(research_id: str, new_content: dict):
    """Update research and embedding"""
    Research = get_model('ResearchData')
    
    with db_manager.session_scope() as session:
        research = session.query(Research).get(research_id)
        research.content = new_content
        session.commit()
        
        # Update vector
        vector_service.update_document(
            document_id=research_id,
            collection_name='research_data',
            new_content=str(new_content),
            metadata={'updated_at': datetime.utcnow().isoformat()}
        )
```

### 5. Monitoring

```python
# Track vector service metrics
class MonitoredVectorService(VectorSearchService):
    
    def search(self, *args, **kwargs):
        start_time = time.time()
        
        try:
            results = super().search(*args, **kwargs)
            
            # Log metrics
            duration = time.time() - start_time
            self.logger.info(f"Search completed in {duration:.3f}s")
            
            # Track in metrics system
            metrics.histogram('vector_search_duration', duration)
            metrics.counter('vector_search_count').inc()
            
            return results
        
        except Exception as e:
            metrics.counter('vector_search_errors').inc()
            raise
```

---

## Testing Vector Search

### Unit Tests

```python
import pytest
from unittest.mock import MagicMock

def test_generate_embedding():
    """Test embedding generation"""
    service = VectorSearchService(...)
    
    embedding = service.generate_embedding("test content")
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384  # BAAI/bge-small dimension
    assert all(isinstance(x, float) for x in embedding)

def test_ingest_document(mock_model_instance):
    """Test document ingestion"""
    service = VectorSearchService(...)
    
    # Mock configuration
    config = {
        'vector_search': {
            'enabled': True,
            'content_field': 'content'
        },
        'table_name': 'test_table'
    }
    
    # Should not raise
    service.ingest_document(mock_model_instance, config)
```

### Integration Tests

```python
@pytest.fixture
def vector_service():
    """Setup vector service with test database"""
    # Use in-memory Qdrant for testing
    from qdrant_client import QdrantClient
    
    client = QdrantClient(":memory:")
    service = VectorSearchService(
        vector_store_url=":memory:",
        embedding_model='BAAI/bge-small-en-v1.5'
    )
    
    yield service

def test_search_integration(vector_service):
    """Test complete search workflow"""
    collection_name = "test_docs"
    
    # Create collection
    vector_service.create_collection(collection_name)
    
    # Ingest documents
    docs = [
        {"id": "1", "content": "Machine learning algorithms"},
        {"id": "2", "content": "Deep neural networks"},
        {"id": "3", "content": "Natural language processing"}
    ]
    
    for doc in docs:
        embedding = vector_service.generate_embedding(doc["content"])
        vector_service.client.upsert(
            collection_name=collection_name,
            points=[PointStruct(
                id=doc["id"],
                vector=embedding,
                payload=doc
            )]
        )
    
    # Search
    results = vector_service.search(
        query="artificial intelligence",
        collection_name=collection_name,
        limit=3
    )
    
    # Verify
    assert len(results) > 0
    assert results[0]['score'] > 0.5
```

---

## Troubleshooting

### Issue: Slow Embedding Generation

```python
# Problem: Embeddings taking too long

# Solution 1: Use smaller model
vector_search:
  embedding_model: sentence-transformers/all-MiniLM-L6-v2  # Faster

# Solution 2: Batch processing
embeddings = vector_service.generate_embeddings_batch(texts)  # Much faster

# Solution 3: GPU acceleration
embedding_model = SentenceTransformer('model-name', device='cuda')
```

### Issue: Poor Search Results

```python
# Problem: Search not finding relevant documents

# Solution 1: Check content quality
# Make sure content is clean, not too short/long

# Solution 2: Try different similarity threshold
results = vector_service.search(..., score_threshold=0.6)  # Lower threshold

# Solution 3: Use hybrid search
results = vector_service.hybrid_search(...)  # Combines vector + keyword
```

### Issue: Memory Usage

```python
# Problem: Vector service using too much memory

# Solution 1: Clear embedding cache periodically
vector_service.embedding_cache.clear()

# Solution 2: Use smaller model
# BAAI/bge-small-en-v1.5 (384 dims) vs bge-large (1024 dims)

# Solution 3: Process in batches
for batch in chunks(documents, 100):
    process_batch(batch)
    # Memory released between batches
```

---

## Summary

Timber's vector integration provides:

1. **Zero-Code Setup:** Enable in YAML, automatic embedding generation
2. **Multiple Backends:** Qdrant, Weaviate, Pinecone support
3. **Semantic Search:** Find content by meaning, not just keywords
4. **Similarity Matching:** Find related documents automatically
5. **Hybrid Search:** Combine vector and keyword search
6. **Production Ready:** Batching, caching, async processing

**Key Benefits:**
- Semantic search with one line of YAML
- Automatic embedding generation and storage
- Flexible vector database backends
- High performance with optimization options
- Easy to test and monitor

---

## Next Steps

- **[System Architecture](01_system_architecture.md)** - Overall design
- **[Config-Driven Models](02_config_driven_models.md)** - Model configuration
- **[Persistence Layer](03_persistence_layer.md)** - Database architecture
- **[Multi-App Support](05_multi_app_support.md)** - Supporting multiple applications

---

**Last Updated:** October 19, 2024  
**Version:** 0.2.0  
**Authors:** Timber Architecture Team
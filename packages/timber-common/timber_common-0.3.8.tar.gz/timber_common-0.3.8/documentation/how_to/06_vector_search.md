# Vector Search in Timber

**Complete guide to semantic search, embeddings, and vector database integration**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Vector Database Architecture](#vector-database-architecture)
4. [Embedding Generation](#embedding-generation)
5. [Search Operations](#search-operations)
6. [Data Ingestion](#data-ingestion)
7. [Advanced Patterns](#advanced-patterns)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Timber provides seamless integration with pgvector for semantic search capabilities. The system automatically manages embeddings, supports multiple embedding models, and provides optimized search operations.

### Key Features

- **Automatic Ingestion**: Models marked as searchable auto-ingest to vector DB
- **Multi-Model Support**: FastEmbed, OpenAI, or custom embeddings
- **Optimized Storage**: Two-table strategy for fast filtered searches
- **Metadata Filtering**: Search within specific contexts (ticker, sector, user)
- **Batch Operations**: Efficient bulk embedding generation
- **Hybrid Search**: Combine vector similarity with metadata filters

### When to Use Vector Search

**Great For:**
- Finding similar research notes
- Semantic document search
- Content recommendation
- Question answering systems
- Duplicate detection
- Theme/topic clustering

**Not Ideal For:**
- Exact keyword matching (use full-text search)
- Structured data queries (use SQL)
- Real-time updates (embeddings take time)
- Very small datasets (<1000 records)

---

## Quick Start

### Step 1: Enable pgvector

```sql
-- PostgreSQL with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Step 2: Initialize Timber with Vector Support

```python
from timber.common import initialize_timber

initialize_timber(
    model_config_dirs=['./data/models'],
    enable_auto_vector_ingestion=True,  # âœ… Enable automatic ingestion
    vector_config={
        'embedding_model': 'BAAI/bge-small-en-v1.5',  # FastEmbed model
        'embedding_dim': 384,  # Model dimension
        'batch_size': 32  # Batch size for generation
    }
)
```

### Step 3: Mark Models as Searchable

```yaml
# data/models/research_models.yaml
models:
  - name: ResearchNote
    table_name: research_notes
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: ticker
        type: String(20)
        nullable: false
      
      - name: content
        type: Text
        nullable: false
      
      - name: summary
        type: Text
      
      - name: user_id
        type: String(36)
    
    mixins:
      - TimestampMixin
      - SearchableMixin  # âœ… Enable vector search
    
    search_config:
      # Fields to embed and search
      searchable_fields:
        - content
        - summary
      
      # Metadata for filtering
      metadata_fields:
        - ticker
        - user_id
      
      # How to combine fields for embedding
      content_template: "Ticker: {ticker}\n\nContent: {content}\n\nSummary: {summary}"
```

### Step 4: Create and Search

```python
from timber.common.models import get_model
from timber.common.services.vector import vector_search_service
from timber.common.services.db_service import db_service

ResearchNote = get_model('ResearchNote')

# Create note - automatically ingested to vector DB
with db_service.session_scope() as session:
    note = ResearchNote(
        ticker='AAPL',
        content='Apple shows strong momentum with innovation in AI and services.',
        summary='Bullish on AAPL due to AI growth',
        user_id='user-123'
    )
    session.add(note)
    session.commit()

# Search semantically
results = vector_search_service.search(
    query="artificial intelligence opportunities",
    source_type='research_notes',
    limit=10,
    filters={'ticker': 'AAPL'}  # Optional metadata filter
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Metadata: {result['metadata']}")
    print("---")
```

---

## Vector Database Architecture

### Two-Table Strategy

Timber uses an optimized two-table architecture for vector storage:

```
┌─────────────────────────────────────────────┐
│         text_embeddings                     │
├─────────────────────────────────────────────┤
│ id (UUID)                                   │
│ content_text (TEXT)                         │
│ embedding (VECTOR(384))   â† Vector column │
│ source_type (VARCHAR)                       │
│ source_id (VARCHAR)                         │
│ created_at (TIMESTAMP)                      │
│ updated_at (TIMESTAMP)                      │
└─────────────────────────────────────────────┘
          ↓ 1:1 relationship
┌─────────────────────────────────────────────┐
│      embedding_metadata                     │
├─────────────────────────────────────────────┤
│ embedding_id (UUID) FK                      │
│ ticker (VARCHAR)                            │
│ sector (VARCHAR)                            │
│ user_id (VARCHAR)                           │
│ session_id (VARCHAR)                        │
│ metadata (JSONB)                            │
│ is_encrypted (BOOLEAN)                      │
└─────────────────────────────────────────────┘
```

**Benefits:**
- â Fast metadata filtering without scanning vectors
- â Smaller vector index for better performance
- â Easy GDPR compliance (delete by user_id)
- â Flexible metadata storage

### Database Schema

```sql
-- Main embeddings table
CREATE TABLE text_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_text TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,  -- Dimension depends on model
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT text_embeddings_source_unique UNIQUE (source_type, source_id)
);

-- Metadata table
CREATE TABLE embedding_metadata (
    embedding_id UUID PRIMARY KEY REFERENCES text_embeddings(id) ON DELETE CASCADE,
    ticker VARCHAR(20),
    index_symbol VARCHAR(20),
    sector VARCHAR(100),
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    metadata JSONB,
    is_encrypted BOOLEAN DEFAULT FALSE,
    
    -- Indexes for fast filtering
    CONSTRAINT embedding_metadata_embedding_fk 
        FOREIGN KEY (embedding_id) 
        REFERENCES text_embeddings(id) 
        ON DELETE CASCADE
);

-- Performance indexes
CREATE INDEX idx_embeddings_source ON text_embeddings(source_type, source_id);
CREATE INDEX idx_embeddings_created ON text_embeddings(created_at DESC);
CREATE INDEX idx_metadata_ticker ON embedding_metadata(ticker);
CREATE INDEX idx_metadata_sector ON embedding_metadata(sector);
CREATE INDEX idx_metadata_user ON embedding_metadata(user_id);
CREATE INDEX idx_metadata_session ON embedding_metadata(session_id);
CREATE INDEX idx_metadata_jsonb ON embedding_metadata USING gin(metadata);

-- Vector similarity index (HNSW for best performance)
CREATE INDEX idx_embeddings_vector_hnsw ON text_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Alternative: IVFFlat (faster build, slower search)
-- CREATE INDEX idx_embeddings_vector_ivf ON text_embeddings 
-- USING ivfflat (embedding vector_cosine_ops) 
-- WITH (lists = 100);
```

### Index Selection

**HNSW (Hierarchical Navigable Small World):**
- âœ… Best search performance
- âœ… Good for < 1M vectors
- â Slower index build
- â Higher memory usage

```sql
CREATE INDEX idx_embeddings_hnsw ON text_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,              -- Max connections per layer (default: 16)
    ef_construction = 64 -- Size of dynamic candidate list (default: 64)
);
```

**IVFFlat (Inverted File Flat):**
- âœ… Faster index build
- âœ… Lower memory usage
- âœ… Good for > 1M vectors
- â Requires training
- â Slightly slower search

```sql
CREATE INDEX idx_embeddings_ivf ON text_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);  -- Number of clusters

-- Must analyze after creation
ANALYZE text_embeddings;
```

---

## Embedding Generation

### FastEmbed Integration

Timber uses FastEmbed by default for fast, local embeddings:

```python
from timber.common.services.vector import embedding_service

# Generate single embedding
text = "Apple shows strong growth in services revenue"
embedding = embedding_service.generate_embedding(text)

print(f"Embedding dimension: {len(embedding)}")  # 384 for bge-small
print(f"First values: {embedding[:5]}")

# Generate batch
texts = [
    "Strong buy recommendation for tech sector",
    "Market showing bearish signals",
    "Neutral outlook on financial stocks"
]

embeddings = embedding_service.generate_embeddings_batch(texts)
print(f"Generated {len(embeddings)} embeddings")
```

### Supported Models

```python
# Configure in initialization
initialize_timber(
    vector_config={
        # FastEmbed models (default)
        'embedding_model': 'BAAI/bge-small-en-v1.5',  # 384 dim, fast
        # 'embedding_model': 'BAAI/bge-base-en-v1.5',  # 768 dim, better quality
        # 'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',  # 384 dim
        
        'embedding_dim': 384,  # Must match model
        'batch_size': 32
    }
)
```

**Model Comparison:**

| Model | Dimension | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| bge-small-en-v1.5 | 384 | âš¡âš¡âš¡ | ⭐⭐⭐ | General purpose |
| bge-base-en-v1.5 | 768 | âš¡âš¡ | ⭐⭐⭐⭐ | Better accuracy |
| all-MiniLM-L6-v2 | 384 | âš¡âš¡âš¡ | ⭐⭐ | Fast retrieval |

### OpenAI Embeddings

For OpenAI's ada-002 model:

```python
from timber.common.services.vector import OpenAIEmbeddingService

# Configure OpenAI service
openai_service = OpenAIEmbeddingService(
    api_key=config.OPENAI_API_KEY,
    model='text-embedding-ada-002'  # 1536 dimensions
)

# Use in vector service
vector_search_service.embedding_service = openai_service
```

### Custom Embedding Models

Implement your own embedding service:

```python
from timber.common.services.vector.base import BaseEmbeddingService
from typing import List
import numpy as np

class CustomEmbeddingService(BaseEmbeddingService):
    """Custom embedding service implementation."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        # Load your model
        self.model = self._load_model()
    
    def _load_model(self):
        """Load your custom model."""
        # Implementation depends on your model
        pass
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate single embedding."""
        # Your implementation
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def generate_embeddings_batch(
        self, 
        texts: List[str]
    ) -> List[List[float]]:
        """Generate batch embeddings."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Return embedding dimension."""
        return self.model.get_sentence_embedding_dimension()

# Use custom service
custom_service = CustomEmbeddingService('my-model')
vector_search_service.embedding_service = custom_service
```

---

## Search Operations

### Basic Semantic Search

```python
from timber.common.services.vector import vector_search_service

# Simple search
results = vector_search_service.search(
    query="companies with strong AI capabilities",
    source_type='research_notes',
    limit=10
)

for result in results:
    print(f"{result['score']:.3f}: {result['content'][:100]}")
```

### Search with Metadata Filters

```python
# Filter by ticker
results = vector_search_service.search(
    query="growth potential in cloud computing",
    source_type='research_notes',
    limit=10,
    filters={
        'ticker': 'MSFT',  # Only Microsoft research
        'sector': 'Technology'
    }
)

# Filter by user
user_results = vector_search_service.search(
    query="dividend stocks",
    source_type='research_notes',
    filters={'user_id': 'user-123'}
)

# Multiple filters
filtered_results = vector_search_service.search(
    query="risk assessment",
    source_type='research_notes',
    filters={
        'ticker': ['AAPL', 'MSFT', 'GOOGL'],  # Multiple tickers
        'sector': 'Technology',
        'user_id': 'user-123'
    },
    min_score=0.7  # Minimum similarity threshold
)
```

### Advanced Search Options

```python
# Custom similarity threshold
high_quality_results = vector_search_service.search(
    query="market analysis",
    source_type='research_notes',
    limit=20,
    min_score=0.8  # Only very similar results
)

# Time-based filtering
from datetime import datetime, timedelta

recent_results = vector_search_service.search(
    query="quarterly earnings",
    source_type='research_notes',
    filters={
        'created_after': datetime.now() - timedelta(days=30)
    }
)

# Exclude certain results
results = vector_search_service.search(
    query="investment strategies",
    source_type='research_notes',
    exclude_ids=['id-1', 'id-2']  # Exclude specific embeddings
)
```

### Multi-Source Search

Search across different content types:

```python
# Search across multiple sources
def search_all_content(query: str, user_id: str):
    """Search across all user's content."""
    
    # Search research notes
    research_results = vector_search_service.search(
        query=query,
        source_type='research_notes',
        filters={'user_id': user_id},
        limit=5
    )
    
    # Search session summaries
    session_results = vector_search_service.search(
        query=query,
        source_type='research_sessions',
        filters={'user_id': user_id},
        limit=5
    )
    
    # Search analysis reports
    analysis_results = vector_search_service.search(
        query=query,
        source_type='analysis_reports',
        filters={'user_id': user_id},
        limit=5
    )
    
    # Combine and rank by score
    all_results = (
        research_results + 
        session_results + 
        analysis_results
    )
    
    # Sort by similarity score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    return all_results[:15]  # Top 15 across all sources
```

### Similarity Search Between Documents

Find documents similar to a given document:

```python
def find_similar_research(research_id: str, limit: int = 10):
    """Find research notes similar to a given note."""
    ResearchNote = get_model('ResearchNote')
    
    # Get source document
    with db_service.session_scope() as session:
        source = session.query(ResearchNote)\
            .filter_by(id=research_id)\
            .first()
        
        if not source:
            return []
        
        # Use document content as query
        query_text = f"{source.content} {source.summary}"
    
    # Search for similar
    similar = vector_search_service.search(
        query=query_text,
        source_type='research_notes',
        limit=limit + 1,  # +1 to exclude self
        exclude_ids=[research_id]  # Exclude source document
    )
    
    return similar
```

---

## Data Ingestion

### Automatic Ingestion

Models with `SearchableMixin` auto-ingest on create/update:

```python
from timber.common.models import get_model

ResearchNote = get_model('ResearchNote')

# Create - automatically ingested
with db_service.session_scope() as session:
    note = ResearchNote(
        ticker='TSLA',
        content='Tesla showing strong delivery numbers for Q4',
        summary='Bullish on TSLA'
    )
    session.add(note)
    session.commit()
    # âœ… Embedding automatically created

# Update - embedding refreshed
with db_service.session_scope() as session:
    note = session.query(ResearchNote).filter_by(ticker='TSLA').first()
    note.content = 'Updated: Tesla exceeds delivery expectations'
    session.commit()
    # âœ… Embedding automatically updated
```

### Manual Ingestion

Manually ingest existing data:

```python
from timber.common.services.vector import vector_ingestion_service

# Ingest single document
embedding_id = vector_ingestion_service.ingest_document(
    content="Strong technical indicators for AAPL",
    source_type='research_notes',
    source_id='note-123',
    metadata={
        'ticker': 'AAPL',
        'user_id': 'user-123',
        'sector': 'Technology'
    }
)

print(f"Created embedding: {embedding_id}")
```

### Batch Ingestion

Efficiently ingest large datasets:

```python
def batch_ingest_research_notes():
    """Batch ingest all research notes."""
    ResearchNote = get_model('ResearchNote')
    
    with db_service.session_scope() as session:
        notes = session.query(ResearchNote).all()
        
        # Prepare documents for batch ingestion
        documents = []
        for note in notes:
            documents.append({
                'content': f"{note.content}\n\n{note.summary}",
                'source_type': 'research_notes',
                'source_id': note.id,
                'metadata': {
                    'ticker': note.ticker,
                    'user_id': note.user_id,
                    'created_at': note.created_at.isoformat()
                }
            })
        
        # Batch ingest
        results = vector_ingestion_service.ingest_documents_batch(
            documents,
            batch_size=50  # Process 50 at a time
        )
        
        print(f"âœ… Ingested {len(results)} documents")
        print(f"â Failed: {sum(1 for r in results if r['error'])}")

# Run batch ingestion
batch_ingest_research_notes()
```

### Progressive Ingestion

For very large datasets, use progressive ingestion:

```python
def progressive_ingest(source_type: str, batch_size: int = 100):
    """
    Progressively ingest documents with progress tracking.
    """
    Model = get_model(source_type)
    
    with db_service.session_scope() as session:
        # Get total count
        total = session.query(Model).count()
        
        print(f"Ingesting {total} {source_type} documents...")
        
        # Process in batches
        offset = 0
        ingested = 0
        
        while offset < total:
            # Get batch
            batch = session.query(Model)\
                .offset(offset)\
                .limit(batch_size)\
                .all()
            
            # Prepare documents
            documents = [
                {
                    'content': prepare_content(doc),
                    'source_type': source_type,
                    'source_id': doc.id,
                    'metadata': extract_metadata(doc)
                }
                for doc in batch
            ]
            
            # Ingest batch
            results = vector_ingestion_service.ingest_documents_batch(
                documents,
                batch_size=batch_size
            )
            
            ingested += len(results)
            offset += batch_size
            
            # Progress update
            progress = (ingested / total) * 100
            print(f"Progress: {progress:.1f}% ({ingested}/{total})")
        
        print(f"âœ… Completed ingestion of {ingested} documents")
```

### Selective Ingestion

Ingest only specific records:

```python
def ingest_recent_research(days: int = 30):
    """Ingest only recent research notes."""
    from datetime import datetime, timedelta
    
    ResearchNote = get_model('ResearchNote')
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with db_service.session_scope() as session:
        recent_notes = session.query(ResearchNote)\
            .filter(ResearchNote.created_at >= cutoff_date)\
            .all()
        
        documents = []
        for note in recent_notes:
            documents.append({
                'content': f"{note.content}\n\n{note.summary}",
                'source_type': 'research_notes',
                'source_id': note.id,
                'metadata': {
                    'ticker': note.ticker,
                    'user_id': note.user_id
                }
            })
        
        results = vector_ingestion_service.ingest_documents_batch(documents)
        print(f"Ingested {len(results)} recent notes")
```

---

## Advanced Patterns

### Hybrid Search (Vector + Keyword)

Combine semantic and keyword search:

```python
def hybrid_search(
    query: str,
    source_type: str,
    keywords: List[str] = None,
    limit: int = 10
):
    """
    Hybrid search combining vector similarity and keyword matching.
    """
    # Vector search
    vector_results = vector_search_service.search(
        query=query,
        source_type=source_type,
        limit=limit * 2  # Get more for re-ranking
    )
    
    # Keyword filtering
    if keywords:
        filtered_results = []
        for result in vector_results:
            content_lower = result['content'].lower()
            if any(kw.lower() in content_lower for kw in keywords):
                filtered_results.append(result)
        
        return filtered_results[:limit]
    
    return vector_results[:limit]

# Usage
results = hybrid_search(
    query="growth stocks",
    source_type='research_notes',
    keywords=['technology', 'innovation', 'AI'],
    limit=10
)
```

### Contextual Search

Search with conversation context:

```python
class ConversationalSearch:
    """Maintain conversation context for better search."""
    
    def __init__(self):
        self.conversation_history = []
    
    def search_with_context(
        self,
        query: str,
        source_type: str,
        limit: int = 10
    ):
        """Search considering conversation history."""
        
        # Build contextualized query
        if self.conversation_history:
            # Include recent context
            recent_context = " ".join(self.conversation_history[-3:])
            contextualized_query = f"{recent_context} {query}"
        else:
            contextualized_query = query
        
        # Search
        results = vector_search_service.search(
            query=contextualized_query,
            source_type=source_type,
            limit=limit
        )
        
        # Update history
        self.conversation_history.append(query)
        
        return results
    
    def clear_context(self):
        """Clear conversation history."""
        self.conversation_history = []

# Usage
conv_search = ConversationalSearch()

# First query
results1 = conv_search.search_with_context(
    "technology stocks",
    "research_notes"
)

# Follow-up query with context
results2 = conv_search.search_with_context(
    "which ones have good dividends?",  # Context: technology stocks
    "research_notes"
)
```

### Multi-Modal Search

Search with different content types:

```python
def multi_modal_search(
    text_query: str = None,
    image_query: str = None,
    source_type: str = 'research_notes',
    limit: int = 10
):
    """
    Search using multiple modalities.
    
    Note: Requires multi-modal embedding model.
    """
    results = []
    
    # Text search
    if text_query:
        text_results = vector_search_service.search(
            query=text_query,
            source_type=source_type,
            limit=limit
        )
        results.extend(text_results)
    
    # Image search (if supported)
    if image_query:
        # Generate embedding from image
        image_embedding = generate_image_embedding(image_query)
        
        # Search using embedding directly
        image_results = vector_search_service.search_by_embedding(
            embedding=image_embedding,
            source_type=source_type,
            limit=limit
        )
        results.extend(image_results)
    
    # De-duplicate and re-rank
    seen = set()
    unique_results = []
    for r in sorted(results, key=lambda x: x['score'], reverse=True):
        if r['id'] not in seen:
            seen.add(r['id'])
            unique_results.append(r)
    
    return unique_results[:limit]
```

### Clustering and Topic Discovery

Find themes in your content:

```python
from sklearn.cluster import KMeans
import numpy as np

def discover_topics(source_type: str, n_clusters: int = 5):
    """
    Discover topics using clustering on embeddings.
    """
    # Get all embeddings
    with db_service.session_scope() as session:
        embeddings_data = session.execute(
            """
            SELECT e.id, e.content_text, e.embedding, m.metadata
            FROM text_embeddings e
            JOIN embedding_metadata m ON e.id = m.embedding_id
            WHERE e.source_type = :source_type
            """,
            {'source_type': source_type}
        ).fetchall()
    
    # Convert to numpy array
    embeddings = np.array([
        list(map(float, row[2][1:-1].split(',')))
        for row in embeddings_data
    ])
    
    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    
    # Organize by cluster
    topics = {i: [] for i in range(n_clusters)}
    for idx, cluster_id in enumerate(clusters):
        topics[cluster_id].append({
            'id': embeddings_data[idx][0],
            'content': embeddings_data[idx][1],
            'metadata': embeddings_data[idx][3]
        })
    
    return topics

# Discover topics
topics = discover_topics('research_notes', n_clusters=5)

for topic_id, documents in topics.items():
    print(f"\nTopic {topic_id} ({len(documents)} documents):")
    for doc in documents[:3]:  # Show top 3
        print(f"  - {doc['content'][:100]}...")
```

---

## Performance Optimization

### Index Tuning

**HNSW Parameters:**

```sql
-- Balanced (default)
CREATE INDEX idx_embeddings_balanced ON text_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- High quality (slower build, better search)
CREATE INDEX idx_embeddings_quality ON text_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128);

-- Fast build (faster build, acceptable search)
CREATE INDEX idx_embeddings_fast ON text_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 8, ef_construction = 32);
```

**IVFFlat Parameters:**

```sql
-- Small dataset (< 10K vectors)
CREATE INDEX idx_embeddings_small ON text_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 10);

-- Medium dataset (10K - 100K vectors)
CREATE INDEX idx_embeddings_medium ON text_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Large dataset (> 100K vectors)
CREATE INDEX idx_embeddings_large ON text_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 1000);
```

### Query Optimization

```python
# Use metadata filters to reduce search space
fast_results = vector_search_service.search(
    query="AI investment opportunities",
    source_type='research_notes',
    filters={
        'sector': 'Technology',  # âœ… Filter first
        'user_id': 'user-123'
    },
    limit=10
)

# Adjust limit for better performance
# Lower limit = faster search
quick_results = vector_search_service.search(
    query="market trends",
    source_type='research_notes',
    limit=5  # âœ… Only get top 5
)
```

### Caching Strategy

Cache frequent searches:

```python
from functools import lru_cache
from hashlib import md5

@lru_cache(maxsize=1000)
def cached_search(query_hash: str, source_type: str, limit: int):
    """Cache search results."""
    # This function signature is cacheable
    # Actual query passed separately
    pass

def search_with_cache(
    query: str,
    source_type: str,
    limit: int = 10,
    filters: dict = None
):
    """Search with caching."""
    # Create cache key
    cache_key = md5(
        f"{query}:{source_type}:{limit}:{filters}".encode()
    ).hexdigest()
    
    # Check Redis cache
    cached = redis_client.get(f"search:{cache_key}")
    if cached:
        return json.loads(cached)
    
    # Perform search
    results = vector_search_service.search(
        query=query,
        source_type=source_type,
        limit=limit,
        filters=filters
    )
    
    # Cache for 5 minutes
    redis_client.setex(
        f"search:{cache_key}",
        300,  # 5 minutes
        json.dumps(results)
    )
    
    return results
```

### Batch Processing

Generate embeddings in batches:

```python
def batch_ingest_optimized(documents: List[dict], batch_size: int = 50):
    """
    Optimized batch ingestion with batched embedding generation.
    """
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        # Extract texts
        texts = [doc['content'] for doc in batch]
        
        # Generate embeddings in batch (much faster)
        embeddings = embedding_service.generate_embeddings_batch(texts)
        
        # Store in database
        with db_service.session_scope() as session:
            for doc, embedding in zip(batch, embeddings):
                # Create embedding record
                # ... store in database
                pass
            
            session.commit()
```

### Monitoring Performance

Track search performance:

```python
import time
from datetime import datetime

class SearchMonitor:
    """Monitor search performance."""
    
    def __init__(self):
        self.metrics = []
    
    def monitored_search(self, query: str, **kwargs):
        """Search with performance monitoring."""
        start_time = time.time()
        
        results = vector_search_service.search(query=query, **kwargs)
        
        duration = time.time() - start_time
        
        self.metrics.append({
            'timestamp': datetime.now(),
            'query': query,
            'duration': duration,
            'result_count': len(results),
            'filters': kwargs.get('filters', {})
        })
        
        return results
    
    def get_stats(self):
        """Get performance statistics."""
        if not self.metrics:
            return {}
        
        durations = [m['duration'] for m in self.metrics]
        
        return {
            'total_searches': len(self.metrics),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'slow_searches': len([d for d in durations if d > 1.0])
        }

# Usage
monitor = SearchMonitor()

results = monitor.monitored_search(
    query="investment opportunities",
    source_type='research_notes',
    limit=10
)

print(monitor.get_stats())
```

---

## Troubleshooting

### Common Issues

#### 1. Slow Search Performance

**Symptoms**: Searches taking > 1 second

**Solutions**:
```python
# 1. Check if index exists
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'text_embeddings';

# 2. Rebuild index if needed
DROP INDEX IF EXISTS idx_embeddings_vector;
CREATE INDEX idx_embeddings_vector ON text_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

# 3. Analyze table
ANALYZE text_embeddings;

# 4. Add metadata filters
results = vector_search_service.search(
    query="...",
    filters={'sector': 'Technology'},  # âœ… Reduces search space
    limit=10  # âœ… Lower limit
)
```

#### 2. Out of Memory During Indexing

**Solutions**:
```sql
-- Use IVFFlat instead of HNSW
DROP INDEX IF EXISTS idx_embeddings_vector;
CREATE INDEX idx_embeddings_vector ON text_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Or increase PostgreSQL memory
-- In postgresql.conf:
-- shared_buffers = 4GB
-- work_mem = 256MB
-- maintenance_work_mem = 2GB
```

#### 3. Embeddings Not Generated

**Check automatic ingestion:**
```python
# Verify SearchableMixin is included
ResearchNote = get_model('ResearchNote')
print(ResearchNote.__bases__)  # Should include SearchableMixin

# Check if fields are configured
if hasattr(ResearchNote, '_searchable_fields'):
    print(f"Searchable fields: {ResearchNote._searchable_fields}")
else:
    print("â No searchable fields configured!")

# Manually trigger ingestion
from timber.common.services.vector import vector_ingestion_service

vector_ingestion_service.ingest_document(
    content="test content",
    source_type='research_notes',
    source_id='test-123',
    metadata={}
)
```

#### 4. Inconsistent Search Results

**Solutions**:
```python
# 1. Check embedding model consistency
print(f"Model: {embedding_service.model_name}")
print(f"Dimension: {embedding_service.get_dimension()}")

# 2. Verify all records have embeddings
with db_service.session_scope() as session:
    total_records = session.query(ResearchNote).count()
    total_embeddings = session.execute(
        "SELECT COUNT(*) FROM text_embeddings WHERE source_type = 'research_notes'"
    ).scalar()
    
    print(f"Records: {total_records}")
    print(f"Embeddings: {total_embeddings}")
    
    if total_records != total_embeddings:
        print("â Mismatch - some records not ingested!")

# 3. Re-index if needed
# Delete and regenerate all embeddings
```

### Debug Mode

Enable detailed logging:

```python
import logging

# Enable vector service logging
logging.basicConfig(level=logging.DEBUG)
vector_logger = logging.getLogger('timber.vector')
vector_logger.setLevel(logging.DEBUG)

# Now searches will log:
# - Query text
# - Embedding generation time
# - Search filters
# - Result counts
# - Performance metrics

results = vector_search_service.search(
    query="test",
    source_type='research_notes'
)
```

---

## Complete Example

```python
# Complete example: Building a research assistant with vector search

from timber.common import initialize_timber
from timber.common.models import get_model
from timber.common.services.vector import vector_search_service
from timber.common.services.db_service import db_service

# Initialize
initialize_timber(
    model_config_dirs=['./data/models'],
    enable_auto_vector_ingestion=True,
    vector_config={
        'embedding_model': 'BAAI/bge-small-en-v1.5',
        'embedding_dim': 384,
        'batch_size': 32
    }
)

ResearchNote = get_model('ResearchNote')

# 1. Add research notes (automatically embedded)
def add_research_notes():
    """Add sample research notes."""
    notes = [
        {
            'ticker': 'AAPL',
            'content': 'Apple shows strong momentum in services and wearables. AI integration looks promising.',
            'summary': 'Bullish on AAPL - AI growth driver'
        },
        {
            'ticker': 'MSFT',
            'content': 'Microsoft Azure growth accelerating. AI Copilot showing strong enterprise adoption.',
            'summary': 'Strong buy for cloud and AI exposure'
        },
        {
            'ticker': 'GOOGL',
            'content': 'Google facing regulatory pressure but search dominance intact. Bard catching up to competitors.',
            'summary': 'Hold - regulatory concerns offset by AI progress'
        }
    ]
    
    with db_service.session_scope() as session:
        for note_data in notes:
            note = ResearchNote(
                user_id='user-123',
                **note_data
            )
            session.add(note)
        session.commit()
    
    print("âœ… Added research notes")

# 2. Semantic search
def semantic_search_example():
    """Example semantic searches."""
    
    # Search for AI opportunities
    print("\n=== AI Opportunities ===")
    results = vector_search_service.search(
        query="artificial intelligence growth opportunities",
        source_type='research_notes',
        limit=3
    )
    
    for r in results:
        print(f"Score: {r['score']:.3f}")
        print(f"Ticker: {r['metadata'].get('ticker')}")
        print(f"Summary: {r['content'][:100]}...")
        print()

# 3. Filtered search
def filtered_search_example():
    """Search within specific context."""
    
    print("\n=== MSFT Research ===")
    results = vector_search_service.search(
        query="cloud computing growth",
        source_type='research_notes',
        filters={'ticker': 'MSFT'},
        limit=5
    )
    
    for r in results:
        print(f"Score: {r['score']:.3f}")
        print(f"Content: {r['content']}")
        print()

# 4. Find similar research
def find_similar_example():
    """Find research similar to a specific note."""
    
    # Get a research note
    with db_service.session_scope() as session:
        source_note = session.query(ResearchNote)\
            .filter_by(ticker='AAPL')\
            .first()
        
        print(f"\n=== Similar to AAPL Research ===")
        print(f"Source: {source_note.summary}")
        
        # Find similar using content
        query_text = f"{source_note.content} {source_note.summary}"
    
    similar = vector_search_service.search(
        query=query_text,
        source_type='research_notes',
        limit=3
    )
    
    for r in similar:
        if r['metadata'].get('ticker') != 'AAPL':  # Exclude self
            print(f"\nTicker: {r['metadata'].get('ticker')}")
            print(f"Score: {r['score']:.3f}")
            print(f"Summary: {r['content'][:100]}...")

# Run examples
if __name__ == '__main__':
    add_research_notes()
    semantic_search_example()
    filtered_search_example()
    find_similar_example()
```

---

## Summary

**Key Takeaways:**

âœ… **Automatic Integration** - SearchableMixin handles ingestion  
âœ… **Optimized Storage** - Two-table strategy for performance  
âœ… **Flexible Search** - Combine semantic + metadata filters  
âœ… **Multiple Models** - FastEmbed, OpenAI, or custom  
âœ… **Batch Operations** - Efficient bulk processing  
âœ… **Production Ready** - Monitoring, caching, optimization  

**Next Steps:**

1. Enable pgvector extension
2. Configure vector settings
3. Mark models as searchable
4. Test semantic search
5. Tune index parameters
6. Implement caching
7. Monitor performance

---

**Created:** October 19, 2025  
**Version:** 0.2.0  
**Word Count:** ~7,000 words  
**Status:** âœ… Complete
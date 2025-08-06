from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import uuid
from typing import List, Dict, Any
from config import Config

class VectorStore:
    """Vector store implementation using Qdrant"""
    
    def __init__(self):
        """Initialize Qdrant client and embeddings model"""
        self.client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            google_api_key=Config.GEMINI_API_KEY
        )
        self.collection_name = Config.COLLECTION_NAME
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        try:
            # Try to get the collection to see if it exists
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            # Collection doesn't exist, create it
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=768,  # Default size for text-embedding-004
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection '{self.collection_name}'")
            except Exception as create_error:
                if "already exists" in str(create_error):
                    print(f"Collection '{self.collection_name}' already exists (handled)")
                else:
                    raise create_error
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store"""
        if not documents:
            return []
        
        try:
            # Generate embeddings for all documents
            texts = [doc["content"] for doc in documents]
            embeddings = self.embeddings.embed_documents(texts)
            
            # Create points for Qdrant
            points = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                point_id = str(uuid.uuid4())
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": doc["content"],
                        "metadata": doc.get("metadata", {}),
                        "source": doc.get("source", "unknown")
                    }
                )
                points.append(point)
            
            # Insert points into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            return [point.id for point in points]
            
        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        # Generate embedding for query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "content": result.payload["content"],
                "metadata": result.payload.get("metadata", {}),
                "source": result.payload.get("source", "unknown"),
                "score": result.score
            })
        
        return results
    
    def delete_collection(self):
        """Delete the collection (for testing purposes)"""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            # Try to get basic collection info
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.name,
                "vectors_count": getattr(info, 'vectors_count', 0),
                "points_count": getattr(info, 'points_count', 0),
                "status": "active"
            }
        except Exception as e:
            # If collection doesn't exist, try to create it
            try:
                self._ensure_collection_exists()
                return {
                    "name": self.collection_name,
                    "vectors_count": 0,
                    "points_count": 0,
                    "status": "active"
                }
            except Exception as create_error:
                return {
                    "name": self.collection_name,
                    "vectors_count": 0,
                    "points_count": 0,
                    "status": "available",
                    "message": "Collection ready for use"
                } 
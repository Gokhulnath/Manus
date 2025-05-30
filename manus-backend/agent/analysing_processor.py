import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
from agent.settings import settings
from core.database import get_supabase_client
from services.chunk import ChunkService

load_dotenv()

logger = logging.getLogger(__name__)

class AnalysingProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embedding_model = settings.EMBEDDING_MODEL
        self.embedding_dimensions = settings.EMBEDDING_DIMENSIONS
        self.pinecone_index = self.pc.Index(self.index_name)

        self.chunk_service = ChunkService(get_supabase_client())

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding using OpenAI's text-embedding-3-small"""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text,
            dimensions=self.embedding_dimensions
        )
        return response.data[0].embedding

    async def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        # Get query embedding
        query_embedding = self._get_embedding(query)

        # Search in Pinecone
        search_results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Get full chunk details from Supabase
        vector_ids = [match['id'] for match in search_results['matches']]

        chunk_details = await self.chunk_service.get_chunks_by_vector_ids(vector_ids)

        # Combine results
        results = []
        for match in search_results['matches']:
            # Find corresponding chunk detail
            chunk_detail = next(
                (chunk_doc_tuple for chunk_doc_tuple in chunk_details if chunk_doc_tuple[0].vector_id == match['id']),
                None
            )

            if chunk_detail:
                chunk, document = chunk_detail  # Unpack the tuple
                results.append({
                    'similarity_score': match['score'],
                    'document_name': document.filename,
                    'document_type': document.file_type,
                    'document_filepath': document.file_path,
                    'chunk_id': chunk.id,
                    'chunk_index': chunk.chunk_index,
                    'content': chunk.content,
                    'start_char_index': chunk.start_char_index,
                    'end_char_index': chunk.end_char_index,
                    'vector_id': match['id']
                })

        return results
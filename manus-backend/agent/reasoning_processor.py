import logging
from typing import Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

from agent.analysing_processor import AnalysingProcessor
from agent.settings import settings
from core.database import get_supabase_client
from services.chunk import ChunkService

load_dotenv()

logger = logging.getLogger(__name__)

class ReasoningProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embedding_model = settings.EMBEDDING_MODEL
        self.embedding_dimensions = settings.EMBEDDING_DIMENSIONS
        self.pinecone_index = self.pc.Index(self.index_name)

        self.chunk_service = ChunkService(get_supabase_client())
        self.analysing_processor = AnalysingProcessor()
        self.top_k = 5
        self.openai_model = settings.OPENAI_MODEL

    async def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using RAG"""
        logger.info(f"Searching for relevant information for: {question}")

        # Search for relevant chunks
        relevant_chunks = await self.analysing_processor.search_similar_chunks(question, self.top_k)

        if not relevant_chunks:
            return {
                'answer': "I couldn't find any relevant information in the uploaded documents.",
                'sources': [],
                'question': question
            }

        # Prepare context for the LLM
        context_parts = []
        sources = []

        for i, chunk in enumerate(relevant_chunks):
            char_range = f"characters {chunk['start_char_index']}-{chunk['end_char_index']}"
            context_parts.append(
                f"Document: {chunk['document_name']}\nContent: {chunk['content']}\n")
            sources.append({
                'document_name': chunk['document_name'],
                'document_type': chunk['document_type'],
                'document_filepath': chunk['document_filepath'],
                'chunk_id': chunk['chunk_id'],
                'chunk_index': chunk['chunk_index'] + 1,
                'start_char_index': chunk['start_char_index'],
                'end_char_index': chunk['end_char_index'],
                'character_range': char_range,
                'similarity_score': round(chunk['similarity_score'], 4),
                'content_preview': chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk[
                    'content']
            })

        context = "\n---\n".join(context_parts)

        # Create prompt for the LLM
        prompt = f"""Based on the following context from uploaded documents, please answer the question. 
        If the answer cannot be found in the context, please say so.

        Context:
        {context}
        
        Question: {question}
        
        Please provide a comprehensive answer based on the context above. When referencing information, 
        mention which document and chunk it comes from, along with the character position in the original document."""

        # Get answer from OpenAI
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system",
                 "content": "You are a helpful Law assistant that answers questions based on provided law document context. Always cite your sources by mentioning the document name, chunk number, and character position when referencing information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        return {
            'answer': answer,
            'sources': sources,
            'question': question,
            'total_sources_found': len(relevant_chunks)
        }
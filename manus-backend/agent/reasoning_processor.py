import logging
from typing import Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

from agent.analysing_processor import AnalysingProcessor
from agent.settings import settings
from core.database import get_supabase_client
from core.enums import MessageRole, MessageTask, MessageStatus
from schemas.message import MessageCreate, MessageResponse
from services.chunk import ChunkService
from services.message import MessageService

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
        self.top_k = 10
        self.openai_model = settings.OPENAI_MODEL

        self.chunk_service = ChunkService(get_supabase_client())
        self.analysing_processor = AnalysingProcessor()
        self.message_service = MessageService(get_supabase_client())

    async def answer_question(self, message: MessageResponse) -> Dict[str, Any]:
        """Answer a question using RAG"""
        question = message.content
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
            source = {
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
            }
            sources.append(source)

            new_message = MessageCreate(
                chat_id=message.chat_id,
                chunk_id=chunk['chunk_id'],
                role=MessageRole.ASSISTANT,
                content=str(source),
                task=MessageTask.ANALYSE,
                status=MessageStatus.COMPLETED
            )
            await self.message_service.create_message(new_message)

        context = "\n---\n".join(context_parts)

        # Create prompt for the LLM
        prompt = f"""You are provided with legal context extracted from one or more uploaded documents. 
        Your task is to answer the following question clearly and precisely, using only the information found in the context.

        Instructions:
        - If the answer is available in the context, provide a direct, well-reasoned answer.
        - You must cite **all the documents** provided in the context, regardless of whether they were directly used.
        - Also cite any referenced law names, acts, or section numbers mentioned in the answer.
        - Do **not** include any information that is not present in the context.
        - If the answer cannot be found in the context, respond with: "The answer is not available in the provided context."


        Context:
        {context}
        
        Question: {question}
        
        Please provide a comprehensive answer based on the context above. In the end mention which document it comes from, 
        along with the law or law number or acts if present from the original document."""

        # Get answer from OpenAI
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system",
                 "content": "You are a helpful Law assistant that answers questions based on provided law document context. Always cite your sources by mentioning the document name when referencing information."},
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
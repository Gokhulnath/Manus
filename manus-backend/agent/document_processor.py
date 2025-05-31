import logging
import os
import hashlib
from typing import List, Dict, Any, Tuple
import PyPDF2
from docx import Document
import tiktoken
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from agent.settings import settings
from core.database import get_supabase_client
from schemas.chunk import ChunkCreate
from schemas.document import DocumentCreate, DocumentUpdate
from services.chunk import ChunkService
from services.document import DocumentService

load_dotenv()

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):

        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.max_tokens = settings.MAX_TOKENS_PER_CHUNK
        self.overlap_token = settings.OVERLAPPING_TOKEN
        self.embedding_model = settings.EMBEDDING_MODEL
        self.embedding_dimensions = settings.EMBEDDING_DIMENSIONS

        existing_indexes = [index.name for index in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dimensions,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.PINECONE_CLOUD,
                    region=settings.PINECONE_REGION
                )
            )

        self.pinecone_index = self.pc.Index(self.index_name)

        self.document_service = DocumentService(get_supabase_client())
        self.chunk_service = ChunkService(get_supabase_client())

        self.tokenizer = tiktoken.get_encoding("cl100k_base")


    def _calculate_file_hash(self, content: str) -> str:
        """Calculate hash of file content to avoid duplicates"""
        return hashlib.md5(content.encode()).hexdigest()

    def _extract_text_from_file(self, file_path: str) -> Tuple[str, str]:
        """Extract text from various file formats"""
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path), 'pdf'
        elif file_extension == '.docx':
            return self._extract_from_docx(file_path), 'docx'
        elif file_extension == '.txt':
            return self._extract_from_txt(file_path), 'txt'
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _chunk_text(self, text: str, max_tokens: int = 512, overlap_tokens: int = 50) -> List[Dict[str, Any]]:
        """Chunk text with consideration for headings, short and long paragraphs."""
        paragraphs = text.strip().split('\n')
        merged_paragraphs = []

        # Merge headings with the following paragraph
        i = 0
        while i < len(paragraphs):
            current = paragraphs[i].strip()
            if i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1].strip()
                if len(current.split()) < 10 and next_para:
                    merged_paragraphs.append(f"{current}\n{next_para}")
                    i += 2
                    continue
            if current:
                merged_paragraphs.append(current)
            i += 1

        # Tokenize and chunk
        chunks = []
        current_chunk_tokens = []
        current_chunk_text = ""
        current_start_char = 0

        for para in merged_paragraphs:
            para_tokens = self.tokenizer.encode(para)
            para_token_count = len(para_tokens)

            if para_token_count > max_tokens:
                # If paragraph is too long, chunk it
                start = 0
                while start < para_token_count:
                    end = min(start + max_tokens, para_token_count)
                    sub_tokens = para_tokens[start:end]
                    sub_text = self.tokenizer.decode(sub_tokens).strip()

                    if sub_text:
                        sub_start_char = text.find(sub_text, current_start_char)
                        if sub_start_char == -1:
                            chars_per_token = len(text) / len(self.tokenizer.encode(text))
                            sub_start_char = int(start * chars_per_token)

                        sub_end_char = sub_start_char + len(sub_text)
                        chunks.append({
                            'text': sub_text,
                            'start_char': sub_start_char,
                            'end_char': sub_end_char,
                            'token_count': len(sub_tokens)
                        })
                        current_start_char = sub_end_char

                    if end == para_token_count:
                        break
                    start = end - overlap_tokens

            elif para_token_count < 30:
                # If paragraph is very short, accumulate it with the next
                current_chunk_tokens += para_tokens
                current_chunk_text += '\n' + para
            else:
                # Commit the current chunk if it would exceed max_tokens
                if len(current_chunk_tokens) + para_token_count > max_tokens:
                    if current_chunk_tokens:
                        chunk_text = self.tokenizer.decode(current_chunk_tokens).strip()
                        start_char = text.find(chunk_text, current_start_char)
                        if start_char == -1:
                            chars_per_token = len(text) / len(self.tokenizer.encode(text))
                            start_char = int(current_start_char)

                        end_char = start_char + len(chunk_text)
                        chunks.append({
                            'text': chunk_text,
                            'start_char': start_char,
                            'end_char': end_char,
                            'token_count': len(current_chunk_tokens)
                        })
                        current_start_char = end_char
                    current_chunk_tokens = para_tokens
                    current_chunk_text = para
                else:
                    current_chunk_tokens += para_tokens
                    current_chunk_text += '\n' + para

        # Append any remaining chunk
        if current_chunk_tokens:
            chunk_text = self.tokenizer.decode(current_chunk_tokens).strip()
            start_char = text.find(chunk_text, current_start_char)
            if start_char == -1:
                chars_per_token = len(text) / len(self.tokenizer.encode(text))
                start_char = int(current_start_char)
            end_char = start_char + len(chunk_text)
            chunks.append({
                'text': chunk_text,
                'start_char': start_char,
                'end_char': end_char,
                'token_count': len(current_chunk_tokens)
            })

        return chunks

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding using OpenAI's text-embedding-3-small"""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text,
            dimensions=self.embedding_dimensions
        )
        return response.data[0].embedding

    async def process_document(self, file_path: str):
        """Process a document: extract text, chunk, vectorize, and store"""
        try:
            filename = os.path.basename(file_path)
            text_content, file_type = self._extract_text_from_file(file_path)
            file_hash = self._calculate_file_hash(text_content)

            existing_doc = await self.document_service.get_document_by_hash(file_hash)

            if existing_doc:
                return f"Document {filename} already exists in the system."

            doc_result = await self.document_service.create_document(
                DocumentCreate(
                    filename=filename,
                    file_path=file_path,
                    file_type=file_type,
                    file_hash=file_hash
                )
            )

            document_id = doc_result.id

            chunks = self._chunk_text(text_content, self.max_tokens, self.overlap_token)
            logger.info(f"Created {len(chunks)} chunks")

            vectors_to_upsert = []
            chunk_records = []

            for i, chunk_data in enumerate(chunks):
                logger.info(f"Processing chunk {i + 1}/{len(chunks)}")

                chunk_text = chunk_data['text']

                embedding = self._get_embedding(chunk_text)

                vector_id = f"{document_id}_{i}"

                vectors_to_upsert.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': {
                        'document_id': document_id,
                        'filename': filename,
                        'chunk_index': i,
                        'start_char': chunk_data['start_char'],
                        'end_char': chunk_data['end_char'],
                        'content': chunk_text[:500]  # Store first 500 chars in metadata
                    }
                })

                chunk_records.append({
                    'document_id': document_id,
                    'chunk_index': i,
                    'content': chunk_text,
                    'token_count': chunk_data['token_count'],
                    'start_char_index': chunk_data['start_char'],
                    'end_char_index': chunk_data['end_char'],
                    'vector_id': vector_id
                })

            logger.info("Uploading vectors to Pinecone...")
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.pinecone_index.upsert(vectors=batch)

            logger.info("Storing chunks in Supabase...")
            for i in range(0, len(chunk_records), batch_size):
                batch = chunk_records[i:i + batch_size]
                for chunk in batch:
                    await self.chunk_service.create_chunk(ChunkCreate(**chunk))

            await self.document_service.update_document(document_id, DocumentUpdate(total_chunks = len(chunks)))

            logger.info(f"Successfully processed {filename}: {len(chunks)} chunks created and vectorized.")
        except Exception as e:
            logger.error(f"Error in processing document and chunks {file_path}: {e}")

    async def delete_document(self, file_path: str):
        """Delete a document"""
        try:
            filename = os.path.basename(file_path)
            deleted_doc = await self.document_service.get_document_by_filename(filename)
            if not deleted_doc:
                logger.info("File not found in DB")
                return
            document_id = deleted_doc.id
            deleted_document_chunks = await self.chunk_service.get_chunks_by_document_id(document_id)

            self.pinecone_index.delete([v.vector_id for v in deleted_document_chunks])
            await self.chunk_service.delete_chunks_by_document_id(document_id)
            await self.document_service.delete_document(document_id)
            logger.info("Document and chunks deleted successfully.")
        except Exception as e:
            logger.error(f"Error in deleting document and chunks {file_path}: {e}")
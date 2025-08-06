import PyPDF2
import io
from typing import List, Dict, Any
import re

class PDFProcessor:
    """PDF processing utilities"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this is not the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    @staticmethod
    def process_pdf_for_rag(pdf_file, source_name: str = "pdf_document") -> List[Dict[str, Any]]:
        """Process PDF file for RAG storage"""
        try:
            # Extract text
            text = PDFProcessor.extract_text_from_pdf(pdf_file)
            
            # Chunk the text
            chunks = PDFProcessor.chunk_text(text)
            
            # Create documents for vector store
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "chunk_id": i,
                        "source": source_name,
                        "chunk_size": len(chunk)
                    },
                    "source": source_name
                })
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    @staticmethod
    def get_pdf_info(pdf_file) -> Dict[str, Any]:
        """Get basic information about the PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            return {
                "num_pages": len(pdf_reader.pages),
                "title": pdf_reader.metadata.get('/Title', 'Unknown'),
                "author": pdf_reader.metadata.get('/Author', 'Unknown'),
                "subject": pdf_reader.metadata.get('/Subject', 'Unknown')
            }
        except Exception as e:
            return {"error": f"Error reading PDF info: {str(e)}"} 
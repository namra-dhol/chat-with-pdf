"""
pdf_processor.py
----------------
Handles PDF text extraction and chunking.
"""

import io
import PyPDF2
from typing import List


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text content from a PDF given its raw bytes.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        A single string containing all page text joined with newlines.
    """
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    all_text = []

    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            all_text.append(text.strip())

    if not all_text:
        raise ValueError("No readable text found in the PDF. It may be image-based.")

    return "\n\n".join(all_text)


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split a large text string into overlapping chunks.

    Args:
        text:       The full document text.
        chunk_size: Maximum number of characters per chunk.
        overlap:    Number of characters to overlap between consecutive chunks.

    Returns:
        A list of text chunk strings.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        # Move forward by (chunk_size - overlap) so chunks share context
        start += chunk_size - overlap

    return chunks

import fitz  # PyMuPDF
import re
import os
from typing import Optional, List

class PDFProcessor:
    """
    Handles PDF file processing, including text extraction and DOI identification.
    """

    # improved regex for DOI matching
    # looks for 10.xxxx/ suffix
    DOI_REGEX = r'\b(10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+)\b'

    def __init__(self):
        pass

    def extract_text(self, file_path: str, max_pages: int = 3) -> str:
        """
        Extracts text from the first few pages of a PDF file.
        DOIs are usually on the first page.
        """
        text = ""
        try:
            doc = fitz.open(file_path)
            # Iterate over the first few pages
            for i in range(min(len(doc), max_pages)):
                text += doc[i].get_text()
            doc.close()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        return text

    def find_doi(self, text: str) -> Optional[str]:
        """
        Searches for a DOI in the provided text.
        Returns the first found DOI or None.
        """
        # Search for DOI pattern
        # Case insensitive search might be needed but usually DOIs are standard
        matches = re.findall(self.DOI_REGEX, text, re.IGNORECASE)
        
        if matches:
            # excessive generic cleanup if needed
            # return the first match that looks most promising
            # Sometimes regex catches trailing punctuation like a period if not carefully bounded
            candidate = matches[0]
            # Strip trailing punctuation often caught by regex boundaries if context is text
            candidate = candidate.strip('.')
            return candidate
        return None

    def process_file(self, file_path: str) -> Optional[str]:
        """
        Process a single PDF file and return its DOI if found.
        """
        text = self.extract_text(file_path)
        return self.find_doi(text)

    def process_directory(self, dir_path: str) -> dict:
        """
        Process all PDFs in a directory.
        Returns a dictionary mapping filename to DOI (or None).
        """
        results = {}
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    doi = self.process_file(full_path)
                    results[full_path] = doi
        return results

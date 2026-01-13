import os
import pandas as pd
from typing import List, Dict, Optional
from .pdf_processor import PDFProcessor
from .metadata_fetcher import MetadataFetcher
from .endnote_writer import EndNoteWriter

class LibraryGenerator:
    """
    Main controller class for generating EndNote libraries from PDFs.
    """

    def __init__(self, email: str = "agent@example.com"):
        self.pdf_processor = PDFProcessor()
        self.metadata_fetcher = MetadataFetcher(email)
        self.endnote_writer = EndNoteWriter()
        self.results_df = pd.DataFrame()

    def process_directory(self, folder_path: str, progress_callback=None) -> pd.DataFrame:
        """
        Scans a directory for PDFs, fetches metadata, and returns a DataFrame.
        progress_callback: Optional callable that receives (current_count, total_count, message).
        """
        print(f"Scanning directory: {folder_path}...")
        
        # 1. Find DOIs
        file_doi_map = self.pdf_processor.process_directory(folder_path)
        
        records = []
        total_files = len(file_doi_map)
        print(f"Found {total_files} PDFs. processing...")
        
        for i, (file_path, doi) in enumerate(file_doi_map.items(), start=1):
            filename = os.path.basename(file_path)
            if progress_callback:
                progress_callback(i, total_files, f"Processing {filename}...")

            record = {
                'file_path': file_path,
                'doi': doi,
                'title': None,
                'authors': None,
                'year': None,
                'journal': None,
                'status': 'Pending'
            }
            
            if doi:
                print(f"Fetching metadata for DOI: {doi}")
                metadata = self.metadata_fetcher.fetch_metadata(doi)
                if metadata:
                    record.update(metadata)
                    record['status'] = 'Success'
                else:
                    record['status'] = 'Metadata Not Found'
            else:
                record['status'] = 'DOI Not Found'
                
            records.append(record)
            
        self.results_df = pd.DataFrame(records)
        return self.results_df

    def save_library(self, output_path: str):
        """
        Saves the processed records to an EndNote XML file.
        Only saves records where we have at least some metadata or a file.
        """
        if self.results_df.empty:
            print("No records to save.")
            return

        # Convert DF back to list of dicts
        # Sanitize: Replace NaN with None so XML serialier doesn't crash
        df_clean = self.results_df.where(pd.notnull(self.results_df), None)
        records = df_clean.to_dict('records')
        self.endnote_writer.generate_xml(records, output_path)

    def get_summary_table(self) -> pd.DataFrame:
        return self.results_df

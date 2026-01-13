import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict
import os

class EndNoteWriter:
    """
    Generates EndNote XML files from metadata records.
    """

    def __init__(self):
        pass

    def generate_xml(self, records: List[Dict], output_file: str):
        """
        Writes the records to an EndNote XML file.
        records: List of dictionaries containing metadata and 'file_path'.
        """
        root = ET.Element("xml")
        records_elem = ET.SubElement(root, "records")

        for idx, record in enumerate(records, start=1):
            if not record:
                continue
                
            rec_elem = ET.SubElement(records_elem, "record")
            
            # Record Number
            ET.SubElement(rec_elem, "rec-number").text = str(idx)
            
            # Reference Type (17 is Journal Article, generic fallback)
            ref_type = ET.SubElement(rec_elem, "ref-type", name="Journal Article")
            ref_type.text = "17"

            # Contributors (Authors)
            contributors = ET.SubElement(rec_elem, "contributors")
            authors = ET.SubElement(contributors, "authors")
            for author_name in (record.get('authors') or []):
                ET.SubElement(authors, "author").text = author_name

            # Titles
            titles = ET.SubElement(rec_elem, "titles")
            if record.get('title'):
                ET.SubElement(titles, "title").text = record['title']
            if record.get('journal'):
                ET.SubElement(titles, "secondary-title").text = record['journal']

            # Dates (Year)
            if record.get('year'):
                dates = ET.SubElement(rec_elem, "dates")
                ET.SubElement(dates, "year").text = record['year']

            # Pagination & Volume
            if record.get('pages'):
                ET.SubElement(rec_elem, "pages").text = record['pages']
            if record.get('volume'):
                ET.SubElement(rec_elem, "volume").text = record['volume']
            if record.get('issue'):
                ET.SubElement(rec_elem, "number").text = record['issue']

            # DOI
            if record.get('doi'):
                ET.SubElement(rec_elem, "electronic-resource-num").text = record['doi']

            # PDF Attachment
            # EndNote XML uses <urls><pdf-urls><url>... to link files
            if record.get('file_path'):
                urls = ET.SubElement(rec_elem, "urls")
                pdf_urls = ET.SubElement(urls, "pdf-urls")
                # Ensure the path is a valid file URI
                file_uri = f"file://{os.path.abspath(record['file_path'])}"
                ET.SubElement(pdf_urls, "url").text = file_uri

        # Write to file with pretty printing
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_str)
        print(f"Successfully generated EndNote library at {output_file}")

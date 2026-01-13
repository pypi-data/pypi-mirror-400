# EndNote Library Generator

![App Icon](icon.png)


A Python tool that scans a directory of PDFs, automatically identifies their DOIs, fetches bibliographic metadata from Crossref, and generates an EndNote-compatible XML library with file attachments.

![App Main Window](main_window.png)

## Features

- **PDF Scanning**: Recursive logic to find all PDFs in a folder.
- **DOI Identification**: Regex-based extraction of DOIs from the first few pages of each PDF.
- **Metadata Fetching**: Retrieves Title, Author, Year, Journal, Volume, Issue, Pages from Crossref API.
- **EndNote XML Export**: Generates a rich XML file that can be imported directly into EndNote.
- **File Attachments**: Links the original PDF files to the created EndNote records.

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Using the Python Package

```python
from endnote_generator import LibraryGenerator

# Initialize
generator = LibraryGenerator()

# Process a folder containing PDFs
df = generator.process_directory("path/to/your/pdf_folder")

# View results
print(df)

# Save header to EndNote XML
generator.save_library("MyLibrary.xml")
```

### Using the GUI

To run the modern graphical interface:

```bash
python gui_app.py
```

- Select the folder containing your PDFs.
- Select where to save the EndNote XML.
- Click **Generate Library**.

### Using the Jupyter Notebook

Open `demo.ipynb` to see a step-by-step interactive demonstration.


## Importing into EndNote

1. Open EndNote.
2. Go to **File** -> **Import** -> **File...**
3. Choose the generated `MyLibrary.xml` file.
4. Set **Import Option** to `EndNote generated XML`.
5. Click **Import**.

## Project Structure

- `src/endnote_generator/`: Source code package.
- `src/endnote_generator/pdf_processor.py`: Handles PDF text extraction and DOI finding.
- `src/endnote_generator/metadata_fetcher.py`: Connects to Crossref API.
- `src/endnote_generator/endnote_writer.py`: Generates the XML output.
- `src/endnote_generator/library_manager.py`: Main orchestrator.

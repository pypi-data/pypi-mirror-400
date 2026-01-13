import os
import csv
import logging
import warnings

# Remove basicConfig, rely on root configuration from the main CLI/app
logger = logging.getLogger(__name__)

class DataExtractor:
    """Extracts text from files organized by class folders using LangChain."""

    def __init__(self, data_root: str, output_csv: str):
        """
        Initialize extractor with data directory and output CSV path.
        :param data_root: Root directory containing class folders.
        :param output_csv: Path to save the output CSV.
        """
        self.data_root = data_root
        self.output_csv = output_csv
        self.DoclingLoader = None
        self._check_dependencies()

    def _check_dependencies(self):
        """Check for required dependencies and silence initialization warnings."""
        try:
            # Suppress warnings that might occur during import (like OCR init warnings)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Attempt to silence specific loggers if they are noisy
                logging.getLogger("docling").setLevel(logging.ERROR)
                logging.getLogger("rapid_ocr").setLevel(logging.ERROR)
                logging.getLogger("RapidOCR").setLevel(logging.ERROR)
                logging.getLogger("transformers").setLevel(logging.ERROR)
                
                from docling.document_converter import DocumentConverter
                self.converter = DocumentConverter()
        except ImportError:
            logger.warning("docling or dependencies not installed. Extraction will not work.")

    def extract_text(self, file_path: str) -> str:
        """Extract text using LangChain Docling Loader."""
        if not hasattr(self, 'converter'):
            return ""

        try:
            # Suppress warnings during loading
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.converter.convert(file_path)
            
            # Export to markdown
            return result.document.export_to_markdown().strip()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    def extract(self) -> None:
        """Extract text from all supported files and save results to a CSV."""
        if not hasattr(self, 'converter'):
            logger.error("Skipping extraction: docling is not available.")
            return

        rows = []
        
        if not os.path.exists(self.data_root):
            logger.error(f"Data root directory not found: {self.data_root}")
            return

        from tqdm import tqdm

        for class_name in tqdm([d for d in os.listdir(self.data_root) if os.path.isdir(os.path.join(self.data_root, d))], desc="Classes"):
            class_dir = os.path.join(self.data_root, class_name)

            # logger.info(f"Processing class folder: {class_name}") # redundancy with tqdm

            filenames = [f for f in os.listdir(class_dir) if not f.startswith('.')]
            for filename in tqdm(filenames, desc=f"Processing {class_name}", leave=False):
                file_path = os.path.join(class_dir, filename)
                
                extracted_text = self.extract_text(file_path)

                if extracted_text:
                    rows.append({
                        "classes": class_name,
                        "file_name": filename,
                        "text": extracted_text
                    })
                else:
                    logger.warning(f"No text extracted from {filename}")

        self._save_to_csv(rows)
        logger.info(f"Extraction completed. Saved to: {self.output_csv}")

    def _save_to_csv(self, rows):
        """Save extracted data to CSV file."""
        try:
            with open(self.output_csv, 'w', encoding='utf-8', newline='') as csvfile:
                fieldnames = ['classes', 'file_name', 'text']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")






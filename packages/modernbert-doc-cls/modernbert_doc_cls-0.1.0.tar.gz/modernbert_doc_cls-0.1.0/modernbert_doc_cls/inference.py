import torch
import joblib
import logging
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from modernbert_doc_cls.data.extraction import DataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentClassifier:
    def __init__(self, model_path, encoder_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading model from {model_path} on {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

        if encoder_path:
            logger.info(f"Loading label encoder from {encoder_path}")
            self.label_encoder = joblib.load(encoder_path)
        else:
            self.label_encoder = None

    def predict(self, file_path):
        """
        Predicts the class of a document.
        :param file_path: Path to the PDF, TXT or Image file.
        :return: Predicted class, Confidence score
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None, 0.0

        # reuse extraction logic
        logger.info(f"Extracting text from {file_path}")
        text = ""
        try:
            from langchain_docling import DoclingLoader
            loader = DoclingLoader(file_path)
            docs = loader.load()
            text = "\n\n".join([doc.page_content for doc in docs]).strip()
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None, 0.0

        if not text:
            logger.warning("No text extracted from file.")
            return None, 0.0

        # Tokenize
        inputs = self.tokenizer(
            text, 
            truncation=True, 
            padding='max_length', 
            max_length=512, 
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            confidence, predicted_class_idx = torch.max(probs, dim=-1)
        
        predicted_idx = predicted_class_idx.item()
        confidence_score = confidence.item()
        
        if self.label_encoder:
            predicted_label = self.label_encoder.inverse_transform([predicted_idx])[0]
        else:
            predicted_label = str(predicted_idx)
            
        return predicted_label, confidence_score

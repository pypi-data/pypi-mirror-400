import argparse
import sys
from modernbert_doc_cls.training.train import DocClassifier
from modernbert_doc_cls.data.extraction import DataExtractor
from modernbert_doc_cls.inference import DocumentClassifier

def train_command(args):
    # Load config to check for data requirements
    import yaml
    import os
    
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    data_path = config.get("data_path", "dataset.csv")
    data_dir = config.get("data_dir", None)
    
    # If data_dir is provided, always extract to ensure freshness
    if data_dir and os.path.exists(data_dir):
        print(f"Extracting dataset from '{data_dir}' to '{data_path}'...")
        extractor = DataExtractor(data_dir, data_path)
        extractor.extract()
    elif not os.path.exists(data_path):
        print(f"Error: Dataset '{data_path}' not found and no valid 'data_dir' specified in config (or directory does not exist).")
        print("Please provide a valid 'data_dir' in the config to automatically extract the dataset, or ensure 'dataset.csv' exists.")
        sys.exit(1)
            
    clf = DocClassifier(args.config)
    clf.run()

def extract_command(args):
    extractor = DataExtractor(args.data_dir, args.output)
    extractor.extract()

def predict_command(args):
    classifier = DocumentClassifier(args.model_path, args.encoder_path)
    label, score = classifier.predict(args.file)
    print(f"Prediction: {label} (Confidence: {score:.4f})")

def main():
    parser = argparse.ArgumentParser(description="ModernBERT Document Classification CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Train
    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument("--config", type=str, required=True, help="Path to config file (YAML/JSON)")

    # Extract
    extract_parser = subparsers.add_parser("extract", help="Extract text from documents")
    extract_parser.add_argument("--data_dir", type=str, required=True, help="Root directory of data (class folders)")
    extract_parser.add_argument("--output", type=str, required=True, help="Output CSV path")

    # Predict
    predict_parser = subparsers.add_parser("predict", help="Predict class for a single file")
    predict_parser.add_argument("--model_path", type=str, required=True, help="Path to saved model directory")
    predict_parser.add_argument("--encoder_path", type=str, required=False, help="Path to label encoder pickle")
    predict_parser.add_argument("--file", type=str, required=True, help="File to predict")

    args = parser.parse_args()

    if args.command == "train":
        train_command(args)
    elif args.command == "extract":
        extract_command(args)
    elif args.command == "predict":
        predict_command(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

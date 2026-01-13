# ModernBERT Document Classification

A robust document classification library leveraging **ModernBERT** and **Docling** for state-of-the-art text extraction and classification.

## Features

- **Advanced Extraction**: Uses `docling` and `langchain` to parse complex PDFs, images, and text files with OCR and layout analysis.
- **ModernBERT**: Finetuned on your data for high-performance classification.
- **End-to-End Pipeline**: From raw files to trained model and inference.
- **Metrics & Visualization**: Automated generation of Confusion Matrices, Classification Reports (Precision, Recall, F1).
- **CLI Support**: Easy-to-use command-line interface.

## Installation

```bash
pip install .
```

*Note: Requires `torch`, `docling`, and `tesseract-ocr`/`poppler-utils` (for PDF/Image processing).*

## Usage

### 1. Data Preparation
Organize your data in a folder (e.g., `data_root` which is the default in config) where each subfolder represents a class.

```
data_root/
  ├── invoice/
  │   ├── file1.pdf
  │   └── file2.png
  └── resume/
      ├── file3.txt
      └── file4.pdf
```

### 2. Training (One-Step)
Run the training command. If `dataset.csv` does not exist, the library will automatically extract text from files in `data_dir` (defined in `configs/train_config.yaml`) before training.

```bash
python3 -m modernbert_doc_cls.cli train --config configs/train_config.yaml
```

*Note: You can still run `modernbert-cls extract` manually if preferred.*
Create a configuration file (e.g., `configs/train_config.yaml`):

```yaml
data_path: "dataset.csv"
model_id: "answerdotai/ModernBERT-base"
results_dir: "results"

training_args:
  train_batch_size: 4
  eval_batch_size: 4
  learning_rate: 2e-5
  num_train_epochs: 3
  save_strategy: "epoch"
  eval_strategy: "epoch"
  logging_strategy: "steps"
  logging_steps: 10
  save_total_limit: 2
  metric_for_best_model: "f1"
```

Run training:

```bash
python3 -m modernbert_doc_cls.cli train --config configs/train_config.yaml
```

The model and metrics will be saved in `results/`.



### 4. Inference

#### CLI Usage
Predict the class of a new document.

```bash

python3 -m modernbert_doc_cls.cli predict \
  --model_path results/model \
  --encoder_path results/label_encoder.pkl \
  --file path/to/document.pdf
```

#### Python API Usage
You can also use the library directly in your Python scripts:

```python
from modernbert_doc_cls.inference import DocumentClassifier

# Initialize the classifier
classifier = DocumentClassifier(
    model_path="results/model",
    encoder_path="results/label_encoder.pkl"
)

# Predict
label, confidence = classifier.predict("data_root/class2/invoice.pdf")
print(f"Predicted: {label} ({confidence:.4f})")
```

## License

MIT License

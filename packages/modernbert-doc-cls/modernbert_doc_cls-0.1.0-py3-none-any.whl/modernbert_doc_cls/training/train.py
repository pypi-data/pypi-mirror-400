import os
import re
import pandas as pd
import torch
import numpy as np
import joblib
import json
import yaml
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from datasets import Dataset
import shutil

from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    f1_score, precision_score, recall_score, accuracy_score, 
    classification_report, confusion_matrix, precision_recall_fscore_support
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocClassifier:
    def __init__(self, config_path_or_dict):
        # Load config
        if isinstance(config_path_or_dict, str):
            if config_path_or_dict.endswith('.yaml') or config_path_or_dict.endswith('.yml'):
                with open(config_path_or_dict, 'r') as f:
                    self.cfg = yaml.safe_load(f)
            else:
                with open(config_path_or_dict, 'r') as f:
                    self.cfg = json.load(f)
        else:
            self.cfg = config_path_or_dict

        self.data_path = self.cfg.get("data_path", "dataset.csv")
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = self.cfg.get("results_dir", f"results_{time_str}")
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
            
        self.model_save_path = os.path.join(self.results_dir, "model")
        self.val_model_save_path = os.path.join(self.results_dir, "val_model")
        self.encoder_save_path = os.path.join(self.results_dir, "label_encoder.pkl")
        self.metrics_save_path = os.path.join(self.results_dir, "metrics.json")
        self.report_save_path = os.path.join(self.results_dir, "classification_report.txt")
        self.model_id = self.cfg.get("model_id", "answerdotai/ModernBERT-base")
        
        logger.info(f"Loading tokenizer: {self.model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        self.label_encoder = LabelEncoder()
        self.training_args = None
        self.model = None

    def load_and_clean_data(self):
        logger.info(f"Loading data from {self.data_path}")
        df = pd.read_csv(self.data_path)
        df['cleaned_text'] = df['text'].apply(self.clean_text)
        df['doc_type'] = self.label_encoder.fit_transform(df['classes']) # Changed doc_type to classes to match extractor
        
        logger.info(f"Saving label encoder to {self.encoder_save_path}")
        joblib.dump(self.label_encoder, self.encoder_save_path)
        return df

    @staticmethod
    def clean_text(text):
        if not isinstance(text, str):
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower()

    def prepare_data(self, df):
        # Robust splitting logic
        test_size = self.cfg.get("test_size", 0.2)
        try:
            train_texts, test_texts, train_labels, test_labels = train_test_split(
                df['cleaned_text'], df['doc_type'],
                test_size=test_size,
                random_state=42,
                stratify=df['doc_type']
            )
        except ValueError:
            logger.warning("Stratified split failed (likely too few samples per class). Falling back to random split.")
            try:
                train_texts, test_texts, train_labels, test_labels = train_test_split(
                    df['cleaned_text'], df['doc_type'],
                    test_size=test_size,
                    random_state=42
                )
            except ValueError:
                logger.warning("Random split failed (likely dataset too small). Using Training set as Validation set.")
                train_texts, test_texts, train_labels, test_labels = list(df['cleaned_text']), list(df['cleaned_text']), list(df['doc_type']), list(df['doc_type'])
        if isinstance(train_texts, list):
             train_dataset = Dataset.from_dict({'text': train_texts, 'labels': train_labels})
             test_dataset = Dataset.from_dict({'text': test_texts, 'labels': test_labels})
        else:
             train_dataset = Dataset.from_dict({'text': train_texts.tolist(), 'labels': train_labels.tolist()})
             test_dataset = Dataset.from_dict({'text': test_texts.tolist(), 'labels': test_labels.tolist()})

        def tokenize_function(examples):
            return self.tokenizer(examples['text'], truncation=True, padding='max_length', max_length=8192)

        logger.info("Tokenizing datasets")
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        test_dataset = test_dataset.map(tokenize_function, batched=True)

        train_dataset = train_dataset.remove_columns(['text'])
        test_dataset = test_dataset.remove_columns(['text'])
        return train_dataset, test_dataset, test_labels

    def initialize_model(self, num_labels):
        logger.info(f"Initializing model with {num_labels} labels")
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_id, num_labels=num_labels)

    @staticmethod
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        preds = np.argmax(predictions, axis=1)
        return {
            "precision": precision_score(labels, preds, average='weighted', zero_division=0),
            "recall": recall_score(labels, preds, average='weighted', zero_division=0),
            "f1": f1_score(labels, preds, average='weighted', zero_division=0),
            "accuracy": accuracy_score(labels, preds)
        }

    def train_model(self, train_dataset, test_dataset):
        args = self.cfg.get("training_args", {})
        logger.info("Starting training")
        
        self.training_args = TrainingArguments(
            output_dir=self.val_model_save_path,
            per_device_train_batch_size=args.get("train_batch_size", 2),
            per_device_eval_batch_size=args.get("eval_batch_size", 2),
            learning_rate=float(args.get("learning_rate", 5e-5)),
            num_train_epochs=args.get("num_train_epochs", 5),
            logging_strategy=args.get("logging_strategy", "epoch"),
            eval_strategy=args.get("eval_strategy", "epoch"), # updated from evaluation_strategy
            save_strategy=args.get("save_strategy", "epoch"),
            save_total_limit=args.get("save_total_limit", 2),
            load_best_model_at_end=True,
            metric_for_best_model=args.get("metric_for_best_model", "f1"),
            no_cuda=args.get("no_cuda", False)
        )
        
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            processing_class=self.tokenizer,
            data_collator=DataCollatorWithPadding(self.tokenizer),
            compute_metrics=self.compute_metrics
        )
        
        result = trainer.train()
        train_metrics = result.metrics
        trainer.log_metrics("train", train_metrics)
        trainer.save_metrics("train", train_metrics)

        eval_metrics = trainer.evaluate()
        trainer.log_metrics("eval", eval_metrics)
        trainer.save_metrics("eval", eval_metrics)

        # Save all metrics in metrics.json
        with open(self.metrics_save_path, "w") as f:
            json.dump({"train_metrics": train_metrics, "eval_metrics": eval_metrics}, f, indent=2)

        return trainer

    def save_plots(self, test_labels, preds):
        logger.info("Generating and saving plots")
        class_names = self.label_encoder.classes_
        
        # Confusion Matrix
        cm = confusion_matrix(test_labels, preds)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "confusion_matrix.png"))
        plt.close()

        # Detailed Report Plot (Precision, Recall, F1 per class)
        report = classification_report(test_labels, preds, target_names=class_names, output_dict=True)
        report_df = pd.DataFrame(report).transpose().iloc[:-3] # Exclude avg rows
        
        plt.figure(figsize=(12, 6))
        report_df[['precision', 'recall', 'f1-score']].plot(kind='bar', figsize=(10, 6))
        plt.title('Classification Metrics per Class')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "classification_metrics.png"))
        plt.close()

    def evaluate_model(self, trainer, test_dataset, test_labels):
        logger.info("Evaluating model on test set")
        predictions = trainer.predict(test_dataset)
        preds = np.argmax(predictions.predictions, axis=-1)
        
        try:
            class_report = classification_report(test_labels, preds, target_names=self.label_encoder.classes_)
            logger.info("\n" + class_report)
            
            with open(self.report_save_path, 'w') as f:
                f.write(class_report)
                
            self.save_plots(test_labels, preds)
        except ValueError as e:
            logger.info(f"test data is not sufficient to test the model: {e}")

    def save_model(self, trainer):
        logger.info(f"Saving final model to {self.model_save_path}")
        trainer.save_model(self.model_save_path)
        self.tokenizer.save_pretrained(self.model_save_path)

    def cleanup_val_model(self):
        if os.path.exists(self.val_model_save_path):
            logger.info(f"Deleting validation model directory: {self.val_model_save_path}")
            shutil.rmtree(self.val_model_save_path)

    def run(self):
        df = self.load_and_clean_data()
        train_dataset, test_dataset, test_labels = self.prepare_data(df)
        num_labels = len(self.label_encoder.classes_)
        self.initialize_model(num_labels)
        trainer = self.train_model(train_dataset, test_dataset)
        self.evaluate_model(trainer, test_dataset, test_labels)
        self.save_model(trainer)
        self.cleanup_val_model()


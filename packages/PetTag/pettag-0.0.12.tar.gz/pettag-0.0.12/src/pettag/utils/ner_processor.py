from pettag.utils.logging_setup import get_logger
from transformers import DataCollatorForTokenClassification
import time
import torch
from tqdm.auto import tqdm
import os
from torch.utils.data import DataLoader

os.environ["TOKENIZERS_PARALLELISM"] = "true"

from transformers import DataCollatorWithPadding
from tqdm import tqdm
import time
import numpy as np

def get_date():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

class NERProcessor:
    def __init__(self, ner_model, tokenizer=None, text_column="text", device=None, batch_size=1024):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # Optimization: use torch.compile if on PyTorch 2.0+
        self.model = ner_model.to(self.device)
        self.model.to(self.device)
        self.tokenizer = tokenizer or ner_model.tokenizer
        self.id2label = self.model.config.id2label
        self.text_column = text_column
        self.batch_size = batch_size

    def predict(self, dataset):
        self.model.eval()
        
        # 1. Include index in the batch to prevent misalignment
        def collate_fn(batch_items):
            # batch_items is a list of dicts from the dataset
            indices = [item['idx_internal'] for item in batch_items]
            texts = [item[self.text_column] for item in batch_items]
            
            encodings = self.tokenizer(
                texts, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512,
                return_offsets_mapping=True
            )
            return encodings, texts, indices

        # Add a temporary index column to the dataset
        indexed_ds = dataset.add_column("idx_internal", range(len(dataset)))

        loader = DataLoader(
            indexed_ds, 
            batch_size=self.batch_size, 
            collate_fn=collate_fn,
            num_workers=4,
            pin_memory=True
        )

        # Dictionary to store results by their true index
        indexed_results = {}

        with torch.inference_mode():
            for batch_enc, texts, indices in tqdm(loader, desc="Inference"):
                inputs = {k: v.to(self.device, non_blocking=True) 
                         for k, v in batch_enc.items() if k in ["input_ids", "attention_mask"]}
                
                with torch.amp.autocast('cuda' if 'cuda' in self.device else 'cpu'):
                    logits = self.model(**inputs).logits
                    batch_preds = logits.argmax(dim=-1).cpu().numpy()
                
                # Store offsets on CPU immediately
                offsets = batch_enc["offset_mapping"].numpy()

                # Process this batch and store by index
                for i in range(len(indices)):
                    real_idx = indices[i]
                    indexed_results[real_idx] = {
                        "preds": batch_preds[i],
                        "offsets": offsets[i],
                        "text": texts[i]
                    }

        # 2. Re-sort based on the original index to ensure alignment
        sorted_indices = sorted(indexed_results.keys())
        all_preds = [indexed_results[i]["preds"] for i in sorted_indices]
        all_offsets = [indexed_results[i]["offsets"] for i in sorted_indices]
        all_texts = [indexed_results[i]["text"] for i in sorted_indices]

        return self._finalize_results(dataset, all_preds, all_offsets, all_texts)

    def _finalize_results(self, dataset, all_preds, all_offsets, all_texts):
        # Pre-allocate lists for each category
        # Using separate lists is faster than appending to a dict of lists
        final_disease = [[] for _ in range(len(all_texts))]
        final_symptom = [[] for _ in range(len(all_texts))]
        final_pathogen = [[] for _ in range(len(all_texts))]

        for i in range(len(all_texts)):
            text = all_texts[i]
            row_preds = all_preds[i]
            row_offsets = all_offsets[i]

            # 1. Filter out special tokens (where start == end)
            # This handles [CLS], [SEP], and [PAD] automatically
            mask = row_offsets[:, 0] != row_offsets[:, 1]
            valid_indices = np.where(mask)[0]

            curr_tag = None
            curr_start = -1
            curr_end = -1

            for idx in valid_indices:
                label = self.id2label[row_preds[idx]]
                
                # Case 1: Outside an entity
                if label == "O":
                    if curr_tag:
                        self._append_ent(text, curr_tag, curr_start, curr_end, 
                                        final_disease[i], final_symptom[i], final_pathogen[i])
                        curr_tag = None
                    continue

                prefix = label[0]  # 'B' or 'I'
                tag = label[2:]    # 'DISEASE', 'SYMPTOMS', 'ETIOLOGY'
                start, end = row_offsets[idx]

                # Case 2: Start of a new entity (B-tag or change in category)
                if prefix == "B" or curr_tag != tag:
                    if curr_tag:
                        self._append_ent(text, curr_tag, curr_start, curr_end, 
                                        final_disease[i], final_symptom[i], final_pathogen[i])
                    
                    curr_tag = tag
                    curr_start = int(start)
                    curr_end = int(end)
                
                # Case 3: Continuation of an entity (I-tag)
                else:
                    curr_end = int(end)

            # 2. Final flush for the last entity in the sequence
            if curr_tag:
                self._append_ent(text, curr_tag, curr_start, curr_end, 
                                final_disease[i], final_symptom[i], final_pathogen[i])

        # 3. Securely join back to the dataset
        return dataset.add_column("disease_extraction", final_disease) \
                    .add_column("symptom_extraction", final_symptom) \
                    .add_column("pathogen_extraction", final_pathogen)

    def _append_ent(self, text, tag, start, end, d_list, s_list, p_list):
        """Helper to route extracted text to the correct list."""
        snippet = text[start:end]
        if tag == "DISEASE": d_list.append(snippet)
        elif tag == "SYMPTOMS": s_list.append(snippet)
        elif tag == "ETIOLOGY": p_list.append(snippet)
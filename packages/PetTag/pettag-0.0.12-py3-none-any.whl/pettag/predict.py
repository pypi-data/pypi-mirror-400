from pettag.utils.dataset import DatasetProcessor
from pettag.utils.ner_processor import NERProcessor
from pettag.utils.embedding_processor import ICDCodeMapper
from pettag.utils.logging_setup import get_logger
from datasets import Dataset, load_dataset, Dataset, load_from_disk, concatenate_datasets
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForTokenClassification, AutoTokenizer
from collections import defaultdict
from typing import Optional, Dict, Any, Union, Tuple
import torch
import torch.nn.functional as F
import pandas as pd
import numpy as np
import json
import os
from tqdm import tqdm
import time


class DiseaseCoder:
    """Codes disease text data using pre-trained NER and embedding models.

    Args:
        framework (str): Coding framework ('icd11', 'icd10', 'snomed'). Defaults to 'icd11'.
        dataset (Union[str, Dataset], optional): Path to dataset file or HuggingFace Dataset.
        split (str): Dataset split to use. Defaults to 'train'.
        model (str): HuggingFace NER model path. Defaults to 'seanfarrell/bert-base-uncased'.
        tokenizer (str, optional): Tokenizer path. Defaults to model if not provided.
        batch_size (int): Batch size for processing. Defaults to 16.
        synonyms_dataset (str): Path to synonyms dataset.
        synonyms_embeddings_dataset (str): Path to precomputed embeddings.
        embedding_model (str): Sentence transformer model name.
        text_column (str): Column containing text. Defaults to 'text'.
        label_column (str): Column containing labels. Defaults to 'labels'.
        cache (bool): Whether to use caching. Defaults to True.
        logs (str, optional): Path to save logs.
        device (str, optional): Computation device. Auto-detected if None.
        output_dir (str, optional): Output directory for results.
    """

    def __init__(
        self,
        framework: str = "icd11",
        dataset: Optional[Union[str, Dataset]] = None,
        split: str = "train",
        ner_model: str = "seanfarrell/bert-base-uncased",
        tokenizer: Optional[str] = None,
        batch_size: int = 16,
        synonyms_dataset: str = "seanfarrell/ICD-11_synonyms",
        synonyms_embeddings_dataset: str = "cache/ICD-11_synonyms_embeddings.pt",
        embedding_model: str = "seanfarrell/icd11_synonym_model",
        text_column: str = "text",
        label_column: str = "labels",
        cache: bool = True,
        logs: Optional[str] = None,
        device: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        # Core attributes
        self.framework = framework
        self.dataset = dataset
        self.embedding_model = embedding_model
        self.split = split
        self.text_column = text_column
        self.label_column = label_column
        self.batch_size = batch_size
        self.cache = cache
        self.logs = logs
        self.output_dir = output_dir
        self.num_runs = 0

        # Device setup with optimization
        if device is None:
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Logger setup
        self.logger = self._setup_logger()

        # Dataset processor
        self.dataset_processor = DatasetProcessor(cache=self.cache)

        # Model initialization with optimizations
        self.logger.info(f"Initializing NER pipeline on {self.device}")
        self.ner_model = AutoModelForTokenClassification.from_pretrained(ner_model)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer or ner_model, use_fast=True)
        # Embedding model initialization
        self.embedding_model = SentenceTransformer(embedding_model, device=self.device)

        # Use compile for PyTorch 2.0+ speedup (optional)
        if hasattr(torch, "compile") and "cuda" in self.device:
            try:
                #self.ner_model = torch.compile(self.ner_model, mode="reduce-overhead")
                self.embedding_model = torch.compile(
                    self.embedding_model, mode="reduce-overhead"
                )
                self.logger.info("Applied torch.compile() to NER and Embedding model")
            except Exception as e:
                self.logger.warning(f"Could not compile embedding model: {e}")

        # ICD lookup initialization
        icd_data = None
        if framework:
            icd_data = self._load_or_create_icd_lookup(
                synonyms_dataset, synonyms_embeddings_dataset
            )
            self.logger.info(f"Initialized {framework.upper()} ICDCodeMapper")
        else:
            self.logger.warning("framework=None specified. NER extraction only.")

        # Model processor
        self.model_processor = NERProcessor(
            ner_model=self.ner_model,
            tokenizer=self.tokenizer,
            text_column=self.text_column,
            device=self.device,
            batch_size=batch_size,
        )
        
        self.icd_mapper = ICDCodeMapper(
            framework=self.framework,
            icd_embedding=icd_data,
            embedding_model=self.embedding_model,
            device=self.device,
            batch_size=batch_size,
        )

    ######################## Logger Setup ########################
    def _setup_logger(self) -> Any:
        """Setup logger."""
        from pettag.utils.logging_setup import get_logger

        return get_logger(log_dir=self.logs) if self.logs else get_logger()

    ######################## Embeddings Preperation ########################
    def _load_or_create_icd_lookup(
        self, synonyms_dataset: str, synonyms_embeddings_dataset: str
    ) -> Dict[str, Any]:
        """Load precomputed embeddings or create new ones efficiently."""
        try:
            self.logger.info(f"Loading ICD lookup from {synonyms_embeddings_dataset}")
            data = torch.load(
                synonyms_embeddings_dataset, map_location=self.device, weights_only=True
            )
            # Move tensors to device efficiently with non_blocking
            return {
                k: (
                    v.to(self.device, non_blocking=True)
                    if isinstance(v, torch.Tensor)
                    else v
                )
                for k, v in data.items()
            }
        except (FileNotFoundError, Exception) as e:
            self.logger.info(
                "Generating new ICD embedding store (first run only, may take a few minutes)"
            )
            icd_dataset = load_dataset(
                synonyms_dataset, split="train", download_mode="force_redownload"
            )
            return self._preprocess_icd_lookup(icd_dataset, synonyms_embeddings_dataset)

    def _preprocess_icd_lookup(
        self, disease_code_lookup, save_path: str = "icd_lookup.pt"
    ) -> Dict[str, Any]:
        """
        Preprocess ICD lookup into optimized PyTorch format with normalized embeddings.

        Optimizations:
        - Vectorized operations where possible
        - Single-pass parent grouping
        - Efficient tensor operations
        """
        self.logger.info("Preprocessing ICD lookup into PyTorch format...")

        # Extract and normalize embeddings efficiently
        if self.embedding_model == 'sentence-transformers/all-MiniLM-L6-v2':
            self.logger.info("Using precomputed embeddings from dataset")
            embeddings = torch.tensor(
                np.asarray(disease_code_lookup["embeddings"], dtype=np.float32),
                dtype=torch.float32,
            )
        else:
            self.logger.info("Computing embeddings using embedding model")
            embeddings = self.embedding_model.encode(
                disease_code_lookup["Title_synonym"],
                convert_to_tensor=True,
                batch_size=128,
                show_progress_bar=True,
                device=self.device,
            )
            
        embeddings = F.normalize(embeddings, dim=1)
        self.logger.info(f"Embeddings shape: {embeddings.shape}")

        # Extract metadata using vectorized operations
        icd11_codes = [str(c) for c in disease_code_lookup["icd11Code"]]

        metadata = {
            "icd11Code": icd11_codes,
            "icd11Title": [str(t) for t in disease_code_lookup["icd11Title"]],
            "Title_synonym": [str(s) for s in disease_code_lookup["Title_synonym"]],
            "icd11URI": [str(u) for u in disease_code_lookup["icd11URI"]],
            "ChapterNo": [str(ch) for ch in disease_code_lookup["ChapterNo"]],
            "icd10Code": [str(c) for c in disease_code_lookup["icd10Code"]],
            "icd10Title": [str(t) for t in disease_code_lookup["icd10Title"]],
            "snomedCode": [str(c) for c in disease_code_lookup["snomedCode"]],
            "snomedTitle": [str(t) for t in disease_code_lookup["snomedTitle"]],
        }

        # Build parent → subcode mapping efficiently (single pass)
        parent_groups = {}
        for idx, code in enumerate(icd11_codes):
            parent = code.split(".")[0]
            parent_groups.setdefault(parent, []).append(idx)

        # Only keep parents with multiple subcodes
        parent_to_subcodes_keys = []
        parent_to_subcodes_values = []
        for parent, indices in parent_groups.items():
            if len(indices) > 1:
                parent_to_subcodes_keys.append(parent)
                parent_to_subcodes_values.append(
                    torch.tensor(indices, dtype=torch.long)
                )

        # Create .Z code mask efficiently
        z_code_mask = torch.tensor(
            [c.endswith(".Z") for c in icd11_codes], dtype=torch.bool
        )

        # Ensure save path exists
        save_path = save_path if save_path.endswith(".pt") else f"{save_path}.pt"
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

        # Create lookup dictionary
        lookup_dict = {
            "lookup_embeddings": embeddings.cpu(),
            "parent_to_subcodes_keys": parent_to_subcodes_keys,
            "parent_to_subcodes_values": parent_to_subcodes_values,
            "z_code_mask": z_code_mask.cpu(),
            **metadata,
        }

        torch.save(lookup_dict, save_path)
        self.logger.info(f"ICD lookup saved to {save_path}")

        # Return device-ready dictionary with async transfers
        return {
            k: (
                v.to(self.device, non_blocking=True)
                if isinstance(v, torch.Tensor)
                else v
            )
            for k, v in lookup_dict.items()
        }

    ######################## Dataset Preperation ########################

    def _prepare_single_text(self, text: str) -> Dataset:
        """Prepare single text input with validation."""
        if not isinstance(text, str):
            error_msg = "Input text must be a string."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        clean_text = text.strip()
        df = pd.DataFrame({self.text_column: [clean_text]})
        return Dataset.from_pandas(df)

    def _prepare_dataset(self) -> Tuple[Dataset, Dataset]:
        """Load and validate dataset with caching."""
        if isinstance(self.dataset, Dataset):
            original_data = self.dataset
        elif isinstance(self.dataset, str):
            original_data = self.dataset_processor.load_dataset_file(
                self.dataset, split=self.split
            )
        else:
            raise ValueError("`dataset` must be a filepath or HuggingFace Dataset.")

        validated = self.dataset_processor.validate_dataset(
            dataset=original_data, text_column=self.text_column
        )
        # if self.label_column not in validated.column_names add it
        if self.label_column not in validated.column_names:
            validated = validated.add_column(
                self.label_column, ["" for _ in range(len(validated))]
            )

        target_dataset, completed_dataset = self.dataset_processor.load_cache(
            dataset=validated, cache_column=self.label_column
        )
        return target_dataset, completed_dataset
    
    #######

    def _process_in_chunks(
        self,
        target_dataset: Dataset,
        chunk_size: int = 500_000_000,
        chunk_cache_path: str = "./pettag_chunk_cache",
    ) -> Dataset:
        """Process dataset in chunks with memory-efficient disk caching."""
        
        total_records = len(target_dataset)
        os.makedirs(chunk_cache_path, exist_ok=True)

        # 1. Identify completed chunks
        # We look for directories created by save_to_disk
        completed_chunk_ids = set()
        if os.path.exists(chunk_cache_path):
            for d in os.listdir(chunk_cache_path):
                if d.startswith("chunk_"):
                    try:
                        completed_chunk_ids.add(int(d.split("_")[1]))
                        self.logger.info(f"Found completed chunk: {d}")
                    except ValueError:
                        continue

        # 2. Process chunks
        date_time = time.strftime("%Y-%m-%d %H:%M:%S")
        for i in tqdm(range(0, total_records, chunk_size), desc=f"[{date_time} |   INFO  | PetCoder] Chunk Processing"):
            chunk_id = (i // chunk_size) + 1
            chunk_save_path = os.path.join(chunk_cache_path, f"chunk_{chunk_id}")

            if chunk_id in completed_chunk_ids:
                continue

            # Select and process
            chunk = target_dataset.select(range(i, min(i + chunk_size, total_records)))
            
            # Your processing logic
            processed_chunk = self.model_processor.predict(dataset=chunk)
            processed_chunk = self.icd_mapper.map_diseases(processed_chunk)

            # Standard Hugging Face saving (highly optimized)
            processed_chunk.save_to_disk(chunk_save_path)
            date_time = time.strftime("%Y-%m-%d %H:%M:%S")
            tqdm.write(f"[{date_time} |   INFO  | PetCoder] Processing chunk {chunk_id} of {((total_records - 1) // chunk_size) + 1}")
            
        # 3. Final aggregation (Memory Efficient)
        # We sort to ensure the order of the original dataset is preserved
        chunk_dirs = sorted(
            [
                os.path.join(chunk_cache_path, d)
                for d in os.listdir(chunk_cache_path)
                if d.startswith("chunk_")
            ],
            key=lambda x: int(os.path.basename(x).split("_")[1]),
        )

        self.logger.info(f"Assembling {len(chunk_dirs)} chunks from disk.")
        
        # load_from_disk uses memory mapping; it doesn't load data into RAM yet
        loaded_chunks = [load_from_disk(d) for d in chunk_dirs]
        
        # concatenate_datasets is a pointer-based operation, very fast
        processed_dataset = concatenate_datasets(loaded_chunks)
        self.logger.info("All chunks assembled successfully. You may delete the chunk cache directory if desired.")
        return processed_dataset

    ######################## Single Text Printing ########################

    def _print_output(self, input_text: str, output_data: Any) -> None:
        """Print formatted output."""
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        pretty_output = json.dumps(
            output_data, indent=4, ensure_ascii=False, sort_keys=True
        )
        print(f"[{timestamp} | SUCCESS | PetCoder] Input:  {input_text}")
        print(f"[{timestamp} | SUCCESS | PetCoder] Output:\n{pretty_output}")

    ################################################################################

    def _run(
        self,
        text: Optional[str] = None,
        dataset: Optional[str] = None,
        chunk_size: int = 250_000_000,
        chunk_cache_path: Optional[str] = "./pettag_chunk_cache",
    ) -> Optional[Any]:

        self.num_runs += 1

        # Validation
        if text and self.dataset:
            raise ValueError("Provide either text or dataset, not both.")

        # --------------------
        # Single-text pathway
        # --------------------
        if text:
            self.logger.warning("Coding single text. Use dataset for bulk processing.")
            target_dataset = self._prepare_single_text(text)
            result = self.model_processor.predict(dataset=target_dataset)
            result = self.icd_mapper.map_diseases(result)

            output = {
                "disease_extraction": result['disease_extraction'][0],
                "pathogen_extraction": result["pathogen_extraction"][0],
                "symptom_extraction": result["symptom_extraction"][0],
            }

            self._print_output(text, output)
            return output

        # --------------------
        # Dataset pathway
        # --------------------
        if dataset:
            self.dataset = dataset

        if not self.dataset:
            raise ValueError("Provide either text string or dataset path.")

        target_dataset, completed_dataset = self._prepare_dataset()

        # --------------------
        # Chunked processing
        # --------------------
        if chunk_size and len(target_dataset) > chunk_size:
            self.logger.info(f"Large dataset detected. Batching with chunk size {chunk_size}.")
            processed_dataset = self._process_in_chunks(
                target_dataset=target_dataset,
                chunk_size=chunk_size,
                chunk_cache_path=chunk_cache_path or "./pettag_chunk_cache",
            )
        # --------------------
        # Non-chunked pathway
        # --------------------
        else:
            processed_dataset = self.model_processor.predict(dataset=target_dataset)
            processed_dataset = self.icd_mapper.map_diseases(processed_dataset)

        # --------------------
        # Persist output
        # --------------------
        self.dataset_processor.save_dataset_file(
            target_dataset=processed_dataset,
            completed_dataset=completed_dataset,
            output_dir=self.output_dir,
        )

        return None

    #################################################################################

    def predict(
        self, text: Optional[str] = None, dataset: Optional[str] = None, output_dir: Optional[str] = None
    ) -> Optional[Any]:
        """
        Predict on provided text or dataset.

        Args:
            text: Single text string to code
            dataset: Path to dataset file

        Returns:
            Dictionary with extractions for text input, None for dataset operations
        """
        if self.num_runs > 1:
            self.logger.warning(
                "Sequential model runs detected. Consider passing 'dataset' to class init."
            )
        if output_dir is not None:
            self.output_dir = output_dir
        dataset = dataset or self.dataset

        if text is not None:
            return self._run(text=text, dataset=None)
        elif dataset is not None:
            self._run(text=None, dataset=dataset)
            return None
        else:
            self.logger.warning("No text or dataset provided.")
            return None

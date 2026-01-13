import torch
import torch.nn.functional as F
from tqdm import tqdm
from pettag.utils.logging_setup import get_logger
import time

class ICDCodeMapper:
    """Handles disease coding with optimized batch processing."""
    
    def __init__(
        self,
        framework,
        icd_embedding,
        embedding_model,
        device=None,
        batch_size=256,
        similarity_threshold=0.70,
    ):
        self.device = device if device else ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self.framework = framework
        self.similarity_threshold = similarity_threshold
        self.logger = get_logger()
        
        # Initialize ICD lookup
        self._setup_vectorization(icd_embedding)

    def _setup_vectorization(self, icd_embedding):
        """Helper to set up vectorization tensors."""
        self.lookup_embeddings = icd_embedding["lookup_embeddings"].to(self.device, non_blocking=True)
        self.icd11_codes = icd_embedding["icd11Code"]
        self.icd11_titles = icd_embedding.get("icd11Title", None)
        self.icd11_uris = icd_embedding.get("icd11URI", None)
        self.chapters = icd_embedding.get("ChapterNo", None)
        self.icd10_codes = icd_embedding.get("icd10Code", None)
        self.icd10_titles = icd_embedding.get("icd10Title", None)
        self.snomed_codes = icd_embedding.get("snomedCode", None)
        self.snomed_titles = icd_embedding.get("snomedTitle", None)
        self.num_codes = len(self.icd11_codes)
        self.z_code_mask = icd_embedding["z_code_mask"].to(self.device, non_blocking=True)

        self.parent_keys = list(icd_embedding["parent_to_subcodes_keys"])
        self.parent_key_to_idx = {k: i for i, k in enumerate(self.parent_keys)}
        
        code_parents_list = [code.split(".")[0] for code in self.icd11_codes]
        code_to_row = [self.parent_key_to_idx.get(p, -1) for p in code_parents_list]
        self.code_to_parent_row = torch.tensor(code_to_row, dtype=torch.long, device=self.device)

        max_subcodes = max(len(v) for v in icd_embedding["parent_to_subcodes_values"])
        self.subcodes_tensor = torch.full((len(self.parent_keys), max_subcodes), -1, dtype=torch.long, device=self.device)
        self.subcodes_mask = torch.zeros((len(self.parent_keys), max_subcodes), dtype=torch.bool, device=self.device)
        
        for i, values in enumerate(icd_embedding["parent_to_subcodes_values"]):
            values_tensor = values.to(self.device, non_blocking=True)
            self.subcodes_tensor[i, :len(values_tensor)] = values_tensor
            self.subcodes_mask[i, :len(values_tensor)] = True

    @torch.inference_mode()
    def _disease_coder_batch(self, encoded, Z_BOOST):
        """
        Internal optimized similarity computation.
        Fixed: Handles -1 padding to prevent CUDA device-side assertions.
        """
        # 1. Compute initial cosine similarities (Batch x Num_Codes)
        sims = F.linear(encoded, self.lookup_embeddings)
        top_scores, top_idx = sims.max(dim=1)

        # 2. Identify which items need refinement
        parent_rows = self.code_to_parent_row[top_idx]
        
        # Create a mask for items that have valid subcodes (row != -1)
        valid_mask = parent_rows >= 0
        
        if not valid_mask.any():
            return top_idx, top_scores

        # 3. Gather Data for Refinement
        active_indices = torch.nonzero(valid_mask, as_tuple=True)[0]
        active_rows = parent_rows[active_indices]

        # Gather subcodes: (Num_Active, Max_Subcodes)
        batch_subcodes = self.subcodes_tensor[active_rows]
        batch_sub_mask = self.subcodes_mask[active_rows]

        # Replace -1 padding with a valid index (0) before gathering
        safe_indices = batch_subcodes.clamp(min=0)

        # 4. Gather Similarities
        active_sims = sims[active_indices]
        batch_sims = active_sims.gather(1, safe_indices)
        
        # 5. Apply Logic (Z-Boost + Masking)
        batch_sims = batch_sims.masked_fill(~batch_sub_mask, -float('inf'))
        
        # Apply Z-boost
        batch_z_boost = self.z_code_mask[safe_indices] * Z_BOOST
        batch_sims = batch_sims + batch_z_boost
        
        # 6. Find New Best
        new_best_local_scores, new_best_local_idx = batch_sims.max(dim=1)
        
        # Map local index back to global code index
        new_best_global_idx = safe_indices.gather(1, new_best_local_idx.unsqueeze(1)).squeeze(1)

        # 7. Update Results
        top_idx[active_indices] = new_best_global_idx
        top_scores[active_indices] = new_best_local_scores

        return top_idx, top_scores
    
    @torch.inference_mode()
    def disease_coder_batch(self, diseases, Z_BOOST=0.06):
        """Encode diseases and find best matching ICD codes."""
        if not diseases:
            return [], []
            
        encoded = self.embedding_model.encode(
            diseases, 
            convert_to_tensor=True, 
            device=self.device,
            batch_size=self.batch_size, 
            show_progress_bar=False, 
            normalize_embeddings=True
        )
        
        if not hasattr(self.embedding_model, "normalize_embeddings"):
            encoded = F.normalize(encoded, dim=1)
            
        final_idx, final_score = self._disease_coder_batch(encoded, Z_BOOST)
        return final_idx.cpu().tolist(), torch.clamp(final_score, max=1.0).cpu().tolist()

    def _format_result(self, disease, idx, score):
        """Format the coding result based on the framework."""
        framework = self.framework.lower()
        
        if framework == "icd11":
            code = self.icd11_codes[idx]
            title = self.icd11_titles[idx] if self.icd11_titles else None
            uri = self.icd11_uris[idx] if self.icd11_uris else None
        elif framework == "icd10":
            code = self.icd10_codes[idx]
            title = self.icd10_titles[idx]
            uri = ""
        elif framework == "snomed":
            code = self.snomed_codes[idx]
            title = self.snomed_titles[idx]
            uri = ""
        else:
            code = self.icd11_codes[idx]
            title = self.icd11_titles[idx] if self.icd11_titles else None
            uri = self.icd11_uris[idx] if self.icd11_uris else None
            
        return {
            "NER Extraction": disease, 
            "Framework": framework.upper(),
            "Code": code, 
            "Title": title,
            "URI": f"https://icd.who.int/browse/2025-01/mms/en#{uri}" if uri else None,
            "Similarity": score,
        }

    def map_diseases(self, dataset, show_progress=True):
        """
        Map diseases to ICD codes with batch processing.
        
        Args:
            dataset: Dataset containing diseases to code
            disease_column: Column name containing disease lists
            show_progress: Whether to show progress bar
        """
        # Collect all unique diseases from the dataset
        all_diseases = set()
        for diseases in dataset['disease_extraction']:
            all_diseases.update(diseases)
        all_diseases_list = list(all_diseases)
        
        # If no diseases found, return dataset with empty disease_extraction column
        if not all_diseases_list:
            return dataset.add_column("disease_extraction", [[] for _ in range(len(dataset))])
        
        # Bulk code all unique diseases
        disease_lookup = {}
        coding_batch_size = self.batch_size * 4
        
        iterator = range(0, len(all_diseases_list), coding_batch_size)
        date_time = time.strftime("%Y-%m-%d %H:%M:%S")
        iterator = tqdm(iterator, desc=f"[{date_time} |   INFO  | PetCoder] Disease Coding")
        
        for batch_start in iterator:
            batch = all_diseases_list[batch_start:batch_start + coding_batch_size]
            indices, scores = self.disease_coder_batch(batch)
            
            for j, disease in enumerate(batch):
                score = round(scores[j], 4)
                if score < self.similarity_threshold:
                    disease_lookup[disease] = {
                        "NER Extraction": disease, 
                        "Framework": None, 
                        "Code": None
                    }
                else:
                    disease_lookup[disease] = self._format_result(disease, indices[j], score)
        
        # Map codes back to each record in the dataset
        def map_codes(example):
            return {
                "disease_extraction": [disease_lookup.get(d, {}) for d in example['disease_extraction']]
            }
        
        result_dataset = dataset.map(
            map_codes, 
            desc="Mapping codes to records" if show_progress else None
        )

        return result_dataset
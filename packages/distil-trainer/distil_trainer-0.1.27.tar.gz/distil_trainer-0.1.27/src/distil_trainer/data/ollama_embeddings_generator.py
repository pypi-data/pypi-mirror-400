"""Ollama Embeddings Generator for generating embeddings using Ollama models."""

from __future__ import annotations

import logging

import numpy as np
from datasets import Dataset, load_dataset
from tqdm import tqdm

try:
    import ollama
except ImportError:
    raise ImportError(
        "ollama is required for OllamaEmbeddingsGenerator. "
        "Install it with: pip install ollama"
    )

logger = logging.getLogger(__name__)


class OllamaEmbeddingsGenerator:
    """
    Generate and store embeddings using Ollama models.
    
    This class uses Ollama's embedding API to generate embeddings
    for texts and saves them as a HuggingFace dataset.
    
    Example:
        >>> generator = OllamaEmbeddingsGenerator(
        ...     model_name="alibayram/distilled-sentence-transformer-c400",
        ...     batch_size=32
        ... )
        >>> dataset = generator.generate(
        ...     source_dataset="BILGEM-AI/BILGE-Synthetic-Stories",
        ...     text_column="text",
        ...     max_samples=1000
        ... )
        >>> generator.push_to_hub("your-username/corpus-with-ollama-embeddings")
    """

    def __init__(
        self,
        model_name: str,
        batch_size: int = 32,
        host: str | None = None,
    ):
        """
        Initialize the Ollama embeddings generator.
        
        Args:
            model_name: Name of the Ollama model to use for embeddings.
            batch_size: Batch size for encoding.
            host: Optional Ollama server host (defaults to localhost:11434).
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.dataset: Dataset | None = None
        
        # Initialize Ollama client with optional host
        kwargs = {}
        if host is not None:
            kwargs['host'] = host
        
        # Test connection and model availability
        try:
            test_response = ollama.embed(
                model=model_name,
                input=["test"],
                **kwargs
            )
            logger.info(f"Successfully connected to Ollama model: {model_name}")
            if 'embeddings' in test_response:
                embedding_dim = len(test_response['embeddings'][0])
                logger.info(f"Embedding dimension: {embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama model: {e}")
            raise

    def generate(
        self,
        source_dataset: str | Dataset,
        text_column: str = "text",
        split: str = "train",
        max_samples: int | None = None,
        embedding_column_name: str = "ollama_embedding",
    ) -> Dataset:
        """
        Generate embeddings for the source dataset using Ollama.
        
        Args:
            source_dataset: HuggingFace dataset ID or Dataset object.
            text_column: Name of the column containing text.
            split: Dataset split to use (if loading from HuggingFace).
            max_samples: Maximum number of samples to process.
            embedding_column_name: Name of the column to store embeddings in.
            
        Returns:
            Dataset with text and Ollama embeddings.
        """
        # Load dataset
        if isinstance(source_dataset, str):
            logger.info(f"Loading dataset: {source_dataset}")
            dataset = load_dataset(source_dataset, split=split)
        else:
            dataset = source_dataset
            
        # Limit samples if requested
        if max_samples is not None and max_samples < len(dataset):
            dataset = dataset.select(range(max_samples))
            logger.info(f"Limited to {max_samples} samples")
            
        logger.info(f"Generating Ollama embeddings for {len(dataset)} samples...")
        
        texts = dataset[text_column]
        all_embeddings = []
        
        # Process in batches
        for i in tqdm(range(0, len(texts), self.batch_size), desc="Generating embeddings"):
            batch_texts = texts[i:i + self.batch_size]
            
            try:
                response = ollama.embed(
                    model=self.model_name,
                    input=batch_texts
                )
                
                # Extract embeddings from response
                if 'embeddings' in response:
                    batch_embeddings = response['embeddings']
                elif 'embedding' in response:
                    # Handle single embedding response
                    batch_embeddings = [response['embedding']]
                else:
                    raise ValueError(f"Unexpected response format: {response.keys()}")
                
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i}: {e}")
                raise
        
        # Add embeddings to dataset
        embeddings_array = np.array(all_embeddings)
        dataset = dataset.add_column(embedding_column_name, embeddings_array.tolist())
        
        logger.info(
            f"Generated {len(all_embeddings)} embeddings "
            f"(dim={len(all_embeddings[0])})"
        )
        
        self.dataset = dataset
        return self.dataset
    
    def push_to_hub(
        self,
        repo_id: str,
        private: bool = False,
        token: str | None = None,
        commit_message: str | None = None,
    ) -> str:
        """
        Push the generated dataset to HuggingFace Hub.
        
        Args:
            repo_id: Repository ID on HuggingFace Hub.
            private: Whether the repository should be private.
            token: HuggingFace Hub token for authentication.
            commit_message: Custom commit message.
            
        Returns:
            URL of the uploaded dataset.
        """
        if self.dataset is None:
            raise ValueError("No dataset to push. Call generate() first.")
            
        if commit_message is None:
            commit_message = f"Add Ollama embeddings from {self.model_name}"
            
        logger.info(f"Pushing dataset to: {repo_id}")
        
        self.dataset.push_to_hub(
            repo_id=repo_id,
            private=private,
            token=token,
            commit_message=commit_message,
        )
        
        url = f"https://huggingface.co/datasets/{repo_id}"
        logger.info(f"Dataset pushed: {url}")
        return url
    
    def save_to_disk(self, path: str) -> None:
        """
        Save the generated dataset to disk.
        
        Args:
            path: Path to save the dataset.
        """
        if self.dataset is None:
            raise ValueError("No dataset to save. Call generate() first.")
            
        self.dataset.save_to_disk(path)
        logger.info(f"Dataset saved to: {path}")
    
    def generate_and_push(
        self,
        source_dataset: str | Dataset,
        repo_id: str,
        text_column: str = "text",
        split: str = "train",
        push_every: int = 100000,
        private: bool = False,
        token: str | None = None,
        max_samples: int | None = None,
        embedding_column_name: str = "ollama_embedding",
    ) -> str:
        """
        Generate embeddings and push to HuggingFace Hub iteratively.
        
        This method processes the dataset in chunks and pushes updates
        to HuggingFace Hub every `push_every` examples.
        
        Args:
            source_dataset: HuggingFace dataset ID or Dataset object.
            repo_id: Repository ID on HuggingFace Hub.
            text_column: Name of the column containing text.
            split: Dataset split to use (if loading from HuggingFace).
            push_every: Push to hub after this many examples (default: 10000).
            private: Whether the repository should be private.
            token: HuggingFace Hub token for authentication.
            max_samples: Maximum number of samples to process.
            embedding_column_name: Name of the column to store embeddings in.
            
        Returns:
            URL of the uploaded dataset.
        """
        from datasets import concatenate_datasets
        
        # Load dataset
        if isinstance(source_dataset, str):
            logger.info(f"Loading dataset: {source_dataset}")
            dataset = load_dataset(source_dataset, split=split)
        else:
            dataset = source_dataset
            
        # Limit samples if requested
        if max_samples is not None and max_samples < len(dataset):
            dataset = dataset.select(range(max_samples))
            logger.info(f"Limited to {max_samples} samples")
        
        total_samples = len(dataset)
        logger.info(f"Processing {total_samples} samples, pushing every {push_every}...")
        
        processed_dataset = None
        processed_count = 0
        
        # Process in chunks
        for start_idx in range(0, total_samples, push_every):
            end_idx = min(start_idx + push_every, total_samples)
            chunk = dataset.select(range(start_idx, end_idx))
            texts = chunk[text_column]
            
            logger.info(f"Processing chunk {start_idx}-{end_idx} ({end_idx - start_idx} samples)")
            
            # Generate embeddings for this chunk
            all_embeddings = []
            for i in tqdm(
                range(0, len(texts), self.batch_size),
                desc=f"Chunk {start_idx}-{end_idx}"
            ):
                batch_texts = texts[i:i + self.batch_size]
                
                try:
                    response = ollama.embed(
                        model=self.model_name,
                        input=batch_texts
                    )
                    
                    if 'embeddings' in response:
                        batch_embeddings = response['embeddings']
                    elif 'embedding' in response:
                        batch_embeddings = [response['embedding']]
                    else:
                        raise ValueError(f"Unexpected response format: {response.keys()}")
                    
                    all_embeddings.extend(batch_embeddings)
                    
                except Exception as e:
                    logger.error(f"Error generating embeddings for batch {i}: {e}")
                    raise
            
            # Add embeddings to chunk
            embeddings_array = np.array(all_embeddings)
            chunk = chunk.add_column(embedding_column_name, embeddings_array.tolist())
            
            # Concatenate with previous chunks
            if processed_dataset is None:
                processed_dataset = chunk
            else:
                processed_dataset = concatenate_datasets([processed_dataset, chunk])
            
            processed_count = end_idx
            
            # Push checkpoint
            commit_msg = (
                f"Checkpoint: {processed_count}/{total_samples} samples "
                f"from {self.model_name}"
            )
            logger.info(f"Pushing checkpoint: {processed_count}/{total_samples}")
            
            processed_dataset.push_to_hub(
                repo_id=repo_id,
                private=private,
                token=token,
                commit_message=commit_msg,
            )
        
        self.dataset = processed_dataset
        url = f"https://huggingface.co/datasets/{repo_id}"
        logger.info(f"Completed! Dataset pushed: {url}")
        return url

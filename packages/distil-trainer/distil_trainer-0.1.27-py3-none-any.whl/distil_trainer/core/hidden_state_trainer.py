"""Hidden State Distillation Trainer for transformer models.

Trains a student model to match teacher hidden states from the last layer
before the LM head. Uses the last token's hidden state as the representation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import os
import shutil

import torch
from datasets import Dataset, load_dataset
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    get_scheduler,
)

logger = logging.getLogger(__name__)


@dataclass
class HiddenStateTrainerConfig:
    """Configuration for hidden state distillation training."""
    
    # Model
    student_model: str
    hidden_dim: int = 3840  # Gemma3 hidden dimension
    
    # Training
    learning_rate: float = 2e-5
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 1
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    max_seq_length: int = 2048
    
    # Loss
    loss_type: Literal["cosine", "smooth_l1", "mse"] = "cosine"
    
    # Columns
    text_column: str = "texts"
    embedding_column: str = "embeddings"
    
    # Output
    output_dir: str = "./trained_model"
    save_steps: int = 500
    save_total_limit: int = 1  # Only keep the last checkpoint
    logging_steps: int = 50
    
    # Hub
    push_to_hub: bool = False
    hub_model_id: str | None = None
    hub_token: str | None = None
    
    # Device
    device: str = "auto"
    
    # Optimization
    use_bf16: bool = True
    compile_model: bool = False
    use_flash_attention: bool = True
    gradient_checkpointing: bool = True
    
    # WandB
    use_wandb: bool = False
    wandb_project: str = "hidden-state-distillation"
    wandb_run_name: str | None = None


class HiddenStateDistillationTrainer:
    """
    Trainer for distilling transformer models using hidden states.
    
    Trains a student model (e.g., Gemma3) to match pre-computed teacher
    hidden states from the last transformer layer before the LM head.
    
    Since embeddings and LM head weights are tied, training the hidden
    states effectively trains both the embedding layer and LM head.
    
    Example:
        >>> config = HiddenStateTrainerConfig(
        ...     student_model="alibayram/gemma-3-12b-it-tr-v64k",
        ...     use_bf16=True,
        ...     use_flash_attention=True,
        ... )
        >>> trainer = HiddenStateDistillationTrainer(config)
        >>> trainer.train("your-dataset-with-embeddings")
    """
    
    def __init__(self, config: HiddenStateTrainerConfig):
        self.config = config
        self.device = self._get_device()
        self.model = None
        self.tokenizer = None
        self._wandb = None
        self.optimizer = None
        self.scheduler = None
        self.global_step = 0
        
        self._load_model()
        
    def _get_device(self) -> torch.device:
        if self.config.device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif torch.backends.mps.is_available():
                return torch.device("mps")
            return torch.device("cpu")
        return torch.device(self.config.device)
    
    def _load_model(self) -> None:
        """Load the student model and tokenizer."""
        logger.info(f"Loading student model: {self.config.student_model}")
        
        # Model kwargs
        model_kwargs = {
            "torch_dtype": torch.bfloat16 if self.config.use_bf16 else torch.float32,
        }
        
        # Flash Attention
        if self.config.use_flash_attention:
            try:
                model_kwargs["attn_implementation"] = "flash_attention_2"
                logger.info("Using Flash Attention 2")
            except Exception as e:
                logger.warning(f"Flash Attention not available: {e}")
        
        # Load model
        try:
            from transformers import Gemma3ForConditionalGeneration
            logger.info("Imported Gemma3ForConditionalGeneration")
            model_class = Gemma3ForConditionalGeneration
        except ImportError:
            logger.warning("Gemma3ForConditionalGeneration not found, checking if model is gemma-3...")
            if "gemma-3" in self.config.student_model.lower():
                 logger.warning("Model appears to be Gemma-3 but class not found in transformers. Using AutoModelForCausalLM.")
            model_class = AutoModelForCausalLM

        # Override if specific
        if "gemma-3" in self.config.student_model.lower():
             try:
                 from transformers import Gemma3ForConditionalGeneration
                 model_class = Gemma3ForConditionalGeneration
                 logger.info("Using Gemma3ForConditionalGeneration for Gemma 3 model")
             except ImportError:
                 pass
        
        self.model = model_class.from_pretrained(
            self.config.student_model,
            **model_kwargs
        )
        self.model.to(self.device)
        
        # Gradient checkpointing
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
            logger.info("Gradient checkpointing enabled")
        
        # Compile (optional)
        if self.config.compile_model and self.device.type == "cuda":
            try:
                self.model = torch.compile(self.model)
                logger.info("Model compiled with torch.compile()")
            except Exception as e:
                logger.warning(f"torch.compile() failed: {e}")
        
        # Load tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.student_model)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "left"  # For causal LM
            logger.info("Tokenizer loaded successfully.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to load tokenizer: {e}")
            raise e
        
        # Log model info
        num_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        logger.info(f"Model loaded: {num_params:,} params ({trainable_params:,} trainable)")
    
    def _get_loss_fn(self):
        """Get the loss function based on config."""
        if self.config.loss_type == "cosine":
            def cosine_loss(student: torch.Tensor, teacher: torch.Tensor) -> torch.Tensor:
                similarity = torch.nn.functional.cosine_similarity(student, teacher, dim=-1)
                return (1 - similarity).mean()
            return cosine_loss
        elif self.config.loss_type == "smooth_l1":
            return torch.nn.SmoothL1Loss()
        elif self.config.loss_type == "mse":
            return torch.nn.MSELoss()
        else:
            raise ValueError(f"Unknown loss type: {self.config.loss_type}")
    
    def _get_last_hidden_state(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Get the hidden state of the last non-padding token.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
            
        Returns:
            Hidden states for last token [batch_size, hidden_dim]
        """
        # Forward pass with hidden states output
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            return_dict=True,
        )
        
        # Get last layer hidden states [batch_size, seq_len, hidden_dim]
        last_hidden_state = outputs.hidden_states[-1]
        
        # Find the position of the last non-padding token for each sequence
        # attention_mask: 1 for real tokens, 0 for padding
        # Sum along seq_len dim gives the number of real tokens
        seq_lengths = attention_mask.sum(dim=1) - 1  # -1 for 0-indexing
        
        batch_size = input_ids.size(0)
        batch_indices = torch.arange(batch_size, device=self.device)
        
        # Extract hidden state at last token position for each sequence
        last_token_hidden = last_hidden_state[batch_indices, seq_lengths]
        
        return last_token_hidden
    
    def train(
        self,
        dataset: str | Dataset,
        split: str = "test",
        eval_dataset: str | Dataset | None = None,
        resume_from_checkpoint: str | None = None,
        initial_global_step: int = 0,
    ) -> dict:
        """
        Train the student model to match teacher hidden states.
        
        Args:
            dataset: HuggingFace dataset with pre-computed embeddings.
            split: Dataset split to use.
            eval_dataset: Optional evaluation dataset.
            resume_from_checkpoint: Path to checkpoint to resume from.
            initial_global_step: Step to start from if not resuming from checkpoint (skips data).
            
        Returns:
            Training metrics.
        """
        # Load dataset
        if isinstance(dataset, str):
            logger.info(f"Loading dataset: {dataset}")
            try:
                train_ds = load_dataset(dataset, split=split)
                logger.info("Dataset loaded successfully.")
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Failed to load dataset: {e}")
                raise e
        else:
            train_ds = dataset
        
        text_column = self.config.text_column
        embedding_column = self.config.embedding_column
        
        logger.info(f"Dataset size: {len(train_ds)}")
        logger.info(f"Text column: {text_column}, Embedding column: {embedding_column}")
        
        # Initialize WandB
        if self.config.use_wandb:
            try:
                import wandb
                wandb.init(
                    project=self.config.wandb_project,
                    name=self.config.wandb_run_name,
                    config={
                        "student_model": self.config.student_model,
                        "hidden_dim": self.config.hidden_dim,
                        "learning_rate": self.config.learning_rate,
                        "num_epochs": self.config.num_epochs,
                        "batch_size": self.config.batch_size,
                        "loss_type": self.config.loss_type,
                    }
                )
                self._wandb = wandb
            except ImportError:
                logger.warning("wandb not installed, disabling logging")
                self._wandb = None
        
        # Setup optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )
        
        # Setup scheduler
        steps_per_epoch = len(train_ds) // (self.config.batch_size * self.config.gradient_accumulation_steps)
        total_steps = steps_per_epoch * self.config.num_epochs
        warmup_steps = int(total_steps * self.config.warmup_ratio)
        
        self.scheduler = get_scheduler(
            "linear",
            optimizer=self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps,
        )
        
        # Loss function
        loss_fn = self._get_loss_fn()
        
        # Training loop
        self.model.train()
        self.global_step = initial_global_step
        start_epoch = 0
        
        # Resume from checkpoint
        if resume_from_checkpoint:
            logger.info(f"Resuming from checkpoint: {resume_from_checkpoint}")
            # Load model weights
            # ... (load logic) ...
            from transformers.modeling_utils import load_sharded_checkpoint
            if (Path(resume_from_checkpoint) / "model.safetensors.index.json").exists():
                 load_sharded_checkpoint(self.model, resume_from_checkpoint)
            else:
                 pass

            # Update global step from checkpoint name (checkpoint-X)
            try:
                self.global_step = int(resume_from_checkpoint.split("-")[-1])
                logger.info(f"Resuming at global_step={self.global_step}")
            except (ValueError, IndexError):
                logger.warning(f"Could not parse global step from {resume_from_checkpoint}")
        
        if self.global_step > 0:
            start_epoch = self.global_step // steps_per_epoch
            logger.info(f"Starting at global_step={self.global_step}, epoch={start_epoch}")
            
            # Skip steps in scheduler
            for _ in range(self.global_step):
                self.scheduler.step()
        
        for epoch in range(start_epoch, self.config.num_epochs):
            # Reload dataset from Hub at the start of each epoch (except first)
            if epoch > start_epoch and isinstance(dataset, str):
                logger.info(f"\\nReloading dataset from Hub to fetch newly generated embeddings...")
                try:
                    train_ds = load_dataset(dataset, split=split)
                    logger.info(f"Dataset reloaded successfully. New size: {len(train_ds)} samples")
                except Exception as e:
                    logger.warning(f"Failed to reload dataset: {e}. Using existing dataset.")
            
            epoch_loss = 0.0
            num_batches = 0
            accumulated_loss = 0.0
            
            indices = list(range(len(train_ds)))
            
            # Skip batches if resuming in the middle of an epoch
            resume_batch_idx = 0
            if epoch == start_epoch and self.global_step > 0:
                # Calculate how many batches to skip
                # global_step counts optimizer steps (every gradient_accumulation_steps batches)
                # We need to skip global_step * gradient_accumulation_steps batches
                # But wait, global_step is updated at the END of the accumulation block.
                # So we have completed self.global_step blocks.
                # Total batches processed = self.global_step * self.config.gradient_accumulation_steps
                
                # However, this naive skipping assumes we align exactly with epochs.
                # For simplicity in this script, we can just skip the whole epoch if fully done,
                # or calculate offset.
                
                batches_per_epoch = len(train_ds) // self.config.batch_size
                completed_batches_total = self.global_step * self.config.gradient_accumulation_steps
                resume_batch_idx = completed_batches_total % batches_per_epoch
                
                logger.info(f"Skipping {resume_batch_idx} batches to resume at step {self.global_step}")

            progress = tqdm(
                range(0, len(train_ds), self.config.batch_size),
                desc=f"Epoch {epoch + 1}/{self.config.num_epochs}",
                initial=resume_batch_idx
            )
            
            for batch_idx, start_idx in enumerate(progress):
                # Skip batches if resuming
                if batch_idx < resume_batch_idx:
                    continue

                end_idx = min(start_idx + self.config.batch_size, len(train_ds))
                batch_indices = indices[start_idx:end_idx]
                batch = train_ds.select(batch_indices)
                
                # Get texts and teacher embeddings
                texts = batch[text_column]
                
                # Debug logging
                if batch_idx == 0:
                    logger.info(f"Batch texts type: {type(texts)}")
                    if isinstance(texts, list):
                        logger.info(f"First text element type: {type(texts[0])}")
                        logger.info(f"First text sample: {texts[0][:100]}...")
                
                # Ensure texts is a list of strings
                if not isinstance(texts, list):
                    texts = list(texts)
                texts = [str(t) if t is not None else "" for t in texts]
                
                teacher_embeddings = torch.tensor(
                    batch[embedding_column],
                    dtype=torch.bfloat16 if self.config.use_bf16 else torch.float32
                ).to(self.device)
                
                # Tokenize
                encoded = self.tokenizer(
                    texts,
                    padding=True,
                    truncation=True,
                    max_length=self.config.max_seq_length,
                    return_tensors="pt",
                )
                input_ids = encoded["input_ids"].to(self.device)
                attention_mask = encoded["attention_mask"].to(self.device)
                
                # Forward pass
                student_hidden = self._get_last_hidden_state(input_ids, attention_mask)
                
                # Compute loss
                loss = loss_fn(student_hidden, teacher_embeddings)
                loss = loss / self.config.gradient_accumulation_steps
                
                # Backward
                loss.backward()
                accumulated_loss += loss.item()
                
                # Gradient accumulation step
                if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                    if self.config.max_grad_norm > 0:
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(),
                            self.config.max_grad_norm
                        )
                    
                    self.optimizer.step()
                    self.scheduler.step()
                    self.optimizer.zero_grad()
                    
                    epoch_loss += accumulated_loss
                    num_batches += 1
                    self.global_step += 1
                    
                    progress.set_postfix({"loss": f"{accumulated_loss:.4f}"})
                    accumulated_loss = 0.0
                    
                    # Logging
                    if self.global_step % self.config.logging_steps == 0:
                        avg_loss = epoch_loss / num_batches
                        lr = self.scheduler.get_last_lr()[0]
                        logger.info(f"Step {self.global_step}: loss = {avg_loss:.4f}, lr = {lr:.2e}")
                        
                        if self._wandb:
                            self._wandb.log({
                                "train/loss": avg_loss,
                                "train/learning_rate": lr,
                                "train/epoch": epoch + 1,
                            }, step=self.global_step)
                    
                    # Save checkpoint
                    if self.global_step % self.config.save_steps == 0:
                        checkpoint_dir = self._save_checkpoint(f"checkpoint-{self.global_step}")
                        if self.config.push_to_hub and self.config.hub_model_id:
                            logger.info(f"Pushing checkpoint {self.global_step} to hub...")
                            self._push_to_hub()
                            # Delete local checkpoint after successful push to save disk space
                            import shutil
                            if checkpoint_dir and os.path.exists(checkpoint_dir):
                                shutil.rmtree(checkpoint_dir)
                                logger.info(f"Deleted local checkpoint {checkpoint_dir} after push")
            
            avg_epoch_loss = epoch_loss / max(num_batches, 1)
            logger.info(f"Epoch {epoch + 1}: avg_loss = {avg_epoch_loss:.4f}")
            
            # Save and push at end of epoch
            logger.info(f"End of Epoch {epoch + 1}. Saving and pushing...")
            self._save_checkpoint(f"checkpoint-epoch-{epoch + 1}")
            if self.config.push_to_hub and self.config.hub_model_id:
                self._push_to_hub()
        
        # Save final model
        self._save_checkpoint("final")
        
        # Push to hub
        if self.config.push_to_hub and self.config.hub_model_id:
            self._push_to_hub()
        
        if self._wandb:
            self._wandb.finish()
        
        return {"train_loss": avg_epoch_loss}
    
    def _save_checkpoint(self, name: str) -> str:
        """Save a checkpoint."""
        output_path = Path(self.config.output_dir) / name
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        logger.info(f"Checkpoint saved: {output_path}")
        
        # Rotate checkpoints
        if self.config.save_total_limit is not None:
            self._rotate_checkpoints()
        
        return str(output_path)
            
    def _rotate_checkpoints(self) -> None:
        """Delete old checkpoints to stay within save_total_limit."""
        if self.config.save_total_limit <= 0:
            return
            
        import shutil
        import re
        
        # List all checkpoint directories
        output_dir = Path(self.config.output_dir)
        checkpoints = sorted(
            [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("checkpoint-")],
            key=lambda x: int(x.name.split("-")[-1])
        )
        
        # Remove oldest if we have too many
        if len(checkpoints) > self.config.save_total_limit:
            num_to_reduce = len(checkpoints) - self.config.save_total_limit
            for i in range(num_to_reduce):
                chk = checkpoints[i]
                logger.info(f"Deleting old checkpoint: {chk}")
                shutil.rmtree(chk)
    
    def _push_to_hub(self) -> str:
        """Push model to HuggingFace Hub."""
        url = self.model.push_to_hub(
            repo_id=self.config.hub_model_id,
            token=self.config.hub_token,
        )
        self.tokenizer.push_to_hub(
            repo_id=self.config.hub_model_id,
            token=self.config.hub_token,
        )
        logger.info(f"Pushed to: {url}")
        return url

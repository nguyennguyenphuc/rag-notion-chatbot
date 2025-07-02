"""Language model module."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface.llms import HuggingFacePipeline
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LanguageModel:
    """Wrapper for language model."""
    
    def __init__(self, model_name: str, llm_config: Dict[str, Any], quantization_config: Dict[str, Any]):
        """Initialize language model.
        
        Args:
            model_name: Name of the HuggingFace model
            llm_config: Configuration for LLM generation
            quantization_config: Configuration for model quantization
        """
        self.model_name = model_name
        self.llm_config = llm_config
        self.quantization_config = quantization_config
        self._llm: Optional[HuggingFacePipeline] = None
        
    def load(self) -> HuggingFacePipeline:
        """Load language model.
        
        Returns:
            Loaded language model
        """
        if self._llm is None:
            logger.info(f"Loading language model: {self.model_name}")
            try:
                # Create quantization config
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=self.quantization_config['load_in_4bit'],
                    bnb_4bit_use_double_quant=self.quantization_config['bnb_4bit_use_double_quant'],
                    bnb_4bit_compute_dtype=getattr(torch, self.quantization_config['bnb_4bit_compute_dtype']),
                    bnb_4bit_quant_type=self.quantization_config['bnb_4bit_quant_type']
                )
                
                # Load model
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True
                )
                
                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    trust_remote_code=True
                )
                
                # Create pipeline
                model_pipeline = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=self.llm_config['max_new_tokens'],
                    temperature=self.llm_config['temperature'],
                    top_p=self.llm_config['top_p'],
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    device_map="auto"
                )
                
                # Wrap in LangChain
                self._llm = HuggingFacePipeline(pipeline=model_pipeline)
                logger.info("Language model loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading language model: {str(e)}")
                raise
                
        return self._llm
    
    @property
    def llm(self) -> HuggingFacePipeline:
        """Get language model, loading if necessary.
        
        Returns:
            Language model
        """
        if self._llm is None:
            self.load()
        return self._llm
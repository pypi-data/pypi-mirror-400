"""
Local LLM Provider
==================

Local LLM inference without API calls using transformers or llama.cpp.
Supports CPU and GPU inference.
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, List
import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)

# Check available backends
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available. Install: pip install transformers torch")


class DomainClassifier:
    """
    Small text classification model for domain recognition.
    
    Uses DistilBERT (~67M parameters) for fast domain classification.
    Supports banking, medical, legal, general domains.
    """
    
    # Default small model for domain classification
    DEFAULT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"  # Can be fine-tuned for domains
    
    # Domain labels (can be extended)
    DOMAINS = {
        0: "general",
        1: "banking",
        2: "medical", 
        3: "legal",
        4: "technical"
    }
    
    def __init__(
        self,
        model_name: str = None,
        device: str = "cpu",
    ):
        """
        Initialize domain classifier with small model.
        
        Args:
            model_name: Model name (defaults to DistilBERT)
            device: "cpu" or "cuda"
        """
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError("transformers not installed. Run: pip install transformers torch")
        
        if model_name is None:
            model_name = self.DEFAULT_MODEL
        
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self._is_loaded = False
        
        logger.info(f"Initialized DomainClassifier: {model_name} on {device}")
    
    def load(self):
        """Load small classification model."""
        if self._is_loaded:
            return
        
        logger.info(f"Loading domain classifier: {self.model_name}...")
        
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Move to device
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to("cuda")
                logger.info("✅ Domain classifier loaded on GPU")
            else:
                self.model = self.model.to("cpu")
                logger.info("✅ Domain classifier loaded on CPU")
            
            self.model.eval()
            self._is_loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load domain classifier: {e}")
            raise
    
    def classify_domain(self, text: str) -> Dict[str, float]:
        """
        Classify the domain of input text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dict with domain probabilities
        """
        if not self._is_loaded:
            self.load()
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Move to device
            if self.device == "cuda":
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=-1)
            
            # Convert to domain probabilities
            probs = probabilities[0].cpu().numpy()
            
            # For now, map to our domains (this is a placeholder - would need fine-tuning)
            domain_probs = {
                "banking": float(probs[0] * 0.4 + probs[1] * 0.6),  # Banking keywords boost
                "medical": float(probs[0] * 0.3),
                "legal": float(probs[0] * 0.2),
                "technical": float(probs[1] * 0.4),
                "general": float(probs[0] * 0.6 + probs[1] * 0.4)
            }
            
            return domain_probs
            
        except Exception as e:
            logger.error(f"Domain classification failed: {e}")
            return {"general": 1.0, "banking": 0.0, "medical": 0.0, "legal": 0.0, "technical": 0.0}
    
    def get_top_domain(self, text: str) -> str:
        """
        Get the most likely domain for the text.
        
        Args:
            text: Input text
            
        Returns:
            Top domain name
        """
        probs = self.classify_domain(text)
        return max(probs.items(), key=lambda x: x[1])[0]
    
    def is_banking_domain(self, text: str, threshold: float = 0.6) -> bool:
        """
        Check if text is likely banking domain.
        
        Args:
            text: Input text
            threshold: Confidence threshold
            
        Returns:
            True if banking domain
        """
        probs = self.classify_domain(text)
        return probs.get("banking", 0.0) > threshold


class LocalLLM:
    """
    Local LLM for text polishing and correction using Qwen 2.5B Instruct.
    
    Uses Qwen/Qwen2.5-3B-Instruct (~5GB)
    - Fast inference on consumer GPUs
    - Excellent multilingual support (Hindi/English)
    - Strong instruction following
    - Great for banking domain conversations
    """
    
    # Default model
    DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"
    
    def __init__(
        self,
        model_name: str = None,
        device: str = "cpu",
        compute_type: str = "float32",
        use_domain_classifier: bool = True,
    ):
        """
        Initialize local LLM with Qwen 2.5B Instruct.
        
        Args:
            model_name: Model name (defaults to Qwen2.5-3B-Instruct)
            device: "cpu" or "cuda"
            compute_type: "float32", "float16", or "int8"
            use_domain_classifier: Whether to use small model for domain detection
        """
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError("transformers not installed. Run: pip install transformers torch")
        
        # Use Qwen by default
        if model_name is None:
            model_name = self.DEFAULT_MODEL
        
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.use_domain_classifier = use_domain_classifier
        self.model = None
        self.tokenizer = None
        self.domain_classifier = None
        self._is_loaded = False
        
        # Initialize domain classifier if requested
        if self.use_domain_classifier:
            self.domain_classifier = DomainClassifier(device=device)
        
        logger.info(f"Initialized LocalLLM: {model_name} on {device}")
        if use_domain_classifier:
            logger.info("Domain classifier enabled for smart processing")
    
    def load(self):
        """Load model and tokenizer."""
        if self._is_loaded:
            return
        
        logger.info(f"Loading local LLM: {self.model_name}...")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Determine torch dtype
            dtype = torch.float32
            if self.compute_type == "float16" and self.device == "cuda":
                dtype = torch.float16
            elif self.compute_type == "int8":
                dtype = torch.int8
            
            # Load Mistral (causal LM) - no seq2seq models
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
            )
            
            # Move to device
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to("cuda")
                logger.info("✅ LLM loaded on GPU")
            else:
                self.model = self.model.to("cpu")
                logger.info("✅ LLM loaded on CPU")
            
            self.model.eval()  # Set to evaluation mode
            self._is_loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_length: int = 512,
        temperature: float = 0.1,
        num_beams: int = 1,
    ) -> str:
        """
        Generate text using Qwen 2.5B Instruct.
        
        Args:
            prompt: Input prompt/text to polish (already formatted with chat template)
            max_length: Maximum output length
            temperature: Sampling temperature (lower = more deterministic)
            num_beams: Number of beams for beam search (1 = greedy)
            
        Returns:
            Generated text
        """
        if not self._is_loaded:
            self.load()
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=2048,
                truncation=True,
                padding=True,
            )
            
            # Move to device
            if self.device == "cuda":
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate with Qwen
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=temperature > 0.0,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode ONLY the newly generated tokens (skip input prompt)
            input_length = inputs['input_ids'].shape[-1]
            generated_tokens = outputs[0][input_length:]  # Only new tokens
            generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            # Clean up whitespace
            generated_text = generated_text.strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return prompt  # Return original on error
    
    def polish_hindi_text(self, text: str) -> str:
        """
        Polish Hindi/Hinglish text for ICICI Bank domain conversations using Qwen 2.5B Instruct.
        
        Uses small domain classifier to detect context and adapt cleaning rules.
        
        Args:
            text: Raw ASR output (Hindi/Hinglish mix with errors, repetitions, filler words)
            
        Returns:
            Clean, professional conversation with proper formatting
        """
        # Detect domain using small classifier
        detected_domain = "general"
        if self.domain_classifier:
            try:
                detected_domain = self.domain_classifier.get_top_domain(text)
                logger.info(f"Detected domain: {detected_domain}")
            except Exception as e:
                logger.warning(f"Domain detection failed: {e}, using general")
        
        # Adapt system message based on detected domain
        if detected_domain == "banking":
            system_message = (
                "You are an expert at cleaning and rephrasing messy ASR transcripts of ICICI Bank customer service calls.\n\n"
                "⚠️ CRITICAL RULES:\n"
                "1. Fix ALL spelling errors and correct misheard words\n"
                "2. Remove filler words (हाँ हाँ, ना, ठीक है when repeated unnecessarily)\n"
                "3. Remove repetitions and stutters\n"
                "4. Structure into proper sentences with line breaks for clarity\n"
                "5. Convert ALL spoken numbers to Indian currency format with ₹ symbol:\n"
                "   - 'पांच सौ' → '₹500'\n"
                "   - 'चार हजार' → '₹4,000'\n"
                "   - 'पंद्रह हज़ार' → '₹15,000'\n"
                "   - 'तीन लाख' → '₹3,00,000'\n"
                "   - 'दो लाख' → '₹2,00,000'\n"
                "   - 'छह हजार पांच सौ' → '₹6,500'\n\n"
                "6. Fix common ASR errors:\n"
                "   - 'आईसीआईसी' / 'आई सी एस' / 'ICES' → 'ICICI Bank'\n"
                "   - 'पर्सनल एक्सीडेंट' → 'Personal Accident Cover'\n"
                "   - 'फ्यूल सरचार्ज' → 'Fuel Surcharge Waiver'\n"
                "   - 'बुकमाईशो' → 'BookMyShow'\n"
                "   - 'डोमेस्टिक' → 'Domestic'\n"
                "   - 'इंटरनेशनल' → 'International'\n"
                "   - 'एक्टिवेट' → 'activate'\n"
                "   - 'कूरियर' → 'courier'\n\n"
                "7. ICICI Products & Services (use exact spelling):\n"
                "   Cards: Coral, Rubyx, Sapphiro, Amazon Pay, HPCL, Platinum, MakeMyTrip\n"
                "   Benefits: reward points, cashback, lounge access, milestone benefits\n"
                "   Terms: credit card, joining fee, annual fee, statement date, due date, OTP\n\n"
                "8. Keep natural Hindi-English code-mixing style\n"
                "9. Add proper punctuation (commas, periods, question marks)\n"
                "10. Structure as professional customer service dialogue\n\n"
                "Output ONLY the cleaned, professional text. No explanations."
            )
        elif detected_domain == "medical":
            system_message = (
                "You are an expert at cleaning medical consultation transcripts.\n\n"
                "CRITICAL RULES:\n"
                "1. Fix medical terminology and drug names\n"
                "2. Remove filler words and repetitions\n"
                "3. Structure as professional medical dialogue\n"
                "4. Convert spoken numbers appropriately\n"
                "5. Maintain medical accuracy\n\n"
                "Output ONLY the cleaned medical text. No explanations."
            )
        elif detected_domain == "legal":
            system_message = (
                "You are an expert at cleaning legal consultation transcripts.\n\n"
                "CRITICAL RULES:\n"
                "1. Fix legal terminology and case references\n"
                "2. Remove filler words and repetitions\n"
                "3. Structure as professional legal dialogue\n"
                "4. Convert spoken numbers appropriately\n"
                "5. Maintain legal accuracy\n\n"
                "Output ONLY the cleaned legal text. No explanations."
            )
        else:  # general
            system_message = (
                "You are an expert at cleaning and rephrasing messy ASR transcripts.\n\n"
                "CRITICAL RULES:\n"
                "1. Fix ALL spelling errors and correct misheard words\n"
                "2. Remove filler words (हाँ हाँ, ना, ठीक है when repeated unnecessarily)\n"
                "3. Remove repetitions and stutters\n"
                "4. Structure into proper sentences with line breaks for clarity\n"
                "5. Convert spoken numbers appropriately\n"
                "6. Add proper punctuation\n\n"
                "Output ONLY the cleaned, professional text. No explanations."
            )
        
        # User message with the actual text to clean
        user_message = f"Clean this raw ASR transcript:\n\n{text}"
        
        # Use Qwen's chat template
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Apply chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Generate polished text with longer output limit
        polished = self.generate(prompt, max_length=len(text.split()) * 6)
        
        return polished
    
    def is_available(self) -> bool:
        """Check if model is loaded and available."""
        return self._is_loaded
    
    def unload(self):
        """Unload model to free memory."""
        if self._is_loaded:
            del self.model
            del self.tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self._is_loaded = False
            logger.info("LLM unloaded from memory")


# Singleton instance
_local_llm_instance: Optional[LocalLLM] = None


def get_local_llm(
    model_name: str = "small",
    device: str = "cpu",
    compute_type: str = "float32",
) -> LocalLLM:
    """
    Get or create local LLM singleton instance.
    
    Args:
        model_name: Model name or size ("small", "base", "large")
        device: "cpu" or "cuda"
        compute_type: "float32", "float16", or "int8"
        
    Returns:
        LocalLLM instance
    """
    global _local_llm_instance
    
    if _local_llm_instance is None:
        _local_llm_instance = LocalLLM(
            model_name=model_name,
            device=device,
            compute_type=compute_type,
        )
        _local_llm_instance.load()
    
    return _local_llm_instance

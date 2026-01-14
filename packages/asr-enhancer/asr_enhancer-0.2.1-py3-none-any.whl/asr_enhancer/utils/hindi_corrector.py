"""
Hindi Text Corrector
====================

Specialized corrections for Hindi/Hinglish ASR errors.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


class HindiTextCorrector:
    """
    Corrects common Hindi ASR errors.
    
    Handles:
        - Truncated words (missing initial characters)
        - English words misrecognized in Hindi
        - Common Hinglish code-mixing patterns
        - Banking/financial domain terms
    """
    
    # Truncated word patterns (missing initial vowel marks)
    TRUNCATION_FIXES = {
        "्जी": "जी",
        "्सीडेंट": "एक्सीडेंट",
        "ेनिफिट": "बेनिफिट",
        "ारी": "सारी",
        "ंक": "बैंक",
        "ंबर": "नंबर",
        "ॉब": "",  # Garbage
        "िस.": "",  # Garbage
    }
    
    # Common Hindi ASR misrecognitions
    WORD_CORRECTIONS = {
        # Banking terms - English → Canonical form
        "आई सी एच के": "ICICI",
        "आई सी आई सी आई": "ICICI",
        "एच डी एफ सी": "HDFC",
        "पीनियम": "प्रीमियम",
        "प्रीमीयम": "प्रीमियम",
        "Premi": "Premium",  # Fix truncated English
        "कोरोल": "Coral",
        "कोरोल कार्ड": "Coral Card",
        "काव्यज": "कवरेज",
        "कवरेज़": "कवरेज",
        "इंटर वेस्ट": "Interest",
        "Interest": "Interest",  # Keep canonical
        "मिस्टिक्स": "मिस्टेक्स",
        "बिरकम": "बिल",
        "काप": "का",
        "काड़": "कार्ड",
        "एडिशनली": "additionally",
        
        # Additional banking terms
        "एक्सपी": "expiry",
        "ऐक्टिवेट": "activate",
        "अनुअल": "annual",
        "सब्सिडी": "subsidy",
        "एनुअल": "annual",
        "मेंबरशिप": "membership",
        "लाइफ टाइम": "lifetime",
        "लाइफटाइम": "lifetime",
        "चार्ज": "charge",
        "भुगतान": "payment",
        "समय": "समय",  # Keep as Hindi
        
        # Numbers spoken as English in Hindi
        "फिफ्टी थाउजेंड": "50,000",
        "थर्टी": "30",
        "फोर्टी": "40",
        "टेन थाउजेंड": "10,000",
        "फिफ्टी": "50",
        "ट्वेंटी": "20",
        "टेन": "10",
        
        # Common fillers/corrections - will use word boundary regex
        # "um": "",  # Removed - causes issues with words containing "um"
        # "uhm": "",
        # "erm": "",
        # "uh": "",
        # "hmm": "",
        
        # Time/Duration
        "दादा किंग दर्ज": "7-10 working days",
        "वर्किंग दर्ज": "working days",
        "सेकंड इयर": "second year",
        "फर्स्ट इयर": "first year",
        
        # Card types
        "dual variant": "dual variant",
        "वीज़ा": "Visa",
        "वीसा": "Visa",
        "रुपये": "RuPay",
        "रूपए": "RuPay",
        "अमेज़न": "Amazon",
        "अमेज़ॉन": "Amazon",
    }
    
    # Regex patterns for structural fixes
    REGEX_PATTERNS = [
        # Fix repeated words
        (r'\b(\w+)\s+\1\b', r'\1'),
        # Fix excessive spaces
        (r'\s{2,}', ' '),
        # Fix trailing/leading punctuation issues
        (r'\s+([।,?!])', r'\1'),
        (r'([।,?!])\s*([।,?!])', r'\1'),
        # Remove filler words (with word boundaries)
        (r'\b(um|uhm|erm|uh|hmm)\b\s*', ''),
    ]
    
    def __init__(self):
        """Initialize the Hindi text corrector."""
        # Compile regex patterns
        self.compiled_patterns = [
            (re.compile(pattern), replacement)
            for pattern, replacement in self.REGEX_PATTERNS
        ]
    
    def correct_truncations(self, text: str) -> str:
        """Fix truncated words with missing initial characters."""
        for truncated, fixed in self.TRUNCATION_FIXES.items():
            # Match at word boundaries or start of text
            pattern = rf'(^|\s){re.escape(truncated)}'
            replacement = rf'\1{fixed}' if fixed else r'\1'
            text = re.sub(pattern, replacement, text)
        return text
    
    def _is_devanagari(self, text: str) -> bool:
        """Check if text contains Devanagari characters."""
        return any('\u0900' <= char <= '\u097F' for char in text)
    
    def correct_words(self, text: str) -> str:
        """Apply word-level corrections with word boundary awareness."""
        for wrong, correct in self.WORD_CORRECTIONS.items():
            # Check for exact match first (handles single word or phrase input)
            if text.strip() == wrong:
                return correct
            
            # For multi-word patterns (with spaces), match as-is
            if ' ' in wrong:
                pattern = re.compile(re.escape(wrong), re.IGNORECASE)
                text = pattern.sub(correct, text)
            elif self._is_devanagari(wrong):
                # Devanagari: use space-based boundaries
                pattern = re.compile(
                    rf'(?:(?<=\s)|^){re.escape(wrong)}(?=\s|$|[।,?!])',
                    re.IGNORECASE
                )
                text = pattern.sub(correct, text)
            else:
                # ASCII/Latin - use word boundaries
                pattern = re.compile(rf'\b{re.escape(wrong)}\b', re.IGNORECASE)
                text = pattern.sub(correct, text)
        return text
    
    def apply_regex_fixes(self, text: str) -> str:
        """Apply regex-based structural fixes."""
        for pattern, replacement in self.compiled_patterns:
            text = pattern.sub(replacement, text)
        return text.strip()
    
    def correct(self, text: str) -> str:
        """
        Apply all corrections to text.
        
        Args:
            text: Input text (Hindi/Hinglish)
            
        Returns:
            Corrected text
        """
        # Step 1: Fix truncations
        text = self.correct_truncations(text)
        
        # Step 2: Apply word corrections
        text = self.correct_words(text)
        
        # Step 3: Apply regex fixes
        text = self.apply_regex_fixes(text)
        
        return text
    
    def correct_tokens(self, tokens: list[WordToken]) -> list[WordToken]:
        """
        Apply corrections to token list.
        
        Args:
            tokens: List of WordToken objects
            
        Returns:
            Corrected token list
        """
        for token in tokens:
            word_lower = token.word.lower()
            
            # Check truncation fixes
            for truncated, fixed in self.TRUNCATION_FIXES.items():
                if truncated in token.word:
                    token.word = token.word.replace(truncated, fixed)
                    token.is_corrected = True
                    token.correction_source = "hindi_truncation"
                    break
            
            # Check word corrections
            for wrong, correct in self.WORD_CORRECTIONS.items():
                if wrong.lower() == word_lower:
                    token.word = correct
                    token.is_corrected = True
                    token.correction_source = "hindi_word"
                    break
        
        return tokens


# Banking/Financial domain lexicon for Hindi
BANKING_LEXICON_HI = {
    # Bank names
    "ICICI Bank": ["आई सी आई सी आई बैंक", "आई सी एच के बैंक", "ICICI बैंक"],
    "HDFC Bank": ["एच डी एफ सी बैंक", "HDFC बैंक"],
    "SBI": ["एस बी आई", "स्टेट बैंक"],
    "Axis Bank": ["एक्सिस बैंक", "axis बैंक"],
    "Kotak Bank": ["कोटक बैंक", "kotak बैंक"],
    
    # Card types
    "Credit Card": ["क्रेडिट कार्ड", "credit card", "क्रेडिट काड़"],
    "Debit Card": ["डेबिट कार्ड", "debit card"],
    "RuPay": ["रुपे", "रुपये", "रूपए", "rupay"],
    "Visa": ["वीसा", "visa"],
    "MasterCard": ["मास्टरकार्ड", "mastercard"],
    "Coral Card": ["कोरल कार्ड", "कोरोल कार्ड", "coral card"],
    "Amazon Card": ["अमेज़न कार्ड", "amazon card"],
    
    # Banking terms
    "Premium": ["प्रीमियम", "पीनियम", "premium"],
    "Coverage": ["कवरेज", "काव्यज", "coverage"],
    "Insurance": ["इंश्योरेंस", "बीमा", "insurance"],
    "Interest": ["इंटरेस्ट", "इंटर वेस्ट", "ब्याज", "interest"],
    "Transaction": ["ट्रांजेक्शन", "लेनदेन", "transaction"],
    "EMI": ["ईएमआई", "EMI", "किस्त"],
    "Annual Fee": ["वार्षिक शुल्क", "annual fee", "सालाना फीस"],
    "Joining Fee": ["ज्वाइनिंग फीस", "joining fee"],
    "Reward Points": ["रिवॉर्ड पॉइंट्स", "reward points", "पॉइंट्स"],
    "Cashback": ["कैशबैक", "cashback", "कैश बैक"],
    "Statement": ["स्टेटमेंट", "statement", "विवरण"],
    "Due Date": ["ड्यू डेट", "due date", "भुगतान तिथि"],
    "Credit Limit": ["क्रेडिट लिमिट", "credit limit", "सीमा"],
    "Minimum Due": ["मिनिमम ड्यू", "minimum due", "न्यूनतम भुगतान"],
    
    # Actions
    "Activate": ["एक्टिवेट", "activate", "सक्रिय"],
    "Block": ["ब्लॉक", "block", "बंद"],
    "Upgrade": ["अपग्रेड", "upgrade"],
    "Apply": ["अप्लाई", "apply", "आवेदन"],
    
    # Amounts (Hindi)
    "Lakh": ["लाख", "lakh", "lac"],
    "Crore": ["करोड़", "crore"],
    "Thousand": ["हज़ार", "thousand"],
    "Hundred": ["सौ", "hundred"],
}

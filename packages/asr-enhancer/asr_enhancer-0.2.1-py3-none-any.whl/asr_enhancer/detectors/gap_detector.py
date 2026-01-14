"""
Gap Detector for Missing Words
==============================

Detects potential missing words/phrases in ASR output using:
1. Linguistic patterns (incomplete sentences, missing verbs)
2. Domain-specific expectations (banking terms that should appear together)
3. LLM-based semantic gap detection
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GapInfo:
    """Information about a detected gap."""
    
    position: int  # Character position in text
    context_before: str  # Text before the gap
    context_after: str  # Text after the gap
    gap_type: str  # Type of gap detected
    confidence: float  # Confidence that this is a real gap
    suggested_content: Optional[str] = None  # LLM-suggested missing content


class LinguisticGapDetector:
    """
    Detects gaps in transcripts using linguistic patterns.
    
    Works with plain text (no timestamps required).
    """
    
    # Patterns that suggest incomplete sentences
    INCOMPLETE_PATTERNS = [
        # Dangling conjunctions
        (r'\b(और|या|लेकिन|पर|तो|कि|जो|अगर)\s*[।\.\,]', 'dangling_conjunction'),
        (r'\b(and|or|but|so|if|that|which)\s*[.,]', 'dangling_conjunction_en'),
        
        # Missing verb patterns (Hindi)
        (r'\b(को|से|में|पर|के लिए)\s*[।\.]', 'missing_verb_hi'),
        
        # Truncated numbers
        (r'\b(\d+)\s*[।\.](?!\d)', 'truncated_number'),
        
        # Incomplete phone numbers (less than 10 digits)
        (r'\b(\d{1,9})\b(?!\d)', 'incomplete_phone'),
        
        # Banking terms that usually have amounts
        (r'(रुपये|rupees?|₹|Rs\.?)\s*[।\.\,](?!\s*\d)', 'missing_amount'),
        (r'(charge|चार्ज|fee|फीस)\s+(?:है|is)\s*[।\.]', 'missing_amount_after_fee'),
        
        # Consent patterns (often missed)
        (r'(सहमति|consent|agree)\s*[।\.]', 'incomplete_consent'),
        
        # Abrupt endings
        (r'\b(आपका|your|the|यह|this)\s*[।\.]', 'abrupt_ending'),
    ]
    
    # Word pairs that should appear together (if one is present, other likely missing)
    EXPECTED_PAIRS = {
        # Hindi pairs
        'क्रेडिट': ['कार्ड', 'लिमिट', 'स्कोर'],
        'डेबिट': ['कार्ड'],
        'वार्षिक': ['शुल्क', 'फीस', 'चार्ज'],
        'ब्याज': ['दर', 'रेट'],
        'न्यूनतम': ['भुगतान', 'राशि', 'ड्यू'],
        'सहमति': ['देना', 'लेना', 'है'],
        
        # English pairs
        'credit': ['card', 'limit', 'score'],
        'annual': ['fee', 'charge'],
        'interest': ['rate', 'free'],
        'minimum': ['due', 'payment', 'amount'],
        'consent': ['give', 'provided', 'taken'],
        'terms': ['conditions', 'and'],
    }
    
    # Filler words that might indicate ASR confusion
    CONFUSION_MARKERS = [
        r'\b(um|uh|uhm|hmm|err)\b',
        r'\b(अं|हां|हं|उं)\b',
        r'\.{3,}',  # Multiple dots
        r'\s{3,}',  # Multiple spaces
    ]
    
    def __init__(self):
        """Initialize the gap detector."""
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE | re.UNICODE), gap_type)
            for pattern, gap_type in self.INCOMPLETE_PATTERNS
        ]
        self.confusion_patterns = [
            re.compile(pattern, re.IGNORECASE | re.UNICODE)
            for pattern in self.CONFUSION_MARKERS
        ]
    
    def detect_gaps(self, text: str) -> list[GapInfo]:
        """
        Detect potential gaps in the transcript.
        
        Args:
            text: Plain text transcript
            
        Returns:
            List of detected gaps with context
        """
        gaps = []
        
        # Check incomplete patterns
        for pattern, gap_type in self.compiled_patterns:
            for match in pattern.finditer(text):
                gap = GapInfo(
                    position=match.start(),
                    context_before=text[max(0, match.start()-50):match.start()],
                    context_after=text[match.end():min(len(text), match.end()+50)],
                    gap_type=gap_type,
                    confidence=0.7,
                )
                gaps.append(gap)
        
        # Check for missing pair words
        gaps.extend(self._detect_missing_pairs(text))
        
        # Check for confusion markers
        gaps.extend(self._detect_confusion_zones(text))
        
        # Check sentence structure
        gaps.extend(self._detect_structural_gaps(text))
        
        return gaps
    
    def _detect_missing_pairs(self, text: str) -> list[GapInfo]:
        """Detect cases where expected word pairs are incomplete."""
        gaps = []
        text_lower = text.lower()
        
        for trigger, expected in self.EXPECTED_PAIRS.items():
            if trigger.lower() in text_lower:
                # Check if any expected word is present
                has_pair = any(exp.lower() in text_lower for exp in expected)
                if not has_pair:
                    # Find position of trigger
                    pos = text_lower.find(trigger.lower())
                    gap = GapInfo(
                        position=pos,
                        context_before=text[max(0, pos-30):pos],
                        context_after=text[pos:min(len(text), pos+50)],
                        gap_type='missing_pair_word',
                        confidence=0.6,
                        suggested_content=f"Expected one of: {expected}",
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _detect_confusion_zones(self, text: str) -> list[GapInfo]:
        """Detect areas with filler words that might indicate ASR confusion."""
        gaps = []
        
        for pattern in self.confusion_patterns:
            for match in pattern.finditer(text):
                gap = GapInfo(
                    position=match.start(),
                    context_before=text[max(0, match.start()-30):match.start()],
                    context_after=text[match.end():min(len(text), match.end()+30)],
                    gap_type='confusion_marker',
                    confidence=0.5,
                )
                gaps.append(gap)
        
        return gaps
    
    def _detect_structural_gaps(self, text: str) -> list[GapInfo]:
        """Detect structural issues like very short sentences."""
        gaps = []
        
        # Split into sentences
        sentences = re.split(r'[।\.\?!]', text)
        
        position = 0
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Very short sentence (likely incomplete)
            if sentence and len(sentence.split()) <= 2 and len(sentence) > 3:
                gap = GapInfo(
                    position=position,
                    context_before="",
                    context_after=sentence,
                    gap_type='very_short_sentence',
                    confidence=0.5,
                )
                gaps.append(gap)
            
            position += len(sentence) + 1
        
        return gaps
    
    def get_segments_for_reprocessing(
        self,
        text: str,
        audio_duration: Optional[float] = None,
    ) -> list[dict]:
        """
        Get audio segments that should be re-processed with secondary ASR.
        
        Args:
            text: Transcript text
            audio_duration: Total audio duration in seconds (optional)
            
        Returns:
            List of segments with estimated time ranges
        """
        gaps = self.detect_gaps(text)
        
        if not gaps:
            return []
        
        # Without timestamps, we estimate based on character position
        # Assuming ~15 characters per second of speech
        CHARS_PER_SECOND = 15
        
        segments = []
        for gap in gaps:
            if gap.confidence >= 0.6:  # Only high-confidence gaps
                # Estimate time range (with buffer)
                start_char = max(0, gap.position - 50)
                end_char = min(len(text), gap.position + 50)
                
                if audio_duration:
                    # Estimate times
                    start_time = max(0, (start_char / len(text)) * audio_duration - 2)
                    end_time = min(audio_duration, (end_char / len(text)) * audio_duration + 2)
                else:
                    # No duration, estimate from characters
                    start_time = max(0, start_char / CHARS_PER_SECOND - 2)
                    end_time = end_char / CHARS_PER_SECOND + 2
                
                segments.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'gap_type': gap.gap_type,
                    'context': gap.context_before + " [GAP] " + gap.context_after,
                    'confidence': gap.confidence,
                })
        
        # Merge overlapping segments
        return self._merge_segments(segments)
    
    def _merge_segments(self, segments: list[dict]) -> list[dict]:
        """Merge overlapping segments."""
        if not segments:
            return []
        
        # Sort by start time
        segments = sorted(segments, key=lambda x: x['start_time'])
        
        merged = [segments[0]]
        for seg in segments[1:]:
            last = merged[-1]
            if seg['start_time'] <= last['end_time']:
                # Overlapping - extend
                last['end_time'] = max(last['end_time'], seg['end_time'])
                last['gap_type'] += f",{seg['gap_type']}"
                last['confidence'] = max(last['confidence'], seg['confidence'])
            else:
                merged.append(seg)
        
        return merged


class LLMGapDetector:
    """
    Uses LLM to detect semantic gaps in transcripts.
    
    More accurate but slower than linguistic detection.
    """
    
    GAP_DETECTION_PROMPT = """Analyze this transcript for missing or incomplete content.

Transcript:
{transcript}

Look for:
1. Incomplete sentences or thoughts
2. Missing numbers/amounts that should be present
3. Abrupt topic changes suggesting missing content
4. References to things not mentioned earlier
5. Missing consent/agreement phrases in formal conversations

Return a JSON list of gaps found:
[
  {{"position": "after 'X'", "likely_missing": "description of what's missing", "confidence": 0.8}}
]

If no gaps detected, return: []

IMPORTANT: Only flag clear gaps, not stylistic issues. Be conservative."""

    def __init__(self, llm_provider=None):
        """Initialize with optional LLM provider."""
        self.llm = llm_provider
    
    async def detect_gaps(self, text: str) -> list[GapInfo]:
        """
        Use LLM to detect semantic gaps.
        
        Args:
            text: Transcript text
            
        Returns:
            List of detected gaps
        """
        if not self.llm:
            return []
        
        try:
            prompt = self.GAP_DETECTION_PROMPT.format(transcript=text[:2000])
            response = await self.llm.generate(prompt)
            
            # Parse response
            import json
            gaps_data = json.loads(response)
            
            gaps = []
            for gap_data in gaps_data:
                gap = GapInfo(
                    position=0,  # LLM gives textual position
                    context_before=gap_data.get('position', ''),
                    context_after='',
                    gap_type='llm_detected',
                    confidence=gap_data.get('confidence', 0.7),
                    suggested_content=gap_data.get('likely_missing'),
                )
                gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            # Fallback to empty if LLM fails
            return []

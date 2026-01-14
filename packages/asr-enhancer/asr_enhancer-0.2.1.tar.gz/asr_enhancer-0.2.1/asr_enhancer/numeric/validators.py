"""
Numeric Validators
==================

Validation utilities for numeric sequences.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result of numeric validation."""

    is_valid: bool
    pattern_type: str
    details: dict[str, Any]
    suggestions: list[str]


class NumericValidator:
    """
    Validates numeric sequences against expected patterns.

    Supports validation for:
        - Phone numbers (with country code detection)
        - OTP codes
        - Currency amounts
        - Dates
        - Credit card numbers (Luhn check)
        - ID numbers
    """

    # Country code patterns
    COUNTRY_CODES = {
        "1": "US/Canada",
        "44": "UK",
        "91": "India",
        "86": "China",
        "49": "Germany",
        "33": "France",
        "81": "Japan",
    }

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate_phone(self, digits: str) -> ValidationResult:
        """
        Validate phone number.

        Args:
            digits: Digit string

        Returns:
            ValidationResult
        """
        # Remove any non-digit characters
        clean_digits = re.sub(r"\D", "", digits)
        length = len(clean_digits)

        # Check length
        if length < 10:
            return ValidationResult(
                is_valid=False,
                pattern_type="phone",
                details={"length": length, "expected_min": 10},
                suggestions=["Phone number appears incomplete"],
            )

        if length > 15:
            return ValidationResult(
                is_valid=False,
                pattern_type="phone",
                details={"length": length, "expected_max": 15},
                suggestions=["Phone number too long, may contain extra digits"],
            )

        # Detect country code
        country = None
        for code, name in self.COUNTRY_CODES.items():
            if clean_digits.startswith(code):
                country = name
                break

        return ValidationResult(
            is_valid=True,
            pattern_type="phone",
            details={
                "length": length,
                "country": country,
                "formatted": self._format_phone(clean_digits),
            },
            suggestions=[],
        )

    def validate_otp(self, digits: str) -> ValidationResult:
        """
        Validate OTP code.

        Args:
            digits: Digit string

        Returns:
            ValidationResult
        """
        clean_digits = re.sub(r"\D", "", digits)
        length = len(clean_digits)

        if 4 <= length <= 8:
            return ValidationResult(
                is_valid=True,
                pattern_type="otp",
                details={"length": length},
                suggestions=[],
            )

        return ValidationResult(
            is_valid=False,
            pattern_type="otp",
            details={"length": length, "expected_range": "4-8"},
            suggestions=[
                f"OTP should be 4-8 digits, got {length}"
            ],
        )

    def validate_amount(self, text: str) -> ValidationResult:
        """
        Validate currency amount.

        Args:
            text: Amount text (may include currency symbols)

        Returns:
            ValidationResult
        """
        # Extract numeric part
        amount_match = re.search(r"[\d,]+\.?\d*", text)
        if not amount_match:
            return ValidationResult(
                is_valid=False,
                pattern_type="amount",
                details={},
                suggestions=["No numeric amount found"],
            )

        amount_str = amount_match.group().replace(",", "")
        try:
            amount = float(amount_str)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                pattern_type="amount",
                details={"raw": amount_str},
                suggestions=["Invalid numeric format"],
            )

        # Detect currency
        currency = None
        if "$" in text:
            currency = "USD"
        elif "€" in text:
            currency = "EUR"
        elif "£" in text:
            currency = "GBP"
        elif "₹" in text or "rs" in text.lower():
            currency = "INR"

        return ValidationResult(
            is_valid=True,
            pattern_type="amount",
            details={
                "amount": amount,
                "currency": currency,
                "formatted": f"{currency or ''}{amount:,.2f}".strip(),
            },
            suggestions=[],
        )

    def validate_credit_card(self, digits: str) -> ValidationResult:
        """
        Validate credit card number using Luhn algorithm.

        Args:
            digits: Digit string

        Returns:
            ValidationResult
        """
        clean_digits = re.sub(r"\D", "", digits)

        if len(clean_digits) < 13 or len(clean_digits) > 19:
            return ValidationResult(
                is_valid=False,
                pattern_type="credit_card",
                details={"length": len(clean_digits)},
                suggestions=["Credit card numbers are typically 13-19 digits"],
            )

        # Luhn check
        is_valid = self._luhn_check(clean_digits)

        # Detect card type
        card_type = self._detect_card_type(clean_digits)

        return ValidationResult(
            is_valid=is_valid,
            pattern_type="credit_card",
            details={
                "length": len(clean_digits),
                "card_type": card_type,
                "luhn_valid": is_valid,
            },
            suggestions=[] if is_valid else ["Luhn check failed, number may be incorrect"],
        )

    def _luhn_check(self, digits: str) -> bool:
        """Perform Luhn algorithm check."""
        total = 0
        reverse_digits = digits[::-1]

        for i, d in enumerate(reverse_digits):
            n = int(d)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n

        return total % 10 == 0

    def _detect_card_type(self, digits: str) -> str | None:
        """Detect credit card type from prefix."""
        if digits.startswith("4"):
            return "Visa"
        if digits.startswith(("51", "52", "53", "54", "55")):
            return "Mastercard"
        if digits.startswith(("34", "37")):
            return "American Express"
        if digits.startswith("6011"):
            return "Discover"
        return None

    def _format_phone(self, digits: str) -> str:
        """Format phone number for display."""
        length = len(digits)
        if length == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        if length == 11:
            return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        if length == 12:
            return f"+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
        return digits

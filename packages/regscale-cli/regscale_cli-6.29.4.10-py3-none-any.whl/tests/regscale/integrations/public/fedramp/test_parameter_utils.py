#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for parameter_utils module.

Tests parameter ID conversion between legacy Rev4 format and OSCAL format.
"""

import pytest

from regscale.integrations.public.fedramp.parameter_utils import (
    convert_legacy_to_oscal_param_id,
    format_parameter_name,
    normalize_parameter_id,
    parse_oscal_param_id,
)


class TestConvertLegacyToOscalParamId:
    """Test convert_legacy_to_oscal_param_id function"""

    def test_basic_control_single_digit(self):
        """Test basic control with single-digit number"""
        result = convert_legacy_to_oscal_param_id("ac-1", 1)
        assert result == "ac-01_odp.01"

    def test_basic_control_double_digit(self):
        """Test basic control with double-digit number"""
        result = convert_legacy_to_oscal_param_id("ac-12", 1)
        assert result == "ac-12_odp.01"

    def test_uppercase_input(self):
        """Test that uppercase input is normalized"""
        result = convert_legacy_to_oscal_param_id("AC-1", 1)
        assert result == "ac-01_odp.01"

    def test_control_enhancement(self):
        """Test control enhancement format"""
        result = convert_legacy_to_oscal_param_id("AC-2(1)", 1)
        assert result == "ac-02.1_odp.01"

    def test_control_enhancement_no_parens(self):
        """Test control enhancement that's already formatted"""
        result = convert_legacy_to_oscal_param_id("ac-2.1", 1)
        assert result == "ac-02.1_odp.01"

    def test_double_digit_parameter(self):
        """Test parameter with double-digit number"""
        result = convert_legacy_to_oscal_param_id("si-12", 10)
        assert result == "si-12_odp.10"

    def test_spaces_removed(self):
        """Test that spaces are removed from input"""
        result = convert_legacy_to_oscal_param_id("ac- 1", 1)
        assert result == "ac-01_odp.01"

    def test_various_control_families(self):
        """Test different control families"""
        test_cases = [
            ("ac-1", 1, "ac-01_odp.01"),
            ("au-5", 2, "au-05_odp.02"),
            ("cm-2", 3, "cm-02_odp.03"),
            ("ia-5", 1, "ia-05_odp.01"),
            ("sc-7", 5, "sc-07_odp.05"),
            ("si-2", 1, "si-02_odp.01"),
        ]
        for control_id, param_num, expected in test_cases:
            result = convert_legacy_to_oscal_param_id(control_id, param_num)
            assert result == expected, f"Failed for {control_id}, {param_num}"


class TestParseOscalParamId:
    """Test parse_oscal_param_id function"""

    def test_parse_oscal_format(self):
        """Test parsing OSCAL format parameter ID"""
        result = parse_oscal_param_id("ac-01_odp.01")
        assert result is not None
        assert result["control_id"] == "ac-01"
        assert result["param_number"] == 1
        assert result["format"] == "oscal"

    def test_parse_legacy_format(self):
        """Test parsing legacy format parameter ID"""
        result = parse_oscal_param_id("ac-1_prm_1")
        assert result is not None
        assert result["control_id"] == "ac-1"
        assert result["param_number"] == 1
        assert result["format"] == "legacy"

    def test_parse_control_enhancement_oscal(self):
        """Test parsing control enhancement in OSCAL format"""
        result = parse_oscal_param_id("ac-02.1_odp.03")
        assert result is not None
        assert result["control_id"] == "ac-02.1"
        assert result["param_number"] == 3
        assert result["format"] == "oscal"

    def test_parse_control_enhancement_legacy(self):
        """Test parsing control enhancement in legacy format"""
        result = parse_oscal_param_id("ac-2.1_prm_5")
        assert result is not None
        assert result["control_id"] == "ac-2.1"
        assert result["param_number"] == 5
        assert result["format"] == "legacy"

    def test_parse_invalid_format(self):
        """Test parsing invalid parameter ID"""
        result = parse_oscal_param_id("invalid-format")
        assert result is None

    def test_parse_empty_string(self):
        """Test parsing empty string"""
        result = parse_oscal_param_id("")
        assert result is None

    def test_parse_none(self):
        """Test parsing None value"""
        result = parse_oscal_param_id(None)
        assert result is None

    def test_parse_uppercase(self):
        """Test that uppercase is normalized"""
        result = parse_oscal_param_id("AC-01_ODP.01")
        assert result is not None
        assert result["control_id"] == "ac-01"


class TestNormalizeParameterId:
    """Test normalize_parameter_id function"""

    def test_normalize_legacy_to_oscal(self):
        """Test normalizing legacy format to OSCAL"""
        result = normalize_parameter_id("ac-1_prm_1")
        assert result == "ac-01_odp.01"

    def test_normalize_already_oscal(self):
        """Test normalizing already OSCAL format returns same"""
        result = normalize_parameter_id("ac-01_odp.01")
        assert result == "ac-01_odp.01"

    def test_normalize_invalid(self):
        """Test normalizing invalid format returns as-is"""
        result = normalize_parameter_id("invalid-format")
        assert result == "invalid-format"

    def test_normalize_control_enhancement(self):
        """Test normalizing control enhancement"""
        result = normalize_parameter_id("ac-2.1_prm_3")
        assert result == "ac-02.1_odp.03"

    def test_normalize_batch(self):
        """Test normalizing multiple parameter IDs"""
        test_cases = [
            ("ac-1_prm_1", "ac-01_odp.01"),
            ("ac-01_odp.01", "ac-01_odp.01"),
            ("si-12_prm_10", "si-12_odp.10"),
            ("cm-2.1_prm_5", "cm-02.1_odp.05"),
        ]
        for input_id, expected in test_cases:
            result = normalize_parameter_id(input_id)
            assert result == expected, f"Failed for {input_id}"


class TestFormatParameterName:
    """Test format_parameter_name function (now using OSCAL format)"""

    def test_format_basic(self):
        """Test basic parameter name formatting"""
        result = format_parameter_name("ac-1", 1)
        assert result == "ac-01_odp.01"

    def test_format_uppercase(self):
        """Test formatting with uppercase input"""
        result = format_parameter_name("AC-2", 3)
        assert result == "ac-02_odp.03"

    def test_format_enhancement(self):
        """Test formatting control enhancement"""
        result = format_parameter_name("ac-2(1)", 1)
        assert result == "ac-02.1_odp.01"

    def test_format_double_digit_param(self):
        """Test formatting with double-digit parameter number"""
        result = format_parameter_name("si-12", 10)
        assert result == "si-12_odp.10"

    def test_format_matches_convert(self):
        """Test that format_parameter_name matches convert_legacy_to_oscal_param_id"""
        test_cases = [
            ("ac-1", 1),
            ("au-5", 3),
            ("cm-2", 5),
            ("ia-5", 7),
        ]
        for control_id, param_num in test_cases:
            format_result = format_parameter_name(control_id, param_num)
            convert_result = convert_legacy_to_oscal_param_id(control_id, param_num)
            assert (
                format_result == convert_result
            ), f"Mismatch for {control_id}, {param_num}: {format_result} != {convert_result}"


class TestBackwardCompatibility:
    """Test backward compatibility scenarios"""

    def test_legacy_ac_1_prm_1(self):
        """Test legacy format ac-1_prm_1 converts correctly"""
        parsed = parse_oscal_param_id("ac-1_prm_1")
        assert parsed["format"] == "legacy"
        normalized = normalize_parameter_id("ac-1_prm_1")
        assert normalized == "ac-01_odp.01"

    def test_legacy_with_parentheses(self):
        """Test legacy format with control enhancements"""
        # Legacy system would have created: ac-2.1_prm_3
        normalized = normalize_parameter_id("ac-2.1_prm_3")
        assert normalized == "ac-02.1_odp.03"

    def test_oscal_formats_unchanged(self):
        """Test that existing OSCAL formats are not changed"""
        test_cases = [
            "ac-01_odp.01",
            "ac-01_odp.o3",  # Some OSCAL variants use 'o' prefix
            "ac-02.1_odp.05",
            "si-12_odp.10",
        ]
        for param_id in test_cases:
            result = normalize_parameter_id(param_id)
            # Should return unchanged (though o3 format won't parse, so returns as-is)
            assert result == param_id or param_id.endswith("o3")


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_zero_param_number(self):
        """Test parameter number of 0"""
        result = convert_legacy_to_oscal_param_id("ac-1", 0)
        assert result == "ac-01_odp.00"

    def test_large_param_number(self):
        """Test large parameter number"""
        result = convert_legacy_to_oscal_param_id("ac-1", 99)
        assert result == "ac-01_odp.99"

    def test_very_large_param_number(self):
        """Test very large parameter number (over 2 digits)"""
        result = convert_legacy_to_oscal_param_id("ac-1", 100)
        assert result == "ac-01_odp.100"

    def test_empty_control_id(self):
        """Test empty control ID"""
        result = convert_legacy_to_oscal_param_id("", 1)
        # Should still work, just produce odd output
        assert "_odp.01" in result

    def test_whitespace_only(self):
        """Test whitespace-only control ID"""
        result = convert_legacy_to_oscal_param_id("   ", 1)
        assert "_odp.01" in result

    def test_special_characters(self):
        """Test control ID with special characters"""
        result = convert_legacy_to_oscal_param_id("ac-1(2)(3)", 1)
        # Parentheses should be removed
        assert "ac-01.2.3_odp.01" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

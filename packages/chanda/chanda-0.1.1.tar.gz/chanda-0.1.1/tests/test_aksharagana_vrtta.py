#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Chanda meter identification

Tests various Sanskrit meters including Sama-vṛtta, Ardhasama-vṛtta,
Viṣama-vṛtta, and Mātrā-vṛtta.

@author: Hrishikesh Terdalkar
"""

import pytest
from chanda import identify_meter, analyze_text, Chanda
from chanda.utils import get_default_data_path


# Example verses for different meters
METER_EXAMPLES = {
    "शालिनी": [
        "माता रामो मत्पिता रामचन्द्रः",
        "स्वामी रामो मत्सखा रामचन्द्रः।",
        "सर्वस्वं मे रामचन्द्रो दयालुर्",
        "नान्यं‌ जाने नैव जाने न जाने॥"
    ],
    "इन्द्रवज्रा": [
        "लोकाभिरामं रणरङ्गधीरं",
        "राजीवनेत्रं रघुवंशनाथम्।",
        "कारुण्यरूपं करुणाकरं तं",
        "श्रीरामचन्द्रं शरणं प्रपद्ये॥"
    ],
    "वसन्ततिलका": [
        "योऽन्तः प्रविश्य मम वाचमिमां प्रसुप्तां",
        "सञ्जीवयत्यखिलशक्तिधरः स्वधाम्ना।",
        "अन्यांश्च हस्तचरणश्रवणत्वगादीन्",
        "प्राणान्नमो भगवते पुरुषाय तुभ्यम्॥"
    ],
    "भुजङ्गप्रयात": [
        "नमस्ते सदा वत्सले मातृभूमे",
        "त्वया हिन्दुभूमे सुखं वर्धितोऽहम्।",
        "महामङ्गले पुण्यभूमे त्वदर्थे",
        "पतत्वेष कायो नमस्ते नमस्ते॥"
    ],
    "पञ्चचामर": [
        "जटाटवीगलज्जलप्रवाहपावितस्थले",
        "गलेऽवलम्ब्य लम्बितां भुजङ्गतुङ्गमालिकाम्।",
        "डमड्डमड्डमड्डमन्निनादवड्डमर्वयम्",
        "चकार चण्डताण्डवं तनोतु नः शिवः शिवम्॥"
    ],
    "शार्दूलविक्रीडित": [
        "विद्या नाम नरस्य रूपमधिकं प्रच्छन्नगुप्तं धनम्",
        "विद्या भोगकरी यशः सुखकरी विद्या गुरूणां गुरुः।",
        "विद्या बन्धुजनो विदेशगमने विद्या परा देवता",
        "विद्या राजसु पूज्यते न हि धनं विद्याविहीनः पशुः॥"
    ]
}


class TestMeterIdentification:
    """Test basic meter identification functionality"""

    @pytest.fixture
    def chanda(self):
        """Create Chanda instance"""
        return Chanda(get_default_data_path())

    def test_shalini_identification(self, chanda):
        """Test Śālinī meter identification"""
        line = METER_EXAMPLES["शालिनी"][0]
        result = identify_meter(line)

        assert result['found'], "Should identify Śālinī meter"
        assert 'शालिनी' in result['display_chanda'], "Should contain Śālinī"

    def test_indravajra_identification(self, chanda):
        """Test Indravajrā meter identification"""
        line = METER_EXAMPLES["इन्द्रवज्रा"][0]
        result = identify_meter(line)

        assert result['found'], "Should identify Indravajrā meter"
        assert 'इन्द्रवज्रा' in result['display_chanda'], "Should contain Indravajrā"

    def test_vasantatilaka_identification(self, chanda):
        """Test Vasantatilakā meter identification"""
        line = METER_EXAMPLES["वसन्ततिलका"][0]
        result = identify_meter(line)

        assert result['found'], "Should identify Vasantatilakā meter"
        assert 'वसन्ततिलका' in result['display_chanda'] or 'वसन्ततिलक' in result['display_chanda']

    def test_bhujangaprayat_identification(self, chanda):
        """Test Bhujaṅgaprayāta meter identification"""
        line = METER_EXAMPLES["भुजङ्गप्रयात"][0]
        result = identify_meter(line)

        assert result['found'], "Should identify Bhujaṅgaprayāta meter"
        # May appear with different spellings
        assert any(x in result['display_chanda'] for x in ['भुजङ्ग', 'भुजंग'])

    def test_panchachamara_identification(self, chanda):
        """Test Pañcacāmara meter identification"""
        line = METER_EXAMPLES["पञ्चचामर"][0]
        result = identify_meter(line)

        assert result['found'], "Should identify Pañcacāmara meter"
        # Check if identified (may have variations)

    def test_shardulavikridita_identification(self, chanda):
        """Test Śārdūlavikrīḍita meter identification"""
        line = METER_EXAMPLES["शार्दूलविक्रीडित"][0]
        result = identify_meter(line)

        assert result['found'], "Should identify Śārdūlavikrīḍita meter"
        assert 'शार्दूल' in result['display_chanda']


class TestVerseAnalysis:
    """Test verse-level analysis"""

    def test_shalini_verse(self):
        """Test complete Śālinī verse"""
        verse = "\n".join(METER_EXAMPLES["शालिनी"])
        results = analyze_text(verse, verse_mode=True)

        assert len(results['result']['verse']) > 0, "Should identify at least one verse"
        verse_result = results['result']['verse'][0]

        if verse_result.get('chanda'):
            best_meters, score = verse_result['chanda']
            assert 'शालिनी' in best_meters or score > 0

    def test_indravajra_verse(self):
        """Test complete Indravajrā verse"""
        verse = "\n".join(METER_EXAMPLES["इन्द्रवज्रा"])
        results = analyze_text(verse, verse_mode=True)

        assert len(results['result']['verse']) > 0, "Should identify at least one verse"
        verse_result = results['result']['verse'][0]

        if verse_result.get('chanda'):
            best_meters, score = verse_result['chanda']
            assert score >= 3  # At least 3 out of 4 lines should match

    def test_vasantatilaka_verse(self):
        """Test complete Vasantatilakā verse"""
        verse = "\n".join(METER_EXAMPLES["वसन्ततिलका"])
        results = analyze_text(verse, verse_mode=True)

        assert len(results['result']['verse']) > 0, "Should identify at least one verse"


class TestCoreFeatures:
    """Test core functionality"""

    @pytest.fixture
    def chanda(self):
        """Create Chanda instance"""
        return Chanda(get_default_data_path())

    def test_mark_lg(self, chanda):
        """Test Laghu-Guru marking"""
        text = "धर्मक्षेत्रे"
        syllables, lg_marks = chanda.mark_lg(text)

        assert len(lg_marks) > 0, "Should return LG marks"
        assert all(mark in ['L', 'G', ''] for mark in lg_marks), "Marks should be L, G, or empty"

    def test_lg_to_gana(self, chanda):
        """Test LG to Gana conversion"""
        lg_str = "LGGLGGLGG"
        gana_str = chanda.lg_to_gana(lg_str)

        assert len(gana_str) == 3, "Should convert to 3 ganas"
        assert all(g in 'YRTMBJSNLG' for g in gana_str), "Should be valid gana symbols"

    def test_gana_to_lg(self, chanda):
        """Test Gana to LG conversion"""
        gana_str = "YMT"
        lg_str = chanda.gana_to_lg(gana_str)

        assert len(lg_str) == 9, "Should convert to 9 LG marks"
        assert all(lg in 'LG' for lg in lg_str), "Should be L or G"

    def test_count_matra(self, chanda):
        """Test mātrā counting"""
        gana_str = "YMT"  # LGG GGG GGL
        matra_count = chanda.count_matra(gana_str)

        # L=1, G=2: 1+2+2 + 2+2+2 + 2+2+1 = 16
        assert matra_count == 16, f"Expected 16 mātrās, got {matra_count}"


class TestFuzzyMatching:
    """Test fuzzy matching functionality"""

    def test_fuzzy_match_close(self):
        """Test fuzzy matching with close match"""
        # Intentionally slightly incorrect meter
        line = "धर्मक्षेत्रे कुरुक्षेत्रे"
        result = identify_meter(line, fuzzy=True, k=5)

        if not result['found'] and result['fuzzy']:
            assert len(result['fuzzy']) > 0, "Should return fuzzy matches"
            best_match = result['fuzzy'][0]
            assert 'similarity' in best_match
            assert 0 <= best_match['similarity'] <= 1

    def test_fuzzy_match_parameters(self):
        """Test fuzzy matching parameter k"""
        line = "रामो राजमणिः सदा"

        # Test with k=3
        result = identify_meter(line, fuzzy=True, k=3)
        if result['fuzzy']:
            assert len(result['fuzzy']) <= 3, "Should return at most k matches"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_input(self):
        """Test with empty input"""
        result = identify_meter("")
        # Should handle gracefully without crashing
        assert isinstance(result, dict)

    def test_whitespace_only(self):
        """Test with whitespace only"""
        result = identify_meter("   ")
        assert isinstance(result, dict)

    def test_single_syllable(self):
        """Test with single syllable"""
        result = identify_meter("रा")
        assert isinstance(result, dict)

    def test_very_long_line(self):
        """Test with very long line"""
        long_line = "रामो राजमणिः सदा विजयते " * 10
        result = identify_meter(long_line)
        assert isinstance(result, dict)


class TestMultiScript:
    """Test multi-script support"""

    def test_devanagari(self):
        """Test Devanagari input"""
        result = identify_meter("को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्")
        assert isinstance(result, dict)

    def test_iast(self):
        """Test IAST input"""
        result = identify_meter("dharmakṣetre kurukṣetre samavetā yuyutsavaḥ")
        assert isinstance(result, dict)


class TestOutputFormat:
    """Test output format and structure"""

    def test_result_structure(self):
        """Test result dictionary structure"""
        line = METER_EXAMPLES["इन्द्रवज्रा"][0]
        result = identify_meter(line)

        # Check required keys
        assert 'found' in result
        assert 'syllables' in result
        assert 'lg' in result
        assert 'gana' in result
        assert 'length' in result
        assert 'matra' in result
        assert 'display_chanda' in result
        assert 'display_gana' in result

    def test_display_fields(self):
        """Test display field formatting"""
        line = METER_EXAMPLES["इन्द्रवज्रा"][0]
        result = identify_meter(line)

        if result['found']:
            assert isinstance(result['display_chanda'], str)
            assert isinstance(result['display_gana'], str)
            assert isinstance(result['display_line'], str)


# Parameterized tests for all meter examples
@pytest.mark.parametrize("meter_name,lines", METER_EXAMPLES.items())
def test_all_meter_examples(meter_name, lines):
    """Test all provided meter examples"""
    # Test first line of each meter
    result = identify_meter(lines[0])

    # Should either identify correctly or at least not crash
    assert isinstance(result, dict)
    assert 'found' in result

    # If found, should have valid structure
    if result['found']:
        assert 'display_chanda' in result
        assert len(result['display_chanda']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

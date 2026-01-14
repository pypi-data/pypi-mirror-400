"""Python tests for hangeul_jamo library"""

import hangeul_jamo_rs as hj


class TestHCJ:
    """Test HCJ (Hangul Compatibility Jamo) functions"""

    def test_decompose_hcj(self):
        assert hj.decompose_hcj("한글") == "ㅎㅏㄴㄱㅡㄹ"
        assert hj.decompose_hcj("안녕하세요") == "ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ"
        assert hj.decompose_hcj("Hello 한글!") == "Hello ㅎㅏㄴㄱㅡㄹ!"

    def test_compose_hcj(self):
        assert hj.compose_hcj("ㅎㅏㄴㄱㅡㄹ") == "한글"
        assert hj.compose_hcj("ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ") == "안녕하세요"
        assert hj.compose_hcj("Hello ㅎㅏㄴㄱㅡㄹ!") == "Hello 한글!"

    def test_roundtrip_hcj(self):
        original = "안녕하세요 Hello 世界!"
        decomposed = hj.decompose_hcj(original)
        composed = hj.compose_hcj(decomposed)
        assert composed == original


class TestJamo:
    """Test U+11xx jamo functions"""

    def test_decompose_jamo(self):
        result = hj.decompose_jamo("한글")
        assert len(result) == 6  # 한(3) + 글(3) = 6 chars

        result = hj.decompose_jamo("Hello 한글!")
        assert "Hello " in result
        assert result.endswith("!")

    def test_compose_jamo(self):
        decomposed = hj.decompose_jamo("한글")
        composed = hj.compose_jamo(decomposed)
        assert composed == "한글"

    def test_roundtrip_jamo(self):
        original = "안녕하세요 Hello 世界!"
        decomposed = hj.decompose_jamo(original)
        composed = hj.compose_jamo(decomposed)
        assert composed == original


class TestCharacterChecks:
    """Test character type checking functions"""

    def test_is_hangul_syllable(self):
        assert hj.is_hangul_syllable("한") == True
        assert hj.is_hangul_syllable("글") == True
        assert hj.is_hangul_syllable("a") == False
        assert hj.is_hangul_syllable("ㄱ") == False

    def test_is_hcj(self):
        assert hj.is_hcj("ㄱ") == True
        assert hj.is_hcj("ㅏ") == True
        assert hj.is_hcj("ㄲ") == True
        assert hj.is_hcj("한") == False
        assert hj.is_hcj("a") == False

    def test_is_jamo(self):
        assert hj.is_jamo("\u1100") == True  # ᄀ (lead)
        assert hj.is_jamo("\u1161") == True  # ᅡ (vowel)
        assert hj.is_jamo("\u11a8") == True  # ᆨ (tail)
        assert hj.is_jamo("ㄱ") == False  # HCJ
        assert hj.is_jamo("한") == False

    def test_is_jamo_lead(self):
        assert hj.is_jamo_lead("ㄱ") == True
        assert hj.is_jamo_lead("ㄲ") == True
        assert hj.is_jamo_lead("ㅏ") == False

    def test_is_jamo_vowel(self):
        assert hj.is_jamo_vowel("ㅏ") == True
        assert hj.is_jamo_vowel("ㅘ") == True
        assert hj.is_jamo_vowel("ㄱ") == False

    def test_is_jamo_tail(self):
        assert hj.is_jamo_tail("ㄱ") == True
        assert hj.is_jamo_tail("ㄺ") == True
        assert hj.is_jamo_tail("ㅏ") == False

    def test_is_jamo_compound(self):
        assert hj.is_jamo_compound("ㄲ") == True  # double consonant
        assert hj.is_jamo_compound("ㅘ") == True  # diphthong
        assert hj.is_jamo_compound("ㄺ") == True  # cluster
        assert hj.is_jamo_compound("ㄱ") == False


class TestCompound:
    """Test compound jamo functions"""

    def test_decompose_compound(self):
        assert hj.decompose_compound("ㄲ") == ("ㄱ", "ㄱ")
        assert hj.decompose_compound("ㅘ") == ("ㅗ", "ㅏ")
        assert hj.decompose_compound("ㄳ") == ("ㄱ", "ㅅ")
        assert hj.decompose_compound("ㅢ") == ("ㅡ", "ㅣ")

    def test_compose_compound(self):
        assert hj.compose_compound(["ㄱ", "ㄱ"]) == "ㄲ"
        assert hj.compose_compound(["ㅗ", "ㅏ"]) == "ㅘ"
        assert hj.compose_compound(["ㄱ", "ㅅ"]) == "ㄳ"
        assert hj.compose_compound(["ㅡ", "ㅣ"]) == "ㅢ"


class TestConversion:
    """Test jamo-HCJ conversion functions"""

    def test_jamo_to_hcj(self):
        assert hj.jamo_to_hcj("\u1100") == "ㄱ"  # ᄀ -> ㄱ
        assert hj.jamo_to_hcj("\u1161") == "ㅏ"  # ᅡ -> ㅏ
        assert hj.jamo_to_hcj("\u11a8") == "ㄱ"  # ᆨ -> ㄱ

    def test_hcj_to_jamo(self):
        assert hj.hcj_to_jamo("ㄱ", "lead") == "\u1100"  # ㄱ -> ᄀ
        assert hj.hcj_to_jamo("ㅏ", "vowel") == "\u1161"  # ㅏ -> ᅡ
        assert hj.hcj_to_jamo("ㄱ", "tail") == "\u11a8"  # ㄱ -> ᆨ

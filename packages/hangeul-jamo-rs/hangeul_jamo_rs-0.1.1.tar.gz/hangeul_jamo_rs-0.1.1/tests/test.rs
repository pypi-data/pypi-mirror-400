#[cfg(test)]
mod tests {
    use hangeul_jamo::core::*;
    use hangeul_jamo::hcj::*;
    use hangeul_jamo::jamo::*;

    #[test]
    fn test_is_hangul_syllable() {
        assert!(is_hangul_syllable('한'));
        assert!(is_hangul_syllable('글'));
        assert!(!is_hangul_syllable('a'));
        assert!(!is_hangul_syllable('ㄱ'));
    }

    #[test]
    fn test_decompose_hcj() {
        assert_eq!(decompose_hcj("한글"), "ㅎㅏㄴㄱㅡㄹ");
        assert_eq!(decompose_hcj("안녕하세요"), "ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ");
        assert_eq!(decompose_hcj("Hello 한글!"), "Hello ㅎㅏㄴㄱㅡㄹ!");
    }

    #[test]
    fn test_compose_hcj() {
        assert_eq!(compose_hcj("ㅎㅏㄴㄱㅡㄹ"), "한글");
        assert_eq!(compose_hcj("ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ"), "안녕하세요");
        assert_eq!(compose_hcj("Hello ㅎㅏㄴㄱㅡㄹ!"), "Hello 한글!");
    }

    #[test]
    fn test_decompose_compound() {
        assert_eq!(decompose_compound('ㄲ'), Some(vec!['ㄱ', 'ㄱ']));
        assert_eq!(decompose_compound('ㅘ'), Some(vec!['ㅗ', 'ㅏ']));
        assert_eq!(decompose_compound('ㄱ'), None);
    }

    #[test]
    fn test_compose_compound() {
        assert_eq!(compose_compound(&['ㄱ', 'ㄱ']), Some('ㄲ'));
        assert_eq!(compose_compound(&['ㅗ', 'ㅏ']), Some('ㅘ'));
    }

    #[test]
    fn test_decompose_jamo() {
        // U+11xx jamo decomposition
        let result = decompose_jamo("한글");
        assert_eq!(result.chars().count(), 6); // 한(ᄒ+ᅡ+ᆫ) + 글(ᄀ+ᅳ+ᆯ) = 6 chars

        // Check that non-Hangul characters remain unchanged
        let result = decompose_jamo("Hello 한글!");
        assert!(result.starts_with("Hello "));
        assert!(result.ends_with("!"));

        // Empty string test
        assert_eq!(decompose_jamo(""), "");
    }

    #[test]
    fn test_compose_jamo() {
        // Test basic composition
        let decomposed = decompose_jamo("한글");
        let composed = compose_jamo(&decomposed);
        assert_eq!(composed, "한글");

        // Test with mixed content
        let decomposed = decompose_jamo("안녕하세요");
        let composed = compose_jamo(&decomposed);
        assert_eq!(composed, "안녕하세요");

        // Empty string test
        assert_eq!(compose_jamo(""), "");
    }

    #[test]
    fn test_is_jamo() {
        // U+11xx jamo characters
        assert!(is_jamo('\u{1100}')); // ᄀ (lead)
        assert!(is_jamo('\u{1161}')); // ᅡ (vowel)
        assert!(is_jamo('\u{11A8}')); // ᆨ (tail)

        // Not jamo
        assert!(!is_jamo('ㄱ')); // HCJ
        assert!(!is_jamo('한')); // Hangul syllable
        assert!(!is_jamo('a')); // Latin
    }

    #[test]
    fn test_is_hcj() {
        // HCJ characters (U+31xx)
        assert!(is_hcj('ㄱ'));
        assert!(is_hcj('ㅏ'));
        assert!(is_hcj('ㄲ'));

        // Not HCJ
        assert!(!is_hcj('\u{1100}')); // U+11xx jamo
        assert!(!is_hcj('한')); // Hangul syllable
        assert!(!is_hcj('a')); // Latin
        assert!(!is_hcj('\u{3164}')); // Hangul filler (excluded)
    }

    #[test]
    fn test_jamo_hcj_conversion() {
        // jamo to HCJ
        assert_eq!(jamo_to_hcj('\u{1100}'), 'ㄱ'); // ᄀ -> ㄱ
        assert_eq!(jamo_to_hcj('\u{1161}'), 'ㅏ'); // ᅡ -> ㅏ

        // HCJ to jamo
        assert_eq!(hcj_to_jamo('ㄱ', "lead"), '\u{1100}'); // ㄱ -> ᄀ
        assert_eq!(hcj_to_jamo('ㅏ', "vowel"), '\u{1161}'); // ㅏ -> ᅡ
        assert_eq!(hcj_to_jamo('ㄱ', "tail"), '\u{11A8}'); // ㄱ -> ᆨ
    }

    #[test]
    fn test_roundtrip_hcj() {
        let original = "안녕하세요 Hello 世界!";
        let decomposed = decompose_hcj(original);
        let composed = compose_hcj(&decomposed);
        assert_eq!(composed, original);
    }

    #[test]
    fn test_roundtrip_jamo() {
        let original = "안녕하세요 Hello 世界!";
        let decomposed = decompose_jamo(original);
        let composed = compose_jamo(&decomposed);
        assert_eq!(composed, original);
    }
}

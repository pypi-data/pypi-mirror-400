use crate::constants::*;

/// Check if a character is a Hangul syllable (U+AC00 to U+D7A3)
#[inline(always)]
pub fn is_hangul_syllable(ch: char) -> bool {
    let code = ch as u32;
    (HANGUL_BASE..=HANGUL_END).contains(&code)
}

/// Decompose a compound jamo into its components
///
/// # Arguments
/// * `jamo` - A compound jamo character (e.g., 'ㄲ', 'ㅘ')
///
/// # Returns
/// * `Some(Vec<char>)` - Component jamo characters if compound
/// * `None` - If not a compound jamo
///
/// # Examples
/// ```
/// use hangeul_jamo::core::decompose_compound;
///
/// assert_eq!(decompose_compound('ㄲ'), Some(vec!['ㄱ', 'ㄱ']));
/// assert_eq!(decompose_compound('ㅘ'), Some(vec!['ㅗ', 'ㅏ']));
/// assert_eq!(decompose_compound('ㄱ'), None);
/// ```
pub fn decompose_compound(jamo: char) -> Option<Vec<char>> {
    COMPOUND_JAMO
        .iter()
        .find(|(compound, _)| compound.chars().next() == Some(jamo))
        .map(|(_, components)| components.to_vec())
}

/// Compose component jamo into a compound jamo
///
/// # Arguments
/// * `components` - Component jamo characters
///
/// # Returns
/// * `Some(char)` - The composed compound jamo if valid
/// * `None` - If components cannot be composed
///
/// # Examples
/// ```
/// use hangeul_jamo::core::compose_compound;
///
/// assert_eq!(compose_compound(&['ㄱ', 'ㄱ']), Some('ㄲ'));
/// assert_eq!(compose_compound(&['ㅗ', 'ㅏ']), Some('ㅘ'));
/// ```
pub fn compose_compound(components: &[char]) -> Option<char> {
    COMPOUND_JAMO
        .iter()
        .find(|(_, comp)| *comp == components)
        .and_then(|(compound, _)| compound.chars().next())
}

/// Convert a jamo character (U+11xx) to HCJ (U+31xx)
///
/// # Arguments
/// * `ch` - A jamo character
///
/// # Returns
/// * The corresponding HCJ character, or the input if not convertible
///
/// # Examples
/// ```
/// use hangeul_jamo::core::jamo_to_hcj;
///
/// assert_eq!(jamo_to_hcj('ᄀ'), 'ㄱ');
/// ```
pub fn jamo_to_hcj(ch: char) -> char {
    let code = ch as u32;

    // Lead jamo (U+1100-U+1112) -> HCJ
    if (0x1100..=0x1112).contains(&code) {
        let index = (code - JAMO_LEAD_BASE) as usize;
        if index < HCJ_LEADS.len() {
            return HCJ_LEADS[index];
        }
    }

    // Vowel jamo (U+1161-U+1175) -> HCJ
    if (0x1161..=0x1175).contains(&code) {
        let index = (code - JAMO_VOWEL_BASE) as usize;
        if index < HCJ_VOWELS.len() {
            return HCJ_VOWELS[index];
        }
    }

    // Tail jamo (U+11A8-U+11C2) -> HCJ
    if (0x11A8..=0x11C2).contains(&code) {
        let index = ((code - JAMO_TAIL_BASE) as usize) + 1;
        if index < HCJ_TAILS.len() {
            return HCJ_TAILS[index];
        }
    }

    ch
}

/// Convert an HCJ character to jamo (U+11xx)
///
/// # Arguments
/// * `ch` - An HCJ character
/// * `position` - The position context ("lead", "vowel", "tail")
///
/// # Returns
/// * The corresponding jamo character, or the input if not convertible
///
/// # Examples
/// ```
/// use hangeul_jamo::core::hcj_to_jamo;
///
/// assert_eq!(hcj_to_jamo('ㄱ', "lead"), 'ᄀ');
/// assert_eq!(hcj_to_jamo('ㅏ', "vowel"), 'ᅡ');
/// ```
pub fn hcj_to_jamo(ch: char, position: &str) -> char {
    match position {
        "lead" => {
            if let Some(index) = get_lead_index(ch) {
                if let Some(jamo) = char::from_u32(JAMO_LEAD_BASE + index as u32) {
                    return jamo;
                }
            }
        }
        "vowel" => {
            if let Some(index) = get_vowel_index(ch) {
                if let Some(jamo) = char::from_u32(JAMO_VOWEL_BASE + index as u32) {
                    return jamo;
                }
            }
        }
        "tail" => {
            if let Some(index) = get_tail_index(ch) {
                if index > 0 {
                    if let Some(jamo) = char::from_u32(JAMO_TAIL_BASE + (index - 1) as u32) {
                        return jamo;
                    }
                }
            }
        }
        _ => {}
    }
    ch
}

use crate::constants::*;
use crate::lookup_tables::*;

/// Check if a character is a Hangul Compatibility Jamo (U+31xx)
#[inline(always)]
pub fn is_hcj(ch: char) -> bool {
    let code = ch as u32;
    (HCJ_BASE..=HCJ_END).contains(&code) && code != 0x3164
}

#[inline(always)]
const fn utf8_char_width(b: u8) -> usize {
    const UTF8_CHAR_WIDTH: &[u8; 256] = &[
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
        4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ];
    UTF8_CHAR_WIDTH[b as usize] as usize
}

// Helper function to get next character and its end position
#[inline(always)]
fn next_char(bytes: &[u8], start: usize) -> Option<(usize, char)> {
    if start >= bytes.len() {
        return None;
    }

    let first_byte = bytes[start];
    let width = utf8_char_width(first_byte);

    if start + width > bytes.len() {
        return None;
    }

    // SAFETY: We've checked the bounds
    let s = unsafe { std::str::from_utf8_unchecked(&bytes[start..start + width]) };
    s.chars().next().map(|ch| (start + width, ch))
}

/// Decompose Hangul syllables in text into HCJ jamo characters
///
/// Uses a compile-time generated lookup table for maximum performance.
/// The lookup table contains all 11,172 Hangul syllables pre-decomposed.
///
/// # Arguments
/// * `text` - Input text containing Hangul syllables
///
/// # Returns
/// * String with Hangul syllables decomposed into HCJ jamo
///
/// # Examples
/// ```
/// use hangeul_jamo::hcj::decompose_hcj;
///
/// assert_eq!(decompose_hcj("한글"), "ㅎㅏㄴㄱㅡㄹ");
/// assert_eq!(decompose_hcj("Hello 한글!"), "Hello ㅎㅏㄴㄱㅡㄹ!");
/// ```
pub fn decompose_hcj(text: &str) -> String {
    let mut result = String::with_capacity(text.len() * 3);

    for ch in text.chars() {
        let code = ch as u32;
        if (HANGUL_BASE..=HANGUL_END).contains(&code) {
            let index = (code - HANGUL_BASE) as usize;
            let (lead, vowel, tail) = DECOMPOSE_LOOKUP[0][index];

            result.push(lead);
            result.push(vowel);
            if tail != '\0' {
                result.push(tail);
            }
        } else {
            result.push(ch);
        }
    }

    result
}

/// Compose jamo characters in text into Hangul syllables
///
/// This function uses pre-built vector-based lookup tables for optimal performance,
/// similar to the Python implementation.
///
/// # Arguments
/// * `text` - Input text containing jamo characters
///
/// # Returns
/// * String with jamo characters composed into Hangul syllables
///
/// # Examples
/// ```
/// use hangeul_jamo::hcj::compose_hcj;
///
/// assert_eq!(compose_hcj("ㅎㅏㄴㄱㅡㄹ"), "한글");
/// assert_eq!(compose_hcj("Hello ㅎㅏㄴㄱㅡㄹ!"), "Hello 한글!");
/// ```
pub fn compose_hcj(text: &str) -> String {
    if text.is_empty() {
        return String::new();
    }

    let mut result = String::with_capacity(text.len() / 2);
    let bytes = text.as_bytes();
    let mut i = 0;

    while i < bytes.len() {
        // Try to get 3 UTF-8 characters starting from position i
        let ch1_start = i;
        let ch1 = if let Some((ch1_end, ch1)) = next_char(bytes, ch1_start) {
            i = ch1_end;
            ch1
        } else {
            break;
        };

        // Get lead index
        let lead_idx = if let Some(idx) = get_lead_index(ch1) {
            idx
        } else {
            result.push(ch1);
            continue;
        };

        // Try 3-jamo composition first
        if i < bytes.len() {
            if let Some((ch2_end, ch2)) = next_char(bytes, i) {
                // Get vowel index
                let vowel_idx = if let Some(idx) = get_vowel_index(ch2) {
                    idx
                } else {
                    result.push(ch1);
                    continue;
                };

                if ch2_end < bytes.len() {
                    if let Some((ch3_end, ch3)) = next_char(bytes, ch2_end) {
                        // Get tail index
                        if let Some(tail_idx) = get_tail_index(ch3) {
                            if tail_idx > 0 {
                                let syllable = COMPOSE_LOOKUP_3[lead_idx][vowel_idx][tail_idx];

                                // Optimization: Only check lookahead if the tail can be a leading consonant
                                // Cluster consonants (ㄳ, ㄵ, ㄶ, ㄺ-ㅀ, ㅄ) cannot start a new syllable
                                if tail_can_be_lead(tail_idx) && ch3_end < bytes.len() {
                                    if let Some((_, ch4)) = next_char(bytes, ch3_end) {
                                        if is_vowel(ch4) {
                                            // Use 2-jamo instead
                                            let syllable_2 = COMPOSE_LOOKUP_2[lead_idx][vowel_idx];
                                            i = ch2_end;
                                            result.push(syllable_2);
                                            continue;
                                        }
                                    }
                                }

                                // Use 3-jamo
                                i = ch3_end;
                                result.push(syllable);
                                continue;
                            }
                        }
                    }
                }

                // Try 2-jamo lookup
                let syllable = COMPOSE_LOOKUP_2[lead_idx][vowel_idx];
                i = ch2_end;
                result.push(syllable);
                continue;
            }
        }

        // Not composable, add as-is
        result.push(ch1);
    }

    result
}

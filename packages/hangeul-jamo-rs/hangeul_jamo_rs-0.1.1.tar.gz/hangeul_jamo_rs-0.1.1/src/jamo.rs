use crate::constants::*;

/// Check if a character is a jamo character (U+11xx)
#[inline]
pub fn is_jamo(ch: char) -> bool {
    let code = ch as u32;
    (0x1100..=0x1112).contains(&code)
        || (0x1161..=0x1175).contains(&code)
        || (0x11A8..=0x11C2).contains(&code)
}

/// Decompose Hangul syllables in text into U+11xx jamo characters
///
/// # Arguments
/// * `text` - Input text containing Hangul syllables
///
/// # Returns
/// * String with Hangul syllables decomposed into U+11xx jamo
///
/// # Examples
/// ```
/// use hangeul_jamo::jamo::decompose_jamo;
///
/// let result = decompose_jamo("한글");
/// // Returns text with U+11xx jamo characters
/// ```
pub fn decompose_jamo(text: &str) -> String {
    if text.is_empty() {
        return String::new();
    }

    let mut result = String::with_capacity(text.len() * 3);

    for ch in text.chars() {
        let code = ch as u32;
        if (HANGUL_BASE..=HANGUL_END).contains(&code) {
            let index = (code - HANGUL_BASE) as usize;
            let lead_index = index / NUM_SYLLABLES_PER_LEAD;
            let vowel_index = (index % NUM_SYLLABLES_PER_LEAD) / NUM_TAIL;
            let tail_index = index % NUM_TAIL;

            result.push(char::from_u32(JAMO_LEAD_BASE + lead_index as u32).unwrap());
            result.push(char::from_u32(JAMO_VOWEL_BASE + vowel_index as u32).unwrap());
            if tail_index > 0 {
                result.push(char::from_u32(JAMO_TAIL_BASE + (tail_index - 1) as u32).unwrap());
            }
        } else {
            result.push(ch);
        }
    }

    result
}

/// Compose U+11xx jamo characters in text into Hangul syllables
///
/// # Arguments
/// * `text` - Input text containing U+11xx jamo characters
///
/// # Returns
/// * String with jamo characters composed into Hangul syllables
///
/// # Examples
/// ```
/// use hangeul_jamo::jamo::compose_jamo;
///
/// let result = compose_jamo("jamo text");
/// // Returns text with composed syllables
/// ```
pub fn compose_jamo(text: &str) -> String {
    if text.is_empty() {
        return String::new();
    }

    let mut result = String::with_capacity(text.len() / 2);
    let chars: Vec<char> = text.chars().collect();
    let length = chars.len();
    let mut i = 0;

    while i < length {
        let ch = chars[i];
        let code = ch as u32;

        // Check if this is a lead jamo (U+1100-U+1112)
        if (0x1100..=0x1112).contains(&code) {
            let lead_index = (code - JAMO_LEAD_BASE) as usize;

            // Check for vowel
            if i + 1 < length {
                let vowel_code = chars[i + 1] as u32;
                if (0x1161..=0x1175).contains(&vowel_code) {
                    let vowel_index = (vowel_code - JAMO_VOWEL_BASE) as usize;

                    // Check for tail
                    let mut tail_index = 0;
                    let mut consumed = 2;
                    if i + 2 < length {
                        let tail_code = chars[i + 2] as u32;
                        if (0x11A8..=0x11C2).contains(&tail_code) {
                            // Check lookahead: if next char is vowel, don't consume tail
                            if i + 3 < length {
                                let next_code = chars[i + 3] as u32;
                                if (0x1161..=0x1175).contains(&next_code) {
                                    // Next is vowel, so tail should be lead of next syllable
                                } else {
                                    tail_index = (tail_code - JAMO_TAIL_BASE + 1) as usize;
                                    consumed = 3;
                                }
                            } else {
                                tail_index = (tail_code - JAMO_TAIL_BASE + 1) as usize;
                                consumed = 3;
                            }
                        }
                    }

                    // Compose syllable
                    let syllable_index =
                        lead_index * NUM_SYLLABLES_PER_LEAD + vowel_index * NUM_TAIL + tail_index;
                    result.push(char::from_u32(HANGUL_BASE + syllable_index as u32).unwrap());
                    i += consumed;
                    continue;
                }
            }
        }

        // Not composable, add as-is
        result.push(ch);
        i += 1;
    }

    result
}

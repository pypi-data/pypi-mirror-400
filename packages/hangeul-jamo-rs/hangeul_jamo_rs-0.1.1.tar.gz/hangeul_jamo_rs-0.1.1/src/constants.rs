/// Korean Hangul and Jamo constants
///
/// This module contains Unicode constants and lookup tables for Korean Hangul syllables
/// and jamo characters.

// Unicode base code points
pub const HANGUL_BASE: u32 = 0xAC00;
pub const HANGUL_END: u32 = 0xD7A3;

pub const JAMO_LEAD_BASE: u32 = 0x1100;
pub const JAMO_VOWEL_BASE: u32 = 0x1161;
pub const JAMO_TAIL_BASE: u32 = 0x11A8;

pub const HCJ_BASE: u32 = 0x3131;
pub const HCJ_END: u32 = 0x318E;

// Syllable composition constants
pub const NUM_LEAD: usize = 19;
pub const NUM_VOWEL: usize = 21;
pub const NUM_TAIL: usize = 28; // Includes no-tail case (0)

// Derived constants for syllable calculation
pub const NUM_SYLLABLES_PER_LEAD: usize = NUM_VOWEL * NUM_TAIL; // 588
pub const TOTAL_SYLLABLES: usize = NUM_LEAD * NUM_SYLLABLES_PER_LEAD; // 11172

// Leading consonants (초성) in HCJ form
pub const HCJ_LEADS: [char; 19] = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ',
    'ㅌ', 'ㅍ', 'ㅎ',
];

// Vowels (중성) in HCJ form
pub const HCJ_VOWELS: [char; 21] = [
    'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ',
    'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ',
];

// Trailing consonants (종성) in HCJ form - None represented as '\0'
pub const HCJ_TAILS: [char; 28] = [
    '\0', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ',
    'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
];

// Compound jamo components (double consonants, clusters, diphthongs)
pub const COMPOUND_JAMO: &[(&str, &[char])] = &[
    // Double consonants (쌍자음)
    ("ㄲ", &['ㄱ', 'ㄱ']),
    ("ㄸ", &['ㄷ', 'ㄷ']),
    ("ㅃ", &['ㅂ', 'ㅂ']),
    ("ㅆ", &['ㅅ', 'ㅅ']),
    ("ㅉ", &['ㅈ', 'ㅈ']),
    // Consonant clusters (자음군)
    ("ㄳ", &['ㄱ', 'ㅅ']),
    ("ㄵ", &['ㄴ', 'ㅈ']),
    ("ㄶ", &['ㄴ', 'ㅎ']),
    ("ㄺ", &['ㄹ', 'ㄱ']),
    ("ㄻ", &['ㄹ', 'ㅁ']),
    ("ㄼ", &['ㄹ', 'ㅂ']),
    ("ㄽ", &['ㄹ', 'ㅅ']),
    ("ㄾ", &['ㄹ', 'ㅌ']),
    ("ㄿ", &['ㄹ', 'ㅍ']),
    ("ㅀ", &['ㄹ', 'ㅎ']),
    ("ㅄ", &['ㅂ', 'ㅅ']),
    // Diphthongs (이중모음)
    ("ㅘ", &['ㅗ', 'ㅏ']),
    ("ㅙ", &['ㅗ', 'ㅐ']),
    ("ㅚ", &['ㅗ', 'ㅣ']),
    ("ㅝ", &['ㅜ', 'ㅓ']),
    ("ㅞ", &['ㅜ', 'ㅔ']),
    ("ㅟ", &['ㅜ', 'ㅣ']),
    ("ㅢ", &['ㅡ', 'ㅣ']),
];

// Lookup table for lead consonant indices
// HCJ range: 0x3131 (ㄱ) to 0x314E (ㅎ) = 30 characters
// Use i8 with -1 for invalid entries to save space
const LEAD_LOOKUP: [i8; 30] = [
    0,  // 0x3131 ㄱ
    1,  // 0x3132 ㄲ
    -1, // 0x3133 ㄳ (not a lead)
    2,  // 0x3134 ㄴ
    -1, // 0x3135 ㄵ (not a lead)
    -1, // 0x3136 ㄶ (not a lead)
    3,  // 0x3137 ㄷ
    4,  // 0x3138 ㄸ
    5,  // 0x3139 ㄹ
    -1, // 0x313A ㄺ (not a lead)
    -1, // 0x313B ㄻ (not a lead)
    -1, // 0x313C ㄼ (not a lead)
    -1, // 0x313D ㄽ (not a lead)
    -1, // 0x313E ㄾ (not a lead)
    -1, // 0x313F ㄿ (not a lead)
    -1, // 0x3140 ㅀ (not a lead)
    6,  // 0x3141 ㅁ
    7,  // 0x3142 ㅂ
    8,  // 0x3143 ㅃ
    -1, // 0x3144 ㅄ (not a lead)
    9,  // 0x3145 ㅅ
    10, // 0x3146 ㅆ
    11, // 0x3147 ㅇ
    12, // 0x3148 ㅈ
    13, // 0x3149 ㅉ
    14, // 0x314A ㅊ
    15, // 0x314B ㅋ
    16, // 0x314C ㅌ
    17, // 0x314D ㅍ
    18, // 0x314E ㅎ
];

/// Get index of lead consonant, returns None if not found
/// Optimized with lookup table instead of match statement
#[inline(always)]
pub fn get_lead_index(ch: char) -> Option<usize> {
    let code = ch as u32;
    if code < 0x3131 || code > 0x314E {
        return None;
    }
    let idx = LEAD_LOOKUP[(code - 0x3131) as usize];
    if idx >= 0 { Some(idx as usize) } else { None }
}

// Lookup table for vowel indices
// HCJ vowel range: 0x314F (ㅏ) to 0x3163 (ㅣ) = 21 characters
const VOWEL_LOOKUP: [i8; 21] = [
    0,  // 0x314F ㅏ
    1,  // 0x3150 ㅐ
    2,  // 0x3151 ㅑ
    3,  // 0x3152 ㅒ
    4,  // 0x3153 ㅓ
    5,  // 0x3154 ㅔ
    6,  // 0x3155 ㅕ
    7,  // 0x3156 ㅖ
    8,  // 0x3157 ㅗ
    9,  // 0x3158 ㅘ
    10, // 0x3159 ㅙ
    11, // 0x315A ㅚ
    12, // 0x315B ㅛ
    13, // 0x315C ㅜ
    14, // 0x315D ㅝ
    15, // 0x315E ㅞ
    16, // 0x315F ㅟ
    17, // 0x3160 ㅠ
    18, // 0x3161 ㅡ
    19, // 0x3162 ㅢ
    20, // 0x3163 ㅣ
];

/// Get index of vowel, returns None if not found
/// Optimized with lookup table instead of match statement
#[inline(always)]
pub fn get_vowel_index(ch: char) -> Option<usize> {
    let code = ch as u32;
    if code < 0x314F || code > 0x3163 {
        return None;
    }
    let idx = VOWEL_LOOKUP[(code - 0x314F) as usize];
    Some(idx as usize)
}

// Lookup table for tail consonant indices
// HCJ tail range: 0x3131 (ㄱ) to 0x314E (ㅎ) = 30 characters (same as lead)
// Note: tails include consonant clusters (ㄳ, ㄵ, etc.)
const TAIL_LOOKUP: [i8; 30] = [
    1,  // 0x3131 ㄱ
    2,  // 0x3132 ㄲ
    3,  // 0x3133 ㄳ
    4,  // 0x3134 ㄴ
    5,  // 0x3135 ㄵ
    6,  // 0x3136 ㄶ
    7,  // 0x3137 ㄷ
    -1, // 0x3138 ㄸ (not used as tail)
    8,  // 0x3139 ㄹ
    9,  // 0x313A ㄺ
    10, // 0x313B ㄻ
    11, // 0x313C ㄼ
    12, // 0x313D ㄽ
    13, // 0x313E ㄾ
    14, // 0x313F ㄿ
    15, // 0x3140 ㅀ
    16, // 0x3141 ㅁ
    17, // 0x3142 ㅂ
    -1, // 0x3143 ㅃ (not used as tail)
    18, // 0x3144 ㅄ
    19, // 0x3145 ㅅ
    20, // 0x3146 ㅆ
    21, // 0x3147 ㅇ
    22, // 0x3148 ㅈ
    -1, // 0x3149 ㅉ (not used as tail)
    23, // 0x314A ㅊ
    24, // 0x314B ㅋ
    25, // 0x314C ㅌ
    26, // 0x314D ㅍ
    27, // 0x314E ㅎ
];

/// Get index of tail consonant, returns None if not found
/// Optimized with lookup table instead of match statement
#[inline(always)]
pub fn get_tail_index(ch: char) -> Option<usize> {
    // Special case for null character
    if ch == '\0' {
        return Some(0);
    }

    let code = ch as u32;
    if code < 0x3131 || code > 0x314E {
        return None;
    }
    let idx = TAIL_LOOKUP[(code - 0x3131) as usize];
    if idx >= 0 { Some(idx as usize) } else { None }
}

/// Check if character is a leading consonant
#[inline]
pub fn is_lead(ch: char) -> bool {
    matches!(
        ch,
        'ㄱ' | 'ㄲ'
            | 'ㄴ'
            | 'ㄷ'
            | 'ㄸ'
            | 'ㄹ'
            | 'ㅁ'
            | 'ㅂ'
            | 'ㅃ'
            | 'ㅅ'
            | 'ㅆ'
            | 'ㅇ'
            | 'ㅈ'
            | 'ㅉ'
            | 'ㅊ'
            | 'ㅋ'
            | 'ㅌ'
            | 'ㅍ'
            | 'ㅎ'
    )
}

/// Check if character is a vowel
#[inline]
pub fn is_vowel(ch: char) -> bool {
    // Reuse get_vowel_index to avoid duplicate logic
    get_vowel_index(ch).is_some()
}

/// Check if character is a trailing consonant
#[inline]
pub fn is_tail(ch: char) -> bool {
    matches!(
        ch,
        'ㄱ' | 'ㄲ'
            | 'ㄳ'
            | 'ㄴ'
            | 'ㄵ'
            | 'ㄶ'
            | 'ㄷ'
            | 'ㄹ'
            | 'ㄺ'
            | 'ㄻ'
            | 'ㄼ'
            | 'ㄽ'
            | 'ㄾ'
            | 'ㄿ'
            | 'ㅀ'
            | 'ㅁ'
            | 'ㅂ'
            | 'ㅄ'
            | 'ㅅ'
            | 'ㅆ'
            | 'ㅇ'
            | 'ㅈ'
            | 'ㅊ'
            | 'ㅋ'
            | 'ㅌ'
            | 'ㅍ'
            | 'ㅎ'
    )
}

/// Check if character is a compound jamo
#[inline]
pub fn is_compound(ch: char) -> bool {
    COMPOUND_JAMO
        .iter()
        .any(|(c, _)| c.chars().next() == Some(ch))
}

/// Check if a tail consonant can also be used as a leading consonant
/// This is used for lookahead optimization in compose()
/// Only these consonants need lookahead checking because they can start a new syllable
#[inline]
pub fn tail_can_be_lead(tail_idx: usize) -> bool {
    // tail_idx to consonant mapping (from HCJ_TAILS):
    // 1:ㄱ, 2:ㄲ, 4:ㄴ, 7:ㄷ, 8:ㄹ, 16:ㅁ, 17:ㅂ, 19:ㅅ, 20:ㅆ, 21:ㅇ, 22:ㅈ, 23:ㅊ, 24:ㅋ, 25:ㅌ, 26:ㅍ, 27:ㅎ
    // Cluster consonants (ㄳ, ㄵ, ㄶ, ㄺ-ㅀ, ㅄ) cannot be leading consonants
    matches!(
        tail_idx,
        1 | 2 | 4 | 7 | 8 | 16 | 17 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27
    )
}

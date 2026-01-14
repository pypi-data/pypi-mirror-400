use crate::constants::*;

// Compile-time generated lookup table for decomposition
// Each Hangul syllable (U+AC00 to U+D7A3) maps to its decomposed form
// The decomposed form is stored as up to 3 chars: [lead, vowel, tail]
// If there's no tail, the third element is '\0'
const fn generate_decompose_lookup() -> [[(char, char, char); 11172]; 1] {
    let mut table = [[(HCJ_LEADS[0], HCJ_VOWELS[0], '\0'); 11172]; 1];

    let mut syllable_idx = 0;
    while syllable_idx < 11172 {
        let lead_index = syllable_idx / NUM_SYLLABLES_PER_LEAD;
        let vowel_index = (syllable_idx % NUM_SYLLABLES_PER_LEAD) / NUM_TAIL;
        let tail_index = syllable_idx % NUM_TAIL;

        let lead = HCJ_LEADS[lead_index];
        let vowel = HCJ_VOWELS[vowel_index];
        let tail = if tail_index > 0 {
            HCJ_TAILS[tail_index]
        } else {
            '\0'
        };

        table[0][syllable_idx] = (lead, vowel, tail);
        syllable_idx += 1;
    }

    table
}

// Compile-time generated lookup tables for composition
// 2D array: [lead_idx][vowel_idx] -> syllable
const fn generate_compose_lookup_2() -> [[char; NUM_VOWEL]; NUM_LEAD] {
    let mut table = [['\0'; NUM_VOWEL]; NUM_LEAD];

    let mut lead_idx = 0;
    while lead_idx < NUM_LEAD {
        let mut vowel_idx = 0;
        while vowel_idx < NUM_VOWEL {
            let syllable_code =
                HANGUL_BASE + (lead_idx * NUM_SYLLABLES_PER_LEAD + vowel_idx * NUM_TAIL) as u32;
            // char::from_u32 is not const, so we use unsafe transmute
            // Safety: We know the range is valid Hangul syllables (0xAC00-0xD7A3)
            table[lead_idx][vowel_idx] = unsafe { core::char::from_u32_unchecked(syllable_code) };
            vowel_idx += 1;
        }
        lead_idx += 1;
    }

    table
}

// 3D array: [lead_idx][vowel_idx][tail_idx] -> syllable
const fn generate_compose_lookup_3() -> [[[char; NUM_TAIL]; NUM_VOWEL]; NUM_LEAD] {
    let mut table = [[['\0'; NUM_TAIL]; NUM_VOWEL]; NUM_LEAD];

    let mut lead_idx = 0;
    while lead_idx < NUM_LEAD {
        let mut vowel_idx = 0;
        while vowel_idx < NUM_VOWEL {
            let mut tail_idx = 1; // Start at 1, skip 0 (no tail)
            while tail_idx < NUM_TAIL {
                let syllable_code = HANGUL_BASE
                    + (lead_idx * NUM_SYLLABLES_PER_LEAD + vowel_idx * NUM_TAIL + tail_idx) as u32;
                // Safety: We know the range is valid Hangul syllables (0xAC00-0xD7A3)
                table[lead_idx][vowel_idx][tail_idx] =
                    unsafe { core::char::from_u32_unchecked(syllable_code) };
                tail_idx += 1;
            }
            vowel_idx += 1;
        }
        lead_idx += 1;
    }

    table
}

pub static DECOMPOSE_LOOKUP: [[(char, char, char); 11172]; 1] = generate_decompose_lookup();
pub static COMPOSE_LOOKUP_2: [[char; NUM_VOWEL]; NUM_LEAD] = generate_compose_lookup_2();

pub static COMPOSE_LOOKUP_3: [[[char; NUM_TAIL]; NUM_VOWEL]; NUM_LEAD] =
    generate_compose_lookup_3();

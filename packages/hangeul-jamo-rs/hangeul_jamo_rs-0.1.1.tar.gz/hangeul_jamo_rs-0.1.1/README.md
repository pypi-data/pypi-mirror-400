# hangeul_jamo_rs

A high-performance Korean Hangul syllable and jamo manipulation library written in Rust with Python bindings.

## Features

- **Fast decomposition/composition** using pre-computed lookup tables
- **Dual API support**: Both Rust and Python
- **Two jamo formats**: HCJ (U+31xx) and U+11xx jamo
- **Compound jamo handling**: Decompose/compose complex jamo characters

## Installation

### Rust

```toml
[dependencies]
hangeul_jamo = "0.1"
```

## Usage

### Rust

```rust
use hangeul_jamo::hcj::{decompose_hcj, compose_hcj};

// HCJ decomposition/composition
assert_eq!(decompose_hcj("한글"), "ㅎㅏㄴㄱㅡㄹ");
assert_eq!(compose_hcj("ㅎㅏㄴㄱㅡㄹ"), "한글");

// U+11xx jamo
use hangeul_jamo::jamo::{decompose_jamo, compose_jamo};
let jamo = decompose_jamo("한글");
assert_eq!(compose_jamo(&jamo), "한글");

// Compound jamo
use hangeul_jamo::core::{decompose_compound, compose_compound};
assert_eq!(decompose_compound('ㄲ'), Some(vec!['ㄱ', 'ㄱ']));
assert_eq!(compose_compound(&['ㄱ', 'ㄱ']), Some('ㄲ'));
```

## API Reference

### Core Functions

#### HCJ (Hangul Compatibility Jamo - U+31xx)
- `decompose_hcj(text)` - Decompose syllables into HCJ jamo (한 → ㅎㅏㄴ)
- `compose_hcj(text)` - Compose HCJ jamo into syllables (ㅎㅏㄴ → 한)

#### U+11xx Jamo
- `decompose_jamo(text)` - Decompose syllables into U+11xx jamo
- `compose_jamo(text)` - Compose U+11xx jamo into syllables

#### Character Checks
- `is_hangul_syllable(ch)` - Check if character is Hangul syllable (U+AC00-U+D7A3)
- `is_hcj(ch)` - Check if character is HCJ (U+31xx)
- `is_jamo(ch)` - Check if character is U+11xx jamo
- `is_jamo_lead(ch)` - Check if leading consonant
- `is_jamo_vowel(ch)` - Check if vowel
- `is_jamo_tail(ch)` - Check if trailing consonant
- `is_jamo_compound(ch)` - Check if compound jamo (ㄲ, ㅘ, etc.)

#### Compound Jamo
- `decompose_compound(jamo)` - Decompose compound jamo (ㄲ → [ㄱ, ㄱ])
- `compose_compound(components)` - Compose into compound ([ㄱ, ㄱ] → ㄲ)

#### Conversion
- `jamo_to_hcj(ch)` - Convert U+11xx jamo to HCJ (ᄀ → ㄱ)
- `hcj_to_jamo(ch, position)` - Convert HCJ to U+11xx jamo (ㄱ → ᄀ)
  - `position`: "lead", "vowel", or "tail"


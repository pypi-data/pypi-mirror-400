/// Hangeul Rust - A high-performance Korean Hangul syllable and jamo manipulation library
///
/// This library provides efficient functions for decomposing and composing Korean
/// Hangul syllables and jamo characters, with both Rust and Python APIs.
pub mod constants;
pub mod core;
pub mod hcj;
pub mod jamo;
pub mod lookup_tables;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Check if a character is a Hangul syllable (U+AC00 to U+D7A3)
///
/// Args:
///     ch (str): A single character to check
///
/// Returns:
///     bool: True if the character is a Hangul syllable, False otherwise
///
/// Examples:
///     >>> is_hangul_syllable('한')
///     True
///     >>> is_hangul_syllable('a')
///     False
///     >>> is_hangul_syllable('ㄱ')
///     False
#[pyfunction]
fn is_hangul_syllable(ch: &str) -> PyResult<bool> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;
    Ok(core::is_hangul_syllable(c))
}

/// Check if a character is a jamo character (U+11xx)
///
/// Args:
///     ch (str): A single character to check
///
/// Returns:
///     bool: True if the character is a jamo, False otherwise
///
/// Examples:
///     >>> is_jamo('ᄀ')
///     True
///     >>> is_jamo('ㄱ')
///     False
#[pyfunction]
fn is_jamo(ch: &str) -> PyResult<bool> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;
    Ok(jamo::is_jamo(c))
}

/// Check if a character is a Hangul Compatibility Jamo (U+31xx)
///
/// Args:
///     ch (str): A single character to check
///
/// Returns:
///     bool: True if the character is HCJ, False otherwise
///
/// Examples:
///     >>> is_hcj('ㄱ')
///     True
///     >>> is_hcj('ᄀ')
///     False
#[pyfunction]
fn is_hcj(ch: &str) -> PyResult<bool> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;
    Ok(hcj::is_hcj(c))
}

/// Check if a character is a leading jamo consonant
///
/// Args:
///     ch (str): A single character to check
///
/// Returns:
///     bool: True if the character is a leading jamo, False otherwise
#[pyfunction]
fn is_jamo_lead(ch: &str) -> PyResult<bool> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;
    Ok(constants::is_lead(c))
}

/// Check if a character is a jamo vowel
///
/// Args:
///     ch (str): A single character to check
///
/// Returns:
///     bool: True if the character is a jamo vowel, False otherwise
#[pyfunction]
fn is_jamo_vowel(ch: &str) -> PyResult<bool> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;
    Ok(constants::is_vowel(c))
}

/// Check if a character is a trailing jamo consonant
///
/// Args:
///     ch (str): A single character to check
///
/// Returns:
///     bool: True if the character is a trailing jamo, False otherwise
#[pyfunction]
fn is_jamo_tail(ch: &str) -> PyResult<bool> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;
    Ok(constants::is_tail(c))
}

/// Check if a jamo is a compound (double consonant, cluster, or diphthong)
///
/// Args:
///     ch (str): A single character to check
///
/// Returns:
///     bool: True if the character is a compound jamo, False otherwise
///
/// Examples:
///     >>> is_jamo_compound('ㄲ')
///     True
///     >>> is_jamo_compound('ㅘ')
///     True
///     >>> is_jamo_compound('ㄱ')
///     False
#[pyfunction]
fn is_jamo_compound(ch: &str) -> PyResult<bool> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;
    Ok(constants::is_compound(c))
}

/// Decompose Hangul syllables in text into HCJ jamo characters
///
/// Args:
///     text (str): Input text containing Hangul syllables
///
/// Returns:
///     str: Text with Hangul syllables decomposed into HCJ jamo
///
/// Examples:
///     >>> decompose_hcj('한글')
///     'ㅎㅏㄴㄱㅡㄹ'
///     >>> decompose_hcj('Hello 한글!')
///     'Hello ㅎㅏㄴㄱㅡㄹ!'
#[pyfunction]
fn decompose_hcj(text: &str) -> String {
    hcj::decompose_hcj(text)
}

/// Compose HCJ jamo characters in text into Hangul syllables
///
/// Args:
///     text (str): Input text containing HCJ jamo characters
///
/// Returns:
///     str: Text with jamo characters composed into Hangul syllables
///
/// Examples:
///     >>> compose_hcj('ㅎㅏㄴㄱㅡㄹ')
///     '한글'
///     >>> compose_hcj('Hello ㅎㅏㄴㄱㅡㄹ!')
///     'Hello 한글!'
#[pyfunction]
fn compose_hcj(text: &str) -> String {
    hcj::compose_hcj(text)
}

/// Decompose Hangul syllables in text into U+11xx jamo characters
///
/// Args:
///     text (str): Input text containing Hangul syllables
///
/// Returns:
///     str: Text with Hangul syllables decomposed into U+11xx jamo
///
/// Examples:
///     >>> decompose_jamo('한글')
///     # Returns text with U+11xx jamo
#[pyfunction]
fn decompose_jamo(text: &str) -> String {
    jamo::decompose_jamo(text)
}

/// Compose U+11xx jamo characters in text into Hangul syllables
///
/// Args:
///     text (str): Input text containing U+11xx jamo characters
///
/// Returns:
///     str: Text with jamo characters composed into Hangul syllables
///
/// Examples:
///     >>> compose_jamo('jamo text')
///     # Returns text with composed syllables
#[pyfunction]
fn compose_jamo(text: &str) -> String {
    jamo::compose_jamo(text)
}

/// Decompose a compound jamo into its components
///
/// Args:
///     jamo (str): A compound jamo character (e.g., 'ㄲ', 'ㅘ')
///
/// Returns:
///     tuple[str, ...]: Component jamo characters
///
/// Raises:
///     ValueError: If the input is not a compound jamo
///
/// Examples:
///     >>> decompose_compound('ㄲ')
///     ('ㄱ', 'ㄱ')
///     >>> decompose_compound('ㅘ')
///     ('ㅗ', 'ㅏ')
#[pyfunction]
fn decompose_compound(py: Python, jamo: &str) -> PyResult<Py<pyo3::types::PyTuple>> {
    let ch = jamo
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;

    let components = core::decompose_compound(ch)
        .ok_or_else(|| PyValueError::new_err(format!("'{}' is not a compound jamo", ch)))?;

    let strings: Vec<String> = components.iter().map(|c| c.to_string()).collect();
    Ok(pyo3::types::PyTuple::new(py, strings)?.unbind())
}

/// Compose component jamo into a compound jamo
///
/// Args:
///     components (tuple or list): Component jamo characters
///
/// Returns:
///     str: The composed compound jamo
///
/// Raises:
///     ValueError: If the components cannot be composed
///
/// Examples:
///     >>> compose_compound(('ㄱ', 'ㄱ'))
///     'ㄲ'
///     >>> compose_compound(['ㅗ', 'ㅏ'])
///     'ㅘ'
#[pyfunction]
fn compose_compound(components: Vec<String>) -> PyResult<String> {
    let chars: Vec<char> = components.iter().filter_map(|s| s.chars().next()).collect();

    let compound = core::compose_compound(&chars)
        .ok_or_else(|| PyValueError::new_err("Cannot compose compound jamo from components"))?;

    Ok(compound.to_string())
}

/// Convert a jamo character (U+11xx) to HCJ (U+31xx)
///
/// Args:
///     char (str): A jamo character
///
/// Returns:
///     str: The corresponding HCJ character, or the input if not convertible
///
/// Examples:
///     >>> jamo_to_hcj('ᄀ')
///     'ㄱ'
#[pyfunction]
fn jamo_to_hcj(ch: &str) -> PyResult<String> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;

    Ok(core::jamo_to_hcj(c).to_string())
}

/// Convert an HCJ character to jamo (U+11xx)
///
/// Args:
///     char (str): An HCJ character
///     position (str): The position context ("lead", "vowel", "tail"), defaults to "vowel"
///
/// Returns:
///     str: The corresponding jamo character, or the input if not convertible
///
/// Examples:
///     >>> hcj_to_jamo('ㄱ', 'lead')
///     'ᄀ'
///     >>> hcj_to_jamo('ㅏ', 'vowel')
///     'ᅡ'
#[pyfunction]
#[pyo3(signature = (ch, position="vowel"))]
fn hcj_to_jamo(ch: &str, position: &str) -> PyResult<String> {
    let c = ch
        .chars()
        .next()
        .ok_or_else(|| PyValueError::new_err("Expected a single character"))?;

    Ok(core::hcj_to_jamo(c, position).to_string())
}

/// A high-performance Korean Hangul syllable and jamo manipulation library
#[pymodule]
fn hangeul_jamo_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_hangul_syllable, m)?)?;
    m.add_function(wrap_pyfunction!(is_jamo, m)?)?;
    m.add_function(wrap_pyfunction!(is_hcj, m)?)?;
    m.add_function(wrap_pyfunction!(is_jamo_lead, m)?)?;
    m.add_function(wrap_pyfunction!(is_jamo_vowel, m)?)?;
    m.add_function(wrap_pyfunction!(is_jamo_tail, m)?)?;
    m.add_function(wrap_pyfunction!(is_jamo_compound, m)?)?;
    m.add_function(wrap_pyfunction!(decompose_hcj, m)?)?;
    m.add_function(wrap_pyfunction!(compose_hcj, m)?)?;
    m.add_function(wrap_pyfunction!(decompose_jamo, m)?)?;
    m.add_function(wrap_pyfunction!(compose_jamo, m)?)?;
    m.add_function(wrap_pyfunction!(decompose_compound, m)?)?;
    m.add_function(wrap_pyfunction!(compose_compound, m)?)?;
    m.add_function(wrap_pyfunction!(jamo_to_hcj, m)?)?;
    m.add_function(wrap_pyfunction!(hcj_to_jamo, m)?)?;
    Ok(())
}

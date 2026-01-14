use criterion::{BenchmarkId, Criterion, criterion_group, criterion_main};
use hangeul_jamo::{core::*, hcj::*, jamo::*};
use std::hint::black_box;

fn generate_test_data() -> (String, String, String) {
    // Korean text
    let korean_text = "안녕하세요 여러분! 오늘은 날씨가 정말 좋네요. ".repeat(1000);

    // Jamo text for composition
    let jamo_text = "ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ ㅇㅕㄹㅓㅂㅜㄴ! ㅇㅗㄴㅡㄹㅇㅡㄴ ㄴㅏㄹㅆㅣㄱㅏ ㅈㅓㅇㅁㅏㄹ ㅈㅗㅎㄴㅔㅇㅛ. ".repeat(1000);

    // Long text with various syllables
    let long_text = (0..11172)
        .step_by(10)
        .map(|i| char::from_u32(0xAC00 + i).unwrap())
        .collect::<String>()
        .repeat(10);

    (korean_text, jamo_text, long_text)
}

fn benchmark_decompose_hcj(c: &mut Criterion) {
    let (korean_text, _, _) = generate_test_data();

    c.bench_function("decompose_hcj", |b| {
        b.iter(|| decompose_hcj(black_box(&korean_text)))
    });
}

fn benchmark_compose_hcj(c: &mut Criterion) {
    let (_, jamo_text, _) = generate_test_data();

    c.bench_function("compose_hcj", |b| {
        b.iter(|| compose_hcj(black_box(&jamo_text)))
    });
}

fn benchmark_decompose_jamo(c: &mut Criterion) {
    let (korean_text, _, _) = generate_test_data();

    c.bench_function("decompose_jamo", |b| {
        b.iter(|| decompose_jamo(black_box(&korean_text)))
    });
}

fn benchmark_compose_jamo(c: &mut Criterion) {
    let (korean_text, _, _) = generate_test_data();
    let jamo_unicode = decompose_jamo(&korean_text);

    c.bench_function("compose_jamo", |b| {
        b.iter(|| compose_jamo(black_box(&jamo_unicode)))
    });
}

fn benchmark_character_checks(c: &mut Criterion) {
    let test_chars = ['한', 'ㄱ', 'ᄀ', 'a', '가', 'ㅘ', 'ㄲ'];

    c.bench_function("is_hangul_syllable", |b| {
        b.iter(|| {
            for &ch in &test_chars {
                black_box(is_hangul_syllable(ch));
            }
        })
    });
}

fn benchmark_mixed_operations(c: &mut Criterion) {
    let (korean_text, _, _) = generate_test_data();

    c.bench_function("mixed_operations", |b| {
        b.iter(|| {
            let jamo = decompose_hcj(black_box(&korean_text));
            let recomposed = compose_hcj(&jamo);
            let jamo_unicode = decompose_jamo(&recomposed);
            let final_text = compose_jamo(&jamo_unicode);
            black_box(final_text);
        })
    });
}

fn benchmark_compose_variants(c: &mut Criterion) {
    let mut group = c.benchmark_group("compose_variants");

    let (_, jamo_text, _) = generate_test_data();

    // Benchmark different text sizes
    for size in [100, 500, 1000].iter() {
        let text: String = jamo_text.chars().take(*size).collect();
        group.bench_with_input(BenchmarkId::from_parameter(size), &text, |b, text| {
            b.iter(|| compose_hcj(black_box(text)))
        });
    }

    group.finish();
}

fn benchmark_decompose_variants(c: &mut Criterion) {
    let mut group = c.benchmark_group("decompose_variants");

    let (korean_text, _, _) = generate_test_data();

    // Benchmark different text sizes
    for size in [100, 500, 1000].iter() {
        let text: String = korean_text.chars().take(*size).collect();
        group.bench_with_input(BenchmarkId::from_parameter(size), &text, |b, text| {
            b.iter(|| decompose_hcj(black_box(text)))
        });
    }

    group.finish();
}

criterion_group!(
    benches,
    benchmark_decompose_hcj,
    benchmark_compose_hcj,
    benchmark_decompose_jamo,
    benchmark_compose_jamo,
    benchmark_character_checks,
    benchmark_mixed_operations,
    benchmark_compose_variants,
    benchmark_decompose_variants,
);

criterion_main!(benches);

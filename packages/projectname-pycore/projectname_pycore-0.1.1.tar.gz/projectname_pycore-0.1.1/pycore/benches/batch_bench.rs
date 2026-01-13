use criterion::{
    black_box, criterion_group, criterion_main, BatchSize, BenchmarkId, Criterion, Throughput,
};
use pycore::{
    core_add_batch, core_add_batch_into, core_process_batch, core_process_batch_into, Operation,
};
use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;

static ALLOCATIONS: AtomicUsize = AtomicUsize::new(0);

struct CountingAllocator;

#[global_allocator]
static GLOBAL: CountingAllocator = CountingAllocator;

unsafe impl GlobalAlloc for CountingAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        ALLOCATIONS.fetch_add(1, Ordering::SeqCst);
        System.alloc(layout)
    }

    unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
        ALLOCATIONS.fetch_add(1, Ordering::SeqCst);
        System.alloc_zeroed(layout)
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        System.dealloc(ptr, layout)
    }

    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        ALLOCATIONS.fetch_add(1, Ordering::SeqCst);
        System.realloc(ptr, layout, new_size)
    }
}

fn reset_allocations() {
    ALLOCATIONS.store(0, Ordering::SeqCst);
}

fn allocations() -> usize {
    ALLOCATIONS.load(Ordering::SeqCst)
}

fn bench_core_add_batch(c: &mut Criterion) {
    let mut group = c.benchmark_group("core_add_batch");
    group.sample_size(50);
    group.measurement_time(Duration::from_secs(5));

    for &size in &[10usize, 100, 1_000, 10_000, 100_000, 1_000_000] {
        group.bench_with_input(BenchmarkId::from_parameter(size), &size, |b, &size| {
            let base: Vec<(i64, i64)> = (0..size as i64).map(|i| (i, i + 1)).collect();

            b.iter_batched(
                || base.clone(),
                |batch| core_add_batch(black_box(batch)),
                BatchSize::SmallInput,
            );
        });
    }

    group.finish();
}

fn build_alternating_ops(size: usize) -> Vec<Operation> {
    (0..size)
        .map(|i| {
            if i % 2 == 0 {
                Operation::Add(i as i64, (i + 1) as i64)
            } else {
                Operation::Subtract((i + 10) as i64, i as i64)
            }
        })
        .collect()
}

fn build_bursts(size: usize, burst: usize) -> Vec<Operation> {
    (0..size)
        .map(|i| {
            if (i / burst) % 2 == 0 {
                Operation::Add(i as i64, 1)
            } else {
                Operation::Subtract((i + 2) as i64, 1)
            }
        })
        .collect()
}

fn build_small_pattern(repeats: usize) -> Vec<Operation> {
    let pattern = vec![
        Operation::Add(1, 2),
        Operation::Subtract(10, 4),
        Operation::Add(-3, -7),
        Operation::Subtract(-5, -5),
    ];

    pattern.into_iter().cycle().take(repeats * 4).collect()
}

fn bench_core_process_batch(c: &mut Criterion) {
    let mut group = c.benchmark_group("core_process_batch");
    group.sample_size(50);
    group.measurement_time(Duration::from_secs(5));

    group.bench_function("alternando_sumas_y_restas_100k", |b| {
        let ops = build_alternating_ops(100_000);

        b.iter_batched(
            || ops.clone(),
            |batch| core_process_batch(black_box(batch)),
            BatchSize::SmallInput,
        );
    });

    group.bench_function("rafagas_en_bloques_100k", |b| {
        let ops = build_bursts(100_000, 50);

        b.iter_batched(
            || ops.clone(),
            |batch| core_process_batch(black_box(batch)),
            BatchSize::SmallInput,
        );
    });

    group.bench_function("patron_pequeno_repetido", |b| {
        let ops = build_small_pattern(20_000);

        b.iter_batched(
            || ops.clone(),
            |batch| core_process_batch(black_box(batch)),
            BatchSize::SmallInput,
        );
    });

    group.finish();
}

fn bench_core_process_batch_by_size(c: &mut Criterion) {
    let mut group = c.benchmark_group("core_process_batch_batch_sizes");
    group.sample_size(40);
    group.measurement_time(Duration::from_secs(6));

    for &size in &[64usize, 256, 1_024, 4_096, 16_384] {
        let ops = build_alternating_ops(size);
        group.throughput(Throughput::Elements(size as u64));

        group.bench_with_input(BenchmarkId::from_parameter(size), &size, |b, &_size| {
            b.iter_batched(
                || ops.clone(),
                |batch| core_process_batch(black_box(batch)),
                BatchSize::SmallInput,
            );
        });
    }

    group.finish();
}

fn bench_batch_with_reused_buffers(c: &mut Criterion) {
    let mut group = c.benchmark_group("core_batch_reused_buffers");
    group.sample_size(30);
    group.measurement_time(Duration::from_secs(6));

    group.bench_function("core_add_batch_reutiliza_resultados", |b| {
        let pairs: Vec<(i64, i64)> = (0..50_000).map(|i| (i as i64, i as i64 + 1)).collect();
        let mut output = Vec::with_capacity(pairs.len());

        b.iter(|| {
            reset_allocations();
            core_add_batch_into(black_box(&pairs), &mut output);
            let after_process = allocations();

            assert_eq!(
                after_process, 0,
                "La reserva inicial evita nuevas asignaciones"
            );
            black_box(&output);
        });
    });

    group.bench_function("core_process_batch_reutiliza_resultados", |b| {
        let ops = build_alternating_ops(50_000);
        let mut output = Vec::with_capacity(ops.len());

        b.iter(|| {
            reset_allocations();
            core_process_batch_into(black_box(&ops), &mut output);
            let after_process = allocations();

            assert_eq!(
                after_process, 0,
                "El buffer preasignado evita reallocations"
            );
            black_box(&output);
        });
    });

    group.finish();
}

fn bench_allocation_regressions(c: &mut Criterion) {
    let mut group = c.benchmark_group("allocation_regressions");
    group.sample_size(20);

    group.bench_function("core_add_batch_single_allocation", |b| {
        let base: Vec<(i64, i64)> = (0..1_024).map(|i| (i as i64, i as i64 + 1)).collect();

        b.iter(|| {
            reset_allocations();

            let before_clone = allocations();
            let input = base.clone();
            let after_clone = allocations();
            assert!(
                after_clone - before_clone <= 1,
                "Clonar el lote debería requerir una única asignación"
            );

            let before_process = allocations();
            let output = core_add_batch(black_box(input));
            let after_process = allocations();

            assert!(
                after_process - before_process <= 1,
                "core_add_batch debería reutilizar un único buffer preasignado"
            );

            black_box(output);
        });
    });

    group.bench_function("core_process_batch_single_allocation", |b| {
        let ops = build_alternating_ops(2_048);

        b.iter(|| {
            reset_allocations();

            let before_clone = allocations();
            let input = ops.clone();
            let after_clone = allocations();
            assert!(
                after_clone - before_clone <= 1,
                "Clonar operaciones no debería fragmentar el heap"
            );

            let before_process = allocations();
            let output = core_process_batch(black_box(input));
            let after_process = allocations();

            assert!(
                after_process - before_process <= 1,
                "core_process_batch debería reservar el vector de salida de una sola vez"
            );

            black_box(output);
        });
    });

    group.finish();
}

criterion_group!(
    benches,
    bench_core_add_batch,
    bench_core_process_batch,
    bench_core_process_batch_by_size,
    bench_batch_with_reused_buffers,
    bench_allocation_regressions
);
criterion_main!(benches);

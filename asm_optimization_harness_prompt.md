# Assembly Optimization Harness — Prompt Template

**Purpose:** Iterative assembly optimization with correctness verification and cycle-accurate timing feedback. Fill in the bracketed sections for your specific task.

---

## Prompt

I want to build an iterative assembly optimization harness for x86-64 (System V ABI, Linux). The goal is to write a function in assembly, verify it against a reference implementation, measure performance, and iterate until we hit diminishing returns.

### The task

**Function:** [DESCRIBE THE FUNCTION — e.g., "compute the dot product of two float64 arrays of length N"]

**Signature:**
```c
[RETURN TYPE] function_name([PARAMS]);
// e.g.: double dot_product(const double* a, const double* b, size_t n);
```

**Reference implementation:** [PROVIDE A C OR PYTHON IMPLEMENTATION THAT IS KNOWN-CORRECT. This is the ground truth — the assembly must produce identical output for all test inputs.]

**Input characteristics:** [DESCRIBE TYPICAL INPUT — array sizes, value ranges, alignment guarantees, anything that affects optimization strategy. e.g., "arrays are 16-byte aligned, N is always a multiple of 4, values in [-1000, 1000]"]

### Build the harness

Create three files:

1. **`reference.c`** — The reference implementation compiled as a shared object or static lib. Used only for correctness comparison.

2. **`harness.c`** — Test runner that:
   - Calls the reference implementation and the assembly implementation on the same inputs
   - Compares outputs (with tolerance for floating point: [SPECIFY TOLERANCE or "exact match for integer work"])
   - Reports pass/fail per test case with input details on failure
   - Runs a timing loop: [N_ITERATIONS, e.g., 10 million] calls, reports median cycles per call using `rdtsc` (or `clock_gettime` with `CLOCK_MONOTONIC` for wall time)
   - Pins to a single core (`sched_setaffinity`) to reduce noise
   - Test cases should include: [LIST EDGE CASES — e.g., "empty array, single element, power-of-2 lengths, non-power-of-2, maximum expected size"]

3. **`function.s`** — The assembly implementation. Start with a naive correct version. We will iterate on this.

4. **`Makefile`** — Builds everything. `make test` runs correctness checks. `make bench` runs timing. `make all` does both.

### Iteration protocol

After the harness is built:

1. I will run `make all` and give you the output (pass/fail + cycles per call)
2. You propose an optimization to `function.s` with a one-line explanation of what you're trying (e.g., "unroll inner loop 4x", "replace scalar with AVX2 packed multiply")
3. I run it again, report results
4. Repeat until cycles plateau or we hit the target

**Target:** [SPECIFY A TARGET IF KNOWN — e.g., "within 2x of the compiler's -O3 -march=native output" or "under 100 cycles" or "just explore, no fixed target"]

**Constraints:**
- [INSTRUCTION SET EXTENSIONS ALLOWED — e.g., "SSE4.2 and AVX2 only, no AVX-512" or "baseline x86-64 only, no SIMD"]
- [ABI — "System V AMD64 ABI" is the Linux default]
- [OS — Linux assumed unless specified]
- [ASSEMBLER — NASM / GAS (AT&T or Intel syntax) — pick one]

### What I care about

[OPTIONAL — e.g., "I care more about learning the optimization process than hitting a specific target" or "I need this to be production-fast, minimize cycles above all" or "I want to understand what the compiler does and whether we can beat it"]

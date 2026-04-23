# LLM-Driven Assembly Optimization — Research Landscape

**As of:** 2026-04-13
**Context:** Exploring whether LLMs can iteratively optimize assembly code using execution feedback, and whether that loop can produce training signal for fine-tuning.

---

## The key paper: SuperCoder (May 2025)

This is exactly the system we were discussing. SuperCoder demonstrates LLMs as superoptimizers for assembly — generating assembly that outperforms gcc -O3.

**What they built:**
- First large-scale assembly optimization benchmark: 8,072 programs averaging 130 lines (prior datasets were limited to 2-15 straight-line, loop-free programs)
- Evaluated 23 LLMs on the benchmark
- Fine-tuned a 7B model using RL with execution feedback as the reward signal

**Results:**
- Baseline: Claude Opus achieved 51.5% test-passing rate and 1.43x average speedup over gcc -O3
- Starting point for fine-tuning: Qwen2.5-Coder-7B-Instruct (61.4% correctness, 1.10x speedup)
- After RL fine-tuning → **SuperCoder: 95.0% correctness, 1.46x average speedup**
- Additional improvement from Best-of-N sampling and iterative refinement

**RL approach:** PPO and GRPO with a reward function integrating correctness (test case pass/fail) and performance speedup. This is the "execution feedback as training signal" loop — the model learns from its own optimization attempts.

**Why this matters:** A 7B model, after RL fine-tuning on execution feedback, beats gcc -O3 on average. The training signal is exactly what we discussed — run the code, measure the speed, feed it back.

**Sources:**
- [SuperCoder paper (arxiv)](https://arxiv.org/abs/2505.11480)
- [HuggingFace paper page](https://huggingface.co/papers/2505.11480)
- [OpenReview](https://openreview.net/forum?id=30iarHLvCS)
- [MarkTechPost summary](https://www.marktechpost.com/2025/05/24/optimizing-assembly-code-with-llms-reinforcement-learning-outperforms-traditional-compilers/)

---

## Meta LLM Compiler (2024, published CC 2025)

Foundation model approach — pre-train on compiler IR and assembly, then fine-tune for optimization tasks.

**What they built:**
- Code Llama fine-tuned on 546 billion tokens of LLVM-IR and assembly
- Two sizes: 7B and 13B parameters
- Tasks: code size optimization, disassembly (x86-64 and ARM → LLVM-IR)

**Results:**
- 77% of autotuning search optimization potential for code size
- 45% disassembly round-trip accuracy (14% exact match)
- Released under commercial license

**Relevance:** This is the foundation model for the space. SuperCoder builds on this direction but adds the RL execution-feedback loop that Meta's work stops short of.

**Sources:**
- [Meta LLM Compiler paper (arxiv)](https://arxiv.org/abs/2407.02524)
- [Meta AI research page](https://ai.meta.com/research/publications/meta-large-language-model-compiler-foundation-models-of-compiler-optimization/)
- [CC 2025 proceedings](https://dl.acm.org/doi/10.1145/3708493.3712691)

---

## The broader landscape

**Iterative feedback approaches** are now common in LLM code optimization — a 2025 survey identifies 35 studies using feedback-based iterative techniques. The pattern: generate optimization, execute, measure, feed results back to the model.

**POLO (IJCAI 2025)** — project-level code optimization using two LLM agents (Generator + Decision), where the Decision Agent incorporates performance feedback. Higher-level (not assembly-specific) but same loop structure.

**CompilerGym / MLGO (Google)** — RL environment for compiler optimization decisions (inlining, register allocation). Uses smaller specialized models. Established the infrastructure for RL-on-compilation but focused on compiler passes, not direct assembly generation.

---

## Gap analysis: what's not yet done

1. **Production-grade self-optimizing assembly pipeline** — SuperCoder proves the concept works for benchmarks. Nobody has shipped a tool that takes arbitrary C code and produces optimized assembly through LLM iteration in a CI/CD pipeline.

2. **Architecture-specific fine-tuning** — SuperCoder and LLM Compiler work on x86-64. ARM64, RISC-V, and embedded architectures are underexplored. The training data exists (compilers emit assembly for all of these) but nobody has built the benchmark harnesses.

3. **Domain-specific assembly optimization** — Hot loops in specific domains (signal processing, cryptography, numerical kernels) where the LLM could be fine-tuned on a narrow benchmark with known theoretical performance bounds. The harness we designed (correctness + timing + iteration) is exactly the right shape for this.

4. **Continuous learning from deployment** — Using production timing data as ongoing training signal. The assembly runs in production, performance is measured, delta from optimal feeds back to the model. Nobody is doing this yet.

---

## Connection to our harness design

The prompt template in `asm_optimization_harness_prompt.md` implements the same loop as SuperCoder but at the prompting level (no fine-tuning):
- Reference implementation for correctness verification
- Cycle-accurate timing for performance measurement
- Iterative refinement with human-in-the-loop running the benchmarks

SuperCoder's contribution is showing that this loop, when automated and used as an RL reward signal, produces a fine-tuned model that's better than prompting alone. If we wanted to go further than the prompt template, the path is:
1. Build the harness (our template)
2. Automate the iteration loop (script replaces human-in-the-loop)
3. Collect (input_assembly, optimized_assembly, speedup) triples
4. Use those triples as RL training signal (SuperCoder's approach)

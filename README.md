# gem5 RISC-V Custom ISA Extension: MAC & ReLU

A three-way performance comparison of custom neural network instructions (MAC, ReLU, fused MAC+ReLU) implemented as a RISC-V ISA extension in the gem5 simulator.

---

## Overview

This project extends the RISC-V ISA with two custom instructions:

| Instruction | funct7 | funct3 | opcode | Description |
|-------------|--------|--------|--------|-------------|
| `mac`       | `0x00` | `0x1`  | `0x2B` | Multiply-accumulate: `rd += rs1 * rs2` |
| `relu`      | `0x16` | `0x1`  | `0x2B` | ReLU activation: `rd = max(0, rs1)` |
| `fmacrelu`  | `0x15` | `0x1`  | `0x2B` | Fused MAC+ReLU in a single instruction |

Three benchmark configurations run a 64×64 matrix-vector multiply with ReLU activation:

- **base** — plain RISC-V, no custom instructions
- **mac_relu** — separate MAC and ReLU custom instructions
- **fmacrelu** — single fused MAC+ReLU instruction

---

## Results

| Config    | simInsts | CPI   | IPC   |
|-----------|----------|-------|-------|
| base      | 277,950  | 1.389 | 0.720 |
| mac_relu  | 270,162  | 1.307 | 0.765 |
| fmacrelu  | 269,454  | 1.307 | 0.765 |

- base → fmacrelu: **8,496 fewer instructions (3.1% reduction)**
- mac_relu → fmacrelu: **708 fewer instructions** (64 standalone ReLU instrs eliminated)

Simulated on gem5 v25.1 with AtomicSimpleCPU, classic cache hierarchy (L1I/D: 32kB, L2: 256kB).

---

## Repo Structure

```
gem5-riscv-isa-extension/
├── benchmarks/
│   ├── base.c          # Baseline: plain C multiply-accumulate + ReLU
│   ├── mac_relu.c      # Separate MAC + ReLU custom instructions
│   └── fmacrelu.c      # Fused MAC+ReLU custom instruction
├── scripts/
│   └── run_simulation.py
├── gem5-mods/
│   └── decoder.isa     # Modified RISC-V decoder with custom instructions
└── results/
    ├── base/stats.txt
    ├── mac_relu/stats.txt
    └── fmacrelu/stats.txt
```

---

## Requirements

- [gem5](https://www.gem5.org/) (tested on v25.1)
- RISC-V cross-compiler: `riscv64-unknown-elf-gcc`
- Python 3.8+

---

## Setup

### 1. Patch gem5

Copy the modified decoder into your gem5 source tree and rebuild:

```bash
cp gem5-mods/decoder.isa <gem5-root>/src/arch/riscv/isa/decoder.isa
cd <gem5-root>
scons build/RISCV/gem5.opt -j$(nproc)
```

### 2. Compile Benchmarks

```bash
cd benchmarks
riscv64-unknown-elf-gcc -O0 -nostdlib -static -o base.elf base.c
riscv64-unknown-elf-gcc -O0 -nostdlib -static -o mac_relu.elf mac_relu.c
riscv64-unknown-elf-gcc -O0 -nostdlib -static -o fmacrelu.elf fmacrelu.c
cd ..
```

### 3. Run Simulations

Run all three configs:

```bash
python3 scripts/run_simulation.py \
  --gem5 <gem5-root>/build/RISCV/gem5.opt \
  --benchmarks ./benchmarks
```

Run a single config:

```bash
python3 scripts/run_simulation.py \
  --gem5 <gem5-root>/build/RISCV/gem5.opt \
  --benchmarks ./benchmarks \
  --config fmacrelu
```

Dry run (prints commands without executing):

```bash
python3 scripts/run_simulation.py \
  --gem5 <gem5-root>/build/RISCV/gem5.opt \
  --benchmarks ./benchmarks \
  --dry-run
```

### 4. View Results

```bash
grep -E "simInsts|cpi|ipc" results/base/stats.txt
grep -E "simInsts|cpi|ipc" results/mac_relu/stats.txt
grep -E "simInsts|cpi|ipc" results/fmacrelu/stats.txt
```

---

## Instruction Encoding

All custom instructions use R-type encoding with custom-0 opcode (`0x2B`):

```
[31:25] funct7 | [24:20] rs2 | [19:15] rs1 | [14:12] funct3 | [11:7] rd | [6:0] opcode
```

Example `.word` encodings (rd=a0, rs1=a1, rs2=a2):

| Instruction | .word      |
|-------------|------------|
| mac         | 0x00C5852B |
| fmacrelu    | 0x2AC5852B |

---

## License

MIT — see [LICENSE](LICENSE).

"""
run_simulation.py
Runs gem5 RISC-V simulations for three configs:
  1. base       — no custom instructions
  2. mac_relu   — separate MAC + ReLU instructions
  3. fmacrelu   — fused MAC+ReLU instruction

Usage:
  python3 run_simulation.py --gem5 <path/to/gem5.opt> --benchmarks <dir>
  python3 run_simulation.py --gem5 ./build/RISCV/gem5.opt --benchmarks ./benchmarks
  python3 run_simulation.py --config mac_relu --gem5 ./build/RISCV/gem5.opt --benchmarks ./benchmarks
"""

import argparse
import subprocess
import os
import sys

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONFIGS = {
    "base": {
        "binary":  "base.elf",
        "out_dir": "results/base",
        "desc":    "Baseline RISC-V (no custom instructions)",
    },
    "mac_relu": {
        "binary":  "mac_relu.elf",
        "out_dir": "results/mac_relu",
        "desc":    "Separate MAC + ReLU instructions",
    },
    "fmacrelu": {
        "binary":  "fmacrelu.elf",
        "out_dir": "results/fmacrelu",
        "desc":    "Fused MAC+ReLU instruction",
    },
}

# gem5 SE mode script
GEM5_SE_SCRIPT = "configs/deprecated/example/se.py"

CPU_TYPE    = "AtomicSimpleCPU"
MEM_TYPE    = "DDR3_1600_8x8"
MEM_SIZE    = "512MB"
L1I_SIZE    = "32kB"
L1D_SIZE    = "32kB"
L2_SIZE     = "256kB"
CACHES      = True

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_cmd(gem5_bin: str, binary_path: str, out_dir: str) -> list:
    cmd = [
        gem5_bin,
        f"--outdir={out_dir}",
        GEM5_SE_SCRIPT,
        f"--cpu-type={CPU_TYPE}",
        f"--mem-type={MEM_TYPE}",
        f"--mem-size={MEM_SIZE}",
        "--cmd", binary_path,
    ]
    if CACHES:
        cmd += [
            "--caches",
            "--l2cache",
            f"--l1i_size={L1I_SIZE}",
            f"--l1d_size={L1D_SIZE}",
            f"--l2_size={L2_SIZE}",
        ]
    return cmd


def run_config(name: str, cfg: dict, gem5_bin: str, bench_dir: str, dry_run: bool):
    # flat structure: benchmarks/base.elf (not benchmarks/base/base.elf)
    binary_path = os.path.join(bench_dir, cfg["binary"])
    out_dir     = cfg["out_dir"]

    print(f"\n{'='*60}")
    print(f"Config : {name}")
    print(f"Desc   : {cfg['desc']}")
    print(f"Binary : {binary_path}")
    print(f"Output : {out_dir}")
    print(f"{'='*60}")

    if not os.path.isfile(binary_path):
        print(f"[SKIP] Binary not found: {binary_path}")
        return False

    os.makedirs(out_dir, exist_ok=True)
    cmd = build_cmd(gem5_bin, binary_path, out_dir)

    print("CMD:", " ".join(cmd))
    if dry_run:
        print("[DRY RUN] Not executing.")
        return True

    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        print(f"[ERROR] gem5 exited with code {result.returncode}")
        return False

    stats_file = os.path.join(out_dir, "stats.txt")
    if os.path.isfile(stats_file):
        print(f"[OK] stats.txt written -> {stats_file}")
    else:
        print(f"[WARN] stats.txt not found in {out_dir}")

    return True

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="gem5 RISC-V ISA extension simulation runner")
    p.add_argument("--gem5",       required=True, help="Path to gem5 binary (e.g. build/RISCV/gem5.opt)")
    p.add_argument("--benchmarks", required=True, help="Dir containing .elf binaries")
    p.add_argument("--config",     default="all", choices=["all", "base", "mac_relu", "fmacrelu"],
                   help="Which config to run (default: all)")
    p.add_argument("--dry-run",    action="store_true", help="Print commands without executing")
    return p.parse_args()


def main():
    args = parse_args()

    if not os.path.isfile(args.gem5):
        print(f"[ERROR] gem5 binary not found: {args.gem5}")
        sys.exit(1)

    if not os.path.isdir(args.benchmarks):
        print(f"[ERROR] Benchmarks dir not found: {args.benchmarks}")
        sys.exit(1)

    targets = CONFIGS if args.config == "all" else {args.config: CONFIGS[args.config]}

    results = {}
    for name, cfg in targets.items():
        ok = run_config(name, cfg, args.gem5, args.benchmarks, args.dry_run)
        results[name] = "OK" if ok else "FAILED/SKIPPED"

    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    for name, status in results.items():
        print(f"  {name:<12} {status}")
    print()


if __name__ == "__main__":
    main()

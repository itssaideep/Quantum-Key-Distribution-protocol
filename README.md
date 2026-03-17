# Quantum Key Distribution Protocol Simulation

A comprehensive quantum key distribution (QKD) simulator implementing **BB84** (prepare-and-measure) and **E91 (Ekert91)** (entanglement-based) protocols. This project demonstrates quantum cryptography principles, security metrics, and eavesdropping detection across multiple attack scenarios.

## Features

### Implemented Protocols

- **BB84 Protocol**: Prepare-and-measure QKD with 2 measurement bases
  - ~25% key efficiency due to basis sifting
  - QBER detection threshold: 11% for eavesdropping
  
- **E91 Protocol (Ekert91)**: Entanglement-based QKD with 3 measurement bases
  - 100% key efficiency (no sifting losses)
  - CHSH Bell inequality testing for eavesdropper detection
  - Classical threshold: 2.0, Quantum threshold: 2.828

### Security Analysis

- **Eavesdropping Scenarios**: 3 different Eve attack positions
  - Scenario 1: No eavesdropping (baseline)
  - Scenario 2: Eve measures before Alice
  - Scenario 3: Eve measures between Alice and Bob
  
- **Detection Metrics**:
  - QBER (Quantum Bit Error Rate) for BB84
  - CHSH inequality value for E91
  - Statistical reliability across multiple runs

### Visualizations

The `analysis/compare_protocols.py` generates 5 comprehensive comparison plots:

1. **Security Metrics Comparison** - QBER vs CHSH values
2. **Key Efficiency Comparison** - BB84 (25%) vs E91 (100%)
3. **Eavesdropping Scenarios** - E91 detection across attack positions
4. **Average Results** - Statistical averages from 10 protocol runs
5. **Protocol Comparison Table** - Feature-by-feature analysis

### Performance Benchmarking

Performance analysis module (`analysis/performance_benchmark.py`) provides:
- **Execution Time Analysis** - Protocol duration across different qubit counts
- **Scalability Testing** - How performance changes with size (100-5000 qubits)
- **Memory Profiling** - Memory consumption tracking
- **Throughput Metrics** - Key generation rate (bits/second)
- **Comparative Analysis** - BB84 vs E91 efficiency comparison
- **Bottleneck Identification** - Sifting, measurement, and simulation overhead

## Project Structure

```
quantum-key-distribution-protocol/
├── protocols/
│   ├── bb84.py              # BB84 implementation
│   ├── e91.py               # E91 with 3 eavesdropping scenarios
│   └── __init__.py
├── analysis/
│   ├── compare_protocols.py # Comprehensive visualization generator
│   ├── performance_benchmark.py # Performance benchmarking module
│   └── visualize.py         # Visualization utilities
├── eavesdropping/
│   ├── eve_strategies.py    # Eavesdropper attack implementations
│   └── __init__.py
├── utils/
│   ├── quantum_helpers.py   # Quantum state and measurement utilities
│   └── __init__.py
├── results/                 # Generated PNG visualizations & benchmark reports
├── notebooks/
│   └── bb84_tutorial.ipynb  # Interactive protocol exploration
├── main.py                  # Main execution script (runs everything)
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

**Activate (Windows):**
```bash
.\.venv\Scripts\Activate.ps1
```

**Activate (macOS/Linux):**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- `qiskit` (2.3.1+) - Quantum circuit framework
- `qiskit-aer` (0.17.2+) - Quantum simulator
- `numpy` (2.2.6+) - Numerical computation
- `matplotlib` (3.10.8+) - Data visualization

## Usage

### Run Complete Simulation (Recommended)
```bash
python main.py
```

This orchestrates:
- BB84 and E91 protocol analysis
- All eavesdropping scenarios
- Eve attack strategy testing
- Statistical comparative runs (3 iterations)
- Visualization generation
- Performance benchmarking

### Run Individual Components

**Run BB84 protocol alone:**
```bash
python protocols/bb84.py
```

**Run E91 protocol with eavesdropping scenarios:**
```bash
python protocols/e91.py
```

**Generate comparison visualizations:**
```bash
python analysis/compare_protocols.py
```
Generates 5 PNG files in `results/` folder.

**Run performance benchmarking:**
```bash
python analysis/performance_benchmark.py
```
Generates performance analysis report and CSV data.

**Interactive exploration:**
```bash
jupyter notebook notebooks/bb84_tutorial.ipynb
```

## Key Findings

Based on the simulations:

### BB84 Protocol
- **Without Eve**: QBER ≈ 3-5% (secure baseline)
- **With Eve**: QBER ≈ 23-25% (easily detected)
- **Key Generation**: ~250 bits from 1000 qubits (25% efficiency)

### E91 Protocol
- **No Eavesdropping**: CHSH ≈ 2.0-2.47 (above classical limit)
- **Eve Before Alice**: CHSH ≈ 1.74-1.93 (always detected)
- **Eve Before Bob**: CHSH ≈ 1.83-2.22 (mostly detected)
- **Key Generation**: ~1000 bits from 1000 qubits (100% efficiency)

### Security Comparison
| Metric | BB84 | E91 |
|--------|------|-----|
| Bases | 2 | 3 |
| Key Efficiency | 25% | 100% |
| Sifting Required | Yes | No |
| Security Test | Statistical (QBER) | Mathematical (Bell) |
| Eve Detection | Probabilistic | Deterministic |

## Protocol Details

### BB84 Implementation
- Alice randomly chooses basis (0° or 45°) and encodes each bit
- Bob randomly measures in same basis set
- Public basis reconciliation over classical channel
- Sifting: keep only matching bases (~50%) → 25% final key
- Eve detection: presence increases QBER above 11% threshold

### E91 Implementation
- Bell pair creation: `|Φ+⟩ = (|00⟩ + |11⟩)/√2`
- Three measurement bases: 0°, 22.5° (π/8), 45° (π/4)
- CHSH inequality: `S = |E(0,0) - E(0,2) + E(1,0) + E(1,2)|`
- No sifting: all measurement results usable
- Eve detection: CHSH drops below 2.0 when eavesdropping occurs

## Quantum Concepts

### Bell Pairs (Entanglement)
Two qubits in the state `|Φ+⟩` are perfectly correlated—measuring one instantly determines the other (non-locally). Eve's measurement on one qubit collapses the pair, introducing detectable errors.

### CHSH Bell Inequality
Classical systems satisfy `CHSH ≤ 2.0`. Quantum entanglement violates this (up to 2.828 by Tsirelson's bound), enabling secure key distribution without basis pre-agreement.

### Measurement Bases
- **BB84**: 2 bases (Rectilinear: ↕, Diagonal: ×)
- **E91**: 3 bases enabling CHSH testing to prove entanglement and detect eavesdropping

## Performance Metrics

### Security Metrics
- **QBER**: Percentage of mismatched bits in matching bases (target < 11%)
- **CHSH Value**: Violation of classical Bell inequality (target > 2.0 without Eve)
- **Key Rate**: Usable key bits per quantum state transmitted

### Benchmarking Metrics
- **Execution Time**: Total protocol duration (seconds)
- **Throughput**: Key generation rate (bits/second)
- **Scalability**: Performance scaling with qubit count
- **Memory Usage**: Peak memory consumption (MB)
- **Simulation Overhead**: Time spent in quantum simulation
- **Sifting Overhead** (BB84): Time spent filtering matching bases

### Typical Performance Results

**BB84 (1000 qubits):**
- Execution Time: ~2-3 seconds
- Sifted Key: ~250 bits
- Throughput: ~83 bits/second
- Memory: ~50-80 MB

**E91 (1000 qubits):**
- Execution Time: ~3-4 seconds
- Generated Key: ~1000 bits
- Throughput: ~250-330 bits/second
- Memory: ~60-100 MB

**Scalability (10,000 qubits):**
- BB84: ~20-25 seconds (linear scaling)
- E91: ~30-40 seconds (linear scaling)
- Memory remains proportional to qubit count

## Troubleshooting

**Import errors for qiskit?**
```bash
pip install --upgrade qiskit qiskit-aer
```

**Matplotlib display issues?**
Output automatically saves PNG files to `results/` folder regardless of matplotlib backend.

**Out of memory?**
Reduce `num_qubits` parameter in simulation functions (default: 500-1000).

## Performance Optimization Tips

1. **Batch Simulations**: Run multiple protocol instances in parallel for statistical analysis
2. **Reduce Qubit Count**: Start with 100-500 qubits for quick testing
3. **Use Caching**: Cache Bell pair circuits for E91 to reduce circuit generation overhead
4. **GPU Acceleration**: Enable Qiskit GPU simulator if available for large-scale runs
5. **Memory Profiling**: Use `performance_benchmark.py` to identify bottlenecks

## Future Enhancements

- Scenario 4: Eve eavesdrops on publicly announced bases (passive attack)
- Noise models for realistic quantum channels
- Quantum error correction integration
- GPU-accelerated simulation backend
- Additional protocols: BBM92, B92, DPS
- Real hardware implementation via Qiskit native operators
- Multi-threaded benchmarking for parallel analysis
- Apache Arrow format for large-scale data export

## References

- Bennett, C. H., & Brassard, G. (1984). "Quantum Cryptography: Public Key Distribution and Coin Tossing"
- Ekert, A. K. (1991). "Quantum cryptography based on Bell's theorem"
- Brunner, N., et al. (2014). "Bell nonlocality" (Review of Modern Physics 86.2)

## Author

Sai Deep - Quantum Cryptography Research

## License

MIT License

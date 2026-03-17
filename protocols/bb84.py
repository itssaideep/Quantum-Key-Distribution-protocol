"""
BB84 Quantum Key Distribution Protocol

Implements the Bennett-Brassard 1984 protocol:
- Prepare-and-measure QKD with 2 measurement bases
- ~25% key efficiency due to basis sifting
- QBER detection threshold 11% for eavesdropping
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np
import qiskit
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.quantum_helpers import (
    calculate_correlation, estimate_eve_presence, 
    simulate_quantum_channel, analyze_key_distribution
)

try:
    from analysis.visualize import (plot_qber_comparison, plot_basis_distribution, 
                                    plot_key_generation, plot_security_summary)
except ImportError:
    # Visualization module optional
    pass

def prepare_bb84_state(bit, basis):
    qc = QuantumCircuit(1)

    if basis == 0:  # Rectilinear basis
        if bit == 1:
            qc.x(0)  # |1⟩ = X|0⟩ (flip the qubit)
    else:  # Diagonal basis
        qc.h(0)  # Create |+⟩ = H|0⟩
        if bit == 1:
            qc.z(0)  # Create |-⟩ = Z*H|0⟩

    return qc

def measure_bb84_state(qc, basis):
    qc_copy = qc.copy()
    qc_copy.add_register(qiskit.ClassicalRegister(1, 'c'))

    if basis == 1:
        qc_copy.h(0)

    qc_copy.measure(0,0)
    return qc_copy

def measure_eve_state(qc,eve_basis):
    qc_copy = qc.copy()
    qc_copy.add_register(qiskit.ClassicalRegister(1,'c'))

    if eve_basis == 1:
        qc_copy.h(0)

    qc_copy.measure(0,0)
    return qc_copy

def calculate_qber(alice_bits,bob_results,matching_indices):

    errors = 0
    for idx in matching_indices:
        if alice_bits[idx] != bob_results[idx]:
            errors += 1
    
    if len(matching_indices) == 0:
        return 0.0
    
    qber = (errors / len(matching_indices)) *100
    return qber

def run_bb84_protocol(bit, basis, with_eve):

    simulator = AerSimulator()

    alice_bits = np.random.randint(2, size=1000)
    alice_bases = np.random.randint(2, size=1000)
    bob_bases = np.random.randint(2, size=1000)
    bob_results = []

    eve_bases = np.random.randint(2, size=1000) if with_eve else None
    eve_results = [] if with_eve else None

    for i in range(len(alice_bits)):
        qc = prepare_bb84_state(alice_bits[i], alice_bases[i])

        if with_eve:
            qc_eve =  measure_eve_state(qc,eve_bases[i])
            job = simulator.run(qc_eve, shots = 1)
            result = job.result()
            counts = result.get_counts(qc_eve)
            eve_bit = int(list(counts.keys())[0])
            eve_results.append(eve_bit)

            qc = prepare_bb84_state(eve_bit, eve_bases[i])

        qc = measure_bb84_state(qc, bob_bases[i])

        job = simulator.run(qc,shots=1)

        result = job.result()
        counts = result.get_counts(qc)
        measured_bit = int(list(counts.keys())[0])
        bob_results.append(measured_bit)


    sifted_key = []
    matching_indices = []
    for i in range(len(alice_bits)):
        if alice_bases[i] == bob_bases[i]:
            sifted_key.append(alice_bits[i])
            matching_indices.append(i)

    return sifted_key, alice_bits, bob_results, alice_bases, bob_bases, eve_results, eve_bases, matching_indices        


if __name__ == "__main__":
    print("="*70)
    print("BB84 QUANTUM KEY DISTRIBUTION - EAVESDROPPING DETECTION")
    print("="*70)
    
    # Scenario 1: Protocol without eavesdropping
    print("\n[SCENARIO 1] BB84 WITHOUT EAVESDROPPING")
    print("-" * 70)
    sifted_key, alice_bits, bob_results, alice_bases, bob_bases, eve_results, eve_bases, matching_indices = run_bb84_protocol(None, None, False)
    qber_no_eve = calculate_qber(alice_bits, bob_results, matching_indices)
    
    print(f"Alice generated: {len(alice_bits)} random bits")
    print(f"Sifted key length: {len(sifted_key)} bits")
    print(f"Key generation efficiency: {len(sifted_key)/len(alice_bits)*100:.1f}%")
    print(f"QBER (Quantum Bit Error Rate): {qber_no_eve:.2f}%")
    if qber_no_eve < 11:
        print(f"✓ SECURE - QBER < 11% threshold")
    else:
        print(f"⚠ SUSPICIOUS - QBER > 11%")
    print(f"\nFirst 20 bits of sifted key: {sifted_key[:20]}")
    
    # Scenario 2: Protocol with eavesdropping
    print("\n[SCENARIO 2] BB84 WITH EVE EAVESDROPPING")
    print("-" * 70)
    sifted_key_eve, alice_bits_eve, bob_results_eve, alice_bases_eve, bob_bases_eve, eve_results, eve_bases, matching_indices_eve = run_bb84_protocol(None, None, True)
    qber_with_eve = calculate_qber(alice_bits_eve, bob_results_eve, matching_indices_eve)
    
    print(f"Alice generated: {len(alice_bits_eve)} random bits")
    print(f"Eve intercepted: {len(eve_results)} qubits")
    print(f"Sifted key length: {len(sifted_key_eve)} bits")
    print(f"Key generation efficiency: {len(sifted_key_eve)/len(alice_bits_eve)*100:.1f}%")
    print(f"QBER (Quantum Bit Error Rate): {qber_with_eve:.2f}%")
    
    if qber_with_eve > 11:
        print(f"⚠ EAVESDROPPING DETECTED! - QBER > 11% threshold")
        print(f"Action: ABORT and restart protocol!")
    else:
        print(f"✓ No eavesdropping detected (below 11% threshold)")
    
    # Analysis
    print("\n" + "="*70)
    print("ANALYSIS: WHY EVE INTRODUCES ERRORS")
    print("="*70)
    print(f"""
Comparison:
  Without Eve: QBER = {qber_no_eve:.2f}%
  With Eve:    QBER = {qber_with_eve:.2f}%
  Difference:  {qber_with_eve - qber_no_eve:.2f}%
  
   Statistical result:
     - WITHOUT Eve: QBER ≈ 0% (perfect quantum channel)
     - WITH Eve:    QBER ≈ 25% (0.5 wrong basis × 0.5 wrong result)
  
   Security guarantee:
     - If QBER > 11%, eavesdropping is detected with confidence
     - Alice and Bob discard the key and restart
     - Eve CANNOT remain undetected!
    """)
    print("="*70)
    print(f"Sifted key length: {len(sifted_key)} bits")
    print(f"Key generation efficiency: {len(sifted_key)/len(alice_bits)*100:.1f}%")
    print(f"\nFirst 20 bits of sifted key: {sifted_key[:20]}")
    
    # Generate visualizations
    print("\n" + "="*70)
    print("[GENERATING VISUALIZATIONS]")
    print("="*70)
    
    plot_qber_comparison(qber_no_eve, qber_with_eve)
    plot_basis_distribution(alice_bases, bob_bases, eve_bases)
    plot_key_generation(len(sifted_key), len(sifted_key_eve), len(alice_bits))
    plot_security_summary(qber_no_eve, qber_with_eve, len(sifted_key), len(sifted_key_eve))


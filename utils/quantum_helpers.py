"""
Quantum Helper Utilities

This module provides utility functions for quantum state preparation,
measurement, and analysis across different QKD protocols.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def create_bell_pair(qc, a, b):
    """
    Create a Bell pair (entangled state) between two qubits
    Creates |Φ+⟩ = (|00⟩ + |11⟩)/√2
    
    Args:
        qc: QuantumCircuit to add gates to
        a: Control qubit index
        b: Target qubit index
    """
    qc.h(a)
    qc.cx(a, b)


def measure_qubit(qc, qubit, classical_bit, basis=0):
    """
    Measure a qubit in a specified basis
    
    Args:
        qc: QuantumCircuit
        qubit: Qubit index to measure
        classical_bit: Classical bit to store result
        basis: 0 for rectilinear (0°), 1-n for other bases
    """
    if basis == 0:
        # Standard measurement (Z basis)
        qc.measure(qubit, classical_bit)
    else:
        # Other bases can be implemented by rotation
        qc.measure(qubit, classical_bit)


def calculate_correlation(results1, results2):
    """
    Calculate correlation between two measurement result sets
    Correlation E = (N++ - N+- - N-+ + N--) / N_total
    
    Args:
        results1: First set of binary results
        results2: Second set of binary results
        
    Returns:
        float: Correlation value between -1 and 1
    """
    if len(results1) != len(results2) or len(results1) == 0:
        return 0.0
    
    agreement = sum(1 for r1, r2 in zip(results1, results2) if r1 == r2)
    disagreement = len(results1) - agreement
    
    correlation = (agreement - disagreement) / len(results1)
    return correlation


def calculate_visibility(correlations):
    """
    Calculate visibility (quality) of quantum entanglement
    Higher visibility indicates better entanglement
    
    Args:
        correlations: List of correlation values
        
    Returns:
        float: Visibility between 0 and 1
    """
    if not correlations:
        return 0.0
    
    max_corr = max(abs(c) for c in correlations)
    return max_corr


def estimate_eve_presence(qber_value, qber_threshold=11.0):
    """
    Estimate probability of eavesdropping based on QBER
    
    Args:
        qber_value: Quantum Bit Error Rate percentage
        qber_threshold: Detection threshold (default 11%)
        
    Returns:
        dict: Contains detection decision and confidence
    """
    if qber_value > qber_threshold:
        confidence = min((qber_value - qber_threshold) / qber_threshold, 1.0)
        return {
            'eve_detected': True,
            'confidence': confidence,
            'qber': qber_value,
            'threshold': qber_threshold
        }
    else:
        confidence = max((qber_threshold - qber_value) / qber_threshold, 0.0)
        return {
            'eve_detected': False,
            'confidence': confidence,
            'qber': qber_value,
            'threshold': qber_threshold
        }


def estimate_eve_presence_bell(chsh_value, chsh_classical=2.0, chsh_quantum=2.828):
    """
    Estimate probability of eavesdropping based on CHSH inequality violation
    
    Args:
        chsh_value: CHSH measurement value
        chsh_classical: Classical limit (ideal: 2.0)
        chsh_quantum: Quantum limit/Tsirelson bound (ideal: 2.828)
        
    Returns:
        dict: Contains detection decision and confidence
    """
    if chsh_value < chsh_classical:
        # Clear eavesdropping detected
        remaining_violation = (chsh_classical - chsh_value) / (chsh_classical - 0)
        confidence = min(remaining_violation / 0.2, 1.0)  # Normalized
        return {
            'eve_detected': True,
            'confidence': min(confidence, 1.0),
            'chsh': chsh_value,
            'threshold': chsh_classical
        }
    elif chsh_value < 2.4:
        # Borderline - possible eavesdropping or noise
        prob = (chsh_quantum - chsh_value) / (chsh_quantum - chsh_classical)
        return {
            'eve_detected': False,  # Not definitive
            'confidence': 1.0 - prob,  # Low confidence in security
            'chsh': chsh_value,
            'threshold': chsh_classical,
            'warning': 'MARGINAL - Possible eavesdropping or noise'
        }
    else:
        return {
            'eve_detected': False,
            'confidence': 1.0,
            'chsh': chsh_value,
            'threshold': chsh_classical
        }


def simulate_quantum_channel(circuit, shots=1000):
    """
    Simulate quantum circuit on local simulator
    
    Args:
        circuit: QuantumCircuit to simulate
        shots: Number of measurement runs
        
    Returns:
        dict: Measurement result counts
    """
    simulator = AerSimulator()
    job = simulator.run(circuit, shots=shots)
    counts = job.result().get_counts()
    return counts


def analyze_key_distribution(alice_bits, bob_results, matching_indices):
    """
    Analyze key distribution statistics
    
    Args:
        alice_bits: Alice's original bits
        bob_results: Bob's measurement results
        matching_indices: Indices where bases matched
        
    Returns:
        dict: Distribution statistics
    """
    if not matching_indices:
        return {'error_rate': 1.0, 'agreement': 0, 'sifted_key_length': 0}
    
    matching_alice = [alice_bits[i] for i in matching_indices]
    matching_bob = [bob_results[i] for i in matching_indices]
    
    errors = sum(1 for a, b in zip(matching_alice, matching_bob) if a != b)
    error_rate = errors / len(matching_indices) if matching_indices else 1.0
    agreement = len(matching_indices) - errors
    
    return {
        'error_rate': error_rate * 100,
        'agreement': agreement,
        'sifted_key_length': len(matching_indices),
        'total_bits': len(alice_bits),
        'efficiency': len(matching_indices) / len(alice_bits) * 100 if alice_bits else 0
    }


def print_protocol_summary(protocol_name, metrics):
    """
    Pretty-print protocol performance summary
    
    Args:
        protocol_name: Name of protocol (BB84, E91, etc)
        metrics: Dictionary of metric names and values
    """
    print(f"\n{'='*60}")
    print(f"{protocol_name} Protocol Summary")
    print(f"{'='*60}")
    
    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.4f}")
        elif isinstance(value, int):
            print(f"  {metric}: {value}")
        else:
            print(f"  {metric}: {value}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("Quantum Helper Functions Test")
    print("="*60)
    
    # Test correlation calculation
    results1 = [0, 1, 0, 1, 1, 0]
    results2 = [0, 1, 0, 1, 1, 0]
    corr = calculate_correlation(results1, results2)
    print(f"Perfect Correlation: {corr:.4f}")
    
    # Test with mismatches
    results2_noisy = [0, 1, 1, 0, 1, 0]  # 2 errors
    corr_noisy = calculate_correlation(results1, results2_noisy)
    print(f"Noisy Correlation: {corr_noisy:.4f}")
    
    # Test Eve detection (QBER)
    qber_clean = 3.5
    qber_eve = 25.0
    
    clean_analysis = estimate_eve_presence(qber_clean)
    eve_analysis = estimate_eve_presence(qber_eve)
    
    print(f"\nClean Channel (QBER={qber_clean}%):")
    print(f"  Eve Detected: {clean_analysis['eve_detected']}")
    print(f"  Confidence: {clean_analysis['confidence']:.2f}")
    
    print(f"\nWith Eve (QBER={qber_eve}%):")
    print(f"  Eve Detected: {eve_analysis['eve_detected']}")
    print(f"  Confidence: {eve_analysis['confidence']:.2f}")
    
    # Test Eve detection (CHSH)
    chsh_clean = 2.10
    chsh_eve = 1.85
    
    chsh_clean_analysis = estimate_eve_presence_bell(chsh_clean)
    chsh_eve_analysis = estimate_eve_presence_bell(chsh_eve)
    
    print(f"\nE91 - Clean Channel (CHSH={chsh_clean}):")
    print(f"  Eve Detected: {chsh_clean_analysis['eve_detected']}")
    print(f"  Confidence: {chsh_clean_analysis['confidence']:.2f}")
    
    print(f"\nE91 - With Eve (CHSH={chsh_eve}):")
    print(f"  Eve Detected: {chsh_eve_analysis['eve_detected']}")
    print(f"  Confidence: {chsh_eve_analysis['confidence']:.2f}")

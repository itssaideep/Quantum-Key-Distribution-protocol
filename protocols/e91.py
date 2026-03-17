"""
E91 Quantum Key Distribution Protocol (Ekert91)

Implements the Ekert 1991 protocol:
- Entanglement-based QKD using Bell pairs
- 3-basis measurement for CHSH Bell inequality testing
- 100% key efficiency (no sifting)
- Eavesdropping detection via CHSH violation below classical limit
"""

from qiskit import QuantumCircuit
import numpy as np
import qiskit
from qiskit_aer import AerSimulator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.quantum_helpers import (
    create_bell_pair, measure_qubit, calculate_correlation,
    estimate_eve_presence_bell, simulate_quantum_channel, 
    calculate_visibility
)

def create_bell_pair():
    qc = QuantumCircuit(2, name = "Bell Pair")
    qc.h(0)
    qc.cx(0,1)
    return qc

def measure_bell_pair(qc,qubit_index, basis):
    qc_measured = qc.copy()

    if qc_measured.num_clbits == 0:
        qc_measured.add_register(qiskit.ClassicalRegister(2,'c'))

    if basis == 0:
        pass
    elif basis == 1:
        qc_measured.ry(np.pi / 8, qubit_index)
    elif basis == 2:    
        qc_measured.ry(np.pi / 4, qubit_index)

    qc_measured.measure(qubit_index, qubit_index)

    return qc_measured

def calculate_chsh(alice_bases, bob_bases, alice_measurement, bob_measurement):
    def get_correlation(a_choice, b_choice):
        sum_corr = 0
        count = 0

        for i in range(len(alice_measurement)):
            if alice_bases[i]== a_choice and bob_bases[i] == b_choice:
                if alice_measurement[i] == bob_measurement[i]:
                    sum_corr += 1
                else:
                    sum_corr -= 1
                count += 1

        if count == 0:
            return 0
    
        return sum_corr / count

    E_00 = get_correlation(0,0)
    E_02 = get_correlation(0,2)
    E_10 = get_correlation(1,0)
    E_12 = get_correlation(1,2)

    S = E_00 - E_02 + E_10 + E_12
    CHSH = abs(S)
    return CHSH

def run_E91_protocol(num_qubits = 2000, with_eve = False):
    simulator = AerSimulator()
    alice_bases = np.random.randint(3, size=num_qubits)
    bob_bases = np.random.randint(3, size=num_qubits)   

    alice_measurements = []
    bob_measurements = []
    eve_bases = np.random.randint(3, size=num_qubits) if with_eve else None
    eve_measurements = [] if with_eve else None

    for i in range(num_qubits):
        bell_pair = create_bell_pair()

        if with_eve:
            qc_eve = measure_bell_pair(bell_pair, 0, eve_bases[i])

            job = simulator.run(qc_eve, shots=1)
            result = job.result()
            counts = result.get_counts(qc_eve)
            eve_bit = int(list(counts.keys())[0])
            eve_measurements.append(eve_bit)

        # Measure BOTH qubits in the SAME circuit
        qc_both = measure_bell_pair(bell_pair, 0, alice_bases[i])
        qc_both = measure_bell_pair(qc_both, 1, bob_bases[i])
        
        job = simulator.run(qc_both, shots=1)
        result = job.result()
        counts = result.get_counts(qc_both)
        bits = list(counts.keys())[0]
        alice_bit = int(bits[1])  # qubit 0
        bob_bit = int(bits[0])    # qubit 1
        alice_measurements.append(alice_bit)
        bob_measurements.append(bob_bit)

        if (i +1) % 250  == 0:
            print(f"Progress: {i + 1}/{num_qubits} qubits measured.")

    chsh =  calculate_chsh(alice_bases, bob_bases, alice_measurements, bob_measurements)
    sifted_keys = alice_measurements

    return{
        'sifted_keys': sifted_keys,
        'alice_measurements': alice_measurements,
        'bob_measurements': bob_measurements,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'chsh': chsh,
        'eve_measurements': eve_measurements,
        'eve_bases': eve_bases
    }

def scenario_1_no_eve(num_qubits=2000):
    """Scenario 1: No eavesdropping (baseline)"""
    simulator = AerSimulator()
    alice_bases = np.random.randint(3, size=num_qubits)
    bob_bases = np.random.randint(3, size=num_qubits)
    
    alice_measurements = []
    bob_measurements = []
    
    for i in range(num_qubits):
        bell_pair = create_bell_pair()
        
        # Alice and Bob measure the SAME Bell pair
        qc = bell_pair.copy()
        qc.add_register(qiskit.ClassicalRegister(2, 'c'))
        
        # Alice measures qubit 0
        if alice_bases[i] == 1:
            qc.ry(np.pi / 8, 0)
        elif alice_bases[i] == 2:
            qc.ry(np.pi / 4, 0)
        qc.measure(0, 1)
        
        # Bob measures qubit 1
        if bob_bases[i] == 1:
            qc.ry(np.pi / 8, 1)
        elif bob_bases[i] == 2:
            qc.ry(np.pi / 4, 1)
        qc.measure(1, 0)
        
        job = simulator.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts(qc)
        bits = list(counts.keys())[0]
        
        alice_measurements.append(int(bits[0]))
        bob_measurements.append(int(bits[1]))
        
        if (i + 1) % 125 == 0:
            print(f"  {i+1}/{num_qubits}")
    
    chsh = calculate_chsh(alice_bases, bob_bases, alice_measurements, bob_measurements)

    return {
        'chsh': chsh,
  
        'alice': alice_measurements,
        'bob': bob_measurements,
        'agreement': sum(1 for a, b in zip(alice_measurements, bob_measurements) if a == b)
    }


def scenario_2_eve_before_alice(num_qubits=2000):
    """Scenario 2: Eve intercepts and measures BEFORE Alice (maximally destructive)"""
    simulator = AerSimulator()
    alice_bases = np.random.randint(3, size=num_qubits)
    bob_bases = np.random.randint(3, size=num_qubits)
    eve_bases = np.random.randint(3, size=num_qubits)
    
    alice_measurements = []
    bob_measurements = []
    eve_measurements = []
    
    for i in range(num_qubits):
        bell_pair = create_bell_pair()
        
        # Eve measures qubit 0 FIRST → collapses the pair
        qc = bell_pair.copy()
        qc.add_register(qiskit.ClassicalRegister(3, 'c'))
        
        # Eve measures qubit 0 to position 2
        if eve_bases[i] == 1:
            qc.ry(np.pi / 8, 0)
        elif eve_bases[i] == 2:
            qc.ry(np.pi / 4, 0)
        qc.measure(0, 2)
        
        # Alice measures the NOW-COLLAPSED qubit 0 to position 1
        if alice_bases[i] == 1:
            qc.ry(np.pi / 8, 0)
        elif alice_bases[i] == 2:
            qc.ry(np.pi / 4, 0)
        qc.measure(0, 1)
        
        # Bob measures the NOW-COLLAPSED qubit 1 to position 0
        if bob_bases[i] == 1:
            qc.ry(np.pi / 8, 1)
        elif bob_bases[i] == 2:
            qc.ry(np.pi / 4, 1)
        qc.measure(1, 0)
        
        job = simulator.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts(qc)
        bits = list(counts.keys())[0]
        
        eve_measurements.append(int(bits[2]))
        alice_measurements.append(int(bits[1]))
        bob_measurements.append(int(bits[0]))
        
        if (i + 1) % 125 == 0:
            print(f"  {i+1}/{num_qubits}")
    
    chsh = calculate_chsh(alice_bases, bob_bases, alice_measurements, bob_measurements)

    return {
        'chsh': chsh,
        
        'alice': alice_measurements,
        'bob': bob_measurements,
        'eve': eve_measurements,
        'agreement': sum(1 for a, b in zip(alice_measurements, bob_measurements) if a == b)
    }


def scenario_3_eve_before_bob(num_qubits=2000):
    """Scenario 3: Eve intercepts BETWEEN Alice and Bob measurements"""
    simulator = AerSimulator()
    alice_bases = np.random.randint(3, size=num_qubits)
    bob_bases = np.random.randint(3, size=num_qubits)
    eve_bases = np.random.randint(3, size=num_qubits)
    
    alice_measurements = []
    bob_measurements = []
    eve_measurements = []
    
    for i in range(num_qubits):
        bell_pair = create_bell_pair()
        
        # Alice measures qubit 0 FIRST
        qc = bell_pair.copy()
        qc.add_register(qiskit.ClassicalRegister(3, 'c'))
        
        if alice_bases[i] == 1:
            qc.ry(np.pi / 8, 0)
        elif alice_bases[i] == 2:
            qc.ry(np.pi / 4, 0)
        qc.measure(0, 1)
        
        # Eve measures qubit 1 → collapses it BEFORE Bob
        if eve_bases[i] == 1:
            qc.ry(np.pi / 8, 1)
        elif eve_bases[i] == 2:
            qc.ry(np.pi / 4, 1)
        qc.measure(1, 2)
        
        # Bob measures the NOW-COLLAPSED qubit 1
        if bob_bases[i] == 1:
            qc.ry(np.pi / 8, 1)
        elif bob_bases[i] == 2:
            qc.ry(np.pi / 4, 1)
        qc.measure(1, 0)
        
        job = simulator.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts(qc)
        bits = list(counts.keys())[0]
        
        alice_measurements.append(int(bits[1]))
        eve_measurements.append(int(bits[2]))
        bob_measurements.append(int(bits[0]))
        
        if (i + 1) % 125 == 0:
            print(f"  {i+1}/{num_qubits}")
    
    chsh = calculate_chsh(alice_bases, bob_bases, alice_measurements, bob_measurements)

    return {
        'chsh': chsh,
     
        'alice': alice_measurements,
        'bob': bob_measurements,
        'eve': eve_measurements,
        'agreement': sum(1 for a, b in zip(alice_measurements, bob_measurements) if a == b)
    }

if __name__ == "__main__":
    print("="*75)
    print("E91 QKD - Four Eavesdropping Scenarios")
    print("="*75)
    print()
    
    # SCENARIO 1: No Eve
    print("[SCENARIO 1] NO EAVESDROPPING (Baseline)")
    print("-" * 75)
    result1 = scenario_1_no_eve(num_qubits=2000)
    print(f"CHSH value: {result1['chsh']:.4f} (threshold > 2.0)")
    
    print(f"Alice-Bob agreement: {result1['agreement']}/2000 ({100*result1['agreement']/2000:.1f}%)")
    if result1['chsh'] > 2.0:
        print("✓ ENTANGLEMENT VERIFIED - No Eve detected")
    else:
        print("✗ EVE DETECTED - CHSH shows eavesdropping!")
    print()
    print()
    
    # SCENARIO 2: Eve before Alice
    print("[SCENARIO 2] EVE INTERCEPTS BEFORE ALICE")
    print("-" * 75)
    result2 = scenario_2_eve_before_alice(num_qubits=2000)
    print(f"CHSH value: {result2['chsh']:.4f} (threshold > 2.0)")
  
    print(f"Alice-Bob agreement: {result2['agreement']}/2000 ({100*result2['agreement']/2000:.1f}%)")
    if result2['chsh'] < 2.0 :
        print("✗ EVE DETECTED - CHSH shows eavesdropping!")
    else:
        print("✓ ENTANGLEMENT VERIFIED - No Eve detected")
    print()
    print()
    
    # SCENARIO 3: Eve between Alice and Bob
    print("[SCENARIO 3] EVE INTERCEPTS BETWEEN ALICE AND BOB")
    print("-" * 75)
    result3 = scenario_3_eve_before_bob(num_qubits=2000)
    print(f"CHSH value: {result3['chsh']:.4f} (threshold > 2.0)")
   
    print(f"Alice-Bob agreement: {result3['agreement']}/2000 ({100*result3['agreement']/2000:.1f}%)")
    if result3['chsh'] < 2.0 :
        print("✗ EVE DETECTED - CHSH shows eavesdropping!")
    else: 
        print("✓ ENTANGLEMENT VERIFIED - No Eve detected")
    print()
    print()
    
    # Summary
    print("="*75)
    print("SUMMARY - CHSH Comparison")
    print("="*75)
    print(f"{'Scenario':<25} {'CHSH':<15}")
    print("-" * 75)
    print(f"{'No Eve':<25} {result1['chsh']:<15.4f} %")
    print(f"{'Eve→Alice':<25} {result2['chsh']:<15.4f} %")
    print(f"{'Eve between Alice-Bob':<25} {result3['chsh']:<15.4f} %")
    print()
    print("Thresholds:")
    print("  CHSH > 2.0 = Entanglement OK (no Eve)")
    
    print("="*75)

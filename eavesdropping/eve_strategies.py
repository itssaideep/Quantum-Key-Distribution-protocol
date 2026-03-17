"""
Eve Eavesdropping Strategies for QKD Protocols

This module provides different eavesdropping attack implementations:
- Intercept-resend attacks (Eve measures and resends)
- Position-based attacks (Eve attacks at different protocol stages)
- Measurement strategy variations
"""

from protocols.bb84 import run_bb84_protocol, calculate_qber
from protocols.e91 import (
    scenario_1_no_eve, 
    scenario_2_eve_before_alice, 
    scenario_3_eve_before_bob
)


class EVEAttackBB84:
    """Eavesdropping attacks on BB84 protocol"""
    
    @staticmethod
    def intercept_resend(num_qubits=1000):
        """
        Classic intercept-resend attack on BB84
        Eve randomly chooses bases and measures qubits, then resends
        This increases QBER when detected
        
        Args:
            num_qubits: Number of qubits to test
            
        Returns:
            dict: Contains qber_value, success_rate, detection_prob
        """
        sifted_key, alice_bits, bob_results, alice_bases, bob_bases, \
            eve_results, eve_bases, matching_indices = run_bb84_protocol(None, None, True)
        
        qber_eve = calculate_qber(alice_bits, bob_results, matching_indices)
        
        return {
            'name': 'Intercept-Resend Attack (BB84)',
            'qber': qber_eve,
            'detected': qber_eve > 11.0,
            'eve_information': len(eve_results) / num_qubits,  # Fraction of bits Eve got
            'attack_success': qber_eve < 11.0  # Eve undetected
        }


class EVEAttackE91:
    """Eavesdropping attacks on E91 protocol using Bell pair disruption"""
    
    @staticmethod
    def scenario_1_baseline():
        """
        Baseline: No eavesdropping (for comparison)
        
        Returns:
            dict: Clean CHSH value, agreement rate
        """
        result = scenario_1_no_eve(num_qubits=1000)
        return {
            'name': 'E91 Baseline (No Eve)',
            'chsh': result['chsh'],
            'agreement': result.get('agreement', 0),
            'detected': False,
            'status': '[OK] SECURE'
        }
    
    @staticmethod
    def early_intercept():
        """
        Early Interception: Eve measures before Alice
        Most destructive - Eve collapses the Bell pair immediately
        
        Returns:
            dict: Degraded CHSH value, detection status
        """
        result = scenario_2_eve_before_alice(num_qubits=1000)
        return {
            'name': 'E91 Early Intercept (Eve→Alice)',
            'chsh': result['chsh'],
            'agreement': result.get('agreement', 0),
            'detected': result['chsh'] < 2.0,
            'status': '[X] DETECTED' if result['chsh'] < 2.0 else '[?] MARGINAL'
        }
    
    @staticmethod
    def mid_intercept():
        """
        Mid-Protocol Interception: Eve measures between Alice and Bob
        Less destructive but still detectable through CHSH degradation
        
        Returns:
            dict: Moderately degraded CHSH value, detection status
        """
        result = scenario_3_eve_before_bob(num_qubits=1000)
        return {
            'name': 'E91 Mid-Protocol Intercept (Eve→Bob)',
            'chsh': result['chsh'],
            'agreement': result.get('agreement', 0),
            'detected': result['chsh'] < 2.0,
            'status': '[X] DETECTED' if result['chsh'] < 2.0 else '[?] MARGINAL'
        }


class EVEComparison:
    """Unified comparison of Eve attacks across both protocols"""
    
    @staticmethod
    def run_all_bb84_attacks(num_runs=3):
        """
        Run BB84 against Eve multiple times for statistical analysis
        
        Args:
            num_runs: Number of attack runs
            
        Returns:
            dict: Statistics on detection success
        """
        results = []
        detected_count = 0
        qber_values = []
        
        for run in range(num_runs):
            attack = EVEAttackBB84.intercept_resend()
            results.append(attack)
            if attack['detected']:
                detected_count += 1
            qber_values.append(attack['qber'])
        
        import numpy as np
        return {
            'protocol': 'BB84',
            'attack_type': 'Intercept-Resend',
            'num_runs': num_runs,
            'detection_rate': detected_count / num_runs * 100,
            'avg_qber': np.mean(qber_values),
            'std_qber': np.std(qber_values),
            'detailed_results': results
        }
    
    @staticmethod
    def run_all_e91_attacks(num_runs=3):
        """
        Run E91 against all three Eve scenarios multiple times
        
        Args:
            num_runs: Number of attack runs per scenario
            
        Returns:
            dict: Statistics on three different attack positions
        """
        import numpy as np
        
        scenarios = [
            EVEAttackE91.scenario_1_baseline,
            EVEAttackE91.early_intercept,
            EVEAttackE91.mid_intercept
        ]
        
        results_by_scenario = {}
        
        for scenario_func in scenarios:
            scenario_name = scenario_func.__name__
            chsh_values = []
            detected_count = 0
            
            for run in range(num_runs):
                result = scenario_func()
                chsh_values.append(result['chsh'])
                if result['detected']:
                    detected_count += 1
            
            results_by_scenario[scenario_name] = {
                'avg_chsh': np.mean(chsh_values),
                'std_chsh': np.std(chsh_values),
                'detection_rate': detected_count / num_runs * 100,
                'is_attack': scenario_name != 'scenario_1_baseline'
            }
        
        return {
            'protocol': 'E91',
            'attack_types': ['No Eve', 'Early Intercept', 'Mid-Protocol'],
            'num_runs': num_runs,
            'scenarios': results_by_scenario
        }


if __name__ == "__main__":
    print("="*75)
    print("Eve Eavesdropping Strategy Tests")
    print("="*75)
    
    print("\n[BB84] Intercept-Resend Attack:")
    bb84_attack = EVEAttackBB84.intercept_resend()
    print(f"  QBER: {bb84_attack['qber']:.2f}%")
    print(f"  Detected: {bb84_attack['detected']}")
    print(f"  Eve's Information Gain: {bb84_attack['eve_information']:.2f}")
    
    print("\n[E91] Baseline (No Eve):")
    e91_baseline = EVEAttackE91.scenario_1_baseline()
    print(f"  CHSH: {e91_baseline['chsh']:.4f}")
    print(f"  Status: {e91_baseline['status']}")
    
    print("\n[E91] Early Intercept Attack:")
    e91_early = EVEAttackE91.early_intercept()
    print(f"  CHSH: {e91_early['chsh']:.4f}")
    print(f"  Status: {e91_early['status']}")
    
    print("\n[E91] Mid-Protocol Intercept Attack:")
    e91_mid = EVEAttackE91.mid_intercept()
    print(f"  CHSH: {e91_mid['chsh']:.4f}")
    print(f"  Status: {e91_mid['status']}")
    
    print("\n" + "="*75)
    print("Comparative Attack Analysis (3 runs each)")
    print("="*75)
    
    bb84_comp = EVEComparison.run_all_bb84_attacks(num_runs=3)
    print(f"\n[BB84] Detection Rate: {bb84_comp['detection_rate']:.1f}%")
    print(f"Avg QBER: {bb84_comp['avg_qber']:.2f}% +/- {bb84_comp['std_qber']:.2f}%")
    
    e91_comp = EVEComparison.run_all_e91_attacks(num_runs=3)
    print(f"\n[E91] Results across scenarios:")
    for scenario, stats in e91_comp['scenarios'].items():
        print(f"  {scenario}:")
        print(f"    Avg CHSH: {stats['avg_chsh']:.4f} +/- {stats['std_chsh']:.4f}")
        print(f"    Detection Rate: {stats['detection_rate']:.1f}%")

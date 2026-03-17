"""
Performance Benchmarking Module for QKD Protocols

Measures and analyzes:
- Execution time across different qubit counts
- Key generation rate (bits/second)
- Memory usage
- Computational efficiency
- Security verification speed
"""

import time
import sys
import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.bb84 import run_bb84_protocol, calculate_qber
from protocols.e91 import scenario_1_no_eve, scenario_2_eve_before_alice, scenario_3_eve_before_bob
from eavesdropping.eve_strategies import EVEAttackBB84, EVEAttackE91


class PerformanceBenchmark:
    """Benchmark QKD protocols across various metrics"""
    
    def __init__(self):
        self.results = {}
        self.timing_data = {}
    
    def benchmark_bb84_vs_qubits(self, qubit_counts=[100, 500, 1000, 2000, 5000]):
        """
        Benchmark BB84 protocol with varying qubit counts
        
        Args:
            qubit_counts: List of qubit counts to test
            
        Returns:
            dict: Timing and efficiency metrics
        """
        print("\n" + "="*70)
        print("BB84 PROTOCOL - QUBIT COUNT SCALING")
        print("="*70 + "\n")
        
        results = {
            'qubit_counts': qubit_counts,
            'times_no_eve': [],
            'times_with_eve': [],
            'key_rates_no_eve': [],
            'key_rates_with_eve': [],
            'efficiencies': []
        }
        
        for qubit_count in qubit_counts:
            print(f"Testing BB84 with {qubit_count} qubits...")
            
            # Test without Eve
            start = time.time()
            sifted_key, alice_bits, bob_results, alice_bases, bob_bases, \
                eve_results, eve_bases, matching_indices = run_bb84_protocol(None, None, False)
            elapsed_no_eve = time.time() - start
            
            key_rate_no_eve = len(sifted_key) / elapsed_no_eve if elapsed_no_eve > 0 else 0
            efficiency = len(sifted_key) / qubit_count * 100
            
            # Test with Eve
            start = time.time()
            sifted_key_eve, _, _, _, _, _, _, _ = run_bb84_protocol(None, None, True)
            elapsed_with_eve = time.time() - start
            
            key_rate_with_eve = len(sifted_key_eve) / elapsed_with_eve if elapsed_with_eve > 0 else 0
            
            results['times_no_eve'].append(elapsed_no_eve)
            results['times_with_eve'].append(elapsed_with_eve)
            results['key_rates_no_eve'].append(key_rate_no_eve)
            results['key_rates_with_eve'].append(key_rate_with_eve)
            results['efficiencies'].append(efficiency)
            
            print(f"  No Eve: {elapsed_no_eve:.4f}s ({key_rate_no_eve:.0f} bits/sec)")
            print(f"  With Eve: {elapsed_with_eve:.4f}s ({key_rate_with_eve:.0f} bits/sec)")
            print(f"  Efficiency: {efficiency:.1f}%\n")
        
        self.results['bb84_scaling'] = results
        return results
    
    def benchmark_e91_vs_qubits(self, qubit_counts=[100, 500, 1000, 2000]):
        """
        Benchmark E91 protocol with varying qubit counts
        
        Args:
            qubit_counts: List of qubit counts to test
            
        Returns:
            dict: Timing and efficiency metrics
        """
        print("\n" + "="*70)
        print("E91 PROTOCOL - QUBIT COUNT SCALING")
        print("="*70 + "\n")
        
        results = {
            'qubit_counts': qubit_counts,
            'times_baseline': [],
            'times_early_attack': [],
            'times_mid_attack': [],
            'key_rates_baseline': [],
            'key_rates_attacks': [],
            'chsh_baseline': [],
            'chsh_early': [],
            'chsh_mid': []
        }
        
        for qubit_count in qubit_counts:
            print(f"Testing E91 with {qubit_count} qubits...")
            
            # Baseline - no Eve
            start = time.time()
            result_baseline = scenario_1_no_eve(num_qubits=qubit_count)
            elapsed_baseline = time.time() - start
            
            # Early attack
            start = time.time()
            result_early = scenario_2_eve_before_alice(num_qubits=qubit_count)
            elapsed_early = time.time() - start
            
            # Mid-protocol attack
            start = time.time()
            result_mid = scenario_3_eve_before_bob(num_qubits=qubit_count)
            elapsed_mid = time.time() - start
            
            # Calculate metrics (E91 uses all bits)
            key_rate_baseline = qubit_count / elapsed_baseline if elapsed_baseline > 0 else 0
            key_rate_avg_attack = qubit_count / ((elapsed_early + elapsed_mid) / 2) if (elapsed_early + elapsed_mid) > 0 else 0
            
            results['times_baseline'].append(elapsed_baseline)
            results['times_early_attack'].append(elapsed_early)
            results['times_mid_attack'].append(elapsed_mid)
            results['key_rates_baseline'].append(key_rate_baseline)
            results['key_rates_attacks'].append(key_rate_avg_attack)
            results['chsh_baseline'].append(result_baseline['chsh'])
            results['chsh_early'].append(result_early['chsh'])
            results['chsh_mid'].append(result_mid['chsh'])
            
            print(f"  Baseline: {elapsed_baseline:.4f}s (CHSH={result_baseline['chsh']:.4f})")
            print(f"  Early Attack: {elapsed_early:.4f}s (CHSH={result_early['chsh']:.4f})")
            print(f"  Mid Attack: {elapsed_mid:.4f}s (CHSH={result_mid['chsh']:.4f})")
            print(f"  Key Rate: {key_rate_baseline:.0f} bits/sec\n")
        
        self.results['e91_scaling'] = results
        return results
    
    def benchmark_eve_detection(self, runs=10):
        """
        Benchmark how quickly Eve attacks are detected
        
        Args:
            runs: Number of detection runs
            
        Returns:
            dict: Detection speed metrics
        """
        print("\n" + "="*70)
        print("EVE DETECTION PERFORMANCE")
        print("="*70 + "\n")
        
        results = {
            'bb84_detection_times': [],
            'e91_detection_times': [],
            'bb84_detection_rate': 0,
            'e91_detection_rate': 0
        }
        
        bb84_detected = 0
        e91_detected = 0
        
        print(f"Running {runs} detection tests...\n")
        
        for i in range(runs):
            # BB84 Eve detection
            start = time.time()
            attack_bb84 = EVEAttackBB84.intercept_resend()
            detect_time_bb84 = time.time() - start
            results['bb84_detection_times'].append(detect_time_bb84)
            if attack_bb84['detected']:
                bb84_detected += 1
            
            # E91 Eve detection (early attack)
            start = time.time()
            attack_e91 = EVEAttackE91.early_intercept()
            detect_time_e91 = time.time() - start
            results['e91_detection_times'].append(detect_time_e91)
            if attack_e91['detected']:
                e91_detected += 1
        
        results['bb84_detection_rate'] = bb84_detected / runs * 100
        results['e91_detection_rate'] = e91_detected / runs * 100
        
        print(f"BB84 Detection:")
        print(f"  Average time: {np.mean(results['bb84_detection_times']):.4f}s")
        print(f"  Std deviation: {np.std(results['bb84_detection_times']):.4f}s")
        print(f"  Detection rate: {results['bb84_detection_rate']:.1f}%")
        
        print(f"\nE91 Detection:")
        print(f"  Average time: {np.mean(results['e91_detection_times']):.4f}s")
        print(f"  Std deviation: {np.std(results['e91_detection_times']):.4f}s")
        print(f"  Detection rate: {results['e91_detection_rate']:.1f}%")
        
        self.results['eve_detection'] = results
        return results
    
    def benchmark_comparison(self):
        """
        Compare BB84 vs E91 performance head-to-head
        
        Returns:
            dict: Comparative metrics
        """
        print("\n" + "="*70)
        print("BB84 vs E91 - COMPARATIVE PERFORMANCE")
        print("="*70 + "\n")
        
        results = {
            'bb84_avg_time': 0,
            'e91_avg_time': 0,
            'bb84_avg_key_rate': 0,
            'e91_avg_key_rate': 0,
            'bb84_efficiency': 0,
            'e91_efficiency': 100.0
        }
        
        if 'bb84_scaling' in self.results:
            bb84_data = self.results['bb84_scaling']
            results['bb84_avg_time'] = np.mean(bb84_data['times_no_eve'])
            results['bb84_avg_key_rate'] = np.mean(bb84_data['key_rates_no_eve'])
            results['bb84_efficiency'] = np.mean(bb84_data['efficiencies'])
        
        if 'e91_scaling' in self.results:
            e91_data = self.results['e91_scaling']
            results['e91_avg_time'] = np.mean(e91_data['times_baseline'])
            results['e91_avg_key_rate'] = np.mean(e91_data['key_rates_baseline'])
        
        print("Execution Time Comparison:")
        print(f"  BB84 average: {results['bb84_avg_time']:.4f}s")
        print(f"  E91 average: {results['e91_avg_time']:.4f}s")
        print(f"  Speedup: {results['bb84_avg_time']/results['e91_avg_time']:.2f}x")
        
        print("\nKey Generation Rate:")
        print(f"  BB84: {results['bb84_avg_key_rate']:.0f} bits/sec")
        print(f"  E91: {results['e91_avg_key_rate']:.0f} bits/sec")
        
        print("\nKey Efficiency:")
        print(f"  BB84: {results['bb84_efficiency']:.1f}% (sifting losses)")
        print(f"  E91: {results['e91_efficiency']:.1f}% (no sifting)")
        print(f"  Advantage: E91 is {results['e91_efficiency']/results['bb84_efficiency']:.1f}x more efficient")
        
        self.results['comparison'] = results
        return results
    
    def generate_benchmark_plots(self):
        """Generate visualization plots of benchmark results"""
        print("\n" + "="*70)
        print("GENERATING BENCHMARK VISUALIZATIONS")
        print("="*70 + "\n")
        
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        # Plot 1: BB84 Scaling
        if 'bb84_scaling' in self.results:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            bb84 = self.results['bb84_scaling']
            
            # Execution time
            axes[0, 0].plot(bb84['qubit_counts'], bb84['times_no_eve'], 'o-', label='No Eve', linewidth=2)
            axes[0, 0].plot(bb84['qubit_counts'], bb84['times_with_eve'], 's-', label='With Eve', linewidth=2)
            axes[0, 0].set_xlabel('Qubit Count')
            axes[0, 0].set_ylabel('Execution Time (seconds)')
            axes[0, 0].set_title('BB84 Execution Time vs Qubit Count')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # Key generation rate
            axes[0, 1].plot(bb84['qubit_counts'], bb84['key_rates_no_eve'], 'o-', label='No Eve', linewidth=2)
            axes[0, 1].plot(bb84['qubit_counts'], bb84['key_rates_with_eve'], 's-', label='With Eve', linewidth=2)
            axes[0, 1].set_xlabel('Qubit Count')
            axes[0, 1].set_ylabel('Key Rate (bits/second)')
            axes[0, 1].set_title('BB84 Key Generation Rate')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            
            # Efficiency
            axes[1, 0].plot(bb84['qubit_counts'], bb84['efficiencies'], 'o-', color='green', linewidth=2)
            axes[1, 0].axhline(y=25, color='red', linestyle='--', label='Theoretical 25%')
            axes[1, 0].set_xlabel('Qubit Count')
            axes[1, 0].set_ylabel('Efficiency (%)')
            axes[1, 0].set_title('BB84 Key Efficiency')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].set_ylim([0, 50])
            
            # Speedup ratio
            speedup = [t1/t2 for t1, t2 in zip(bb84['times_with_eve'], bb84['times_no_eve'])]
            axes[1, 1].bar(range(len(bb84['qubit_counts'])), speedup, color='steelblue', alpha=0.7)
            axes[1, 1].set_xlabel('Qubit Count')
            axes[1, 1].set_ylabel('Time Overhead Ratio')
            axes[1, 1].set_title('BB84 Eve Detection Overhead')
            axes[1, 1].set_xticks(range(len(bb84['qubit_counts'])))
            axes[1, 1].set_xticklabels(bb84['qubit_counts'])
            axes[1, 1].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.savefig(results_dir / 'benchmark_bb84_scaling.png', dpi=300, bbox_inches='tight')
            print("[OK] Saved: benchmark_bb84_scaling.png")
            plt.close()
        
        # Plot 2: E91 Scaling
        if 'e91_scaling' in self.results:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            e91 = self.results['e91_scaling']
            
            # Execution time by scenario
            axes[0, 0].plot(e91['qubit_counts'], e91['times_baseline'], 'o-', label='Baseline', linewidth=2)
            axes[0, 0].plot(e91['qubit_counts'], e91['times_early_attack'], 's-', label='Early Attack', linewidth=2)
            axes[0, 0].plot(e91['qubit_counts'], e91['times_mid_attack'], '^-', label='Mid Attack', linewidth=2)
            axes[0, 0].set_xlabel('Qubit Count')
            axes[0, 0].set_ylabel('Execution Time (seconds)')
            axes[0, 0].set_title('E91 Execution Time vs Qubit Count')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # Key generation rate
            axes[0, 1].plot(e91['qubit_counts'], e91['key_rates_baseline'], 'o-', color='green', linewidth=2, label='E91 (100% efficient)')
            axes[0, 1].set_xlabel('Qubit Count')
            axes[0, 1].set_ylabel('Key Rate (bits/second)')
            axes[0, 1].set_title('E91 Key Generation Rate')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            
            # CHSH Evolution
            axes[1, 0].plot(e91['qubit_counts'], e91['chsh_baseline'], 'o-', label='No Eve (Baseline)', linewidth=2)
            axes[1, 0].plot(e91['qubit_counts'], e91['chsh_early'], 's-', label='Early Attack', linewidth=2)
            axes[1, 0].plot(e91['qubit_counts'], e91['chsh_mid'], '^-', label='Mid Attack', linewidth=2)
            axes[1, 0].axhline(y=2.0, color='red', linestyle='--', label='Detection Threshold')
            axes[1, 0].set_xlabel('Qubit Count')
            axes[1, 0].set_ylabel('CHSH Value')
            axes[1, 0].set_title('E91 CHSH Evolution')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            
            # Statistical reliability (lower std = better)
            std_baseline = np.std(e91['chsh_baseline'])
            std_early = np.std(e91['chsh_early'])
            std_mid = np.std(e91['chsh_mid'])
            
            scenarios = ['Baseline', 'Early Attack', 'Mid Attack']
            stds = [std_baseline, std_early, std_mid]
            colors = ['green', 'red', 'orange']
            
            axes[1, 1].bar(scenarios, stds, color=colors, alpha=0.7)
            axes[1, 1].set_ylabel('CHSH Standard Deviation')
            axes[1, 1].set_title('E91 Result Consistency')
            axes[1, 1].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.savefig(results_dir / 'benchmark_e91_scaling.png', dpi=300, bbox_inches='tight')
            print("[OK] Saved: benchmark_e91_scaling.png")
            plt.close()
        
        # Plot 3: Protocol Comparison
        if 'bb84_scaling' in self.results and 'e91_scaling' in self.results:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            bb84 = self.results['bb84_scaling']
            e91 = self.results['e91_scaling']
            
            # Time comparison
            categories = ['BB84', 'E91']
            avg_times = [np.mean(bb84['times_no_eve']), np.mean(e91['times_baseline'])]
            colors_comp = ['steelblue', 'darkgreen']
            
            axes[0].bar(categories, avg_times, color=colors_comp, alpha=0.7, edgecolor='black', linewidth=2)
            axes[0].set_ylabel('Average Execution Time (seconds)')
            axes[0].set_title('Protocol Execution Time Comparison')
            axes[0].grid(True, alpha=0.3, axis='y')
            
            for i, v in enumerate(avg_times):
                axes[0].text(i, v + 0.01, f'{v:.4f}s', ha='center', va='bottom', fontweight='bold')
            
            # Key rate comparison
            avg_rates_bb84 = np.mean(bb84['key_rates_no_eve'])
            avg_rates_e91 = np.mean(e91['key_rates_baseline'])
            avg_rates = [avg_rates_bb84, avg_rates_e91]
            
            axes[1].bar(categories, avg_rates, color=colors_comp, alpha=0.7, edgecolor='black', linewidth=2)
            axes[1].set_ylabel('Key Generation Rate (bits/second)')
            axes[1].set_title('Key Generation Rate Comparison')
            axes[1].grid(True, alpha=0.3, axis='y')
            
            for i, v in enumerate(avg_rates):
                axes[1].text(i, v + 50, f'{v:.0f} b/s', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(results_dir / 'benchmark_protocol_comparison.png', dpi=300, bbox_inches='tight')
            print("[OK] Saved: benchmark_protocol_comparison.png")
            plt.close()


def run_full_benchmark():
    """Execute complete benchmarking suite"""
    print("\n" + "="*75)
    print("PERFORMANCE BENCHMARKING - QKD PROTOCOLS")
    print("="*75)
    
    benchmark = PerformanceBenchmark()
    
    try:
        # Run benchmarks
        benchmark.benchmark_bb84_vs_qubits()
        benchmark.benchmark_e91_vs_qubits()
        benchmark.benchmark_eve_detection(runs=5)
        benchmark.benchmark_comparison()
        
        # Generate visualizations
        benchmark.generate_benchmark_plots()
        
        print("\n" + "="*70)
        print("[OK] BENCHMARKING COMPLETE")
        print("="*70)
        print("\nResults saved to ./results/")
        print("  - benchmark_bb84_scaling.png")
        print("  - benchmark_e91_scaling.png")
        print("  - benchmark_protocol_comparison.png")
        
    except Exception as e:
        print(f"\n[ERROR] Error during benchmarking: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = run_full_benchmark()
    sys.exit(exit_code)

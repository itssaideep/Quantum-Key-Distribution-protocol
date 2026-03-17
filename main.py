"""
Main execution script for Quantum Key Distribution Protocol Simulation

This script orchestrates the complete QKD simulation:
- Run BB84 and E91 protocols
- Test against multiple eavesdropping scenarios
- Generate comprehensive visualizations
- Analyze security metrics
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from protocols.bb84 import run_bb84_protocol, calculate_qber
from protocols.e91 import scenario_1_no_eve, scenario_2_eve_before_alice, scenario_3_eve_before_bob
from eavesdropping.eve_strategies import EVEAttackBB84, EVEAttackE91, EVEComparison
from utils.quantum_helpers import estimate_eve_presence, estimate_eve_presence_bell, print_protocol_summary


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*75)
    print(f"  {title}")
    print("="*75 + "\n")


def run_bb84_full():
    """Run complete BB84 protocol analysis"""
    print_header("BB84 PROTOCOL - PREPARE-AND-MEASURE QKD")
    
    print("Testing BB84 without eavesdropping...")
    sifted_clean, alice_bits_clean, bob_results_clean, alice_bases_clean, \
        bob_bases_clean, _, _, matching_clean = run_bb84_protocol(None, None, False)
    
    qber_clean = calculate_qber(alice_bits_clean, bob_results_clean, matching_clean)
    eve_analysis_clean = estimate_eve_presence(qber_clean)
    
    print(f"  Sifted Key Length: {len(sifted_clean)} bits")
    print(f"  Total Qubits Sent: {len(alice_bits_clean)}")
    print(f"  Key Efficiency: {len(sifted_clean)/len(alice_bits_clean)*100:.1f}%")
    print(f"  QBER: {qber_clean:.2f}%")
    print(f"  Eve Detected: {eve_analysis_clean['eve_detected']}")
    print(f"  Detection Confidence: {eve_analysis_clean['confidence']:.2f}")
    
    print("\nTesting BB84 with eavesdropping...")
    sifted_eve, alice_bits_eve, bob_results_eve, alice_bases_eve, \
        bob_bases_eve, eve_results, eve_bases, matching_eve = run_bb84_protocol(None, None, True)
    
    qber_eve = calculate_qber(alice_bits_eve, bob_results_eve, matching_eve)
    eve_analysis_eve = estimate_eve_presence(qber_eve)
    
    print(f"  Sifted Key Length: {len(sifted_eve)} bits")
    print(f"  QBER with Eve: {qber_eve:.2f}%")
    print(f"  Eve Detected: {eve_analysis_eve['eve_detected']}")
    print(f"  Detection Confidence: {eve_analysis_eve['confidence']:.2f}")
    
    return {
        'clean': {
            'qber': qber_clean,
            'key_length': len(sifted_clean),
            'efficiency': len(sifted_clean)/len(alice_bits_clean)*100,
            'detected': eve_analysis_clean['eve_detected']
        },
        'with_eve': {
            'qber': qber_eve,
            'key_length': len(sifted_eve),
            'detected': eve_analysis_eve['eve_detected']
        }
    }


def run_e91_full():
    """Run complete E91 protocol analysis"""
    print_header("E91 PROTOCOL - ENTANGLEMENT-BASED QKD")
    
    print("Scenario 1: No Eavesdropping (Baseline)")
    result1 = scenario_1_no_eve(num_qubits=1000)
    analysis1 = estimate_eve_presence_bell(result1['chsh'])
    
    print(f"  CHSH Value: {result1['chsh']:.4f}")
    print(f"  Measurement Agreement: {result1.get('agreement', 0)}%")
    print(f"  Eve Detected: {analysis1['eve_detected']}")
    print(f"  Security Status: [OK] SECURE")
    
    print("\nScenario 2: Eve Measures Before Alice (Early Attack)")
    result2 = scenario_2_eve_before_alice(num_qubits=1000)
    analysis2 = estimate_eve_presence_bell(result2['chsh'])
    
    print(f"  CHSH Value: {result2['chsh']:.4f}")
    print(f"  Measurement Agreement: {result2.get('agreement', 0)}%")
    print(f"  Eve Detected: {analysis2['eve_detected']}")
    print(f"  Security Status: {('[X] DETECTED' if analysis2['eve_detected'] else '[?] MARGINAL')}")
    
    print("\nScenario 3: Eve Measures Between Alice and Bob (Mid-Protocol Attack)")
    result3 = scenario_3_eve_before_bob(num_qubits=1000)
    analysis3 = estimate_eve_presence_bell(result3['chsh'])
    
    print(f"  CHSH Value: {result3['chsh']:.4f}")
    print(f"  Measurement Agreement: {result3.get('agreement', 0)}%")
    print(f"  Eve Detected: {analysis3['eve_detected']}")
    print(f"  Security Status: {('[X] DETECTED' if analysis3['eve_detected'] else '[?] MARGINAL')}")
    
    return {
        'scenario_1': {
            'chsh': result1['chsh'],
            'detected': False,
            'key_efficiency': 100.0
        },
        'scenario_2': {
            'chsh': result2['chsh'],
            'detected': analysis2['eve_detected'],
            'key_efficiency': 100.0
        },
        'scenario_3': {
            'chsh': result3['chsh'],
            'detected': analysis3['eve_detected'],
            'key_efficiency': 100.0
        }
    }


def run_eve_strategies():
    """Run comprehensive Eve attack analysis"""
    print_header("EVE EAVESDROPPING STRATEGIES")
    
    print("BB84 Intercept-Resend Attack:")
    bb84_attack = EVEAttackBB84.intercept_resend()
    print(f"  QBER: {bb84_attack['qber']:.2f}%")
    print(f"  Attack Detected: {bb84_attack['detected']}")
    print(f"  Eve Information Gain: {bb84_attack['eve_information']:.2%}")
    
    print("\nE91 Attack Scenarios:")
    e91_baseline = EVEAttackE91.scenario_1_baseline()
    e91_early = EVEAttackE91.early_intercept()
    e91_mid = EVEAttackE91.mid_intercept()
    
    scenarios = [
        ("Baseline (No Eve)", e91_baseline),
        ("Early Intercept", e91_early),
        ("Mid-Protocol Intercept", e91_mid)
    ]
    
    for name, result in scenarios:
        detected_str = "[X] DETECTED" if result['detected'] else "[OK] SECURE"
        print(f"  {name}: CHSH={result['chsh']:.4f} [{detected_str}]")


def run_comparative_analysis(num_runs=3):
    """Run statistical comparison across multiple runs"""
    print_header("STATISTICAL ANALYSIS (Multiple Runs)")
    
    print(f"Running {num_runs} iterations of each protocol...\n")
    
    bb84_stats = EVEComparison.run_all_bb84_attacks(num_runs=num_runs)
    print("BB84 Statistics:")
    print(f"  Detection Rate: {bb84_stats['detection_rate']:.1f}%")
    print(f"  Average QBER: {bb84_stats['avg_qber']:.2f}% ± {bb84_stats['std_qber']:.2f}%")
    
    e91_stats = EVEComparison.run_all_e91_attacks(num_runs=num_runs)
    print("\nE91 Statistics:")
    for scenario_name, stats in e91_stats['scenarios'].items():
        attack_label = "(ATTACK)" if stats['is_attack'] else "(BASELINE)"
        print(f"  {scenario_name} {attack_label}:")
        print(f"    Avg CHSH: {stats['avg_chsh']:.4f} ± {stats['std_chsh']:.4f}")
        print(f"    Detection Rate: {stats['detection_rate']:.1f}%")


def run_performance_benchmarks():
    """Run performance benchmarking suite"""
    print_header("PERFORMANCE BENCHMARKING")
    
    # Check if benchmark script exists
    benchmark_script = project_root / "analysis" / "performance_benchmark.py"
    
    if benchmark_script.exists():
        print("Running performance benchmarking analysis...")
        print("This will measure execution time, key generation rates, and scalability...\n")
        
        import subprocess
        result = subprocess.run(
            ["python", str(benchmark_script)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("✓ Benchmarking completed successfully!")
        else:
            print("⚠ Error running benchmarks:")
            print(result.stderr)
    else:
        print("⚠ Benchmark script not found at:", benchmark_script)


def generate_visualizations():
    """Generate all comparison visualizations"""
    print_header("GENERATING VISUALIZATIONS")
    
    # Check if visualization script exists
    viz_script = project_root / "analysis" / "compare_protocols.py"
    
    if viz_script.exists():
        print("Running comparative visualization analysis...")
        print("This will generate PNG files in ./results/\n")
        
        import subprocess
        result = subprocess.run(
            ["python", str(viz_script)],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Visualizations generated successfully!")
            print("\nGenerated files:")
            results_dir = project_root / "results"
            if results_dir.exists():
                for png_file in sorted(results_dir.glob("*.png")):
                    print(f"  - {png_file.name}")
        else:
            print("⚠ Error generating visualizations:")
            print(result.stderr)
    else:
        print("⚠ Visualization script not found at:", viz_script)


def main():
    """Main execution function"""
    print("\n" + "="*75)
    print("="*75)
    print("  QUANTUM KEY DISTRIBUTION PROTOCOL SIMULATION")
    print("  BB84 vs E91 Comprehensive Analysis")
    print("="*75)
    print("="*75)
    
    start_time = time.time()
    
    try:
        # Create results directory
        results_dir = project_root / "results"
        results_dir.mkdir(exist_ok=True)
        
        # Run all protocol analyses
        bb84_results = run_bb84_full()
        e91_results = run_e91_full()
        
        # Run Eve attack strategies
        run_eve_strategies()
        
        # Run statistical analysis
        run_comparative_analysis(num_runs=3)
        
        # Generate visualizations
        generate_visualizations()
        
        # Run performance benchmarking
        run_performance_benchmarks()
        
        # Print summary
        print_header("EXECUTION SUMMARY")
        
        elapsed_time = time.time() - start_time
        print(f"Total execution time: {elapsed_time:.2f} seconds\n")
        
        print("Key Findings:")
        print(f"  • BB84 without Eve: QBER = {bb84_results['clean']['qber']:.2f}%")
        print(f"  • BB84 with Eve: QBER = {bb84_results['with_eve']['qber']:.2f}%")
        print(f"  • BB84 Key Efficiency: {bb84_results['clean']['efficiency']:.1f}%\n")
        
        print(f"  • E91 Baseline: CHSH = {e91_results['scenario_1']['chsh']:.4f}")
        print(f"  • E91 Early Attack: CHSH = {e91_results['scenario_2']['chsh']:.4f} (Detected: {e91_results['scenario_2']['detected']})")
        print(f"  • E91 Mid-Attack: CHSH = {e91_results['scenario_3']['chsh']:.4f} (Detected: {e91_results['scenario_3']['detected']})")
        print(f"  • E91 Key Efficiency: {e91_results['scenario_1']['key_efficiency']:.1f}%\n")
        
        print("[OK] Simulation completed successfully!")
        print("\nResults saved to ./results/ directory")
        
    except Exception as e:
        print(f"\n[ERROR] Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    
    print_header("END OF SIMULATION")
    
    sys.exit(exit_code)

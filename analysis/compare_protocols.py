"""
Compare BB84 and E91 Quantum Key Distribution Protocols

Visualizes:
- Security metrics (QBER vs CHSH)
- Key generation efficiency
- Eavesdropping detection comparison
- Practical advantages
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from protocols.bb84 import run_bb84_protocol, calculate_qber
from protocols.e91 import scenario_1_no_eve, scenario_2_eve_before_alice, scenario_3_eve_before_bob


def plot_security_metrics():
    """Compare QBER (BB84) vs CHSH (E91) detection"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    print("Running BB84...")
    sifted_key_no_eve, alice_bits_no_eve, bob_results_no_eve, alice_bases_no_eve, bob_bases_no_eve, _, _, matching_no_eve = run_bb84_protocol(None, None, False)
    qber_no_eve = calculate_qber(alice_bits_no_eve, bob_results_no_eve, matching_no_eve)
    
    sifted_key_with_eve, alice_bits_with_eve, bob_results_with_eve, alice_bases_with_eve, bob_bases_with_eve, _, _, matching_with_eve = run_bb84_protocol(None, None, True)
    qber_with_eve = calculate_qber(alice_bits_with_eve, bob_results_with_eve, matching_with_eve)
    
    print("Running E91...")
    e91_no_eve = scenario_1_no_eve(num_qubits=500)
    e91_with_eve_2 = scenario_2_eve_before_alice(num_qubits=500)
    
    # Plot 1: QBER Comparison
    ax = axes[0]
    protocols = ['BB84\nNo Eve', 'BB84\nWith Eve']
    qber_values = [qber_no_eve, qber_with_eve]
    colors = ['green', 'red']
    
    bars = ax.bar(protocols, qber_values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=11, color='orange', linestyle='--', linewidth=2, label='Detection Threshold (11%)')
    ax.set_ylabel('QBER (%)', fontsize=12, fontweight='bold')
    ax.set_title('BB84: Quantum Bit Error Rate', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 30)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, qber_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: CHSH Comparison
    ax = axes[1]
    protocols = ['E91\nNo Eve', 'E91\nWith Eve']
    chsh_values = [e91_no_eve['chsh'], e91_with_eve_2['chsh']]
    colors = ['green', 'red']
    
    bars = ax.bar(protocols, chsh_values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=2.0, color='orange', linestyle='--', linewidth=2, label='Detection Threshold (2.0)')
    ax.axhline(y=2.828, color='blue', linestyle=':', linewidth=2, label='Tsirelson Bound (2.828)')
    ax.set_ylabel('CHSH Value', fontsize=12, fontweight='bold')
    ax.set_title('E91: Bell Inequality Violation', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 3.0)
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, chsh_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../results/security_metrics_comparison.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: security_metrics_comparison.png")
    plt.close()


def plot_key_efficiency():
    """Compare key generation efficiency"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    print("\nCalculating key efficiencies...")
    sifted_key_bb84, _, _, _, _, _, _, _ = run_bb84_protocol(None, None, False)
    e91_no_eve = scenario_1_no_eve(num_qubits=1000)
    
    protocols = ['BB84\n(2 bases)', 'E91\n(3 bases)']
    total_qubits = [1000, 1000]
    sifted_keys = [len(sifted_key_bb84), len(e91_no_eve['alice'])]
    efficiency = [s/t*100 for s, t in zip(sifted_keys, total_qubits)]
    
    x = np.arange(len(protocols))
    width = 0.35
    
    bars = ax.bar(x, efficiency, width, color=['steelblue', 'darkgreen'], 
                   alpha=0.8, edgecolor='black', linewidth=2)
    
    ax.set_ylabel('Key Generation Efficiency (%)', fontsize=12, fontweight='bold')
    ax.set_title('Key Efficiency: BB84 vs E91', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(protocols, fontsize=11)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels and key details
    for i, (bar, eff, key_len) in enumerate(zip(bars, efficiency, sifted_keys)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{eff:.1f}%\n({key_len} bits)', 
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Add annotation
    ax.text(0.5, 85, 'BB84: 50% lost in sifting', ha='center', fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(1.5, 85, 'E91: All bits usable!', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('../results/key_efficiency_comparison.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: key_efficiency_comparison.png")
    plt.close()


def plot_eavesdropping_scenarios():
    """Compare eavesdropping detection across scenarios"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    print("\nTesting eavesdropping scenarios...")
    
    scenarios = [
        ('E91: No Eve', scenario_1_no_eve(num_qubits=1000)['chsh'], 'green'),
        ('E91: Eve→Alice', scenario_2_eve_before_alice(num_qubits=1000)['chsh'], 'red'),
        ('E91: Eve→Bob', scenario_3_eve_before_bob(num_qubits=1000)['chsh'], 'orange'),
    ]
    
    names = [s[0] for s in scenarios]
    chsh_values = [s[1] for s in scenarios]
    colors = [s[2] for s in scenarios]
    
    bars = ax.bar(names, chsh_values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add threshold lines
    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Eve Detection Threshold (2.0)')
    ax.axhline(y=2.828, color='blue', linestyle=':', linewidth=2, label='Tsirelson Bound (2.828)')
    
    ax.set_ylabel('CHSH Value', fontsize=12, fontweight='bold')
    ax.set_title('E91 Eavesdropping Detection: CHSH in Different Attack Scenarios', 
                 fontsize=13, fontweight='bold')
    ax.set_ylim(0, 3.2)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, chsh_values):
        height = bar.get_height()
        detected = "✗ DETECTED" if val < 2.0 else "✓ SECURE"
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{val:.4f}\n{detected}', ha='center', va='bottom', 
                fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('../results/eavesdropping_scenarios.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: eavesdropping_scenarios.png")
    plt.close()


def plot_average_results():
    """Run both protocols multiple times and plot average results"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    print("\nCollecting average results from multiple runs...")
    num_runs = 10
    
    # BB84 runs
    print(f"Running BB84 {num_runs} times...")
    bb84_qber_no_eve = []
    bb84_qber_with_eve = []
    
    for i in range(num_runs):
        sifted_key, alice_bits, bob_results, alice_bases, bob_bases, eve_results, eve_bases, matching_no_eve = run_bb84_protocol(None, None, False)
        qber_no_eve = calculate_qber(alice_bits, bob_results, matching_no_eve)
        bb84_qber_no_eve.append(qber_no_eve)
        
        sifted_key, alice_bits, bob_results, alice_bases, bob_bases, eve_results, eve_bases, matching_with_eve = run_bb84_protocol(None, None, True)
        qber_with_eve = calculate_qber(alice_bits, bob_results, matching_with_eve)
        bb84_qber_with_eve.append(qber_with_eve)
        print(f"  Run {i+1}/{num_runs}")
    
    # E91 runs
    print(f"Running E91 {num_runs} times...")
    e91_chsh_no_eve = []
    e91_chsh_eve_before_alice = []
    e91_chsh_eve_before_bob = []
    
    for i in range(num_runs):
        result1 = scenario_1_no_eve(num_qubits=500)
        e91_chsh_no_eve.append(result1['chsh'])
        
        result2 = scenario_2_eve_before_alice(num_qubits=500)
        e91_chsh_eve_before_alice.append(result2['chsh'])
        
        result3 = scenario_3_eve_before_bob(num_qubits=500)
        e91_chsh_eve_before_bob.append(result3['chsh'])
        print(f"  Run {i+1}/{num_runs}")
    
    # Calculate statistics
    bb84_no_eve_mean, bb84_no_eve_std = np.mean(bb84_qber_no_eve), np.std(bb84_qber_no_eve)
    bb84_eve_mean, bb84_eve_std = np.mean(bb84_qber_with_eve), np.std(bb84_qber_with_eve)
    
    e91_no_eve_mean, e91_no_eve_std = np.mean(e91_chsh_no_eve), np.std(e91_chsh_no_eve)
    e91_eve_alice_mean, e91_eve_alice_std = np.mean(e91_chsh_eve_before_alice), np.std(e91_chsh_eve_before_alice)
    e91_eve_bob_mean, e91_eve_bob_std = np.mean(e91_chsh_eve_before_bob), np.std(e91_chsh_eve_before_bob)
    
    # Plot BB84
    ax = axes[0]
    scenarios = ['No Eve', 'With Eve']
    means = [bb84_no_eve_mean, bb84_eve_mean]
    stds = [bb84_no_eve_std, bb84_eve_std]
    colors = ['green', 'red']
    
    bars = ax.bar(scenarios, means, yerr=stds, capsize=10, color=colors, 
                  alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=11, color='orange', linestyle='--', linewidth=2, label='Detection Threshold (11%)')
    ax.set_ylabel('QBER (%)', fontsize=12, fontweight='bold')
    ax.set_title('BB84 Average QBER (10 runs)', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 35)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(fontsize=10)
    
    for bar, mean, std in zip(bars, means, stds):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 1,
                f'{mean:.2f}+/{std:.2f}%', ha='center', va='bottom', 
                fontweight='bold', fontsize=11)
    
    # Plot E91
    ax = axes[1]
    scenarios = ['No Eve', 'Eve→Alice', 'Eve→Bob']
    means = [e91_no_eve_mean, e91_eve_alice_mean, e91_eve_bob_mean]
    stds = [e91_no_eve_std, e91_eve_alice_std, e91_eve_bob_std]
    colors = ['green', 'darkred', 'orange']
    
    bars = ax.bar(scenarios, means, yerr=stds, capsize=10, color=colors,
                  alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Detection Threshold (2.0)')
    ax.axhline(y=2.828, color='blue', linestyle=':', linewidth=2, label='Tsirelson Bound (2.828)')
    ax.set_ylabel('CHSH Value', fontsize=12, fontweight='bold')
    ax.set_title('E91 Average CHSH (10 runs)', fontsize=13, fontweight='bold')
    ax.set_ylim(1.5, 3.0)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(fontsize=10)
    
    for bar, mean, std in zip(bars, means, stds):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.05,
                f'{mean:.3f}+/{std:.3f}', ha='center', va='bottom',
                fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('../results/average_results.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: average_results.png")
    plt.close()


def plot_comparison_table():
    """Create a comprehensive comparison plot"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    
    # Prepare data
    comparison_data = [
        ['Feature', 'BB84', 'E91'],
        ['', '', ''],
        ['Basis Count', '2 bases', '3 bases'],
        ['Quantum State', 'Prepare-and-measure', 'Entanglement-based'],
        ['', '', ''],
        ['Key Efficiency', '~25%', '100%'],
        ['Sifting Loss', '~75%', 'None'],
        ['', '', ''],
        ['Security Test', 'QBER < 11%', 'CHSH > 2.0'],
        ['Detection Method', 'Statistical', 'Mathematical (Bell)'],
        ['Eve Proof', 'Probabilistic', 'Deterministic'],
        ['', '', ''],
        ['Eavesdropping Impact', '25% error rate', 'Destroys entanglement'],
        ['False Positive Risk', 'High with noise', 'Low with statistics'],
        ['', '', ''],
        ['Real-world Readiness', 'Deployed widely', 'Lab demonstrations'],
    ]
    
    # Create table
    cell_text = comparison_data
    cell_colors = []
    for i, row in enumerate(comparison_data):
        if i == 0:  # Header
            cell_colors.append(['#4472C4', '#4472C4', '#4472C4'])
        elif i in [1, 4, 7, 11, 14]:  # Separator rows
            cell_colors.append(['#E7E6E6', '#E7E6E6', '#E7E6E6'])
        else:
            cell_colors.append(['#D9E1F2', '#E2EFDA', '#FCE4D6'])
    
    table = ax.table(cellText=cell_text, cellColours=cell_colors,
                     cellLoc='center', loc='center',
                     colWidths=[0.25, 0.37, 0.37])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header row
    for i in range(3):
        table[(0, i)].set_text_props(weight='bold', color='white', fontsize=11)
    
    # Bold key rows
    bold_rows = [2, 3, 5, 6, 8, 9, 10, 12, 13, 15]
    for row in bold_rows:
        for col in range(3):
            table[(row, col)].set_text_props(weight='bold')
    
    plt.title('BB84 vs E91: Comprehensive Comparison', 
              fontsize=15, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('../results/protocol_comparison_table.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: protocol_comparison_table.png")
    plt.close()


if __name__ == "__main__":
    # Create results folder if needed
    os.makedirs('../results', exist_ok=True)
    
    print("="*75)
    print("BB84 vs E91 Protocol Comparison - Average Results")
    print("="*75)
    print()
    
    plot_security_metrics()
    plot_key_efficiency()
    plot_eavesdropping_scenarios()
    plot_average_results()
    plot_comparison_table()
    
    print()
    print("="*75)
    print("All comparison plots generated and saved to ../results/")
    print("="*75)

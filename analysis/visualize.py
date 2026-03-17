"""
Visualization module for BB84 QKD protocol analysis.
"""

import matplotlib.pyplot as plt
import numpy as np
import os


# Create results folder if it doesn't exist
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)


def _save_plot(filename):
    """Helper function to save plots to results folder"""
    filepath = os.path.join(RESULTS_DIR, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {filename} → {RESULTS_DIR}")


def plot_qber_comparison(qber_no_eve, qber_with_eve):
    """
    Plot QBER comparison between scenarios with security threshold.
    
    Args:
        qber_no_eve: QBER without eavesdropping (%)
        qber_with_eve: QBER with eavesdropping (%)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # LEFT: QBER Values
    scenarios = ['No Eve', 'With Eve']
    qber_values = [qber_no_eve, qber_with_eve]
    colors = ['#2ecc71', '#e74c3c']  # Green=safe, Red=danger
    
    bars = ax1.bar(scenarios, qber_values, color=colors, alpha=0.7, 
                   edgecolor='black', linewidth=2)
    
    # Add values on bars
    for bar, val in zip(bars, qber_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}%', ha='center', va='bottom', 
                fontweight='bold', fontsize=11)
    
    # Security threshold
    ax1.axhline(y=11, color='red', linestyle='--', linewidth=2.5, 
               label='Security Threshold (11%)')
    ax1.fill_between([-0.5, 1.5], 0, 11, alpha=0.1, color='green')
    ax1.fill_between([-0.5, 1.5], 11, 50, alpha=0.1, color='red')
    
    ax1.set_ylabel('QBER (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Quantum Bit Error Rate', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, max(qber_values) + 5)
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(axis='y', alpha=0.3)
    
    # RIGHT: Security Status
    security_text = ['SECURE ✓' if qber_no_eve < 11 else 'SUSPICIOUS',
                     'DETECTED ⚠' if qber_with_eve > 11 else 'HIDDEN']
    status_colors = ['#2ecc71', '#e74c3c']
    
    bars2 = ax2.bar(scenarios, [1, 1], color=status_colors, alpha=0.7,
                    edgecolor='black', linewidth=2)
    
    for i, text in enumerate(security_text):
        ax2.text(i, 0.5, text, ha='center', va='center',
                fontsize=13, fontweight='bold', color='white')
    
    ax2.set_ylim(0, 1.2)
    ax2.set_yticks([])
    ax2.set_title('Security Status', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    _save_plot('qber_comparison.png')
    plt.show()


def plot_basis_distribution(alice_bases, bob_bases, eve_bases=None):
    """
    Plot basis distribution and matching statistics.
    
    Args:
        alice_bases: Alice's measurement bases
        bob_bases: Bob's measurement bases
        eve_bases: Eve's bases (optional)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # LEFT: Basis histogram
    alice_rectilinear = np.sum(alice_bases == 0)
    alice_diagonal = np.sum(alice_bases == 1)
    bob_rectilinear = np.sum(bob_bases == 0)
    bob_diagonal = np.sum(bob_bases == 1)
    
    x = np.arange(2)
    width = 0.35
    
    ax1.bar(x - width/2, [alice_rectilinear, alice_diagonal], width,
           label='Alice', alpha=0.7, color='#3498db', edgecolor='black', linewidth=1.5)
    ax1.bar(x + width/2, [bob_rectilinear, bob_diagonal], width,
           label='Bob', alpha=0.7, color='#e67e22', edgecolor='black', linewidth=1.5)
    
    ax1.set_ylabel('Count', fontsize=11, fontweight='bold')
    ax1.set_title('Basis Usage Distribution', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Rectilinear (|0⟩/|1⟩)', 'Diagonal (|+⟩/-⟩)'])
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)
    
    # RIGHT: Basis matching pie chart
    total = len(alice_bases)
    matching = np.sum(alice_bases == bob_bases)
    non_matching = total - matching
    
    sizes = [matching, non_matching]
    labels = [f'Matched\n({matching} bits)', f'Different\n({non_matching} bits)']
    colors_pie = ['#2ecc71', '#95a5a6']
    explode = (0.05, 0)
    
    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie,
                                        autopct='%1.1f%%', explode=explode,
                                        startangle=90, textprops={'fontsize': 10})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    
    ax2.set_title('Basis Matching Rate', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    _save_plot('basis_distribution.png')
    plt.show()


def plot_key_generation(key_length_no_eve, key_length_with_eve, total_qubits):
    """
    Plot key generation efficiency comparison.
    
    Args:
        key_length_no_eve: Sifted key length without Eve
        key_length_with_eve: Sifted key length with Eve
        total_qubits: Total qubits transmitted
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = ['No Eve', 'With Eve']
    key_lengths = [key_length_no_eve, key_length_with_eve]
    efficiency = [(k/total_qubits)*100 for k in key_lengths]
    colors = ['#2ecc71', '#e74c3c']
    
    bars = ax.bar(scenarios, key_lengths, color=colors, alpha=0.7,
                  edgecolor='black', linewidth=2)
    
    # Add labels with efficiency
    for bar, length, eff in zip(bars, key_lengths, efficiency):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(length)} bits\n({eff:.1f}%)',
               ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.axhline(y=total_qubits/2, color='blue', linestyle='--', linewidth=2,
              label=f'Expected 50% ({total_qubits//2} bits)', alpha=0.7)
    
    ax.set_ylabel('Sifted Key Length (bits)', fontsize=12, fontweight='bold')
    ax.set_title('Key Generation Efficiency', fontsize=13, fontweight='bold')
    ax.set_ylim(0, max(key_lengths) * 1.15)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    _save_plot('key_generation.png')
    plt.show()


def plot_security_summary(qber_no_eve, qber_with_eve, key_length_no_eve, 
                         key_length_with_eve):
    """
    Create a comprehensive security summary dashboard.
    
    Args:
        qber_no_eve: QBER without Eve
        qber_with_eve: QBER with Eve
        key_length_no_eve: Key length without Eve
        key_length_with_eve: Key length with Eve
    """
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)
    
    # Plot 1: QBER Comparison
    ax1 = fig.add_subplot(gs[0, 0])
    scenarios = ['No Eve', 'With Eve']
    qber_vals = [qber_no_eve, qber_with_eve]
    colors = ['#2ecc71', '#e74c3c']
    
    bars = ax1.bar(scenarios, qber_vals, color=colors, alpha=0.7, 
                   edgecolor='black', linewidth=1.5)
    ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Threshold')
    
    for bar, val in zip(bars, qber_vals):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    ax1.set_ylabel('QBER (%)', fontweight='bold')
    ax1.set_title('QBER Analysis', fontweight='bold', fontsize=11)
    ax1.set_ylim(0, max(qber_vals) + 5)
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Key Lengths
    ax2 = fig.add_subplot(gs[0, 1])
    key_vals = [key_length_no_eve, key_length_with_eve]
    
    bars = ax2.bar(scenarios, key_vals, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars, key_vals):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{int(val)} bits', ha='center', va='bottom', fontweight='bold')
    
    ax2.set_ylabel('Key Length (bits)', fontweight='bold')
    ax2.set_title('Sifted Key Comparison', fontweight='bold', fontsize=11)
    ax2.grid(axis='y', alpha=0.3)
    
    # Plot 3: Security Status Indicators
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.axis('off')
    
    status_no_eve = 'SECURE ✓' if qber_no_eve < 11 else 'SUSPICIOUS'
    status_with_eve = 'DETECTED ✗' if qber_with_eve > 11 else 'UNDETECTED'
    
    status_text = f"""
SECURITY STATUS

Without Eavesdropping:
  QBER: {qber_no_eve:.2f}%
  Status: {status_no_eve}
  Action: Accept Key ✓

With Eavesdropping:
  QBER: {qber_with_eve:.2f}%
  Status: {status_with_eve}
  Action: Reject & Restart ✗

Decision Threshold: 11% QBER
    """
    
    ax3.text(0.1, 0.5, status_text, fontsize=10, verticalalignment='center',
            fontfamily='monospace', bbox=dict(boxstyle='round', 
            facecolor='#ecf0f1', alpha=0.8))
    
    # Plot 4: Difference visualization
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')
    
    qber_diff = qber_with_eve - qber_no_eve
    key_diff = key_length_with_eve - key_length_no_eve
    
    info_text = f"""
PROTOCOL ANALYSIS

QBER Difference: {qber_diff:.2f}%
  (Eve introduces ~25% error spike)

Key Length Difference: {int(key_diff)} bits
  (~1% variation, statistically normal)

Why Eve is Detected:
  • Eve measures wrong basis 50% of time
  • Wrong basis → 50% collapsing errors
  • Combined effect: ~25% QBER increase
  • Easily detectable above 11% threshold

Conclusion:
  ✓ BB84 provides information-theoretic
    security against eavesdropping
  ✓ Eve cannot remain undetected
    """
    
    ax4.text(0.1, 0.5, info_text, fontsize=9.5, verticalalignment='center',
            fontfamily='monospace', bbox=dict(boxstyle='round',
            facecolor='#fff9e6', alpha=0.8))
    
    _save_plot('security_summary.png')
    plt.show()
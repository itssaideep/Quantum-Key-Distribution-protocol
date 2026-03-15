# Quantum Key Distribution Protocol Simulation

This project simulates and analyzes multiple Quantum Key Distribution (QKD) protocols including **BB84** and **E91 (Ekert91)**, providing a comprehensive understanding of quantum cryptography and quantum entanglement-based key distribution.

### Project Structure

A well-organized QKD simulation project typically follows a structure like this:

```
quantum-key-distribution-protocol/
├── main.py                 # Main script to run the simulation
├── protocols/              # Directory for QKD protocol implementations
│   ├── bb84.py             # Implementation of the BB84 protocol
│   ├── e91.py              # Implementation of the E91 protocol (Ekert91 with entanglement)
│   └── __init__.py         # Makes 'protocols' a Python package
├── utils/                  # Directory for utility functions
│   ├── quantum_helpers.py  # Functions for quantum state preparation, measurement
│   ├── classical_helpers.py# Functions for key sifting, error correction, privacy amplification
│   └── __init__.py
├── eavesdropping/          # (Optional) Module to simulate eavesdropper actions
│   └── eve_strategies.py   # Different eavesdropping strategies
│   └── __init__.py
├── analysis/               # Scripts or functions for analyzing results and plotting
│   └── visualize.py        # Functions for generating plots (QBER, key rate, etc.)
│   └── __init__.py
├── config.py               # Configuration file for simulation parameters (e.g., num_qubits, noise_levels)
├── ├── bb84_tutorial.ipynb
│   └── e91_tutorial.ipynb  # E91 protocol with entanglement testing # (Optional) Jupyter notebooks for interactive exploration and visualization
│   └── bb84_tutorial.ipynb
├── requirements.txt        # Lists all necessary Python packages
└── README.md               # Project description, setup, and usage instructions
```

### Features of a QKD Simulation

Your QKD simulation can incorporate various features to provide a comprehensive analysis:
BB84 and E91 (Ekert91) for testing both prepare-and-measure and entanglement-based approaches
*   **Multiple QKD Protocols:** Implementations of popular protocols like BB84, E91.
*   **Quantum State Preparation:** Modeling how Alice prepares quantum states (e.g., photons with specific polarizations) to encode key bits.
*   **Quantum Channel Simulation:** Simulating the transmission of quantum states, including the application of noise models to represent real-world channel imperfections.
*   **Measurement and Basis Reconciliation:** Simulating Bob's measurements and the subsequent public discussion between Alice and Bob to compare measurement bases and sift the raw key.
*   **Eavesdropping Detection:** Implementing an "Eve" entity to simulate interception attempts and demonstrate how QKD protocols detect her presence through introduced errors.
*   **Classical Post-Processing:**
    *   **Key Sifting:** Discarding bits where Alice and Bob used different bases.
    *   **Error Correction:** Applying classical error correction techniques to reconcile discrepancies.
    *   **Privacy Amplification:** Reducing Eve's knowledge of the shared key.
*   **Performance Metrics:** Calculation and analysis of key performance indicators such as:
    *   **Quantum Bit Error Rate (QBER):** The rate of errors in the quantum channel.
    *   **Key Rate:** The number of secure key bits generated per quantum state transmitted.
*   **Visualization:** Generating plots for quantum circuits, key agreement progress, and error rates to better understand the simulation's behavior.

### How to Run

To set up and run your QKD simulation project:

1.  **Install Python:** Ensure you have Python (3.8+) installed on your system.

2.  **Create a Virtual Environment (Recommended):**
    Navigate to your project's root directory in the terminal and run:
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    *   **Windows:** `.\venv\Scripts\activate`
    *   **macOS/Linux:** `source venv/bin/activate`

3.  **Install Dependencies:**
    Create a `requirements.txt` file in your project root with the following content:
    ```
    qiskit
    qiskit-aer
    numpy
    matplotlib
    ```
    Then, install them using pip:
    ```bash
    pip install -r requirements.txt
    ```
    (If you prefer Cirq over Qiskit, replace `qiskit` and `qiskit-aer` with `cirq` in `requirements.txt`.)

4.  **Execute the Simulation:**
    *   **For Python Scripts:** If your main simulation logic is in `main.py`, you can run it directly from your project root:
        ```bash
        python main.py
        ```
    *   **For Jupyter Notebooks:** If you're using Jupyter notebooks for interactive development or presentation:
        ```bash
        jupyter notebook
        ```
        This will open a browser window where you can navigate to and run your `.ipynb` files.

5.  **Configuration:** Modify parameters in your `config.py` file (or create one if it doesn't exist) to experiment with different QKD protocols, noise levels, or other simulation settings.

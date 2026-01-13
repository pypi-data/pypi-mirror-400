import sys
from qiskit import QuantumCircuit, transpile
import qiskit.qasm3

# Import Medusa
from qiskit_medusa.backend import MedusaBackend

# Import Qiskit Aer (The standard popular simulator)
try:
    from qiskit_aer import AerSimulator
except ImportError:
    print("Error: 'qiskit-aer' is missing. Please install it via 'pip install qiskit-aer'")
    sys.exit(1)

def main():
    # 1. Initialize Backends
    medusa_backend = MedusaBackend()
    medusa_backend.set_options(symbolic=True)

    aer_backend = AerSimulator()

    # 2. Load Circuit (File or Default)
    if len(sys.argv) > 1:
        qasm_file = sys.argv[1]
        print(f"--- Loading OpenQASM from file: {qasm_file} ---")
        try:
            with open(qasm_file, 'r') as f:
                data = f.read()
            qc = qiskit.qasm3.loads(data)
        except Exception as e:
            print(f"Error reading file '{qasm_file}': {e}")
            sys.exit(1)
    else:
        print("--- No file argument provided. Simulating default Bell State circuit. ---")
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

    # Define simulation parameters
    SHOTS = 5000

    # ---------------------------------------------------------
    # Simulation 1: Medusa
    # ---------------------------------------------------------
    print(f"\n[1] Running on MedusaBackend...")
    # Transpile specifically for Medusa
    qc_medusa = transpile(qc, backend=medusa_backend)

    job_medusa = medusa_backend.run(qc_medusa, shots=SHOTS)
    result_medusa = job_medusa.result()
    counts_medusa = result_medusa.get_counts()

    # ---------------------------------------------------------
    # Simulation 2: Aer Simulator (Standard Benchmark)
    # ---------------------------------------------------------
    print(f"[2] Running on AerSimulator...")
    # Transpile specifically for Aer
    qc_aer = transpile(qc, backend=aer_backend)

    job_aer = aer_backend.run(qc_aer, shots=SHOTS)
    result_aer = job_aer.result()
    counts_aer = result_aer.get_counts()

    # ---------------------------------------------------------
    # Comparison Output
    # ---------------------------------------------------------
    print("-" * 50)
    print("COMPARISON RESULTS")
    print("-" * 50)
    print(f"Medusa Counts: {counts_medusa}")
    print(f"Aer Counts:    {counts_aer}")

    # Simple check for matching keys (detected states)
    medusa_states = set(counts_medusa.keys())
    aer_states = set(counts_aer.keys())

    if medusa_states == aer_states:
        print("\nSUCCESS: Both simulators detected the same set of output states.")
    else:
        print("\nWARNING: The simulators detected different output states.")
        print(f"States in Medusa only: {medusa_states - aer_states}")
        print(f"States in Aer only:    {aer_states - medusa_states}")

if __name__ == "__main__":
    main()
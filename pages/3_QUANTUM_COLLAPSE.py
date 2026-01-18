import streamlit as st
import numpy as np
import sympy as sp
from itertools import product
import pandas as pd

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="Quantum Collapse Simulator", layout="wide")
st.title("Quantum Collapse Simulator")
st.markdown("""
Simulate **quantum measurement collapse** for 2-qubit or 3-qubit tensor product states.  
Enter **α and β** using fractions or square roots (e.g., 1/sqrt(2)), select qubit(s) to measure, 
and see how the state collapses along with probabilities.
""")
st.divider()

# -----------------------------
# Mode selection
# -----------------------------
num_qubits = st.radio("Select number of qubits:", [2, 3])

# -----------------------------
# User Inputs
# -----------------------------
qubit_values = []
for i in range(1, num_qubits + 1):
    st.subheader(f"Qubit {i} coefficients (α|0⟩ + β|1⟩)")
    alpha_str = st.text_input(f"α for qubit {i}", "1/sqrt(2)")
    beta_str = st.text_input(f"β for qubit {i}", "1/sqrt(2)")

    try:
        alpha = float(sp.N(sp.sympify(alpha_str)))
        beta = float(sp.N(sp.sympify(beta_str)))
        if not np.isclose(alpha**2 + beta**2, 1.0, atol=1e-6):
            st.error(f"Qubit {i}: |α|² + |β|² must equal 1. Check your inputs!")
            st.stop()
    except:
        st.error(f"Qubit {i}: Invalid input. Use numbers, fractions or sqrt().")
        st.stop()
    
    qubit_values.append((alpha, beta))

# -----------------------------
# Construct Tensor Product State
# -----------------------------
st.subheader("Tensor Product State")
states = ["0","1"]
tensor_coeffs = []
tensor_labels = []

for basis in product(states, repeat=num_qubits):
    coeff = 1.0
    label = ""
    for q, b in zip(qubit_values, basis):
        alpha, beta = q
        coeff *= alpha if b=="0" else beta
        label += b
    tensor_coeffs.append(coeff)
    tensor_labels.append(label)

# Display full state
full_state_str = " + ".join([f"({c:.3f})|{lbl}⟩" for c, lbl in zip(tensor_coeffs, tensor_labels)])
st.code(full_state_str)

# -----------------------------
# Measurement Selection
# -----------------------------
st.subheader("Select qubit measurement")
measure_qubits = []

for i in range(num_qubits):
    outcome = st.selectbox(f"Measure qubit {i+1}:", [None, "0","1"], index=0 if i==0 else 0)
    measure_qubits.append(outcome)

# -----------------------------
# Collapse logic
# -----------------------------
measured_indices = [i for i, val in enumerate(measure_qubits) if val is not None]

if measured_indices:
    # Partial collapsed state (before normalization)
    partial_coeffs = []
    partial_labels = []
    for c, lbl in zip(tensor_coeffs, tensor_labels):
        match = True
        for i in measured_indices:
            if lbl[i] != measure_qubits[i]:
                match = False
                break
        if match:
            partial_coeffs.append(c)
            partial_labels.append(lbl)

    st.subheader("Partial collapsed state (pre-normalization)")
    partial_state_str = " + ".join([f"({c:.3f})|{lbl}⟩" for c, lbl in zip(partial_coeffs, partial_labels)])
    st.code(partial_state_str)

    # Check normalization
    norm_sq = sum([abs(c)**2 for c in partial_coeffs])
    if not np.isclose(norm_sq,1.0):
        st.warning(f"State is not normalized: Σ|α|² = {norm_sq:.3f} ≠ 1")

    # Calculate normalization factor
    norm_factor = np.sqrt(1/norm_sq)
    st.markdown(f"**Normalization factor X applied:** {norm_factor:.3f}")

    # Apply normalization
    collapsed_coeffs = [c*norm_factor for c in partial_coeffs]
    collapsed_labels = partial_labels

    # Display collapsed state
    st.subheader("Collapsed State (normalized)")
    collapsed_state_str = " + ".join([f"({c:.3f})|{lbl}⟩" for c, lbl in zip(collapsed_coeffs, collapsed_labels)])
    st.code(collapsed_state_str)

    # -----------------------------
    # Probability Graph
    # -----------------------------
    st.subheader("Measurement Probabilities")
    df = pd.DataFrame({"State": collapsed_labels, "Probability": [abs(c)**2 for c in collapsed_coeffs]})
    st.bar_chart(df.set_index("State"))

else:
    st.info("Select at least one qubit outcome to perform collapse.")

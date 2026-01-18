import streamlit as st
import numpy as np
import plotly.graph_objects as go
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(page_title="Quantum Superposition", layout="wide")
st.title("Quantum Superposition — Bloch Sphere & Measurement")
st.markdown("""
Explore how different single-qubit states and their **phase** affect the **Bloch vector** and measurement probabilities.
""")
st.divider()

# ------------------------------------------------------------
# MCQ-based state selection
# ------------------------------------------------------------
st.subheader("Select a quantum state (α|0⟩ + β|1⟩)")

state_choice = st.radio(
    "Choose one state:",
    (
        "|0⟩",
        "|1⟩",
        "|+⟩ = (|0⟩ + |1⟩)/√2",
        "|−⟩ = (|0⟩ − |1⟩)/√2",
        "|i⟩ = (|0⟩ + i|1⟩)/√2",
        "|−i⟩ = (|0⟩ − i|1⟩)/√2",
        "Intermediate 1",
        "Intermediate 2",
        "Intermediate 3",
        "Intermediate 4",
    )
)

# Define real amplitudes for each choice (α always real, β magnitude adjusted)
if state_choice == "|0⟩":
    alpha, beta = 1.0, 0.0
    default_phi = 0.0
elif state_choice == "|1⟩":
    alpha, beta = 0.0, 1.0
    default_phi = 0.0
elif state_choice == "|+⟩ = (|0⟩ + |1⟩)/√2":
    alpha, beta = 1/np.sqrt(2), 1/np.sqrt(2)
    default_phi = 0.0
elif state_choice == "|−⟩ = (|0⟩ − |1⟩)/√2":
    alpha, beta = 1/np.sqrt(2), 1/np.sqrt(2)
    default_phi = np.pi
elif state_choice == "|i⟩ = (|0⟩ + i|1⟩)/√2":
    alpha, beta = 1/np.sqrt(2), 1/np.sqrt(2)
    default_phi = np.pi/2
elif state_choice == "|−i⟩ = (|0⟩ − i|1⟩)/√2":
    alpha, beta = 1/np.sqrt(2), 1/np.sqrt(2)
    default_phi = -np.pi/2
elif state_choice == "Intermediate 1":
    alpha, beta = np.sqrt(0.8), np.sqrt(0.2)
    default_phi = 0.0
elif state_choice == "Intermediate 2":
    alpha, beta = np.sqrt(0.6), np.sqrt(0.4)
    default_phi = 0.0
elif state_choice == "Intermediate 3":
    alpha, beta = np.sqrt(0.5), np.sqrt(0.5)
    default_phi = 0.0
else:  # Intermediate 4
    alpha, beta = np.sqrt(0.3), np.sqrt(0.7)
    default_phi = 0.0

# ------------------------------------------------------------
# Phase slider
# ------------------------------------------------------------
st.subheader("Adjust relative phase φ (radians)")

phi = st.slider(
    "Phase φ:",
    min_value=0.0,
    max_value=2*np.pi,
    value=default_phi,
    step=0.01
)

# Apply phase to beta
beta_complex = beta * np.exp(1j * phi)

# ------------------------------------------------------------
# Display state and probabilities
# ------------------------------------------------------------
st.subheader("State equation & probabilities")

st.latex(rf"|\psi\rangle = {alpha:.3f}|0\rangle + ({beta_complex:.3f})|1\rangle")
p0 = np.abs(alpha)**2
p1 = np.abs(beta_complex)**2

st.markdown(f"""
**Probabilities**  
- P(|0⟩) = |α|² = **{p0:.3f}**  
- P(|1⟩) = |β|² = **{p1:.3f}**  
- Normalization check: |α|² + |β|² = **{p0 + p1:.1f}**
""")

st.divider()

# ------------------------------------------------------------
# Bloch vector calculation (full 3D)
# ------------------------------------------------------------
x = 2 * np.real(np.conj(alpha) * beta_complex)
y = 2 * np.imag(np.conj(alpha) * beta_complex)
z = p0 - p1

# ------------------------------------------------------------
# 3D Bloch sphere using Plotly
# ------------------------------------------------------------
st.subheader("Bloch sphere visualization")

# Sphere surface
u = np.linspace(0, 2*np.pi, 50)
v = np.linspace(0, np.pi, 50)
xs = np.outer(np.cos(u), np.sin(v))
ys = np.outer(np.sin(u), np.sin(v))
zs = np.outer(np.ones_like(u), np.cos(v))

fig = go.Figure()
fig.add_surface(x=xs, y=ys, z=zs, opacity=0.25, showscale=False, colorscale='Blues')

# Axes with labels
axis_len = 1.2
fig.add_trace(go.Scatter3d(x=[-axis_len, axis_len], y=[0,0], z=[0,0], mode='lines+text', name='X axis'))
fig.add_trace(go.Scatter3d(x=[0,0], y=[-axis_len, axis_len], z=[0,0], mode='lines+text', name='Y axis'))
fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[-axis_len, axis_len], mode='lines+text', name='Z axis'))

# Add Bloch vector
fig.add_trace(go.Scatter3d(
    x=[0, x],
    y=[0, y],
    z=[0, z],
    mode='lines+markers',
    line=dict(width=6, color='red'),
    marker=dict(size=5),
    name='Qubit state'
))

fig.update_layout(
    scene=dict(
        xaxis=dict(title='X (|+⟩ / |−⟩)', range=[-1.2,1.2]),
        yaxis=dict(title='Y (|i⟩ / |−i⟩)', range=[-1.2,1.2]),
        zaxis=dict(title='Z (|0⟩ / |1⟩)', range=[-1.2,1.2]),
        aspectmode='cube',
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.2))
    ),
    margin=dict(l=0,r=0,t=0,b=0)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
- Vector rotates in full 3D as you adjust **phase φ**  
- Axes show canonical states  
- Sphere opacity gives depth perception  
""")

st.divider()

# ------------------------------------------------------------
# Measurement simulation
# ------------------------------------------------------------
st.subheader("Simulated measurement")

shots = st.slider("Number of measurements", min_value=100, max_value=5000, value=1000, step=100)

qc = QuantumCircuit(1,1)
# Apply general rotation: first Ry to get θ
theta = 2 * np.arccos(np.abs(alpha))
qc.ry(theta,0)
# Apply phase Rz for φ
qc.rz(phi,0)
qc.measure(0,0)

simulator = AerSimulator()
result = simulator.run(qc, shots=shots).result()
counts = result.get_counts()
p0_meas = counts.get("0",0)/shots
p1_meas = counts.get("1",0)/shots

st.bar_chart({"|0⟩": p0_meas, "|1⟩": p1_meas})

st.markdown("""
**Interpretation:**  
- The Bloch vector encodes the qubit state  
- Measurement collapses the vector to |0⟩ or |1⟩  
- Repeating measurements shows probabilities aligned with α, β, φ
""")

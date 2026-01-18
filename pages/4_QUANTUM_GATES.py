import streamlit as st
import numpy as np
import plotly.graph_objects as go
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

st.set_page_config(page_title="Interactive Quantum Gates", layout="wide")

# ---------------------------------------------------------
# 1. Helper Function: Draw 3D Bloch Sphere (Plotly)
# ---------------------------------------------------------
def plot_bloch_3d(state):
    # Calculate coordinates from Density Matrix
    rho = state.to_operator().data
    sigma_x = np.array([[0, 1], [1, 0]])
    sigma_y = np.array([[0, -1j], [1j, 0]])
    sigma_z = np.array([[1, 0], [0, -1]])
    
    x = np.real(np.trace(np.dot(rho, sigma_x)))
    y = np.real(np.trace(np.dot(rho, sigma_y)))
    z = np.real(np.trace(np.dot(rho, sigma_z)))

    # Draw Sphere (Wireframe & Surface)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    sphere_x = np.outer(np.cos(u), np.sin(v))
    sphere_y = np.outer(np.sin(u), np.sin(v))
    sphere_z = np.outer(np.ones(np.size(u)), np.cos(v))

    fig = go.Figure()
    
    # Surface
    fig.add_trace(go.Surface(x=sphere_x, y=sphere_y, z=sphere_z, opacity=0.1, showscale=False, colorscale='Blues'))
    
    # Equator & Meridians
    theta = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter3d(x=np.cos(theta), y=np.sin(theta), z=np.zeros_like(theta), mode='lines', line=dict(color='black', width=2), showlegend=False))
    phi = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter3d(x=np.zeros_like(phi), y=np.cos(phi), z=np.sin(phi), mode='lines', line=dict(color='black', width=2), showlegend=False))
    
    # State Vector (Arrow)
    fig.add_trace(go.Scatter3d(x=[0, x], y=[0, y], z=[0, z], mode='lines+markers', line=dict(color='#FF4B4B', width=10), marker=dict(size=5), name='State'))
    fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z], mode='markers', marker=dict(size=10, color='#FF4B4B'), showlegend=False))

    # Labels
    labels = [
        (1.3, 0, 0, '|+x⟩'), (-1.3, 0, 0, '|-x⟩'),
        (0, 1.3, 0, '|+y⟩'), (0, -1.3, 0, '|-y⟩'),
        (0, 0, 1.3, '|0⟩'), (0, 0, -1.3, '|1⟩')
    ]
    for lx, ly, lz, txt in labels:
        fig.add_trace(go.Scatter3d(x=[lx], y=[ly], z=[lz], mode='text', text=[txt], textposition="middle center", showlegend=False))

    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
        margin=dict(l=0, r=0, b=0, t=0), height=500
    )
    return fig

# ---------------------------------------------------------
# 2. Main Logic & Session State
# ---------------------------------------------------------
st.title("🧮 Interactive Gate Lab")

if 'gates' not in st.session_state:
    st.session_state.gates = []

# Two-column layout: Controls on Left, Visuals on Right
col_ctrl, col_vis = st.columns([1, 2])

with col_ctrl:
    st.markdown("### 1. Configuration")
    
    # MCQ: Initial State
    st.write("**Initialize Qubit State:**")
    init_state = st.radio(
        "Choose starting state", 
        ["|0⟩", "|1⟩", "|+⟩", "|-⟩"], 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # MCQ: Gate Selection
    st.markdown("### 2. Apply Gate")
    st.write("**Select a gate to apply:**")
    gate_choice = st.radio(
        "Select Gate",
        ["X (NOT)", "Y", "Z", "H (Hadamard)", "S (Phase)", "T (π/4)"],
        horizontal=False # Vertical list is easier to read for names
    )
    
    # Action Buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Apply Gate", use_container_width=True):
            # Extract just the letter (e.g., "X" from "X (NOT)")
            clean_gate = gate_choice.split()[0].lower()
            st.session_state.gates.append(clean_gate)
            
    with c2:
        if st.button("🔄 Reset All", type="primary", use_container_width=True):
            st.session_state.gates = []

    # Show History
    if st.session_state.gates:
        st.divider()
        st.write("**Gate History:**")
        st.caption(" → ".join([g.upper() for g in st.session_state.gates]))

# ---------------------------------------------------------
# 3. Circuit Construction
# ---------------------------------------------------------
qc = QuantumCircuit(1)

# Apply Initialization
if init_state == "|1⟩":
    qc.x(0)
elif init_state == "|+⟩":
    qc.h(0)
elif init_state == "|-⟩":
    qc.x(0)
    qc.h(0)

# Apply User Gates
for gate in st.session_state.gates:
    getattr(qc, gate)(0)

# ---------------------------------------------------------
# 4. Visualization (Right Column)
# ---------------------------------------------------------
with col_vis:
    # Generate Data
    state = Statevector.from_instruction(qc)
    probs = state.probabilities()
    
    # Draw 3D Sphere
    st.plotly_chart(plot_bloch_3d(state), use_container_width=True)
    
    # Circuit & Stats below the sphere
    sub_c1, sub_c2 = st.columns([2, 1])
    with sub_c1:
        st.write("**Circuit Diagram:**")
        st.pyplot(qc.draw(output='mpl', style='iqp'))
    with sub_c2:
        st.write("**Probabilities:**")
        st.write(f"P(0): **{probs[0]:.2%}**")
        st.progress(float(probs[0]))
        st.write(f"P(1): **{probs[1]:.2%}**")
        st.progress(float(probs[1]))
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Pauli

st.set_page_config(page_title="Quantum Gates", layout="wide")

# ==========================================
# 1. HELPER FUNCTION: DRAW 3D BLOCH SPHERE
# ==========================================
def plot_bloch_3d(state, title="Bloch Sphere"):
    """
    Creates a 3D interactive Bloch sphere with clear Axis Labels.
    """
    # 1. Calculate coordinates
    x_val = state.expectation_value(Pauli('X'))
    y_val = state.expectation_value(Pauli('Y'))
    z_val = state.expectation_value(Pauli('Z'))
    
    # 2. Setup Sphere Wireframe
    phi = np.linspace(0, 2*np.pi, 30)
    theta = np.linspace(0, np.pi, 30)
    phi, theta = np.meshgrid(phi, theta)
    sphere_x = np.sin(theta) * np.cos(phi)
    sphere_y = np.sin(theta) * np.sin(phi)
    sphere_z = np.cos(theta)
    
    fig = go.Figure()

    # Surface (Transparent)
    fig.add_trace(go.Surface(
        x=sphere_x, y=sphere_y, z=sphere_z,
        opacity=0.1, showscale=False, colorscale='Blues',
        hoverinfo='skip'  # Don't show coordinates when hovering surface
    ))

    # 3. Draw The Axes (The "Cross" inside)
    # X-axis line
    fig.add_trace(go.Scatter3d(
        x=[-1, 1], y=[0, 0], z=[0, 0],
        mode='lines', line=dict(color='black', width=2, dash='solid'),
        showlegend=False, hoverinfo='skip'
    ))
    # Y-axis line
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[-1, 1], z=[0, 0],
        mode='lines', line=dict(color='black', width=2, dash='solid'),
        showlegend=False, hoverinfo='skip'
    ))
    # Z-axis line
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[-1, 1],
        mode='lines', line=dict(color='black', width=2, dash='solid'),
        showlegend=False, hoverinfo='skip'
    ))

    # 4. Add The State Vector (Red Arrow)
    fig.add_trace(go.Scatter3d(
        x=[0, x_val], y=[0, y_val], z=[0, z_val],
        mode='lines+markers',
        line=dict(color='#FF4B4B', width=10), # Streamlit Red
        marker=dict(size=6, color='#FF4B4B'),
        name='Quantum State',
        hovertemplate=f"x: {x_val:.2f}<br>y: {y_val:.2f}<br>z: {z_val:.2f}<extra></extra>"
    ))
    
    # 5. Add Axis Labels (X, Y, Z, |0>, |1>)
    # We use 'text' mode to place labels at the tips of the axes
    labels = [
        dict(x=1.2, y=0, z=0, txt="<b>X</b> (|+⟩)", col="black"),
        dict(x=-1.2, y=0, z=0, txt="<b>-X</b> (|-⟩)", col="grey"),
        dict(x=0, y=1.2, z=0, txt="<b>Y</b>", col="black"),
        dict(x=0, y=-1.2, z=0, txt="<b>-Y</b>", col="grey"),
        dict(x=0, y=0, z=1.2, txt="<b>Z</b> (|0⟩)", col="black"),
        dict(x=0, y=0, z=-1.2, txt="<b>-Z</b> (|1⟩)", col="black"),
    ]
    
    for l in labels:
        fig.add_trace(go.Scatter3d(
            x=[l['x']], y=[l['y']], z=[l['z']],
            mode='text', text=[l['txt']],
            textposition="middle center",
            showlegend=False, hoverinfo='skip',
            textfont=dict(size=12, color=l['col'])
        ))

    # 6. Layout Cleanup (Remove the box)
    fig.update_layout(
        title=dict(text=title, y=0.9),
        width=350, height=350,
        scene=dict(
            xaxis=dict(visible=False), # Hide the box
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    return fig

# ==========================================
# 2. APP LOGIC
# ==========================================

st.title("Quantum Gate Playground 🛠️")
st.markdown("Visualizing how gates rotate the state vector on the Bloch Sphere.")
st.divider()

# --- INPUTS ---
col_setup, col_gate = st.columns(2)

with col_setup:
    st.subheader("Step 1: Start State")
    init_choice = st.radio(
        "Initial State:",
        ["|0⟩ (Z-up)", "|1⟩ (Z-down)", "|+⟩ (X-front)", "|-⟩ (X-back)"],
        horizontal=False
    )

with col_gate:
    st.subheader("Step 2: Apply Gate")
    gate_choice = st.radio(
        "Gate:",
        ["Identity", "X (NOT)", "Y", "Z", "H (Hadamard)"],
        horizontal=False
    )

# --- CALCULATION ---
qc = QuantumCircuit(1)

# Initialize
if "|1⟩" in init_choice: qc.x(0)
elif "|+⟩" in init_choice: qc.h(0)
elif "|-⟩" in init_choice: 
    qc.x(0)
    qc.h(0)

state_before = Statevector.from_instruction(qc)

# Apply Gate
qc_after = qc.copy()
if "X" in gate_choice: qc_after.x(0)
elif "Y" in gate_choice: qc_after.y(0)
elif "Z" in gate_choice: qc_after.z(0)
elif "H" in gate_choice: qc_after.h(0)

state_after = Statevector.from_instruction(qc_after)

# --- VISUALIZATION ---
st.divider()
col1, col2, col3 = st.columns([1, 0.2, 1])

with col1:
    st.markdown("##### Before")
    # Added key="bloch_before" to fix the Duplicate ID error
    st.plotly_chart(plot_bloch_3d(state_before, ""), use_container_width=True, key="bloch_before")

with col2:
    st.markdown("<br><br><br><br><h1 style='text-align: center; color: grey;'>➜</h1>", unsafe_allow_html=True)

with col3:
    st.markdown(f"##### After applying **{gate_choice.split()[0]}**")
    # Added key="bloch_after" to fix the Duplicate ID error
    st.plotly_chart(plot_bloch_3d(state_after, ""), use_container_width=True, key="bloch_after")
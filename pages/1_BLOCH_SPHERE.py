import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization.bloch import Bloch

# --------------------------------------------------
# Page title
# --------------------------------------------------
st.title("Bloch Sphere Visualization")

st.markdown("""
The Bloch Sphere is a geometric representation of a single qubit.
Each point on the sphere corresponds to a valid quantum state.
""")

st.markdown("---")

# --------------------------------------------------
# User controls
# --------------------------------------------------
st.subheader("Select quantum states to display")

col1, col2 = st.columns(2)

with col1:
    show_0 = st.checkbox("|0⟩", True)
    show_1 = st.checkbox("|1⟩", True)
    show_plus = st.checkbox("|+⟩", True)

with col2:
    show_minus = st.checkbox("|−⟩", True)
    show_random = st.checkbox("Random state", False)

# --------------------------------------------------
# Create Bloch Sphere
# --------------------------------------------------
bloch = Bloch()
bloch.figsize = [6, 6]
bloch.font_size = 12

vectors = []
colors = []

if show_0:
    vectors.append([0, 0, 1])
    colors.append("tab:blue")

if show_1:
    vectors.append([0, 0, -1])
    colors.append("tab:red")

if show_plus:
    vectors.append([1, 0, 0])
    colors.append("tab:green")

if show_minus:
    vectors.append([-1, 0, 0])
    colors.append("tab:orange")

if show_random:
    theta = np.random.uniform(0, np.pi)
    phi = np.random.uniform(0, 2 * np.pi)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    vectors.append([x, y, z])
    colors.append("purple")

if vectors:
    bloch.add_vectors(vectors)
    bloch.vector_color = colors

# --------------------------------------------------
# Render
# --------------------------------------------------
fig = plt.figure(figsize=(6, 6))
bloch.render(fig)
st.pyplot(fig)

# --------------------------------------------------
# Explanation
# --------------------------------------------------
st.markdown("""
### Interpretation

- |0⟩ and |1⟩ lie on the Z-axis  
- |+⟩ and |−⟩ lie on the X-axis  
- Any other point on the sphere represents a superposition  
- Measurement collapses the state onto |0⟩ or |1⟩  

This visualization helps connect linear algebra with geometry.
""")

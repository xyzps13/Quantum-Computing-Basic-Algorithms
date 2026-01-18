import streamlit as st

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Quantum Computing Project",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Custom CSS: minimal, professional, aesthetic
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-image: none;
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }

    .block-container {
        background-color: rgba(255, 255, 255, 0);
        padding: 3rem;
        border-radius: 16px;
        max-width: 1100px;
        margin: auto;
    }

    h1 {
        font-size: 52px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeIn 1.5s ease-in-out;
    }

    h2 {
        margin-top: 2.5rem;
        font-size: 28px;
    }

    p, li {
        font-size: 18px;
        line-height: 1.7;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Home Page Content
# --------------------------------------------------
st.markdown("<h1>Quantum Computing Interactive Project</h1>", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center; font-size:20px;'>"
    "A visual and conceptual exploration of quantum computation using Qiskit"
    "</p>",
    unsafe_allow_html=True
)

st.markdown("---")

st.markdown("""
## About the Project

This project is designed to build a **deep conceptual understanding of quantum computing**
through **interactive visualizations** and **simulations**.

Instead of treating quantum mechanics as abstract mathematics, this dashboard allows you
to **see**, **manipulate**, and **experiment** with quantum states and algorithms.

The implementation uses:
- Qiskit for quantum computation
- Streamlit for interactive visualization
- Jupyter notebooks for theory and explanation
""")

st.markdown("""
## What You Will Explore

- Bloch Sphere visualization of single-qubit states  
- Superposition and measurement collapse  
- Quantum gates and their geometric effects  
- Entanglement and Bell states  
- Superdense coding  
- Quantum algorithms compared with classical approaches  
- A sandbox-style quantum circuit builder  
""")

st.markdown("""
## How to Use This Dashboard

Use the **sidebar on the left** to navigate between sections.
Each topic is implemented as a **separate page** for clarity and modularity.

You are encouraged to:
- Explore visually first
- Read the explanations
- Then inspect the related Jupyter notebooks
""")

st.markdown("---")

st.markdown(
    "<p style='text-align:center; font-size:16px;'>"
    "This project prioritizes clarity, intuition, and correctness over noise."
    "</p>",
    unsafe_allow_html=True
)

import streamlit as st
import numpy as np
import time
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Quantum Arcade", layout="wide", page_icon="🕹️")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
# Navigation
if 'arcade_mode' not in st.session_state:
    st.session_state.arcade_mode = "Lobby"

# --- State for Grover's Game ---
if 'secret_target' not in st.session_state:
    st.session_state.secret_target = np.random.randint(0, 16)
if 'clicked_boxes' not in st.session_state:
    st.session_state.clicked_boxes = set()
if 'grover_game_over' not in st.session_state:
    st.session_state.grover_game_over = False

# --- State for Deutsch-Jozsa (Jar Game) ---
if 'dj_history' not in st.session_state:
    st.session_state.dj_history = []
if 'dj_balls_remaining' not in st.session_state:
    st.session_state.dj_balls_remaining = []
if 'dj_n_balls' not in st.session_state:
    st.session_state.dj_n_balls = 8 # Default
if 'dj_type' not in st.session_state:
    st.session_state.dj_type = "Constant (All Red)"

# Helper Functions
def go_lobby():
    st.session_state.arcade_mode = "Lobby"

def reset_grover():
    st.session_state.secret_target = np.random.randint(0, 16)
    st.session_state.clicked_boxes = set()
    st.session_state.grover_game_over = False

def reset_dj(n, jar_type):
    st.session_state.dj_history = []
    st.session_state.dj_n_balls = n
    st.session_state.dj_type = jar_type
    
    if "Constant" in jar_type:
        # All Red
        st.session_state.dj_balls_remaining = ["🔴"] * n
    else:
        # Balanced: Half Red, Half Blue
        half = n // 2
        balls = ["🔴"] * half + ["🔵"] * half
        np.random.shuffle(balls)
        st.session_state.dj_balls_remaining = balls

# ==========================================
# 1. THE LOBBY (MENU)
# ==========================================
if st.session_state.arcade_mode == "Lobby":
    st.title("🕹️ The Quantum Arcade")
    st.markdown("### Choose a mission to compare **Human/Classical effort** vs. **Quantum Power**.")
    st.divider()

    col1, col2, col3 = st.columns(3)

    # CARD 1: GROVER
    with col1:
        st.container(border=True).markdown("""
        ### 🚀 Galactic Hunt
        **Algorithm:** Grover's Search
        
        * **The Mission:** Find the alien signal in 16 sectors.
        * **Classical:** YOU click sectors one by one.
        * **Quantum:** Finds it instantly.
        """)
        if st.button("Start Mission 1 ➜"):
            reset_grover()
            st.session_state.arcade_mode = "Grover"
            st.rerun()

    # CARD 2: DEUTSCH-JOZSA
    with col2:
        st.container(border=True).markdown("""
        ### 🏺 The Mystery Jar
        **Algorithm:** Deutsch-Jozsa
        
        * **The Mission:** Check if a jar has mixed colors or one color.
        * **Classical:** Draw balls until sure.
        * **Quantum:** Check all balls at once.
        """)
        if st.button("Start Mission 2 ➜"):
            # Initialize with default settings
            reset_dj(8, "Constant (All Red)")
            st.session_state.arcade_mode = "DJ"
            st.rerun()

    # CARD 3: SHOR
    with col3:
        st.container(border=True).markdown("""
        ### 🏦 The Bank Heist
        **Algorithm:** Shor's Algorithm
        
        * **The Mission:** Crack the RSA lock (Factorize 15).
        * **Classical:** Guess numbers blindly.
        * **Quantum:** Find the wave pattern.
        """)
        if st.button("Start Mission 3 ➜"):
            st.session_state.arcade_mode = "Shor"
            st.rerun()

# ==========================================
# 2. MISSION 1: GROVER'S GALACTIC HUNT
# ==========================================
elif st.session_state.arcade_mode == "Grover":
    st.button("🏠 Exit to Lobby", on_click=go_lobby)
    st.title("🚀 Mission: The Galactic Search")
    st.markdown("A signal is hidden in one of these 16 sectors. **Can you find it?**")

    tab_user, tab_algo = st.tabs(["👤 You (Classical Search)", "⚛️ Grover's Algorithm"])

    # --- CLASSICAL TAB ---
    with tab_user:
        st.subheader("Manual Search Mode")
        st.caption("Click the buttons below. Try to find the Alien Signal 👽.")
        
        # Grid Layout
        cols = st.columns(4)
        for i in range(16):
            # Determine visual state of button
            if i in st.session_state.clicked_boxes:
                if i == st.session_state.secret_target:
                    label = "👽 FOUND!"
                    btn_type = "primary"
                else:
                    label = "Empty"
                    btn_type = "secondary"
            else:
                label = f"Sector {i}"
                btn_type = "secondary"

            # Button Logic
            disabled = (i in st.session_state.clicked_boxes) or st.session_state.grover_game_over
            
            if cols[i % 4].button(label, key=f"btn_{i}", type=btn_type, disabled=disabled, use_container_width=True):
                st.session_state.clicked_boxes.add(i)
                if i == st.session_state.secret_target:
                    st.session_state.grover_game_over = True
                    st.balloons()
                st.rerun()

        # Stats
        attempts = len(st.session_state.clicked_boxes)
        st.divider()
        st.metric("Your Attempts (Queries)", f"{attempts} / 16")
        
        if st.session_state.grover_game_over:
            st.success(f"🎉 Target Neutralized! It took you {attempts} queries.")
            if st.button("🔄 Play Again (New Target)"):
                reset_grover()
                st.rerun()

    # --- QUANTUM TAB ---
    with tab_algo:
        st.subheader("Quantum Search Mode")
        st.write("The Quantum Computer builds a circuit to amplify the probability of the Target.")
        
        col_c, col_r = st.columns([2, 1])
        with col_c:
            target_bin = format(st.session_state.secret_target, '04b')
            
            # Build Circuit Visualization
            qc = QuantumCircuit(4, 4)
            qc.h(range(4))
            qc.barrier()
            # Simplified Oracle for display
            for idx, bit in enumerate(reversed(target_bin)):
                if bit == '0': qc.x(idx)
            qc.h(3); qc.mcx([0,1,2], 3); qc.h(3)
            for idx, bit in enumerate(reversed(target_bin)):
                if bit == '0': qc.x(idx)
            qc.barrier()
            qc.measure(range(4), range(4))
            
            st.pyplot(qc.draw('mpl', style="iqp"), use_container_width=True)
            
        with col_r:
            if st.button("Run Grover's Algorithm ⚡"):
                with st.spinner("Amplifying Amplitudes..."):
                    # Simulation Logic
                    qc_sim = QuantumCircuit(4, 4)
                    qc_sim.h(range(4))
                    # 3 Iterations is optimal for N=16
                    for _ in range(3):
                        # Oracle
                        for idx, bit in enumerate(reversed(target_bin)):
                            if bit == '0': qc_sim.x(idx)
                        qc_sim.h(3); qc_sim.mcx([0,1,2], 3); qc_sim.h(3)
                        for idx, bit in enumerate(reversed(target_bin)):
                            if bit == '0': qc_sim.x(idx)
                        # Diffuser
                        qc_sim.h(range(4)); qc_sim.x(range(4))
                        qc_sim.h(3); qc_sim.mcx([0,1,2], 3); qc_sim.h(3)
                        qc_sim.x(range(4)); qc_sim.h(range(4))
                    
                    qc_sim.measure(range(4), range(4))
                    sim = AerSimulator()
                    counts = sim.run(transpile(qc_sim, sim), shots=1024).result().get_counts()
                    
                    st.pyplot(plot_histogram(counts))
                    
                    winner = int(max(counts, key=counts.get), 2)
                    st.metric("Queries Used", "3 (Fixed)", delta="Optimal")
                    st.success(f"Target Located: Sector {winner}")

# ==========================================
# 3. MISSION 2: DEUTSCH-JOZSA (THE JAR)
# ==========================================
elif st.session_state.arcade_mode == "DJ":
    st.button("🏠 Exit to Lobby", on_click=go_lobby)
    st.title("🏺 Mission: The Mystery Jar")
    
    st.markdown("""
    **The Puzzle:** You have a jar of **N Balls**.
    * **Constant Jar:** All balls are **RED** 🔴🔴🔴🔴.
    * **Balanced Jar:** Half are **RED**, Half are **BLUE** 🔴🔴🔵🔵.
    """)

    # --- CONFIGURATION ---
    with st.container(border=True):
        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1:
            n_select = st.select_slider("Size of Jar (N):", options=[8, 16, 32], value=st.session_state.dj_n_balls)
        with col_cfg2:
            type_select = st.radio("Secret Contents:", ["Constant (All Red)", "Balanced (Half Red/Half Blue)"])
        with col_cfg3:
            if st.button("🔄 Apply & Reset Game", use_container_width=True):
                reset_dj(n_select, type_select)
                st.rerun()

    worst_case = int((st.session_state.dj_n_balls / 2) + 1)

    tab_c, tab_q = st.tabs(["🤚 Classical Hand (You)", "⚛️ Quantum Hand"])

    # --- CLASSICAL TAB ---
    with tab_c:
        col_game, col_log = st.columns([1, 1])
        
        with col_game:
            st.subheader("Draw Balls")
            st.write(f"To be 100% sure it's Constant, you need **{worst_case} Reds** in a row.")
            
            if st.session_state.dj_balls_remaining:
                if st.button("🖐️ Draw One Ball", use_container_width=True):
                    ball = st.session_state.dj_balls_remaining.pop(0)
                    st.session_state.dj_history.append(ball)
            else:
                st.warning("Jar is empty.")
            
            # Visual Representation of "Unknowns"
            st.caption("Balls remaining in jar:")
            st.write("❔ " * len(st.session_state.dj_balls_remaining))

        with col_log:
            st.subheader("History")
            history_str = " ".join(st.session_state.dj_history)
            st.markdown(f"### {history_str}")
            
            tries = len(st.session_state.dj_history)
            st.metric("Balls Drawn", f"{tries} / {worst_case}")
            
            # Verdict Logic
            unique = set(st.session_state.dj_history)
            if len(unique) > 1:
                st.success("✅ **Balanced!** (You found Blue and Red)")
            elif tries >= worst_case:
                st.success(f"✅ **Constant!** (You found {worst_case} Reds, so majority is Red)")
            else:
                st.info("Still unsure...")

    # --- QUANTUM TAB ---
    with tab_q:
        st.subheader("Quantum Solution")
        st.markdown("The Quantum Computer inputs **indices of all balls** simultaneously.")
        
        if st.button("Run Quantum Circuit ⚡"):
            n_qubits = int(np.log2(st.session_state.dj_n_balls))
            
            qc = QuantumCircuit(n_qubits + 1, n_qubits)
            qc.x(n_qubits); qc.h(range(n_qubits + 1)) # Init
            
            # Oracle
            if "Balanced" in st.session_state.dj_type:
                for i in range(n_qubits): qc.cx(i, n_qubits) # XOR logic
            
            qc.h(range(n_qubits))
            qc.measure(range(n_qubits), range(n_qubits))
            
            sim = AerSimulator()
            res = sim.run(transpile(qc, sim), shots=1).result().get_counts()
            outcome = list(res.keys())[0]
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.pyplot(qc.draw('mpl'), use_container_width=True)
            with col_res2:
                st.metric("Queries Used", "1", delta="Instant")
                if outcome == "0" * n_qubits:
                    st.success("Measurement: |0..0> → **Constant (All Red)**")
                    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Deutsch-Jozsa-algorithm-quantum-circuit.png/600px-Deutsch-Jozsa-algorithm-quantum-circuit.png", caption="Constructive Interference")
                else:
                    st.success(f"Measurement: |{outcome}> → **Balanced (Mixed)**")

# ==========================================
# 4. MISSION 3: SHOR'S BANK HEIST
# ==========================================
elif st.session_state.arcade_mode == "Shor":
    st.button("🏠 Exit to Lobby", on_click=go_lobby)
    st.title("🏦 The Bank Heist")
    st.markdown("Unlock the vault by factoring **N = 15**. (Factors: 3 and 5)")
    
    col_c, col_q = st.columns(2)
    
    with col_c:
        st.container(border=True).markdown("### 🔨 Classical Brute Force")
        st.write("Trying to divide by every number...")
        if st.button("Start Guessing"):
            status = st.empty()
            time.sleep(0.5); status.write("Trying 2... 15 % 2 != 0 ❌")
            time.sleep(0.5); status.write("Trying 3... 15 % 3 == 0 ✅ **FOUND FACTOR 3!**")
            st.metric("Complexity", "Exponential O(2^n)", delta="Fail for large N")

    with col_q:
        st.container(border=True).markdown("### 🌊 Quantum Period Finding")
        st.write("Using Modular Exponentiation $f(x) = 7^x \mod 15$")
        
        if st.button("Find Period (Quantum Wave)"):
            x = np.arange(0, 10, 1)
            y = (7 ** x) % 15 
            
            fig, ax = plt.subplots()
            ax.step(x, y, where='mid', color='#7000ff')
            ax.set_title("Periodicity of f(x)")
            ax.grid(True)
            st.pyplot(fig)
            
            st.success("**Period r=4 found!**")
            st.latex(r"\text{Factors} = \text{gcd}(7^{4/2} \pm 1, 15) \rightarrow 3, 5")
            st.balloons()
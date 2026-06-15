import numpy as np
import pandas as pd

PHI = (1 + np.sqrt(5)) / 2

def generate_golden_numbers(historical_data_path, quantum_csv_path, next_draw_seq, jitter_strength=0.1):
    # ---------------------------------------------------------
    # 1. LOAD HISTORICAL DATA (Both Pools)
    # ---------------------------------------------------------
    try:
        df_history = pd.read_csv(historical_data_path)
        
        # Main 6 Numbers (1-37)
        all_picks = df_history[['p1', 'p2', 'p3', 'p4', 'p5', 'p6']].values.flatten()
        counts = pd.Series(all_picks).value_counts()
        hist_weights_main = {i: counts.get(i, 0) + 5 for i in range(1, 38)} # +5 smoothing
        max_freq_main = max(hist_weights_main.values())
        hist_weights_main = {k: v / max_freq_main for k, v in hist_weights_main.items()}
        
        # Strong Number (1-7)
        strong_picks = df_history['strong_num'].values
        strong_counts = pd.Series(strong_picks).value_counts()
        hist_weights_strong = {i: strong_counts.get(i, 0) + 5 for i in range(1, 8)} # +5 smoothing
        max_freq_strong = max(hist_weights_strong.values())
        hist_weights_strong = {k: v / max_freq_strong for k, v in hist_weights_strong.items()}

    except Exception as e:
        print(f"Warning: Failed to load historical data. {e}")
        hist_weights_main = {i: 1.0 for i in range(1, 38)}
        hist_weights_strong = {i: 1.0 for i in range(1, 8)}

    # ---------------------------------------------------------
    # 2. CALCULATE WAVES
    # ---------------------------------------------------------
    jitter = np.random.normal(0, jitter_strength)
    t_adjusted = next_draw_seq + jitter
    wave_value = np.sin((2 * np.pi / PHI) * t_adjusted)
    normalized_wave = (wave_value + 1) / 2
    
    # Map wave to 1-37 pool
    target_center_main = 1 + int(normalized_wave * 36)
    balls_main = np.arange(1, 38)
    wave_weights_main = 1 / (np.abs(balls_main - target_center_main) + 1)
    wave_weights_main /= wave_weights_main.max()

    # Map same wave to 1-7 pool
    target_center_strong = 1 + int(normalized_wave * 6)
    balls_strong = np.arange(1, 8)
    wave_weights_strong = 1 / (np.abs(balls_strong - target_center_strong) + 1)
    wave_weights_strong /= wave_weights_strong.max()

    # ---------------------------------------------------------
    # 3. COMBINE WEIGHTS
    # ---------------------------------------------------------
    final_main = {ball: hist_weights_main[ball] * wave_weights_main[i] for i, ball in enumerate(balls_main)}
    final_main = {k: v / max(final_main.values()) for k, v in final_main.items()}

    final_strong = {ball: hist_weights_strong[ball] * wave_weights_strong[i] for i, ball in enumerate(balls_strong)}
    final_strong = {k: v / max(final_strong.values()) for k, v in final_strong.items()}

    # ---------------------------------------------------------
    # 4. QUANTUM REJECTION SAMPLING
    # ---------------------------------------------------------
    try:
        df_quantum = pd.read_csv(quantum_csv_path)
        quantum_pool = df_quantum['quantum_number'].tolist()
    except Exception:
        quantum_pool = np.random.randint(1, 38, size=5000).tolist()
        
    chosen_main = set()
    chosen_strong = None
    
    for q_num in quantum_pool:
        if len(chosen_main) == 6 and chosen_strong is not None:
            break
            
        # Filter for main 6 (1-37)
        if len(chosen_main) < 6 and 1 <= q_num <= 37 and q_num not in chosen_main:
            if np.random.random() <= final_main[q_num]:
                chosen_main.add(q_num)
                
        # Filter for strong number (1-7)
        if chosen_strong is None and 1 <= q_num <= 7:
            if np.random.random() <= final_strong[q_num]:
                chosen_strong = q_num
            
    # Safety Nets
    while len(chosen_main) < 6:
        fb = int(np.random.randint(1, 38))
        if fb not in chosen_main: chosen_main.add(fb)
    
    if chosen_strong is None:
        chosen_strong = int(np.random.randint(1, 8))
        
    return sorted(list(chosen_main)), chosen_strong
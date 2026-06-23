import numpy as np
import time
import os

def simulate_kinematic_draw(historical_data_path, quantum_csv_path, next_draw_seq, motor_hz, kinetic_hz):
    print(f"\n=======================================================")
    print(f"[KINEMATICS ENGINE] BOOTING DRUM SIMULATION FOR SEQ {next_draw_seq}")
    print(f"=======================================================")
    
    # 1. NEW: Parse Comma-Separated Quantum Seed
    try:
        with open(quantum_csv_path, 'r') as file:
            raw_text = file.read()
            
        # Clean the text: remove the header and replace line breaks with commas
        cleaned_text = raw_text.replace('quantum_number', '').replace('\n', ',')
        
        # Split by comma, strip spaces, and keep only actual numbers
        quantum_pool = np.array([
            int(x.strip()) for x in cleaned_text.split(',') 
            if x.strip().isdigit()
        ])
        
        if len(quantum_pool) == 0:
            raise ValueError("No valid numbers found in the file.")
            
    except Exception as e:
        print(f"[ERROR] Could not load/parse Quantum Seed: {e}")
        return [1, 2, 3, 4, 5, 6], 1

    total_pool_size = len(quantum_pool)
    
    # 2. Stateless pointer drop-in
    ns_time = time.time_ns() 
    current_pointer = ns_time % total_pool_size
    
    selected_balls = []
    search_space = list(range(1, 38))
    
    # Physical Simulation Parameters
    t = 0.0          
    time_step = 0.01 
    trapdoor_threshold = 1.90 
    
    print(f"[PHYSICS] Motor Set: {motor_hz}Hz | Kinetic Set: {kinetic_hz}Hz")
    print(f"[PHYSICS] Trapdoor opens at amplitude > {trapdoor_threshold}")
    print(f"[DATA] Successfully loaded {total_pool_size} quantum numbers.")
    print("\n[SIMULATION] --- SPINNING DRUM ---")
    
    # Simulate time moving forward until 6 balls are ejected
    while len(selected_balls) < 6:
        # Calculate the Beat Frequency at the current millisecond
        w1 = np.sin(2 * np.pi * motor_hz * t)
        w2 = np.sin(2 * np.pi * kinetic_hz * t)
        compound_amplitude = w1 + w2
        
        # If the wave spikes, the trapdoor opens!
        if compound_amplitude > trapdoor_threshold:
            # The Quantum measurement occurs ONLY at this exact millisecond
            raw_q = quantum_pool[current_pointer]
            
            # Map the raw quantum integer to the remaining balls in the drum
            index_to_pluck = raw_q % len(search_space)
            ejected_ball = search_space.pop(index_to_pluck)
            
            selected_balls.append(ejected_ball)
            
            print(f"  [!] RESONANCE SPIKE at {t:.2f}s (Amp: {compound_amplitude:.3f})")
            print(f"      -> Trapdoor Open! Quantum Seed [{raw_q}] ejected Ball {ejected_ball:02d}")
            
            # Advance the quantum pointer
            current_pointer = (current_pointer + 1) % total_pool_size
            
            # Jump time forward slightly so we don't immediately trigger on the same peak
            t += 0.1 
        
        # Advance time naturally
        t += time_step

    # Seek Strong Number (1-7) using the next resonance spike
    strong_num = 1
    print("\n[SIMULATION] --- SEEKING STRONG NUMBER ---")
    strong_space = list(range(1, 8))
    
    while True:
        w1 = np.sin(2 * np.pi * motor_hz * t)
        w2 = np.sin(2 * np.pi * kinetic_hz * t)
        if (w1 + w2) > trapdoor_threshold:
            raw_q = quantum_pool[current_pointer]
            index = raw_q % len(strong_space)
            strong_num = strong_space[index]
            
            print(f"  [!] FINAL SPIKE at {t:.2f}s | Ejected Strong Num: {strong_num}")
            break
            
        t += time_step

    print(f"\n[ENGINE] Simulation complete. Total virtual spin time: {t:.2f} seconds.")
    print(f"=======================================================\n")
    
    return sorted(selected_balls), strong_num
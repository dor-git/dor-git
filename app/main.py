from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import numpy as np
import os
from app.engine import generate_golden_numbers

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# ==========================================
# FILE CONFIGURATION (These were missing!)
# ==========================================
HISTORICAL_FILE = "historical_data.csv" 
QUANTUM_FILE = "quantum_seed.csv"

@app.head("/")
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/next-sequence")
async def get_next_sequence():
    try:
        if os.path.exists(HISTORICAL_FILE):
            df = pd.read_csv(HISTORICAL_FILE)
            highest_seq = int(df['draw_seq'].max())
            return {"next_sequence": highest_seq + 1}
        else:
            return {"next_sequence": 1}
    except Exception as e:
        print(f"Error reading sequence: {e}")
        return {"next_sequence": 1}

@app.get("/api/auto-tune")
async def auto_tune_jitter(seq: int):
    try:
        past_seq = seq - 1 
        
        if not os.path.exists(HISTORICAL_FILE):
            return {"optimal_jitter": 0.10, "message": "File not found."}
            
        df = pd.read_csv(HISTORICAL_FILE)
        past_draw = df[df['draw_seq'] == past_seq]
        
        if past_draw.empty:
            return {"optimal_jitter": 0.10, "message": "Previous sequence not found."}
            
        # Convert to standard Python integers to guarantee exact matching
        real_numbers = set([int(x) for x in past_draw.iloc[0][['p1', 'p2', 'p3', 'p4', 'p5', 'p6']].values])
        real_strong = int(past_draw.iloc[0]['strong_num'])
        
        best_jitter = 0.00
        highest_score = -1
        
        print(f"\n--- STARTING AUTO-TUNE FOR PAST SEQ {past_seq} ---")
        print(f"Target Numbers: {real_numbers} | Target Strong: {real_strong}")
        
        for j in np.arange(0.00, 1.62, 0.05):
            current_jitter = round(j, 2)
            total_score = 0
            
            # Sample 3 times per jitter to account for quantum variance
            for _ in range(3):
                main_nums, strong = generate_golden_numbers(
                    historical_data_path=HISTORICAL_FILE, 
                    quantum_csv_path=QUANTUM_FILE, 
                    next_draw_seq=past_seq, 
                    jitter_strength=current_jitter
                )
                
                matches = len(set(main_nums).intersection(real_numbers))
                total_score += matches
                if strong == real_strong:
                    total_score += 3  # Strong number hits are worth 3 points
                    
            if total_score > highest_score:
                highest_score = total_score
                best_jitter = current_jitter
                
            # Log every single step to the terminal!
            print(f"Jitter {current_jitter:.2f} | Total Score: {total_score}")
            
        print(f">>> WINNER: Jitter {best_jitter:.2f} with Score {highest_score}")
        print("-------------------------------------------------\n")
        
        return {"optimal_jitter": best_jitter, "score": highest_score}
        
    except Exception as e:
        print(f"Auto-tune error: {e}")
        return {"optimal_jitter": 0.10, "message": "Error calculating. Defaulting."}

@app.get("/api/draw")
async def get_draw(seq: int, jitter: float = 0.1):
    main_numbers, strong_number = generate_golden_numbers(
        historical_data_path=HISTORICAL_FILE, 
        quantum_csv_path=QUANTUM_FILE,
        next_draw_seq=seq, 
        jitter_strength=jitter
    )
    return {
        "sequential_draw": seq, 
        "yielded_numbers": main_numbers,
        "strong_number": strong_number
    }
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
from app.engine import generate_golden_numbers

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.head("/")
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# --- NEW ENDPOINT: Fetch Next Sequence ---
@app.get("/api/next-sequence")
async def get_next_sequence():
    try:
        # Check if the file exists before trying to read it
        if os.path.exists("historical_data.csv"):
            df = pd.read_csv("historical_data.csv")
            # Find the absolute highest sequence number in the file
            highest_seq = int(df['draw_seq'].max())
            return {"next_sequence": highest_seq + 1}
        else:
            return {"next_sequence": 1} # Fallback if file is missing
    except Exception as e:
        print(f"Error reading sequence: {e}")
        return {"next_sequence": 1} # Fallback on read error
@app.get("/api/auto-tune")
async def auto_tune_jitter(seq: int):
    try:
        # We want to backtest the PREVIOUS draw to calibrate for the CURRENT one
        past_seq = seq - 1 
        
        df = pd.read_csv(HISTORICAL_FILE)
        past_draw = df[df['draw_seq'] == past_seq]
        
        if past_draw.empty:
            return {"optimal_jitter": 0.10, "message": "Previous sequence not found. Defaulting."}
            
        # Extract the real historical numbers
        real_numbers = set(past_draw.iloc[0][['p1', 'p2', 'p3', 'p4', 'p5', 'p6']].values)
        real_strong = past_draw.iloc[0]['strong_num']
        
        best_jitter = 0.00
        highest_score = -1
        
        # Sweep the Golden Wave from 0.00 to 1.61 in steps of 0.05
        for j in np.arange(0.00, 1.62, 0.05):
            current_jitter = round(j, 2)
            total_score = 0
            
            # Sample 3 times per jitter to account for quantum variance
            for _ in range(3):
                main_nums, strong = generate_golden_numbers(
                    HISTORICAL_FILE, QUANTUM_FILE, past_seq, current_jitter
                )
                
                # Scoring System: +1 for main numbers, +3 for strong number
                matches = len(set(main_nums).intersection(real_numbers))
                total_score += matches
                if strong == real_strong:
                    total_score += 3
                    
            # Keep track of the highest scoring jitter
            if total_score > highest_score:
                highest_score = total_score
                best_jitter = current_jitter
                
        return {"optimal_jitter": best_jitter, "score": highest_score}
        
    except Exception as e:
        print(f"Auto-tune error: {e}")
        return {"optimal_jitter": 0.10, "message": "Error calculating. Defaulting."}

@app.get("/api/draw")
async def get_draw(seq: int, jitter: float = 0.1):
    main_numbers, strong_number = generate_golden_numbers(
        historical_data_path="historical_data.csv", 
        quantum_csv_path="quantum_seed.csv",
        next_draw_seq=seq, 
        jitter_strength=jitter
    )
    return {
        "sequential_draw": seq, 
        "yielded_numbers": main_numbers,
        "strong_number": strong_number
    }
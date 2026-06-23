from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

# THE FIX: Importing the newly named physics function
from app.engine import simulate_kinematic_draw

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# File Configurations
HISTORICAL_FILE = "historical_data.csv" 
QUANTUM_FILE = "quantum_seed.csv"

@app.get("/")
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

# THE FIX: Updated endpoint to accept the new physical Hz parameters
@app.get("/api/draw")
async def get_draw(seq: int, motor: float = 0.75, kinetic: float = 3.14):
    try:
        main_numbers, strong_number = simulate_kinematic_draw(
            historical_data_path=HISTORICAL_FILE, 
            quantum_csv_path=QUANTUM_FILE,
            next_draw_seq=seq, 
            motor_hz=motor,
            kinetic_hz=kinetic
        )
        return {
            "sequential_draw": seq, 
            "yielded_numbers": main_numbers,
            "strong_number": strong_number
        }
    except Exception as e:
        print(f"Draw calculation error: {e}")
        return {"error": str(e)}
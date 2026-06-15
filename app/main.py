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
        if os.path.exists("mock_historical_data.csv"):
            df = pd.read_csv("mock_historical_data.csv")
            # Find the absolute highest sequence number in the file
            highest_seq = int(df['draw_seq'].max())
            return {"next_sequence": highest_seq + 1}
        else:
            return {"next_sequence": 1} # Fallback if file is missing
    except Exception as e:
        print(f"Error reading sequence: {e}")
        return {"next_sequence": 1} # Fallback on read error

@app.get("/api/draw")
async def get_draw(seq: int, jitter: float = 0.1):
    main_numbers, strong_number = generate_golden_numbers(
        historical_data_path="mock_historical_data.csv", 
        quantum_csv_path="quantum_seed.csv",
        next_draw_seq=seq, 
        jitter_strength=jitter
    )
    return {
        "sequential_draw": seq, 
        "yielded_numbers": main_numbers,
        "strong_number": strong_number
    }
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.engine import simulate_kinematic_draw
import os

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Only the Quantum Seed is required for the Kinematic Engine
QUANTUM_FILE = "quantum_seed.csv"

@app.get("/")
async def read_item(request: Request):
    # Using explicit keyword arguments to avoid Starlette/Jinja2 hashing errors
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/draw")
async def get_draw(motor: float = 0.75, kinetic: float = 3.14):
    try:
        # We pass dummy values (0, "") for parameters no longer needed by the physics engine
        main_numbers, strong_number = simulate_kinematic_draw(
            historical_data_path="", 
            quantum_csv_path=QUANTUM_FILE,
            next_draw_seq=0, 
            motor_hz=motor,
            kinetic_hz=kinetic
        )
        return {
            "yielded_numbers": main_numbers,
            "strong_number": strong_number
        }
    except Exception as e:
        print(f"[API ERROR] Draw calculation failed: {e}")
        return {"error": "Engine Failure", "details": str(e)}
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.engine import simulate_kinematic_draw

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# We only need the quantum seed now!
QUANTUM_FILE = "quantum_seed.csv"

@app.get("/")
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/draw")
async def get_draw(motor: float = 0.75, kinetic: float = 3.14):
    try:
        # We pass 0 and "" to the old sequence/historical parameters so engine.py doesn't crash
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
        print(f"Draw calculation error: {e}")
        return {"error": str(e)}
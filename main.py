from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import json, tempfile, traceback
from fastapi.middleware.cors import CORSMiddleware
from data_handling import get_combined_dataframe
from output_formatting import get_final_statistics, construct_json, return_to_mainframe

app = FastAPI()

origins = [
    "http://localhost:5000",   # Next.js dev server
    "https://zerorain.vercel.app",  # production frontend (replace with real domain)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # only allow these origins
    allow_credentials=True,     # allow cookies / auth headers
    allow_methods=["*"],        # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],        # allow all headers (Content-Type, Authorization, etc.)
)

class Data(BaseModel):
    target_date: str
    lat: float
    lon: float
    days: int = 2
    years: int = 2


@app.post('/')
def results(data: Data):
    vector_data, yearly_data = get_combined_dataframe(data.lat, data.lon, data.target_date, data.days, data.years)
    final_stats = get_final_statistics(vector_data)
    full_json, yearly_json = construct_json(vector_data, yearly_data, final_stats)

    #Save them in FastAPI's app state (in-memory)
    app.state.full_json = full_json
    app.state.yearly_json = yearly_json
    app.state.final_stats = final_stats

    return return_to_mainframe(final_stats)


@app.get('/full_json/download')
def download_full_json():

    # Retrieve stored data
    full_json = getattr(app.state, "full_json", None)


    # If data not ready, show error
    if not full_json:
        return JSONResponse(
            content={"error": "No processed data available. Run the POST endpoint first."},
            status_code=400
        )

    try:
        data = json.loads(full_json)  

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as temp_file:
            json.dump(data, temp_file, indent=4)
            temp_path = temp_file.name

        return FileResponse(
            path=temp_path,
            filename="full_json.json",
            media_type="application/json"
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.get('/yearly_data/download')
def download_yearly_json():

    # Retrieve stored data
    yearly_json = getattr(app.state, "yearly_json", None)


    # If data not ready, show error
    if not yearly_json:
        return JSONResponse(
            content={"error": "No processed data available. Run the POST endpoint first."},
            status_code=400
        )

    try:
        data = json.loads(yearly_json)  

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as temp_file:
            json.dump(data, temp_file, indent=4)
            temp_path = temp_file.name

        return FileResponse(
            path=temp_path,
            filename="yearly_data.json",
            media_type="application/json"
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )



def main():
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
if __name__ == "_main_":
    main()
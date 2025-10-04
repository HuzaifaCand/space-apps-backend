from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
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
    """
    Main entry point for the weather analysis program.
    ------
    """
    vector_data, yearly_data = get_combined_dataframe(data.lat, data.lon, data.target_date, data.days, data.years)
    final_stats = get_final_statistics(vector_data)
    full_json, yearly_json = construct_json(vector_data, yearly_data, final_stats)

    acc_final_stats = return_to_mainframe(final_stats)

    return({"finalStats": acc_final_stats, "fullJson": full_json, "yearlyJson": yearly_json})

def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
if __name__ == "_main_":
    main()
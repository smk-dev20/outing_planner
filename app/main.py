import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datatypes import RequestBody
from app_service import geocode, geo_get_places
from llm_service import llm_extract_outing_info, llm_summarize_places

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.post("/plan_outing")
def plan_outing(req: RequestBody):
    try:
        user_text = req.text

        # Use LLM to extract outing info from user text. Example usage
        #user_text = "Looking for stroller-friendly parks near San Jose, California with shaded areas."
        output = llm_extract_outing_info(user_text)
        if output is None:
            return {"error": "Failed to extract outing info"}

        city = output["city"]
        state = output["state"]
        drive_time_max = output["drive_time_max"]

        # Obtain lat and long from city and state
        lat, lon = geocode(city, state)
        if lat is None or lon is None:
            return {"error": "Failed to geocode city and state"}

        output["lat"] = lat
        output["lon"] = lon

        # From lat and long, get places
        if drive_time_max is None:
            drive_time_max = 45
        distance = drive_time_max * 60 * 12.5 #assume 12.5 m/s avg speed * 60 seconds per minute
        places = geo_get_places(lat, lon, distance)
        if places is None or len(places) == 0:
            return {"error": "Failed to get places"}

        # Summarize places
        places_summary = llm_summarize_places(user_text, places)
        if places_summary is None:
            return {"error": "Failed to summarize places"}

        return {"result": places_summary}

    except KeyError as e:
        return {"error": f"Missing key in output: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


@app.get("/")
def start(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

if __name__ == "__main__":  
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
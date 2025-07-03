import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datatypes import RequestBody
from app_service import geocode, geo_get_places
from llm_service import llm_extract_outing_info, llm_summarize_places
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.post("/plan_outing")
def plan_outing(req: RequestBody):
    try:
        user_text = req.text
        logger.info(f'Received user input: {user_text}')
        # Use LLM to extract outing info from user text. Example usage
        #user_text = "Looking for stroller-friendly parks near San Jose, California with shaded areas."
        output = llm_extract_outing_info(user_text)
        if output is None or len(output) == 0:
            logger.error('Failed to extract outing info')
            return {"error": "Something went wrong, please try again"}

        city = output["city"]
        state = output["state"]
        drive_time_max = output["drive_time_max"]
        if city is None or state is None:
            logger.error('Failed to extract city and state')
            return {"error": "Something went wrong, please try again:"}
        logger.info(f'Extracted city: {city}, state: {state}, drive_time_max: {drive_time_max}, user_text: {user_text}')
        # Obtain lat and long from city and state
        lat, lon = geocode(city, state)
        logger.info(f'Geocoded lat: {lat}, lon: {lon}')
        if lat is None or lon is None:
            logger.error('Failed to geocode city and state')
            return {"error": "Something went wrong, please try again:"}

        output["lat"] = lat
        output["lon"] = lon

        # From lat and long, get places
        if drive_time_max is None:
            drive_time_max = 45
        distance = drive_time_max * 60 * 12.5 #assume 12.5 m/s avg speed * 60 seconds per minute
        places = geo_get_places(lat, lon, distance)
        logger.info(f'Got places: {places}')
        if places is None or len(places) == 0:
            logger.error('Failed to get places')
            return {"error": "Something went wrong, please try again:"}

        # Summarize places
        places_summary = llm_summarize_places(user_text, places)
        logger.info(f'Summarized places: {places_summary}')
        if places_summary is None:
            logger.error('Failed to summarize places')
            return {"error": "Something went wrong, please try again:"}

        return {"result": places_summary}

    except KeyError as e:
        logger.error(f'Missing key in output: {e}')
        return {"error": f"Something went wrong, please try again"}
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return {"error": f"Something went wrong, please try again"}


@app.get("/")
def start(request: Request):
    try:
        logger.info('Serving index page')
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return {"error": "Something went wrong, please try again:"}

if __name__ == "__main__":  
    logger.info('Starting server')
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
import requests
from config import Config
import logging
import json

def geocode(city, state):
    try:
        geourl = Config.GEO_CODE_URL
        r = requests.get(geourl, params={"city": city, "state": state, "apiKey": Config.GEO_KEY})
        rj = r.json()["features"][0]["geometry"]["coordinates"]
        return rj[1], rj[0]
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to geocode: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

def geo_get_places(lat, lon, distance=12.5 *3600):
    try:
        params = {
            "categories": Config.GEO_CATEGORIES,
            "filter": f"circle:{lon},{lat},{distance}",
            "conditions": Config.GEO_CONDITIONS,
            "apiKey": Config.GEO_KEY,
            "limit": 10
        }
        places = requests.get(Config.GEO_PLACES_URL, params=params).json().get("features", [])
        return places
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get places: {e}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return []
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []
from pydantic import BaseModel
# Define request schema
class RequestBody(BaseModel):
    text: str
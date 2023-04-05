import requests
import os

api_port = os.environ.get("API_PORT")
api_url  = f"http://localhost:{api_port}"
requests.get(f"{api_url}")
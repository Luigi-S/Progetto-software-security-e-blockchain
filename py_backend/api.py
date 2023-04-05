from flask import Flask
import os
import json
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
port = os.environ.get("API_PORT")
manager_addr = str(os.environ.get("MANAGER_ADDRESS"))
manager_abi = json.load(open("abi/Manager.json","r"))

@app.route('/')
def hello():
  return "Hello World"

@app.route('/manager_addr')
def get_manager_addr():
  return manager_addr
  
@app.route('/manager_abi')
def get_manager_abi():
  return manager_abi


if __name__ == "__main__":
  print(f"API running on port {port}")   
  app.run(host='0.0.0.0', port = port)
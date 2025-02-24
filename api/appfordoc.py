import sys
import os

# Add the directory of flask_api.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flasgger import Swagger
import flask_api

# ✅ Initialize Swagger
swagger = Swagger(flask_api.app)

if __name__ == "__main__":
    flask_api.app.run(debug=True, host="0.0.0.0", port=5001)


# run python appfordoc.py
# go to http://127.0.0.1:5001/apidocs


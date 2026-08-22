import os
import sys
import uvicorn

# Add project root and App/ directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.main import app

if __name__ == "__main__":
    print("Starting NOVA Agent Application Server on http://localhost:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

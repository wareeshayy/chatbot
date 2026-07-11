import sys
from pathlib import Path

# Add backend directory to python path to resolve imports (Force Vercel Rebuild v1)
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_dir))

from app.main import app

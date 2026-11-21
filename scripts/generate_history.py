from __future__ import annotations

import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
backend = root / 'backend'
sys.path.insert(0, str(backend))

from app.services.demo_seed import generate_demo_data


if __name__ == '__main__':
    data = generate_demo_data()
    print(f"Generated {len(data['products'])} products and {len(data['history'])} historical observations.")

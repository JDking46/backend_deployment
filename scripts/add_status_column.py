import os
import sys
from sqlalchemy import text

# Ensure project root is on sys.path so `db` package can be imported
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

from db.session import engine

sql = """
ALTER TABLE help_request
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending' NOT NULL;
"""

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Ensured column `status` exists on help_request.")

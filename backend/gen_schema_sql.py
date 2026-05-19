"""Generate SQL DDL from SQLAlchemy models for Supabase SQL Editor."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.db.models import Base

sql = "-- Resume Optimizer Database Schema\n"
sql += "-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/jbdaabtcektgxtblwoow/sql/new\n\n"

# Generate CREATE TABLE statements
from sqlalchemy.schema import CreateTable

for table in Base.metadata.sorted_tables:
    create_sql = str(CreateTable(table).compile(
        dialect=__import__('sqlalchemy.dialects.postgresql', fromlist=['dialect']).dialect()
    ))
    sql += create_sql + ";\n\n"

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'supabase', 'schema.sql')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(sql)

print(f'[OK] Schema SQL written to: {output_path}')
print(f'Content:\n{sql}')

"""
Supabase client for the resume-optimizer backend.
Uses Supabase REST API (HTTPS) — works behind firewalls where direct PG is blocked.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jbdaabtcektgxtblwoow.supabase.co")
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "sb_publishable_ZD6SOtJzzFk6DpB9eJuW9g_Hx4CW-xd",
)

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create the Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# Re-export for convenience
supabase: Client = get_supabase_client()

from app.database.connection import get_db, check_db_connection
from app.database.queries import (
    get_synonyms_for_word,
    get_all_synonyms,
    get_all_synonyms_query,
    add_synonym_query,
    get_all_services
)

__all__ = [
    "get_db",
    "check_db_connection",
    "get_synonyms_for_word",
    "get_all_synonyms",
    "get_all_synonyms_query",
    "add_synonym_query",
    "get_all_services"
]

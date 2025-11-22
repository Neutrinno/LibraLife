from app.database.connection import get_db_connection, init_db_pool, close_db_pool
from app.database.queries import (
    get_synonyms_for_word,
    get_all_synonyms,
    get_all_synonyms_query,
    add_synonym_query,
    get_all_services  # Не search_lots_query!
)

__all__ = [
    "get_db_connection",
    "init_db_pool",
    "close_db_pool",
    "get_synonyms_for_word",
    "get_all_synonyms",
    "get_all_synonyms_query",
    "add_synonym_query",
    "get_all_services"
]
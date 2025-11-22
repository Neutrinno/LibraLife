"""
Минимальный препроцессинг для базовой нормализации текста.
Typesense самостоятельно обрабатывает морфологию, опечатки и т.д.
"""
import re
from typing import List
import logging

logger = logging.getLogger(__name__)

def preprocess_text(text: str) -> List[str]:
    """
    Минимальная предобработка текста.
    
    Args:
        text: Исходный текст
        
    Returns:
        Список слов
    """
    if not text or not isinstance(text, str):
        return []
    
    try:
        # Базовая очистка
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Разбиваем на слова
        words = text.split()
        
        return words
        
    except Exception as e:
        logger.error(f"Error preprocessing text: {e}")
        return []
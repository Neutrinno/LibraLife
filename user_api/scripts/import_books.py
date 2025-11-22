"""
Скрипт для импорта книг из CSV/JSON файла в базу данных.

Использование:
    python scripts/import_books.py --file path/to/books.csv --format csv
    python scripts/import_books.py --file path/to/books.json --format json
"""
import asyncio
import argparse
import csv
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Добавляем корневую директорию user_api в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.models import Book


def normalize_value(value: Any, field_type: str) -> Optional[Any]:
    """Нормализация значений из датасета"""
    if value is None or value == "":
        return None
    
    # Обработка строковых значений "Unknown", "No description", "No rating"
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in ["unknown", "unknown author", "unknown genre", "unknown publisher", 
                            "no description available", "no description", "no rating"]:
            return None
    
    # Преобразование типов
    if field_type == "int":
        try:
            return int(float(value)) if value else None
        except (ValueError, TypeError):
            return None
    elif field_type == "float":
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    elif field_type == "str":
        return str(value) if value else None
    
    return value


def parse_csv_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Парсинг строки CSV в словарь для создания Book"""
    title = normalize_value(row.get("title", ""), "str")
    author = normalize_value(row.get("author", ""), "str")
    category = normalize_value(row.get("genre", ""), "str")  # genre -> category
    
    # Обрезаем длинные значения до лимитов модели
    if title and len(title) > 200:
        title = title[:197] + "..."
    if author and len(author) > 200:
        author = author[:197] + "..."
    if category and len(category) > 100:
        category = category[:97] + "..."
    
    return {
        "title": title,
        "author": author,
        "category": category,
        "description": normalize_value(row.get("description", ""), "str"),
        "is_available": True,  # По умолчанию все книги доступны
    }


def parse_json_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Парсинг элемента JSON в словарь для создания Book"""
    title = normalize_value(item.get("title", ""), "str")
    author = normalize_value(item.get("author", ""), "str")
    category = normalize_value(item.get("genre", ""), "str")  # genre -> category
    
    # Обрезаем длинные значения до лимитов модели
    if title and len(title) > 200:
        title = title[:197] + "..."
    if author and len(author) > 200:
        author = author[:197] + "..."
    if category and len(category) > 100:
        category = category[:97] + "..."
    
    return {
        "title": title,
        "author": author,
        "category": category,
        "description": normalize_value(item.get("description", ""), "str"),
        "is_available": True,
    }


async def import_books_from_file(file_path: str, file_format: str, batch_size: int = 100) -> None:
    """Импорт книг из файла в базу данных"""
    books_data: List[Dict[str, Any]] = []
    
    print(f"Чтение файла: {file_path}")
    
    # Чтение данных из файла
    if file_format.lower() == "csv":
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                book_data = parse_csv_row(row)
                # Пропускаем записи без обязательных полей
                if book_data["title"] and book_data["author"]:
                    books_data.append(book_data)
    
    elif file_format.lower() == "json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Если это список
            if isinstance(data, list):
                for item in data:
                    book_data = parse_json_item(item)
                    if book_data["title"] and book_data["author"]:
                        books_data.append(book_data)
            # Если это словарь с ключом, содержащим список
            elif isinstance(data, dict):
                # Ищем первый список в словаре
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            book_data = parse_json_item(item)
                            if book_data["title"] and book_data["author"]:
                                books_data.append(book_data)
                        break
    
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {file_format}")
    
    print(f"Загружено {len(books_data)} книг из файла")
    
    # Импорт в базу данных батчами
    async with async_session_maker() as session:
        imported = 0
        skipped = 0
        
        for i in range(0, len(books_data), batch_size):
            batch = books_data[i:i + batch_size]
            books_to_add = []
            
            for book_data in batch:
                # Проверяем, существует ли уже книга с таким title и author
                existing = await session.execute(
                    sa.select(Book).where(
                        Book.title == book_data["title"],
                        Book.author == book_data["author"]
                    ).limit(1)
                )
                if existing.first():
                    skipped += 1
                    continue
                
                book = Book(**book_data)
                books_to_add.append(book)
            
            if books_to_add:
                session.add_all(books_to_add)
                await session.commit()
                imported += len(books_to_add)
                print(f"Импортировано {imported} книг (пропущено {skipped})...")
        
        print(f"\nИмпорт завершен!")
        print(f"Всего импортировано: {imported}")
        print(f"Пропущено дубликатов: {skipped}")


async def main():
    parser = argparse.ArgumentParser(description="Импорт книг из CSV/JSON в базу данных")
    parser.add_argument("--file", "-f", required=True, help="Путь к файлу с данными")
    parser.add_argument("--format", "-t", choices=["csv", "json"], required=True, help="Формат файла (csv или json)")
    parser.add_argument("--batch-size", "-b", type=int, default=100, help="Размер батча для импорта (по умолчанию 100)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Ошибка: файл {args.file} не найден")
        sys.exit(1)
    
    try:
        await import_books_from_file(args.file, args.format, args.batch_size)
    except Exception as e:
        print(f"Ошибка при импорте: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


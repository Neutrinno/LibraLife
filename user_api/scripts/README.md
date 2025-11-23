# Скрипты импорта данных

## Импорт книг

Скрипт `import_books.py` позволяет импортировать книги из CSV или JSON файла в базу данных.

### Подготовка

1. Убедитесь, что выполнена миграция базы данных:
   ```bash
   alembic upgrade head
   ```

2. Убедитесь, что файл `.env` содержит правильные настройки подключения к БД.

### Использование

#### Импорт из CSV:
```bash
python scripts/import_books.py --file path/to/books.csv --format csv
```

#### Импорт из JSON:
```bash
python scripts/import_books.py --file path/to/books.json --format json
```

#### С указанием размера батча:
```bash
python scripts/import_books.py --file books.csv --format csv --batch-size 200
```

### Формат данных

Скрипт ожидает следующие поля в файле:

- `title` (обязательно) - Название книги
- `author` (обязательно) - Автор книги
- `genre` - Жанр/категория (маппится в `category`)
- `description` - Описание книги

Остальные поля из датасета (pages, published_date, publisher, language, average_rating, ratings_count, thumbnail) будут проигнорированы.

### Особенности

- Скрипт автоматически нормализует значения: "Unknown", "No description", "No rating" преобразуются в `NULL`
- Проверяет дубликаты по комбинации `title` + `author`
- Импортирует данные батчами для оптимизации производительности
- Пропускает записи без обязательных полей (`title` или `author`)


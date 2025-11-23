import os
from datetime import datetime
from docx import Document
from fastapi.responses import StreamingResponse
import io
import uuid


class EventDocumentGenerator:
    def generate_event_report(self, event_data: dict) -> io.BytesIO:
        """
        Генерирует документ мероприятия в формате DOCX в памяти
        """
        doc = Document()

        # Заголовок
        title = doc.add_heading('ОТЧЕТ О МЕРОПРИЯТИИ', 0)
        title.alignment = 1  # Центрирование

        doc.add_paragraph()  # Пустая строка

        # Основная информация
        formatted_date = self._parse_timestamp(event_data.get('date', ''))
        self._add_field(doc, "ДАТА ПРОВЕДЕНИЯ", formatted_date)
        self._add_field(doc, "ФОРМА МЕРОПРИЯТИЯ", event_data.get('event_type', 'Мероприятие'))
        self._add_field(doc, "НАЗВАНИЕ МЕРОПРИЯТИЯ", event_data.get('title', ''))
        doc.add_paragraph()  # Пустая строка

        self._add_field(doc, "МЕСТО ПРОВЕДЕНИЯ", event_data.get('location', 'Не указано'))
        self._add_field(doc, "КОЛ-ВО ПРИСУТСТВУЮЩИХ", str(event_data.get('participants_count', 0)))

        # Документы по отраслям знания
        documents_info = event_data.get('documents_info', 'Не предоставлено')
        self._add_field(doc, "КОЛ-ВО ПРЕДОСТАВЛЕННЫХ/ВЫДАННЫХ ДОКУМЕНТОВ, в т.ч. по отраслям знания", documents_info)

        doc.add_paragraph()  # Пустая строка

        # Содержание мероприятия
        content_heading = doc.add_paragraph()
        content_heading.add_run("СОДЕРЖАНИЕ И СОСТАВНЫЕ ЧАСТИ МЕРОПРИЯТИЯ:").bold = True

        content = event_data.get('content', 'Содержание не указано')
        content_paragraph = doc.add_paragraph()
        for line in content.split('\n'):
            if line.strip():  # Пропускаем пустые строки
                content_paragraph.add_run(line)
                content_paragraph.add_run().add_break()

        doc.add_paragraph()  # Пустая строка

        # Участники подготовки
        organizers_heading = doc.add_paragraph()
        organizers_heading.add_run(
            "Ф.И.О., ОРГАНИЗАЦИЯ, участвующие в подготовке и проведении мероприятия:").bold = True

        organizers = event_data.get('organizers', 'Не указаны')
        organizers_paragraph = doc.add_paragraph()
        for line in organizers.split('\n'):
            if line.strip():  # Пропускаем пустые строки
                organizers_paragraph.add_run(line)
                organizers_paragraph.add_run().add_break()

        doc.add_paragraph()  # Пустая строка

        # Библиотекарь
        self._add_field(doc, "Ф.И.О. БИБЛИОТЕКАРЯ, проводившего мероприятие", event_data.get('librarian', 'Не указан'))

        # Сохраняем в память
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)

        return file_stream

    def _add_field(self, doc, field_name: str, field_value: str):
        """
        Добавляет поле в документ
        """
        paragraph = doc.add_paragraph()
        run = paragraph.add_run(f"{field_name} ")
        run.bold = True
        paragraph.add_run(field_value)

    def _parse_timestamp(self, timestamp_str: str) -> str:
        """
        Парсит UNIX timestamp строку в читаемый формат даты
        """
        if not timestamp_str:
            return "Не указана"

        try:
            # Преобразуем строку в число
            timestamp_int = int(timestamp_str)

            # Проверяем, это секунды или миллисекунды
            if timestamp_int > 9999999999:  # Если больше ~2001 года в миллисекундах
                timestamp_int = timestamp_int // 1000  # Конвертируем в секунды

            # Преобразуем UNIX timestamp в datetime объект
            dt = datetime.fromtimestamp(timestamp_int)

            # Форматируем в русский формат: "20 января 2024 года, 15:30"
            months = {
                1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
                5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
                9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
            }

            day = dt.day
            month = months[dt.month]
            year = dt.year
            time = dt.strftime('%H:%M')

            return f"{day} {month} {year} года, {time}"

        except (ValueError, TypeError, OSError):
            # В случае ошибки возвращаем оригинальную строку
            return timestamp_str
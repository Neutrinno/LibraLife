--- Включаем расширение для генерации UUID, если оно еще не включено
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создаем перечисляемые типы (ENUM) для ролей, категорий и статусов
DO $$ BEGIN
    CREATE TYPE role AS ENUM ('ADMIN','SUPPLIER','TENANT');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE service_category AS ENUM ('SOLAR','WIND','HYDRO','STORAGE','OTHER');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE rental_request_status AS ENUM ('PENDING','APPROVED','REJECTED','CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM ('SYSTEM','RENTAL','CHAT','OTHER');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Таблица пользователей (users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role role NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    inn VARCHAR(64) UNIQUE,
    phone VARCHAR(64),
    address VARCHAR(512),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица услуг/мощностей (services)
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category service_category NOT NULL,
    price_per_day NUMERIC(19,2) NOT NULL,
    location VARCHAR(255),
    capacity VARCHAR(100),
    technical_specs TEXT,
    supplier_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    supplier_name VARCHAR(255),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица доступности услуг (service_availability)
CREATE TABLE IF NOT EXISTS service_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    available BOOLEAN NOT NULL DEFAULT true
);

-- Таблица аренд (rentals)
CREATE TABLE IF NOT EXISTS rentals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    service_title VARCHAR(200),
    supplier_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    supplier_name VARCHAR(255),
    tenant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_name VARCHAR(255),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_price NUMERIC(19,2) NOT NULL,
    chat_id UUID,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица заявок на аренду (rental_requests)
CREATE TABLE IF NOT EXISTS rental_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    service_title VARCHAR(200),
    tenant_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_name VARCHAR(255),
    tenant_inn VARCHAR(64),
    tenant_email VARCHAR(255),
    tenant_phone VARCHAR(64),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_price NUMERIC(19,2),
    message TEXT,
    status rental_request_status NOT NULL DEFAULT 'PENDING',
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    responded_at TIMESTAMPTZ
);

-- Таблица чатов (chats)
CREATE TABLE IF NOT EXISTS chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rental_id UUID REFERENCES rentals(id) ON DELETE SET NULL,
    supplier_id UUID REFERENCES users(id) ON DELETE SET NULL,
    supplier_name VARCHAR(255),
    tenant_id UUID REFERENCES users(id) ON DELETE SET NULL,
    tenant_name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица сообщений в чатах (chat_messages)
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    sender_name VARCHAR(255),
    content TEXT NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица уведомлений (notifications)
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type notification_type NOT NULL,
    title VARCHAR(255),
    message TEXT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица синонимов (для поиска)
CREATE TABLE IF NOT EXISTS synonyms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    word VARCHAR(255) NOT NULL,
    synonym VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT unique_synonym UNIQUE (word, synonym)
);

-- Индекс для быстрого поиска по основному слову
CREATE INDEX IF NOT EXISTS idx_synonyms_word ON synonyms(LOWER(word));

-- Тестовые синонимы
INSERT INTO synonyms (word, synonym) VALUES
    ('трактор', 'мтз'),
    ('трактор', 'беларус'),
    ('станок', 'чпу'),
    ('фрезерный', 'станок'),
    ('упаковка', 'фасовка')
ON CONFLICT (word, synonym) DO NOTHING;

-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_services_supplier ON services(supplier_id);
CREATE INDEX IF NOT EXISTS idx_services_category ON services(category);
CREATE INDEX IF NOT EXISTS idx_service_availability_service ON service_availability(service_id, date);
CREATE INDEX IF NOT EXISTS idx_rentals_service ON rentals(service_id);
CREATE INDEX IF NOT EXISTS idx_rentals_tenant ON rentals(tenant_id);
CREATE INDEX IF NOT EXISTS idx_rental_requests_service ON rental_requests(service_id);
CREATE INDEX IF NOT EXISTS idx_rental_requests_tenant ON rental_requests(tenant_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat ON chat_messages(chat_id, sent_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, created_at);
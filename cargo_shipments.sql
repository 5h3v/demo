-- Creating table for users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, -- Plain text password
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL, -- Format: +7(XXX)-XXX-XX-XX
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creating table for cargo shipment requests
CREATE TABLE cargo_shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    shipment_date TIMESTAMP NOT NULL, -- Дата и время заявки
    cargo_weight DECIMAL(10, 2) NOT NULL, -- Вес груза в кг
    cargo_type TEXT NOT NULL, -- Тип груза (например, "Паллеты", "Сыпучие", "Жидкости")
    origin_address TEXT NOT NULL, -- Адрес отправления
    destination_address TEXT NOT NULL, -- Адрес доставки
    status TEXT CHECK(status IN ('pending', 'in_transit', 'delivered', 'cancelled')) DEFAULT 'pending', -- Статус заявки
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Дата создания записи
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert sample data with plain text passwords
INSERT INTO users (login, password, full_name, phone, email) VALUES
('testuser', 'password', 'Иванов Иван', '+7(999)-123-45-67', 'test@example.com'),
('admin', 'gruzovik2024', 'Администратор', '+7(999)-000-00-00', 'admin@example.com');
INSERT INTO cargo_shipments (user_id, shipment_date, cargo_weight, cargo_type, origin_address, destination_address) VALUES
(1, '2025-06-17 01:02:00', 500.50, 'Паллеты', 'ул. Центральная 10, Москва', 'пр. Ленина 5, Санкт-Петербург'),
(1, '2025-06-18 09:15:00', 1200.75, 'Сыпучие', 'ул. Промышленная 3, Екатеринбург', 'ул. Заводская 12, Новосибирск');
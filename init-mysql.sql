CREATE DATABASE IF NOT EXISTS reservation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS paiement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE reservation_db;

CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_per_day DECIMAL(10,2) NOT NULL DEFAULT 100.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS reservations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_email VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    status ENUM('PENDING','CONFIRMED','CANCELLED') DEFAULT 'PENDING',
    nb_persons INT NOT NULL DEFAULT 1,
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_email),
    INDEX idx_category (category_id, start_date, end_date),
    FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_email VARCHAR(150),
    action VARCHAR(255) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_email),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

INSERT INTO categories (name, description, price_per_day) VALUES
('Hotel', 'Chambre d''hotel confortable', 120.00),
('Restaurant', 'Reservation de table restaurant', 50.00),
('Salle de conference', 'Salle equipee pour evenements', 200.00)
ON DUPLICATE KEY UPDATE name=name;

USE paiement_db;

CREATE TABLE IF NOT EXISTS paiements (
    id CHAR(36) NOT NULL,
    reservation_id INT NOT NULL,
    montant DECIMAL(10,2) NOT NULL,
    devise CHAR(3) NOT NULL DEFAULT 'EUR',
    methode VARCHAR(50) NOT NULL,
    statut ENUM('en_attente', 'valide', 'refuse', 'rembourse') NOT NULL DEFAULT 'en_attente',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_reservation_id (reservation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    paiement_id CHAR(36),
    action VARCHAR(255) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_paiement (paiement_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

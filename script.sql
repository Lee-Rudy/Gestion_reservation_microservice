-- user-service
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role ENUM('USER','ADMIN') DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- auth-service
CREATE TABLE auth_tokens (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

CREATE TABLE logs (
    id CHAR(36) PRIMARY KEY,               
    correlation_id CHAR(36) NOT NULL,          
    action VARCHAR(50) NOT NULL,                  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correlation (correlation_id) 
) ENGINE=InnoDB;

-- reservation-service
CREATE TABLE categories (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE reservations (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    category_id CHAR(36) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    status ENUM('PENDING','CONFIRMED','CANCELLED') DEFAULT 'PENDING',
    expires_at DATETIME,
    version INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_category (category_id, start_date, end_date)
) ENGINE=InnoDB;

CREATE TABLE logs (
    id CHAR(36) PRIMARY KEY,               
    correlation_id CHAR(36) NOT NULL,          
    action VARCHAR(50) NOT NULL,                  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correlation (correlation_id) 
) ENGINE=InnoDB;

CREATE TABLE notification_reservation (
    id CHAR(36) PRIMARY KEY,
    reservation_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    type ENUM('RESERVATION') DEFAULT 'RESERVATION',
    content TEXT,
    status ENUM('PENDING','SENT','FAILED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME,
    INDEX idx_user (user_id),
    INDEX idx_reservation (reservation_id)
) ENGINE=InnoDB;

-- payment-service
CREATE TABLE payments (
    id CHAR(36) PRIMARY KEY,
    reservation_id CHAR(36) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('PENDING','SUCCESS','FAILED') DEFAULT 'PENDING',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_reservation (reservation_id)
) ENGINE=InnoDB;

CREATE TABLE logs (
    id CHAR(36) PRIMARY KEY,               
    correlation_id CHAR(36) NOT NULL,          
    action VARCHAR(50) NOT NULL,                  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correlation (correlation_id) 
) ENGINE=InnoDB;

CREATE TABLE notification_payment (
    id CHAR(36) PRIMARY KEY,
    payment_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    type ENUM('PAYMENT') DEFAULT 'PAYMENT',
    content TEXT,
    status ENUM('PENDING','SENT','FAILED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME,
    INDEX idx_user (user_id),
    INDEX idx_payment (payment_id)
) ENGINE=InnoDB;
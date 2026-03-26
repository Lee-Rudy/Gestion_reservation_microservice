-- auth-service
CREATE TABLE auth_tokens (
    id int PRIMARY KEY AUTO_INCREMENT,
    user_id CHAR(36) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

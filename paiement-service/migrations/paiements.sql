-- Migration : création de la table paiements
-- Base de données : paiement_db
-- Moteur : InnoDB / MySQL 8+
--
-- Les identifiants sont stockés en CHAR(36) pour conserver les UUID
-- du domaine. Le statut utilise un ENUM aligné sur les valeurs métier.

CREATE DATABASE IF NOT EXISTS paiement_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE paiement_db;

CREATE TABLE IF NOT EXISTS paiements (
    id             CHAR(36)     NOT NULL,
    reservation_id CHAR(36)     NOT NULL,
    montant        DECIMAL(10,2) NOT NULL,
    devise         CHAR(3)      NOT NULL,
    methode        VARCHAR(50)  NOT NULL,
    statut         ENUM(
                       'en_attente',
                       'valide',
                       'refuse',
                       'rembourse'
                   ) NOT NULL DEFAULT 'en_attente',
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_reservation_id (reservation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

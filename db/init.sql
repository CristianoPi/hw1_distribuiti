CREATE DATABASE IF NOT EXISTS users;
USE users;

-- CREATE TABLE IF NOT EXISTS users (
--     email VARCHAR(255) PRIMARY KEY,
--     ticker VARCHAR(255)
-- );

-- CREATE TABLE IF NOT EXISTS stock_prices (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     email VARCHAR(255),
--     ticker VARCHAR(255),
--     price FLOAT,
--     timestamp TIMESTAMP,
--     FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
-- );

CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    ticker VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME NOT NULL
);
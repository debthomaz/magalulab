CREATE TABLE clients (
    clientId INT AUTO_INCREMENT,
    name VARCHAR(255),
    email VARCHAR(255),
    PRIMARY KEY (clientId)
);

CREATE TABLE wishlist (
    clientId INT,
    productId INT,
    FOREIGN KEY (clientId) REFERENCES clients(clientId)
    ON DELETE CASCADE
);

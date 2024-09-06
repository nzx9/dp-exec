CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    price FLOAT NOT NULL,
    user_id uuid REFERENCES users(id)
);
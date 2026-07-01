import sqlite3

def create_database():

    connection = sqlite3.connect("spam_detection.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL,

            prediction TEXT NOT NULL,

            confidence REAL NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    connection.commit()

    connection.close()

    print("Database created successfully!")

if __name__ == "__main__":
    create_database()
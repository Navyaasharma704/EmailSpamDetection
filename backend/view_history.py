import sqlite3

connection = sqlite3.connect("spam_detection.db")

cursor = connection.cursor()

cursor.execute("SELECT * FROM prediction_history")

rows = cursor.fetchall()

if len(rows) == 0:
    print("No records found.")
else:
    for row in rows:
        print(row)

connection.close()
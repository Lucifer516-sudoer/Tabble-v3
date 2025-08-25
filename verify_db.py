import sqlite3

try:
    conn = sqlite3.connect('Tabble.db')
    cursor = conn.cursor()

    print("Querying for hotel 'Tabble Inn'...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hotels';")
    if cursor.fetchone() is None:
        print("Error: 'hotels' table does not exist.")
        exit(1)

    cursor.execute("SELECT hotel_name FROM hotels WHERE hotel_name = ?", ('Tabble Inn',))
    hotel = cursor.fetchone()

    if hotel:
        print(f"Success! Found hotel: {hotel[0]}")
        exit(0)
    else:
        print("Error: Sample hotel 'Tabble Inn' not found in the database.")
        exit(1)

except sqlite3.Error as e:
    print(f"Database error: {e}")
    exit(1)
finally:
    if conn:
        conn.close()

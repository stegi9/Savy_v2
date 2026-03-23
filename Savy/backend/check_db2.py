import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='Ciao1806@', database='savy_db')
    cursor = conn.cursor()
    cursor.execute("SELECT email, full_name, (SELECT COUNT(*) FROM transactions WHERE user_id=profiles.id) FROM profiles")
    print("USERS IN DATABASE:")
    for row in cursor.fetchall():
        print(f"Email: {row[0]}, Name: {row[1]}, Transactions: {row[2]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

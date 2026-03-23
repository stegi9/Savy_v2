import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='Ciao1806@', database='savy_db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM profiles WHERE email='stegi@gmail.com'")
    user_id = cursor.fetchone()[0]
    cursor.execute("SELECT description, amount, category, category_id, ai_confidence FROM transactions WHERE user_id=%s ORDER BY created_at DESC LIMIT 10", (user_id,))
    print("\\nTOP 10 TRANSACTIONS FOR stegi@gmail.com:")
    for row in cursor.fetchall():
        print(f"Desc: {repr(row[0])} | Amt: {repr(row[1])} | Cat: {repr(row[2])} | Cat_ID: {repr(row[3])} | Conf: {repr(row[4])}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

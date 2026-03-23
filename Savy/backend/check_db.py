import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='Ciao1806@', database='savy_db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, created_at FROM profiles")
    users = cursor.fetchall()
    print(f"FOUND {len(users)} PROFILES IN WINDOWS savy_db:")
    for u in users:
        print(u)
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    tx_count = cursor.fetchone()[0]
    print(f"TOTAL TRANSACTIONS IN WINDOWS savy_db: {tx_count}")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")

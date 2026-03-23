import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='Ciao1806@', database='savy_db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM profiles WHERE email='stegi@gmail.com'")
    user_id = cursor.fetchone()[0]
    
    # Get all Cat_IDs from transactions
    cursor.execute("SELECT DISTINCT category_id FROM transactions WHERE user_id=%s", (user_id,))
    tx_cat_ids = [r[0] for r in cursor.fetchall() if r[0]]
    
    # Get all categories for user
    cursor.execute("SELECT id, name FROM user_categories WHERE user_id=%s", (user_id,))
    user_cats = {r[0]: r[1] for r in cursor.fetchall()}
    
    print(f"User has {len(user_cats)} categories registered.")
    
    missing = 0
    for cat_id in tx_cat_ids:
        if cat_id not in user_cats:
            missing += 1
            print(f"Transaction uses Cat_ID {cat_id} BUT it is missing from user_categories!")
        else:
            print(f"Cat_ID {cat_id} maps to -> {user_cats[cat_id]}")
            
    print(f"Total orphaned Category IDs: {missing}")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")

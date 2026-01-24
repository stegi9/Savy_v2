try:
    with open('verify_log_4.txt', 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading log: {e}")

#!/usr/bin/env python3
"""
Celery Queue Manager
--------------------
A command-line interface (CLI) tool to inspect, monitor, and clean up 
Celery queues stored in Redis.

Features:
- Scans all Redis databases (0-15) for active queues.
- Inspects JSON payloads of tasks.
- Supports purging entire queues.
- Supports selective deletion of tasks using wildcards (e.g., '*email*').

Created by: Machiel Broekman
"""
import sys
import redis
import json
import fnmatch
import os  # <--- Belangrijk voor os.getenv

# --- CONFIGURATION ---
# Haalt URL uit environment variabele, of gebruikt localhost als fallback
BASE_REDIS_URL = os.getenv('CELERY_REDIS_URL', 'redis://localhost:6379')

def scan_all_databases():
    """Scans Redis databases 0 through 15 for Lists (Celery queues)."""
    all_found_queues = []
    print(f"\n--- Scanning databases 0-15 on {BASE_REDIS_URL} ---")

    for db_num in range(16):
        try:
            current_url = f"{BASE_REDIS_URL}/{db_num}"
            r = redis.from_url(current_url, socket_timeout=0.5)
            
            try:
                if r.dbsize() == 0: continue
            except: pass

            for key in r.scan_iter("*"):
                try:
                    if r.type(key).decode('utf-8') == 'list':
                        key_name = key.decode('utf-8')
                        length = r.llen(key_name)
                        all_found_queues.append({
                            'db': db_num,
                            'name': key_name,
                            'count': length,
                            'connection': r
                        })
                except Exception:
                    pass
        except Exception:
            pass

    return all_found_queues

def get_task_name(task_bytes):
    try:
        task_data = json.loads(task_bytes.decode('utf-8'))
        headers = task_data.get('headers', {})
        name = headers.get('task')
        if not name:
            name = task_data.get('task')
        return name if name else "Unknown_Task"
    except:
        return "Unreadable_Data"

def purge_all_queues(queues):
    """Verwijdert ALLE gevonden queues in één keer."""
    total_items = sum(q['count'] for q in queues)
    queue_count = len(queues)
    
    print(f"\n🚨  WARNING: GLOBAL PURGE INITIATED 🚨")
    print(f"You are about to delete {queue_count} queues containing {total_items} tasks.")
    print("This action cannot be undone.")
    
    confirm = input("Type 'yes' to confirm deleting EVERYTHING: ")
    
    if confirm == 'yes':
        print("Purging...")
        deleted_count = 0
        for q in queues:
            try:
                q['connection'].delete(q['name'])
                print(f" - Deleted: {q['name']} (DB {q['db']})")
                deleted_count += 1
            except Exception as e:
                print(f" - Failed to delete {q['name']}: {e}")
        print(f"✅ Done. {deleted_count} queues purged.")
    else:
        print("❌ Operation cancelled.")

def delete_tasks_by_pattern(r_conn, queue_name):
    print(f"\n--- Selective Delete from '{queue_name}' ---")
    pattern = input("Enter task name (or pattern like '*email*') to delete: ")
    if not pattern: return

    print("Scanning...")
    all_items = r_conn.lrange(queue_name, 0, -1)
    to_delete = []
    
    for item in all_items:
        t_name = get_task_name(item)
        if fnmatch.fnmatch(t_name, pattern):
            to_delete.append(item)

    if not to_delete:
        print(f"No matches for '{pattern}'.")
        return

    print(f"Found {len(to_delete)} matches.")
    if input("Delete these tasks? (yes/no): ").lower() == 'yes':
        count = 0
        for raw_data in to_delete:
            if r_conn.lrem(queue_name, 0, raw_data) > 0:
                count += 1
        print(f"✅ {count} tasks removed.")
    else:
        print("Cancelled.")

def main():
    print("Starting Celery Queue Manager...")
    
    while True:
        queues = scan_all_databases()

        if not queues:
            print("\n❌ No queues found. Check connection or try later.")
            # We breaken niet hier, zodat de gebruiker 'r' kan doen na een retry
            if input("Retry? (y/n): ").lower() != 'y':
                break
            else:
                continue

        print("\n--- Found Queues ---")
        for i, q in enumerate(queues):
            print(f"{i + 1}. [DB {q['db']}] {q['name']:<30} (Items: {q['count']})")

        print("\nOptions:")
        print(" - Type a NUMBER to manage a specific queue")
        print(" - Type 'all' to PURGE ALL queues (Global Wipe)")
        print(" - Type 'r' to refresh")
        print(" - Type 'q' to quit")

        choice = input("\nChoice: ").lower()

        if choice == 'q':
            sys.exit()
        elif choice == 'r':
            continue
        elif choice == 'all':
            purge_all_queues(queues)
            input("\nPress Enter to continue...")
            continue
        
        try:
            idx = int(choice)
            if 1 <= idx <= len(queues):
                target = queues[idx - 1]
                r_conn = target['connection']
                q_name = target['name']
                
                print(f"\nSelected: '{q_name}'")
                print("1. Inspect (Top 5)")
                print("2. Purge This Queue")
                print("3. Selective Delete (*wildcard*)")
                print("4. Back")
                
                sub = input("Action: ")
                
                if sub == '1':
                    items = r_conn.lrange(q_name, 0, 4)
                    for raw in items: print(f"- {get_task_name(raw)}")
                    input("\nEnter to continue...")
                elif sub == '2':
                    if input(f"Delete ALL in '{q_name}'? (yes/no): ") == 'yes':
                        r_conn.delete(q_name)
                        print("Deleted.")
                elif sub == '3':
                    delete_tasks_by_pattern(r_conn, q_name)
            else:
                print("Invalid number.")
        except ValueError:
            pass

if __name__ == "__main__":
    main()

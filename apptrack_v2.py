import sqlite3
import argparse
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "job_applications.sqlite")

def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute('''
    PRAGMA foreign_keys = ON''')
    return (conn, cur)


def init_db():
    conn, cur = get_conn()
    
    # CREATING companies TABLE
    cur.execute('''
    CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')

    # CREATING applications TABLE
    cur.execute('''
    CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id INTEGER NOT NULL, role TEXT NOT NULL, 
    status TEXT NOT NULL, date_applied TEXT NOT NULL, job_link TEXT NULL, last_updated TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id))''')

    # CREATING notes TABLE
    cur.execute('''
    CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, application_id INTEGER NOT NULL,
    created_at TEXT NOT NULL, note TEXT NOT NULL,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE)''')

    conn.commit()
    conn.close()
    
parser = argparse.ArgumentParser()
sub_parser = parser.add_subparsers(dest="cmd", required=True)

# Add argument

addp = sub_parser.add_parser("add")
addp.add_argument("--company", default=None)
addp.add_argument("--role", default=None)
addp.add_argument("--date_applied", default=None)
addp.add_argument("--status", default="Applied")
addp.add_argument("--job_link", default=None)
addp.add_argument("--notes", default=None)

# list argument

listp = sub_parser.add_parser("list")

# stats argument

statsp = sub_parser.add_parser("stats")

# update argument

updatep = sub_parser.add_parser("update")
updatep.add_argument("id", type=int)
#optional fields
updatep.add_argument("--status", default=None)
updatep.add_argument("--date_applied", default=None)
updatep.add_argument("--notes", default=None)
updatep.add_argument("--job_link", default=None)

# delete argument

delp = sub_parser.add_parser("delete")
delp.add_argument("id", type=int)

if __name__ == "__main__":
    init_db()
    args = parser.parse_args()
    # add branch

    if args.cmd == "add":
        company = args.company
        role = args.role
        date_applied = args.date_applied
        if company == None:
            company = input("Company: ")
        if role == None:
            role = input("Role: ")
        if date_applied is None:
            date_applied = datetime.now().strftime("%Y-%m-%d")
        status = args.status
        job_link = args.job_link
        if job_link == None:
            job_link = input("Job link: ")
        notes = args.notes
        conn, cur = get_conn()
        company = company.strip()
        cur.execute('''
        SELECT id FROM companies WHERE name = ? ''', (company,))
        rows = cur.fetchone()
        if rows:
            company_id = rows[0]
        else:
            cur.execute('''
            INSERT INTO companies(name) VALUES (?)''', (company,))
            company_id = cur.lastrowid
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute('''
        INSERT INTO applications (company_id, role, status, date_applied, job_link, last_updated) VALUES (?, ?, ?, ?, ?, ?) 
        ''', (company_id, role, status, date_applied, job_link, last_updated))
        application_id = cur.lastrowid

        if notes:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute('''
            INSERT INTO notes(application_id, created_at, note) VALUES (?, ?, ?)
            ''', (application_id, created_at, notes))
                    
        conn.commit()
        conn.close()
        print("Added")
    # list branch 

    elif args.cmd == "list":
        conn, cur = get_conn()
        cur.execute('''
        SELECT applications.id, companies.name, applications.role, applications.status, applications.date_applied, 
        applications.job_link, applications.last_updated FROM applications JOIN companies ON applications.company_id = companies.id
        ORDER BY applications.id DESC''')
        rows = cur.fetchall()
        conn.close()
        #Empty rows
        if not rows:     
            print("No applications yet")
        else:
            for i in rows:
                print(f'Application ID: {i[0]}, Company Name: {i[1]}, Role: {i[2]}, Application Status: {i[3]}, Date Applied: {i[4]}, Job Link: {i[5] if i[5] is not None else 'Job link not available'}\n')

    # stats branch
    elif args.cmd == "stats":
        conn, cur = get_conn()

        cur.execute('''
        SELECT COUNT(*) 
        FROM applications''')
        row = cur.fetchone()
        total_applications = row[0]
        print(f'Total applications: {total_applications}')

        cur.execute('''
        SELECT applications.status, COUNT(*)
        FROM applications
        GROUP BY applications.status
        ORDER BY COUNT(*) DESC''')
        rows = cur.fetchall()
        for status, count in rows:
            print(f"{status}: {count}")
        conn.close()

    # update branch 

    elif args.cmd =="update":
        conn, cur = get_conn()
        did_update = False
        cur.execute('''
        SELECT 1 FROM applications WHERE id = ?''', (args.id,))
        exists = cur.fetchone()
        if not exists:
            print("No application with that id")
            conn.close()
        else:
            if not args.status is None:
                cur.execute('''
                UPDATE applications SET status = ? WHERE id = ?
                ''', (args.status, args.id))
                did_update = True

            if not args.date_applied is None:
                cur.execute('''
                UPDATE applications SET date_applied = ? WHERE id = ?
                ''', (args.date_applied, args.id))
                did_update = True

            if not args.job_link is None:
                cur.execute('''
                UPDATE applications SET job_link = ? WHERE id = ? ''', 
                (args.job_link, args.id)) 
                did_update = True
      
            if args.notes:
                application_id = args.id
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                note = args.notes
                cur.execute('''
                INSERT INTO notes (application_id , created_at, note) VALUES (?, ?, ?) ''', (application_id, created_at, note))
                did_update = True
        
        
            if did_update == True:
                last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute('''
                UPDATE applications SET last_updated = ? WHERE id = ? ''',
                (last_updated, args.id))
                conn.commit()
                print("Updated")   
            else:
                print("Nothing to update")
            conn.close()

    # delete branch
    
    elif args.cmd == "delete":
        conn, cur = get_conn()
        cur.execute('''DELETE FROM applications WHERE id = ?''', (args.id,))
        if cur.rowcount == 0:
            print("No application with that id")
        else:
            conn.commit()
            print("Deleted")
        conn.close()
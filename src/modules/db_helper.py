import psycopg2
import psycopg2.extras

SUCCESS = 0
FAIL = None

def insert_member(conn, bot, member):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Members (id, default_nickname)
            VALUES (%s, %s) ;
        """,
                    (member.id, member.display_name))
        conn.commit()
        refresh_member_in_db(conn, member, bot.config["roles"])
        return SUCCESS
    except:
        conn.rollback()
        return FAIL

def member_exists(conn, id):
    """
    Check if a member exists in the database

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM Members where id = '%s'", (id,))
        return cur.fetchone() is not None
    except:
        conn.rollback()
        return FAIL


def fetch_member(conn, id):
    """
    Return a member from the database as a tuple. Schema can be inferred from config.json

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Members where id = '%s'", (id,))
        return cur.fetchone()
    except:
        conn.rollback()
        return FAIL

def fetch_member_roles(conn,id,roles):
    """
    Return all the member role objects of a member

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    roles = list of all role ids within the server
    """
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM Members where id = '%s'", (id,))
        member = cur.fetchone()
        member_roles= []
        for role in roles:
            key = "role_"+str(role)
            if member[key]:
                member_roles.append(role)
        return member_roles
    except:
        conn.rollback()
        return FAIL

def fetch_member_nickname(conn,id):
    """
    Return the nickname of the member

    args:
    conn = database connection. Typically bot.conn
    id = member.id
    """
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM Members where id = '%s'", (id,))
        member = cur.fetchone()
        return member["default_nickname"]
    except:
        conn.rollback()
        return FAIL

def refresh_member_in_db(conn, member, config_roles):
    """
    Refresh a member's database data

    args:
    conn = database connection. Typically bot.conn
    member = member object to refresh
    """
    if member_exists(conn, member.id):
        try:
            cur = conn.cursor()
            cur.execute("""
                    UPDATE Members
                    SET default_nickname = %s
                    WHERE id = '%s' ;
                """,
                (member.display_name, member.id)
            )
            conn.commit()
        except:
            conn.rollback()
            return FAIL

        member_roles = [role.id for role in member.roles]
        for role in config_roles.values():
            if int(role) in member_roles:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                            UPDATE Members
                            SET role_%s = True
                            WHERE id = '%s' ;
                        """,
                        (int(role), member.id)
                    )
                    conn.commit()
                except:
                    conn.rollback()
                    return FAIL
            else:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                            UPDATE Members
                            SET role_%s = False
                            WHERE id = '%s' ;
                        """,
                        (int(role), member.id)
                    )
                    conn.commit()
                except:
                    conn.rollback()
                    return FAIL

def remove_role(conn, role_id):
    try:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE Members
            DROP COLUMN role_%s;
        """,
        (int(role_id),))
        conn.commit()
    except:
        conn.rollback()

def add_role(conn, role_id):
    try:
        cur = conn.cursor()
        cur.execute("""
            ALTER TABLE Members
            ADD COLUMN role_%s bool DEFAULT False;
        """,
        (int(role_id),))
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()

if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--id')
    parser.add_argument('--delete', action='store_true')
    args = parser.parse_args()
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print(DATABASE_URL)
    if args.delete:
        remove_role(conn, args.id)
    else:
        add_role(conn, args.id)
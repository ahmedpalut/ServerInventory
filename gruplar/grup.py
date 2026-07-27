from ldap3 import Server, Connection, ALL
from dotenv import load_dotenv
from ldap3 import SUBTREE
import os

load_dotenv()

LDAP_SERVER = os.getenv("LDAP_SERVER")
LDAP_PORT = int(os.getenv("LDAP_PORT", 389))
LDAP_DOMAIN = os.getenv("LDAP_DOMAIN")
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN")


def authenticate(username, password):

    try:
        server = Server(
            LDAP_SERVER,
            port=LDAP_PORT,
            get_info=ALL
        )

        user = f"{username}@{LDAP_DOMAIN}"

        conn = Connection(
            server,
            user=user,
            password=password,
            auto_bind=True
        )

        return True, conn

    except Exception as e:
        print(f"LDAP Hatası: {e}")
        return False, None


def disconnect(conn):

    if conn:
        conn.unbind()


def get_users(conn):
    cookie = True
    count = 0
    users = []

    search_filter = "(&(objectCategory=person)(objectClass=user))"

    while cookie:
        conn.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["cn", "sAMAccountName", "memberOf"],
            paged_size=500
        )

        for entry in conn.entries:
            count += 1
            print(f"\n===== KULLANICI {count} =====")
            print(entry)
            users.append(entry)

        cookie = conn.result.get("controls", {}) \
                             .get("1.2.840.113556.1.4.319", {}) \
                             .get("value", {}) \
                             .get("cookie")

        if not cookie:
            break

    return users


def list_groups(conn):
    conn.search(
        search_base=LDAP_BASE_DN,
        search_filter="(objectClass=group)",
        search_scope=SUBTREE,
        attributes=["cn", "distinguishedName"]
    )

    for entry in conn.entries:
        print(entry.cn, "->", entry.distinguishedName)
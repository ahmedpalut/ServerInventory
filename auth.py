from ldap3 import Server, Connection, ALL
from dotenv import load_dotenv
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
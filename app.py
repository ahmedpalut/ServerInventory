from flask import *
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key, find_dotenv
from ldap3 import Server, Connection, SUBTREE, SIMPLE, NONE
from functools import wraps
import json
import win32serviceutil
import win32service
import time
import subprocess
import mysql.connector
import os
import re
import threading
import socket
from scheduler import update_backup_schedule

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

AD_SERVER = os.getenv("LDAP_SERVER")
AD_DOMAIN = os.getenv("LDAP_DOMAIN")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lang = session.get("lang", "tr")
        translations = get_translation(lang)
        if not session.get("is_admin"):
            flash(translations["permission"], "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function

def mysql_service_running():
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Service -Name 'MySQL*' -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq 'Running'}"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        return bool(result.stdout.strip())

    except Exception as e:
        print("MySQL service check error:", e)
        return False


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "3306"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "")
}


def get_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            connect_timeout=2
        )

        return conn, conn.cursor(dictionary=True), True

    except Exception:
        return None, None, False

REQUIRED_DATABASE_SCHEMA = {
    "servers": [
        "id",
        "name",
        "disk_gb",
        "ram_g",
        "core_amount",
        "ip_address",
        "usage_project",
        "os_type_id",
        "created_at"
    ],
    "os_types": [
        "id",
        "name"
    ],
    "custom_columns": [
        "id",
        "column_name",
        "data_type",
        "created_at"
    ],
    "custom_values": [
        "server_id",
        "column_id",
        "value"
    ],
    "clients": [
        "id",
        "hostname",
        "ip_address",
        "username",
        "os_name",
        "last_seen"
    ],
    "network_devices": [
        "id",
        "name",
        "device_type",
        "brand",
        "model",
        "serial_number",
        "ip_address",
        "mac_address",
        "location",
        "status",
        "software_version",
        "description",
        "created_at",
        "updated_at"
    ],
    "logs": [
        "id",
        "username",
        "action",
        "target",
        "description",
        "created_at"
    ],
    "backup_settings": [
        "id",
        "is_enabled",
        "frequency",
        "backup_time",
        "backup_folder",
        "max_backup_count",
        "delete_old_backups",
        "last_backup_date",
        "last_backup_status"
    ]
}


def validate_database_schema(conn, database_name):
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS backup_settings (
                id INT PRIMARY KEY DEFAULT 1,
                is_enabled TINYINT(1) DEFAULT 0,
                frequency VARCHAR(20) DEFAULT 'daily',
                backup_time VARCHAR(10) DEFAULT '03:00',
                backup_folder VARCHAR(255) DEFAULT '',
                max_backup_count INT DEFAULT 10,
                delete_old_backups TINYINT(1) DEFAULT 1,
                last_backup_date VARCHAR(50) DEFAULT NULL,
                last_backup_status VARCHAR(255) DEFAULT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO backup_settings (id, is_enabled, frequency, backup_time, backup_folder, max_backup_count, delete_old_backups)
            SELECT 1, 0, 'daily', '03:00', '', 10, 1
            WHERE NOT EXISTS (SELECT 1 FROM backup_settings WHERE id = 1)
            """
        )

        try:
            cursor.execute("ALTER TABLE clients DROP COLUMN status")
        except Exception:
            pass

        try:
            cursor.execute("ALTER TABLE clients DROP COLUMN site_status")
        except Exception:
            pass

        conn.commit()

        for table_name, required_columns in REQUIRED_DATABASE_SCHEMA.items():

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = %s
                """,
                (database_name, table_name)
            )

            table_result = cursor.fetchone()

            if not table_result or table_result["total"] == 0:
                return False, f"'{table_name}' tablosu bulunamadı."

            cursor.execute(
                """
                SELECT COLUMN_NAME AS column_name
                FROM information_schema.columns
                WHERE table_schema = %s
                AND table_name = %s
                """,
                (database_name, table_name)
            )

            existing_columns = {
                row["column_name"]
                for row in cursor.fetchall()
            }

            missing_columns = [
                column
                for column in required_columns
                if column not in existing_columns
            ]

            if missing_columns:
                return False, (
                    f"'{table_name}' tablosunda eksik sütunlar: "
                    + ", ".join(missing_columns)
                )

        return True, "Veritabanı uyumlu."

    finally:
        cursor.close()

@app.route("/change_database_password", methods=["POST"])
@admin_required
def change_database_password():

    new_password = request.form.get("new_password", "")
    new_password_confirm = request.form.get("new_password_confirm", "")

    if not new_password or not new_password_confirm:
        flash("Yeni şifre alanlarını doldurun.", "error")
        return redirect(url_for("database"))

    if new_password != new_password_confirm:
        flash("Yeni şifreler eşleşmiyor.", "error")
        return redirect(url_for("database"))

    if not is_db_password_strong(new_password):
        flash(
            "Şifre en az 8 karakter olmalı ve büyük harf, "
            "küçük harf ve rakam içermelidir.",
            "error"
        )
        return redirect(url_for("database"))

    conn = None
    cursor = None

    try:

        conn, cursor, is_connected = get_db()

        if not is_connected:
            flash("Veritabanına bağlı değil.", "error")
            return redirect(url_for("database"))

        db_user = DB_CONFIG["user"]

        safe_user = db_user.replace("`", "``")

        cursor.execute(
            f"ALTER USER `{safe_user}`@`localhost` IDENTIFIED BY %s",
            (new_password,)
        )

        conn.commit()

        conn.close()
        conn = None

        DB_CONFIG["password"] = new_password

        dotenv_path = find_dotenv()

        if dotenv_path:
            set_key(
                dotenv_path,
                "DB_PASSWORD",
                new_password
            )

        flash(
            "Veritabanı şifresi başarıyla değiştirildi.",
            "success"
        )

    except Exception as e:

        print("Database password change error:", repr(e))

        if cursor:
            try:
                cursor.close()
            except:
                pass

        if conn:
            try:
                conn.close()
            except:
                pass

        flash(
            f"Veritabanı şifresi değiştirilemedi: {e}",
            "error"
        )

    return redirect(url_for("database"))

@app.route("/connect_database", methods=["POST"])
@admin_required
def connect_database():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    if not mysql_service_running():
        flash("MySQL hizmeti çalışmıyor.", "error")
        return redirect(url_for("database"))

    host = request.form.get("host", "").strip()
    port = request.form.get("port", "3306").strip()
    user = request.form.get("user", "").strip()
    password = request.form.get("password", "")
    database = request.form.get("database", "").strip()

    if not host or not port or not user or not database or not password:
        flash("Veritabanı bilgilerini eksiksiz girin.", "error")
        return redirect(url_for("database"))
    
    conn = None

    try:
        conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            connection_timeout=5
        )

        if not conn.is_connected():
            flash("Veritabanına bağlanılamadı.", "error")
            return redirect(url_for("database"))

        valid, message = validate_database_schema(conn, database)

        if not valid:
            conn.close()
            flash(f"Veritabanı uyumsuz: {message}", "error")
            return redirect(url_for("database"))

        conn.close()

        DB_CONFIG["host"] = host
        DB_CONFIG["port"] = port
        DB_CONFIG["user"] = user
        DB_CONFIG["password"] = password
        DB_CONFIG["database"] = database

        dotenv_path = find_dotenv()

        if dotenv_path:
            set_key(dotenv_path, "DB_HOST", host)
            set_key(dotenv_path, "DB_PORT", port)
            set_key(dotenv_path, "DB_USER", user)
            set_key(dotenv_path, "DB_PASSWORD", password)
            set_key(dotenv_path, "DB_NAME", database)

        flash("Veritabanı bağlantısı başarılı.", "success")

    except Exception as e:
        print("Database connection error:", repr(e))

        if conn:
            try:
                conn.close()
            except:
                pass

        flash(f"Veritabanına bağlanılamadı: {e}", "error")

    return redirect(url_for("database"))


def get_translation(lang="tr"):
    with open(f"static/js/translations/{lang}.json", encoding="utf-8") as file:
        return json.load(file)


def add_log(cursor, username, action, target="", description=""):
    cursor.execute(
        """
        INSERT INTO logs
        (username, action, target, description)
        VALUES (%s,%s,%s,%s)
        """,
        (username, action, target, description),
    )


@app.route("/change_language/<lang>")
def change_language(lang):
    if lang in ["tr", "en"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))


@app.before_request
def update_client_last_seen():
    username = session.get("user")

    if not username:
        return

    conn, cursor, is_connected = get_db()

    if not is_connected:
        return

    client_ip = request.remote_addr

    try:
        cursor.execute("""
            UPDATE clients
            SET last_seen = NOW()
            WHERE username = %s
              AND ip_address = %s
        """, (username, client_ip))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

@app.route("/database/restore", methods=["POST"])
@admin_required
def database_restore():

    mysql_path = r"C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe"

    db_host = DB_CONFIG["host"]
    db_port = DB_CONFIG["port"]
    db_user = DB_CONFIG["user"]
    db_password = DB_CONFIG["password"]
    db_name = DB_CONFIG["database"]

    file = request.files.get("database_file")

    if not file or file.filename == "":
        flash("SQL dosyası seçilmedi.","error")
        return redirect(url_for("database"))

    if not file.filename.lower().endswith(".sql"):
        flash("Sadece .sql dosyaları yüklenebilir.","error")
        return redirect(url_for("database"))

    temp_path = os.path.join(
        os.getcwd(),
        "_restore_temp.sql"
    )

    try:
        file.save(temp_path)

        with open(temp_path, "r", encoding="utf-8-sig", errors="replace") as f:
            sql_content = f.read()

        sql_content = re.sub(
            r"SET\s+@@GLOBAL\.GTID_PURGED\s*=\s*.*?;",
            "",
            sql_content,
            flags=re.IGNORECASE | re.DOTALL
        )

        sql_content = re.sub(
            r"SET\s+GLOBAL\.GTID_PURGED\s*=\s*.*?;",
            "",
            sql_content,
            flags=re.IGNORECASE | re.DOTALL
        )

        sql_content = re.sub(
            r"SET\s+@@GLOBAL\.GTID_PURGED\s*=\s*/\*![0-9]+\s*\+\s*\*/\s*'.*?';",
            "",
            sql_content,
            flags=re.IGNORECASE | re.DOTALL
        )

        with open(temp_path, "w", encoding="utf-8") as f:
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n" + sql_content + "\nSET FOREIGN_KEY_CHECKS = 1;\n")

        command = [
            mysql_path,
            "-h", db_host,
            "-P", db_port,
            "-u", db_user,
            f"-p{db_password}",
            db_name
        ]

        with open(temp_path, "r", encoding="utf-8") as sql_file:
            result = subprocess.run(
                command,
                stdin=sql_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

        if result.returncode != 0:

            error_message = result.stderr.strip()

            if not error_message:
                error_message = "Veritabanı geri yüklenemedi."

            flash(f"Restore error: {error_message}","error")
            return redirect(url_for("database"))
        
        log_conn, log_cursor, log_connected = get_db()
        
        if log_connected:
            username=session["user"]
        
            add_log(
                log_cursor,
                username,
                "Veritabanı İçe Aktar",
                db_name,
                f"{file.filename} dosyası içe aktarıldı."
            )
            
            log_conn.commit()
            log_conn.close()

        flash("Veritabanı başarıyla geri yüklendi.","success")
        return redirect(url_for("database"))

    except Exception as e:

        flash(f"Restore error: {e}","error")
        return redirect(url_for("database"))

    finally:

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def is_db_password_strong(password):

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    return True

@app.route("/backup_database")
@admin_required
def backup_database():

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash("Veritabanına bağlı değil.","error")
        return redirect(url_for("database"))

    conn.close()

    db_name = DB_CONFIG["database"]
    db_user = DB_CONFIG["user"]
    db_password = DB_CONFIG["password"]
    db_host = DB_CONFIG["host"]
    db_port = DB_CONFIG["port"]

    filename = f"{db_name}_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.sql"
    filepath = os.path.join(os.getcwd(), filename)

    mysql_dump = r"C:\Program Files\MySQL\MySQL Server 9.7\bin\mysqldump.exe"

    try:
        command = [
            mysql_dump,
            f"--host={db_host}",
            f"--port={db_port}",
            f"--user={db_user}",
            f"--password={db_password}",
            "--set-gtid-purged=OFF",
            "--routines",
            "--triggers",
            "--events",
            "--single-transaction",
            "--add-drop-table",
            db_name
        ]

        with open(filepath, "w", encoding="utf-8") as f:
            result = subprocess.run(
                command,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

        if result.returncode != 0:
            if os.path.exists(filepath):
                os.remove(filepath)

            error_message = result.stderr.strip()

            if not error_message:
                error_message = "Yedek oluşturulamadı."

            flash(f"Backup error: {error_message}","error")
            return redirect(url_for("database"))
        
        
        log_conn, log_cursor, log_connected = get_db()

        if log_connected:
            username = session["user"]

            add_log(
                log_cursor,
                username,
                "Veritabanı Dışa Aktar",
                db_name,
                f"{filename} dosyası dışa aktarıldı"
            )

            log_conn.commit()
            log_conn.close()

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype="application/sql"
        )
        
    except Exception as e:
        print("Backup error:", e)

        if os.path.exists(filepath):
            os.remove(filepath)

        flash(f"Backup error: {e}","error")
        return redirect(url_for("database"))

@app.route("/login", methods=["GET", "POST"])
def login():
    # session["user"] = "apalut"
    # session["role"] = "admin"
    # session["is_admin"] = True

    # return redirect(url_for("index"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if "\\" in username:
            user_dn = username
        else:
            user_dn = f"{username}@{AD_DOMAIN}"

        conn = None
        try:
            server = Server(AD_SERVER, get_info=NONE)
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=SIMPLE,
                raise_exceptions=True,
            )

            if conn.bind():
                search_base = ",".join([f"DC={x}" for x in AD_DOMAIN.split(".")])
                conn.search(
                    search_base=search_base,
                    search_filter=f"(sAMAccountName={username})",
                    search_scope=SUBTREE,
                    attributes=["memberOf"],
                )

                role = "Visitor"
                if conn.entries:
                    groups = conn.entries[0]["memberOf"]
                    for group in groups:
                        group = str(group)
                        if "CN=Test Admin," in group or "CN=Domain Admins," in group:
                            role = "Admin"

                session.clear()
                session["user"] = username
                session["role"] = role
                session["is_admin"] = role == "Admin"
                flash(translations["login_s"],"success")

                conn_db, cursor, is_connected = get_db()

                if is_connected:
                    client_ip = request.remote_addr

                    hostname = socket.gethostname()

                    cursor.execute("""
                        SELECT id
                        FROM clients
                        WHERE hostname = %s
                    """, (hostname,))

                    client = cursor.fetchone()

                    if client:
                        cursor.execute("""
                            UPDATE clients
                            SET username = %s,
                                last_seen = NOW()
                            WHERE id = %s
                        """, (
                            username,
                            client["id"]
                        ))

                    else:
                        cursor.execute("""
                            INSERT INTO clients
                                (hostname, ip_address, username, os_name, last_seen)
                            VALUES
                                (%s, %s, %s, %s, NOW())
                        """, (
                            hostname,
                            client_ip,
                            username,
                            None
                        ))

                    add_log(
                        cursor,
                        username,
                        "Giriş",
                        "Sunucu Envanteri",
                        f"{username}, sunucu envanter sitesine giriş yaptı."
                    )

                    conn_db.commit()
                    cursor.close()
                    conn_db.close()
                    
                    return redirect(url_for("index"))
            else:
                flash(translations["name_error"],"error")
                return redirect(url_for("login"))

        except Exception as e:
            print("LOGIN HATASI:", repr(e))
            flash(translations["error"],"error")
            if conn:
                conn.unbind()
            return redirect(url_for("login"))

        finally:
            if conn:
                conn.unbind()

    return render_template("login.html", translations=translations, lang=lang)


@app.route("/logout")
def logout():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    username = session.get("user", "Bilinmeyen kullanıcı")

    conn, cursor, is_connected = get_db()

    if is_connected:
        add_log(
            cursor,
            username,
            "Çıkış",
            "Sunucu Envanteri",
            f"{username}, sunucu envanter sitesinden çıkış yaptı."
        )

        conn.commit()
        cursor.close()
        conn.close()

    session.clear()

    flash(translations["logout_s"],"success")

    return redirect(url_for("login"))


@app.route("/start_database", methods=["POST"])
@admin_required
def start_database():

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if is_connected:
        conn.close()
        flash("Veritabanı zaten bağlı.","error")
        return redirect(url_for("database"))

    service_name = os.getenv("MYSQL_SERVICE")

    try:
        status = win32serviceutil.QueryServiceStatus(service_name)[1]

        if status != win32service.SERVICE_RUNNING:
            win32serviceutil.StartService(service_name)

        for _ in range(5):
            time.sleep(1)

            conn, cursor, is_connected = get_db()

            if is_connected:
                conn.close()
                flash("Veritabanına başarıyla bağlanıldı.","success")
                return redirect(url_for("database"))

        flash("MySQL servisi başlatılamadı.","error")

    except Exception as e:
        print(e)
        flash("Bir hata oluştu.","error")

    return redirect(url_for("database"))

@app.route("/mysql_service_status")
@admin_required
def mysql_service_status():

    service_name = os.getenv("MYSQL_SERVICE")

    try:
        status = win32serviceutil.QueryServiceStatus(service_name)[1]

        if status == win32service.SERVICE_RUNNING:
            return {"running": True}

        return {"running": False}

    except Exception as e:
        print(e)
        return {"running": False}

@app.route("/database_service_warning")
@admin_required
def database_service_warning():

    flash("MySQL hizmeti kapalı!", "error")

    return redirect(url_for("database"))

@app.route("/logs")
def logs():
    if "user" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        return render_template(
            "logs.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            logs=[],
        )

    try:
        cursor.execute(
            """
            SELECT
                username,
                action,
                target,
                description,
                created_at
            FROM logs
            ORDER BY created_at DESC
            LIMIT 100
        """
        )

        logs = cursor.fetchall()

        conn.close()

        return render_template(
            "logs.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=True,
            logs=logs,
        )

    except Exception:
        if conn:
            conn.close()

        return render_template(
            "logs.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            logs=[],
        )


@app.route("/logs/search")
def logs_search():
    if "user" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        return render_template(
            "logs.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            logs=[],
        )

    try:
        q = request.args.get("q", "").strip()
        fields = request.args.getlist("fields")

        if not q:
            if conn:
                conn.close()
            return redirect(url_for("logs"))

        if not fields:
            if conn:
                conn.close()
            flash(translations.get("select_at_least_one_field", "Lütfen en az bir arama alanı seçin."), "error")
            return redirect(url_for("logs"))

        allowed_fields = {
            "username": "username",
            "action": "action",
            "target": "target",
            "description": "description",
            "created_at": "created_at",
        }

        selected_fields = []
        for field in fields:
            if field in allowed_fields:
                selected_fields.append(allowed_fields[field])

        if q and not selected_fields:
            selected_fields = list(allowed_fields.values())

        sql = """
            SELECT
                username,
                action,
                target,
                description,
                created_at
            FROM logs
        """
        values = []

        if q and selected_fields:
            conditions = []
            for field in selected_fields:
                conditions.append(f"CAST({field} AS CHAR) LIKE %s")
                values.append(f"%{q}%")
            sql += " WHERE " + " OR ".join(conditions)

        sql += " ORDER BY created_at DESC LIMIT 100"

        cursor.execute(sql, values)
        logs = cursor.fetchall()
        conn.close()

        return render_template(
            "logs.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=True,
            logs=logs,
        )
    except Exception:
        if conn:
            conn.close()

        return render_template(
            "logs.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            logs=[],
        )


@app.route("/")
def index():
    
    if "user" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        return render_template(
            "index.html",
            servers=[],
            windows_amount=0,
            os_list=[],
            custom_columns=[],
            custom_values={},
            is_admin=session.get("is_admin", False),
            username=session.get("user"),
            translations=translations,
            lang=lang,
        )

    try:
        cursor.execute("SELECT * FROM custom_columns ORDER BY column_name")
        custom_columns = cursor.fetchall()

        cursor.execute("SELECT server_id, column_id, value FROM custom_values")
        rows = cursor.fetchall()

        custom_values = {}
        for row in rows:
            server_id = row["server_id"]
            if server_id not in custom_values:
                custom_values[server_id] = {}
            custom_values[server_id][row["column_id"]] = row["value"]

        cursor.execute(
            """
            SELECT
                s.id,
                s.name,
                s.disk_gb,
                s.ram_g,
                s.core_amount,
                s.ip_address,
                s.usage_project,
                s.created_at,
                o.name AS os_name
            FROM servers s
            LEFT JOIN os_types o ON s.os_type_id = o.id
            """
        )
        servers = cursor.fetchall()

        for server in servers:
            server["custom_values"] = custom_values.get(server["id"], {})

        windows_amount = sum(
            1 for s in servers if s["os_name"] and "windows" in s["os_name"].lower()
        )

        cursor.execute("SELECT name FROM os_types ORDER BY name")
        os_list = cursor.fetchall()
        conn.close()

        return render_template(
            "index.html",
            servers=servers,
            windows_amount=windows_amount,
            os_list=os_list,
            custom_columns=custom_columns,
            custom_values=custom_values,
            is_admin=session.get("is_admin", False),
            username=session.get("user"),
            translations=translations,
            lang=lang,
        )
    except Exception:
        if conn:
            conn.close()
        return render_template(
            "index.html",
            servers=[],
            windows_amount=0,
            os_list=[],
            custom_columns=[],
            custom_values={},
            is_admin=session.get("is_admin", False),
            username=session.get("user"),
            translations=translations,
            lang=lang,
        )


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        return render_template(
            "dashboard.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            db_status=translations["connection_status_offline"],
            db_size="0 MB",
            table_count=0,
            server_count=0,
            labels=[],
            values=[],
            other_info_text="",
            disk_labels="[]",
            disk_values="[]",
            total_servers=0,
            ram_labels="[]",
            ram_values="[]",
            cpu_labels="[]",
            cpu_values="[]",
            date_labels="[]",
            date_values="[]",
            no_date=0,
            total_disk_str="0 GB",
            total_ram_str="0 GB",
            total_cpu=0,
            win_percent=0,
            other_percent=0,
            top_servers=[],
            net_labels="[]",
            net_values="[]",
            net_other_info_text="",
            total_net_devices=0,
        )

    try:
        cursor.execute(
            """
            SELECT 
                COALESCE(SUM(disk_gb), 0) AS total_disk,
                COALESCE(SUM(ram_g), 0) AS total_ram,
                COALESCE(SUM(core_amount), 0) AS total_cpu
            FROM servers
            """
        )
        totals = cursor.fetchone()

        total_disk_gb = totals["total_disk"]
        if total_disk_gb >= 1024:
            total_disk_str = f"{round(total_disk_gb / 1024, 1)} TB"
        else:
            total_disk_str = f"{round(total_disk_gb, 1)} GB"

        total_ram_gb = totals["total_ram"]
        if total_ram_gb >= 1024:
            total_ram_str = f"{round(total_ram_gb / 1024, 1)} TB"
        else:
            total_ram_str = f"{total_ram_gb} GB"

        total_cpu = totals["total_cpu"]

        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN LOWER(o.name) LIKE '%windows%' THEN 1 ELSE 0 END) AS windows_count,
                COUNT(*) AS total_count
            FROM servers s
            LEFT JOIN os_types o ON s.os_type_id = o.id
            """
        )
        os_counts = cursor.fetchone()
        total_count = os_counts["total_count"] or 0
        windows_count = os_counts["windows_count"] or 0

        if total_count > 0:
            win_percent = round((windows_count / total_count) * 100)
            other_percent = 100 - win_percent
        else:
            win_percent = 0
            other_percent = 0

        cursor.execute(
            """
            SELECT
                o.name AS os_name,
                COUNT(*) AS total
            FROM servers s
            LEFT JOIN os_types o ON s.os_type_id = o.id
            GROUP BY o.name
            ORDER BY total DESC
            """
        )

        os_stats = cursor.fetchall()

        TOP_N = 5
        labels = []
        values = []
        other_total = 0
        other_details = []

        for i, row in enumerate(os_stats):
            os_name = row["os_name"] or "Bilinmeyen"
            total = row["total"]

            if i < TOP_N:
                labels.append(os_name)
                values.append(total)
            else:
                other_total += total
                other_details.append(f"{os_name}: {total}")

        if other_total > 0:
            labels.append("Diğer")
            values.append(other_total)

        other_info_text = ", ".join(other_details)

        cursor.execute("SELECT core_amount FROM servers")
        cpu_servers = cursor.fetchall()

        cpu_labels = ["1-2 Core", "4-8 Core", "8-16 Core", "16+ Core"]
        cpu_values = [0] * len(cpu_labels)

        for server in cpu_servers:
            cpu = server["core_amount"] or 0
            if cpu <= 2:
                cpu_values[0] += 1
            elif cpu <= 8:
                cpu_values[1] += 1
            elif cpu <= 16:
                cpu_values[2] += 1
            else:
                cpu_values[3] += 1

        cursor.execute("SELECT ram_g FROM servers")
        ram_servers = cursor.fetchall()

        ram_labels = ["0-4 GB", "4-16 GB", "16-32 GB", "32-64 GB", "64+ GB"]
        ram_values = [0] * len(ram_labels)

        for server in ram_servers:
            ram = server["ram_g"] or 0
            if ram < 4:
                ram_values[0] += 1
            elif ram < 16:
                ram_values[1] += 1
            elif ram < 32:
                ram_values[2] += 1
            elif ram < 64:
                ram_values[3] += 1
            else:
                ram_values[4] += 1

        cursor.execute(
            """
            SELECT 
                MONTH(created_at) AS month,
                COUNT(*) AS total
            FROM servers
            WHERE created_at IS NOT NULL
            GROUP BY MONTH(created_at)
            ORDER BY MONTH(created_at)
            """
        )

        date_stats = cursor.fetchall()

        months = [
            "Ocak",
            "Şubat",
            "Mart",
            "Nisan",
            "Mayıs",
            "Haziran",
            "Temmuz",
            "Ağustos",
            "Eylül",
            "Ekim",
            "Kasım",
            "Aralık",
        ]

        date_labels = []
        date_values = []

        for row in date_stats:
            date_labels.append(months[row["month"] - 1])
            date_values.append(row["total"])

        cursor.execute("SELECT COUNT(*) AS total FROM servers WHERE created_at IS NULL")
        no_date = cursor.fetchone()["total"]

        cursor.execute("SELECT disk_gb FROM servers")
        disk_data = cursor.fetchall()

        disk_labels = [
            "0-100 GB",
            "100-250 GB",
            "250-500 GB",
            "500 GB-1 TB",
            "1-2 TB",
            "2-5 TB",
            "5-10 TB",
            "10+ TB",
        ]

        disk_values = [0] * len(disk_labels)

        for row in disk_data:
            disk = row["disk_gb"] or 0
            if disk < 100:
                disk_values[0] += 1
            elif disk < 250:
                disk_values[1] += 1
            elif disk < 500:
                disk_values[2] += 1
            elif disk < 1024:
                disk_values[3] += 1
            elif disk < 2048:
                disk_values[4] += 1
            elif disk < 5120:
                disk_values[5] += 1
            elif disk < 10240:
                disk_values[6] += 1
            else:
                disk_values[7] += 1

        cursor.execute(
            """
            SELECT 
                s.name,
                s.ram_g,
                s.disk_gb,
                s.core_amount,
                s.ip_address,
                o.name AS os_name
            FROM servers s
            LEFT JOIN os_types o ON s.os_type_id = o.id
            ORDER BY s.ram_g DESC, s.disk_gb DESC
            LIMIT 3
            """
        )
        top_servers = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                COALESCE(device_type, 'Bilinmeyen') AS dev_type,
                COUNT(*) AS total
            FROM network_devices
            GROUP BY device_type
            ORDER BY total DESC
            """
        )
        net_stats = cursor.fetchall()

        net_TOP_N = 5
        net_labels = []
        net_values = []
        net_other_total = 0
        net_other_details = []

        for i, row in enumerate(net_stats):
            d_type = row["dev_type"] or "Bilinmeyen"
            total = row["total"]

            if i < net_TOP_N:
                net_labels.append(d_type)
                net_values.append(total)
            else:
                net_other_total += total
                net_other_details.append(f"{d_type}: {total}")

        if net_other_total > 0:
            net_labels.append("Diğer")
            net_values.append(net_other_total)

        net_other_info_text = ", ".join(net_other_details)
        total_net_devices = sum(row["total"] for row in net_stats)

        conn.close()

        return render_template(
            "dashboard.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            is_admin=session.get("is_admin"),
            is_connected=True,
            db_status=translations["connection_status_online"],
            labels=labels,
            values=values,
            other_info_text=other_info_text,
            disk_labels=json.dumps(disk_labels),
            disk_values=json.dumps(disk_values),
            total_servers=sum(values),
            ram_labels=json.dumps(ram_labels),
            ram_values=json.dumps(ram_values),
            cpu_labels=json.dumps(cpu_labels),
            cpu_values=json.dumps(cpu_values),
            date_labels=json.dumps(date_labels),
            date_values=json.dumps(date_values),
            no_date=no_date,
            total_disk_str=total_disk_str,
            total_ram_str=total_ram_str,
            total_cpu=total_cpu,
            win_percent=win_percent,
            other_percent=other_percent,
            top_servers=top_servers,
            net_labels=json.dumps(net_labels),
            net_values=json.dumps(net_values),
            net_other_info_text=net_other_info_text,
            total_net_devices=total_net_devices,
        )
    except Exception:
        if conn:
            conn.close()
        return render_template(
            "dashboard.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            db_status=translations["connection_status_offline"],
            db_size="0 MB",
            table_count=0,
            server_count=0,
            labels=[],
            values=[],
            other_info_text="",
            disk_labels="[]",
            disk_values="[]",
            total_servers=0,
            ram_labels="[]",
            ram_values="[]",
            cpu_labels="[]",
            cpu_values="[]",
            date_labels="[]",
            date_values="[]",
            no_date=0,
            total_disk_str="0 GB",
            total_ram_str="0 GB",
            total_cpu=0,
            win_percent=0,
            other_percent=0,
            top_servers=[],
            net_labels="[]",
            net_values="[]",
            net_other_info_text="",
            total_net_devices=0,
        )


@app.route("/database")
def database():
    if "user" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        return render_template(
            "database.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            db_status=translations["connection_status_offline"],
            db_size="0 MB",
            table_count=0,
            server_count=0,
            db_name=DB_CONFIG["database"],
            config_db_host=DB_CONFIG["host"],
            config_db_port=DB_CONFIG["port"],
            config_db_user=DB_CONFIG["user"],
            config_db_name=DB_CONFIG["database"],
            logs=[]
        )

    try:
        active_database = DB_CONFIG["database"]

        cursor.execute("SELECT COUNT(*) AS total FROM servers")
        server_result = cursor.fetchone()
        server_count = server_result["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM information_schema.tables
            WHERE table_schema = %s
            """,
            (active_database,)
        )

        table_result = cursor.fetchone()
        table_count = table_result["total"]

        cursor.execute(
            """
            SELECT
                ROUND(
                    SUM(data_length + index_length) / 1024 / 1024,
                    2
                ) AS size_mb
            FROM information_schema.tables
            WHERE table_schema = %s
            """,
            (active_database,)
        )

        db_size_row = cursor.fetchone()
        db_size = f"{db_size_row['size_mb'] or 0} MB"

        conn.close()

        return render_template(
            "database.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=True,
            db_status=translations["connection_status_online"],
            db_size=db_size,
            table_count=table_count,
            server_count=server_count,
            db_name=active_database,
            config_db_host=DB_CONFIG["host"],
            config_db_port=DB_CONFIG["port"],
            config_db_user=DB_CONFIG["user"],
            config_db_name=DB_CONFIG["database"]
        )

    except Exception as e:
        print("Database page error:", repr(e))

        if conn:
            conn.close()

        return render_template(
            "database.html",
            translations=translations,
            lang=lang,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            is_connected=False,
            db_status=translations["connection_status_offline"],
            db_size="0 MB",
            table_count=0,
            server_count=0,
            db_name=DB_CONFIG["database"],
            config_db_host=DB_CONFIG["host"],
            config_db_port=DB_CONFIG["port"],
            config_db_user=DB_CONFIG["user"],
            config_db_name=DB_CONFIG["database"],
            logs=[]
        )


@app.route("/edit/<int:id>", methods=["POST"])
@admin_required
def edit(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")
        return redirect(url_for("index"))

    try:
        cursor.execute(
            """
            SELECT
                name,
                disk_gb,
                ram_g,
                ip_address,
                usage_project,
                core_amount,
                os_type_id,
                created_at
            FROM servers
            WHERE id=%s
        """,
            (id,),
        )

        old_server = cursor.fetchone()

        if not old_server:
            conn.close()
            flash(translations.get("error", "Server not found"),"error")
            return redirect(url_for("index"))

        name = request.form["ad"]
        disk = float(request.form["disk"])
        ram = int(request.form["ram"])
        ip = request.form["ip"]
        project = request.form["project"]
        cpu = int(request.form["cpu"])
        date = request.form["date"] or None
        disk_type = request.form["disktur"]

        if disk_type.upper() == "TB":
            disk *= 1024

        selected_os = request.form.get("server", "").strip()

        if not selected_os:
            raise Exception("İşletim sistemi seçilmedi.")

        if selected_os == "Yeni":

            new_os_name = request.form.get("isletim", "").strip()

            if not new_os_name:
                raise Exception("Yeni işletim sistemi adı boş bırakılamaz.")

            cursor.execute(
                "SELECT id FROM os_types WHERE name=%s",
                (new_os_name,)
            )

            existing_os = cursor.fetchone()

            if existing_os:
                os_type_id = existing_os["id"]
                os_name = new_os_name

            else:
                cursor.execute(
                    "INSERT INTO os_types (name) VALUES (%s)",
                    (new_os_name,)
                )

                os_type_id = cursor.lastrowid
                os_name = new_os_name

        else:

            os_name = selected_os

            cursor.execute(
                "SELECT id FROM os_types WHERE name=%s",
                (os_name,)
            )

            result = cursor.fetchone()

            if not result:
                raise Exception("İşletim sistemi bulunamadı.")

            os_type_id = result["id"]

        cursor.execute(
            "SELECT name FROM os_types WHERE id=%s", (old_server["os_type_id"],)
        )

        old_os_result = cursor.fetchone()
        old_os_name = old_os_result["name"] if old_os_result else ""

        changes = []

        if str(old_server["name"] or "") != str(name):
            changes.append(f"Sunucu Adı: '{old_server['name']}' → '{name}'")

        if float(old_server["disk_gb"] or 0) != float(disk):
            changes.append(f"Disk: '{old_server['disk_gb']}' → '{disk}' GB")

        if str(old_os_name or "") != str(os_name):
            changes.append(f"İşletim Sistemi: '{old_os_name}' → '{os_name}'")

        if int(old_server["ram_g"] or 0) != int(ram):
            changes.append(f"RAM: '{old_server['ram_g']}' → '{ram}' GB")

        if str(old_server["ip_address"] or "") != str(ip):
            changes.append(f"IP: '{old_server['ip_address']}' → '{ip}'")

        if str(old_server["usage_project"] or "") != str(project):
            changes.append(f"Açıklama: '{old_server['usage_project']}' → '{project}'")

        if int(old_server["core_amount"] or 0) != int(cpu):
            changes.append(f"CPU: '{old_server['core_amount']}' → '{cpu}'")

        old_date = str(old_server["created_at"] or "")
        new_date = str(date or "")

        if old_date != new_date:
            changes.append(f"Tarih: '{old_date}' → '{new_date}'")

        cursor.execute(
            """
            SELECT id, column_name, data_type
            FROM custom_columns
        """
        )

        custom_columns = cursor.fetchall()

        for column in custom_columns:
            column_id = column["id"]
            column_name = column["column_name"]
            data_type = column["data_type"]

            value = request.form.get(f"custom_{column_id}")

            if data_type == "BOOLEAN":
                value = "True" if value else "False"

            cursor.execute(
                """
                SELECT id, value
                FROM custom_values
                WHERE server_id=%s AND column_id=%s
            """,
                (id, column_id),
            )

            old_value_result = cursor.fetchone()

            old_value = old_value_result["value"] if old_value_result else ""

            new_value = value if value not in ("", None) else ""

            if str(old_value) != str(new_value):
                changes.append(f"{column_name}: '{old_value}' → '{new_value}'")

            if value not in ("", None):
                if old_value_result:
                    cursor.execute(
                        """
                        UPDATE custom_values
                        SET value=%s
                        WHERE server_id=%s
                        AND column_id=%s
                    """,
                        (value, id, column_id),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO custom_values
                        (
                            server_id,
                            column_id,
                            value
                        )
                        VALUES (%s, %s, %s)
                    """,
                        (id, column_id, value),
                    )
            elif old_value_result:
                cursor.execute(
                    """
                    DELETE FROM custom_values
                    WHERE server_id=%s
                    AND column_id=%s
                """,
                    (id, column_id),
                )

        sql = """
        UPDATE servers
        SET
            name=%s,
            disk_gb=%s,
            ram_g=%s,
            ip_address=%s,
            usage_project=%s,
            core_amount=%s,
            os_type_id=%s,
            created_at=%s
        WHERE id=%s
        """

        values = (name, disk, ram, ip, project, cpu, os_type_id, date, id)

        cursor.execute(sql, values)

        for change in changes:
            add_log(cursor, session["user"], "Sunucu Düzenle", name, change)

        conn.commit()
        conn.close()

        flash(translations["server_updated"],"success")
        return redirect(url_for("index"))

    except Exception as e:
        print(e)

        if conn:
            conn.close()

        flash(translations.get("error", "Error updating server"),"error")

        return redirect(url_for("index"))


@app.route("/delete/<int:id>")
@admin_required
def delete(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")
        return redirect(url_for("index"))

    try:
        cursor.execute("SELECT name FROM servers WHERE id=%s", (id,))
        server = cursor.fetchone()

        cursor.execute("DELETE FROM custom_values WHERE server_id = %s", (id,))
        cursor.execute("DELETE FROM servers WHERE id = %s", (id,))

        add_log(
            cursor,
            session["user"],
            "Sunucu Sil",
            server["name"],
            f"'{server['name']}' sunucusu silindi.",
        )

        conn.commit()
        conn.close()

        flash(translations["delete_server_s"],"success")
        return redirect(url_for("index"))
    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Error deleting server"),"error")
        return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
@admin_required
def add():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")
        return redirect(url_for("index"))

    try:
        if request.method == "POST":
            name = request.form["ad"]
            disk_gb = float(request.form["disk"])
            ram_g = int(request.form["ram"])
            core_amount = int(request.form["cpu"])
            ip_address = request.form["ip"]
            usage_project = request.form["aciklama"]
            created_at = request.form["tarih"]

            if created_at == "":
                created_at = None

            if request.form["server"] == "Yeni":
                os = request.form["isletim"]
                cursor.execute("INSERT INTO os_types (name) VALUES (%s)", (os,))
                conn.commit()
                os_type_id = cursor.lastrowid
            else:
                os = request.form["server"]
                cursor.execute("SELECT id FROM os_types WHERE name = %s", (os,))
                result = cursor.fetchone()
                os_type_id = result["id"]

            disk_type = request.form["disktur"].upper()
            if disk_type == "TB":
                disk_gb *= 1024

            sql = """INSERT INTO servers 
            (name, disk_gb, ram_g, core_amount, ip_address, os_type_id, usage_project, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                name,
                disk_gb,
                ram_g,
                core_amount,
                ip_address,
                os_type_id,
                usage_project,
                created_at,
            )

            cursor.execute(sql, values)
            server_id = cursor.lastrowid

            cursor.execute("SELECT id, data_type FROM custom_columns")
            custom_columns = cursor.fetchall()

            for column in custom_columns:
                value = request.form.get(f"custom_{column['id']}")
                if column["data_type"] == "BOOLEAN":
                    value = "True" if value else "False"

                if value not in ("", None):
                    cursor.execute(
                        "INSERT INTO custom_values (server_id, column_id, value) VALUES (%s, %s, %s)",
                        (server_id, column["id"], value),
                    )

            add_log(
                cursor,
                session["user"],
                "Sunucu Ekle",
                name,
                f"'{name}' sunucusu eklendi.",
            )

            conn.commit()
            conn.close()

            flash(translations["server_added"],"success")
            return redirect(url_for("index"))

        cursor.execute("SELECT name FROM os_types ORDER BY name")
        os_list = cursor.fetchall()

        cursor.execute(
            "SELECT id, column_name, data_type FROM custom_columns ORDER BY id"
        )
        custom_columns = cursor.fetchall()
        conn.close()

        return render_template(
            "add.html",
            os_list=os_list,
            custom_columns=custom_columns,
            translations=translations,
            lang=lang,
        )
    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Database error"),"error")
        return redirect(url_for("index"))


@app.route("/search")
def search():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        return render_template(
            "index.html",
            servers=[],
            windows_amount=0,
            os_list=[],
            custom_columns=[],
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            translations=translations,
            lang=lang,
        )

    try:
        q = request.args.get("q", "").strip()
        fields = request.args.getlist("fields")
        disk_unit = request.args.get("disk_unit", "GB")
        disk_compare = request.args.get("disk_compare", "equal")

        if not q:
            if conn:
                conn.close()
            return redirect(url_for("index"))

        if not fields:
            if conn:
                conn.close()
            flash(translations.get("select_at_least_one_field", "Lütfen en az bir arama alanı seçin."), "error")
            return redirect(url_for("index"))

        allowed_fields = {
            "name": "servers.name",
            "os_name": "os_types.name",
            "ip_address": "servers.ip_address",
            "usage_project": "servers.usage_project",
            "disk_gb": "servers.disk_gb",
            "ram_g": "servers.ram_g",
            "core_amount": "servers.core_amount",
            "created_at": "servers.created_at",
        }

        cursor.execute("SELECT * FROM custom_columns")
        custom_columns = cursor.fetchall()

        for col in custom_columns:
            allowed_fields[f"custom_{col['id']}"] = {"type": "custom", "id": col["id"]}

        selected_fields = []
        for f in fields:
            if f in allowed_fields:
                selected_fields.append(allowed_fields[f])
            elif f.startswith("custom_"):
                column_id = int(f.split("_")[1])
                selected_fields.append({"type": "custom", "id": column_id})

        sql = """
            SELECT
                servers.*,
                os_types.name AS os_name
            FROM servers
            LEFT JOIN os_types ON servers.os_type_id = os_types.id
        """
        values = []

        if q and selected_fields:
            conditions = []
            for field in selected_fields:
                if isinstance(field, dict) and field["type"] == "custom":
                    conditions.append(
                        """
                        EXISTS (
                            SELECT 1
                            FROM custom_values cv
                            WHERE cv.server_id = servers.id
                            AND cv.column_id = %s
                            AND cv.value LIKE %s
                        )
                        """
                    )
                    values.append(field["id"])
                    values.append(f"%{q}%")
                elif field == "servers.disk_gb":
                    try:
                        limit = float(q)
                        if disk_unit == "TB":
                            limit *= 1024
                        if disk_compare == "equal":
                            conditions.append(
                                "CAST(servers.disk_gb AS DECIMAL(10,2)) = CAST(%s AS DECIMAL(10,2))"
                            )
                        elif disk_compare == "gte":
                            conditions.append(
                                "CAST(servers.disk_gb AS DECIMAL(10,2)) >= CAST(%s AS DECIMAL(10,2))"
                            )
                        elif disk_compare == "lte":
                            conditions.append(
                                "CAST(servers.disk_gb AS DECIMAL(10,2)) <= CAST(%s AS DECIMAL(10,2))"
                            )
                        values.append(limit)
                    except ValueError:
                        pass
                else:
                    conditions.append(f"{field} LIKE %s")
                    values.append(f"%{q}%")

            if conditions:
                sql += " WHERE " + " OR ".join(conditions)

        cursor.execute(sql, values)
        servers = cursor.fetchall()

        cursor.execute("SELECT server_id, column_id, value FROM custom_values")
        rows = cursor.fetchall()

        custom_values = {}
        for row in rows:
            server_id = row["server_id"]
            if server_id not in custom_values:
                custom_values[server_id] = {}
            custom_values[server_id][row["column_id"]] = row["value"]

        for server in servers:
            server["custom_values"] = custom_values.get(server["id"], {})

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM servers
            LEFT JOIN os_types ON servers.os_type_id = os_types.id
            WHERE os_types.name LIKE '%windows%'
            """
        )
        windows_amount = cursor.fetchone()["count"]

        cursor.execute("SELECT name FROM os_types ORDER BY name")
        os_list = cursor.fetchall()

        cursor.execute("SELECT * FROM custom_columns ORDER BY column_name")
        custom_columns = cursor.fetchall()
        conn.close()

        return render_template(
            "index.html",
            servers=servers,
            windows_amount=windows_amount,
            os_list=os_list,
            custom_columns=custom_columns,
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            translations=translations,
            lang=lang,
        )
    except Exception:
        if conn:
            conn.close()
        return render_template(
            "index.html",
            servers=[],
            windows_amount=0,
            os_list=[],
            custom_columns=[],
            username=session.get("user"),
            role=session.get("role"),
            is_admin=session.get("is_admin"),
            translations=translations,
            lang=lang,
        )

@app.route("/networkdevices/search")
def networkdevices_search():

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    username = session.get("user", "Unknown")
    is_admin = session.get("is_admin", False)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")

        return render_template(
            "networkdevices.html",
            translations=translations,
            lang=lang,
            username=username,
            is_admin=is_admin,
            devices=[]
        )

    try:

        q = request.args.get("q", "").strip()
        fields = request.args.getlist("fields")

        if not q:
            if conn:
                conn.close()
            return redirect(url_for("networkdevices"))

        if not fields:
            if conn:
                conn.close()
            flash(translations.get("select_at_least_one_field", "Lütfen en az bir arama alanı seçin."), "error")
            return redirect(url_for("networkdevices"))

        allowed_fields = {
            "name": "name",
            "device_type": "device_type",
            "brand": "brand",
            "model": "model",
            "serial_number": "serial_number",
            "ip_address": "ip_address",
            "mac_address": "mac_address",
            "location": "location",
            "status": "status",
            "software_version": "software_version",
            "description": "description",
            "created_at": "created_at",
            "updated_at": "updated_at"
        }

        selected_fields = []

        for field in fields:

            if field in allowed_fields:
                selected_fields.append(
                    allowed_fields[field]
                )

        sql = """
            SELECT
                id,
                name,
                device_type,
                brand,
                model,
                serial_number,
                ip_address,
                mac_address,
                location,
                status,
                software_version,
                description,
                created_at,
                updated_at
            FROM network_devices
        """

        values = []

        if q and selected_fields:

            conditions = []

            for field in selected_fields:

                conditions.append(
                    f"CAST({field} AS CHAR) LIKE %s"
                )

                values.append(f"%{q}%")

            sql += " WHERE " + " OR ".join(conditions)

        sql += " ORDER BY id DESC"

        cursor.execute(sql, values)

        devices = cursor.fetchall()

        conn.close()

        return render_template(
            "networkdevices.html",
            translations=translations,
            lang=lang,
            username=username,
            is_admin=is_admin,
            devices=devices
        )

    except Exception as e:

        print(e)

        if conn:
            conn.close()

        flash(translations.get("error", "Database error"),"error")

        return render_template(
            "networkdevices.html",
            translations=translations,
            lang=lang,
            username=username,
            is_admin=is_admin,
            devices=[]
        )

@app.route("/addcolumn", methods=["GET", "POST"])
@admin_required
def addcolumn():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")
        return redirect(url_for("index"))

    try:
        if request.method == "POST":
            column_name = request.form["colName"].strip()
            data_type = request.form["dataType"]

            cursor.execute(
                "SELECT id FROM custom_columns WHERE LOWER(column_name) = LOWER(%s)",
                (column_name,),
            )

            if cursor.fetchone():
                conn.close()
                flash(translations["col_already_exists"],"error")
                return redirect(url_for("addcolumn"))

            cursor.execute(
                """
                INSERT INTO custom_columns
                (column_name, data_type, created_at)
                VALUES (%s, %s, CURDATE())
                """,
                (column_name, data_type),
            )

            add_log(
                cursor,
                session["user"],
                "Sütun Ekle",
                column_name,
                f"'{column_name}' sütunu eklendi, veri tipi={data_type}",
            )

            conn.commit()
            conn.close()

            flash(translations["added_new_column"],"success")
            return redirect(url_for("index"))

        conn.close()
        return render_template("addcolumn.html", translations=translations, lang=lang)
    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Database error"),"error")
        return redirect(url_for("index"))


@app.route("/editcolumn/<int:id>", methods=["POST"])
@admin_required
def editcolumn(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")
        return redirect(url_for("index"))

    try:
        column_name = request.form["columnName"].strip()
        data_type = request.form["dataType"]

        cursor.execute(
            """
            SELECT column_name, data_type
            FROM custom_columns
            WHERE id=%s
            """,
            (id,),
        )

        current = cursor.fetchone()

        if not current:
            conn.close()
            flash(translations.get("error", "Column not found"),"error")
            return redirect(url_for("index"))

        old_column_name = current["column_name"]
        old_data_type = current["data_type"]

        changes = []

        if str(old_column_name or "") != str(column_name):
            changes.append(
                f"Sütun Adı: '{old_column_name}' → '{column_name}'"
            )

        if str(old_data_type or "") != str(data_type):
            changes.append(
                f"Veri Tipi: '{old_data_type}' → '{data_type}'"
            )

        cursor.execute(
            """
            UPDATE custom_columns
            SET column_name=%s, data_type=%s
            WHERE id=%s
            """,
            (column_name, data_type, id),
        )

        if old_data_type != data_type:
            cursor.execute(
                "DELETE FROM custom_values WHERE column_id=%s",
                (id,),
            )

            flash(translations["update_column_override"],"success")
        else:
            flash(translations["update_column"],"success")

        for change in changes:
            add_log(
                cursor,
                session["user"],
                "Sütun Düzenle",
                column_name,
                change
            )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    except Exception as e:
        print(e)

        if conn:
            conn.close()

        flash(translations.get("error", "Database error"),"error")

        return redirect(url_for("index"))


@app.route("/deleteColumn/<int:id>", methods=["POST"])
@admin_required
def deleteColumn(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")
        return redirect(url_for("index"))

    try:
        cursor.execute("SELECT * FROM custom_columns WHERE id=%s", (id,))
        column_name = cursor.fetchone()["column_name"]

        cursor.execute("DELETE FROM custom_values WHERE column_id = %s", (id,))
        cursor.execute("DELETE FROM custom_columns WHERE id = %s", (id,))

        add_log(
            cursor,
            session["user"],
            "Sütun Sil",
            column_name,
            f"'{column_name}' sütunu silindi.",
        )

        conn.commit()
        conn.close()

        flash(translations["f_delete_column"],"success")
        return redirect(url_for("index"))

    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Database error"),"error")
        return redirect(url_for("index"))
    
@app.route("/clients")
def clients():

    if "user" not in session:
        return redirect(url_for("login"))

    conn, cursor, is_connected = get_db()

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    if not is_connected:
        flash("Veritabanına bağlanılamadı.","error")
        return redirect(url_for("index"))

    try:
        cursor.execute("""
            SELECT
                id,
                hostname,
                ip_address,
                username,
                os_name,
                last_seen
            FROM clients
            ORDER BY hostname
        """)

        clients = cursor.fetchall()

        conn.close()

        return render_template(
            "clients.html",
            clients=clients,
            translations=translations,
            lang=lang,
            username=session.get("user"),
            is_admin=session.get("is_admin", False)
        )

    except Exception as e:
        print("Clients error:", e)

        if conn:
            conn.close()

        flash("Client bilgileri alınamadı.","error")
        return redirect(url_for("index"))


@app.route("/clients/search")
def clients_search():
    if "user" not in session:
        return redirect(url_for("login"))

    conn, cursor, is_connected = get_db()
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    if not is_connected:
        flash("Veritabanına bağlanılamadı.", "error")
        return redirect(url_for("clients"))

    try:
        q = request.args.get("q", "").strip()
        fields = request.args.getlist("fields")

        if not q:
            if conn:
                conn.close()
            return redirect(url_for("clients"))

        if not fields:
            if conn:
                conn.close()
            flash(translations.get("select_at_least_one_field", "Lütfen en az bir arama alanı seçin."), "error")
            return redirect(url_for("clients"))

        allowed_fields = {
            "hostname": "hostname",
            "ip_address": "ip_address",
            "username": "username",
            "os_name": "os_name",
            "last_seen": "last_seen",
        }

        selected_fields = []
        for field in fields:
            if field in allowed_fields:
                selected_fields.append(allowed_fields[field])

        if q and not selected_fields:
            selected_fields = list(allowed_fields.values())

        sql = """
            SELECT
                id,
                hostname,
                ip_address,
                username,
                os_name,
                last_seen
            FROM clients
        """
        values = []

        if q and selected_fields:
            conditions = []
            for field in selected_fields:
                conditions.append(f"CAST({field} AS CHAR) LIKE %s")
                values.append(f"%{q}%")
            sql += " WHERE " + " OR ".join(conditions)

        sql += " ORDER BY hostname"

        cursor.execute(sql, values)
        clients = cursor.fetchall()
        conn.close()

        return render_template(
            "clients.html",
            clients=clients,
            translations=translations,
            lang=lang,
            username=session.get("user"),
            is_admin=session.get("is_admin", False),
        )
    except Exception as e:
        print("Clients search error:", e)
        if conn:
            conn.close()
        flash("Client arama hatası.", "error")
        return redirect(url_for("clients"))
    
@app.route("/networkdevices")
def networkdevices():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    username = session.get("user", "Unknown")
    is_admin = session.get("is_admin", False)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash(
            translations.get("error", "Database disconnected"),
            "error"
        )

        return render_template(
            "networkdevices.html",
            translations=translations,
            lang=lang,
            username=username,
            is_admin=is_admin,
            devices=[],
            device_types=[]
        )

    try:
        cursor.execute("""
            SELECT
                id,
                name,
                device_type,
                brand,
                model,
                serial_number,
                ip_address,
                mac_address,
                location,
                status,
                software_version,
                description,
                created_at,
                updated_at
            FROM network_devices
            ORDER BY id DESC
        """)

        devices = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT device_type
            FROM network_devices
            WHERE device_type IS NOT NULL
              AND device_type != ''
              AND device_type NOT IN (
                  'Switch',
                  'Router',
                  'Firewall',
                  'Access Point',
                  'Modem',
                  'Diğer'
              )
            ORDER BY device_type
        """)

        device_types = [row["device_type"] for row in cursor.fetchall()]

        conn.close()

        return render_template(
            "networkdevices.html",
            translations=translations,
            lang=lang,
            username=username,
            is_admin=is_admin,
            devices=devices,
            device_types=device_types
        )

    except Exception as e:
        print(e)

        if conn:
            conn.close()

        flash(
            translations.get("error", "Database error"),
            "error"
        )

        return render_template(
            "networkdevices.html",
            translations=translations,
            lang=lang,
            username=username,
            is_admin=is_admin,
            devices=[],
            device_types=[]
        )
    
@app.route("/addnetworkdevice", methods=["POST"])
@admin_required
def addnetworkdevice():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash(translations.get("error", "Database disconnected"),"error")
        return redirect(url_for("networkdevices"))

    try:
        name = request.form["name"].strip()
        device_type = request.form["device_type"]
        
        if device_type == "Diğer":
            device_type = request.form.get("other_device_type", "").strip()
            
            if not device_type:
                flash("Lütfen cihaz türünü girin.", "error")
                conn.close()
                return redirect(url_for("addnetworkdevice_page"))
            
        brand = request.form["brand"].strip()
        model = request.form["model"].strip()
        serial_number = request.form["serial_number"].strip()
        ip_address = request.form["ip_address"].strip()
        mac_address = request.form["mac_address"].strip()
        location = request.form["location"].strip()
        status = request.form["status"]
        software_version = request.form["software_version"].strip()
        description = request.form["description"].strip()
        created_at = request.form["created_at"] or None

        cursor.execute(
            """
            INSERT INTO network_devices
            (
                name,
                device_type,
                brand,
                model,
                serial_number,
                ip_address,
                mac_address,
                location,
                status,
                software_version,
                description,
                created_at,
                updated_at
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, NOW()
            )
            """,
            (
                name,
                device_type,
                brand,
                model,
                serial_number,
                ip_address,
                mac_address,
                location,
                status,
                software_version,
                description,
                created_at,
            ),
        )

        add_log(
            cursor,
            session["user"],
            "Ağ Cihazı Ekle",
            name,
            f"Ağ cihazı eklendi: {name}"
        )

        conn.commit()
        conn.close()

        flash("Ağ cihazı başarıyla eklendi.","success")
        return redirect(url_for("networkdevices"))

    except Exception as e:
        print(e)

        if conn:
            conn.close()

        flash(translations.get("error", "Error adding network device"))
        return redirect(url_for("networkdevices"))   
    
@app.route("/addnetworkdevice")
@admin_required
def addnetworkdevice_page():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    device_types = []

    if is_connected:
        try:
            cursor.execute("""
                SELECT DISTINCT device_type
                FROM network_devices
                WHERE device_type IS NOT NULL
                  AND device_type != ''
                  AND device_type NOT IN (
                      'Switch',
                      'Router',
                      'Firewall',
                      'Access Point',
                      'Modem',
                      'Diğer'
                  )
                ORDER BY device_type
            """)

            device_types = [
                row["device_type"]
                for row in cursor.fetchall()
            ]

        finally:
            conn.close()

    return render_template(
        "addnetworkdevice.html",
        translations=translations,
        lang=lang,
        device_types=device_types
    )


@app.route("/deletenetworkdevice/<int:id>")
@admin_required
def deletenetworkdevice(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Veritabanı hatası."), "error")
        return redirect(url_for("networkdevices"))

    try:
        cursor.execute("SELECT name FROM network_devices WHERE id = %s", (id,))
        device = cursor.fetchone()
        dev_name = device["name"] if device else f"ID {id}"

        cursor.execute("DELETE FROM network_devices WHERE id = %s", (id,))

        add_log(
            cursor,
            session["user"],
            "Ağ Cihazı Sil",
            dev_name,
            f"'{dev_name}' ağ cihazı silindi."
        )

        conn.commit()
        conn.close()
        flash("Ağ cihazı silindi!", "success")
    except Exception as e:
        print("Delete network device error:", e)
        if conn:
            conn.close()
        flash(translations.get("error", "Silme işlemi başarısız."), "error")

    return redirect(url_for("networkdevices"))


@app.route("/editnetworkdevice/<int:id>", methods=["POST"])
@admin_required
def editnetworkdevice(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Veritabanı hatası."), "error")
        return redirect(url_for("networkdevices"))

    try:
        cursor.execute("SELECT * FROM network_devices WHERE id = %s", (id,))
        old_device = cursor.fetchone()

        if not old_device:
            conn.close()
            flash("Cihaz bulunamadı.", "error")
            return redirect(url_for("networkdevices"))

        name = request.form.get("name", "").strip()
        device_type = request.form.get("device_type", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        serial_number = request.form.get("serial_number", "").strip()
        ip_address = request.form.get("ip_address", "").strip()
        mac_address = request.form.get("mac_address", "").strip()
        location = request.form.get("location", "").strip()
        status = request.form.get("status", "").strip()
        software_version = request.form.get("software_version", "").strip()
        description = request.form.get("description", "").strip()

        form_data = {
            "name": name,
            "device_type": device_type,
            "brand": brand,
            "model": model,
            "serial_number": serial_number,
            "ip_address": ip_address,
            "mac_address": mac_address,
            "location": location,
            "status": status,
            "software_version": software_version,
            "description": description,
        }

        field_labels = [
            ("name", "Cihaz Adı"),
            ("device_type", "Tür"),
            ("brand", "Marka"),
            ("model", "Model"),
            ("serial_number", "Seri Numarası"),
            ("ip_address", "IP Adresi"),
            ("mac_address", "MAC Adresi"),
            ("location", "Lokasyon"),
            ("status", "Durum"),
            ("software_version", "Software Version"),
            ("description", "Açıklama"),
        ]

        changes = []
        for field_key, label in field_labels:
            old_val = str(old_device.get(field_key) or "")
            new_val = str(form_data.get(field_key) or "")
            if old_val != new_val:
                changes.append(f"{label}: '{old_val}' → '{new_val}'")

        cursor.execute(
            """
            UPDATE network_devices
            SET name=%s, device_type=%s, brand=%s, model=%s, serial_number=%s,
                ip_address=%s, mac_address=%s, location=%s, status=%s,
                software_version=%s, description=%s, updated_at=NOW()
            WHERE id=%s
            """,
            (name, device_type, brand, model, serial_number, ip_address,
             mac_address, location, status, software_version, description, id)
        )

        target_name = old_device.get("name") or name
        for change in changes:
            add_log(cursor, session["user"], "Ağ Cihazı Düzenle", target_name, change)

        conn.commit()
        conn.close()
        flash("Ağ cihazı güncellendi!", "success")
    except Exception as e:
        print("Edit network device error:", e)
        if conn:
            conn.close()
        flash(translations.get("error", "Güncelleme hatası."), "error")

    return redirect(url_for("networkdevices"))


def ensure_backup_settings_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS backup_settings (
            id INT PRIMARY KEY DEFAULT 1,
            is_enabled TINYINT(1) DEFAULT 0,
            frequency VARCHAR(20) DEFAULT 'daily',
            backup_day VARCHAR(20) DEFAULT 'mon',
            backup_time VARCHAR(10) DEFAULT '03:00',
            backup_folder VARCHAR(255) DEFAULT '',
            max_backup_count INT DEFAULT 10,
            delete_old_backups TINYINT(1) DEFAULT 1,
            last_backup_date VARCHAR(50) DEFAULT NULL,
            last_backup_status VARCHAR(255) DEFAULT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
    )
    try:
        cursor.execute("ALTER TABLE backup_settings ADD COLUMN backup_day VARCHAR(20) DEFAULT 'mon'")
    except Exception:
        pass

    cursor.execute(
        """
        INSERT INTO backup_settings (id, is_enabled, frequency, backup_day, backup_time, backup_folder, max_backup_count, delete_old_backups)
        SELECT 1, 0, 'daily', 'mon', '03:00', '', 10, 1
        WHERE NOT EXISTS (SELECT 1 FROM backup_settings WHERE id = 1)
        """
    )


@app.route("/api/backup/select-folder", methods=["POST"])
@admin_required
def select_backup_folder_dialog():
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        selected_directory = filedialog.askdirectory(
            title="Yedekleme Klasörünü Seçin"
        )
        root.destroy()

        if selected_directory:
            selected_directory = selected_directory.replace("/", "\\")
            return jsonify({"success": True, "folder": selected_directory}), 200
        else:
            return jsonify({"success": False, "message": "Klasör seçilmedi."}), 200
    except Exception as e:
        print("Folder picker dialog error:", e)
        return jsonify({"error": "Klasör seçici açılamadı: " + str(e)}), 500


@app.route("/api/backup/settings", methods=["GET"])
@admin_required
def get_backup_settings():
    conn, cursor, is_connected = get_db()
    if not is_connected:
        return jsonify({"error": "Veritabanına bağlanılamadı."}), 500

    try:
        ensure_backup_settings_table(cursor)
        conn.commit()

        cursor.execute("SELECT * FROM backup_settings WHERE id = 1")
        settings = cursor.fetchone()
        if not settings:
            settings = {
                "id": 1,
                "is_enabled": 0,
                "frequency": "daily",
                "backup_day": "mon",
                "backup_time": "03:00",
                "backup_folder": "",
                "max_backup_count": 10,
                "delete_old_backups": 1,
                "last_backup_date": None,
                "last_backup_status": None
            }

        return jsonify({"success": True, "settings": settings}), 200
    except Exception as e:
        print("Backup settings fetch error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/backup/settings", methods=["POST"])
@admin_required
def save_backup_settings():
    conn, cursor, is_connected = get_db()
    if not is_connected:
        return jsonify({"error": "Veritabanına bağlanılamadı."}), 500

    try:
        ensure_backup_settings_table(cursor)

        data = request.get_json() or {}

        is_enabled = 1 if data.get("is_enabled") else 0
        frequency = data.get("frequency", "daily").strip()
        backup_day = data.get("backup_day", "mon").strip()
        backup_time = data.get("backup_time", "03:00").strip()
        backup_folder = data.get("backup_folder", "").strip()
        max_backup_count = int(data.get("max_backup_count", 10))
        delete_old_backups = 1 if data.get("delete_old_backups") else 0

        cursor.execute(
            """
            INSERT INTO backup_settings
                (id, is_enabled, frequency, backup_day, backup_time, backup_folder, max_backup_count, delete_old_backups)
            VALUES (1, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                is_enabled = VALUES(is_enabled),
                frequency = VALUES(frequency),
                backup_day = VALUES(backup_day),
                backup_time = VALUES(backup_time),
                backup_folder = VALUES(backup_folder),
                max_backup_count = VALUES(max_backup_count),
                delete_old_backups = VALUES(delete_old_backups)
            """,
            (is_enabled, frequency, backup_day, backup_time, backup_folder, max_backup_count, delete_old_backups)
        )
        conn.commit()

        update_backup_schedule(is_enabled, frequency, backup_day, backup_time, backup_folder, max_backup_count, delete_old_backups, get_db, DB_CONFIG, add_log)

        return jsonify({"success": True, "message": "Yedekleme ayarları kaydedildi."}), 200
    except Exception as e:
        print("Backup settings save error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def parse_ad_timestamp(val):
    if not val:
        return None
    try:
        if isinstance(val, (list, tuple)) and len(val) > 0:
            val = val[0]
            
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%d %H:%M:%S")

        num_val = int(str(val).strip())
        if num_val <= 0 or num_val == 9223372036854775807:
            return None

        days = num_val // 864000000000
        rem = num_val % 864000000000
        seconds = rem // 10000000
        microseconds = (rem % 10000000) // 10

        start = datetime(1601, 1, 1)
        dt = start + timedelta(days=days, seconds=seconds, microseconds=microseconds)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("AD timestamp parse error:", e)
        return None


@app.route("/api/clients/sync_ad", methods=["POST"])
@admin_required
def sync_clients_from_ad():
    if not session.get("is_admin"):
        return jsonify({"error": "Bu işlem için admin yetkisi gereklidir."}), 403

    load_dotenv(find_dotenv(), override=True)

    if not AD_SERVER or not AD_DOMAIN:
        return jsonify({"error": "Active Directory (LDAP) sunucu bilgileri yapılandırılmamış."}), 400

    data = request.get_json() or {}
    ad_user = data.get("ad_user", "").strip() or os.getenv("LDAP_BIND_USER") or os.getenv("AD_USER")
    ad_pass = data.get("ad_password", "").strip() or os.getenv("LDAP_BIND_PASSWORD") or os.getenv("AD_PASSWORD")

    if ad_user and "\\" not in ad_user and "@" not in ad_user:
        ad_user = f"{ad_user}@{AD_DOMAIN}"

    if not ad_user or not ad_pass:
        return jsonify({
            "error": "Lütfen Active Directory kullanıcı adı ve şifrenizi girin."
        }), 400

    try:
        server = Server(AD_SERVER, get_info=NONE)
        conn_ad = Connection(
            server,
            user=ad_user,
            password=ad_pass,
            authentication=SIMPLE,
            raise_exceptions=True
        )

        if not conn_ad.bind():
            return jsonify({"error": "Active Directory bağlantısı kurulamadı."}), 500

        custom_search_base = os.getenv("LDAP_SEARCH_BASE") or os.getenv("AD_SEARCH_BASE")
        if custom_search_base:
            search_base = custom_search_base.strip()
        else:
            search_base = ",".join([f"DC={x}" for x in AD_DOMAIN.split(".")])

        target_ou = os.getenv("LDAP_TARGET_OU") or os.getenv("AD_TARGET_OU")
        if target_ou:
            search_filter = f"(&(objectCategory=computer)(objectClass=computer)(operatingSystem=Windows*)(!(operatingSystem=*Server*))(distinguishedName=*{target_ou.strip()}*))"
        else:
            search_filter = "(&(objectCategory=computer)(objectClass=computer)(operatingSystem=Windows*)(!(operatingSystem=*Server*)))"

        attributes = ["cn", "dNSHostName", "operatingSystem", "description", "distinguishedName", "lastLogonTimestamp", "lastLogon"]

        conn_ad.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=attributes
        )

        conn_db, cursor, is_connected = get_db()
        if not is_connected:
            return jsonify({"error": "Veritabanı bağlantısı kurulamadı."}), 500

        added_count = 0
        updated_count = 0

        for entry in conn_ad.entries:
            hostname = str(entry.cn.value) if entry.cn and entry.cn.value else ""
            if not hostname:
                continue

            dns_name = str(entry.dNSHostName.value) if entry.dNSHostName and entry.dNSHostName.value else hostname
            os_name = str(entry.operatingSystem.value) if entry.operatingSystem and entry.operatingSystem.value else "Windows"
            description = str(entry.description.value) if entry.description and entry.description.value else ""

            raw_logon = (entry.lastLogon.value if hasattr(entry, "lastLogon") and entry.lastLogon else None) or (entry.lastLogonTimestamp.value if hasattr(entry, "lastLogonTimestamp") and entry.lastLogonTimestamp else None)
            last_seen_val = parse_ad_timestamp(raw_logon)

            cursor.execute("SELECT id FROM clients WHERE hostname = %s", (hostname,))
            existing = cursor.fetchone()

            if existing:
                if last_seen_val:
                    cursor.execute("""
                        UPDATE clients
                        SET ip_address = %s,
                            username = %s,
                            os_name = %s,
                            last_seen = %s
                        WHERE hostname = %s
                    """, (dns_name, description, os_name, last_seen_val, hostname))
                else:
                    cursor.execute("""
                        UPDATE clients
                        SET ip_address = %s,
                            username = %s,
                            os_name = %s
                        WHERE hostname = %s
                    """, (dns_name, description, os_name, hostname))
                updated_count += 1
            else:
                cursor.execute("""
                    INSERT INTO clients (hostname, ip_address, username, os_name, last_seen)
                    VALUES (%s, %s, %s, %s, %s)
                """, (hostname, dns_name, description, os_name, last_seen_val or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                added_count += 1

        conn_db.commit()

        username = session.get("user", "System")
        add_log(
            cursor,
            username,
            "AD Senkronizasyon",
            "Clients",
            f"Active Directory'den {added_count} yeni bilgisayar eklendi, {updated_count} güncellendi."
        )
        conn_db.commit()

        cursor.close()
        conn_db.close()
        conn_ad.unbind()

        return jsonify({
            "success": True,
            "message": f"Active Directory senkronizasyonu başarılı: {added_count} bilgisayar eklendi, {updated_count} güncellendi."
        }), 200

    except Exception as e:
        print("AD Sync Error:", e)
        return jsonify({"error": f"AD Senkronizasyon Hatası: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
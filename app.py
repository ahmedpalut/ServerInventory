from flask import *
from datetime import datetime
from dotenv import load_dotenv
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

load_dotenv()


def get_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            connect_timeout=2,
        )
        return conn, conn.cursor(dictionary=True), True
    except Exception:
        return None, None, False


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

AD_SERVER = os.getenv("LDAP_SERVER")
AD_DOMAIN = os.getenv("LDAP_DOMAIN")


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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lang = session.get("lang", "tr")
        translations = get_translation(lang)
        if not session.get("is_admin"):
            flash(translations["permission"])
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function

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
            SET last_seen = NOW(),
                status = %s
            WHERE username = %s
              AND ip_address = %s
        """, ("online", username, client_ip))

        conn.commit()

    finally:
        cursor.close()
        conn.close()

@app.route("/database/restore", methods=["POST"])
@admin_required
def database_restore():

    mysql_path = r"C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe"

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME")

    file = request.files.get("database_file")

    if not file or file.filename == "":
        flash("SQL dosyası seçilmedi.")
        return redirect(url_for("database"))

    if not file.filename.lower().endswith(".sql"):
        flash("Sadece .sql dosyaları yüklenebilir.")
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
            f.write(sql_content)

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

            flash(f"Restore error: {error_message}")
            return redirect(url_for("database"))

        flash("Veritabanı başarıyla geri yüklendi.")
        return redirect(url_for("database"))

    except Exception as e:

        flash(f"Restore error: {e}")
        return redirect(url_for("database"))

    finally:

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.route("/backup_database")
@admin_required
def backup_database():

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash("Veritabanına bağlı değil.")
        return redirect(url_for("database"))

    conn.close()

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")

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

            flash(f"Backup error: {error_message}")
            return redirect(url_for("database"))

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

        flash(f"Backup error: {e}")
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
                flash(translations["login_s"])

                conn_db, cursor, is_connected = get_db()

                if is_connected:
                    client_ip = request.remote_addr

                    cursor.execute("""
                        SELECT hostname
                        FROM clients
                        WHERE username = %s AND ip_address = %s
                    """, (username, client_ip))

                    client = cursor.fetchone()

                    if client:
                        cursor.execute("""
                            UPDATE clients
                            SET status = %s,
                                site_status = %s,
                                last_seen = NOW()
                            WHERE username = %s AND ip_address = %s
                        """, ("online", "active", username, client_ip))

                    else:
                        cursor.execute("""
                            INSERT INTO clients
                                (hostname, ip_address, username, os_name, status, site_status, last_seen)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, NOW())
                        """, (
                            "Unknown",
                            client_ip,
                            username,
                            None,
                            "online",
                            "active"
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
                flash(translations["name_error"])
                return redirect(url_for("login"))

        except Exception as e:
            print("LOGIN HATASI:", repr(e))
            flash(translations["error"])
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
        cursor.execute("""
            UPDATE clients
            SET site_status = %s
            WHERE username = %s
        """, ("inactive", username))

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

    flash(translations["logout_s"])

    return redirect(url_for("login"))


@app.route("/start_database", methods=["POST"])
@admin_required
def start_database():

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if is_connected:
        conn.close()
        flash("Veritabanı zaten bağlı.")
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
                flash("Veritabanına başarıyla bağlanıldı.")
                return redirect(url_for("database"))

        flash("MySQL servisi başlatılamadı.")

    except Exception as e:
        print(e)
        flash("Bir hata oluştu.")

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
            db_name="",
            logs=[],
        )

    try:

        cursor.execute("SELECT COUNT(*) AS total FROM servers")
        server_count = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM information_schema.tables WHERE table_schema = %s",
            (os.getenv("DB_NAME"),),
        )
        table_count = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT 
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb 
            FROM information_schema.tables 
            WHERE table_schema = %s
            """,
            (os.getenv("DB_NAME"),),
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
            db_name=os.getenv("DB_NAME"),
        )

    except Exception:
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
            db_status=translations["connection_status_online"],
            db_size="0 MB",
            table_count=0,
            server_count=0,
        )


@app.route("/edit/<int:id>", methods=["POST"])
@admin_required
def edit(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()

    if not is_connected:
        flash(translations.get("error", "Database disconnected"))
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
            flash(translations.get("error", "Server not found"))
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

        if request.form["server"] == "Yeni":
            os_name = request.form["isletim"]

            cursor.execute("INSERT INTO os_types (name) VALUES (%s)", (os_name,))

            conn.commit()
            os_type_id = cursor.lastrowid

        else:
            os_name = request.form["server"]

            cursor.execute("SELECT id FROM os_types WHERE name=%s", (os_name,))

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
            add_log(cursor, session["user"], "Düzenle", name, change)

        conn.commit()
        conn.close()

        flash(translations["server_updated"])
        return redirect(url_for("index"))

    except Exception as e:
        print(e)

        if conn:
            conn.close()

        flash(translations.get("error", "Error updating server"))

        return redirect(url_for("index"))


@app.route("/delete/<int:id>")
@admin_required
def delete(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"))
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

        flash(translations["delete_server_s"])
        return redirect(url_for("index"))
    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Error deleting server"))
        return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
@admin_required
def add():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"))
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

            flash(translations["server_added"])
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
        flash(translations.get("error", "Database error"))
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

        if not fields:
            fields = ["name"]

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


@app.route("/addcolumn", methods=["GET", "POST"])
@admin_required
def addcolumn():
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"))
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
                flash(translations["col_already_exists"])
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

            flash(translations["added_new_column"])
            return redirect(url_for("index"))

        conn.close()
        return render_template("addcolumn.html", translations=translations, lang=lang)
    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Database error"))
        return redirect(url_for("index"))


@app.route("/editcolumn/<int:id>", methods=["POST"])
@admin_required
def editcolumn(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"))
        return redirect(url_for("index"))

    try:
        column_name = request.form["columnName"].strip()
        data_type = request.form["dataType"]

        cursor.execute("SELECT data_type FROM custom_columns WHERE id=%s", (id,))
        current = cursor.fetchone()
        old_data_type = current["data_type"]

        cursor.execute(
            """
            UPDATE custom_columns
            SET column_name=%s, data_type=%s
            WHERE id=%s
            """,
            (column_name, data_type, id),
        )

        if old_data_type != data_type:
            cursor.execute("DELETE FROM custom_values WHERE column_id=%s", (id,))
            flash(translations["update_column_override"])
        else:
            flash(translations["update_column"])

        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Database error"))
        return redirect(url_for("index"))


@app.route("/deleteColumn/<int:id>", methods=["POST"])
@admin_required
def deleteColumn(id):
    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    conn, cursor, is_connected = get_db()
    if not is_connected:
        flash(translations.get("error", "Database disconnected"))
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

        flash(translations["f_delete_column"])
        return redirect(url_for("index"))

    except Exception:
        if conn:
            conn.close()
        flash(translations.get("error", "Database error"))
        return redirect(url_for("index"))
    
@app.route("/clients")
def clients():

    if "user" not in session:
        return redirect(url_for("login"))

    conn, cursor, is_connected = get_db()

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    if not is_connected:
        flash("Veritabanına bağlanılamadı.")
        return redirect(url_for("index"))

    try:
        cursor.execute("""
        UPDATE clients
        SET status = 'offline'
        WHERE last_seen IS NULL
        OR last_seen < NOW() - INTERVAL 2 MINUTE
        """)

        conn.commit()
        
        cursor.execute("""
            SELECT
                id,
                hostname,
                ip_address,
                username,
                os_name,
                status,
                site_status,
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

        flash("Client bilgileri alınamadı.")
        return redirect(url_for("index"))
    
@app.route("/api/client/update", methods=["POST"])
def client_update():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Veri alınamadı"}), 400

    hostname = data.get("hostname")
    username = data.get("username")
    os_name = data.get("os_name")
    ip_address = data.get("ip_address")

    if not hostname or not username:
        return jsonify({"error": "Eksik bilgi"}), 400

    conn, cursor, is_connected = get_db()

    if not is_connected:
        return jsonify({"error": "Veritabanına bağlanılamadı"}), 500

    try:
        cursor.execute("""
            SELECT id
            FROM clients
            WHERE hostname = %s
        """, (hostname,))

        client = cursor.fetchone()

        if client:
            cursor.execute("""
                UPDATE clients
                SET ip_address = %s,
                    username = %s,
                    os_name = %s,
                    status = %s,
                    last_seen = NOW()
                WHERE hostname = %s
            """, (
                ip_address,
                username,
                os_name,
                "online",
                hostname
            ))

        else:
            cursor.execute("""
                INSERT INTO clients
                    (hostname, ip_address, username, os_name, status, site_status, last_seen)
                VALUES
                    (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                hostname,
                ip_address,
                username,
                os_name,
                "online",
                "inactive"
            ))

        conn.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        print("CLIENT AGENT HATASI:", repr(e))
        conn.rollback()
        return jsonify({"error": "Sunucu hatası"}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

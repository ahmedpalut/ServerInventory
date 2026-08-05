from flask import *
import mysql.connector
import os
from dotenv import load_dotenv
from ldap3 import Server, Connection, SUBTREE, SIMPLE, NONE
from functools import wraps
import json

load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor=mydb.cursor(dictionary=True)

app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY")

AD_SERVER = os.getenv("LDAP_SERVER") 
AD_DOMAIN = os.getenv("LDAP_DOMAIN") 

def get_translation(lang="tr"):
    with open(f"static/js/translations/{lang}.json", encoding="utf-8") as file:
        return json.load(file)
    
@app.route("/change_language/<lang>")
def change_language(lang):

    if lang in ["tr", "en"]:
        session["lang"] = lang

    return redirect(request.referrer or url_for("index"))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lang = session.get("lang","tr")

        translations = get_translation(lang)

        if not session.get("is_admin"):
            flash(translations["permission"])
            return redirect(url_for("index"))

        return f(*args, **kwargs)

    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    lang = session.get("lang","tr")

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
                raise_exceptions=True
            )

            if conn.bind():

                search_base = ",".join(
                    [f"DC={x}" for x in AD_DOMAIN.split(".")]
                )

                conn.search(
                    search_base=search_base,
                    search_filter=f"(sAMAccountName={username})",
                    search_scope=SUBTREE,
                    attributes=["memberOf"]
                )

                role = "Visitor"

                print(f"\n=== {username} kullanıcısının grupları ===")

                if conn.entries:

                    groups = conn.entries[0]["memberOf"]

                    for group in groups:
                        print(group)

                        group = str(group)

                        if "CN=Test Admin," in group:
                            role = "Admin"

                        elif "CN=Domain Admins," in group:
                            role = "Admin"

                else:
                    print("Grup bilgisi bulunamadı.")

                print("========================================\n")
                
                session.clear()

                session["user"] = username
                session["role"] = role
                session["is_admin"] = (role == "Admin")

                flash(translations["login_s"])

                return redirect(url_for("index"))

            else:
                flash(translations["name_error"])
                return redirect(url_for("login"))

        except Exception as e:
            print(e)
            flash(translations["error"])

            if conn:
                conn.unbind()

            return redirect(url_for("login"))

        finally:
            if conn:
                conn.unbind()

    return render_template(
        "login.html",
        translations=translations,
        lang=lang)


@app.route("/logout")
def logout():
    lang = session.get("lang","tr")

    translations = get_translation(lang)
    session.clear()

    flash(translations["logout_s"])
    return redirect(url_for("login"))



@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    
    lang = session.get("lang","tr")

    translations = get_translation(lang)
    
    cursor.execute("""
        SELECT *
        FROM custom_columns
        ORDER BY column_name
        """)

    custom_columns = cursor.fetchall()
    
    cursor.execute("""
    SELECT server_id,column_id,value
    FROM custom_values
    """)

    rows = cursor.fetchall()

    custom_values = {}

    for row in rows:

        server_id = row["server_id"]

        if server_id not in custom_values:
            custom_values[server_id] = {}

        custom_values[server_id][row["column_id"]] = row["value"]

    cursor.execute("""
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
        LEFT JOIN os_types o
        ON s.os_type_id = o.id
    """)

    servers = cursor.fetchall()
    
    for server in servers:
        server["custom_values"] = custom_values.get(server["id"], {})

    windows_amount = sum(
        1 for s in servers
        if s["os_name"] and "windows" in s["os_name"].lower()
    )

    cursor.execute("SELECT name FROM os_types ORDER BY name")
    os_list = cursor.fetchall()

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
        lang=lang
    )
    
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    cursor.execute("""
        SELECT
            o.name AS os_name,
            COUNT(*) AS total
        FROM servers s
        LEFT JOIN os_types o
            ON s.os_type_id = o.id
        GROUP BY o.name
        ORDER BY total DESC
    """)

    os_stats = cursor.fetchall()

    labels = [row["os_name"] or "Unknown" for row in os_stats]
    values = [row["total"] for row in os_stats]
    
    cursor.execute("""
        SELECT disk_gb
        FROM servers
    """)

    disk_data = cursor.fetchall()

    disk_labels = [
        "0-100 GB",
        "100-250 GB",
        "250-500 GB",
        "500 GB-1 TB",
        "1-2 TB",
        "2-5 TB",
        "5-10 TB",
        "10+ TB"
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

    return render_template(
        "dashboard.html",
        translations=translations,
        lang=lang,
        username=session.get("user"),
        is_admin=session.get("is_admin"),
        labels=labels,
        values=values,
        disk_labels=json.dumps(disk_labels),
        disk_values=json.dumps(disk_values),
        total_servers=sum(values)
    )


@app.route("/database")
def database():

    if "user" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "tr")
    translations = get_translation(lang)

    return render_template(
        "database.html",
        translations=translations,
        lang=lang,
        username=session.get("user"),
        role=session.get("role"),
        is_admin=session.get("is_admin")
    )

@app.route("/edit/<int:id>", methods=["POST"])
@admin_required
def edit(id):
    
    lang = session.get("lang","tr")

    translations = get_translation(lang)

    name = request.form["ad"]
    disk = float(request.form["disk"])
    ram = int(request.form["ram"])
    ip = request.form["ip"]
    project = request.form["project"]
    cpu = int(request.form["cpu"])
    date = request.form["date"] or None
    disk_type=request.form["disktur"]
    
    if(disk_type.upper() == "TB"):
        disk*=1024

    if request.form["server"] == "Yeni":
        os_name = request.form["isletim"]

        cursor.execute(
            "INSERT INTO os_types (name) VALUES (%s)",
            (os_name,)
        )
        mydb.commit()

        os_type_id = cursor.lastrowid

    else:
        os_name = request.form["server"]

        cursor.execute(
            "SELECT id FROM os_types WHERE name = %s",
            (os_name,)
        )

        result = cursor.fetchone()
        os_type_id = result["id"]

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

    values = (
        name,
        disk,
        ram,
        ip,
        project,
        cpu,
        os_type_id,
        date,
        id
    )
    
    cursor.execute("""
        SELECT id, data_type
        FROM custom_columns
    """)

    custom_columns = cursor.fetchall()

    for column in custom_columns:

        value = request.form.get(f"custom_{column['id']}")

        if column["data_type"] == "BOOLEAN":
            value = "True" if value else "False"

        cursor.execute("""
            SELECT id
            FROM custom_values
            WHERE server_id=%s AND column_id=%s
        """, (id, column["id"]))

        exists = cursor.fetchone()

        if value not in ("", None):

            if exists:

                cursor.execute("""
                    UPDATE custom_values
                    SET value=%s
                    WHERE server_id=%s AND column_id=%s
                """, (
                    value,
                    id,
                    column["id"]
                ))

            else:

                cursor.execute("""
                    INSERT INTO custom_values
                    (server_id, column_id, value)
                    VALUES (%s, %s, %s)
                """, (
                    id,
                    column["id"],
                    value
                ))

        elif exists:

            cursor.execute("""
                DELETE FROM custom_values
                WHERE server_id=%s AND column_id=%s
            """, (
                id,
                column["id"]
            ))

    cursor.execute(sql, values)
    mydb.commit()
    
    flash(translations["server_updated"])

    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
@admin_required
def sil(id):
    lang = session.get("lang","tr")

    translations = get_translation(lang)

    cursor.execute("""
        DELETE FROM custom_values
        WHERE server_id = %s
    """, (id,))

    cursor.execute("""
        DELETE FROM servers
        WHERE id = %s
    """, (id,))

    mydb.commit()

    flash(translations["delete_server_s"])

    return redirect(url_for("index"))


@app.route("/add", methods=["GET","POST"])
@admin_required
def ekle():
    lang = session.get("lang","tr")

    translations = get_translation(lang)
    
    
    if request.method=="POST":
        name=request.form["ad"]
        disk_gb=float(request.form["disk"])
        ram_g=int(request.form["ram"])
        core_amount=int(request.form["cpu"])
        ip_address=request.form["ip"]
        usage_project=request.form["aciklama"]
        created_at=request.form["tarih"]
        
        if created_at=="":
            created_at=None
        
        if request.form["server"]=="Yeni":
            os=request.form["isletim"]
            os_sql="insert into os_types (name) values(%s)"
            os_values=(os,)
            cursor.execute(os_sql,os_values)
            mydb.commit()
            os_type_id = cursor.lastrowid
            
        else:
            os=request.form["server"]
            os_sql="select id from os_types where name = %s"
            os_values=(os,)
            cursor.execute(os_sql,os_values)
            result=cursor.fetchone()
            os_type_id=result["id"]
        
        disk_type=request.form["disktur"].upper()
        
        if disk_type=="TB":
            disk_gb*=1024
        
        sql="""insert into servers 
        (name,disk_gb,ram_g,core_amount,ip_address,os_type_id,usage_project,created_at)
        values (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        
        values=(name,disk_gb,ram_g,core_amount,ip_address,os_type_id,usage_project,created_at)
        
        cursor.execute(sql, values)

        server_id = cursor.lastrowid
        
        cursor.execute("""
            SELECT id, data_type
            FROM custom_columns
        """)

        custom_columns = cursor.fetchall()
        
        for column in custom_columns:

            value = request.form.get(f"custom_{column['id']}")

            if column["data_type"] == "BOOLEAN":
                value = "True" if value else "False"

            if value not in ("", None):

                cursor.execute("""
                    INSERT INTO custom_values
                    (server_id, column_id, value)
                    VALUES (%s, %s, %s)
                """,
                (
                    server_id,
                    column["id"],
                    value
                ))
                
        mydb.commit()
                
        flash(translations["server_added"])
        
        return redirect(url_for("index"))
    
    cursor.execute("select name from os_types order by name")
    os_list=cursor.fetchall()
    
    cursor.execute("""
        SELECT id, column_name, data_type
        FROM custom_columns
        ORDER BY id
    """)

    custom_columns = cursor.fetchall()
        
    return render_template(
        "add.html",
        os_list=os_list,
        custom_columns=custom_columns,
        translations=translations,
        lang=lang)


@app.route("/search")
def search():
    lang = session.get("lang","tr")

    translations = get_translation(lang)

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
    
    cursor.execute("""
        SELECT *
        FROM custom_columns
    """)

    custom_columns = cursor.fetchall()
    
    for col in custom_columns:
        allowed_fields[f"custom_{col['id']}"] = {
            "type": "custom",
            "id": col["id"]
        }

    selected_fields = []

    for f in fields:
        if f in allowed_fields:
            selected_fields.append(allowed_fields[f])

        elif f.startswith("custom_"):
            column_id = int(f.split("_")[1])
            selected_fields.append({
                "type": "custom",
                "id": column_id
            })

    sql = """
        SELECT
            servers.*,
            os_types.name AS os_name
        FROM servers
        LEFT JOIN os_types
        ON servers.os_type_id = os_types.id
    """

    values = []

    if q and selected_fields:

        conditions = []

        for field in selected_fields:

            if isinstance(field, dict) and field["type"] == "custom":

                conditions.append("""
                    EXISTS (
                        SELECT 1
                        FROM custom_values cv
                        WHERE cv.server_id = servers.id
                        AND cv.column_id = %s
                        AND cv.value LIKE %s
                    )
                """)

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

    cursor.execute("""
        SELECT server_id, column_id, value
        FROM custom_values
    """)

    rows = cursor.fetchall()

    custom_values = {}

    for row in rows:

        server_id = row["server_id"]

        if server_id not in custom_values:
            custom_values[server_id] = {}

        custom_values[server_id][row["column_id"]] = row["value"]

    for server in servers:
        server["custom_values"] = custom_values.get(server["id"], {})

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM servers
        LEFT JOIN os_types
        ON servers.os_type_id = os_types.id
        WHERE os_types.name LIKE '%windows%'
    """)
    windows_amount = cursor.fetchone()["count"]

    cursor.execute("SELECT name FROM os_types ORDER BY name")
    os_list = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM custom_columns
        ORDER BY column_name
    """)
    custom_columns = cursor.fetchall()

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
        lang=lang
    )
    
@app.route("/addcolumn", methods=["GET", "POST"])
@admin_required
def addcolumn():
    lang = session.get("lang","tr")

    translations = get_translation(lang)

    if request.method == "POST":

        column_name = request.form["colName"].strip()
        data_type = request.form["dataType"]

        cursor.execute("""
            SELECT id
            FROM custom_columns
            WHERE LOWER(column_name) = LOWER(%s)
        """, (column_name,))

        if cursor.fetchone():
            flash(translations["col_already_exists"])
            return redirect(url_for("addcolumn"))

        cursor.execute("""
            INSERT INTO custom_columns
            (column_name, data_type, created_at)
            VALUES (%s, %s, CURDATE())
        """, (column_name, data_type))

        mydb.commit()

        flash(translations["added_new_column"])
        return redirect(url_for("index"))

    return render_template(
        "addcolumn.html",
        translations=translations,
        lang=lang)


@app.route("/editcolumn/<int:id>", methods=["POST"])
@admin_required
def editcolumn(id):
    lang = session.get("lang","tr")

    translations = get_translation(lang)

    column_name=request.form["columnName"].strip()
    data_type=request.form["dataType"]

    cursor.execute("""
        SELECT data_type
        FROM custom_columns
        WHERE id=%s
    """, (id,))

    current = cursor.fetchone()
    old_data_type = current["data_type"]

    cursor.execute("""
        UPDATE custom_columns
        SET
            column_name=%s,
            data_type=%s
        WHERE id=%s
    """,(column_name,data_type,id))

    if old_data_type != data_type:
        cursor.execute("""
            DELETE FROM custom_values
            WHERE column_id=%s
        """, (id,))
        flash(translations["update_column_override"])
    else:
        flash(translations["update_column"])

    mydb.commit()

    return redirect(url_for("index"))

@app.route("/deleteColumn/<int:id>", methods=["POST"])
@admin_required
def deleteColumn(id):
    lang = session.get("lang","tr")

    translations = get_translation(lang)

    cursor.execute("""
        DELETE FROM custom_values
        WHERE column_id = %s
    """, (id,))

    cursor.execute("""
        DELETE FROM custom_columns
        WHERE id = %s
    """, (id,))

    mydb.commit()

    flash(translations["f_delete_column"])

    return redirect(url_for("index"))


if __name__=="__main__":
    app.run(debug=True)
from flask import *
import mysql.connector

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="OrdekBumbo1453",
    database="serverinventorydeneme"
)

cursor=mydb.cursor(dictionary=True)

app=Flask(__name__)
app.secret_key="SunucuEnvanter"

@app.route("/")
def index():

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
        os_list=os_list
    )

@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    name = request.form["ad"]
    disk = float(request.form["disk"])
    ram = int(request.form["ram"])
    ip = request.form["ip"]
    project = request.form["project"]
    cpu = int(request.form["cpu"])
    date=request.form["date"]
    disk_type=request.form["disktur"]
    
    date.replace(".","-")
    
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

    cursor.execute(sql, values)
    mydb.commit()
    
    flash("Sunucu güncellendi!")

    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def sil(id):
    sql="delete from servers where id = %s"
    values=(id,)
    
    cursor.execute(sql,values)
    mydb.commit()
    
    flash("Sunucu silindi!")
    
    return redirect(url_for("index"))

@app.route("/add", methods=["GET","POST"])
def ekle():
    if request.method=="POST":
        name=request.form["ad"]
        disk_gb=float(request.form["disk"])
        ram_g=int(request.form["ram"])
        core_amount=int(request.form["cpu"])
        ip_address=request.form["ip"]
        usage_project=request.form["aciklama"]
        created_at=request.form["tarih"]
        
        if created_at!="": 
            created_at.replace(".","-")
        else:
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
        
        cursor.execute(sql,values)
        mydb.commit()
        
        flash("Sunucu başarıyla eklendi!")
        
        return redirect(url_for("ekle"))
    
    cursor.execute("select name from os_types order by name")
    os_list=cursor.fetchall()
        
    return render_template("add.html",os_list=os_list)


@app.route("/search")
def search():

    q = request.args.get("q", "").strip()
    fields = request.args.getlist("fields")
    disk_unit = request.args.get("disk_unit", "GB")

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
        "created_at": "servers.created_at"
    }

    selected_fields = [
        allowed_fields[f]
        for f in fields
        if f in allowed_fields
    ]

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
        values = []

        for field in selected_fields:

            if field == "servers.disk_gb":

                try:
                    limit = float(q)

                    if disk_unit == "TB":
                        limit *= 1024

                    conditions.append("servers.disk_gb <= %s")
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
        SELECT COUNT(*) AS count
        FROM servers
        LEFT JOIN os_types
        ON servers.os_type_id = os_types.id
        WHERE os_types.name like '%windows%'
    """)
    windows_amount = cursor.fetchone()["count"]

    cursor.execute("SELECT name FROM os_types")
    os_list = cursor.fetchall()

    return render_template(
        "index.html",
        servers=servers,
        windows_amount=windows_amount,
        os_list=os_list
    )


if __name__=="__main__":
    app.run(debug=True)
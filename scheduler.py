import os
import subprocess
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

_scheduler = None


def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
    return _scheduler


def perform_backup_rotation(folder_path, max_count, delete_old):
    if not delete_old or not folder_path or not os.path.exists(folder_path):
        return

    try:
        max_count = int(max_count)
        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".sql")
        ]

        if len(files) > max_count:
            files.sort(key=lambda f: os.path.getctime(f))
            files_to_delete = files[: len(files) - max_count]
            for old_file in files_to_delete:
                try:
                    os.remove(old_file)
                except Exception:
                    pass
    except Exception:
        pass


def generate_native_python_sql_dump(cursor, db_name, filepath):
    cursor.execute("SHOW TABLES")
    tables_result = cursor.fetchall()

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"-- Automatic Backup File for {db_name}\n")
        f.write(f"-- Created at {datetime.datetime.now()}\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        for row in tables_result:
            table_name = list(row.values())[0]
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            create_result = cursor.fetchone()
            create_sql = list(create_result.values())[1]

            f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
            f.write(f"{create_sql};\n\n")

            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
            for data_row in rows:
                cols = ", ".join([f"`{k}`" for k in data_row.keys()])
                vals = []
                for v in data_row.values():
                    if v is None:
                        vals.append("NULL")
                    elif isinstance(v, (int, float)):
                        vals.append(str(v))
                    else:
                        escaped_v = str(v).replace("\\", "\\\\").replace("'", "\\'")
                        vals.append(f"'{escaped_v}'")
                vals_str = ", ".join(vals)
                f.write(f"INSERT INTO `{table_name}` ({cols}) VALUES ({vals_str});\n")
            f.write("\n")

        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

    return True


def execute_auto_backup(get_db_func, db_config, add_log_func):
    conn, cursor, is_connected = get_db_func()
    if not is_connected:
        return

    try:
        cursor.execute("SELECT * FROM backup_settings WHERE id = 1")
        settings = cursor.fetchone()
        if not settings or not settings["is_enabled"]:
            return

        folder = settings["backup_folder"] or os.path.join(os.getcwd(), "backups")
        os.makedirs(folder, exist_ok=True)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backup_{now_str}.sql"
        filepath = os.path.join(folder, filename)

        db_name = db_config.get("database", "sunucu_envanteri")
        user = db_config.get("user", "root")
        password = db_config.get("password", "")
        host = db_config.get("host", "localhost")
        port = str(db_config.get("port", 3306))

        dump_success = False
        error_message = ""

        try:
            cmd = [
                "mysqldump",
                f"--host={host}",
                f"--port={port}",
                f"--user={user}",
                f"--password={password}",
                db_name,
            ]
            with open(filepath, "w", encoding="utf-8") as out:
                subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True, check=True)
            dump_success = True
        except Exception as mysqldump_err:
            error_message = str(mysqldump_err)
            try:
                dump_success = generate_native_python_sql_dump(cursor, db_name, filepath)
            except Exception as native_err:
                error_message += f" | Native dump error: {native_err}"

        timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if dump_success:
            cursor.execute(
                """
                UPDATE backup_settings
                SET last_backup_date = %s, last_backup_status = %s
                WHERE id = 1
                """,
                (timestamp_now, "Success"),
            )
            add_log_func(
                cursor,
                "System",
                "Otomatik Yedekleme",
                "Veritabanı",
                f"Otomatik yedek alındı: {filename}",
            )
            conn.commit()

            perform_backup_rotation(
                folder, settings["max_backup_count"], settings["delete_old_backups"]
            )
        else:
            cursor.execute(
                """
                UPDATE backup_settings
                SET last_backup_status = %s
                WHERE id = 1
                """,
                (f"Error: {error_message[:200]}",),
            )
            add_log_func(
                cursor,
                "System",
                "Otomatik Yedekleme Hatası",
                "Veritabanı",
                f"Yedek alma hatası: {error_message[:200]}",
            )
            conn.commit()

    except Exception:
        pass
    finally:
        cursor.close()
        conn.close()


def update_backup_schedule(is_enabled, frequency, backup_day, backup_time, backup_folder, max_backup_count, delete_old_backups, get_db_func, db_config, add_log_func):
    sch = get_scheduler()
    try:
        try:
            sch.remove_job("db_auto_backup")
        except Exception:
            pass

        if not is_enabled or not backup_time:
            return

        parts = backup_time.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0

        def job_wrapper():
            execute_auto_backup(get_db_func, db_config, add_log_func)

        day_of_week = backup_day if backup_day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] else "mon"

        if frequency == "weekly":
            sch.add_job(
                func=job_wrapper,
                trigger="cron",
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                id="db_auto_backup",
                replace_existing=True,
            )
        elif frequency == "monthly":
            sch.add_job(
                func=job_wrapper,
                trigger="cron",
                day=1,
                hour=hour,
                minute=minute,
                id="db_auto_backup",
                replace_existing=True,
            )
        else:
            sch.add_job(
                func=job_wrapper,
                trigger="cron",
                hour=hour,
                minute=minute,
                id="db_auto_backup",
                replace_existing=True,
            )
    except Exception:
        pass

from grup import *

username = input("Kullanıcı Adı: ")
password = input("Şifre: ")

success, conn = authenticate(username, password)

if success:
    print("✅ Giriş başarılı!\n")

    print("Gruplar:\n")
    list_groups(conn)

    disconnect(conn)
else:
    print("❌ Giriş başarısız!")
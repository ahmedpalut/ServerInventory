from auth import *

username = input("Kullanıcı Adı: ")
password = input("Şifre: ")

success, conn = authenticate(username, password)

if success:
    print("✅ Giriş başarılı!\n")

    print("Kullanıcılar:\n")
    get_users(conn)

    disconnect(conn)
else:
    print("❌ Giriş başarısız!")
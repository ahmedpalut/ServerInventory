from auth import *

username = input("Kullanıcı Adı: ")
password = input("Şifre: ")

success, conn = authenticate(username, password)

if success:
    print("+ Giriş başarıl!!!")
    disconnect(conn)
else:
    print("❌ Giriş başarısız!")
from flask import Flask, render_template, request, redirect, url_for, session, flash
from ldap3 import Server, Connection, ALL, SIMPLE, MODIFY_REPLACE
# Diğer mevcut importlarınız burada kalabilir...

# Active Directory (LDAP) Ayarlarınız (Kendi ortamınıza göre düzenleyin)
AD_SERVER = "ldap://sirket.local"  # veya AD sunucu IP adresi
AD_DOMAIN = "sirket.local"         # Domain adınız

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Kullanıcının domainli veya domainsiz girmesini esnetmek için:
        if "\\" in username:
            user_dn = username
        else:
            user_dn = f"{username}@{AD_DOMAIN}"

        try:
            # Active Directory sunucusuna bağlanıp kullanıcıyı test ediyoruz
            server = Server(AD_SERVER, get_info=ALL)
            conn = Connection(server, user=user_dn, password=password, authentication=SIMPLE, raise_exceptions=True)
            
            if conn.bind():
                session['user'] = username
                flash("Giriş başarılı!", "success")
                return redirect(url_for('index')) # Ana sayfa rotanız neyse (örn: index)
        except Exception as e:
            flash("Kullanıcı adı veya şifre hatalı!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Oturum kapatıldı.", "success")
    return redirect(url_for('login'))
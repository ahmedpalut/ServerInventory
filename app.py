# from flask import *
# from ldap3 import Server, Connection, ALL, SIMPLE
# import os
# from dotenv import load_dotenv

# load_dotenv()

# AD_SERVER = os.getenv("LDAP_SERVER") 
# AD_DOMAIN = os.getenv("LDAP_DOMAIN") 

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         if "\\" in username:
#             user_dn = username
#         else:
#             user_dn = f"{username}@{AD_DOMAIN}"

#         try:
#             server = Server(AD_SERVER, get_info=ALL)
#             conn = Connection(server, user=user_dn, password=password, authentication=SIMPLE, raise_exceptions=True)
            
#             if conn.bind():
#                 session['user'] = username
#                 flash("Giriş başarılı!", "success")
#                 conn.unbind()
#                 return redirect(url_for('index')) 
#             else:
#                 flash("Kullanıcı adı veya şifre hatalı.", "error")
#                 return redirect(url_for("login"))
                
                
#         except Exception as e:
#             flash(str(e), "error")
#             return redirect(url_for('login'))

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     flash("Oturum kapatıldı.", "success")
#     return redirect(url_for('login'))
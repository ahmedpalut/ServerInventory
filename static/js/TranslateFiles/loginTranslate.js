let tr = true;

document.getElementById("langButton").onclick = function () {

    if (tr) {

        document.querySelector("h1").innerHTML = "🖥️ GIG Server Inventory";

        document.querySelector("p").innerHTML = "Welcome";

        document.querySelectorAll("label")[0].innerHTML = "Username";

        document.querySelectorAll("label")[1].innerHTML = "Password";

        document.querySelector("input[name='username']").placeholder = "Username";

        document.querySelector("input[name='password']").placeholder = "Password";

        document.querySelector(".login-btn").innerHTML = "Login";

        document.querySelector(".login-options label").lastChild.textContent = " Remember Me";

    } else {

        document.querySelector("h1").innerHTML = "🖥️ GIG Server Inventory";

        document.querySelector("p").innerHTML = "Hoş Geldiniz";

        document.querySelectorAll("label")[0].innerHTML = "Kullanıcı Adı";

        document.querySelectorAll("label")[1].innerHTML = "Şifre";

        document.querySelector("input[name='username']").placeholder = "Kullanıcı Adı";

        document.querySelector("input[name='password']").placeholder = "Şifre";

        document.querySelector(".login-btn").innerHTML = "Giriş Yap";

        document.querySelector(".login-options label").lastChild.textContent = " Beni Hatırla";

    }

    tr = !tr;

}
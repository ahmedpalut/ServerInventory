const password = document.getElementById("password");
const toggle = document.getElementById("toggle");
const icon = toggle.querySelector("i");

if(password && toggle){
    toggle.addEventListener("click", function () {

        if (password.type === "password") {

            password.type = "text";
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");

        } else {

            password.type = "password";
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");

        }

    }); 
}




const username = document.getElementById("username");
const rememberMe = document.getElementById("rememberMe");
const form = document.querySelector("form");

const savedUsername = localStorage.getItem("rememberedUsername");

if (savedUsername) {
    username.value = savedUsername;
    rememberMe.checked = true;
}

form.addEventListener("submit", function () {

    if (rememberMe.checked) {
        localStorage.setItem("rememberedUsername", username.value);
    } else {
        localStorage.removeItem("rememberedUsername");
    }

});
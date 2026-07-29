const select = document.getElementById("server");
const serverekle = document.getElementById("serverekle");

if(select && serverekle){
    select.addEventListener("change", function () {
        if (this.value == "Yeni") {
            serverekle.style.display = "block";
        } else {
            serverekle.style.display = "none";
        }
    });

}


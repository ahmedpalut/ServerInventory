const select = document.getElementById("server");
const serverekle = document.getElementById("serverekle");

select.addEventListener("change", function () {
    if (this.value == "Yeni") {
        serverekle.style.display = "block";
    } else {
        serverekle.style.display = "none";
    }
});

let tr = true;

document.getElementById("langButton").onclick = function () {

    if (tr) {

        document.documentElement.lang = "en";

        document.getElementById("title").innerHTML = "Add New Server";

        document.getElementById("l1").innerHTML = "Server Name";
        document.getElementById("l2").innerHTML = "Disk Size (GB)";
        document.getElementById("l3").innerHTML = "Operating System";
        document.getElementById("l4").innerHTML = "RAM";
        document.getElementById("l5").innerHTML = "IP Address";
        document.getElementById("l6").innerHTML = "Description";
        document.getElementById("l7").innerHTML = "CPU";
        document.getElementById("l8").innerHTML = "Date";
        document.getElementById("l9").innerHTML = "Disk Size Type (GB/TB)";
        document.getElementById("l10").innerHTML = "New Operating System";
        document.getElementById("sunucusec").innerHTML = "Select Server";
        document.getElementById("yeni").innerHTML = "New";

        document.getElementById("saveBtn").innerHTML = "Save";
        document.getElementById("cancelBtn").innerHTML = "Cancel";

    } else {

        document.documentElement.lang = "tr";

        document.getElementById("title").innerHTML = "Yeni Sunucu Ekle";

        document.getElementById("l1").innerHTML = "Sunucu Adı";
        document.getElementById("l2").innerHTML = "Disk Boyutu (GB)";
        document.getElementById("l3").innerHTML = "İşletim Sistemi";
        document.getElementById("l4").innerHTML = "RAM";
        document.getElementById("l5").innerHTML = "IP Adresi";
        document.getElementById("l6").innerHTML = "Açıklama";
        document.getElementById("l7").innerHTML = "CPU";
        document.getElementById("l8").innerHTML = "Tarih";
        document.getElementById("l9").innerHTML = "Disk Boyut Cinsi (GB/TB)";
        document.getElementById("l10").innerHTML = "Yeni İşletim Sistemi";
        document.getElementById("sunucusec").innerHTML = "Sunucu Seçin";
        document.getElementById("yeni").innerHTML = "Yeni";

        document.getElementById("saveBtn").innerHTML = "Kaydet";
        document.getElementById("cancelBtn").innerHTML = "İptal";

    }

    tr = !tr;

};
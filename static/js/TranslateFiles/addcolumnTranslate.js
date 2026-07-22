let tr = true;

document.getElementById("langButton").onclick = function () {
    if(tr){
        document.documentElement.lang = "en";

        document.getElementById("cancelColumnBtn").innerHTML="Cancel";
        document.getElementById("addColumnBtn").innerHTML="Add";
        document.getElementById("title").innerHTML="Add New Column";
        document.getElementById("dataTypeLabel").innerHTML="Data Type";
        document.getElementById("colNameLabel").innerHTML="Column Name";
    }
    else{
        document.documentElement.lang = "tr";

        document.getElementById("cancelColumnBtn").innerHTML="İptal";
        document.getElementById("addColumnBtn").innerHTML="Ekle";
        document.getElementById("title").innerHTML="Yeni Sütun Ekle";
        document.getElementById("dataTypeLabel").innerHTML="Veri Tipi";
        document.getElementById("colNameLabel").innerHTML="Sütun Adı";
    }

    tr=!tr;
}
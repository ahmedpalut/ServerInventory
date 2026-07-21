
function openPanel(
    id,
    name,
    disk,
    os,
    ram,
    ip,
    project,
    cpu,
    date
) {
    document.getElementById("p_name").value = name;
    if(disk>=1024){
        disk/=1024;
        document.getElementById("p_disktur").value="TB";
    }
    else{
        document.getElementById("p_disktur").value="GB";
    }
    document.getElementById("p_disk").value = disk;
    document.getElementById("server").value = os;
    document.getElementById("p_ram").value = ram;
    document.getElementById("p_ip").value = ip;
    document.getElementById("p_project").value = project;
    document.getElementById("p_cpu").value = cpu;
    document.getElementById("p_date").value = date;

    document.getElementById("editForm").action =
        "/edit/" + id;

    document.getElementById("editPanel").style.right = "0";
}

function closePanel() {
    document.getElementById("editPanel").style.right =
        "-420px";
}
const select = document.getElementById("server");
const serverekle =
    document.getElementById("serverekle");

select.addEventListener("change", function () {
    if (this.value === "Yeni") {
        serverekle.style.display = "block";
    }
    else {
        serverekle.style.display = "none";
    }
});

let turkce = true;

document.getElementById("langButton").onclick = function () {

    if (turkce) {

        document.getElementById("title").innerHTML = "🖥️ Server Inventory";

        document.getElementById("card1").innerHTML = "Total Servers";
        document.getElementById("card2").innerHTML = "Windows Servers";
        document.getElementById("card3").innerHTML = "IT Inventory";

        document.getElementById("searchInput").placeholder = "🔍 Search Server...";

        document.getElementById("th1").innerHTML = "Server";
        document.getElementById("th2").innerHTML = "Disk Size (GB)";
        document.getElementById("th3").innerHTML = "Operating System";
        document.getElementById("th4").innerHTML = "RAM";
        document.getElementById("th5").innerHTML = "IP";
        document.getElementById("th6").innerHTML = "Description";
        document.getElementById("th7").innerHTML = "CPU";
        document.getElementById("th8").innerHTML = "Date";
        document.getElementById("th9").innerHTML = "Action";

        document.getElementById("searchSettingsBtn").innerHTML = "⚙️ Search Settings";
        document.getElementById("aramalabel").innerHTML = "Search Settings";
        if(window.location.pathname=="/search"){
            document.getElementById("searchBtn").innerHTML="⬅️ Back";
        }else{
            document.getElementById("searchBtn").innerHTML="🔍 Search";
        }
        document.getElementById("aranacakalan").innerHTML = "Searching Areas";

        document.getElementById("selectAllBtn").innerHTML = "Select All";
        document.getElementById("clearAllBtn").innerHTML = "Clear";

        document.getElementById("editSunucuDuzenle").innerHTML = "Edit Server";
        document.getElementById("esl1").innerHTML = "Server Name";
        document.getElementById("esl2").innerHTML = "Disk Size";
        document.getElementById("esl3").innerHTML = "Disk Size Type (GB/TB)";
        document.getElementById("esl4").innerHTML = "Operating System";
        document.getElementById("esl41").innerHTML = "Select Server";
        document.getElementById("esl42").innerHTML = "New";
        document.getElementById("yeniIsletim").placeholder="New operating system";
        document.getElementById("esl5").innerHTML = "Description";
        document.getElementById("esl6").innerHTML = "Date";

        document.getElementById("sl1").lastChild.textContent = "Server Name";
        document.getElementById("sl2").lastChild.textContent = "Operating System";
        document.getElementById("sl3").lastChild.textContent = "IP Adress";
        document.getElementById("sl4").lastChild.textContent = "Description";
        document.getElementById("sl5").lastChild.textContent = "Disk Size";
        document.getElementById("sl6").lastChild.textContent = "Date";

        document.getElementById("addBtn").innerHTML = "➕ Add Server";

    }

    else {

        document.getElementById("title").innerHTML = "🖥️ Sunucu Envanteri";

        document.getElementById("card1").innerHTML = "Toplam Sunucu";
        document.getElementById("card2").innerHTML = "Windows Sunucu";
        document.getElementById("card3").innerHTML = "IT Envanteri";

        document.getElementById("searchInput").placeholder = "🔍 Sunucu Ara...";

        document.getElementById("th1").innerHTML = "Sunucu";
        document.getElementById("th2").innerHTML = "Disk Boyutu (GB)";
        document.getElementById("th3").innerHTML = "İşletim Sistemi";
        document.getElementById("th4").innerHTML = "RAM";
        document.getElementById("th5").innerHTML = "IP";
        document.getElementById("th6").innerHTML = "Açıklama";
        document.getElementById("th7").innerHTML = "CPU";
        document.getElementById("th8").innerHTML = "Tarih";
        document.getElementById("th9").innerHTML = "İşlem";

        document.getElementById("searchSettingsBtn").innerHTML = "⚙️ Arama Ayarları";
        document.getElementById("aramalabel").innerHTML = "Arama Ayarları";
        if(window.location.pathname=="/search"){
            document.getElementById("searchBtn").innerHTML="⬅️ Geri Dön";
        }else{
            document.getElementById("searchBtn").innerHTML="🔍 Ara";
        }
        document.getElementById("aranacakalan").innerHTML = "Aranacak Alanlar";

        document.getElementById("selectAllBtn").innerHTML = "Tümünü Seç";
        document.getElementById("clearAllBtn").innerHTML = "Temizle";

        document.getElementById("editSunucuDuzenle").innerHTML = "Sunucu Düzenle";
        document.getElementById("esl1").innerHTML = "Sunucu Adı";
        document.getElementById("esl2").innerHTML = "Disk Boyutu";
        document.getElementById("esl3").innerHTML = "Disk Boyut Türü (GB/TB)";
        document.getElementById("esl4").innerHTML = "İşletim Sistemi";
        document.getElementById("esl41").innerHTML = "Sunucu Seçin";
        document.getElementById("esl42").innerHTML = "Yeni";
        document.getElementById("yeniIsletim").placeholder="Yeni İşletim Sistemi";
        document.getElementById("esl5").innerHTML = "Açıklama";
        document.getElementById("esl6").innerHTML = "Tarih";

        document.getElementById("sl1").lastChild.textContent = "Sunucu Adı";
        document.getElementById("sl2").lastChild.textContent = "işletim Sistemi";
        document.getElementById("sl3").lastChild.textContent = "IP Adresi";
        document.getElementById("sl4").lastChild.textContent = "Açıklama";
        document.getElementById("sl5").lastChild.textContent = "Disk Boyutu";
        document.getElementById("sl6").lastChild.textContent = "Tarih";

        document.getElementById("addBtn").innerHTML = "➕ Yeni Sunucu";

    }

    turkce = !turkce;

}



const searchSettingsBtn = document.getElementById("searchSettingsBtn");
const overlay = document.getElementById("searchSettingsOverlay");
const panel = document.getElementById("searchSettingsPanel");
const closeBtn = document.getElementById("closeSearchSettings");

searchSettingsBtn.onclick = function () {
    overlay.style.display = "flex";
};

closeBtn.onclick = function () {
    overlay.style.display = "none";
};

overlay.onclick = function () {
    overlay.style.display = "none";
};

panel.onclick = function (e) {
    e.stopPropagation();
};

const checkboxes = document.querySelectorAll(
    'input[name="fields"]'
);

document.getElementById("selectAllBtn").onclick = function () {

    checkboxes.forEach(function (box) {
        box.checked = true;
    });

};

document.getElementById("clearAllBtn").onclick = function () {

    checkboxes.forEach(function (box) {
        box.checked = false;
    });

};

const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");

document.getElementById("searchBtn").onclick = function (e) {

    e.preventDefault();

    if (window.location.pathname === "/search") {
        window.location.href = "/";
        return;
    }

    let q = searchInput.value.trim();

    if (q === "") {
        window.location.href = "/";
        return;
    }

    let url = "/search?q=" + encodeURIComponent(q);

    document.querySelectorAll("input[name='fields']:checked")
        .forEach(function (box) {
            url += "&fields=" + encodeURIComponent(box.value);
        });

    const diskRadio =
        document.querySelector("input[name='disk_unit']:checked");

    if (diskRadio) {
        url += "&disk_unit=" + encodeURIComponent(diskRadio.value);
    }

    window.location.href = url;
};

let sortDirection = {};

function sortTable(column) {

    const table = document.getElementById("serverTable");
    const tbody = table.tBodies[0];

    const rows = Array.from(tbody.rows);

    sortDirection[column] = !sortDirection[column];

    rows.sort(function(a, b){

        let x = a.cells[column].innerText.trim();
        let y = b.cells[column].innerText.trim();

        let nx = parseFloat(x);
        let ny = parseFloat(y);

        if(!isNaN(nx) && !isNaN(ny)){
            return sortDirection[column] ? nx - ny : ny - nx;
        }

        return sortDirection[column]
            ? x.localeCompare(y, "tr")
            : y.localeCompare(x, "tr");
    });

    rows.forEach(function(row){
        tbody.appendChild(row);
    });
}

const diskCheckbox = document.querySelector(
    "input[name='fields'][value='disk_gb']"
);

const diskUnitOptions = document.getElementById("diskUnitOptions");



const diskOptions = document.getElementById("diskUnitOptions");

function updateDiskOptions() {
    if (diskCheckbox.checked) {
        diskOptions.style.display = "flex";
    } else {
        diskOptions.style.display = "none";
    }
}

diskCheckbox.addEventListener("change", updateDiskOptions);

updateDiskOptions();


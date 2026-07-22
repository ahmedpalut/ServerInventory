const searchSettingsBtn = document.getElementById("searchSettingsBtn");
const overlay = document.getElementById("searchSettingsOverlay");
const panel = document.getElementById("searchSettingsPanel");
const closeBtn = document.getElementById("closeSearchSettings");
const tableSettingsOverlay=document.getElementById("tableSettingsOverlay");
const tableSettingsBtn=document.getElementById("tableSettingsBtn");
const tableCloseBtn=document.getElementById("closeTableSettings");
const tablePanel=document.getElementById("tableSettingsPanel");
let currentPage = 1;
const maxPage = 2;

function updatePageButtons(){

    document.querySelectorAll(".page2").forEach(function(cell){

        cell.style.display =
            currentPage == 2 ? "" : "none";

    });

    document.querySelectorAll("#serverTable tr").forEach(function(row){

        for(let i=0;i<firstPageColumns;i++){

            if(row.cells[i]){

                row.cells[i].style.display =
                    currentPage==1 ? "" : "none";

            }

        }

    });

    document.getElementById("prevPage").style.display =
        currentPage > 1 ? "" : "none";

    document.getElementById("nextPage").style.display =
        currentPage < maxPage ? "" : "none";

    document.querySelectorAll(".prevPageCell").forEach(cell=>{
        cell.style.display =
            currentPage>1 ? "" : "none";
    });

    document.querySelectorAll(".nextPageCell").forEach(cell=>{
        cell.style.display =
            currentPage<maxPage ? "" : "none";
    });

}

document.getElementById("nextPage").onclick=function(){

    currentPage++;

    updatePageButtons();

}

document.getElementById("prevPage").onclick=function(){

    currentPage--;

    updatePageButtons();

}

function openDeleteColumnPanel(){

    document.body.classList.add("modal-open");

    fillDeleteColumn();

    document.getElementById("columnDeletePanel").style.right="0";

    document.getElementById("columndeletelay").style.display="block";
    tableSettingsOverlay.style.display="none";

}

function closeDeleteColumnPanel(){

    document.body.classList.remove("modal-open");

    document.getElementById("columnDeletePanel").style.right="-420px";

    document.getElementById("columndeletelay").style.display="none";

}

document.getElementById("columndeletelay").onclick=function(){

    closeDeleteColumnPanel();

}

document.getElementById("closeDeleteColumnBtn").onclick=function(){
    closeDeleteColumnPanel();
}

function openColumnPanel(){

    document.body.classList.add("modal-open");

    fillColumn();

    document.getElementById("columnPanel").style.right="0";

    document.getElementById("columnOverlay").style.display="block";
    tableSettingsOverlay.style.display="none";

}

function closeColumnPanel(){

    document.body.classList.remove("modal-open");

    document.getElementById("columnPanel").style.right="-420px";

    document.getElementById("columnOverlay").style.display="none";

}

document.getElementById("columnOverlay").onclick=function(){

    closeColumnPanel();

}

document.getElementById("columnDeleteForm").onsubmit = function () {

    return confirm("Bu sütun silinecek. Devam etmek istiyor musunuz?");

};

function fillDeleteColumn(){

    const select=document.getElementById("columnDeleteSelect");

    const option=
        select.options[select.selectedIndex];


    document.getElementById("columnDeleteForm").action=
        "/deleteColumn/"+option.value;

}

function fillColumn(){

    const select=document.getElementById("columnSelect");

    const option=
        select.options[select.selectedIndex];

    document.getElementById("columnName").value=
        option.dataset.name;

    document.getElementById("columnType").value=
        option.dataset.type;

    document.getElementById("columnForm").action=
        "/editcolumn/"+option.value;

}

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
    document.body.classList.add("modal-open");

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
    document.getElementById("editOverlay").style.display = "block";
}

function closePanel() {
    document.body.classList.remove("modal-open");
    document.getElementById("editPanel").style.right = "-420px";
    document.getElementById("editOverlay").style.display = "none";
}

document.getElementById("editOverlay").onclick = function(){
    closePanel();
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

tableSettingsBtn.onclick = function(){
    tableSettingsOverlay.style.display="flex";
    document.body.classList.add("modal-open");
};

tableCloseBtn.onclick = function(){
    tableSettingsOverlay.style.display="none";
    document.body.classList.remove("modal-open");
};

tableSettingsOverlay.onclick=function(){
    tableSettingsOverlay.style.display="none";
    document.body.classList.remove("modal-open");
};

searchSettingsBtn.onclick = function () {
    overlay.style.display = "flex";
    document.body.classList.add("modal-open");
};

tablePanel.onclick=function(e){
    e.stopPropagation();
}

closeBtn.onclick = function () {
    overlay.style.display = "none";
    document.body.classList.remove("modal-open");
};

overlay.onclick = function () {
    overlay.style.display = "none";
    document.body.classList.remove("modal-open");
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

    document.querySelectorAll("input[name='disk_compare']").forEach(function(radio){
        radio.checked = false;
    });

    document.querySelectorAll("input[name='disk_unit']").forEach(function(radio){
        radio.checked = false;
    });

    diskOptions.style.display = "none";
    diskCompareOptions.style.display = "none";  

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

    const compare =
        document.querySelector("input[name='disk_compare']:checked");

    if (compare) {
        url += "&disk_compare=" + encodeURIComponent(compare.value);
    }

    window.location.href = url;
};

let sortDirection = {};

function sortTable(column) {
    const table = document.getElementById("serverTable");
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);

    sortDirection[column] = !sortDirection[column];

    rows.sort(function(a, b) {
        let x = a.cells[column].innerText.trim();
        let y = b.cells[column].innerText.trim();

        let nx = parseFloat(x);
        let ny = parseFloat(y);

        if (!isNaN(nx) && !isNaN(ny)) {
            return sortDirection[column] ? nx - ny : ny - nx;
        }

        return sortDirection[column]
            ? x.localeCompare(y, "tr")
            : y.localeCompare(x, "tr");
    });

    rows.forEach(function(row) {
        tbody.appendChild(row);
    });

    for (let i = 0; i < 9; i++) {
        let th = document.getElementById("th" + (i + 1));
        if (th) {
            let span = th.querySelector(".sort-icon");
            if (span) span.innerText = "↕";
        }
    }

    let activeTh = document.getElementById("th" + (column + 1));
    if (activeTh) {
        let activeSpan = activeTh.querySelector(".sort-icon");
        if (activeSpan) {
            activeSpan.innerText = sortDirection[column] ? "▲" : "▼";
        }
    }
}
const diskCheckbox = document.querySelector(
    "input[name='fields'][value='disk_gb']"
);

const diskUnitOptions = document.getElementById("diskUnitOptions");



const diskOptions = document.getElementById("diskUnitOptions");

const diskCompareOptions =
    document.getElementById("diskCompareOptions");

function updateDiskOptions(){

    if(diskCheckbox.checked){

        diskOptions.style.display="flex";
        diskCompareOptions.style.display="flex";

    }else{

        diskOptions.style.display="none";
        diskCompareOptions.style.display="none";

    }

}

diskCheckbox.addEventListener("change", updateDiskOptions);

updateDiskOptions();

document.querySelectorAll(".columnToggle").forEach(function (checkbox) {

    checkbox.addEventListener("change", function () {

        const column = Number(this.dataset.column);

        document.querySelectorAll("#serverTable tr").forEach(function (row) {

            if (row.cells[column]) {
                row.cells[column].style.display = checkbox.checked ? "" : "none";
            }

        });

        localStorage.setItem(
            "column_" + column,
            checkbox.checked
        );

    });

});

document.querySelectorAll(".columnToggle").forEach(function (checkbox) {

    const column = Number(checkbox.dataset.column);

    const saved = localStorage.getItem("column_" + column);

    if (saved !== null) {

        checkbox.checked = (saved === "true");

        document.querySelectorAll("#serverTable tr").forEach(function (row) {

            if (row.cells[column]) {
                row.cells[column].style.display =
                    checkbox.checked ? "" : "none";
            }

        });

    }

});

updatePageButtons();
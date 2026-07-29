const searchSettingsBtn = document.getElementById("searchSettingsBtn");
const overlay = document.getElementById("searchSettingsOverlay");
const panel = document.getElementById("searchSettingsPanel");
const closeBtn = document.getElementById("closeSearchSettings");
const tableSettingsOverlay=document.getElementById("tableSettingsOverlay");
const tableSettingsBtn=document.getElementById("tableSettingsBtn");
const tableCloseBtn=document.getElementById("closeTableSettings");
const tablePanel=document.getElementById("tableSettingsPanel");


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
    date,
    customValues
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

    document.querySelectorAll("[id^='custom_']").forEach(input => {

        if (input.type === "checkbox") {
            input.checked = false;
        } else {
            input.value = "";
        }

    });

    for (const columnId in customValues) {

        const input = document.getElementById("custom_" + columnId);

        if (!input) continue;

        if (input.type === "checkbox") {

            input.checked = (customValues[columnId] === "True");

        } else {

            input.value = customValues[columnId];

        }

    }

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

document.getElementById("columnForm").onsubmit = function () {

    const select = document.getElementById("columnSelect");
    const option = select.options[select.selectedIndex];
    const originalType = option.dataset.type;

    const newType = document.getElementById("columnType").value;

    if (originalType !== newType) {
        return confirm("Veri tipini değiştiriyorsunuz. Bu sütuna ait mevcut tüm değerler silinecek. Devam etmek istiyor musunuz?");
    }

    return true;

};

document.querySelectorAll(".columnToggle").forEach(function (checkbox) {

    checkbox.addEventListener("change", function () {

        const colKey = this.dataset.col;

        document.querySelectorAll(`#serverTable [data-col="${colKey}"]`).forEach(function (cell) {
            cell.style.display = checkbox.checked ? "" : "none";
        });

        localStorage.setItem("column_" + colKey, checkbox.checked);

    });

});

document.querySelectorAll(".columnToggle").forEach(function (checkbox) {

    const colKey = checkbox.dataset.col;
    const saved = localStorage.getItem("column_" + colKey);

    if (saved !== null) {

        checkbox.checked = (saved === "true");

        document.querySelectorAll(`#serverTable [data-col="${colKey}"]`).forEach(function (cell) {
            cell.style.display = checkbox.checked ? "" : "none";
        });

    }

});

function getColumnOrder() {
    return Array.from(
        document.querySelectorAll("#serverTable thead th[data-col]")
    ).map(function (th) {
        return th.dataset.col;
    });
}

function applyColumnOrder(order) {

    const table = document.getElementById("serverTable");
    const headerRow = table.tHead.rows[0];
    const lastTh = document.getElementById("th_last");

    order.forEach(function (colKey) {
        const th = headerRow.querySelector(`th[data-col="${colKey}"]`);
        if (th) headerRow.insertBefore(th, lastTh);
    });

    Array.from(table.tBodies[0].rows).forEach(function (row) {

        const lastCell = row.cells[row.cells.length - 1];

        order.forEach(function (colKey) {
            const cell = row.querySelector(`[data-col="${colKey}"]`);
            if (cell) row.insertBefore(cell, lastCell);
        });

    });

}

let draggedKey = null;

document.querySelectorAll(".draggable-th").forEach(function (th) {

    th.addEventListener("dragstart", function () {
        draggedKey = th.dataset.col;
        th.classList.add("dragging");
    });

    th.addEventListener("dragend", function () {
        th.classList.remove("dragging");
        draggedKey = null;
        saveColumnOrder();
    });

    th.addEventListener("dragover", function (e) {
        e.preventDefault();

        if (!draggedKey || draggedKey === th.dataset.col) return;

        const order = getColumnOrder();

        const fromIndex = order.indexOf(draggedKey);

        if (fromIndex === -1) return;

        const rect = th.getBoundingClientRect();
        const isAfter = e.clientX > rect.left + rect.width / 2;

        order.splice(fromIndex, 1);

        let insertIndex = order.indexOf(th.dataset.col);

        if (isAfter) insertIndex += 1;

        order.splice(insertIndex, 0, draggedKey);

        applyColumnOrder(order);

    });

});

function saveColumnOrder() {

    const order = Array.from(
        document.querySelectorAll("#serverTable thead th[data-col]")
    ).map(function (th) {
        return th.dataset.col;
    });

    localStorage.setItem("columnOrder", JSON.stringify(order));

}

function restoreColumnOrder() {

    const saved = localStorage.getItem("columnOrder");

    if (!saved) return;

    let order;

    try {
        order = JSON.parse(saved);
    } catch (e) {
        return;
    }

    const table = document.getElementById("serverTable");
    const headerRow = table.tHead.rows[0];
    const lastTh = document.getElementById("th_last");

    order.forEach(function (colKey) {

        const th = headerRow.querySelector(`th[data-col="${colKey}"]`);

        if (th) {
            headerRow.insertBefore(th, lastTh);
        }

        Array.from(table.tBodies[0].rows).forEach(function (row) {

            const cell = row.querySelector(`[data-col="${colKey}"]`);
            const lastCell = row.cells[row.cells.length - 1];

            if (cell) {
                row.insertBefore(cell, lastCell);
            }

        });

    });

}

let activeColumn = null; // Şu an hangi sütun menüsünün açık olduğunu tutar

function toggleColumnMenu(event, colKey) {
    window.scrollTo({
        top: 0,
        behavior: "smooth" 
    });
    event.stopPropagation();
    activeColumn = colKey; // Tıklanan sütunu kaydet
    
    const menu = document.getElementById('sharedColumnMenu');
    const btn = event.currentTarget;
    
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    } else {
        // Butonun ekrandaki yerini hesapla
        const rect = btn.getBoundingClientRect();
        
        // Önceki aramadan kalan input kutusu varsa temizle
        const oldSearch = menu.querySelector('.col-search-box');
        if (oldSearch) oldSearch.remove();
        
        menu.style.display = 'block';
        
        // Butonun tam altına yerleştir
        let leftPos = rect.right - menu.offsetWidth;
        if (leftPos < 10) leftPos = rect.left;
        
        menu.style.top = (rect.bottom + 4) + 'px';
        menu.style.left = leftPos + 'px';
    }
}

// Sıralama Yap
function executeSort(order) {
    if (!activeColumn) return;
    sortTable(activeColumn, order);
    document.getElementById('sharedColumnMenu').style.display = 'none';
}

// Sütun İçi Arama Kutusunu Aç
function openSharedSearch(event) {
    event.stopPropagation();
    
    const menu = document.getElementById('sharedColumnMenu');
    
    if (!menu.querySelector('.col-search-box')) {
        const searchDiv = document.createElement('div');
        searchDiv.className = 'col-search-box';
        searchDiv.innerHTML = `<input type="text" placeholder="Aranacak kelime..." class="col-filter-input" onclick="event.stopPropagation()">`;
        
        menu.appendChild(searchDiv);
        
        const input = searchDiv.querySelector('input');
        input.focus();
        
        // Yazdıkça satırları filtrele (Satırlar azalsa bile panel etkilenmez)
        input.oninput = function() {
            let val = this.value.toLowerCase();
            const rows = document.querySelectorAll("#serverTable tbody tr.serverRow");
            rows.forEach(row => {
                let cell = row.querySelector(`[data-col="${activeColumn}"]`);
                if (cell) {
                    let text = cell.innerText.toLowerCase();
                    row.style.display = text.includes(val) ? "" : "none";
                }
            });
        };
    }
}

// Boş bir yere tıklandığında paneli kapat
window.addEventListener('click', function() {
    const menu = document.getElementById('sharedColumnMenu');
    if (menu) menu.style.display = 'none';
});

// Sıralama Mantığı
function sortTable(colKey, order) {
    const table = document.getElementById("serverTable");
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.querySelectorAll("tr.serverRow"));

    rows.sort((a, b) => {
        let cellA = a.querySelector(`[data-col="${colKey}"]`) ? a.querySelector(`[data-col="${colKey}"]`).innerText.trim() : "";
        let cellB = b.querySelector(`[data-col="${colKey}"]`) ? b.querySelector(`[data-col="${colKey}"]`).innerText.trim() : "";

        let numA = parseFloat(cellA);
        let numB = parseFloat(cellB);

        if (!isNaN(numA) && !isNaN(numB)) {
            return order === 'asc' ? numA - numB : numB - numA;
        }

        return order === 'asc' ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
    });

    rows.forEach(row => tbody.appendChild(row));
}

// 4. Sütun Silme Yönlendirmesi
function deleteColumnPrompt(colKey) {
    // Özel sütun mu yoksa standart sütun mü kontrolü
    if (colKey.startsWith('custom_')) {
        let realId = colKey.replace('custom_', '');
        if (confirm("Bu sütunu silmek istediğinize emin misiniz?")) {
            window.location.href = "/deleteColumn/" + realId;
        }
    } else {
        alert("Bu varsayılan bir sütundur, silinemez!");
    }
}

// Sayfa kaydırıldığında açık olan ortak paneli otomatik kapat
window.addEventListener('scroll', function() {
    const menu = document.getElementById('sharedColumnMenu');
    if (menu && menu.style.display === 'block') {
        menu.style.display = 'none';
    }
}, { passive: true });

restoreColumnOrder();
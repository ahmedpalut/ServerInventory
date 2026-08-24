const searchSettingsBtn = document.getElementById("searchSettingsBtn");
const overlay = document.getElementById("searchSettingsOverlay");
const panel = document.getElementById("searchSettingsPanel");
const closeBtn = document.getElementById("closeSearchSettings");
const tableSettingsOverlay = document.getElementById("tableSettingsOverlay");
const tableSettingsBtn = document.getElementById("tableSettingsBtn");
const tableCloseBtn = document.getElementById("closeTableSettings");
const tablePanel = document.getElementById("tableSettingsPanel");
const closeDeleteColumnBtn = document.getElementById("closeDeleteColumnBtn");
const columnDeletePanel = document.getElementById("columnDeletePanel");
const columndeletelay = document.getElementById("columndeletelay");
const deleteColumnBtn = document.getElementById("deleteColumnBtn");
const columnOverlay = document.getElementById("columnOverlay");
const columnDeleteForm = document.getElementById("columnDeleteForm");
const editOverlay = document.getElementById("editOverlay");
const diskOptions = document.getElementById("diskUnitOptions");
const select = document.getElementById("server");
const serverekle = document.getElementById("serverekle");
const diskCheckbox = document.querySelector("input[name='fields'][value='disk_gb']");
const checkboxes = document.querySelectorAll('input[name="fields"]');
const searchInput = document.getElementById("searchInput");
const diskCompareOptions = document.getElementById("diskCompareOptions");
const columnForm = document.getElementById("columnForm");
let activeColumn = null;
let columnSearchActive = false;
let draggedKey = null;


if (deleteColumnBtn) {
    deleteColumnBtn.onclick = function () {
        openDeleteColumnPanel();
    };
}

function openDeleteColumnPanel() {

    document.body.classList.add("modal-open");

    fillDeleteColumn();

    document.getElementById("columnDeletePanel").style.right = "0";

    document.getElementById("columndeletelay").style.display = "block";
    tableSettingsOverlay.style.display = "none";

}

function closeDeleteColumnPanel() {

    document.body.classList.remove("modal-open");

    columnDeletePanel.style.right = "-420px";

    columndeletelay.style.display = "none";

}

if (columndeletelay) {
    columndeletelay.onclick = function () {
        closeDeleteColumnPanel();
    }
}

if (closeDeleteColumnBtn) {
    closeDeleteColumnBtn.onclick = function () {
        closeDeleteColumnPanel();
    };
}

function openColumnPanel() {

    document.body.classList.add("modal-open");

    fillColumn();

    document.getElementById("columnPanel").style.right = "0";

    columnOverlay.style.display = "block";
    tableSettingsOverlay.style.display = "none";

}

function closeColumnPanel() {

    document.body.classList.remove("modal-open");

    document.getElementById("columnPanel").style.right = "-420px";

    columnOverlay.style.display = "none";

}

if (columnOverlay) {
    columnOverlay.onclick = function () {
        closeColumnPanel();
    };
}

if (columnDeleteForm) {
    columnDeleteForm.onsubmit = function () {
        return confirm(window.translations?.confirm_delete_column || "Bu sütun silinecek. Devam etmek istiyor musunuz?");
    };
}

function fillDeleteColumn() {

    const select = document.getElementById("columnDeleteSelect");

    const option =
        select.options[select.selectedIndex];


    document.getElementById("columnDeleteForm").action =
        "/deleteColumn/" + option.value;

}

function fillColumn() {

    const select = document.getElementById("columnSelect");

    const option =
        select.options[select.selectedIndex];

    document.getElementById("columnName").value =
        option.dataset.name;

    document.getElementById("columnType").value =
        option.dataset.type;

    document.getElementById("columnForm").action =
        "/editcolumn/" + option.value;

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
    if (disk >= 1024) {
        disk = Number((disk / 1024).toFixed(2));
        document.getElementById("p_disktur").value = "TB";
    }
    else {
        disk = Number(parseFloat(disk).toFixed(2));
        document.getElementById("p_disktur").value = "GB";
    }
    document.getElementById("p_disk").value = disk;
    
    const serverSelect = document.getElementById("server");
    if (serverSelect) {
        serverSelect.value = (os && os !== "None") ? os : "";
        if (serverSelect.value === "Yeni") {
            if (serverekle) serverekle.style.display = "block";
            const yeniInput = document.getElementById("yeniIsletim");
            if (yeniInput) yeniInput.required = true;
        } else {
            if (serverekle) serverekle.style.display = "none";
            const yeniInput = document.getElementById("yeniIsletim");
            if (yeniInput) {
                yeniInput.required = false;
                yeniInput.value = "";
            }
        }
    }

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
    editOverlay.style.display = "block";
}

function closePanel() {
    document.body.classList.remove("modal-open");
    document.getElementById("editPanel").style.right = "-100%";
    editOverlay.style.display = "none";
}

if (editOverlay) {
    editOverlay.onclick = function () {
        closePanel();
    };
}

const searchBtn = document.getElementById("searchBtn");
const searchActive = window.location.pathname === "/search";

if (searchBtn) {
    searchBtn.onclick = function (e) {
        if (searchActive) {
            e.preventDefault();
            window.location.href = "/";
            return;
        }

        const query = searchInput ? searchInput.value.trim() : "";
        if (!query) {
            e.preventDefault();
            return;
        }

        const checkedFields = document.querySelectorAll('input[name="fields"]:checked');
        if (checkedFields.length === 0) {
            e.preventDefault();
            alert("Lütfen en az bir arama alanı seçin.");
            return;
        }
    };
}

if (select && serverekle) {

    select.addEventListener("change", function () {

        if (this.value === "Yeni") {

            serverekle.style.display = "block";

            document.getElementById("yeniIsletim").required = true;

        } else {

            serverekle.style.display = "none";

            document.getElementById("yeniIsletim").required = false;
            document.getElementById("yeniIsletim").value = "";

        }

    });

}

if (tableSettingsBtn) {
    tableSettingsBtn.onclick = function () {
        tableSettingsOverlay.style.display = "flex";
        document.body.classList.add("modal-open");
    };
}

if (tableCloseBtn) {
    tableCloseBtn.onclick = function () {
        tableSettingsOverlay.style.display = "none";
        document.body.classList.remove("modal-open");
    };
}

if (tableSettingsOverlay) {
    tableSettingsOverlay.onclick = function () {
        tableSettingsOverlay.style.display = "none";
        document.body.classList.remove("modal-open");
    };
}

if (searchSettingsBtn) {
    searchSettingsBtn.onclick = function () {
        overlay.style.display = "flex";
        document.body.classList.add("modal-open");
    };
}


if (tablePanel) {
    tablePanel.onclick = function (e) {
        e.stopPropagation();
    }
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



document.getElementById("selectAllBtn").onclick = function () {

    checkboxes.forEach(function (box) {
        box.checked = true;
    });

    updateDiskOptions();

};

document.getElementById("clearAllBtn").onclick = function () {

    checkboxes.forEach(function (box) {
        box.checked = false;
    });

    updateDiskOptions();

};

document.getElementById("searchBtn").onclick = function (e) {

    e.preventDefault();

    if (columnSearchActive) {

        const rows = document.querySelectorAll("#serverTable tbody tr.serverRow");

        rows.forEach(row => {
            row.style.display = "";
        });

        document.getElementById("serverCount").textContent = rows.length;

        columnSearchActive = false;
        updateSearchButton();

        return;
    }

    if (window.location.pathname === "/search") {
        window.location.href = "/";
        return;
    }

    let q = searchInput.value.trim();

    const selectedFields = document.querySelectorAll(
        "input[name='fields']:checked"
    );

    if (selectedFields.length === 0) {
        alert("Lütfen en az bir arama alanı seçin.");
        return;
    }

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

function updateDiskOptions() {

    if (diskCheckbox.checked) {

        diskOptions.style.display = "flex";
        diskCompareOptions.style.display = "flex";

    } else {

        diskOptions.style.display = "none";
        diskCompareOptions.style.display = "none";

    }

}

if (diskCheckbox) {
    diskCheckbox.addEventListener("change", updateDiskOptions);
    updateDiskOptions();
}

updateDiskOptions();

if (columnForm) {
    columnForm.onsubmit = function () {

        const select = document.getElementById("columnSelect");
        const option = select.options[select.selectedIndex];
        const originalType = option.dataset.type;

        const newType = document.getElementById("columnType").value;

        if (originalType !== newType) {
            return confirm(window.translations?.confirm_change_data_type || "Veri tipini değiştiriyorsunuz. Bu sütuna ait mevcut tüm değerler silinecek. Devam etmek istiyor musunuz?");
        }

        return true;

    };
}



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

    const table = document.getElementById("serverTable");
    if (!table) return;

    const headerRow = table.tHead.rows[0];
    const lastTh = document.getElementById("th_last");

    let order = [];

    if (saved) {
        try {
            order = JSON.parse(saved);
        } catch (e) {
            order = [];
        }
    }

    const currentColumns = Array.from(
        headerRow.querySelectorAll("th[data-col]")
    ).map(th => th.dataset.col);

    const newColumns = currentColumns.filter(
        col => !order.includes(col)
    );

    order = [
        ...order.filter(col => currentColumns.includes(col)),
        ...newColumns
    ];

    order.forEach(function (colKey) {

        const th = headerRow.querySelector(
            `th[data-col="${colKey}"]`
        );

        if (th) {
            headerRow.insertBefore(th, lastTh);
        }

    });

    Array.from(table.tBodies[0].rows).forEach(function (row) {

        const lastCell = row.cells[row.cells.length - 1];

        order.forEach(function (colKey) {

            const cell = row.querySelector(
                `[data-col="${colKey}"]`
            );

            if (cell) {
                row.insertBefore(cell, lastCell);
            }

        });

    });

    localStorage.setItem(
        "columnOrder",
        JSON.stringify(order)
    );
}

function toggleColumnMenu(event, colKey) {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
    event.stopPropagation();
    activeColumn = colKey;

    const menu = document.getElementById('sharedColumnMenu');
    const btn = event.currentTarget;

    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    } else {
        const rect = btn.getBoundingClientRect();

        const oldSearch = menu.querySelector('.col-search-box');
        if (oldSearch) oldSearch.remove();

        menu.style.display = 'block';

        let leftPos = rect.right - menu.offsetWidth;
        if (leftPos < 10) leftPos = rect.left;

        menu.style.top = (rect.bottom + 4) + 'px';
        menu.style.left = leftPos + 'px';
    }
}

function executeSort(order) {
    if (!activeColumn) return;
    sortTable(activeColumn, order);
    document.getElementById('sharedColumnMenu').style.display = 'none';
}

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

        input.oninput = function () {
            let val = this.value.toLowerCase();
            columnSearchActive = val.length > 0;

            const rows = document.querySelectorAll("#serverTable tbody tr.serverRow");

            let visibleCount = 0;

            rows.forEach(row => {
                let cell = row.querySelector(`[data-col="${activeColumn}"]`);

                if (cell) {
                    let text = cell.innerText.toLowerCase();

                    if (text.includes(val)) {
                        row.style.display = "";
                        visibleCount++;
                    } else {
                        row.style.display = "none";
                    }
                }
            });

            if (val === "") {
                document.getElementById("serverCount").textContent = rows.length;
            } else {
                document.getElementById("serverCount").textContent = visibleCount;
            }

            updateSearchButton();
        };
    }
}

function updateSearchButton() {

    const btn = document.getElementById("searchBtn");

    if (columnSearchActive) {
        btn.innerHTML = "⬅️ Geri Dön";
    }
    else {
        btn.innerHTML = "🔍 Ara";
    }

}

window.addEventListener('click', function () {
    const menu = document.getElementById('sharedColumnMenu');
    if (menu) menu.style.display = 'none';
});

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

window.addEventListener('scroll', function () {
    const menu = document.getElementById('sharedColumnMenu');
    if (menu && menu.style.display === 'block') {
        menu.style.display = 'none';
    }
}, { passive: true });

restoreColumnOrder();
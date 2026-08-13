const searchSettingsBtn = document.getElementById("searchSettingsBtn");
const searchSettingsOverlay = document.getElementById("searchSettingsOverlay");
const searchSettingsPanel = document.getElementById("searchSettingsPanel");
const closeSearchSettings = document.getElementById("closeSearchSettings");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const searchFields = document.querySelectorAll('input[name="fields"]');
const selectAllBtn = document.getElementById("selectAllBtn");
const clearAllBtn = document.getElementById("clearAllBtn");

let activeColumn = null;
let columnSearchActive = false;
let searchActive = false;
let draggedKey = null;

updateSearchButton();



if (searchBtn) {

    searchBtn.onclick = function (e) {

        e.preventDefault();

        if (searchActive) {

            window.location.href = "/networkdevices";

            return;
        }

    };

}

if (selectAllBtn) {

    selectAllBtn.onclick = function () {

        searchFields.forEach(function (box) {

            box.checked = true;

        });

    };

}


if (clearAllBtn) {

    clearAllBtn.onclick = function () {

        searchFields.forEach(function (box) {

            box.checked = false;

        });

    };

}

if (searchSettingsBtn) {

    searchSettingsBtn.onclick = function () {

        searchSettingsOverlay.style.display = "flex";

        document.body.classList.add("modal-open");

    };

}


if (closeSearchSettings) {

    closeSearchSettings.onclick = function () {

        searchSettingsOverlay.style.display = "none";

        document.body.classList.remove("modal-open");

    };

}


if (searchSettingsOverlay) {

    searchSettingsOverlay.onclick = function () {

        searchSettingsOverlay.style.display = "none";

        document.body.classList.remove("modal-open");

    };

}


if (searchSettingsPanel) {

    searchSettingsPanel.onclick = function (e) {

        e.stopPropagation();

    };

}

function getColumnOrder() {

    return Array.from(
        document.querySelectorAll("#networkDeviceTable thead th[data-col]")
    ).map(function (th) {
        return th.dataset.col;
    });

}

function applyColumnOrder(order) {

    const table = document.getElementById("networkDeviceTable");
    const headerRow = table.tHead.rows[0];

    order.forEach(function (colKey) {

        const th = headerRow.querySelector(`th[data-col="${colKey}"]`);

        if (th) {
            headerRow.appendChild(th);
        }

    });

    Array.from(table.tBodies[0].rows).forEach(function (row) {

        order.forEach(function (colKey) {

            const cell = row.querySelector(`[data-col="${colKey}"]`);

            if (cell) {
                row.appendChild(cell);
            }

        });

    });

}

function saveColumnOrder() {

    const order = Array.from(
        document.querySelectorAll("#networkDeviceTable thead th[data-col]")
    ).map(function (th) {
        return th.dataset.col;
    });

    localStorage.setItem(
        "networkDeviceColumnOrder",
        JSON.stringify(order)
    );

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

        if (!draggedKey || draggedKey === th.dataset.col) {
            return;
        }

        const order = getColumnOrder();

        const fromIndex = order.indexOf(draggedKey);

        if (fromIndex === -1) {
            return;
        }

        const rect = th.getBoundingClientRect();

        const isAfter =
            e.clientX > rect.left + rect.width / 2;

        order.splice(fromIndex, 1);

        let insertIndex =
            order.indexOf(th.dataset.col);

        if (isAfter) {
            insertIndex++;
        }

        order.splice(insertIndex, 0, draggedKey);

        applyColumnOrder(order);

    });

});

function restoreColumnOrder() {

    const saved =
        localStorage.getItem("networkDeviceColumnOrder");

    if (!saved) {
        return;
    }

    let order;

    try {
        order = JSON.parse(saved);
    }
    catch (e) {
        return;
    }

    applyColumnOrder(order);

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
            searchActive = val.length > 0;

            const rows = document.querySelectorAll("#networkDeviceTable tbody tr.serverRow");


            rows.forEach(row => {
                let cell = row.querySelector(`[data-col="${activeColumn}"]`);

                if (cell) {
                    let text = cell.innerText.toLowerCase();

                    if (text.includes(val)) {
                        row.style.display = "";
                    } else {
                        row.style.display = "none";
                    }
                }
            });

            updateSearchButton();
        };
    }
}

function updateSearchButton() {

    const btn = document.getElementById("searchBtn");

    if (!btn) return;

    if (
        searchActive ||
        window.location.pathname === "/networkdevices/search"
    ) {

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

    const table = document.getElementById("networkDeviceTable");
    const tbody = table.tBodies[0];

    const rows = Array.from(
        tbody.querySelectorAll("tr.serverRow")
    );

    rows.sort((a, b) => {

        let cellA = a.querySelector(`[data-col="${colKey}"]`)
            ? a.querySelector(`[data-col="${colKey}"]`).innerText.trim()
            : "";

        let cellB = b.querySelector(`[data-col="${colKey}"]`)
            ? b.querySelector(`[data-col="${colKey}"]`).innerText.trim()
            : "";

        let numA = parseFloat(cellA);
        let numB = parseFloat(cellB);

        if (!isNaN(numA) && !isNaN(numB)) {
            return order === 'asc'
                ? numA - numB
                : numB - numA;
        }

        return order === 'asc'
            ? cellA.localeCompare(cellB)
            : cellB.localeCompare(cellA);

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
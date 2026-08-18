const searchSettingsBtn = document.getElementById("searchSettingsBtn");
const searchSettingsOverlay = document.getElementById("searchSettingsOverlay");
const searchSettingsPanel = document.getElementById("searchSettingsPanel");
const closeSearchSettings = document.getElementById("closeSearchSettings");

const selectAllBtn = document.getElementById("selectAllBtn");
const clearAllBtn = document.getElementById("clearAllBtn");
const searchBtn = document.getElementById("searchBtn");
const searchInput = document.getElementById("searchInput");

let activeColumn = null;
let columnSearchActive = false;
let searchActive = window.location.pathname === "/clients/search";
let draggedKey = null;

function updateSearchButton() {
    const btn = document.getElementById("searchBtn");

    if (!btn) {
        return;
    }

    if (
        searchActive ||
        columnSearchActive ||
        window.location.pathname === "/clients/search"
    ) {
        btn.innerHTML = "⬅️ Geri Dön";
    } else {
        btn.innerHTML = "🔍 Ara";
    }
}

updateSearchButton();

if (searchBtn) {
    searchBtn.onclick = function (e) {

        if (
            searchActive ||
            columnSearchActive ||
            window.location.pathname === "/clients/search"
        ) {
            e.preventDefault();
            window.location.href = "/clients";
            return;
        }

        const query = searchInput
            ? searchInput.value.trim()
            : "";

        if (!query) {
            e.preventDefault();
            return;
        }

        const checkedFields =
            document.querySelectorAll(
                'input[name="fields"]:checked'
            );

        if (checkedFields.length === 0) {
            e.preventDefault();
            alert("Lütfen en az bir arama alanı seçin.");
            return;
        }
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

if (selectAllBtn) {
    selectAllBtn.onclick = function () {
        document
            .querySelectorAll('input[name="fields"]')
            .forEach(function (box) {
                box.checked = true;
            });
    };
}

if (clearAllBtn) {
    clearAllBtn.onclick = function () {
        document
            .querySelectorAll('input[name="fields"]')
            .forEach(function (box) {
                box.checked = false;
            });
    };
}

function getColumnOrder() {
    return Array.from(
        document.querySelectorAll(
            "#clientsTable thead th[data-col]"
        )
    ).map(function (th) {
        return th.dataset.col;
    });
}

function applyColumnOrder(order) {
    const table = document.getElementById("clientsTable");

    if (!table) {
        return;
    }

    const headerRow = table.tHead
        ? table.tHead.rows[0]
        : null;

    if (!headerRow) {
        return;
    }

    order.forEach(function (colKey) {
        const th = headerRow.querySelector(
            `th[data-col="${colKey}"]`
        );

        if (th) {
            headerRow.appendChild(th);
        }
    });

    const tbody = table.tBodies[0];

    if (!tbody) {
        return;
    }

    Array.from(tbody.rows).forEach(function (row) {
        order.forEach(function (colKey) {
            const cell = row.querySelector(
                `[data-col="${colKey}"]`
            );

            if (cell) {
                row.appendChild(cell);
            }
        });
    });
}

function saveColumnOrder() {
    const order = Array.from(
        document.querySelectorAll(
            "#clientsTable thead th[data-col]"
        )
    ).map(function (th) {
        return th.dataset.col;
    });

    localStorage.setItem(
        "clientsColumnOrder",
        JSON.stringify(order)
    );
}

document
    .querySelectorAll(".draggable-th")
    .forEach(function (th) {

        th.addEventListener(
            "dragstart",
            function () {
                draggedKey = th.dataset.col;
                th.classList.add("dragging");
            }
        );

        th.addEventListener(
            "dragend",
            function () {
                th.classList.remove("dragging");
                draggedKey = null;
                saveColumnOrder();
            }
        );

        th.addEventListener(
            "dragover",
            function (e) {
                e.preventDefault();

                if (
                    !draggedKey ||
                    draggedKey === th.dataset.col
                ) {
                    return;
                }

                const order = getColumnOrder();

                const fromIndex =
                    order.indexOf(draggedKey);

                if (fromIndex === -1) {
                    return;
                }

                const rect =
                    th.getBoundingClientRect();

                const isAfter =
                    e.clientX >
                    rect.left + rect.width / 2;

                order.splice(fromIndex, 1);

                let insertIndex =
                    order.indexOf(th.dataset.col);

                if (isAfter) {
                    insertIndex++;
                }

                order.splice(
                    insertIndex,
                    0,
                    draggedKey
                );

                applyColumnOrder(order);
            }
        );
    });

function restoreColumnOrder() {
    const saved =
        localStorage.getItem(
            "clientsColumnOrder"
        );

    if (!saved) {
        return;
    }

    let order;

    try {
        order = JSON.parse(saved);
    } catch (e) {
        return;
    }

    if (!Array.isArray(order)) {
        return;
    }

    applyColumnOrder(order);
}

function toggleColumnMenu(event, colKey) {
    event.stopPropagation();

    activeColumn = colKey;

    const menu =
        document.getElementById(
            "sharedColumnMenu"
        );

    const btn = event.currentTarget;

    if (!menu || !btn) {
        return;
    }

    if (menu.style.display === "block") {
        menu.style.display = "none";
        return;
    }

    const oldSearch =
        menu.querySelector(
            ".col-search-box"
        );

    if (oldSearch) {
        oldSearch.remove();
    }

    menu.style.display = "block";

    const rect =
        btn.getBoundingClientRect();

    let leftPos =
        rect.right -
        menu.offsetWidth;

    if (leftPos < 10) {
        leftPos = rect.left;
    }

    menu.style.top =
        (rect.bottom + 4) + "px";

    menu.style.left =
        leftPos + "px";
}

function executeSort(order) {
    if (!activeColumn) {
        return;
    }

    sortTable(
        activeColumn,
        order
    );

    const menu =
        document.getElementById(
            "sharedColumnMenu"
        );

    if (menu) {
        menu.style.display = "none";
    }
}

function openSharedSearch(event) {
    event.stopPropagation();

    const menu =
        document.getElementById(
            "sharedColumnMenu"
        );

    if (!menu) {
        return;
    }

    if (!menu.querySelector(".col-search-box")) {

        const searchDiv =
            document.createElement("div");

        searchDiv.className =
            "col-search-box";

        searchDiv.innerHTML =
            `<input
                type="text"
                placeholder="Aranacak kelime..."
                class="col-filter-input"
                onclick="event.stopPropagation()"
            >`;

        menu.appendChild(searchDiv);

        const input =
            searchDiv.querySelector("input");

        input.focus();

        input.oninput = function () {

            const val =
                this.value.toLowerCase();

            const rows =
                document.querySelectorAll(
                    "#clientsTable tbody tr.serverRow"
                );

            if (val.length === 0) {

                columnSearchActive = false;
                searchActive = false;

                rows.forEach(function (row) {
                    row.style.display = "";
                });

                updateSearchButton();

                return;
            }

            columnSearchActive = true;
            searchActive = true;

            rows.forEach(function (row) {

                const cell =
                    row.querySelector(
                        `[data-col="${activeColumn}"]`
                    );

                if (cell) {

                    const text =
                        cell.innerText.toLowerCase();

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

window.addEventListener(
    "click",
    function () {

        const menu =
            document.getElementById(
                "sharedColumnMenu"
            );

        if (menu) {
            menu.style.display = "none";
        }
    }
);

function sortTable(colKey, order) {

    const table =
        document.getElementById(
            "clientsTable"
        );

    if (!table) {
        return;
    }

    const tbody =
        table.tBodies[0];

    if (!tbody) {
        return;
    }

    const rows =
        Array.from(
            tbody.querySelectorAll(
                "tr.serverRow"
            )
        );

    rows.sort(function (a, b) {

        const cellA =
            a.querySelector(
                `[data-col="${colKey}"]`
            );

        const cellB =
            b.querySelector(
                `[data-col="${colKey}"]`
            );

        const textA =
            cellA
                ? cellA.innerText.trim()
                : "";

        const textB =
            cellB
                ? cellB.innerText.trim()
                : "";

        const numA =
            parseFloat(textA);

        const numB =
            parseFloat(textB);

        if (
            !isNaN(numA) &&
            !isNaN(numB)
        ) {
            return order === "asc"
                ? numA - numB
                : numB - numA;
        }

        return order === "asc"
            ? textA.localeCompare(textB)
            : textB.localeCompare(textA);
    });

    rows.forEach(function (row) {
        tbody.appendChild(row);
    });
}

window.addEventListener(
    "scroll",
    function () {

        const menu =
            document.getElementById(
                "sharedColumnMenu"
            );

        if (
            menu &&
            menu.style.display === "block"
        ) {
            menu.style.display = "none";
        }
    },
    {
        passive: true
    }
);

restoreColumnOrder();
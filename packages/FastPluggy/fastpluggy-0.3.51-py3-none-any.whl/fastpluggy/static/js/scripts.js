/* scripts.js */

// ------------------------------------------------------
// 📢 Enhanced Toast Notification
// ------------------------------------------------------
function showNotification(message, level = "info", link = null) {
    const container = document.getElementById("notifications");

    if (!container) {
        console.warn("[Notification] Container not found");
        return;
    }

    const levelClasses = {
        info: "bg-primary text-white",
        warning: "bg-warning text-dark",
        error: "bg-danger text-white",
        success: "bg-success text-white"
    };
    const colorClass = levelClasses[level] || "bg-primary text-white";

    const textNode = document.createElement("div");
    textNode.appendChild(document.createTextNode(message));
    const escapedMessage = textNode.innerHTML;

    const notification = document.createElement("div");
    notification.className = `toast show mb-3 ${colorClass}`;
    notification.role = "alert";

    let toastContent = `
        <div class="toast-header">
            <strong class="me-auto">Task Update</strong>
            <button type="button" class="btn-close ms-2 mb-1" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${escapedMessage}
    `;

    if (link) {
        toastContent += `
            <div class="mt-2">
                <a href="${link}" target="_blank" class="text-white text-decoration-underline">View details</a>
            </div>
        `;
    }

    toastContent += `</div>`;
    notification.innerHTML = toastContent;

    container.appendChild(notification);

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
        if (container.contains(notification)) {
            container.removeChild(notification);
        }
    }, 5000);

    // Handle manual close button
    const closeButton = notification.querySelector('.btn-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            if (container.contains(notification)) {
                container.removeChild(notification);
            }
        });
    }
}

(function () {
    function loadFromLocalStorage(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            return value !== null ? JSON.parse(value) : defaultValue;
        } catch (e) {
            console.warn("Error loading key:", key, e);
            return defaultValue;
        }
    }

    function saveToLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn("Error saving key:", key, e);
        }
    }

    function initAutoLocalStorage() {
        const elements = document.querySelectorAll('[data-ls-key]');
        elements.forEach(el => {
            const key = el.dataset.lsKey;

            // --- Load initial value ---
            const saved = loadFromLocalStorage(key);
            if (saved !== null) {
                if (el.type === 'checkbox') {
                    el.checked = !!saved;
                } else {
                    el.value = saved;
                }
            }

            // --- Save on change ---
            const eventType = (el.type === 'checkbox' || el.tagName === 'SELECT') ? 'change' : 'input';
            el.addEventListener(eventType, () => {
                const value = (el.type === 'checkbox') ? el.checked : el.value;
                saveToLocalStorage(key, value);
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAutoLocalStorage);
    } else {
        initAutoLocalStorage();
    }
})();

// ------------------------------------------------------
// 🌙 Day/Night Theme Toggle (Tabler)
// ------------------------------------------------------
(function() {
    function initThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) {
            return; // Theme toggle not present on this page
        }

        // Load saved theme preference or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);

        // Add click event listener
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    function applyTheme(theme) {
        const themeToggle = document.getElementById('theme-toggle');
        const themeIcon = themeToggle ? themeToggle.querySelector('i') : null;
        
        if (!themeToggle || !themeIcon) {
            return;
        }

        // Set Tabler's data-bs-theme attribute on html element
        document.documentElement.setAttribute('data-bs-theme', theme);

        // Update icon using Tabler Icons
        if (theme === 'dark') {
            themeIcon.classList.remove('ti-moon');
            themeIcon.classList.add('ti-sun');
            themeToggle.setAttribute('title', 'Switch to Light Mode');
        } else {
            themeIcon.classList.remove('ti-sun');
            themeIcon.classList.add('ti-moon');
            themeToggle.setAttribute('title', 'Switch to Dark Mode');
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeToggle);
    } else {
        initThemeToggle();
    }
})();

// ------------------------------------------------------
// 📁 Collapsible Sidebar Toggle with Enhanced Features
// ------------------------------------------------------
(function() {
    let tooltipInstances = [];

    function initSidebarToggle() {
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');

        if (!sidebarToggle || !sidebar) {
            return; // Sidebar toggle not present on this page
        }

        // Load saved sidebar state or default to expanded
        const savedState = localStorage.getItem('sidebarCollapsed') || 'false';
        applySidebarState(savedState === 'true');

        // Add click event listener for toggle button
        sidebarToggle.addEventListener('click', function() {
            const isCollapsed = sidebar.classList.contains('collapsed');
            const newState = !isCollapsed;
            applySidebarState(newState);
            localStorage.setItem('sidebarCollapsed', newState.toString());
        });

        // Add auto-collapse when clicking menu items
        initAutoCollapse(sidebar);
    }

    function applySidebarState(isCollapsed) {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) {
            return;
        }

        if (isCollapsed) {
            sidebar.classList.add('collapsed');
            initTooltips();
        } else {
            sidebar.classList.remove('collapsed');
            destroyTooltips();
        }
    }

    function initTooltips() {
        // Destroy existing tooltips first
        destroyTooltips();

        // Initialize tooltips ONLY for non-dropdown menu items
        // Dropdown toggles already have Bootstrap dropdown bound, so we can't add tooltips to them
        const menuLinks = document.querySelectorAll('#sidebar [data-menu-label]:not([data-bs-toggle="dropdown"])');
        menuLinks.forEach(link => {
            const label = link.getAttribute('data-menu-label');
            if (label && typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                const tooltip = new bootstrap.Tooltip(link, {
                    title: label,
                    placement: 'right',
                    trigger: 'hover',
                    delay: { show: 300, hide: 100 }
                });
                tooltipInstances.push(tooltip);
            }
        });
    }

    function destroyTooltips() {
        // Dispose all tooltip instances
        tooltipInstances.forEach(tooltip => {
            if (tooltip && tooltip.dispose) {
                tooltip.dispose();
            }
        });
        tooltipInstances = [];
    }

    function initAutoCollapse(sidebar) {
        // Add click event listener to all menu links (except dropdown toggles)
        sidebar.addEventListener('click', function(event) {
            const target = event.target.closest('a.nav-link, a.dropdown-item');

            // Only auto-collapse if:
            // 1. Sidebar is collapsed
            // 2. Target is a link (not a dropdown toggle)
            // 3. Link has a real URL (not '#')
            if (target &&
                sidebar.classList.contains('collapsed') &&
                !target.classList.contains('dropdown-toggle') &&
                target.getAttribute('href') !== '#') {

                // Small delay to allow navigation
                setTimeout(() => {
                    sidebar.classList.remove('collapsed');
                    localStorage.setItem('sidebarCollapsed', 'false');
                    destroyTooltips();
                }, 100);
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebarToggle);
    } else {
        initSidebarToggle();
    }
})();

define([], function () {
    const SidebarManager = {
        sidebar: document.querySelector("#sidebar"),

        toggleSidebar: function () {
            // Toggle the sidebar's expand class
            this.sidebar.classList.toggle("expand");
            // Toggle the visibility of the logout text
            const logout_text = document.querySelector("#sidebar .logout-btn .text");
            const logout_icon = document.querySelector("#sidebar .logout-btn .bi");
            logout_icon.classList.toggle("me-2");
            if (logout_text.classList.contains("d-none")) {
                setTimeout(() => {
                    logout_text.classList.toggle("d-none");
                }, 200);
            } else {
                logout_text.classList.add("d-none");
            }
        },

        checkSidebarVisibility: function () {
            const isCurrentlyVisible = window.innerWidth >= 1080;
            this.sidebar.classList.toggle("expand", isCurrentlyVisible);
        },

        init: function () {
            // Toggle Sidebar on Button Click
            document.querySelector(".toggle-btn").addEventListener("click", () => {
                this.toggleSidebar();
            });

            // Check Sidebar Visibility on Resize
            window.addEventListener("resize", () => {
                this.checkSidebarVisibility();
            });

            // Initial Sidebar Visibility Check
            this.checkSidebarVisibility();

        }
    };

    return SidebarManager;
});
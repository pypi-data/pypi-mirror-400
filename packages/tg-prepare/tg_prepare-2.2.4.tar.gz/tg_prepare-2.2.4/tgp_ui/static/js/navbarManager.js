define([], function () {
    const NavbarManager = {
        resetButtons: function (buttons, additionalClasses = []) {
            buttons.forEach(btn => {
                btn.classList.remove('animate-to-long', 'border-primary', ...additionalClasses);
                const icon = btn.querySelector('i');
                const subButtons = btn.querySelector('.sub-buttons');

                if (icon) icon.classList.remove('d-none');
                if (subButtons) {
                    subButtons.classList.add('d-none');
                    subButtons.style.opacity = '0';
                }

                btn.style.width = ''; // Reset width

                // Füge für kleine Buttons die Outline-Secondary-Klasse wieder hinzu
                if (btn.classList.contains('btn-sm')) {
                    btn.classList.add('btn-outline-secondary');
                }
            });
        },

        activateButton: function (button, index, buttons) {
            // Vorherige Buttons hervorheben / Progress anzeigen
            for (let i = 0; i <= index; i++) {
                buttons[i].classList.add('border-primary');
            }

            // Aktuellen Button erweitern
            button.classList.add('animate-to-long');
            const icon = button.querySelector('i');
            const subButtons = button.querySelector('.sub-buttons');

            if (icon) icon.classList.add('d-none');
            if (subButtons) {
                subButtons.classList.remove('d-none');
                setTimeout(() => {
                    subButtons.style.opacity = '1';
                }, 300);

                // Ersten kleinen Button klicken, wenn kein last-opened vorhanden
                const lastOpenedButton = subButtons.querySelector('.last-opened');
                if (lastOpenedButton) {
                    lastOpenedButton.click();
                } else {
                    const firstSmButton = subButtons.querySelector('.btn-sm');
                    if (firstSmButton) firstSmButton.click();
                }
            }

            // Dynamische Breite basierend auf kleinen Buttons
            const smallButtonsCount = subButtons?.querySelectorAll('.btn-sm').length || 0;
            const sizeAdjustment = smallButtonsCount * 5.4;
            button.style.width = `${sizeAdjustment}rem`;
        },

        adjustLine: function (button) {
            const container = document.querySelector('.container.bg'); // Container der Buttons
            const lineBlue = document.querySelector('.line.blue'); // Zweite Linie
            const containerRect = container.getBoundingClientRect(); // Position des Containers
            const buttonRect = button.getBoundingClientRect(); // Position des angeklickten Buttons

            // Berechne die Breite der Linie basierend auf der Position des Buttons
            const newWidth = buttonRect.left - containerRect.left + buttonRect.width / 2;
            lineBlue.style.width = `${newWidth}px`; // Setze die neue Breite der Linie
        },

        triggerLastOpenedTab: function (projectname) {
            fetch(prefix + `/get_last_tab/${projectname}`)
                .then(response => response.json())
                .then(data => {
                    if (data.initial_tab) {
                        const initialTab = document.querySelector('.btn-sm[data-bs-target="#${data.initial_tab}"]');
                        if (initialTab) {
                            initialTab.closest('.btn-xl').click();
                            initialTab.click();
                        }
                    }
                })
                .catch(error => console.error('Error fetching initial tab:', error));
        },

        setLastOpenedTab: function (projectname, tab) {
            fetch(prefix + `/set_last_tab/${projectname}/${tab}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ projectname: projectname, tab: tab })
            })
                .then(response => response.json())
                .catch(error => console.error('Error writing last tab:', error));
        },

        init: function () {
            // Event-Listener für große Buttons (btn-xl)
            document.querySelectorAll('.btn-xl').forEach((button, index, buttons) => {
                button.addEventListener('click', () => {
                    // Delete activate class from all small buttons
                    const smBtnContainer = button.closest('.container.bg');
                    smBtnContainer.querySelectorAll('.btn-sm').forEach(btn => {
                        btn.classList.remove('active');
                    });

                    this.resetButtons(document.querySelectorAll('.btn-xl'));
                    this.activateButton(button, index, buttons);
                    this.adjustLine(button);
                });
            });

            // Event-Listener für kleine Buttons (btn-sm)
            document.querySelectorAll('.btn-sm').forEach(button => {
                button.addEventListener('click', event => {
                    event.stopPropagation(); // Verhindert, dass der große Button reagiert

                    // Alle kleinen Buttons in der gleichen Sektion zurücksetzen
                    const parentSection = button.closest('.sub-buttons');
                    this.resetButtons(parentSection.querySelectorAll('.btn-sm'), ['btn-outline-primary', 'last-opened']);

                    // Aktuellen Button aktivieren
                    button.classList.add('btn-outline-primary', 'last-opened');
                    button.classList.remove('btn-outline-secondary');

                    // Setze den zuletzt geöffneten Tab
                    const projectname = this.getActiveProjectName();
                    const tab = button.getAttribute('data-bs-target').replace('#', '');
                    this.setLastOpenedTab(projectname, tab);
                });
            });

            // Initialisiere den zuletzt geöffneten Tab
            const projectname = this.getActiveProjectName();
            if (projectname) {
                this.triggerLastOpenedTab(projectname);
            }
        },

        getActiveProjectName: function () {
            const activeBtn = Array.from(document.querySelectorAll('.project-btn'))
                .find(btn => btn.querySelector('.bi.bi-circle-fill'));
            if (activeBtn) {
                const nameSpan = activeBtn.querySelector('.projectname');
                return nameSpan ? nameSpan.textContent : null;
            }
            return null;
        }
    };

    return NavbarManager;
});
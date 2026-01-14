require.config({
    baseUrl: '/static/js',
    paths: {
        bootstrap: 'bootstrap.bundle.min',
        jquery: 'jquery.min',
        simpleXML: 'simpleXML',
    },
    shim: {
        jquery: {
            exports: '$'
        },
        simpleXML: {
            deps: ['jquery'],
            exports: 'simpleXML'
        }
    }
});

require([
    'bootstrap', 'jquery', 'simpleXML', 'tabManager', 'modalManager', 'fileManager', 'sidebarManager', 'navbarManager', 'collectionManager', 'projectManager'],
    function (bootstrap, $, simpleXML, TabManager, ModalManager, FileManager, SidebarManager, NavbarManager, CollectionManager, ProjectManager) {
        $(document).ready(function () {
            // Initialize all generic managers
            TabManager.init();
            ModalManager.init();
            FileManager.init();
            SidebarManager.init();
            NavbarManager.init();

            // Initialize all specific managers
            CollectionManager.init();
            ProjectManager.init();

            console.log('Modules loaded successfully!');
        });
    });
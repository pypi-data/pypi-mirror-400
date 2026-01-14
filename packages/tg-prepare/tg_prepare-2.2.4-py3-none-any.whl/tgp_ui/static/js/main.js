var done = false;
const prefixes = window.location.pathname.split('/').filter(function (part) {
    if (['project', 'projects'].indexOf(part) !== -1) {
        // make sure to stop at 'project' or 'projects' to not include any further path parts
        done = true;
    }
    if (part === '' || done) {
        return false;
    } else {
        return true;
    }
});
var prefix = '';
if (prefixes.length > 0) {
    prefix += '/';
    prefix += prefixes.join('/');
}
console.log('Using prefix:', prefix);

require.config({
    baseUrl: prefix + '/static/js',
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
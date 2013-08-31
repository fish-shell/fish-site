$(function () {
    // Show correct tab

    var plat = navigator.platform.toUpperCase();
    var isMac = plat.indexOf('MAC') !== -1;
    var isLinux = plat.indexOf('LINUX') !== -1;

    var which = 'get_fish_tarball';
    if (isMac) {
        which = 'get_fish_mac'
    } else if (isLinux) {
        which = 'get_fish_linux';
    }

    $('#platform_tabs a[href="#' + which + '"]').tab('show');
});

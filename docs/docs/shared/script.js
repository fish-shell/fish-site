// Unhide our old-docs banner if this is not the latest version.
(function () {
    // We expect a global FISH_DOCS_VERSION variable.
    const this_version = window.FISH_DOCS_VERSION;
    if (!this_version) return;

    function process(version_json) {
        const latest_version = version_json["LATEST_VERSION"];
        if (!latest_version) {
            return;
        }
        // Keep only the major version.
        const maj_version = latest_version.split(".").slice(0, 2).join(".");
        if (maj_version !== this_version) {
            const elem = document.getElementById("old-docs-notice");
            if (elem) elem.style.removeProperty('display');
        }
    };

    fetch('/release_version.json')
        .then((r) => r.json())
        .then(process)
        .catch(() => void 0);
})();

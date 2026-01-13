function close_modal() {
    $('.modal-backdrop').click()
}

function close_sidebar() {
    $('body').removeClass('sidebar-open');
}

function toggle_sidebar() {
    if (window.innerWidth >= 1024) {
        $('body').toggleClass('sidebar-collapsed');
    } else {
        $('body').toggleClass('sidebar-open');
    }
}

$('#menu-toggle').click(() => {
    toggle_sidebar();
});

$('#sidebar-overlay').click(() => {
    close_sidebar();
});

$(window).on('resize', function () {
    if (window.innerWidth >= 1024) {
        close_sidebar();
    }
});

const sidebarSearch = document.getElementById('sidebar-search');
if (sidebarSearch) {
    sidebarSearch.addEventListener('input', (event) => {
        const query = event.target.value.trim().toLowerCase();
        const items = document.querySelectorAll('li[data-menu-item]');
        items.forEach((item) => {
            const text = (item.dataset.menuText || item.textContent || '').toLowerCase();
            const shouldShow = !query || text.includes(query);
            item.classList.toggle('hidden', !shouldShow);
        });

        const groups = document.querySelectorAll('li[data-menu-group]');
        groups.forEach((group) => {
            const groupText = (group.dataset.menuText || '').toLowerCase();
            const children = group.querySelectorAll('li[data-menu-item]');
            let childVisible = false;
            children.forEach((child) => {
                if (!child.classList.contains('hidden')) {
                    childVisible = true;
                }
            });

            if (query && groupText.includes(query)) {
                group.classList.remove('hidden');
                children.forEach((child) => child.classList.remove('hidden'));
                const details = group.querySelector('details');
                if (details) {
                    details.setAttribute('open', 'open');
                }
                return;
            }

            if (query && !childVisible) {
                group.classList.add('hidden');
            } else {
                group.classList.remove('hidden');
            }
        });
    });
}


// jquery toggle whole attribute
$.fn.toggleAttr = function (attr, val) {
    var test = $(this).attr(attr);
    if (test) {
        // if attrib exists with ANY value, still remove it
        $(this).removeAttr(attr);
    } else {
        $(this).attr(attr, val);
    }
    return this;
};

// jquery toggle just the attribute value
$.fn.toggleAttrVal = function (attr, val1, val2) {
    var test = $(this).attr(attr);
    if (test === val1) {
        $(this).attr(attr, val2);
        return this;
    }
    if (test === val2) {
        $(this).attr(attr, val1);
        return this;
    }
    // default to val1 if neither
    $(this).attr(attr, val1);
    return this;
};

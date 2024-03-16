$(document).ready(function() {
    var urlParams = new URLSearchParams(window.location.search);
    var section = urlParams.get('section');
    if (section) {
        var target = $('#' + section);
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top
            }, 1000);
        }
    }

    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top
            }, 1000);
        }
    });

    $('#scrollToTop').on('click', function(event) {
        event.preventDefault();
        $('html, body').stop().animate({
            scrollTop: 0
        }, 1000);
    });
});
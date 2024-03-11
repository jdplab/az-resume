function toggleMenu() {
    var links = document.getElementById("links");
    var iconborder = document.getElementById('iconborder');
    if (iconborder.classList.contains('active')) {
        links.style.visibility = 'hidden';
        iconborder.classList.remove('active');
        links.classList.remove('animate', 'animate-in');
    } else {
        links.style.visibility = 'visible';
        iconborder.classList.add('active');
        links.classList.add('animate', 'animate-in');
    }
}

document.addEventListener('click', function(event) {
    var iconborder = document.getElementById('iconborder');
    var links = document.getElementById("links");
    if (event.target != iconborder && event.target.parentNode != iconborder && event.target.parentNode.parentNode != iconborder) {
        if (iconborder.classList.contains('active')) {
            links.style.visibility = 'hidden';
            iconborder.classList.remove('active');
            links.classList.remove('animate', 'animate-in');
        }
    }
});

window.addEventListener('resize', function() {
    var iconborder = document.getElementById('iconborder');
    var links = document.getElementById("links");
    if (iconborder.classList.contains('active')) {
        links.style.visibility = 'hidden';
        iconborder.classList.remove('active');
        links.classList.remove('animate', 'animate-in');
    }
});
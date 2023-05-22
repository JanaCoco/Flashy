window.onscroll = function() {fixNavbar()};

var navbar = document.getElementById("navbar");
var fixpoint = navbar.offsetTop;

function fixNavbar(){
    if (window.pageYOffset >= fixpoint) {
        navbar.classList.add("fixed");
    }
    else {
        navbar.classList.remove("fixed");
    }
}


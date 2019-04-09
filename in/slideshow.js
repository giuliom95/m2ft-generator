// var num_images must be set from html
var current = 0;

function next_image() {
    document.getElementById('image' + current).style.visibility = 'hidden'
    current++;
    if(current == num_images)
        current = 0;
    document.getElementById('image' + current).style.visibility = 'visible'
}


function prev_image() {
    document.getElementById('image' + current).style.visibility = 'hidden'
    current--;
    if(current == -1)
        current = num_images - 1;
    document.getElementById('image' + current).style.visibility = 'visible'
}




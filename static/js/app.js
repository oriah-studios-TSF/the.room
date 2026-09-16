// Toggle between showing and hiding the dropdown content
function toggleDropdown() {
    document.getElementById('dropdownMenu').classList.toggle('show');     
}

// Live Current date and time
const date = new Date();
const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
document.getElementById('date-time').innerHTML = date.toLocaleDateString('en-ZA', options);

// Live Clock
const clock = document.getElementById('clock');
setInterval(() => {
  const date = new Date();
  clock.innerHTML = date.toLocaleTimeString();
}, 1000);

// Home messages
const messages = [
    "Take your time. There's no rush.",
    "Let's see where today takes us.",
    "Maybe today can be a little lighter.",
    "No expectations. Just a little space to be.",
    "Whatever today becomes, that's okay.",
    "You don't have to figure everything out today.",
    "Some days are for talking. Some are just for being here.",
    "A quiet place for a quiet moment.",
    "It's okay if things take time.",
    "You can stay for a while.",
    "Maybe we can make today a good one.",
    "Not everything needs an answer right away.",
    "One moment at a time.",
    "There's nowhere else you need to be right now.",
    "Maybe something good is waiting here.",
    "Take a breath. You're here.",
    "No plans required.",
    "We can just see what happens.",
    "Somewhere to pause for a little while.",
    "Today doesn't have to be perfect.",
    "It's nice to have somewhere to come back to.",
    "Whatever you're feeling, take your time.",
    "Maybe a little music. Maybe a movie. Maybe nothing.",
    "For the moments that don't need much.",
    "Let's not worry about tomorrow just yet.",
    "A little space away from everything else.",
    "You don't have to rush this.",
    "Maybe today is enough.",
    "Come in. Get comfortable.",
    "Let's make the most of this moment."
];

const message = document.getElementById('homeMessage');

function changeMessage() {
    message.classList.add('changing');

    setTimeout(() => {
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        message.innerHTML = randomMessage;
        message.classList.remove('changing');
    }, 600);
}

changeMessage();

setInterval(changeMessage, 1800000);

// On click show different containers 
function showContainer(containerId) {
    const containers = document.querySelectorAll('.container');
    containers.forEach(container => {
        container.style.display = 'none';
    });
    document.getElementById(containerId).style.display = 'block';
}

// Auto hide messages
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.classList.add('hide');
    setTimeout(() => msg.remove(), 500); // remove after fadeUp
  }, 10000); // 10 seconds
});

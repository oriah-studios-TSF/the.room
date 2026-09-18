// Toggle between showing and hiding the dropdown content.
function toggleDropdown() {
    document.getElementById('dropdownMenu').classList.toggle('show');     
}

// Display the current date when the page loads.
const date = new Date();
const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
document.getElementById('date-time').innerHTML = date.toLocaleDateString('en-ZA', options);

// Update the live clock every second.
const clock = document.getElementById('clock');
setInterval(() => {
  const date = new Date();
  clock.innerHTML = date.toLocaleTimeString();
}, 1000);

// Messages shown on the home page.
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

// Show the selected page container and hide the others.
function showContainer(containerId) {
    const containers = document.querySelectorAll('.container');
    containers.forEach(container => {
        container.style.display = 'none';
    });
    document.getElementById(containerId).style.display = 'block';
}

// Automatically hide notification messages after ten seconds.
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.classList.add('hide');
    setTimeout(() => msg.remove(), 500); // remove after fadeUp
  }, 10000); // 10 seconds
});


// Chat panel and real-time messaging.
const socket = io();

const openChatBtn = document.getElementById('openChatBtn');
const chatPanel = document.getElementById('chatPanel');
const closeChatBtn = document.getElementById('closeChatBtn');

if (openChatBtn && chatPanel && closeChatBtn) {
    openChatBtn.addEventListener('click', function() {
        chatPanel.classList.add('active');
    });

    closeChatBtn.addEventListener('click', function() {
        chatPanel.classList.remove('active');
    });
}

const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');
const chatMessages = document.getElementById('chatMessages');

if (chatInput && sendChatBtn && chatMessages) {
    sendChatBtn.addEventListener('click', function() {
        const message = chatInput.value.trim();

        if (!message) {
            return;
        }

        socket.emit('send_message', {
            message: message
        });

        chatInput.value = '';
    });

    chatInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendChatBtn.click();
        }
    });
}

socket.on('receive_message', function(data) {
    const messageElement = document.createElement('p');
    messageElement.classList.add('chat-message');
    messageElement.textContent = data.message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

// Synchronise movie playback between connected clients.
const moviePlayer = document.getElementById('moviePlayer');
let isSynced = false;
let hasInteracted = false;
let isSeek = false;

if (moviePlayer) {
    moviePlayer.addEventListener('click', function() {
       hasInteracted = true;
    });

    moviePlayer.addEventListener('play', function() {
       hasInteracted = true;

       if (isSynced) {
            return;
        }


        socket.emit('movie_play', {
            currentTime: moviePlayer.currentTime
        });
    });

    moviePlayer.addEventListener('pause', function() {
       hasInteracted = true;

       if (isSynced) {
            return;
        }


        socket.emit('movie_pause', {
            currentTime: moviePlayer.currentTime
        });
    });

    moviePlayer.addEventListener('seeked', function() {
        if (isSeek) {
            isSeek = false;
            return;
        }


        socket.emit('movie_seek', {
            currentTime: moviePlayer.currentTime
        });
    });

    socket.on('movie_play', function(data) {

        isSynced = true;
        moviePlayer.currentTime = data.currentTime;

        if (hasInteracted) {
            moviePlayer.play().catch(function(error) {
                console.error('Remote play was blocked:', error);
            });
        } else {
            console.log('Waiting for user interaction...');
        }

        isSynced = false;
    });

    socket.on('movie_pause', function(data) {

        isSynced = true;
        moviePlayer.currentTime = data.currentTime;
        moviePlayer.pause();
        isSynced = false;
    });

    socket.on('movie_seek', function(data) {

        isSeek = true;
        moviePlayer.currentTime = data.currentTime;
    });
}

/*
 * Voice call panel
 *
 * Temporarily disabled. Keep this code here for when voice calling is
 * enabled again.
 */
/*
const voiceCallBtn = document.getElementById('voiceCallBtn');
const voiceCallPanel = document.getElementById('voiceCallPanel');
const closeVoiceCallBtn = document.getElementById('closeVoiceCallBtn');
const voiceCall = document.getElementById('voiceCall');

let peerConnection = null;
let localStream = null;
let isVoiceCaller = null;
let voiceCallReady = null;
let pendingIceCandidates = [];

const rtcConfig = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};

if (voiceCallBtn && voiceCallPanel && closeVoiceCallBtn) {
    voiceCallBtn.addEventListener('click', function() {
        voiceCallPanel.classList.add('active');
        isVoiceCaller = true;
        startVoiceCall();
    });

    closeVoiceCallBtn.addEventListener('click', function() {
        voiceCallPanel.classList.remove('active');
    });
}

async function startVoiceCall() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        createPeerConnection();

        socket.emit('voice_call');

        if (isVoiceCaller) {
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);

            socket.emit('voice_offer', {
                offer: offer
            });
        }

    } catch (error) {
        console.error('Error accessing media devices:', error);
    }


}

socket.on('voice_call', async function() {

    if (!peerConnection) {
       voiceCallReady = navigator.mediaDevices.getUserMedia({ audio: true });

       localStream = await voiceCallReady;

       createPeerConnection();
    }
});

socket.on('voice_offer', async function(data) {

    if (voiceCallReady) {
        await voiceCallReady;
    }

    if (!peerConnection) {
        return;
    }

    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));

    for (const candidate of pendingIceCandidates) {
        await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    }

    pendingIceCandidates = [];

    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);

    socket.emit('voice_answer', {
        answer: answer
    });
});

socket.on('voice_answer', async function(data) {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));

});

socket.on('voice_ice_candidate', async function(data) {

    if (!peerConnection) {
        return;
    }

    if (!peerConnection.remoteDescription) {
        pendingIceCandidates.push(data.candidate);
        return;
    } 

    await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
});

function createPeerConnection() {
    peerConnection = new RTCPeerConnection(rtcConfig);

    localStream.getTracks().forEach(function(track) {
        peerConnection.addTrack(track, localStream);
    });

    peerConnection.onicecandidate = function(event) {
       if (event.candidate && event.candidate.sdpMLineIndex !== null && event.candidate.sdpMid !== null) {
           socket.emit('voice_ice_candidate', {
               candidate: event.candidate
           })
       }
    };

    peerConnection.ontrack = function(event) {

        let remoteAudio = document.getElementById('remoteAudio');
        
        if (!remoteAudio) {
            remoteAudio = document.createElement('audio');
            remoteAudio.id = 'remoteAudio';
            remoteAudio.autoplay = true;
            voiceCall.appendChild(remoteAudio);
        }

        remoteAudio.srcObject = event.streams[0];
    };
};
*/

/* ===== VOICE INPUT ===== */

function startVoiceInput(fieldId) {

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if(!SpeechRecognition){
        alert("Voice recognition not supported in this browser");
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.interimResults = false;

    recognition.start();

    recognition.onresult = function(event){

        const speech = event.results[0][0].transcript;

        document.getElementById(fieldId).value = speech;

    };

}

/* ===== VOICE OUTPUT ===== */

function speakText(text){

    const speech = new SpeechSynthesisUtterance(text);

    speech.lang = "en-IN";
    speech.rate = 1;

    window.speechSynthesis.speak(speech);

}
function startVoiceAssistant(language){

let langCode="en-US"

if(language==="kn") langCode="kn-IN"
if(language==="te") langCode="te-IN"
if(language==="ta") langCode="ta-IN"
if(language==="hi") langCode="hi-IN"

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

const recognition = new SpeechRecognition()

recognition.lang = langCode

recognition.start()

recognition.onresult=function(event){

const command=event.results[0][0].transcript.toLowerCase()

console.log(command)

if(command.includes("location") || command.includes("ಸ್ಥಳ") || command.includes("స్థానం") || command.includes("स्थान")){
window.location.href="/input/location"
}

else if(command.includes("manual") || command.includes("ಕೈಯಾರೆ") || command.includes("మాన్యువల్") || command.includes("मैनुअल")){
window.location.href="/input/manual"
}

else if(command.includes("image") || command.includes("ಚಿತ್ರ") || command.includes("చిత్రం") || command.includes("छवि")){
window.location.href="/input/image"
}

else{
alert("Command not understood")
}

}

}



function speakMessage(text,language){

let langCode="en-US"

if(language==="kn") langCode="kn-IN"
if(language==="te") langCode="te-IN"
if(language==="ta") langCode="ta-IN"
if(language==="hi") langCode="hi-IN"

const speech = new SpeechSynthesisUtterance(text)

speech.lang = langCode
speech.rate = 1
speech.pitch = 1

const voices = window.speechSynthesis.getVoices()

for(let i=0;i<voices.length;i++){

if(voices[i].lang === langCode){

speech.voice = voices[i]
break

}

}

window.speechSynthesis.speak(speech)

}
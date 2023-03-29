const speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SpeechGrammarList = window.SpeechGrammarList || window.webkitSpeechGrammarList;
const grammar = "#JSGF V1.0; grammar dictionnaire; public <dictionnaire> = wikipedia.fr | recherche | sommaire | section | je souhaite continuer | je souhaite arrêter | non | oui  ;"
let recognition = new speechRecognition();
const speechRecognitionList = new SpeechGrammarList();
speechRecognitionList.addFromString(grammar, 1);
recognition.grammars = speechRecognitionList;
recognition.interimResults = false;
recognition.continuous = true;
recognition.lang = 'fr-FR';
let reader
const launchBtn = document.querySelector('button');
let outputPred = document.querySelector('#outputPred');
let outputConfidence = document.querySelector('#outputConfidence');
let contentLecture = document.querySelector('#contentLecture');

let tabSpeech = [];
let global_prediction = "";

let dataToDjango = {
    "prediction": "",
};
let csrfToken = { 'csrfToken': "" }



const token = () => {
    fetch('/get_csrf_token')
        .then(response => response.json())
        .then(data => {
            csrfToken = data.csrfToken;
            // Utiliser le token CSRF dans les requêtes POST, PUT, PATCH ou DELETE
        })
        .catch(error => console.error('Erreur:', error));
};

token_recup = token()




function strUcFirst(a) {
    return (a + '').charAt(0).toUpperCase() + a.substr(1);
}

// Fonction de regex servant à récupérer la prédiction issue de getSpeechOnLive en ignorant le mot recherche encadrant la demande.
const getChoiceWithRegex = str => {
    const regex = /recherche\s+(.+)/i;
    const match = regex.exec(str);
    if (match && match[1]) {
        return match[1].trim();
    } else {
        return "Aucun thème trouvé";
    }
}


// Fonction servant à obtenir la prédiction issue de getSpeechOnLive. Nous récupérons le dernier indice d'un tableau nommé tabSpeech valorisé dans la fonction getSpeechOnLive. Un switch est utilisé en utilisant deux écouteurs d'événements, selon que le mot recherche ait ou non été dit dans la prédiction.
const getPredSpeech = evt => {
    // ajout 21/02:
    console.log("EVENT getPredSpeech")
    window.removeEventListener("tabSpeechResult", postDataToDjango);
    window.removeEventListener("tabSpeechResultWithRegex", postDataToDjango);
    let global_prediction = "";
    let retour;

    switch (evt.type) {
        case "tabSpeechResultWithRegex":
            global_prediction = retour = tabSpeech[tabSpeech.length - 1];
            break;
        case "tabSpeechResult":
            global_prediction = retour = tabSpeech[tabSpeech.length - 1];
            break;
        default:
            console.log("Event non reconnu")
            break;
    }

    dataToDjango = {
        "prediction": strUcFirst(global_prediction),
    };
    console.log("le json à envoyer est :", dataToDjango);
    window.dispatchEvent(new Event("ENVOI"));
}
/*---------- Gestion des choix vocaux vie Events dispatches -------------*/

// Fonction ouvrant et présentant l'application à l'utilisateur. Utilise des gestionnaires d'événéments et du text to speech
const openSpeech = () => {
    window.addEventListener('FIN_INTRO', getSpeechOnLive);
    window.addEventListener("tabSpeechResultWithRegex", getPredSpeech);
    window.addEventListener("tabSpeechResult", getPredSpeech);
    launchBtn.addEventListener('click', stopAndResetAudio);
    // ajout 21/02:
    window.addEventListener("ENVOI", postDataToDjango);

    let speech = new SpeechSynthesisUtterance();
    speech.lang = "fr";
    speech.text = "Vokalpedia, dites recherche aide ou prononcer votre demande.";
    console.log(speech.text);
    voices = window.speechSynthesis.getVoices();
    speech.voice = voices[0];
    speech.onend = () => {
        dispatchEvent(new Event('FIN_INTRO'));
    }
    window.speechSynthesis.speak(speech);

};

// Fonction de speech to text permettant d'écouteur la demande de l'utilisateur
const getSpeechOnLive = () => {

    window.removeEventListener("FIN_INTRO", getSpeechOnLive);

    let speech_buffer = "";

    recognition.start();
    recognition.onerror = function (event) {
        launchBtn.disabled = false;
        launchBtn.textContent = 'Commencer une nouvelle reconnaissance vocale';
        outputPred.textContent = 'Une erreur s\'est produite dans la reconnaissance vocale: ' + event.error;
    }

    recognition.onresult = function (event) {

        let speechResult = event.results[0][0].transcript.toLowerCase();
        outputPred.textContent = "Vous souhaitez consulter: " + strUcFirst(speechResult);
        tabSpeech.push(speechResult);
        outputConfidence.textContent = 'Notre taux de certitude quant à la compréhension de votre demande: ' + Math.round((event.results[0][0].confidence) * 100) + "%.";
        console.log(tabSpeech);
        console.log('Confidence: ' + event.results[0][0].confidence);
        console.log('speechResult : ', speechResult);

        speech_buffer += speechResult;
        if (speech_buffer.split(' ').find(e => e === "recherche")) {
            console.log("on stop la saisie");
            launchBtn.removeEventListener('click', getSpeechOnLive);
            recognition.stop();
            let speech = new SpeechSynthesisUtterance();
            speech.lang = "fr";
            speech.text = "Vous souhaitez consulter : " + speechResult.replaceAll("recherche", "");
            console.log(speech.text);
            voices = window.speechSynthesis.getVoices();
            ;
            window.speechSynthesis.speak(speech);
            speechResult = getChoiceWithRegex(speechResult);
            window.dispatchEvent(new Event("tabSpeechResultWithRegex"));

        } else {
            recognition.onerror;
            recognition.stop();
            let speech = new SpeechSynthesisUtterance();
            speech.lang = "fr";
            speech.text = "Vous avez dit :" + strUcFirst(speechResult);
            console.log(speech.text);
            voices = window.speechSynthesis.getVoices();
            speech.voice = voices[0];
            window.speechSynthesis.speak(speech);
            window.dispatchEvent(new Event("tabSpeechResult"));
        }

    }
    recognition.onspeechend = function () {
        console.log('speech end : ', speech_buffer);
        console.log('on stop le record');
        recognition.stop();
        console.log('Dialogue final : ', speech_buffer);
        if (speech_buffer.split(' ').find(e => e === "continu")) {
            console.log('On reprend la saisie vocale');
        }

    }

    recognition.onaudiostart = function (event) {
        //Fired when the user agent has started to capture audio.
        console.log('SpeechRecognition.onaudiostart');
    }

    recognition.onaudioend = function (event) {
        //Fired when the user agent has finished capturing audio.
        console.log('SpeechRecognition.onaudioend');
    }

    recognition.onend = function (event) {
        //Fired when the speech recognition service has disconnected.
        console.log('SpeechRecognition.onend');
    }

    recognition.onnomatch = function (event) {
        //Fired when the speech recognition service returns a final result with no significant recognition. This may involve some degree of recognition, which doesn't meet or exceed the confidence threshold.
        console.log('SpeechRecognition.onnomatch');
    }

    recognition.onsoundstart = function (event) {
        //Fired when any sound — recognisable speech or not — has been detected.
        console.log('SpeechRecognition.onsoundstart');
    }

    recognition.onsoundend = function (event) {
        //Fired when any sound — recognisable speech or not — has stopped being detected.
        console.log('SpeechRecognition.onsoundend');
    }

    recognition.onspeechstart = function (event) {
        //Fired when sound that is recognised by the speech recognition service as speech has been detected.
        console.log('SpeechRecognition.onspeechstart');
    }
    recognition.onstart = function (event) {
        //Fired when the speech recognition service has begun listening to incoming audio with intent to recognize grammars associated with the current SpeechRecognition.
        console.log('SpeechRecognition.onstart');
    }
};



const buttonTest = launchBtn.addEventListener('click', openSpeech);



// const postDataToDjango = (data, token_recup) => {
//     // ajout 22/02
//     // window.removeEventListener("ENVOI", getAudioFile);

//     data = dataToDjango;
//     console.log("data ici ", data)

//     fetch('/wikispeech/', {
//         method: 'POST',
//         credentials: 'include',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': csrfToken,
//         },
//         body: JSON.stringify(data),
//     })
//         .then(response => response.json())
//         .then(data => {
//             reader = document.getElementById('wikiReaderSound')
//             reader.src = data.fichier_son
//             reader.play()
//             console.log('Success reading file :', data);
//         })
//         .catch((error) => {
//             console.error('Error:', error);
//         });
// };




const postDataToDjango = (data, token_recup) => {

    data = dataToDjango;
    console.log("data ici ", data)

    fetch('/wikispeech/', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            let reader = document.getElementById('wikiReaderSound');
            let speech = new SpeechSynthesisUtterance();
            if (data.fichier_son && data.fichier_son.startsWith('/media')) {
                reader.src = data.fichier_son;
                reader.play();
                console.log('Success playing audio file:', data.fichier_son);
            } else {
                speech.text = data["lecture"];
                speech.lang = "fr";
                voices = window.speechSynthesis.getVoices();
                speech.voice = voices[0];
                window.speechSynthesis.speak(speech);
                contentLecture.textContent = data["lecture"];
                console.log('Success speaking text:', data["lecture"]);
            }
        })
        .catch(error => console.error('Error:', error));
};



window.addEventListener("DOMContentLoaded", () => {
    reader = document.getElementById('wikiReaderSound')
});



// // Gestion de la mise en pause / relance:
// const audio = document.querySelector('audio');
// let isPlaying = false;

// function toggleAudio() {
//     if (!isPlaying) {
//         audio.play();
//     } else {
//         audio.pause();
//     }
//     isPlaying = !isPlaying;
// }

// document.addEventListener('keydown', event => {
//     if (event.code === 'Space') {
//         toggleAudio();
//     }
// });


// const myButton = document.getElementById('boutton_lancement');

// // Ajouter un gestionnaire d'événement sur le clic du bouton
// myButton.addEventListener('click', function () {
//     // Retirer le focus du bouton
//     myButton.blur();
// });
const refreshButton = document.getElementById('refreshButton');

refreshButton.addEventListener('click', () => {
    location.reload(); // Rafraîchir la page
});


const stopButton = document.getElementById('stopButton');

stopButton.addEventListener('click', () => {
    stopAndResetAudio(); // Arrêter et réinitialiser l'audio
});



// Gestion de la mise en pause / relance:
const audio = document.querySelector('audio');
let isPlaying = false;

function toggleAudio() {
    if (!isPlaying) {
        audio.play();
        window.speechSynthesis.resume();
    } else {
        audio.pause();
        window.speechSynthesis.pause();
    }
    isPlaying = !isPlaying;
}

function resetAudio() {
    if (audio.src) {
        audio.currentTime = 0;
    }
    window.speechSynthesis.cancel();
    isPlaying = false;
}

function stopAndResetAudio() {
    audio.pause();
    audio.currentTime = 0;
    window.speechSynthesis.cancel();
    isPlaying = false;
}

document.addEventListener('keydown', event => {
    if (event.code === 'Space') {
        event.preventDefault(); // Empêcher le comportement par défaut de la touche "Espace"
        toggleAudio();
    }
    if (event.code === 'AltLeft' || event.code === 'AltRight') {
        event.preventDefault(); // Empêcher le comportement par défaut de la touche "Alt"
        resetAudio();
    }
    if (event.code === 'Escape') {
        event.preventDefault(); // Empêcher le comportement par défaut de la touche "Escape"
        stopAndResetAudio();
    }
});

const myButton = document.getElementById('launchButton');

// Ajouter un gestionnaire d'événement sur le clic du bouton
myButton.addEventListener('click', function () {
    // Retirer le focus du bouton
    myButton.blur();
});






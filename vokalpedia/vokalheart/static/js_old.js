const speechRecognition = window.webkitSpeechRecognition;
const SpeechGrammarList = window.webkitSpeechGrammarList;
const grammar = "#JSGF V1.0; grammar dictionnaire; public <dictionnaire> = wikipedia.fr | recherche | sommaire | section | je souhaite continuer | je souhaite arrêter | non | oui  ;"
let recognition = new speechRecognition();
const speechRecognitionList = new SpeechGrammarList();
speechRecognitionList.addFromString(grammar, 1);
recognition.grammars = speechRecognitionList;
recognition.interimResults = false;
recognition.continuous = true;
recognition.lang = 'fr-FR';

const launchBtn = document.querySelector('button');
let outputPred = document.querySelector('.outputPred');
let outputConfidence = document.querySelector('.outputConfidence');

let tabSpeech = [];
let global_prediction = "";
let demandeAccessoire = "" ;
let dataToDjango = { "prediction": "" ,
                     "predAccessoire": "",
                    };
let global_prediction_split;
let csrfToken = {'csrfToken': "" }


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
    // const regex = /recherche (.+)sommaire (.+)/m;
    const regex = /recherche (.+) /gm;
    let m;
    let resultat;
    while ((m = regex.exec(str)) !== null) {
        // This is necessary to avoid infinite loops with zero-width matches
        if (m.index === regex.lastIndex) {
            regex.lastIndex++;
        }
        // The result can be accessed through the `m`-variable.
        m.forEach((match, groupIndex) => {
            console.log(`Found match, group ${groupIndex}: ${match}`);
            resultat = m.length > 1 ? m[1] : "Aucun thème trouvé";
        });
        resultat = m.length > 1 ? m[1] : "Aucun thème trouvé";
    }
    return (resultat);
}


// Fonction servant à obtenir la prédiction issue de getSpeechOnLive. Nous récupérons le dernier indice d'un tableau nommé tabSpeech valorisé dans la fonction getSpeechOnLive. Un switch est utilisé en utilisant deux écouteurs d'événements, selon que le mot recherche ait ou non été dit dans la prédiction.
const getPredSpeech = evt => {
    // ajout 21/02:
    window.dispatchEvent(new Event("ENVOI"));
    window.removeEventListener("tabSpeechResult", postDataToDjango);
    window.removeEventListener("tabSpeechResultWithRegex", postDataToDjango);

    let retour;
    let accompagnement;
    switch (evt.type) {
        case "tabSpeechResultWithRegex":
            // global_prediction = retour = getChoiceWithRegex(tabSpeech[tabSpeech.length - 2]);
            global_prediction = retour = tabSpeech[tabSpeech.length - 2];
            demandeAccessoire = accompagnement = getChoiceWithRegex(tabSpeech[tabSpeech.length - 1]);
            break;
        case "tabSpeechResult":
            global_prediction = retour = tabSpeech[tabSpeech.length - 2];
            demandeAccessoire = accompagnement = tabSpeech[tabSpeech.length - 1];
            break;
        default:
            console.log("Event non reconnu")
            break;
    }
    global_prediction_split = global_prediction.split(" ");
    // console.log(global_prediction_split)
    // global_prediction_split = global_prediction_split.reverse();
    // console.log(global_prediction_split)
    // global_prediction_split = global_prediction_split.join(" ");
    // console.log(global_prediction_split)
    // console.log("élement du tableau: " ,global_prediction_split[1])
    dataToDjango = { 
        "prediction": strUcFirst(global_prediction_split[1]),
        // "predAccessoire": strUcFirst(demandeAccessoire),
        "predAccessoire": demandeAccessoire,  
    };
    console.log("La global_prediction est : ", global_prediction);
    console.log("La demandeAccessoire est : ", demandeAccessoire);
    console.log("Le retour est : ", retour);
    console.log("L'accompagnement est : ", accompagnement);
    console.log("le json à envoyer est :", dataToDjango);
}
/*---------- Gestion des choix vocaux vie Events dispatches -------------*/

// Fonction ouvrant et présentant l'application à l'utilisateur. Utilise des gestionnaires d'événéments et du text to speech
const openSpeech = () => {
    window.addEventListener('FIN_INTRO', getSpeechOnLive);
    window.addEventListener("tabSpeechResultWithRegex", getPredSpeech);
    window.addEventListener("tabSpeechResult", getPredSpeech);
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



const postDataToDjango = (data,token_recup) => {
    // ajout 22/02
    window.removeEventListener("ENVOI", getAudioFile);

    data = dataToDjango;

    fetch('/wikispeech/', {
      method: 'POST', 
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken, 
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Success:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
};


// Code pour récupérer le fichier wav : 
//Dans votre code JavaScript, utilisez la fonction fetch pour envoyer une requête GET à l'URL de votre vue Django qui retourne le fichier WAV. 
//Vous pouvez utiliser la méthode blob() pour récupérer le contenu de la réponse sous forme de blob 
// fetch('url/vers/vue/django/qui/retourne/le/fichier/wav')
const getAudioFile = () => {

    fetch('/home/fichier_wav/')
    .then(response => response.blob())
    .then(blob => {
        // faire quelque chose avec le blob
    });

};


// Une fois que vous avez récupéré le blob du fichier WAV, vous pouvez le traiter comme vous le souhaitez dans votre code JavaScript. 
// Par exemple, vous pouvez l'utiliser pour créer un élément audio dans votre page HTML 
// const audioElement = document.createElement('audio');
// audioElement.src = URL.createObjectURL(blob);
// document.body.appendChild(audioElement);


// Pour créer un lecteur audio en JavaScript qui permet de lire ou arrêter la lecture du fichier audio, vous pouvez utiliser l'API Web Audio de HTML5. Voici un exemple de code qui vous permettra de créer un lecteur audio simple :
// Récupération de l'élément audio de la page
const audioElement = document.getElementById('audio');

// Création du contexte audio
const audioContext = new AudioContext();

// Déclaration des nœuds audio
const source = audioContext.createMediaElementSource(audioElement);
const gainNode = audioContext.createGain();
const analyser = audioContext.createAnalyser();

// Connexion des nœuds audio
source.connect(gainNode);
gainNode.connect(analyser);
analyser.connect(audioContext.destination);

// Définition des paramètres audio
gainNode.gain.value = 1;

// Fonction pour démarrer la lecture audio
function playAudio() {
    audioElement.play();
}

// Fonction pour arrêter la lecture audio
function stopAudio() {
    audioElement.pause();
    audioElement.currentTime = 0;
}

// Exemple d'utilisation
playAudio();
setTimeout(stopAudio, 5000); // Arrêter la lecture après 5 secondes


// <audio controls>
//     <source src="{{ fichier_wav }}" type="audio/wav"> */}
// </audio>
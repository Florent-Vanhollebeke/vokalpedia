const speechRecognition = window.webkitSpeechRecognition;
const SpeechGrammarList = window.webkitSpeechGrammarList;
const grammar = "#JSGF V1.0; grammar dictionnaire; public <dictionnaire> =  recherche | sommaire | section | lecture | aide ;"

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
let demandeAccessoire = "";
let dataToDjango = {
  "prediction": "",
  "predAccessoire": "",
};
let global_prediction_split;
let csrfToken = { 'csrfToken': "" }

const token = () => {
  return new Promise((resolve, reject) => {
    fetch('/get_csrf_token')
      .then(response => response.json())
      .then(data => {
        csrfToken = data.csrfToken;
        resolve(csrfToken);
      })
      .catch(error => reject(error));
  });
};

const getChoiceWithRegex = str => {
  const regex = /recherche (.+) /gm;
  let m;
  let resultat;
  while ((m = regex.exec(str)) !== null) {
    if (m.index === regex.lastIndex) {
      regex.lastIndex++;
    }
    m.forEach((match, groupIndex) => {
      console.log(`Found match, group ${groupIndex}: ${match}`);
      resultat = m.length > 1 ? m[1] : "Aucun thème trouvé";
    });
    resultat = m.length > 1 ? m[1] : "Aucun thème trouvé";
  }
  return resultat;
}


const getPredSpeech = (evt) => {
    return new Promise((resolve, reject) => {
        let retour;
        let accompagnement;
        switch (evt.type) {
            case "tabSpeechResultWithRegex":
                global_prediction = retour = getChoiceWithRegex(tabSpeech[tabSpeech.length - 2]);
                demandeAccessoire = accompagnement = getChoiceWithRegex(tabSpeech[tabSpeech.length - 1]);
                break;
            case "tabSpeechResult":
                global_prediction = retour = tabSpeech[tabSpeech.length - 2];
                demandeAccessoire = accompagnement = tabSpeech[tabSpeech.length - 1];
                break;
            default:
                reject(new Error("Event non reconnu"));
                break;
        }
        global_prediction_split = global_prediction.split(" ");
        dataToDjango = { 
            "prediction": strUcFirst(global_prediction_split[1]),
            "predAccessoire": demandeAccessoire,  
        };
        resolve(dataToDjango);
    });
};


// Fonction ouvrant et présentant l'application à l'utilisateur. Utilise des gestionnaires d'événéments et du text to speech
const openSpeech = () => {
    return new Promise((resolve, reject) => {
        let speech = new SpeechSynthesisUtterance();
        speech.lang = "fr";
        speech.text = "Vokalpedia, dites recherche aide ou prononcer votre demande.";
        console.log(speech.text);
        voices = window.speechSynthesis.getVoices();
        speech.voice = voices[0];
        speech.onend = () => {
            resolve();
        }
        window.speechSynthesis.speak(speech);
    });
};


const getSpeechOnLive = () => {

    window.removeEventListener("FIN_INTRO", getSpeechOnLive);
    let speech_buffer = "";
    let resolve, reject;
    const recognitionPromise = new Promise((res, rej) => {
        resolve = res;
        reject = rej;
    });

    recognition.start();

    recognition.onerror = function (event) {
        launchBtn.disabled = false;
        launchBtn.textContent = 'Commencer une nouvelle reconnaissance vocale';
        outputPred.textContent = 'Une erreur s\'est produite dans la reconnaissance vocale: ' + event.error;
        reject(event);
    };

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
            window.speechSynthesis.speak(speech);
            speechResult = getChoiceWithRegex(speechResult);
            window.dispatchEvent(new Event("tabSpeechResultWithRegex"));
            resolve(speechResult);
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
            resolve(speechResult);
        }
    };

    recognition.onspeechend = function () {
        console.log('speech end : ', speech_buffer);
        console.log('on stop le record');
        recognition.stop();
        console.log('Dialogue final : ', speech_buffer);

        if (speech_buffer.split(' ').find(e => e === "continu")) {
            console.log('On reprend la saisie vocale');
        }
    };
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

    recognitionPromise.catch((event) => {
        // Handle errors here
    });
return recognitionPromise;

const buttonTest = launchBtn.addEventListener('click', getSpeechOnLive);


async function speechFlow() {
    try {
    await openSpeech();
    await token();
    await getSpeechOnLive();
    await getPredSpeech({type: "tabSpeechResult"});
    console.log("dataToDjango:", dataToDjango);
    // use dataToDjango to make your fetch request here
    } catch (error) {
    console.log(error);
    }
    }


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





const getSpeechOnLive = () => {

    window.removeEventListener("FIN_INTRO", getSpeechOnLive);
    let speech_buffer = "";
    let resolve, reject;
    const recognitionPromise = new Promise((res, rej) => {
        resolve = res;
        reject = rej;
    });

    recognition.start();

    recognition.onerror = function (event) {
        launchBtn.disabled = false;
        launchBtn.textContent = 'Commencer une nouvelle reconnaissance vocale';
        outputPred.textContent = 'Une erreur s\'est produite dans la reconnaissance vocale: ' + event.error;
        reject(event);
    };

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
            window.speechSynthesis.speak(speech);
            speechResult = getChoiceWithRegex(speechResult);
            window.dispatchEvent(new Event("tabSpeechResultWithRegex"));
            resolve(speechResult);
        } else {
            // appel de la méthode reject pour signaler une erreur lors de la reconnaissance vocale
            reject(new Error("Recherche non détectée"));
        }
    };

    recognition.onend = function() {
        // appel de la méthode reject si la recherche n'a pas été détectée
        reject(new Error("Recherche non détectée"));
    };
    
    return recognitionPromise;
};


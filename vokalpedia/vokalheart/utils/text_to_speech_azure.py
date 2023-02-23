import azure.cognitiveservices.speech as speechsdk
import datetime


speech_key=""
service_region="francecentral"

def speech_synthesis_with_auto_language_detection_to_speaker(text,search):
    """performs speech synthesis to the default speaker with auto language detection
       Note: this is a preview feature, which might be updated in future versions."""

    now = datetime.datetime.today()
    timestamp = datetime.datetime.timestamp(now)

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # create the auto detection language configuration without specific languages
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig()

    # Creates a speech synthesizer using the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config,audio_config=None)

    result = speech_synthesizer.speak_text_async(text).get()
        # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to speaker for text [{}]".format(text))
            stream = speechsdk.AudioDataStream(result)
            stream.save_to_wav_file(f"{search}_{timestamp}.wav")
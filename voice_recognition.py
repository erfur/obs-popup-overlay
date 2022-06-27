import speech_recognition as sr
import time
from queue import Queue
from threading import Thread
from loguru import logger
import requests

class VoiceRecognition:
    def __init__(self, mic_name, grammar=None):
        self.recognizer = sr.Recognizer()
        self.audio_queue = Queue()
        self.grammar = grammar

        if (mic_idx := sr.Microphone.list_microphone_names().index(mic_name)) == -1:
            logger.error('cant find mic: %s' % mic_name)

        self.microphone = sr.Microphone(device_index=mic_idx)
        self.calibrate()
        self.init_model()

    def calibrate(self):
        with self.microphone as source:
            logger.info('calibrate for the ambient noise...')
            # we only need to calibrate once, before we start listening
            self.recognizer.adjust_for_ambient_noise(source)  

    def init_model(self):
        logger.info('initialize vosk models...')
        with self.microphone as source:
            self.recognizer.recognize_vosk(self.recognizer.record(self.microphone, 0.1))

    def recognize_worker(self):
        # this runs in a background thread
        while True:
            audio = self.audio_queue.get()  # retrieve the next audio processing job from the main thread
            if audio is None: break  # stop processing if the main thread is done

            try:
                result = self.recognizer.recognize_vosk(audio, grammar=self.grammar)
                logger.info("Vosk thinks you said " + result)

                if 'archlinux' in result:
                    requests.get('http://localhost:5000/trigger')
                
            except sr.UnknownValueError:
                logger.error("Vosk could not understand audio")
            except sr.RequestError as e:
                logger.error("Vosk error; {0}".format(e))

            self.audio_queue.task_done()  # mark the audio processing job as completed in the queue

    def run(self):
        # start a new thread to recognize audio, while this thread focuses on listening
        recognize_thread = Thread(target=self.recognize_worker)
        recognize_thread.daemon = True
        recognize_thread.start()

        logger.info('start listening...')
        with self.microphone as source:
            try:
                while True:  
                    # repeatedly listen for phrases and put the resulting 
                    # audio on the audio processing job queue
                    self.audio_queue.put(self.recognizer.listen(source))
            except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
                pass

        self.audio_queue.join()  # block until all current audio processing jobs are done
        self.audio_queue.put(None)  # tell the recognize_thread to stop
        recognize_thread.join()  # wait for the recognize_thread to actually stop

if __name__ == '__main__':
    VoiceRecognition('Microphone (NVIDIA Broadcast)', grammar="[\"archlinux\", \"[unk]\"]").run()
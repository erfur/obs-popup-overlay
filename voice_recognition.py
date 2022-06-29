import speech_recognition as sr
import time
from queue import Queue
from threading import Thread
from loguru import logger
import json
import requests
from collections import deque
from math import ceil
import audioop

class VoiceRecognition:
    def __init__(self, mic_name, grammar=None, callback=None):
        self.recognizer = sr.Recognizer()
        self.audio_queue = Queue()
        self.grammar = grammar
        self.callback = callback
        # logger.info('grammar: %s' % grammar)

        if (mic_idx := sr.Microphone.list_microphone_names().index(mic_name)) == -1:
            logger.error('cant find mic: %s' % mic_name)

        self.microphone = sr.Microphone(device_index=mic_idx, sample_rate=16000)
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
                result = self.recognizer.recognize_vosk(audio, grammar=json.dumps(self.grammar))
                logger.info("Vosk thinks you said " + result)

                if [i for i in self.grammar[:-1] if i in json.loads(result)['text'].split()]:
                    logger.info('Hotword found, triggering the action...')
                    self.resampled_frames.clear()
                    self.audio_queue.empty()
                    try:
                        self.callback()
                    except Exception as e:
                        logger.error('Error while triggering the action: %s' % e)
                
            except sr.UnknownValueError:
                logger.error("Vosk could not understand audio")
            except sr.RequestError as e:
                logger.error("Vosk error; {0}".format(e))

            self.audio_queue.task_done()  # mark the audio processing job as completed in the queue

    def catch_hotword(self, source, timeout=None):
        elapsed_time = 0
        seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE

        # buffers capable of holding 5 seconds of original audio
        five_seconds_buffer_count = int(ceil(6 / seconds_per_buffer))
        # buffers capable of holding 0.5 seconds of resampled audio
        second_buffer_count = int(ceil(2 / seconds_per_buffer))

        frames = deque(maxlen=five_seconds_buffer_count)
        self.resampled_frames = deque(maxlen=second_buffer_count)
        
        check_interval = 0.5
        last_check = time.time()

        while True:
            elapsed_time += seconds_per_buffer
            if timeout and elapsed_time > timeout:
                raise TimeoutError("listening timed out while waiting for hotword to be said")

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break  # reached end of the stream
            frames.append(buffer)

            # resample audio to the required sample rate
            resampled_buffer, resampling_state = audioop.ratecv(buffer, source.SAMPLE_WIDTH, 1, source.SAMPLE_RATE, 16000, None)
            self.resampled_frames.append(resampled_buffer)
            if time.time() - last_check > check_interval:
                audio = sr.AudioData(b''.join(self.resampled_frames), 16000, source.SAMPLE_WIDTH)
                self.audio_queue.put(audio)
                # resampled_frames.clear()
                last_check = time.time()

    def run(self, callback=None):
        if callback:
            self.callback = callback

        # start a new thread to recognize audio, while this thread focuses on listening
        recognize_thread = Thread(target=self.recognize_worker)
        recognize_thread.daemon = True
        recognize_thread.start()

        logger.info('start listening...')
        with self.microphone as source:
            try:
                self.catch_hotword(source)
            except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
                pass

        self.audio_queue.join()  # block until all current audio processing jobs are done
        self.audio_queue.put(None)  # tell the recognize_thread to stop
        recognize_thread.join()  # wait for the recognize_thread to actually stop

if __name__ == '__main__':
    logger.info("starting main...")
    VoiceRecognition('Microphone (NVIDIA Broadcast)',
        grammar=json.dumps(['archlinux', '[unk]']),
        callback=lambda: requests.get('http://localhost:5000/trigger')
        ).run()
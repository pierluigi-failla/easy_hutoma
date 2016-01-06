import logging
import pyaudio
import wave

from sys import byteorder
from array import array
from struct import pack


class PlayAudio(object):
    """ A class for play wav files
    """

    def __init__(self, chunk_size=1024):
        self._chunk_size = chunk_size

    def play_wav_file(self, path):
        """ Play a wav file
        """
        logging.info('Preparing to play: {0}'.format(path))
        wave_file = wave.open(path, 'rb')
        py_audio = pyaudio.PyAudio()
        stream = py_audio.open(
                format=py_audio.get_format_from_width(wave_file.getsampwidth()),
                channels=wave_file.getnchannels(),
                rate=wave_file.getframerate(),
                output=True
        )
        # play the file
        data = wave_file.readframes(self._chunk_size)
        while data != '':
            stream.write(data)
            data = wave_file.readframes(self._chunk_size)
        # close stream and py_audio
        stream.close()
        py_audio.terminate()
        logging.info('Done')


class RecordAudio(object):
    """ A class for recording wav audio files
    """

    def __init__(self, threshold=500, chunk_size=1024, format=pyaudio.paInt16, rate=44100):
        self._threshold = threshold
        self._chunk_size = chunk_size
        self._format = format
        self._rate = rate

    def _is_silent(self, snd_data):
        """ Returns 'True' if below the 'silent' threshold
        """
        return max(snd_data) < self._threshold

    def _normalize(self, snd_data):
        """ Average the volume out
        """
        MAXIMUM = 16384
        times = float(MAXIMUM) / max(abs(i) for i in snd_data)

        r = array('h')
        for i in snd_data:
            r.append(int(i * times))
        return r

    def _trim(self, snd_data):
        """ Trim the blank spots at the start and end
        """

        def _trim(snd_data):
            snd_started = False
            r = array('h')

            for i in snd_data:
                if not snd_started and abs(i) > self._threshold:
                    snd_started = True
                    r.append(i)

                elif snd_started:
                    r.append(i)
            return r

        # Trim to the left
        snd_data = _trim(snd_data)

        # Trim to the right
        snd_data.reverse()
        snd_data = _trim(snd_data)
        snd_data.reverse()
        return snd_data

    def _add_silence(self, snd_data, seconds):
        """ Add silence to the start and end of 'snd_data' of length 'seconds' (float)
        """
        r = array('h', [0 for i in xrange(int(seconds * self._rate))])
        r.extend(snd_data)
        r.extend([0 for i in xrange(int(seconds * self._rate))])
        return r

    def record(self):
        """
        Record a word or words from the microphone and
        return the data as an array of signed shorts.

        Normalizes the audio, trims silence from the
        start and end, and pads with 0.5 seconds of
        blank sound to make sure VLC et al can play
        it without getting chopped off.
        """
        py_audio = pyaudio.PyAudio()
        stream = py_audio.open(format=self._format,
                               channels=1,
                               rate=self._rate,
                               input=True,
                               output=True,
                               frames_per_buffer=self._chunk_size)

        num_silent = 0
        snd_started = False

        r = array('h')

        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(self._chunk_size))
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            silent = self._is_silent(snd_data)

            if silent and snd_started:
                num_silent += 1
            elif not silent and not snd_started:
                snd_started = True

            if snd_started and num_silent > 30:
                break

        sample_width = py_audio.get_sample_size(self._format)
        stream.stop_stream()
        stream.close()
        py_audio.terminate()

        r = self._normalize(r)
        r = self._trim(r)
        r = self._add_silence(r, 0.5)
        return sample_width, r

    def record_to_file(self, path):
        """ Records from the microphone and outputs the resulting data to 'path'
        """
        logging.info('Recording to: {0}'.format(path))
        sample_width, data = self.record()
        data = pack('<' + ('h' * len(data)), *data)

        wave_file = wave.open(path, 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(sample_width)
        wave_file.setframerate(self._rate)
        wave_file.writeframes(data)
        wave_file.close()
        logging.info('Done')

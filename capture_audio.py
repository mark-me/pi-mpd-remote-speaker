import pyaudio
import numpy as np
import struct

class AudioSpectrometer(object):
    def __init__(self, block_time=0.005, sound_rate=10000):
        self.pa = pyaudio.PyAudio()
        self.sound_rate = sound_rate
        self.frames_per_block = int(sound_rate * block_time)
        self.stream = self.open_sound_stream()

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None
        for i in range( self.pa.get_device_count() ):
            device_info = self.pa.get_device_info_by_index(i)
            if device_info['name'].lower() == 'default':
                device_index = i
                return device_index
        if device_index == None:
            print('No preferred input found; using default input device.')
        return device_index

    def open_sound_stream(self):
        device_index = self.find_input_device()
        stream = self.pa.open(format = pyaudio.paInt16,
                              channels = 1,
                              rate = self.sound_rate,
                              input = True,
                              input_device_index = device_index,
                              frames_per_buffer = self.frames_per_block)
        return stream

    def get_rms(self, block):
        return np.sqrt(np.mean(np.square(block)))

    def listen(self):
        amplitude=0
        try:
            raw_block = self.stream.read(self.frames_per_block, exception_on_overflow = False)
            format = '%dh' % (len(raw_block) / 2)
            snd_block = np.array(struct.unpack(format, raw_block))
            amplitude = self.get_rms(snd_block)
        except Exception as e:
            print('Error recording: {}'.format(e))
        return amplitude

if __name__ == '__main__':

    audio = AudioSpectrometer()

    running = True
    while running:
        amplitude = audio.listen()
        print(amplitude)
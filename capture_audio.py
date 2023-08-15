import pyaudio
import numpy as np
import struct

import pygame

INPUT_SOUND_RATE = 10000 #44100
INPUT_BLOCK_TIME = 0.005 # 30 ms
INPUT_FRAMES_PER_BLOCK = int(INPUT_SOUND_RATE * INPUT_BLOCK_TIME)
INPUT_DEVICE_INDEX = 6

class AudioSpectrometer(object):
    def __init__(self):
        self.idx_input_device = INPUT_DEVICE_INDEX
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_sound_stream()

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None
        for i in range( self.pa.get_device_count() ):
            devinfo = self.pa.get_device_info_by_index(i)
            print('Device %{}: %{}'.format(i, devinfo['name']))

            for keyword in ['mic','input']:
                if keyword in devinfo['name'].lower():
                    print('Found an input: device {} - {}'.format(i, devinfo['name']))
                    device_index = i
                    return device_index

        if device_index == None:
            print('No preferred input found; using default input device.')

        return device_index

    def open_sound_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(  format = pyaudio.paInt16,
                                channels = 1,
                                rate = INPUT_SOUND_RATE,
                                input = True,
                                input_device_index = self.idx_input_device,
                                frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def get_rms(self, block):
        return np.sqrt(np.mean(np.square(block)))

    def listen(self):
        amplitude=0
        try:
            raw_block = self.stream.read(INPUT_FRAMES_PER_BLOCK, exception_on_overflow = False)
            format = '%dh' % (len(raw_block) / 2)
            snd_block = np.array(struct.unpack(format, raw_block))
            amplitude = self.get_rms(snd_block)
        except Exception as e:
            print('Error recording: {}'.format(e))
        return amplitude

if __name__ == '__main__':
    pygame.init()
    audio = AudioSpectrometer()
    screen = pygame.display.set_mode([800, 480])
    image = pygame.image.load('background.png')

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        amplitude = audio.listen()

        screen.fill((255, 255, 255))
        #print(amplitude / 1000)
        x_size = 800 + amplitude / 700
        y_size = 480 + amplitude / 700
        x_pos = y_pos = - (amplitude / 1000)/2

        scaled_image = pygame.transform.smoothscale(image, (x_size, y_size))
        screen.blit(scaled_image, (x_pos, x_pos))
        # pygame.draw.circle(screen, (0, 0, 255), (amplitude/100, amplitude/100), amplitude/100)
        pygame.display.flip()
    pygame.quit()
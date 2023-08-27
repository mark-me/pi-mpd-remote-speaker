import pyaudio
import numpy as np
import struct

import pygame

class AudioSpectrometer(object):
    def __init__(self, idx_input_device, block_time=0.005, sound_rate=10000):
        self.idx_input_device = idx_input_device
        self.pa = pyaudio.PyAudio()
        self.sound_rate = sound_rate
        self.frames_per_block = int(sound_rate * block_time)
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

    def open_sound_stream(self):
        device_index = self.find_input_device()

        stream = self.pa.open(format = pyaudio.paInt16,
                              channels = 1,
                              rate = self.sound_rate,
                              input = True,
                              input_device_index = self.idx_input_device,
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

    audio = AudioSpectrometer(idx_input_device=6)

    pygame.init()
    screen = pygame.display.set_mode([800, 480])
    surface_background = pygame.Surface((800, 480))
    image = pygame.image.load('background.png')
    surface_background.blit(image, (0, 0))
    surface_foreground = pygame.Surface((400,400))
    color = (255,255,0)
    surface_foreground.fill(color)
    screen.blit(surface_background, (0, 0))
    screen.blit(surface_foreground, (200, 40))

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
        x_pos = y_pos = - (amplitude / 700)/2

        #scaled_image = pygame.transform.smoothscale(image, (x_size, y_size))
        # surface_background.blit(scaled_image, (x_pos, x_pos))
        surface_background_scaled = pygame.transform.scale(surface_background, (x_size, y_size))
        screen.blit(surface_background_scaled, (x_pos, x_pos))
        screen.blit(surface_foreground, (200, 40))
        # pygame.draw.circle(screen, (0, 0, 255), (amplitude/100, amplitude/100), amplitude/100)
        pygame.display.flip()
    pygame.quit()

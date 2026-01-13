# src/audio/audio_player.py
import pygame

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()

    def play(self, file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def stop(self):
        pygame.mixer.music.stop()

    defVolumeSet(self, volume):
        pygame.mixer.music.set_volume(volume)


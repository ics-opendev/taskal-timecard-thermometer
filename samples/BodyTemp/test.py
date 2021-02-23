import os

os.environ["KIVY_AUDIO"] = "sdl2"

from kivy.core.audio import SoundLoader

sound = SoundLoader.load('kivy/sound/ok.wav')
if sound:
    print("Sound found at %s" % sound.source)
    print("Sound is %.3f seconds" % sound.length)
    sound.play()

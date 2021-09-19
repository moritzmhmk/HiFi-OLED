import os
import time
import threading
import logging
from typing import Dict

from PIL import Image

from ac2.plugins.metadata import MetadataDisplay

from luma.core.interface.serial import i2c, spi
from luma.oled.device import ssd1306, ssd1309
from luma.core.render import canvas

from . import trackinfo


class HiFiOLED(MetadataDisplay):

    def __init__(self, params: Dict[str, str] = {}):
        super().__init__()
        serial1 = spi(device=0, port=0)
        serial2 = i2c(port=1, address=0x3C)
        device1 = ssd1309(serial1)
        device2 = ssd1306(serial2, width=128, height=32)
        self.song_render_thread = SongRenderThread(device1)
        self.player_render_thread = PlayerRenderThread(device2)
        self.song_render_thread.start()
        self.player_render_thread.start()

    def notify(self, metadata):
        logging.info(
            f"{metadata.playerName} : {metadata.title} - {metadata.artist}")
        logging.info(
            f"{metadata.get_position()} / {metadata.duration} ({metadata.time})")
        self.song_render_thread.metadata = metadata
        self.player_render_thread.metadata = metadata

    def notify_volume(self, volume):
        logging.info(f"Volume changed to {volume}%")

    def __str__(self):
        return "oled"


class RenderThread(threading.Thread):
    def __init__(self, device):
        threading.Thread.__init__(self)
        self.device = device
        self._metadata = None
        self.last_update = 0

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        if value is None or self.metadata is None or value.title != self.metadata.title or value.artist != self.metadata.artist or value.playerName != self.metadata.playerName:
            self.last_update = time.time()
        self._metadata = value

    @metadata.deleter
    def metadata(self):
        del self._metadata

    def run(self):
        while True:
            self.render()

    def render(self):
        raise NotImplementedError


class SongRenderThread(RenderThread):
    def __init__(self, device):
        super().__init__(device)

    def render(self):
        m = self.metadata
        if m is None or (m.title is None and m.artist is None) or self.last_update < time.time() - 60 * 60:
            self.device.hide()
            time.sleep(5)
        else:
            self.device.show()
            title = getattr(m, "title", "-")
            artist = getattr(m, "artist", "-")
            time_total = 400
            time_current = round(m.get_position())
            tick = round((time.time() - self.last_update) * 10)
            with canvas(self.device) as draw:
                trackinfo.render(draw, title, artist,
                                 time_total, time_current, tick)
            time.sleep(0.1)


class PlayerRenderThread(RenderThread):
    def __init__(self, device):
        super().__init__(device)

    def render(self):
        if self.last_update < time.time() - 60 * 60:
            self.device.hide()
            time.sleep(5)
        else:
            self.device.show()
            image = self.getSourceImage()
            image = image.convert('1')
            self.device.display(image)
            time.sleep(1)

    def getSourceImage(self):
        if self.metadata is not None:
            playerName = getattr(self.metadata, "playerName", "")

        filename = "HiFiBerry.png"

        if playerName == "bluetooth":
            filename = "Bluetooth.png"
        if playerName == "upnp":
            filename = "DLNA.png"
        if playerName == "mpd":
            # see https://github.com/bang-olufsen/create/blob/1afe3d701cc1947b8225f45c03f674ff4aed1814/Beocreate2/beo-extensions/mpd/index.js#L261
            streamUrl = getattr(self.metadata, "streamUrl", "")
            if streamUrl.startswith("http"):
                filename = "Radio.png"
            else:
                filename = "Music.png"
        if playerName == "upmpdcli":
            filename = "OpenHome.png"
        if playerName == "raat":
            filename = "Roon.png"
        if playerName == "ShairportSync":
            filename = "AirPlay.png"
        if playerName == "snapcast":
            filename = "Snapcast.png"
        if playerName == "spotify":
            filename = "Spotify.png"
        if playerName == "lms":
            filename = "Squeezelite.png"
        pathToImage = os.path.join(
            os.path.dirname(__file__), 'images', filename)
        return Image.open(pathToImage, 'r')

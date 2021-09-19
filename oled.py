import time
import threading
import logging
from typing import Dict

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
        device2 = ssd1306(serial2)
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
        self._metadata = value
        self.last_update = time.time()

    @metadata.deleter
    def metadata(self):
        del self._metadata

    def run(self):
        while True:
            if self.metadata is None or self.last_update < time.time() - 60 * 60:
                self.device.hide()
                time.sleep(5)
            else:
                self.device.show()
                with canvas(self.device) as draw:
                    self.render(draw)
                time.sleep(0.1)

    def render(self, draw):
        raise NotImplementedError


class SongRenderThread(RenderThread):
    def __init__(self, device):
        super().__init__(device)

    def render(self, draw):
        title = self.metadata.title or "-"
        artist = self.metadata.artist or "-"
        time_total = 400
        time_current = round(self.metadata.get_position())
        tick = round((time.time() - self.last_update) * 10)
        trackinfo.render(draw, title, artist, time_total, time_current, tick)


class PlayerRenderThread(RenderThread):
    def __init__(self, device):
        super().__init__(device)

    def render(self, draw):
        playerName = self.metadata.playerName or "HifiBerry"
        draw.text((30, 40), playerName, fill="white")
        time.sleep(1)

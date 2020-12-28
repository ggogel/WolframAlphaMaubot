from typing import Type
import urllib.parse
from mautrix.types import RoomID, ImageInfo
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("appid")
        helper.copy("source")
        helper.copy("response_type")


class WolframAlphaPlugin(Plugin):
    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new("wolfram")
    @command.argument("search_term", pass_raw=True, required=True)
    async def handler(self, evt: MessageEvent, search_term: str) -> None:
        await evt.mark_read()

        appid = self.config["appid"]
        url_params = urllib.parse.urlencode({"i": search_term, "appid": appid})
        gif_link =  "https://api.wolframalpha.com/v1/simple?{}".format(url_params)
        resp = await self.http.get(gif_link)
        if resp.status == 501:
            await evt.reply("WolframAlpha doesn't understand your query")
            return None
        if resp.status != 200:
            self.log.warning(f"Unexpected status fetching image {gif_link}: {resp.status}")
            return None
        gif = await resp.read()

        filename = f"{search_term}.png" if len(search_term) > 0 else "wolfram.png"
        uri = await self.client.upload_media(gif, mime_type='image/png', filename=filename)

        await self.client.send_image(evt.room_id, url=uri, file_name=filename, info=ImageInfo(
                        mimetype='image/png'
                    ))

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from game.handlers import game_handler


class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lobby_group_name = None

    async def connect(self):

        user = self.scope['user']
        if user.is_authenticated:

            self.lobby_group_name = 'lobby_group'
            await self.channel_layer.group_add(
                self.lobby_group_name,
                self.channel_name
            )
            await self.accept()
        else:

            await self.close()

    async def disconnect(self, close_code):
        if self.lobby_group_name:

            await self.channel_layer.group_discard(
                self.lobby_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        event_type = data.get('type')

        if event_type.startswith('game'):

            await game_handler.route_event(self, data)

    async def send_message(self, event):
        exclude_channel = event.get('exclude_channel')
        if exclude_channel and exclude_channel == self.channel_name:

            return

        message_data = event['message_data']
        await self.send(text_data=json.dumps(message_data))

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from game.handlers import game_handler, globalchat_handler
from redis_utils.utils import get_async_redis_pool


class XiangqiConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for real-time  events.
    """
    def __init__(self, *args, **kwargs):
        """Initialize the consumer with the default settings."""
        super().__init__(*args, **kwargs)
        self.redis_conn = None
        self.chat_group_name = 'global_chat'
        self.room_group_name = None



    async def connect(self):
        """
        Accepts or rejects an incoming WebSocket connection.
        """
        user = self.scope['user']
        if user.is_authenticated:

            self.redis_conn = await get_async_redis_pool()
            await self.accept()
        else:

         await self.close()

    async def disconnect(self, close_code):
        """
        Removes the WebSocket connection from the group upon disconnection.
        """
        if self.chat_group_name:
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )

        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Processes messages received from the WebSocket.
        """
        data = json.loads(text_data)
        event_type = data.get('type')
        if event_type.startswith('game'):

            await game_handler.route_event(self, data)

        if event_type.startswith('chat'):

            await globalchat_handler.route_event(self, data)

    async def send_message(self, event):
        """
        Sends a message to the WebSocket, excluding certain channels if specified.
        """
        exclude_channel = event.get('exclude_channel', None)
        if exclude_channel and exclude_channel == self.channel_name:

            return
        message_data = event['message_data']
        await self.send(text_data=json.dumps(message_data))

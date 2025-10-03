import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as aioredis
from django.conf import settings
import asyncio

logger = logging.getLogger(__name__)

# RUN WITH VIRTUALENV
# REDIS_URL = 'redis://127.0.0.1:6379'

# RUN WITH DOCKER
REDIS_URL = 'redis://redis:6379'

# Throttling constants
RATE_LIMIT_COUNT = 5
RATE_LIMIT_WINDOW = 10  # seconds

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'

        # logging
        logger.info(f"WS connect user={self.scope.get('user')} conversation={self.conversation_id}")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # on connect, send recent messages from Redis
        redis = await aioredis.from_url(REDIS_URL)
        key = f'chat:{self.conversation_id}:messages'
        messages = await redis.lrange(key, 0, -1)
        # messages are stored as bytes; decode
        recent = [json.loads(m.decode()) for m in reversed(messages)]
        await self.send_json({'type': 'recent_messages', 'messages': recent})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"WS disconnect conversation={self.conversation_id} code={close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        logger.info(f"WS receive conversation={self.conversation_id} data={text_data}")
        try:
            data = json.loads(text_data)
            message = data.get('message')
            user = self.scope.get('user')
            if not message:
                await self.send_json({'error': 'Empty message'})
                return

            # rate limiting using Redis INCR with expiry
            redis = await aioredis.from_url(REDIS_URL)
            rate_key = f'rate:{user.id}:{self.conversation_id}'
            count = await redis.incr(rate_key)
            if count == 1:
                await redis.expire(rate_key, RATE_LIMIT_WINDOW)
            if count > RATE_LIMIT_COUNT:
                await self.send_json({'error': 'Rate limit exceeded'})
                return

            payload = {
                'user_id': user.id if user and user.is_authenticated else None,
                'username': user.username if user and user.is_authenticated else 'anonymous',
                'message': message,
            }

            # store in Redis list
            key = f'chat:{self.conversation_id}:messages'
            await redis.lpush(key, json.dumps(payload))
            # cap list length (keep last 100 messages)
            await redis.ltrim(key, 0, 99)

            # broadcast to group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.message',
                    'message': payload,
                }
            )
        except Exception as e:
            logger.exception('Error handling message')
            await self.send_json({'error': 'Internal server error'})

    async def chat_message(self, event):
        await self.send_json({'type': 'message', 'message': event['message']})

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))
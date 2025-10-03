import pytest
import asyncio
from django.urls import reverse
from django.test import Client
from channels.testing import WebsocketCommunicator
from realtimechat.asgi import application
from chat.models import User

@pytest.mark.django_db
def test_signup_unique_email():
    """Signup failed"""
    client = Client()

    User.objects.create_user(
        username="alejo",
        email="alejo@test.com",
        password="12345"
    )

    response = client.post(reverse("signup"), {
        "first_name": "Otro",
        "last_name": "Usuario",
        "username": "otro",
        "email": "alejo@test.com",
        "password": "54321"
    })

    assert response.status_code == 200
    assert b"is already" in response.content


def test_chat_websocket():
    async def inner():
        communicator = WebsocketCommunicator(application, "/ws/chat/1/")
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({"message": "hello"})
        response = await communicator.receive_json_from()

        assert any(m["message"] == "hello" for m in response["messages"])
        await communicator.disconnect()

    asyncio.run(inner())
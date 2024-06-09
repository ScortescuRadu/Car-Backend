from locust import HttpUser, task, between
import random
import string
import websockets
import asyncio
import json
import gevent
from gevent import monkey; monkey.patch_all()
from locust import events

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:8000"

    def on_start(self):
        # Get CSRF token
        response = self.client.get("/account/csrf/")
        if response.status_code == 200:
            self.csrf_token = response.json()['csrfToken']
        else:
            self.csrf_token = None

    @task
    def register(self):
        if self.csrf_token:
            email = f"{random_string()}@example.com"
            password = "TestPassword!123"
            self.client.post("/account/register", json={"email": email, "password": password}, headers={"X-CSRFToken": self.csrf_token})

    @task
    def login(self):
        if self.csrf_token:
            email = "radu31@email.com"
            password = "radu2radu?"
            self.client.post("/account/login", json={"email": email, "password": password}, headers={"X-CSRFToken": self.csrf_token})

    @task
    def get_user_info(self):
        if self.csrf_token:
            token_response = self.client.post("/account/login", json={"email": "radu31@email.com", "password": "radu2radu?"}, headers={"X-CSRFToken": self.csrf_token})
            if token_response.status_code == 200:
                token = token_response.json().get('token')
                self.client.post("/account/user", json={"token": token}, headers={"X-CSRFToken": self.csrf_token})

    @task
    def logout(self):
        if self.csrf_token:
            token_response = self.client.post("/account/login", json={"email": "radu31@email.com", "password": "radu2radu?"}, headers={"X-CSRFToken": self.csrf_token})
            if token_response.status_code == 200:
                token = token_response.json().get('token')
                self.client.post("/account/logout", json={"token": token}, headers={"X-CSRFToken": self.csrf_token})

class WebSocketUser(HttpUser):
    wait_time = between(1, 5)

    async def connect(self):
        self.websocket = await websockets.connect("ws://localhost:8000/ws/parking_lot_updates/")

    async def disconnect(self):
        await self.websocket.close()

    @task
    async def send_message(self):
        message = {
            "type": "frame_data",
            "camera_address": "camera_1",
            "destination_type": "entry",
            "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD/4QBiRXhpZgAATU0AKgAAAAgABwESAAMAAAABAAEAAAEaAAUAAAABAAAAYgEbAAUAAAABAAAAagEoAAMAAAABAAIAAAExAAIAAAAGAAAAbgEyAAIAAAAUAAAAYodpAAQAAAABAAAAcgAAAAAAAABIAAAAAQAAAEgAAAABAAKgAgAEAAAAAQAAACqgAwAEAAAAAQAAACAAAAAB/9sAQwADAgICAgMCAgIDAwMDBAYEBAQEBQcFBQQECAgICAgICAgICAgICAwMDAwMDAwMDBQQFBQUFBQUEBAQFBQUGBgYGBgcGBgYGBv/xAAaAAACAwEBAAAAAAAAAAAAAAAABQIDBAYB/8QAMxAAAQMDAQYEBwEAAAAAAAABAgMEBREABhIhMRMiQVFhcYEHMkKBkaGxFCNC8P/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwD8RqELtFRnAfbQ9r91G4kmMlnWwEXE3Tb66yfY0Wb25tOlz5RDLsAB5P2fvU4M11WsNlXVp0h7ThZVsASNgWv66nt4nT15M3WHEyjcXKoEItDSUqTQLKWVxuVXaz2DbvPceOxGvPTN7HhItItpqTwkhmZtLO5NmCdo68DjJPnVT6hxmhR+PhXKYztLEdSuwLWwJOt5/QD1O/uDvV8sM9yzTR2HcFJ0kFMUtEsNa4IwJQPLg6hWpW8kjYOPfvx5Hq2k5+zuFg3YixEbVwSz5RkMPCrxL5OB2ST5drZOSOfmloy2oOVjE5LuMNj9RUZlxZgsp0k9q5XAkTBMjqF8tlBG7AN3MWXq2guM8fFOsAdKwdrMD4wOQfY/rAOrq4K2gDAbDszxYAmAIySx4ACtBdA2CMtEjqA7DrX7z8vU8/9k="
        }
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        print(response)

    def on_start(self):
        self.ws_greenlet = gevent.spawn(self._connect_and_run)

    def on_stop(self):
        if self.ws_greenlet:
            self.ws_greenlet.kill()

    def _connect_and_run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect())
        while True:
            try:
                loop.run_until_complete(self.send_message())
            except Exception as e:
                print(f"Error: {e}")
            gevent.sleep(1)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    gevent.monkey.patch_all()

class MyTaskSet(HttpUser):
    tasks = [WebsiteUser, WebSocketUser]
    wait_time = between(1, 5)

    def __init__(self, *args, **kwargs):
        super(MyTaskSet, self).__init__(*args, **kwargs)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
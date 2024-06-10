from locust import HttpUser, task, between
import random
import string

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

from locust import User, task 
from app import get_current_user

class User_login(User):
    @task
    def simulate_login(self):
        get_current_user(User)
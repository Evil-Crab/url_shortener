from locust import HttpLocust, TaskSet, task
import random


class UserBehavior(TaskSet):
    @task(24)
    def shorten_correct(self):
        with self.client.post("/shorten_url",
                              json={"url": "http://captive.apple.com/" + str(random.randint(1, 10000000))},
                              catch_response=True,
                              name='shorten_correct') as response:
            if response.status_code in [200, 201]:
                response.success()

        self.client.post("/shorten_url", {"url": "http://captive.apple.com/" + str(random.randint(1, 10000000))})

    @task(1)
    def shorten_incorrect_url(self):
        with self.client.post("/shorten_url",
                              json={"url": "sdzfsdfsdfsdfsdfdsfs"},
                              catch_response=True,
                              name='shorten_incorrect_url') as response:
            if response.status_code == 400:
                response.success()

    @task(1)
    def shorten_incorrect_json(self):
        with self.client.post("/shorten_url",
                              json={"sfsdfs": "sdzfsdfsdfsdfsdfdsfs"},
                              catch_response=True,
                              name='shorten_incorrect_json') as response:
            if response.status_code == 400:
                response.success()

    @task(1)
    def shorten_corrupted_json(self):
        with self.client.post("/shorten_url",
                              "sdzfsdfsdfsdfsdfdsfs",
                              catch_response=True,
                              name='shorten_corrupted_json') as response:
            if response.status_code == 400:
                response.success()

    @task(3)
    def shorten_existing(self):
        with self.client.post("/shorten_url",
                              json={"url": "http://captive.apple.com/0"},
                              catch_response=True,
                              name='shorten_existing') as response:
            if response.status_code == 200:
                response.success()
        self.client.post("/shorten_url", {"url": "http://captive.apple.com/0"})

    @task(60)
    def get_shortened(self):
        with self.client.get("/766wFV8A",
                             catch_response=True,
                             name='get_shortened') as response:
            if response.is_redirect:
                response.success()

    @task(5)
    def get_missing_shortened(self):
        with self.client.get("/0",
                             catch_response=True,
                             name='get_missing_shortened') as response:
            if response.status_code == 404:
                response.success()

    @task(5)
    def get_malformed_shortened(self):
        with self.client.get("/8xQ0lu-u",
                             catch_response=True,
                             name='get_malformed_shortened') as response:
            if response.status_code == 404:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 50
    max_wait = 200

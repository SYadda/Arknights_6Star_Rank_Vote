from locust import HttpUser, task, between
import requests

class Test_NewCompare_SaveScore_User(HttpUser):
    @task
    def success_stream(self):
        # 请原谅我不是很会用这个框架
        wait_time = between(0.5, 2)
        res:requests.Response = self.client.post("/new_compare") # lst_name[a] + ' ' + lst_name[b] + ' ' + str(code_random)
        try:
            left_name, right_name, code = res.content.decode('utf-8').split(' ')
            self.client.post(f"/save_score", json={
            "win_name": left_name,
            "lose_name": right_name,
            "code": code
            })
        except:
            # 极高并发时，会出现res.status_code=0, res.content=None 
            print(res.status_code, res.content)

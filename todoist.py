import logging as log
import requests


class TODOIST:
    TOKEN = '19f0a1e5c139912f193a6011131b4be9c25e2146'
    URL = "https://api.todoist.com/rest/v2/tasks"
    TIMEOUT = 3

    def __init__(self):
        self.todo_list = None

    def query_todo_list(self):
        try:
            data = requests.get(
                TODOIST.URL,
                headers={'Authorization': f'Bearer {self.TOKEN}'},
                timeout=self.TIMEOUT
            )
            new_todo_list = data.json()
        except requests.ConnectionError as e:
            log.critical('Chyba pripojeni!')
            new_todo_list = [] 
        except Exception as e:
            log.critical(e)
            new_todo_list = [] 
        if new_todo_list != self.todo_list:
            self.todo_list = sorted(new_todo_list, key=TODOIST.__get_date)
            return True
        else:
            return False

    def close_task(self, task_id: str) -> bool:
        try:
            resp = requests.post(
                f'{TODOIST.URL}/{task_id}/close',
                headers={'Authorization': f'Bearer {self.TOKEN}'},
                timeout=self.TIMEOUT
            )
        except requests.ConnectionError as e:
            log.critical('Chyba pripojeni!')
            return False
        except Exception as e:
            log.critical(e)
            return False

        log.debug(f'Todoist resp: {resp.status_code}')
        return resp.status_code == 204

    # def heslo(self):
    #     for task in self.todo_list:
    #         if task['content'].lower() == 'heslo':
    #             return True
    #     else:
    #         return False

    @staticmethod
    def __get_date(task):
        try:
            return task['due']['date']
        except KeyError:
            return '' 


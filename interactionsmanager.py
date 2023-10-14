import json
import os
from filelock import FileLock

class InteractionsManager:
    @staticmethod
    def add_message(sender_name: str, content: str):
        data = {
            "agent_name": sender_name,
            "agent_message": content
        }

        lock = FileLock("interactions.json.lock")

        with lock:
            if os.path.exists("interactions.json"):
                with open("interactions.json", "r") as file:
                    existing_data = json.load(file)
                    existing_data.append(data)
            else:
                existing_data = [data]

            with open("interactions.json", "w") as file:
                json.dump(existing_data, file)
    
    @staticmethod
    def reset_interactions():
        lock = FileLock("interactions.json.lock")
        
        with lock:
            if os.path.exists("interactions.json"):
                os.remove("interactions.json")
                print("ATTENTION: Interactions File (i.e. interactions.json) is removed before the new workflow!")

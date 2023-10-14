
import json


def review_json(filepath):
    with open(filepath, "r") as tempfile:
        tempdata = json.load(tempfile)
    
    print(f'There are {len(tempdata)} items in the {filepath} file')
    print("*-*" * 40)

    for tempitem in tempdata:
        print(tempitem["agent_name"])
        print(tempitem["agent_message"])
        print("-"*40)
        foo = input("Press enter to proceed to next item")
        print("||" * 10)

review_json("new.json")
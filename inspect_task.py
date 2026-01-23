
import sys
import os
from flask import Flask
from app import create_app, db
from app.models.task import Task

app = create_app()

with app.app_context():
    task_id = 2
    task = Task.query.get(task_id)
    if not task:
        print(f"Task {task_id} not found")
        sys.exit(1)
    
    print(f"Task Status: {task.status}")
    print(f"Result Data Type: {type(task.result_data)}")
    
    import json
    try:
        # Try to serialize specifically to catch errors
        json_str = json.dumps(task.result_data)
        print("Serialization Successful")
        print(json_str[:500])  # Print first 500 chars
        
        # Check specifically for behavioral profile
        if 'behavioral_profile' in task.result_data:
            print("\nBehavioral Profile FOUND:")
            print(json.dumps(task.result_data['behavioral_profile'], indent=2))
        else:
            print("\nBehavioral Profile NOT FOUND in result data")
            
        # Check for cross platform
        if 'connected_accounts' in task.result_data:
             print("\nConnected Accounts FOUND:")
             print(json.dumps(task.result_data['connected_accounts'], indent=2))
             
    except Exception as e:
        print(f"Serialization Failed: {e}")
        # iterate keys to find the culprit
        if isinstance(task.result_data, dict):
            for k, v in task.result_data.items():
                try:
                    json.dumps(v)
                except:
                    print(f"Key '{k}' causes serialization error: {type(v)}")


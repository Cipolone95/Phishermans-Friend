import redis
import json

uuidArray = []

def read_redis_db(redis_db_path):
    with open(redis_db_path, 'rb') as file:
        lines = file.readlines()
        
        for i in range(len(lines)):
            if lines[i].strip() == b'set':
                key = lines[i + 1].decode('utf-8').strip()
                value = lines[i + 4].decode('utf-8').strip()
                
                #print("-" * 40)  # Separator for readability
                
                try:
                    uuid = ""
                    username = ""
                    password = ""
                    terminate = ""

                    data = json.loads(value)  # Attempt to parse the value as JSON
                    uuid = data.get("UUID", "").strip()
                    username = data.get("Username", "").strip()
                    password = data.get("Password", "").strip()
                    terminate = data.get("Terminated", "")
                    
                    if username or password or terminate:
                        # print(f"UUID: {uuid}")
                        # print(f"Username: {username}")
                        # print(f"Password: {password}")
                        # print(f"Terminated: {terminate}")

                        uuidArray.append(uuid)
                except json.JSONDecodeError:
                    print(f"Error: value not json")  # Print raw value if not JSON
    return uuidArray




                

# Example usage
read_redis_db("control_plugin_data.db")
#print(uuidArray)

import requests
import json
import urllib3
import argparse

# GoPhish server URL
SERVER_URL = "https://localhost:3333"

# Prompt for API key
API_KEY = input("Enter your GoPhish API key: ")

# Function to make API requests
def make_request(endpoint, templateData):
    url = f"{SERVER_URL}{endpoint}"
    headers = {"Authorization": API_KEY}
    
    try:
        response = requests.post(url, headers=headers, json=templateData, verify=False)
        response.raise_for_status()

        return json.dumps(response.json(), indent=4)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def print_example_json_template():
    
    EXAMPLE_JSON = {
    "name": "Template Name",
    "subject": "Template Email Subject",
    "text": "Some Text",
    "html": "<html><body><h1>Some HTML</h1></body></html>"
    }

    print("This is an example template to use. Note: either the text field OR the html field are required.")
    print(json.dumps(EXAMPLE_JSON, indent=4))
    exit(0)

def load_json_data(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from '{file_path}'. Ensure it is properly formatted.")
        exit(1)


def main():

    parser = argparse.ArgumentParser(description="Submit template data to GoPhish API.")
    parser.add_argument("--input-file", help="Path to the JSON file containing template data.")
    parser.add_argument("--example", action="store_true", help="Print an example JSON structure and exit.")
    args = parser.parse_args()

    if args.example:
        print_example_json_template()

    #Suppress InsecureRequestWarnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


    # Validate inputs
    if not API_KEY or not SERVER_URL:
        print("API key and server URL are required.")
        exit(1)


    if args.input_file:
        payload = load_json_data(args.input_file)
    else:
        print("Please answer the following prompts. At least one text OR HTML field must be specified.\n")
        while True: 
            # Prompt user for template details
            template_name = input("Enter template name: ")
            template_subject = input("Enter email subject: ")
            template_text = input("Enter plain text content: ")
            template_html = input("Enter HTML content: ")

            if template_text == "" and template_html == "":
                print("Error: At least one text or HTML field must be specified.\n")
                continue
            else:
                break

        # Construct JSON payload
        payload = {
            "name": template_name,
            "subject": template_subject,
            "text": template_text,
            "html": template_html
        }


    # Sending template to GoPhish
    print("Sending template to server...")
    templates = make_request("/api/templates/", payload)


    if not templates:
        print("Failed to connect to GoPhish or send template. Check your API key and server URL.")
        exit(1)

    print("Template successfully deposited!")
    print(templates)



if __name__ == "__main__":
    main()








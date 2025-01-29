import requests
import json
import urllib3

#Suppress InsecureRequestWarnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Prompt for API key
API_KEY = input("Enter your GoPhish API key: ")

# GoPhish server URL
SERVER_URL = "https://localhost:3333"

# Validate inputs
if not API_KEY or not SERVER_URL:
    print("API key and server URL are required.")
    exit(1)

# Function to make API requests
def make_request(endpoint):
    url = f"{SERVER_URL}{endpoint}"
    headers = {"Authorization": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def create_customer_file(campaign_name):

    campaignFileResults = f'campaign_{campaign_name}_results.json'
    customerFileResults = f'Campaign_{campaign_name}_Customer_results.txt'

    #Printing Customer Results 
    with open(campaignFileResults, 'r') as f:
        data = json.load(f)

    # Extract results and filter by 'status'
    filtered_results = []

    for result in data['results']:
        if result['status'] in ['Clicked Link', 'Email Opened']:
            # Extract the desired fields
            extracted_data = {
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'status': result['status'],
                'send_date': result['send_date'],
                'modified_date': result['modified_date']
            }
            filtered_results.append(extracted_data)
    
    with open(customerFileResults, 'w') as f:
        for entry in filtered_results:
            # Writing the extracted fields in a readable format
            f.write(f"First Name: {entry['first_name']}\n")
            f.write(f"Last Name: {entry['last_name']}\n")
            f.write(f"Status: {entry['status']}\n")
            f.write(f"Send Date: {entry['send_date']}\n")
            f.write(f"Modified Date: {entry['modified_date']}\n")
            f.write("\n" + "-"*40 + "\n")  # Separator between entries
    
    print(f"Campaign customer results saved to {customerFileResults}.")

def create_campaign_files(campaign_name):

    # Save results to a file
    output_results_file = f"Campaign_{campaign_name}_results.json"
    with open(output_results_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Campaign results saved to {output_results_file}.")

    # Save campaign summary to a file
    output_summary_file = f"Campaign_{campaign_name}_summary.json"
    with open(output_summary_file, "w") as f:
        json.dump(summary, f, indent=4)

    print(f"Campaign summary saved to {output_summary_file}.")


# Fetch campaigns from GoPhish
print("Fetching campaigns...")
campaigns = make_request("/api/campaigns")

if not campaigns:
    print("Failed to connect to GoPhish or retrieve campaigns. Check your API key and server URL.")
    exit(1)

while True: 
    # Display campaign list
    print("\nAvailable Campaigns:")
    for campaign in campaigns:
        print(f"ID: {campaign['id']}, Name: {campaign['name']}")

    # Prompt for campaign ID
    campaign_id = input("Enter the ID of the campaign you want to export or type 'done': ")

    if campaign_id == "done":
        print("Done exporting campaigns. Goodbye!")
        break
    
    # Export campaign results
    print(f"Exporting results for campaign ID: {campaign_id}...")
    results = make_request(f"/api/campaigns/{campaign_id}/results")

    if not results:
        print("Failed to export campaign results. Ensure the campaign ID is correct.")
        continue


    # Export campaign summary
    print(f"Exporting summary for campaign ID: {campaign_id}...")
    summary = make_request(f"/api/campaigns/{campaign_id}/summary")

    if not summary:
        print("Failed to export campaign summary. Ensure the campaign ID is correct.")
        continue
    
    #Retrieving Campaign Name 
    campaign_name = results.get("name", f"campaign_{campaign_id}")
    campaign_name = campaign_name.replace(" ", "_")
    
    create_campaign_files(campaign_name)
    create_customer_file(campaign_name)








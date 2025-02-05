import requests
import json
from docx import Document
import urllib3
from datetime import datetime

#Suppress InsecureRequestWarnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


def generate_word_report(data, campaign_name):
    output_file = f"gophishReport_{campaign_name}.docx"
    doc = Document()
    heading = doc.add_heading(f"GoPhish Report for Campaign {campaign_name}", level=1)
    heading.alignment = 1
    table = doc.add_table(rows=1, cols=5)
    table.style = "Table Grid"
    
    headers = ["Email", "Opened", "Clicked", "Data Submitted", "Date Modified"]
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        hdr_cells[i].paragraphs[0].alignment = 1
    
    for record in data:
        email = record.get("email")
        if record.get("status") == "Submitted Data":
            opened = "✓"
            clicked = "✓"
            submitted_data = "✓"
        elif record.get("status") == "Clicked Link":
            opened = "✓"
            clicked = "✓"
            submitted_data = "✘"
        else:
            opened = "✓"
            clicked = "✘"
            submitted_data = "✘" 
        modDate = str(datetime.strptime(record.get("modified_date")[:19], "%Y-%m-%dT%H:%M:%S"))

        row_cells = table.add_row().cells
        row_cells[0].text = email
        row_cells[1].text = opened
        row_cells[2].text = clicked
        row_cells[3].text = submitted_data
        row_cells[4].text = modDate
    
        for cell in row_cells:
            cell.paragraphs[0].alignment = 1
    
    doc.save(output_file)
    print(f"Report saved to {output_file}")

if __name__ == "__main__":

    # Prompt for API key
    API_KEY = input("Enter your GoPhish API key: ")

    # GoPhish server URL
    SERVER_URL = "https://localhost:3333"

    # Validate inputs
    if not API_KEY or not SERVER_URL:
        print("API key and server URL are required.")
        exit(1)


    campaigns = make_request("/api/campaigns")

    while True: 
        # Display campaign list
        print("\nAvailable Campaigns:")
        for campaign in campaigns:
            print(f"ID: {campaign['id']}, Name: {campaign['name']}")

        # Prompt for campaign ID
        campaign_id = input("Enter the ID of the campaign you want to export or type 'done': ")

        if campaign_id == "done":
            print("Done generating reports. Goodbye!")
            break
        
        # Export campaign results
        print(f"Exporting results and generating report for campaign ID: {campaign_id}...")
        results = make_request(f"/api/campaigns/{campaign_id}/results")


        if not results:
            print("Failed to export campaign results. Ensure the campaign ID is correct.")
            continue

        #Retrieving Campaign Name 
        campaign_name = results.get("name", f"campaign_{campaign_id}")
        campaign_name = campaign_name.replace(" ", "_")

        filtered_results = []
        for result in results['results']:
            if result['status'] in ['Clicked Link', 'Email Opened', 'Submitted Data']:
                # Extract the desired fields
                extracted_data = {
                    'email': result['email'],
                    'status': result['status'],
                    'send_date': result['send_date'],
                    'modified_date': result['modified_date']
                }
                filtered_results.append(extracted_data)
        
        generate_word_report(filtered_results, campaign_name)

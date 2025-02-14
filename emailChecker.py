import subprocess
import smtplib
import time
import random
import argparse
import sys

# Function to extract domain from email
def extract_domain(email):
    try:
        return email.split('@')[1].strip()
    except IndexError:
        return None

# Function to get MX records for a domain
def get_mx_records(domain):
    try:
        result = subprocess.run(["dig", "+short", "MX", domain], capture_output=True, text=True)
        return result.stdout.strip().split('\n')
    except Exception as e:
        print(f"Error: {e}")

# Function to verify email using SMTP
def verify_email(email, mail_server):
    try:
        server = smtplib.SMTP(mail_server, 25, timeout=10)  # Port 25 (Change if needed)
        server.set_debuglevel(0)  # Set to 1 for debugging
        server.helo()
        server.mail("test@example.com")  # Use a real sender email if needed
        code, message = server.rcpt(email)  # Verify recipient email
        server.quit()
        return code
    except Exception as e:
        print(f"⚠ Error connecting to {mail_server}: {e}")
        return None

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Check if emails are valid using MX lookup and SMTP verification.")
parser.add_argument("--file", required=True, help="Path to the file containing email addresses.")
args = parser.parse_args()

# Read emails from file
try:
    with open(args.file, "r") as file:
        emails = [line.strip() for line in file.readlines()]
except FileNotFoundError:
    print(f"❌ Error: The file '{args.file}' was not found.")
    sys.exit(1)

# Output files
VALID_OUTPUT = "valid_emails.txt"
INVALID_OUTPUT = "invalid_emails.txt"

# Open output files
with open(VALID_OUTPUT, "w") as valid_file, open(INVALID_OUTPUT, "w") as invalid_file:
    for email in emails:
        domain = extract_domain(email)
        if not domain:
            continue  # Skip invalid lines

        mx_records = get_mx_records(domain)
        if not mx_records:
            print(f"❌ No MX records found for {email}")
            invalid_file.write(email + "\n")
            continue

        # Try verifying with the first MX server
        mx_record = mx_records[0]
        smtpServer = mx_record.split(" ", 1)[1].rstrip(".")
        #print(f"🔍 Checking {email} on {smtpServer}...")

        response_code = verify_email(email, smtpServer)
        if response_code == 250:
            print(f"✅ Valid: {email}")
            valid_file.write(email + "\n")
        elif response_code == 550:
            print(f"❌ Invalid: {email}")
            invalid_file.write(email + "\n")
        else:
            print(f"⚠ Unknown response for {email}: {response_code}")

        # Add a random delay (4-6 minutes) before the next request
        delay = random.uniform(240, 360)  # 240-360 seconds
        time.sleep(delay)

print("✅ Email validation complete. Check valid_emails.txt and invalid_emails.txt.")



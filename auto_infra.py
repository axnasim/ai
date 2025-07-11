import sys
import os
import subprocess
import json
from dotenv import load_dotenv
import requests  # Use requests for DeepSeek API calls

print("Starting `auto_infra.py`...")
print("Current working directory:", os.getcwd())

# Hardcoded path to the config file
CONFIG_FILE_PATH = "config.json"  # You can change this to the full path if needed

# =========================
# Function: Perform sanity checks
def sanity_checks():
    print("Running sanity checks...")

    # Check if Terraform is installed
    try:
        subprocess.run(['terraform', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Terraform is installed.")
    except subprocess.CalledProcessError as e:
        raise EnvironmentError(f"Terraform is installed but the command failed: {e.stderr.decode()}")
    except FileNotFoundError:
        raise EnvironmentError("Terraform is not installed or not found in the PATH.")

    # Check for DeepSeek API key presence and validity
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key is None:
        raise ValueError("The DEEPSEEK_API_KEY is not set in the environment.")
    if not deepseek_key.strip():
        raise ValueError("The DEEPSEEK_API_KEY in `.env` or GitHub Actions secret is empty.")
    if not deepseek_key.startswith('sk-'):
        raise ValueError("The DEEPSEEK_API_KEY is not in the correct format.")
    print("API key present and valid.")

    print("All sanity checks passed!")

# Function: Generate Terraform code using DeepSeek
def generate_terraform_with_deepseek(command):
    print("Calling DeepSeek to generate Terraform code...")
    prompt = (
        "You are an AI that generates Terraform code based on high-level commands.\n"
        "Given the following command, generate a valid Terraform configuration file:\n"
        f"{command}\n"
        "Respond with only the Terraform code, no explanations."
    )
    try:
        # Make a POST request to DeepSeek's API
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("DEEPSEEK_API_KEY")}'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {"role": "system", "content": "You generate Terraform code from high-level commands."},
                    {"role": "user", "content": prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 600,
            }
        )
        response.raise_for_status()
        print("Raw API Response:", response.text)  # Print the raw response
        
        # Extract the content field from the response
        terraform_code = response.json()['choices'][0]['message']['content'].strip()
        
        # Remove Markdown code block delimiters if present
        if terraform_code.startswith("```") and terraform_code.endswith("```"):
            terraform_code = terraform_code.split("\n", 1)[1].rsplit("\n", 1)[0]
            
        print("Generated Terraform Code:", terraform_code)  # Print the cleaned Terraform code
        
        return terraform_code
    except Exception as e:
        print(f"Error during DeepSeek API call for Terraform code generation: {e}")
        return ""

# Function: Write Terraform code to file
def write_terraform_code(code, filename='infra.tf'):
    print(f"Writing Terraform code to {filename}...")
    try:
        with open(filename, 'w') as f:
            f.write(code)
        print(f"Terraform code written to {filename}.")
    except Exception as e:
        print(f"Error writing Terraform code to file: {e}")
        raise

# Function: Initialize Terraform
def initialize_terraform():
    print("Initializing Terraform...")
    try:
        result = subprocess.run(['terraform', 'init'], capture_output=True, text=True, check=True)
        print("Terraform initialized successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during Terraform initialization: {e.stderr}")
        print(f"Error during Terraform initialization (stdout): {e.stdout}")
        return False
    except Exception as e:
        print(f"Error during Terraform initialization: {e}")
        return False

# Function: Plan Terraform changes
def plan_terraform_changes():
    print("Planning Terraform changes...")
    try:
        result = subprocess.run(['terraform', 'plan'], capture_output=True, text=True, check=True)
        print("Terraform plan completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during Terraform plan: {e.stderr}")
        print(f"Error during Terraform plan (stdout): {e.stdout}")
        return False
    except Exception as e:
        print(f"Error during Terraform plan: {e}")
        return False

# Function: Apply Terraform changes
def apply_terraform_changes():
    print("Applying Terraform changes...")
    try:
        result = subprocess.run(['terraform', 'apply', '-auto-approve'], capture_output=True, text=True, check=True)
        print("Terraform changes applied successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during Terraform apply: {e.stderr}")
        print(f"Error during Terraform apply (stdout): {e.stdout}")
        return False
    except Exception as e:
        print(f"Error during Terraform apply: {e}")
        return False

# Function: Read commands from config file
def read_commands_from_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('commands', [])
    except Exception as e:
        print(f"Error reading config file {config_file}: {e}")
        return []

# The main function
def main():
    print("Script started.")
    try:
        # Perform environment and dependency checks
        sanity_checks()

        # Read the commands from the config file
        commands = read_commands_from_config(CONFIG_FILE_PATH)
        if not commands:
            print(f"No commands found in the config file at {CONFIG_FILE_PATH}. Exiting.")
            return

        # Process each command
        for command in commands:
            print(f"Processing command: {command}")

            # Generate Terraform code using DeepSeek
            terraform_code = generate_terraform_with_deepseek(command)
            if not terraform_code:
                print("No valid Terraform code generated. Skipping this command.")
                continue

            # Write Terraform code to file
            write_terraform_code(terraform_code)

            # Initialize Terraform
            if not initialize_terraform():
                print("Terraform initialization failed. Skipping this command.")
                continue

            # Plan Terraform changes
            if not plan_terraform_changes():
                print("Terraform plan failed. Skipping this command.")
                continue

            # Apply Terraform changes
            if not apply_terraform_changes():
                print("Terraform apply failed. Skipping this command.")
                continue

        print("Script completed successfully.")

    except Exception as e:
        print(f"Script failed with error: {e}")
        sys.exit(1)  # Exit with a non-zero code to indicate failure

if __name__ == "__main__":
    main()

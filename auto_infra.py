import sys
import os
import subprocess
import json
from dotenv import load_dotenv
import requests  # Replace openai with requests

print("Starting `auto_infra.py`...")

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

    # Check if Git is installed
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Git is installed.")
    except subprocess.CalledProcessError as e:
        raise EnvironmentError(f"Git is installed but the command failed: {e.stderr.decode()}")
    except FileNotFoundError:
        raise EnvironmentError("Git is not installed or not found in the PATH.")

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

# Function: Get recent Git changes
def get_git_changes():
    print("Fetching recent git changes...")
    # Check if there's more than one commit
    result = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], capture_output=True, text=True)
    head_rev = result.returncode == 0

    if not head_rev:
        print("No commits found. Skipping git diff.")
        return []

    # If only one commit, no diff to show
    # So check if there's more than 1 commit
    result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], capture_output=True, text=True)
    count = int(result.stdout.strip())

    if count < 2:
        print("Only one commit in repo, skipping git diff.")
        return []

    # Now perform diff between HEAD and previous commit
    result = subprocess.run(['git', 'diff', '--name-status', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
    changes = result.stdout.strip().split('\n')
    print("Changes obtained:", changes)
    return changes

# Function: Call DeepSeek to analyze changes and create a structured recipe
def analyze_changes_with_deepseek(changes):
    print("Calling DeepSeek to analyze changes...")
    change_list = "\n".join(changes)
    prompt = (
        "You are an AI that helps analyze code changes for infrastructure updates.\n"
        "Given a list of file changes, output a JSON array of objects, each with:\n"
        " - action: 'add', 'modify', or 'delete'\n"
        " - resource_type: e.g., 'database', 'server', 'storage', 'network'\n"
        " - details: brief description of the change\n"
        "Respond with a valid JSON array.\n"
        "Here are the changes:\n"
        f"{change_list}\n"
    )
    try:
        # Make a POST request to DeepSeek's API
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',  # Replace with DeepSeek's API endpoint
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("DEEPSEEK_API_KEY")}'
            },
            json={
                'model': 'deepseek-chat',  # Replace with the appropriate DeepSeek model
                'messages': [
                    {"role": "system", "content": "You analyze code changes for infrastructure."},
                    {"role": "user", "content": prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 600,
            }
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        reply_content = response.json()['choices'][0]['message']['content'].strip()
        print("DeepSeek response received.")
        # Parse JSON response
        recipe = json.loads(reply_content)
        print("Analysis JSON parsed successfully.")
        return recipe
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON from DeepSeek response.")
        return []
    except Exception as e:
        print(f"Error during DeepSeek API call: {e}")
        return []

# Function: Generate Terraform code based on the recipe
def synthesize_infra_with_deepseek(recipe):
    print("Generating Terraform code based on recipe...")
    prompt = (
        "Using the following infrastructure change description:\n"
        f"{json.dumps(recipe, indent=2)}\n"
        "Generate Terraform code snippets to implement these changes.\n"
        "Ensure the code is valid Terraform syntax."
    )
    try:
        # Make a POST request to DeepSeek's API
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',  # Replace with DeepSeek's API endpoint
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("DEEPSEEK_API_KEY")}'
            },
            json={
                'model': 'deepseek-gpt-4',  # Replace with the appropriate DeepSeek model
                'messages': [
                    {"role": "system", "content": "You generate Terraform code from infrastructure change descriptions."},
                    {"role": "user", "content": prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 600,
            }
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        reply_content = response.json()['choices'][0]['message']['content'].strip()
        print("Terraform code generated.")
        return reply_content
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
        return False
    except Exception as e:
        print(f"Error during Terraform apply: {e}")
        return False

# The main function
def main():
    print("Script started.")
    try:
        # Perform environment and dependency checks
        sanity_checks()

        # Get recent Git changes
        changes = get_git_changes()

        # Analyze changes with DeepSeek
        recipe = analyze_changes_with_deepseek(changes)
        if not recipe:
            print("No valid recipe generated. Exiting.")
            return

        # Generate Terraform code based on the recipe
        terraform_code = synthesize_infra_with_deepseek(recipe)
        if not terraform_code:
            print("No valid Terraform code generated. Exiting.")
            return

        # Write Terraform code to file
        write_terraform_code(terraform_code)

        # Initialize Terraform
        if not initialize_terraform():
            print("Terraform initialization failed. Exiting.")
            return

        # Plan Terraform changes
        if not plan_terraform_changes():
            print("Terraform plan failed. Exiting.")
            return

        # Apply Terraform changes
        if not apply_terraform_changes():
            print("Terraform apply failed. Exiting.")
            return

        print("Script completed successfully.")

    except Exception as e:
        print(f"Script failed with error: {e}")
        sys.exit(1)  # Exit with a non-zero code to indicate failure

if __name__ == "__main__":
    main()

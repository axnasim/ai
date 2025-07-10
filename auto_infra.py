import sys
import os
import subprocess
import json
from dotenv import load_dotenv
import openai

print("Starting `auto_infra.py`...")

# =========================
# Function: Perform sanity checks
def sanity_checks():
    print("Running sanity checks...")

    # Check if Terraform is installed
    try:
        subprocess.run(['terraform', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Terraform is installed.")
    except subprocess.CalledProcessError:
        raise EnvironmentError("Terraform is installed but the command failed.")
    except FileNotFoundError:
        raise EnvironmentError("Terraform is not installed or not found in the PATH.")

    # Check if Git is installed
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Git is installed.")
    except subprocess.CalledProcessError:
        raise EnvironmentError("Git is installed but the command failed.")
    except FileNotFoundError:
        raise EnvironmentError("Git is not installed or not found in the PATH.")

    # Check for `.env` file existence
    if not os.path.exists('.env'):
        raise FileNotFoundError("The `.env` file is missing. Please create it with your OpenAI API key.")
    print("`.env` file found.")

    # # Load environment variables
    # load_dotenv()
    # print("Environment variables loaded.")

    # Check for OpenAI API key presence and validity
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key is None:
        raise ValueError("The OPENAI_API_KEY is not set in the environment.")
    if not openai_key.strip():
        raise ValueError("The OPENAI_API_KEY in `.env` is empty.")
    if not openai_key.startswith('sk-'):
        raise ValueError("The OPENAI_API_KEY in `.env` is not in the correct format.")
    print("API key present and valid.")

    print("All sanity checks passed!")

# Function: Get recent Git changes
def get_git_changes():
    print("Fetching recent git changes...")
    try:
        result = subprocess.run(['git', 'diff', '--name-status', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")
        changes = result.stdout.strip().split('\n')
        print("Git changes obtained:", changes)
        return changes
    except Exception as e:
        print(f"Error fetching Git changes: {e}")
        raise

# Function: Call GPT to analyze changes and create a structured recipe
def analyze_changes_with_gpt(changes):
    print("Calling GPT to analyze changes...")
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
        response = openai.ChatCompletion.create(
            model='gpt-4', 
            messages=[
                {"role": "system", "content": "You analyze code changes for infrastructure."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600,
        )
        reply_content = response.choices[0].message['content'].strip()
        print("GPT response received.")
        # Parse JSON response
        recipe = json.loads(reply_content)
        print("Analysis JSON parsed successfully.")
        return recipe
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON from GPT response.")
        return []
    except Exception as e:
        print(f"Error during GPT API call: {e}")
        return []

# Function: Generate Terraform code based on the recipe
def synthesize_infra_with_gpt(recipe):
    print("Generating Terraform code based on recipe...")
    prompt = (
        "Using the following infrastructure change description:\n"
        f"{json.dumps(recipe, indent=2)}\n"
        "Generate Terraform code snippets to implement these changes.\n"
        "Ensure the code is valid Terraform syntax."
    )
    try:
        response = openai.ChatCompletion.create(
            model='gpt-4',  
            messages=[
                {"role": "system", "content": "You generate Terraform code from infrastructure change descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600,
        )
        reply_content = response.choices[0].message['content'].strip()
        print("Terraform code generated.")
        return reply_content    
    except Exception as e:
        print(f"Error during GPT API call for Terraform code generation: {e}")
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
        result = subprocess.run(['terraform', 'init'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Terraform initialization failed: {result.stderr}")
        print("Terraform initialized successfully.")
        return True
    except Exception as e:
        print(f"Error during Terraform initialization: {e}")
        raise

# Function: Plan Terraform changes
def plan_terraform_changes():
    print("Planning Terraform changes...")
    try:
        result = subprocess.run(['terraform', 'plan'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Terraform plan failed: {result.stderr}")
        print("Terraform plan completed successfully.")
        return True
    except Exception as e:
        print(f"Error during Terraform plan: {e}")
        raise

# Function: Apply Terraform changes
def apply_terraform_changes():
    print("Applying Terraform changes...")
    try:
        result = subprocess.run(['terraform', 'apply', '-auto-approve'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Terraform apply failed: {result.stderr}")
        print("Terraform changes applied successfully.")
        return True
    except Exception as e:
        print(f"Error during Terraform apply: {e}")
        raise

# The main function
def main():
    print("Script started.")
    try:
        # Perform environment and dependency checks
        sanity_checks()

        # Assign API key from environment
        openai.api_key = os.getenv('OPENAI_API_KEY')
        print("OpenAI API key set.")

        # Get recent Git changes
        changes = get_git_changes()

        # Analyze changes with GPT
        recipe = analyze_changes_with_gpt(changes)
        if not recipe:
            print("No valid recipe generated. Exiting.")
            return

        # Generate Terraform code based on the recipe
        terraform_code = synthesize_infra_with_gpt(recipe)
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

if __name__ == "__main__":
    main()

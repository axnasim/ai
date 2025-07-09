import os
from dotenv import load_dotenv
import openai
import subprocess
import json

# Load environment variables from .env file
load_dotenv()

# Load API key securely
openai.api_key = os.getenv('OPENAI_API_KEY')

# Ensure the API key is set
if not openai.api_key:
    raise ValueError("OpenAI API key is not set. Please set it in the .env file.")

# Ensure Terraform is installed and available in the PATH
try:
    subprocess.run(['terraform', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except FileNotFoundError:
    raise EnvironmentError("Terraform is not installed or not found in the PATH. Please install Terraform and try again.")  
# Ensure Git is installed and available in the PATH
try:
    subprocess.run(['git', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except FileNotFoundError:
    raise EnvironmentError("Git is not installed or not found in the PATH. Please install Git and try again.")

# Ensure the .env file exists and contains the OpenAI API key
if not os.path.exists('.env'):
    raise FileNotFoundError("The .env file is missing. Please create a .env file with your OpenAI API key.")    
# Ensure the .env file contains the OpenAI API key
if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("The .env file does not contain the OPENAI_API_KEY. Please add it to the .env file.")  
# Ensure the .env file is correctly formatted
if not os.environ['OPENAI_API_KEY'].strip():
    raise ValueError("The OPENAI_API_KEY in the .env file is empty. Please set it to your OpenAI API key.") 

def get_git_changes():
    result = subprocess.run(['git', 'diff', '--name-status', 'HEAD~1', 'HEAD'], capture_output=True, text=True)
    changes = result.stdout.strip().split('\n')
    return changes

def analyze_changes_with_gpt(changes):
    change_list = "\n".join(changes)
    prompt = (
        "You are an AI that helps analyze code changes for infrastructure updates.\n"
        "Given a list of file changes, output a JSON array of objects, each with the following fields:\n"
        " - action: one of 'add', 'modify', 'delete'\n"
        " - resource_type: e.g., 'database', 'server', 'storage', 'network'\n"
        " - details: description of the change\n"
        "\nHere is the list of changes:\n"
        f"{change_list}\n"
        "Please respond with a JSON array in the following format:\n"
        "[{{\"action\": \"add\", \"resource_type\": \"database\", \"details\": \"add new Postgres DB\"}}, ...]\n"
        "Ensure the output is valid JSON."
    )
    try:
        response = openai.ChatCompletion.create(
            model='gpt-4',  # or 'gpt-3.5-turbo'
            messages=[
                {"role": "system", "content": "You analyze code changes for infrastructure."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )
        reply_content = response.choices[0].message['content'].strip()
        recipe = json.loads(reply_content)
        return recipe
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON from GPT response.")
        return []
    except Exception as e:
        print(f"Error during GPT API call: {e}")
        return []

def synthesize_infra_with_gpt(recipe):
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
                {"role": "system", "content": "You are an expert in writing Terraform code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        terraform_code = response.choices[0].message['content']
        with open('main.tf', 'w') as f:
            f.write(terraform_code)
        print("Terraform code generated and saved to main.tf.")
    except Exception as e:
        print(f"Error generating Terraform code: {e}")

def validate_infra():
    print("Validating infrastructure code...")
    # Placeholder: add real validation here
    return True

def deploy_infrastructure():
    print("Initializing Terraform...")
    subprocess.run(['terraform', 'init'])
    print("Applying Terraform plan...")
    subprocess.run(['terraform', 'apply', '-auto-approve'])

def main():
    changes = get_git_changes()
    if not changes or changes == ['']:
        print("No changes detected.")
        return
    recipe = analyze_changes_with_gpt(changes)
    if not recipe:
        print("No valid recipe generated, stopping process.")
        return
    synthesize_infra_with_gpt(recipe)
    if validate_infra():
        deploy_infrastructure()
    else:
        print("Validation failed, deployment aborted.")

if __name__ == '__main__':
    main()

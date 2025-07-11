Here’s a **README.md** file for the `auto_infra.py` script. This README provides an overview of the project, how to set it up, and how to use it.

---

# Auto Infrastructure Deployment with Terraform and DeepSeek

This project automates the deployment of infrastructure using **Terraform** and **DeepSeek**. The `auto_infra.py` script generates Terraform code based on high-level commands, initializes Terraform, plans, and applies the changes.

## Features

- **Terraform Code Generation**: The script uses the DeepSeek API to generate Terraform code from high-level commands.
- **S3 Bucket Name Generation**: The `create_s3_bucket.py` script generates a valid S3 bucket name and writes it to `config.json`.
- **Terraform Workflow**: The script automates the Terraform workflow, including initialization, planning, and applying changes.
- **Config File**: The `config.json` file stores the high-level commands and the generated S3 bucket name.

## Prerequisites

Before running the script, ensure you have the following installed:

- **Python 3.8+**
- **Terraform** (installed and added to your PATH)
- **DeepSeek API Key** (set as an environment variable `DEEPSEEK_API_KEY`)

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/auto-infra.git
   cd auto-infra
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory and add your DeepSeek API key:
     ```
     DEEPSEEK_API_KEY=your_api_key_here
     ```
   - Load the environment variables:
     ```bash
     export $(cat .env | xargs)
     ```

4. **Configure `config.json`**:
   - The `config.json` file should contain the high-level commands. Example:
     ```json
     {
         "commands": [
             "Deploy a webserver with Amazon Linux AMI in us-east-1.",
             "Create an S3 bucket with the name {bucket_name}."
         ]
     }
     ```

## Usage

1. **Generate S3 Bucket Name**:
   - Run the `create_s3_bucket.py` script to generate a valid S3 bucket name and update `config.json`:
     ```bash
     python create_s3_bucket.py
     ```

2. **Run the Auto Infrastructure Script**:
   - Execute the `auto_infra.py` script to generate Terraform code, initialize Terraform, and apply the changes:
     ```bash
     python auto_infra.py
     ```

### Example Workflow

1. **Generate S3 Bucket Name**:
   ```bash
   python create_s3_bucket.py
   ```
   - This updates `config.json` with the generated bucket name:
     ```json
     {
         "bucket_name": "my-bucket-abc123xyz",
         "commands": [
             "Deploy a webserver with Amazon Linux AMI in us-east-1.",
             "Create an S3 bucket with the name my-bucket-abc123xyz."
         ]
     }
     ```

2. **Run the Auto Infrastructure Script**:
   ```bash
   python auto_infra.py
   ```
   - The script will:
     - Generate Terraform code using DeepSeek.
     - Write the Terraform code to `infra.tf`.
     - Initialize Terraform.
     - Plan and apply the Terraform changes.

## Script Details

### `auto_infra.py`

- **Main Script**: Automates the Terraform workflow.
- **Functions**:
  - `sanity_checks()`: Checks if Terraform is installed and validates the DeepSeek API key.
  - `generate_terraform_with_deepseek(command)`: Generates Terraform code using the DeepSeek API.
  - `write_terraform_code(code, filename)`: Writes the generated Terraform code to a file.
  - `initialize_terraform()`: Initializes Terraform.
  - `plan_terraform_changes()`: Plans the Terraform changes.
  - `apply_terraform_changes()`: Applies the Terraform changes.
  - `read_commands_from_config(config_file)`: Reads the commands from `config.json`.
  - `run_create_s3_bucket_script()`: Runs the `create_s3_bucket.py` script to generate the S3 bucket name.

### `create_s3_bucket.py`

- **S3 Bucket Name Generator**: Generates a valid S3 bucket name and writes it to `config.json`.
- **Functions**:
  - `generate_s3_bucket_name(prefix, length)`: Generates a valid S3 bucket name.
  - `write_bucket_name_to_config(bucket_name, config_file)`: Writes the bucket name to `config.json`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Example `config.json`:

```json
{
    "bucket_name": "my-bucket-abc123xyz",
    "commands": [
        "Deploy a webserver with Amazon Linux AMI in us-east-1.",
        "Create an S3 bucket with the name my-bucket-abc123xyz."
    ]
}
```

### Example `.env`:

```
DEEPSEEK_API_KEY=your_api_key_here
```

---

This README provides a comprehensive guide to setting up and using the `auto_infra.py` script. Let me know if you need further assistance!
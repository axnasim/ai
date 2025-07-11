import json
import random
import string
import os

# Function to generate a valid S3 bucket name
def generate_s3_bucket_name(prefix="my-bucket", length=10):
    """
    Generates a valid S3 bucket name.
    :param prefix: Prefix for the bucket name (default: "my-bucket").
    :param length: Length of the random suffix (default: 10).
    :return: A valid S3 bucket name.
    """
    # Ensure the prefix is lowercase and only contains allowed characters
    prefix = prefix.lower()
    prefix = ''.join(c for c in prefix if c in string.ascii_lowercase + string.digits + '-')

    # Generate a random suffix
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    # Combine prefix and suffix to form the bucket name
    bucket_name = f"{prefix}-{suffix}"

    # Ensure the bucket name is between 3 and 63 characters
    if len(bucket_name) > 63:
        bucket_name = bucket_name[:63]

    # Ensure the bucket name starts and ends with a letter or number
    if not bucket_name[0].isalnum():
        bucket_name = 'a' + bucket_name[1:]
    if not bucket_name[-1].isalnum():
        bucket_name = bucket_name[:-1] + 'a'

    return bucket_name

# Function to write the bucket name to config.json
def write_bucket_name_to_config(bucket_name, config_file="config.json"):
    """
    Writes the bucket name to a config file.
    :param bucket_name: The S3 bucket name to write.
    :param config_file: The path to the config file (default: "config.json").
    """
    # Check if the config file already exists
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}

    # Add the bucket name to the config
    config["bucket_name"] = bucket_name

    # Write the updated config to the file
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"Bucket name '{bucket_name}' written to {config_file}.")

# Main function
def main():
    # Generate a valid S3 bucket name
    bucket_name = generate_s3_bucket_name()

    # Write the bucket name to config.json
    write_bucket_name_to_config(bucket_name)

if __name__ == "__main__":
    main()

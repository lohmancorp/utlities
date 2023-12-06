##################################################################################
# anonymizer.py 
#
# Description:   Script that allows the user to define keys in a json array that 
#                must be anonymized.  
#
# version: 1.0.1
# Author: taylor.m.giddens@gmail.com
# More information: https://github.com/lohmancorp/utlities/
##################################################################################

import argparse
import json
import random
import re

def generate_lipsum(length):
    lipsum = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
              "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
              "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
              "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
    return (lipsum * (length // len(lipsum) + 1))[:length]

def randomize_number(length):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def is_email(s):
    return re.match(r"[^@]+@[^@]+\.[^@]+", s)

def replace_emails(s):
    return re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "anonymizedemail@domain.com", s)

def preserve_numbers(s):
    return re.sub(r'\d+(\.\d+)?', lambda x: x.group(), s)

def anonymize_urls(s):
    return re.sub(r'https?://[^\s]+', "https://host.foo.com", s)

def anonymize_data(input_file, keys, echo, number_support):
    with open(input_file, 'r') as file:
        data = json.load(file)

    def anonymize_recursive(item):
        if isinstance(item, dict):
            for key, value in item.items():
                if key in keys:
                    if isinstance(value, int):
                        item[key] = int(randomize_number(len(str(value))))
                    elif isinstance(value, str):
                        if is_email(value):
                            value = replace_emails(value)
                        value = anonymize_urls(value)
                        if number_support:
                            value = preserve_numbers(value)
                        item[key] = value
                    else:
                        new_value = generate_lipsum(len(value))
                        new_value = replace_emails(new_value)
                        new_value = anonymize_urls(new_value)
                        if number_support:
                            new_value = preserve_numbers(new_value)
                        item[key] = new_value
                else:
                    anonymize_recursive(value)
        elif isinstance(item, list):
            for elem in item:
                anonymize_recursive(elem)

    anonymize_recursive(data)

    with open(input_file, 'w') as file:
        json.dump(data, file, indent=4)

    if echo:
        print(json.dumps(data, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anonymize specific fields in a JSON file.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file path.")
    parser.add_argument("-k", "--keys", required=True, help="Comma-separated keys to anonymize, spaces after commas are handled.")
    parser.add_argument("-n", "--number-support", action="store_true", help="Preserve numbers in strings during anonymization.")
    parser.add_argument("-e", "--echo", action="store_true", help="Echo the updated result to the screen.")
    
    args = parser.parse_args()
    keys_to_anonymize = [key.strip() for key in args.keys.split(",")]

    anonymize_data(args.input, keys_to_anonymize, args.echo, args.number_support)
    print(f"Data in '{args.input}' has been anonymized.")

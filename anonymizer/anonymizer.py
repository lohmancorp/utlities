##################################################################################
# anonymizer.py 
#
# Description:   Script that allows the user to define keys in a json array that 
#                must be anonymized.  
#
# version: 1.0.2
# Author: taylor.m.giddens@gmail.com
# More information: https://github.com/lohmancorp/utlities/
##################################################################################

import argparse
import json
import re
from html.parser import HTMLParser

# HTMLParser subclass to replace text within HTML tags
class HTMLLipsumParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = ""

    def handle_starttag(self, tag, attrs):
        # Append the start tag to the result
        self.result += f"<{tag}"
        for attr in attrs:
            self.result += f' {attr[0]}="{attr[1]}"'
        self.result += ">"

    def handle_endtag(self, tag):
        # Append the end tag to the result
        self.result += f"</{tag}>"

    def handle_data(self, data):
        # Replace the data with anonymized text
        anonymized_data = replace_emails(data)
        lipsum_text = generate_lipsum(len(anonymized_data))
        self.result += lipsum_text

# Generates lorem ipsum text of a specified length
def generate_lipsum(length):
    # Define a standard lorem ipsum text
    lipsum = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
              "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
              "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
              "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
    # Return a substring of the lorem ipsum text of the required length
    return (lipsum * (length // len(lipsum) + 1))[:length]

def replace_html_content(s):
    # Parse the HTML content and replace text within tags
    parser = HTMLLipsumParser()
    parser.feed(s)
    return parser.result

def replace_emails(s):
    # Regular expression pattern for identifying emails
    email_regex = r"[\w\.-]+@[\w\.-]+\.\w+"
    # Replace emails with a placeholder
    return re.sub(email_regex, "anonymizedemail@domain.com", s)

def preserve_numbers(s):
    # Preserve numbers in the text
    return re.sub(r'\d+(\.\d+)?', lambda x: x.group(), s)

def anonymize_urls(s):
    # Replace URLs with a placeholder
    return re.sub(r'https?://[^\s]+', "https://host.foo.com", s)

def transform_string(s, max_length=None):
    # Anonymize emails first to handle cases like "Lorem ipsu<tom.emery@team.telstra.com>"
    s = replace_emails(s)

    # Then handle HTML content or other transformations
    if '<' in s and '>' in s:
        s = replace_html_content(s)
    else:
        s = anonymize_urls(s)
        s = preserve_numbers(s)

    # Truncate the string if it exceeds the maximum length
    if max_length is not None and len(s) > max_length:
        s = s[:max_length]
    return s

def anonymize_data(input_file, keys, echo, max_length=None):
    # Load data from the input file
    with open(input_file, 'r') as file:
        data = json.load(file)

    def anonymize_recursive(item):
        # Recursively anonymize data in dictionaries and lists
        if isinstance(item, dict):
            for key, value in item.items():
                if key in keys:
                    if isinstance(value, str):
                        transformed = transform_string(value, max_length)
                        item[key] = generate_lipsum(len(transformed)) if transformed == value else transformed
                    elif isinstance(value, list):
                        item[key] = [transform_string(v, max_length) if isinstance(v, str) else v for v in value]
                else:
                    anonymize_recursive(value)
        elif isinstance(item, list):
            for elem in item:
                anonymize_recursive(elem)

    # Apply the anonymization to the data
    anonymize_recursive(data)

    # Write the anonymized data back to the file
    with open(input_file, 'w') as file:
        json.dump(data, file, indent=4)

    # Optionally echo the data
    if echo:
        print(json.dumps(data, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anonymize specific fields in a JSON file.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file path.")
    parser.add_argument("-k", "--keys", required=True, help="Comma-separated keys to anonymize.")
    parser.add_argument("-e", "--echo", action="store_true", help="Echo the updated result to the screen.")
    parser.add_argument("-c", "--concatenate", type=int, nargs='?', const=1000, help="Truncate strings to the specified length after anonymization. Default is 1000 characters.")

    args = parser.parse_args()
    keys_to_anonymize = [key.strip() for key in args.keys.split(",")]

    anonymize_data(args.input, keys_to_anonymize, args.echo, args.concatenate)
    print(f"Data in '{args.input}' has been anonymized.")

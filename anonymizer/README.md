# Anonymizer
Tool created for anonymizing json data that is eventually to be used in datasets for use in ML training or use in training LLMs.

Usage

    python anonymizer.py -k "subject, description, description_text, department_id" -n -i test.json 

("-i", "--input", required=True, help="Input JSON file path.")
("-k", "--keys", required=True, help="Comma-separated keys to anonymize, spaces after commas are handled.")
("-n", "--number-support", action="store_true", help="Preserve numbers in strings during anonymization.")
("-e", "--echo", action="store_true", help="Echo the updated result to the screen.")

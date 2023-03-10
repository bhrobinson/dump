import sys
import jsonschema
import json

file = sys.argv[1]

try:
    data = json.load(open(file))
except json.JSONDecodeError as e:
    print("Invalid JSON file")
    sys.exit(1)

schema_file = sys.argv[2]

try:
    schema = json.load(open(schema_file))
except json.JSONDecodeError as e:
    print("Invalid JSON Schema file")
    sys.exit(1)

result = jsonschema.validate(data, schema)
if result == None:
    print("Valid JSON file")
    sys.exit(0)
else:
    print("Invalid JSON file")
    sys.exit(1)
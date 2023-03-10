import yaml
import json
import sys

def set_default_values(result, schema):
    if schema["type"] == "object" and "properties" in schema:
        for key, value in schema["properties"].items():
            if key not in result and "default" in value:
                result[key] = value["default"]
            if value["type"] == "object":
                if key in result:
                    set_default_values(result[key], value)
                else:
                    result[key] = {}
                    set_default_values(result[key], value)
            elif isinstance(result, dict) and key in result:
                if isinstance(result[key], str):
                    result[key] = {"resource": result[key]}
                    
def yaml_to_json(yaml_file, json_schema, json_file):
    try:
        with open(yaml_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
        with open(json_schema, 'r') as file:
            schema = json.load(file)
        result = {}
        for key, value in schema["properties"].items():
            if key in yaml_content:
                result[key] = yaml_content[key]
            elif "default" in value:
                result[key] = value["default"]
            if value["type"] == "object":
                if key in yaml_content:
                    result[key] = yaml_content[key]
                    set_default_values(result[key], value)
                else:
                    result[key] = {}
                    set_default_values(result[key], value)

        with open(json_file, 'w') as file:
            json.dump(result, file, indent=2)
        print("Success: '{}' converted to '{}' following the schema '{}' successfully!".format(yaml_file, json_file, json_schema))
    except Exception as e:
        print("Error: ", e)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Error: Incorrect number of arguments.")
        print("Usage: python yaml_to_json.py <source_yaml_file> <json_schema> <destination_json_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    json_schema = sys.argv[2]
    json_file = sys.argv[3]
    yaml_to_json(yaml_file, json_schema, json_file)

import json

def load_asset(location):
    with open(location, 'r') as read_file:
        asset = dict(json.load(read_file))
        
    return asset

def write_data(location, data):
    with open(location, 'w') as write_file:
        json.dump(data, write_file)
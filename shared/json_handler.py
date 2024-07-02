import json

def get_tag(data):
    return data["tag"]

def compare_tag_from_socket(data, tag, callback=None, socket=None):
    if callback:
        if get_tag(data) == tag:
            callback(data, socket)

    return get_tag(data) == tag
    
def json_encode(tag, data):
    return json.dumps({"tag": tag, "data": data})

def json_decode(data):
    return json.loads(data)

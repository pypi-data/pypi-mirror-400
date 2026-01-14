import json
from json import JSONEncoder, JSONDecoder


class SimpleObjEncoder(JSONEncoder):
    """
    Classes to encode simple objects to json based on __dict__
    """

    def default(self, obj):
        try:
            return obj.__dict__
        except AttributeError:
            pass


def encode_simple_obj_to_json_dict(obj):
    """
    Encodes less complex classes as json
    """
    return json.dumps(obj, cls=SimpleObjEncoder)


def encode_simple_obj_to_json_file(obj, jsonfile):
    """
    Encodes less complex classes in a json file
    """
    print(obj)
    with open(jsonfile, "w") as oj:
        return json.dump(obj, oj, cls=SimpleObjEncoder)


def from_json(json_dict):
    """
    Placeholder for custom function to pass to the decoder
    """
    return json_dict


def decode_simple_obj_from_json(obj, func_from_json=from_json):
    """
    Encodes less complex classes as json
    """

    json_dict = json.loads(obj)
    return JSONDecoder(object_hook=func_from_json).decode(json_dict)

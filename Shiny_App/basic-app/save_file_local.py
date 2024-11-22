import pickle
import base64


def save_object_to_localstorage(obj):
    """Save an object to disk using pickle."""
    message_bytes = pickle.dumps(obj)
    base64_bytes = base64.b64encode(message_bytes)
    txt = base64_bytes.decode('ascii')
    return txt

def write_js_file(StationName,txt):
    with open("save_data.js", "w") as file:
        file.write(f'localStorage.setItem({StationName}, {txt});')
    
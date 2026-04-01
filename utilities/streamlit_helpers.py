import base64
from io import BytesIO

def decode_base64_image(b64_string):
    # Strip data URL prefix if present
    if b64_string.startswith("data:image"):
        b64_string = b64_string.split(",", 1)[1]

    return BytesIO(base64.b64decode(b64_string))



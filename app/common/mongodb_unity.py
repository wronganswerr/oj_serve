from bson.int64 import Int64

def convert_int64(document):
    if isinstance(document, dict):
        for key, value in document.items():
            document[key] = convert_int64(value)
    elif isinstance(document, list):
        document = [convert_int64(item) for item in document]
    elif isinstance(document, Int64):
        document = int(document)
    return document
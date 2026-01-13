import os
from dotenv import load_dotenv
from syntaxmatrix.project_root import detect_project_root


def getenv_api_key(client_dir, key_name):
    _CLIENT_DOTENV_PATH = os.path.join(str(client_dir.parent), ".env")
    if os.path.isfile(_CLIENT_DOTENV_PATH):
        load_dotenv(_CLIENT_DOTENV_PATH, override=True)

    try:
        return os.getenv(key_name)
    except Exception:
        pass


def read_client_file(client_dir, client_file):
    client_file_path = os.path.join(str(client_dir.parent), client_file)
    try:
        with open(client_file_path, 'r') as f:
            content = f.read()
            return content
    except Exception as e:
        pass

# def client_media_path(client_dir, client_localassets_file):
#     client_asset = os.path.join(str(client_dir.parent), client_localassets_file)
#     return client_asset
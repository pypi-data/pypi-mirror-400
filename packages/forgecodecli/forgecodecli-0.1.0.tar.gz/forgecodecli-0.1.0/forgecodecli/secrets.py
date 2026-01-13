import keyring

SERVICE_NAME = "forgecodecli"

def save_api_key(api_key: str):
    keyring.set_password(SERVICE_NAME, "api_key", api_key)
    
def load_api_key() -> str | None:
    return keyring.get_password(SERVICE_NAME, "api_key")

def delete_api_key():
    keyring.delete_password(SERVICE_NAME, "api_key")
    

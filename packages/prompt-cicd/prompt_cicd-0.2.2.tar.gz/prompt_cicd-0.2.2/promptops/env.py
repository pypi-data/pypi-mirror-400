import os

def get_env():
    return os.getenv("PROMPTOPS_ENV", "dev")

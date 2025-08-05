import os
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(base_dir, "credentials.yaml")
    with open(credentials_path) as file:
        return yaml.load(file, Loader=SafeLoader)

def get_authenticator(config):
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

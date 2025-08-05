from streamlit_authenticator import Hasher

def hash_password(password):
    return Hasher([password]).generate()[0]  # Returns the first hashed password

def check_password(password, hashed_password):
    return Hasher([password]).check([hashed_password])[0]


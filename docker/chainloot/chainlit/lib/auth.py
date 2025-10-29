# lib/auth.py

import chainlit as cl
import os


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """
    Simple authentication callback for Chainlit.
    Checks credentials against environment variables.
    """
    # Simple authentication - check against environment variables
    expected_username = os.getenv("CHAINLIT_USERNAME")
    expected_password = os.getenv("CHAINLIT_PASSWORD")
    
    if username == expected_username and password == expected_password:
        return cl.User(identifier=username, metadata={"role": "admin"})
    else:
        return None
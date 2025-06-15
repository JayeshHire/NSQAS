import os

redirect_uri = os.environ["REDIRECT_URI"]
cookie_secret = os.environ["COOKIE_SECRET"]
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]

auth_str = f"""
[auth]
redirect_uri = "{redirect_uri}"
cookie_secret = "{cookie_secret}"

[auth.google]
client_id = "{client_id}"
client_secret = "{client_secret}"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
"""

with open("./.streamlit/secrets.toml", 'a+') as secret_f:
    secret_f.write(auth_str)
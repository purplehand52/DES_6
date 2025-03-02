# Oracle to encrypt 64 bit messages
import requests

URL = "http://192.168.134.164:8000/"

def encrypt(plaintext: str) -> str:
    # Encrypt plaintext
    r = requests.post(URL, data={"plaintext": plaintext,})
    # Web-scrap the ciphertext (alert alert-secondary)
    ciphertext = r.text.split('<p class="alert alert-secondary">')[1].split('</p>')[0]
    return ciphertext

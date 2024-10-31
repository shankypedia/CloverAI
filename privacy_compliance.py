from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()
with open('secret.key', 'wb') as key_file:
    key_file.write(key)

# Load key and encrypt sensitive information
with open('secret.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)
sensitive_data = "Sensitive information to encrypt".encode()
encrypted_data = cipher_suite.encrypt(sensitive_data)
print("Encrypted data:", encrypted_data)

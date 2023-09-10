from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def encrypt_file(file_path, encryption_key):
    with open(file_path, 'rb') as file:
        content = file.read()

    fernet = Fernet(encryption_key)
    encrypted_content = fernet.encrypt(content)

    encrypted_file_path = file_path + '.encrypted'
    with open(encrypted_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_content)

    return encrypted_file_path


def decrypt_file(encrypted_file_path, encryption_key):
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_content = encrypted_file.read()

    fernet = Fernet(encryption_key)
    decrypted_content = fernet.decrypt(encrypted_content)

    decrypted_file_path = encrypted_file_path[:-10]
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_content)

    return decrypted_file_path

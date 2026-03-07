from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
import os


def generate_rsa_key(path):
    key = rsa.generate_private_key(
        backend=crypto_default_backend(), public_exponent=65537, key_size=4096
    )

    # Private key in OpenSSH format (PEM)
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.OpenSSH,
        crypto_serialization.NoEncryption(),
    )

    # Public key in OpenSSH format
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH
    )

    with open(path, "wb") as f:
        f.write(private_key)

    with open(path + ".pub", "wb") as f:
        f.write(public_key)


if __name__ == "__main__":
    folder = r"c:\Users\Usuario\Desktop\AURENIX\Claves_contraseñas"
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, "aurenix_it_agent_rsa")
    generate_rsa_key(path)
    print(f"RSA key generated at {path}")

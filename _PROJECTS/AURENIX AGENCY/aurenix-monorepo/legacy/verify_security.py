import sys
import os

# Add agent-worker/src to path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, 'apps', 'agent-worker', 'src')
sys.path.append(SRC_PATH)

try:
    from tools.security import encrypt_secret, decrypt_secret
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to direct path append for tools
    sys.path.append(os.path.join(SRC_PATH, 'tools'))
    from security import encrypt_secret, decrypt_secret

def test_encryption():
    # Set env vars for test
    os.environ["AURENIX_MASTER_KEY"] = "test-master-key-1234567890abcdef"
    os.environ["AURENIX_ENCRYPTION_SALT"] = "test-salt-123"

    secret = "SuperSecretValue2026"
    print(f"Testing basic encryption for: {secret}")

    encrypted = encrypt_secret(secret)
    print(f"Encrypted (Python): {encrypted}")

    decrypted = decrypt_secret(encrypted)
    print(f"Decrypted (Python): {decrypted}")

    if secret != decrypted:
        print("FAIL: Python roundtrip failed")
        sys.exit(1)
    
    print("SUCCESS: Python roundtrip passed")

def test_multitenant_isolation():
    """
    Simulates isolation check. In Aurenix, while we use a Master Key, 
    we must ensure that changing the key or salt correctly prevents decryption.
    True multitenancy in the DB is handled via organization_id filters in Prisma.
    """
    print("\n--- Testing Security Isolation ---")
    os.environ["AURENIX_MASTER_KEY"] = "TENANT_A_KEY_1234567890123456"
    os.environ["AURENIX_ENCRYPTION_SALT"] = "SALT_A"
    
    secret = "DataForTenantA"
    encrypted_a = encrypt_secret(secret)
    
    print("Switching security context to Tenant B...")
    os.environ["AURENIX_MASTER_KEY"] = "TENANT_B_KEY_1234567890123456"
    os.environ["AURENIX_ENCRYPTION_SALT"] = "SALT_B"
    
    decrypted_attempt = decrypt_secret(encrypted_a)
    print(f"Decryption attempt with wrong key: {decrypted_attempt}")
    
    if decrypted_attempt == secret:
        print("CRITICAL FAIL: Isolation breach! Data decrypted with wrong key.")
        sys.exit(1)
    else:
        print("SUCCESS: Isolation confirmed. Wrong key cannot decrypt data.")

if __name__ == "__main__":
    test_encryption()
    test_multitenant_isolation()
    
    # Check args for cross-verification
    if len(sys.argv) > 1:
        # CLI tool mode 
        start_val = sys.argv[1]
        if len(start_val) > 20 and " " not in start_val:
            print(f"Decrypting input: {start_val}")
            print(f"Decrypted Input: {decrypt_secret(start_val)}")
        else:
            print(f"Encrypting input: {start_val}")
            print(f"Encrypted Input: {encrypt_secret(start_val)}")

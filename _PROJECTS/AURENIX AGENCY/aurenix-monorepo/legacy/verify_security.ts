import { webcrypto } from 'node:crypto';
import { pbkdf2 } from 'node:crypto';
import { promisify } from 'node:util';

const pbkdf2Async = promisify(pbkdf2);

/**
 * Derives the AES-256 key using PBKDF2-SHA256
 */
async function getKey(): Promise<any> {
  const masterKey = process.env.AURENIX_MASTER_KEY;
  if (!masterKey) {
    throw new Error("CRITICAL: AURENIX_MASTER_KEY is missing.");
  }
  
  const saltEnv = process.env.AURENIX_ENCRYPTION_SALT;
  if (!saltEnv) {
    throw new Error("CRITICAL: AURENIX_ENCRYPTION_SALT is missing.");
  }

  const salt = new TextEncoder().encode(saltEnv);
  
  const derivedBits = await pbkdf2Async(
    masterKey,
    salt,
    100000,
    32,
    'sha256'
  );

  return await webcrypto.subtle.importKey(
    'raw',
    derivedBits,
    { name: 'AES-GCM' },
    false,
    ['encrypt', 'decrypt']
  );
}

async function encryptSecret(plainText: string): Promise<string> {
  if (!plainText) return "";

  try {
    const key = await getKey();
    const nonce = webcrypto.getRandomValues(new Uint8Array(12));
    const encodedText = new TextEncoder().encode(plainText);

    const ciphertextBuffer = await webcrypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: nonce,
      },
      key,
      encodedText
    );

    const ciphertextArray = new Uint8Array(ciphertextBuffer);
    const combined = new Uint8Array(nonce.length + ciphertextArray.length);
    combined.set(nonce);
    combined.set(ciphertextArray, nonce.length);

    return Buffer.from(combined).toString('base64url');
  } catch (error) {
    console.error("Encryption failed:", error);
    throw error;
  }
}

async function decryptSecret(encryptedText: string): Promise<string> {
  if (!encryptedText) return "";

  try {
    const key = await getKey();
    
    // base64url decode
    const combined = Buffer.from(encryptedText, 'base64url');
    
    if (combined.length < 12) return "[INVALID_DATA]";

    const nonce = combined.subarray(0, 12);
    const ciphertextWithTag = combined.subarray(12);

    const decryptedBuffer = await webcrypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: nonce,
      },
      key,
      ciphertextWithTag
    );

    return new TextDecoder().decode(decryptedBuffer);
  } catch (error) {
    console.error("Decryption failed:", error);
    return "[DECRYPTION_FAILED]";
  }
}

const masterKey = "test-master-key-1234567890abcdef";
const salt = "test-salt-123";

process.env.AURENIX_MASTER_KEY = masterKey;
process.env.AURENIX_ENCRYPTION_SALT = salt;

async function test() {
  const secret = "SuperSecretValue2026";
  console.log(`Original: ${secret}`);

  try {
    const encrypted = await encryptSecret(secret);
    console.log(`Encrypted (TS): ${encrypted}`);

    const decrypted = await decryptSecret(encrypted);
    console.log(`Decrypted (TS): ${decrypted}`);

    if (secret !== decrypted) {
      console.error("FAIL: TS roundtrip failed");
      process.exit(1);
    }
    console.log("SUCCESS: TS roundtrip passed");

    // Handle CLI args
    const args = process.argv.slice(2);
    if (args.length > 0) {
        const input = args[0];
        if (input.length > 20 && !input.includes(" ")) {
            console.log(`Decrypting input: ${input}`);
            console.log(`Decrypted Input: ${await decryptSecret(input)}`);
        } else {
            console.log(`Encrypting input: ${input}`);
            console.log(`Encrypted Input: ${await encryptSecret(input)}`);
        }
    }

  } catch (e) {
    console.error(e);
    process.exit(1);
  }
}

test();

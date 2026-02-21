import base64
from nacl.signing import SigningKey

sk = SigningKey.generate()
vk = sk.verify_key

print("PRIVATE_KEY_B64=", base64.b64encode(sk.encode()).decode())
print("PUBLIC_KEY_B64 =", base64.b64encode(vk.encode()).decode())

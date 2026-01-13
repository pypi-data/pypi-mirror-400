from license_tool.keygen import generate_keys
from license_tool.key.signer import sign_license
from license_tool.key.verifier import verify_license
import os

# === 1️⃣ 生成 RSA 公私鑰 ===
keys_dir = "keys"
print("🔧 [Step 1] 生成金鑰...")
generate_keys(keys_dir)   # keys/private.pem & keys/public.pem

# === 2️⃣ 建立一個測試用的 license.json ===
license_path = "license.json"
if not os.path.exists(license_path):
    print("📝 建立 license.json...")
    sample_license = {
        "macs": ["aa:bb:cc:dd:ee:ff", "11:22:33:44:55:66"],
        "expires": "2025-12-31",
        "services": ["app", "db", "worker"],
        "signature": ""  # 先空著，簽名時會自動填上
    }
    import json
    with open(license_path, "w") as f:
        json.dump(sample_license, f, indent=2)

# === 3️⃣ 簽署 license.json ===
print("✍️ [Step 2] 簽署 License...")
sign_license(license_path, os.path.join(keys_dir, "private.pem"))

# === 4️⃣ 驗證 license.json ===
print("✅ [Step 3] 驗證 License...")
try:
    verify_license(
        license_path=license_path,
        public_key_path=os.path.join(keys_dir, "public.pem"),
        service_name="app",
        host_mac="aa:bb:cc:dd:ee:ff"
    )
    print("🎉 驗證成功，授權通過！")
except Exception as e:
    print("❌ 驗證失敗:", e)

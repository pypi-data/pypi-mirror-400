import os
import sys

sys.path.append(os.getcwd())
from license_tool.key.verifier import verify_license
import json

LICENSE_FILE = os.path.join('example', 'license_out.json')      # 授權檔路徑
PUBKEY_FILE = os.path.join('keys', 'public.pem')        # 公鑰檔路徑
MACINFO_FILE = "/etc/macinfo/macaddr"       # MAC 列表檔案


def normalize_mac(raw_mac: str) -> str:
    """將 C8D9D219FA2C 轉換成 C8:D9:D2:19:FA:2C"""
    raw_mac = raw_mac.strip().upper()  # 去除換行、統一大寫
    return ":".join([raw_mac[i:i+2] for i in range(0, len(raw_mac), 2)])

def check_license():
    # 讀取 macaddr 檔案
    try:
        with open(MACINFO_FILE) as f:
            mac_list = [normalize_mac(line) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ 找不到 {MACINFO_FILE}")
        return False

    print(f"📋 從 {MACINFO_FILE} 讀取到 {len(mac_list)} 個 MAC：")
    for mac in mac_list:
        print(f" - {mac}")

    # 逐一嘗試驗證，只要一個通過就合法
    for mac in mac_list:
        try:
            verify_license(
                license_path=LICENSE_FILE,
                public_key_path=PUBKEY_FILE,
                host_mac=mac
            )
            print(f"✅ 授權成功，合法 MAC：{mac}")
            return True   # 只要一個成功就結束
        except Exception as e:
            print(f"❌ 驗證失敗 ({mac}): {e}")

    print("🚫 所有 MAC 都驗證失敗，授權不合法！")
    return False

if __name__ == "__main__":
    if check_license():
        print("🎉 ✅ License 驗證通過！")
    else:
        print("❌ License 驗證失敗！")

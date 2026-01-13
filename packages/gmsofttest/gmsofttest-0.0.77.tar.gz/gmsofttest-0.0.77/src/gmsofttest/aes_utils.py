import base64
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AESUtils:
    """AES对称加密工具类，兼容ECB和CBC模式"""

    CHARSETNAME = "utf-8"

    def __init__(self, key=None):
        """
        初始化AES工具类

        :param key: 密钥字符串，如果不提供则使用默认密钥
        """
        self.default_key = "OnlineBidInfo123" if key is None else key

    def _pad_key(self, key):
        """
        确保密钥长度符合AES要求（16, 24, 32字节）

        :param key: 原始密钥
        :return: 填充后的密钥
        """
        key_bytes = key.encode(self.CHARSETNAME)
        # 如果密钥长度不足，使用PKCS7填充
        if len(key_bytes) not in [16, 24, 32]:
            padder = padding.PKCS7(128).padder()
            padded_key = padder.update(key_bytes) + padder.finalize()
            # 截取到最接近的合法长度
            key_length = 32 if len(padded_key) >= 32 else 24 if len(padded_key) >= 24 else 16
            return padded_key[:key_length]
        return key_bytes

    def encrypt_se_code(self, plain_text, key=None):
        """
        ECB模式加密（对应Java中的encryptSeCode方法）

        :param plain_text: 明文
        :param key: 密钥，使用None则用默认密钥
        :return: Base64编码的密文
        """
        try:
            # 使用提供的密钥或默认密钥
            current_key = key if key else self.default_key
            key_bytes = self._pad_key(current_key)

            # 创建AES ECB模式加密器
            cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=default_backend())
            encryptor = cipher.encryptor()

            # 对明文进行PKCS7填充
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plain_text.encode(self.CHARSETNAME)) + padder.finalize()

            # 加密并进行Base64编码
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            return base64.b64encode(encrypted).decode(self.CHARSETNAME)

        except Exception as e:
            logger.error(f"加密出错: {str(e)}")
            return "加密出错"

    def decrypt_se_code(self, encrypted_text, key=None):
        """
        ECB模式解密

        :param encrypted_text: Base64编码的密文
        :param key: 密钥，使用None则用默认密钥
        :return: 明文
        """
        try:
            current_key = key if key else self.default_key
            key_bytes = self._pad_key(current_key)

            # 创建AES ECB模式解密器
            cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=default_backend())
            decryptor = cipher.decryptor()

            # Base64解码后解密
            encrypted_data = base64.b64decode(encrypted_text)
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

            # 去除PKCS7填充
            unpadder = padding.PKCS7(128).unpadder()
            decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

            return decrypted.decode(self.CHARSETNAME)

        except Exception as e:
            logger.error(f"解密出错: {str(e)}")
            return "解密出错"

    def generate_secret_key(self, password=None, salt=None):
        """
        基于密码生成密钥（对应Java中的getSecretKey方法）

        :param password: 密码字符串
        :param salt: 盐值，None则随机生成
        :return: 生成的密钥bytes
        """
        try:
            password = password if password else self.default_key
            salt = salt if salt else os.urandom(16)

            # 使用PBKDF2HMAC算法从密码派生密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )

            key = kdf.derive(password.encode(self.CHARSETNAME))
            return key

        except Exception as e:
            logger.error(f"密钥生成失败: {str(e)}")
            return None


# 测试代码
if __name__ == "__main__":
    # 创建工具类实例
    aes_utils = AESUtils()

    # 测试ECB加密解密
    import time

    plain_text = f"xLNR9vA82hxqWJswyvkCzMpGZm4NhoVz@{int(time.time() * 1000)}"
    key = "xLNR9vA82hxqWJswyvkCzMpGZm4NhoVz"

    encrypted = aes_utils.encrypt_se_code(plain_text, key)
    print(f"加密结果: {encrypted}")

    decrypted = aes_utils.decrypt_se_code(encrypted, key)
    print(f"解密结果: {decrypted}")

    # 测试密钥生成
    secret_key = aes_utils.generate_secret_key()
    print(f"生成的密钥(Base64): {base64.b64encode(secret_key).decode()}")

    # 测试字符串包含
    print("jyd/222.html".__contains__("222"))
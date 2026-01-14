import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import serialization

RAW_DATA_FORMAT = "apiKey=%s&timestamp=%s&nonce=%s"


def load_private_key(private_key_str: str, key_algorithm: str):
    """
    对应Java的loadPrivateKey方法：从Base64编码字符串加载私钥（解密逻辑需补充）
    
    :param private_key_str: 数据库存储的Base64编码私钥字符串（PKCS8格式）
    :param key_algorithm: 密钥算法（如"RSA"）
    :return: 私钥对象（如RSAPrivateKey）
    :raises GeneralSecurityException: 密钥加载失败时抛出（模拟Java异常）
    """
    try:
        # 1. Base64解码私钥字节（对应Java的Base64.getDecoder().decode）
        encrypted_bytes = base64.b64decode(private_key_str)

        # 2. 实际项目中需在此处添加解密逻辑（与Java注释对应）
        # 示例：decrypted_bytes = decrypt(encrypted_bytes, secret_key)
        decrypted_bytes = encrypted_bytes  # 临时占位，需替换为实际解密逻辑


        # 4. 从DER格式加载私钥（对应Java的PKCS8EncodedKeySpec）
        private_key = serialization.load_der_private_key(
            data=decrypted_bytes,
            password=None,  # 若私钥加密，需传入密码字节（如b"password"）
        )

        return private_key
    
    except Exception as e:
        # 模拟Java的GeneralSecurityException
        raise Exception(f"私钥加载失败: {str(e)}")  # 实际可自定义异常类    
    

# -------------------------- 3. SHA256withRSA 签名工具函数--------------------------
def generate_rsa_signature(private_key_pem: str, api_key: str, timestamp: str, nonce: str) -> str:
    """
    生成SHA256withRSA签名（对应Java的SHA256withRSA算法）
    :param private_key_pem: PEM格式私钥（带-----BEGIN PRIVATE KEY-----头尾）
    :param api_key: 接口密钥
    :param timestamp: 时间戳（毫秒级字符串，与请求头一致）
    :param nonce: 随机字符串（与请求头一致）
    :return: Base64编码后的签名字符串
    :raises InvalidKey: 私钥格式错误或无效
    :raises Exception: 签名过程异常
    """
    # 1. 拼接签名原文（必须与服务端约定一致，此处用"&"分隔）
    sign_source = RAW_DATA_FORMAT % (api_key, timestamp, nonce)
    sign_source = sign_source.encode("UTF-8")
    try:
        # 2. 加载PEM私钥（无密码，若有密码需补充password参数）
        private_key = load_private_key(private_key_str=private_key_pem,key_algorithm="RSA")
        # 3. 执行RSA签名（SHA256哈希 + PKCS#1 v1.5填充，与Java SHA256withRSA兼容）
        signature_bytes = private_key.sign(
            data=sign_source,
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA256()
        )
        # 4. 签名结果Base64编码（便于HTTP头传输）
        return base64.b64encode(signature_bytes).decode("UTF-8")
    except InvalidKey as e:
        raise InvalidKey(f"私钥无效或格式错误: {str(e)}") from e
    except Exception as e:
        raise Exception(f"签名生成失败: {str(e)}") from e
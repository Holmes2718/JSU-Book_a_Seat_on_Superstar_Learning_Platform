from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from hashlib import md5
import random
from uuid import uuid1
import hashlib


def AES_Encrypt(data):
    key = b"u2oh6Vu^HWe4_AES"  # Convert to bytes
    iv = b"u2oh6Vu^HWe4_AES"  # Convert to bytes
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    enctext = base64.b64encode(encrypted_data).decode("utf-8")
    return enctext


def resort(submit_info):
    return {key: submit_info[key] for key in sorted(submit_info.keys())}


def enc(submit_info):
    add = lambda x, y: x + y
    processed_info = resort(submit_info)
    needed = [
        add(add("[", key), "=" + value) + "]" for key, value in processed_info.items()
    ]
    pattern = "%sd`~7^/>N4!Q#){''"
    needed.append(add("[", pattern) + "]")
    seq = "".join(needed)
    return md5(seq.encode("utf-8")).hexdigest()


def generate_captcha_key(timestamp: int):
    captcha_key = md5((str(timestamp) + str(uuid1())).encode("utf-8")).hexdigest()
    encoded_timestamp = (
        md5(
            (
                str(timestamp)
                + "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1"
                + "slide"
                + captcha_key
            ).encode("utf-8")
        ).hexdigest()
        + ":"
        + str(int(timestamp) + 0x493E0)
    )
    return [captcha_key, encoded_timestamp]


def sort_dict_by_keys(dictionary):
    """将字典按键排序并返回新字典"""
    sorted_keys = sorted(dictionary.keys())
    sorted_dict = {key: dictionary[key] for key in sorted_keys}
    return sorted_dict


def verify_param(params, algorithm_value):
    """
    生成参数的MD5验证哈希值

    参数:
        params: 要验证的参数字典
        algorithm_value: 对应JavaScript中id为'submit_enc'的元素值

    返回:
        计算得到的MD5哈希字符串
    """
    # 对参数字典按键排序
    sorted_params = sort_dict_by_keys(params)

    # 构建哈希字符串列表
    hash_list = []

    # 遍历排序后的参数，构建格式为 [key=value] 的字符串
    for key, value in sorted_params.items():
        # 确保值转换为字符串，与JavaScript行为一致
        hash_list.append(f"[{key}={str(value)}]")

    # 添加algorithm值
    hash_list.append(f"[{algorithm_value}]")

    # 连接所有元素形成最终字符串
    hash_string = "".join(hash_list)

    # 计算MD5哈希值
    md5_hash = hashlib.md5(hash_string.encode("utf-8")).hexdigest()

    return md5_hash

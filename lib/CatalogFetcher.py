import json
from base64 import b64encode
from pathlib import Path

from lib.TableEncryptionService import TableEncryptionService

def find_game_config(game_path) -> None | bytes:
    pattern = bytes([
        0x47,
        0x61,
        0x6D,
        0x65,
        0x4D,
        0x61,
        0x69,
        0x6E,
        0x43,
        0x6F,
        0x6E,
        0x66,
        0x69,
        0x67,
        0x00,
        0x00,
        0x92,
        0x03,
        0x00,
        0x00,
    ])

    for config_file in Path(game_path).rglob('*'):
        if config_file.is_file():
            content = config_file.read_bytes()

            if pattern in content:
                start_index = content.index(pattern)
                data = content[start_index + len(pattern) :]
                return data[:-2]
    return None


def decrypt_game_config(data: bytes) -> str:
    encryption_service = TableEncryptionService()
    encoded_data = b64encode(data)

    game_config = encryption_service.create_key('GameMainConfig')
    server_data = encryption_service.create_key('ServerInfoDataUrl')

    decrypted_data = encryption_service.convert_string(encoded_data, game_config)
    loaded_data = json.loads(decrypted_data)

    decrypted_key = encryption_service.new_encrypt_string('ServerInfoDataUrl', server_data)
    decrypted_value = loaded_data[decrypted_key]
    return encryption_service.convert_string(decrypted_value, server_data)
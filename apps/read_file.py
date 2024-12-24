import hashlib
import os

import magic


def read_file(file_name: str) -> dict:
    mime = magic.Magic(mime=True)
    file = {"file_name": file_name, }
    if not os.path.exists(f'{file_name}'):
        raise FileNotFoundError(f'File {file_name} not found')
    else:
        with open(f'{file_name}', 'rb') as source:
            file.update({"file_data": source.read(),
                         "file_mime": mime.from_file(f'{file_name}'),
                         "file_md5": hashlib.md5(source.read()).hexdigest()})
    return file

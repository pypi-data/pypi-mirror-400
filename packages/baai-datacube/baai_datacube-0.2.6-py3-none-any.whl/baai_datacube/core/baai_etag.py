import hashlib


CHUNK_SIZE = 1024 * 1024 * 5


def etag_bytes(bytes_):
    hash_md5 = hashlib.md5()
    hash_md5.update(bytes_)
    return hash_md5.digest()


def etag_write(path, size):

    part_etags = []

    for idx, start_pos in enumerate(range(0, size, CHUNK_SIZE)):
        end_pos = min(start_pos + CHUNK_SIZE, size)

        with path.open("rb") as reader:
            reader.seek(start_pos)
            rbytes = reader.read(end_pos - start_pos)
            part_etags.append(etag_bytes(rbytes))

    combined_md5 = b''.join(part_etags)
    final_md5_hex = hashlib.md5(combined_md5).hexdigest()

    return final_md5_hex
SPLIT_TOKEN = '\n\u0000\uFFFF\uFFFE' # the most unused sybols pattern
VERSION_TOKEN = '$VERSION\x00\b\n'
DATA_TOKEN = '$DATA\x00\b\n'
METADATA_TOKEN = '$MTD\x00\b\n'

TEMPLATE = f'{SPLIT_TOKEN}{VERSION_TOKEN}:\n{METADATA_TOKEN}\n{DATA_TOKEN}'

def file(version, data, metadata = []):
    return (
        TEMPLATE
        .replace(VERSION_TOKEN, str(version))
        .replace(METADATA_TOKEN, str(metadata))
        .replace(DATA_TOKEN, str(data))
    )
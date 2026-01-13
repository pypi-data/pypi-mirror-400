import ast
import hashlib
from .templates import SPLIT_TOKEN, file
from .zip import makeRlezip, unzipRlezip, RLE_SPLIT_BYTE
from .diff_system import find_diff


RAWFILE_VER = 'RAW' # for versions with raw data
SYSTEM_VER = 'SYSTEM|' # start of system versions
HASH_ALGORITM = hashlib.sha3_512





def compile(versions: dict[str, str]):
    result = '' # file
    versions = versions.copy()
    try: # check RAW version data
        raw = versions[RAWFILE_VER] 
        result += file(RAWFILE_VER, makeRlezip(raw)[0].value, HASH_ALGORITM(str(versions).encode()).hexdigest()) # add raw version
        versions.pop(RAWFILE_VER)
    except KeyError:
        raise ValueError(f'Version {repr(RAWFILE_VER)} is not found. That version must be in file like a raw version.')
    last = raw # last data (for diff system)
    i = 0 # version index
    for version in versions.keys():
        data = versions[version] # get version data
        diff = find_diff(last, data)
        last = data # update last data
        rle = makeRlezip(str(diff))[0].value
        i += 1
        if i % 10 == 0: # system version: snapshot
            result += file(SYSTEM_VER+'snap@'+version, makeRlezip(data)[0].value, HASH_ALGORITM(str(rle).encode()).hexdigest())
        result += file(version, rle, HASH_ALGORITM(str(rle).encode()).hexdigest())
    return result


def pre_parse(five_file: str):
    versions = five_file.split(SPLIT_TOKEN)
    result = {}
    for file_version in versions[1:]: # index 0 - null
        split = file_version.split('\n')
        version = split[0][:-1] # get version
        metadata = split[1] # get metadata (hash of rle)
        rle = '\n'.join(split[2:]) # get rle-zipped data
        file = unzipRlezip((rle, RLE_SPLIT_BYTE)) # unzip data
        hash = HASH_ALGORITM(rle.encode()).hexdigest() # hash of rle
        if metadata != hash and version != RAWFILE_VER:  # verificate data
            print(f'Warning: data is invalid or defected')
        result[version] = [file, metadata]
    return result


def decompile(five_file: str):
    parsed = pre_parse(five_file) 
    RW = parsed[RAWFILE_VER][0] # get raw data
    RWMETA = parsed[RAWFILE_VER][1] # get hash of file
    result = {}
    last = RW # last data
    for version in parsed.keys():
        if not version.startswith(SYSTEM_VER):
            content = parsed[version][0] # get data of version
            if version != RAWFILE_VER and content not in ('', '(\'\', -1)'):
                reverse: str = content[::-1] # reverse of diff 
                # ('test', 1) -> )1 , 'tset'(
                diff = reverse[1:-1].split(',')
                diff_index = int(diff[0][::-1]) # find diff
                different = ast.literal_eval(','.join(reverse[1:-1].split(',')[1:])[::-1]) # eval diff
                ver_data = last[:diff_index]+different # create data from diff
                content = ver_data 
            elif content == '(\'\', -1)': # if version has no changes
                content = last
            result[version] = content 
            last = content
    if RWMETA != HASH_ALGORITM(str(result).encode()).hexdigest(): # if hashes of file is different
        print('!!! DATA IS DEFFECTED !!!')
    return result






if __name__ == '__main__':
    examples = [
        {RAWFILE_VER:'data1\ntest\t', 'test2':'data2'},
        {RAWFILE_VER:'data', 'test2':'data2'},
        {RAWFILE_VER:'data2', 'test2':'data2'},
        {RAWFILE_VER:'data2', 'test2':'data2', 'test3':'data', 'test4': '"""test"""\'\'\'', 'test5':'"""test"""6\'\'\''},
        {RAWFILE_VER:'1', '1':'2', '2':'3', '3':'4', '4':'5', '5':'6', '6':'7', '7':'8', '8':'9', '9':'10', '10':'11', '11':'12'},
        {RAWFILE_VER:'abc', '1': 'aXc', '2':'aaabbb'},
    ]
    for example in examples:
        compiled = compile(example)
        decompiled = decompile(compiled)
        print(compiled)
        print(example, decompiled, '\n')
        try: assert example == decompiled
        except:
            example_str = str(example)
            decompile_str = str(decompiled)
            for char in range(len(example_str)):
                print(char, decompile_str[char], example_str[char], example_str[char]==decompile_str[char])
    '''
{'RAW': 'data1\ntest\t', 'test2': 'data2'} {'RAW': 'data1\ntest\t', 'test2': 'data2'} 

{'RAW': 'data', 'test2': 'data2'} {'RAW': 'data', 'test2': 'data2'} 

{'RAW': 'data2', 'test2': 'data2'} {'RAW': 'data2', 'test2': 'data2'} 

{'RAW': 'data2', 'test2': 'data2', 'test3': 'data', 'test4': '"""test"""\'\'\'', 'test5': '"""test"""6\'\'\''} {'RAW': 'data2', 'test2': 'data2', 'test3': 'data', 'test4': '"""test"""\'\'\'', 'test5': '"""test"""6\'\'\''} 

{'RAW': 'abc', '1': 'aXc', '2': 'aaabbb'} {'RAW': 'abc', '1': 'aXc', '2': 'aaabbb'} 
    '''
import pickle




RLE_SPLIT_BYTE = '\uFFFF' # non character


class zip_algoritms:
    def __init__(self) -> None:pass

    class rle:
        def __init__(
            self, 
            val: str, 
            splitbyte: str = RLE_SPLIT_BYTE
        ) -> None:
            self.value = val
            self.raw = val
            self.splitbyte = splitbyte

        def compile(self):
            text = self.value
            result = ''; text += '\x00'; i = 0
            in_pattern = False
            pattern_start = 0
            while i < (len(text) - 1):
                curr = text[i:i+1]
                if curr == text[i+1]:
                    if not in_pattern: in_pattern = True; pattern_start = i
                else:
                    if curr == text[i-1]: in_pattern = False
                    else: pattern_start = i
                    length = i-pattern_start+1
                    if length == 1: result += curr + self.splitbyte
                    else: result += curr + str(length) + self.splitbyte
                i += 1
            self.value = result
            return self
            
        def decompile(self):
            text = self.value
            result = ''
            split = text.split(self.splitbyte)
            i = 0
            while i < (len(split) - 1):
                line = split[i]
                if line != '':
                    if not line[1:].isdigit():
                        result += line[0]
                    else:
                        element = line[0]
                        iters = int(line[1:])
                        result += str(element * iters)
                i += 1
            self.value = result
            return self


def makeRlezip(text: str) -> tuple[zip_algoritms.rle, str]:
    return zip_algoritms().rle(text).compile(), RLE_SPLIT_BYTE

def readRlezip(rlezipTuple: tuple) -> str:
    return rlezipTuple[0].value

def unzipRlezip(rlezipTuple: tuple) -> str:
    if isinstance(rlezipTuple[0], str):
        return zip_algoritms().rle(rlezipTuple[0], rlezipTuple[1]).decompile().value
    return zip_algoritms().rle(readRlezip(rlezipTuple)).decompile().value




if __name__ == '__main__':
    example = 'aaaa1111111111111111     '
    zip = makeRlezip(example)
    print(readRlezip(zip))
    print(f"'{unzipRlezip(zip)}'")
    print(unzipRlezip(zip) == example)
    with open('hex.txt', 'r') as file: 
        content = file.read()
    zip = makeRlezip(content)
    print(len(content), len(readRlezip(zip)))
    print(unzipRlezip(zip) == content)
    '''
a4￿116￿
'aaaa1111111111111111'
True
21963 5850
True
    '''
def find_diff(text1, text2):
    text1, text2 = str(text1), str(text2)
    if len(text1) < len(text2):
        diff_index = len(text1)
        index = 0
        for char in text1:
            if text2[index] != char:
                diff_index = index
                break
            index += 1
        return text2[diff_index:], diff_index
    elif len(text1) > len(text2):
        diff_index = len(text2)
        index = 0
        for char in text2:
            if text1[index] != char:
                diff_index = index
                break
            index += 1
        return text2[diff_index:], diff_index
    else:
        diff_index = -1
        index = 0
        for char in text1:
            if text2[index] != char:
                diff_index = index
                break
            index += 1
        if diff_index != -1:
            return text2[diff_index:], diff_index
        else:
            return '', diff_index

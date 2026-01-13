def binary_recursive_merge_encryption(s):
    try:
        if len(s) <= 2:
            return s
        else:
            left = []
            right = []
            for i in range(len(s)):
                if i % 2 == 0:
                    left.append(s[i])
                else:
                    right.append(s[i])
            return brme("".join(left)) + brme("".join(right))
    except TypeError:
        s = str(s)
        return brme(s)


BRME = brme = binary_recursive_merge_encryption

if __name__ == '__main__':
    print(binary_recursive_merge_encryption(r"qwertyuiop[]\asdfghjkl;'zxcvbnm,./!~@#$%^&*()_+{}|:<>?`1234567890-="
                                            r'QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?·！￥……（）——【】：；“”《》，。？、 '))

import random as r


def shuffle_encryption(s):
    r.shuffle(s)
    return s
    

se = SE = shuffle_encryption

if __name__ == "__main__":
    print(shuffle_encryption("sdlkfjl"))

# 加密（整合）

## 加密方法
1. BinaryRecursiveMergeEncryption
2. ShuffleEncryption

### BinaryRecursiveMergeEncryption（二分归并加密）
* abcdefg => 
* aceg => 
* ae
* cg
* bdf =>
* bf
* d
* => aecgbfd

#### 调用方法
```
from LscEncryption import BRME

"""
BRME/binary_recursive_merge_encryption/brme
"""

print(brme("sdgj")) # => sgdj
```

### ShuffleEncryption（随机加密）
* abcdefg =>
* abcdegf
* abcdfeg
* abcdfge
* ……

#### 调用方法
```
from LscEncryption import SE

"""
se/SE/shuffle_encryption
"""

print(se("sdgj"))
```
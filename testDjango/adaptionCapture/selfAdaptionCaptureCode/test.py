# coding=utf-8
fatherNumList = [0, 2, 52, 68, 78, 93, 131, 201]
numList = [2, 52, 68, 78, 93, 131, 201]
_numList = []
print fatherNumList,numList
for num in numList:
    if num in fatherNumList:
        _numList.append(num)
for num in _numList:
    numList.remove(num)
print numList

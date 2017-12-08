dic = []
with open('data/dic2.txt', 'r', encoding='gbk') as f:
    for line in f:
        for phrase in line.split(','):
            for word in phrase.split(' '):
                if len(word) != 0:
                    dic.append(word.strip())
print(len(dic))
# print(dic)
dic_remove_dup = []
for word in dic:
    if word not in dic_remove_dup:
        dic_remove_dup.append(word)
# [dic_remove_dup.append(i) for i in dic not in dic_remove_dup]
print(len(dic_remove_dup))
# print(dic_remove_dup)
file_object = open('data/dic.txt', 'w', encoding='utf-8')
for word in dic_remove_dup:
    if len(word) > 2:
        file_object.write(word+" 1000")
        file_object.write('\n')
file_object.close()
print('done')

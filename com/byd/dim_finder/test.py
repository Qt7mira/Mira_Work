d = [{
    'content': '按键所实现的做工还行',
    'content_cut': ['按键', '所', '实现', '的', '做工', '还', '行'],
    'dim': '按键/旋钮整体评价',
    'dim_desc': "{'按键'}",
    'dim_index': 392
}, {
    'content': '按键所实现的做工还行',
    'content_cut': ['按键', '所', '实现', '的', '做工', '还', '行'],
    'dim': '按键/旋钮整体评价',
    'dim_desc': "{'做工'}",
    'dim_index': 392
}]

aaa = {
    'content': '按键所实现的做工还行',
    'content_cut': ['按键', '所', '实现', '的', '做工', '还', '行'],
    'dim_desc': "{'按键'}{'做工'}",
    'dim': '按键/旋钮做工',
    'dim_index': 393
}

bbb = {
    'content': '按键所实现的做工还行',
    'content_cut': ['按键', '所', '实现', '的', '做工', '还', '行'],
    'dim_desc': "{'自动大灯'}",
    'dim': '按键/旋钮做工',
    'dim_index': 393
}


def append_mo_gai(l, d):
    if len(l) == 0:
        l.append(d)
        return l
    s = [i['dim_desc'] for i in l]
    s1 = d['dim_desc']
    res = []
    for i in range(len(s)-1, -1, -1):
        if str(s1).__contains__(str(s[i])) and len(s1) > len(s[i]):
            res.append(i)

    if len(res) > 0:
        for i in res:
            l.remove(l[i])
        l.append(d)
        return l

    for i in range(len(s) - 1, -1, -1):
        if str(s[i]).__contains__(str(s1)) and len(s[i]) > len(s1):
            print("c2:" + s1)
            return l

    l.append(d)
    return l

# print(append_mo_gai(d, aaa))
print(append_mo_gai(d, bbb))


asd = "{'按键'}"

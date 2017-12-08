import json
import re
import base64

# with open('data/bbbb', 'r', encoding='utf-8') as f:
#     json_data = json.load(f)
# print(json_data)
jsonstr = ""
with open('data/bbbb', 'r', encoding='utf-8') as f:
    for line in f:
        jsonstr += line

print(jsonstr)
# a = base64.urlsafe_b64encode(bytes(jsonstr, encoding="utf-8"))
a = base64.urlsafe_b64decode(jsonstr).decode()
print(a)
print(type(a))
b = a.replace('\\\\\"', '\\\"')
print(b)
print(type(b))
c = json.loads(b)
print(c)


# def read_data_from_json(type_value):
#     words_set = []
#     for line in json_data['subwords']['subwords']:
#         if line['type'] == type_value:
#             phrase = line['name']
#             word_sub_set = []
#             if phrase.__contains__('"'):
#                 s = re.findall('"(.+?)"', phrase)
#                 if len(s) == 1:
#                     s_real = str(s)[2: len(str(s)) - 2].replace(' ', '')
#                     word_sub_set.append(s_real)
#                 elif len(s) > 1:
#                     for i in s:
#                         s_real = i[1:len(i) - 1].replace(' ', '')
#                         word_sub_set.append(s_real)
#
#                 s2 = phrase.replace('"' + s_real + '"', '').strip()
#                 if len(s2) != 0:
#                     for w in s2.split(','):
#                         for w1 in w.split(' '):
#                             word_sub_set.append(w1)
#             else:
#                 for w in phrase.split(' '):
#                     word_sub_set.append(w)
#             if word_sub_set not in words_set:
#                 words_set.append(word_sub_set)
#     return words_set
#
# title = json_data["title"]
# txt = json_data['txt']
#
# core = read_data_from_json('1')
# inc = read_data_from_json('2')
# not_inc = read_data_from_json('3')
# print(str(core))
# print(str(inc))
# print(str(not_inc))
# # print(dicList["txt"])

import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter


def str_dp2(str1):
    return len(str(str1).strip().replace(" ", ""))

content = pd.read_excel("C:/Users/Administrator/Desktop/autohome_bbs_2017-08-07.xlsx")['G']
content_len = pd.Series(content).apply(str_dp2)
print(content_len[0:10])

x = []
y = []
count = 0
for k, v in Counter(content_len).items():
    if k < 200:
        x.append(k)
        y.append(v)
        count += v
        print(str(k) + "\t" + str(v))

print(" aaaa   "+str(count))
plt.bar(x, y, 0.4, color="blue")
plt.xlabel("Sentences Length")
plt.ylabel("Count")
plt.title("Sentences Length Statistics")
plt.show()

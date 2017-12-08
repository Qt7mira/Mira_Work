import xlrd
import xlwt
import requests
import json

datafile = xlrd.open_workbook('non_im.xlsx')
table = datafile.sheet_by_name('Sheet1')
num_rows = table.nrows

out_xl = xlwt.Workbook(encoding='utf-8')
table_out = out_xl.add_sheet('Sheet1', cell_overwrite_ok=True)

out_xl2 = xlwt.Workbook(encoding='utf-8')
table_out2 = out_xl2.add_sheet('Sheet1', cell_overwrite_ok=True)

url = r'http://60.205.168.205:17779/v1.0/ad_bayes_predict'


def load_data():
    data_list = []
    for row in range(1, num_rows):
        data = {}
        data['a'] = table.cell(row, 0).value
        data['b'] = table.cell(row, 1).value
        data['c'] = table.cell(row, 2).value
        data['d'] = table.cell(row, 3).value
        data['e'] = table.cell(row, 4).value
        data['f'] = table.cell(row, 5).value
        data['g'] = table.cell(row, 6).value
        data['h'] = table.cell(row, 7).value
        data['i'] = table.cell(row, 8).value
        data['j'] = table.cell(row, 9).value
        data['k'] = table.cell(row, 10).value
        data['l'] = table.cell(row, 11).value
        data['m'] = table.cell(row, 12).value
        data['n'] = table.cell(row, 13).value
        data['to_predict'] = {'txt': '', 'title': data['b']}
        data_list.append(data)
    return data_list

data_list = load_data()
print(len(data_list))

ads = []
news = []

for i in range(0, len(data_list)):
    res = eval(json.loads(requests.post(url, data=data_list[i]['to_predict']).text))
    if res["type"] == 'result' and res["result"] == 1:
        ads.append(data_list[i])
    else:
        news.append(data_list[i])

row0 = ['网站', '文章标题', '来源', '类型', '时间', 'URL', '属性', '二级分类', '作者', '点击', '评论', '文章字数', '关键词', '类别']
for i in range(len(row0)):
    table_out.write(0, i, row0[i])
row_out = 1
for i in range(0, len(news)):
    table_out.write(row_out, 0, news[i]['a'])
    table_out.write(row_out, 1, news[i]['b'])
    table_out.write(row_out, 2, news[i]['c'])
    table_out.write(row_out, 3, news[i]['d'])
    table_out.write(row_out, 4, news[i]['e'])
    table_out.write(row_out, 5, news[i]['f'])
    table_out.write(row_out, 6, news[i]['g'])
    table_out.write(row_out, 7, news[i]['h'])
    table_out.write(row_out, 8, news[i]['i'])
    table_out.write(row_out, 9, news[i]['j'])
    table_out.write(row_out, 10, news[i]['k'])
    table_out.write(row_out, 11, news[i]['l'])
    table_out.write(row_out, 12, news[i]['m'])
    table_out.write(row_out, 13, news[i]['n'])
    row_out += 1
out_xl.save('im_news.xls')

for i in range(len(row0)):
    table_out2.write(0, i, row0[i])
row_out2 = 1
for i in range(0, len(ads)):
    table_out2.write(row_out, 0, ads[i]['a'])
    table_out2.write(row_out, 1, ads[i]['b'])
    table_out2.write(row_out, 2, ads[i]['c'])
    table_out2.write(row_out, 3, ads[i]['d'])
    table_out2.write(row_out, 4, ads[i]['e'])
    table_out2.write(row_out, 5, ads[i]['f'])
    table_out2.write(row_out, 6, ads[i]['g'])
    table_out2.write(row_out, 7, ads[i]['h'])
    table_out2.write(row_out, 8, ads[i]['i'])
    table_out2.write(row_out, 9, ads[i]['j'])
    table_out2.write(row_out, 10, ads[i]['k'])
    table_out2.write(row_out, 11, ads[i]['l'])
    table_out2.write(row_out, 12, ads[i]['m'])
    table_out2.write(row_out, 13, ads[i]['n'])
    row_out2 += 1
out_xl2.save('im_ads.xls')

print(len(news))
print(len(ads))

# -*- coding: utf-8 -*-
'''
User Name: wendong@skyguard.com.cn
Date Time: 12/21/20 5:58 PM
File Name: /
Version: /
'''

import matplotlib.pyplot as plt
import jieba
from wordcloud import wordcloud

# 1.read word
test = open("test.txt", 'r', encoding='utf-8').read()
print(test)


# 2.seperate word
cut_test = jieba.cut(test)

# 3. merge with space
res = ' '.join(cut_test)

# 4.generate word cloud
wc = wordcloud.WordCloud(
    font_path='迷你简太极.ttf',
    background_color='white',  # 背景颜色
    width=1000,
    height=600,
    max_font_size=50,  # 字体大小
    min_font_size=10,
    mask=plt.imread('cloud.jpg'),  # 背景图片
    max_words=1000
)

wc.generate(res)

wc.to_file('wc_res.png')

# 5.display image
plt.figure('wc_res.png')  # 图片显示的名字
plt.imshow(wc)
plt.axis('off')  # 关闭坐标
plt.show()
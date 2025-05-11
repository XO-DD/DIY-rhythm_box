# 自由自制节奏盒子
只需添加data文件就可以
目前还有很多严重的bug,希望大家帮我改一改
文件树如下
```file
main.py 主程序
data
 bg.png 背景图450x600
 k.png 框架450x600也可以当成背景图下半部分
 c.txt  用来存储数量和角色名字，假设只有1个，叫a
 done.png 空角色
 again.png 重制按钮,目前还加载不出来
 a 存储角色的文件夹
  music1.wav 前半段的音频
  music2.wav 后半段的音频
  logo.png 图标32x32
  pngs.json 图片的数量和顺序
  pngs
   1.png
   2.png
   ......
```
```
pngs.json例子
{
    "c":10,
    "frames":[
        {
            "name":"1.png",
            "time":3
        },
        {
            "name":"2.png",
            "time":3
        }
    ]
}
```
```
c.txt例子
a
b
c
```

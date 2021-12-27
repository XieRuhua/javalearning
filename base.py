# -*- coding: utf-8 -*-

import os

# 需要忽略的配置文件
omitFiles = [
    ".git",  # git文件夹
    "base.py",  # 生成目录的python脚本
    "_dirs.md", "README.md", "README.md.bak",  # 目录文件及备份文件
    ".nojekyll", "index.html", "_sidebar.md", "my404.md"  # docsify相关配置文件
]


def create_dir_list(file_dir):
    a = 0

    '''
    root:当前路径
    dirs:当前路径下所有子目录
    files:当前路径下所有非目录子文件
    '''
    for root, dirs, files in os.walk(file_dir):
        # 需要写入的目录数组
        dirsArr = []

        # 首页固定的描述
        if root == "./":
            ## 获取备份文件中的数据（头文件）
            f = open(r"./README.md.bak", 'r', encoding='UTF-8')
            dirsArr.append(f.read())

        # 忽略执行的文件
        for omitFile in omitFiles:
            if omitFile in files:
                files.remove(omitFile)
            if omitFile in dirs:
                dirs.remove(omitFile)

        # 组装需要循环的内容
        for dirStr in dirs + files:
            if root == "./":
                dirsArr.append("#### [" + dirStr + "](./" + dirStr + "/_dirs.md)")
            elif ".md" in dirStr :
                dirsArr.append("#### [" + dirStr.strip(".md") + "](" + root + "/" + dirStr + ")")
            elif ".png" in dirStr:
                # 脑图加载并居中
                dirsArr.append("<center> \n\n#### " + dirStr.strip(".png") + " 脑图\n![" + dirStr.strip(".png") + "](./" + dirStr + ")\n</center>")
            elif ".xmind" in dirStr:
                # 不加入xmind文件
                continue
            else:
                dirsArr.append("#### [" + dirStr + "](" + root + "/" + dirStr + "/_dirs.md)")

        # print("当前路径:", root)  # 当前路径
        dirFileName = "/_dirs.md"
        # 根路径
        if root == "./":
            dirFileName = "/README.md"
            # 末尾加上文档工具来源
            dirsArr.append("#\n#\n>文档工具docsify：[官方文档-中文](https://docsify.js.org/#/zh-cn/)")

        # 如果目录下没有文件（子目录和文件），则不生成_dir.md和侧边栏导航文件
        if len(dirsArr) > 0:
            # 生成目录
            file_create(root, dirFileName, dirsArr)
            # 生成docsify工具左边的导航栏 _sidebar
            file_create(root, "./_sidebar.md", dirsArr)


'''
在指定目录下创建文件并写入内容

path:路径
name:文件名
msgs:内容，数组形式（两个元素之间在方法中已换行）
'''
def file_create(path, name, msgs):
    full_path = path + name

    # 判断文件是否存在，存在就删除
    if os.path.exists(full_path):
        os.remove(full_path)

    # 创建文件；encoding='UTF-8' 处理中文乱码
    file = open(full_path, 'w', encoding='UTF-8')
    for msg in msgs:
        file.write("\n")  # 换行
        file.write(msg)  # 内容写入
    file.close()


if __name__ == "__main__":
    create_dir_list("./")
    print("生成完毕")

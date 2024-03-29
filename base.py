# -*- coding: utf-8 -*-

import os
import time
import math

# 需要忽略的配置文件/目录
omitFiles = [
    ".idea",  # idea文件夹
    ".git",  # git文件夹
    "base.py",  # 生成目录的python脚本
    "_dirs.md", "README.md", "README.md.bak",  # 目录文件及备份文件
    ".nojekyll", "index.html", "_sidebar.md", "my404.md",  # docsify相关配置文件
    "startDocsify.bat",  # windows上的docsify启动预览脚本
    "createDirectory.bat",  # windows上的python创建目录的脚本
]


def create_dir_list(file_dir):
    # 计算工作到现在一共有多少个10天（计划10天写一篇笔记）
    day1 = time.strptime("2017-02-20", '%Y-%m-%d')
    day_num = (time.time() - int(time.mktime(day1))) / (24 * 60 * 60)
    totalPlannotes = math.floor(day_num / 10)

    # 笔记总数计数
    count = 0
    # 根目录的拎出来单独生成
    rootDirsArr = []

    # 所有笔记文件名，用于排除掉一个文件出现在多个文件夹时的重复计数
    allFiles = []

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

        # 忽略执行的文件和文件夹
        for omitFile in omitFiles:
            if omitFile in files:
                files.remove(omitFile)
            if omitFile in dirs:
                dirs.remove(omitFile)

        # 组装需要循环的内容
        for dirStr in dirs + files:
            appendStr = ''
            if root == "./":
                appendStr = "[" + dirStr + "](./" + dirStr + "/_dirs.md)"
            elif ".md" in dirStr:
                appendStr = "[" + dirStr.strip(".md") + "](" + root + "/" + dirStr + ")"
                # 排除掉一个文件出现在多个文件夹时的重复计数
                if dirStr not in allFiles:
                    count += 1
                    allFiles.append(dirStr)
            elif ".png" in dirStr:
                # 脑图加载并居中
                appendStr = "<center> \n\n" + dirStr.strip(".png") + " 脑图\n![" + dirStr.strip(
                    ".png") + "](./" + dirStr + ")\n</center>"
            elif ".xmind" in dirStr:
                # 不加入xmind文件
                continue
            else:
                appendStr = "[" + dirStr + "](" + root + "/" + dirStr + "/_dirs.md)"

            # 根目录加目录标识
            if root == "./":
                appendStr = "#### "+appendStr
            dirsArr.append("\n" + appendStr)

            # 循环生成子目录下的子目录和文件
            for element, rootChild in enumerate(rootDirsArr):
                # 子一级
                if root in rootChild:
                    rootDirsArr.insert(element + 1, "   - "+appendStr)
                    break;
                # 子二级
                child2 = appendStr.split("/")[1].split("\\")
                if len(child2) == 2 and child2[0] in rootChild and child2[1] in rootChild and '脑图' not in rootChild:
                    rootDirsArr.insert(element + 1, "       - "+appendStr)
                    break;
                # 子三级
                child3 = appendStr.split("/")[1].split("\\")
                if len(child3) == 3 and child3[0] in rootChild and child3[1] in rootChild and child3[2] in rootChild and '脑图' not in rootChild:
                    rootDirsArr.insert(element + 1, "           - "+appendStr)
                    break;

        # 根路径
        if root == "./":
            rootDirsArr = dirsArr

        # 如果目录下没有文件（子目录和文件），则不生成_dir.md和侧边栏导航文件
        if len(dirsArr) > 0:
            # 生成docsify工具左边的导航栏 _sidebar
            file_create(root, "./_sidebar.md", dirsArr)
            if root != "./":
                # 根目录不用生成./_dirs.md主目录，根目录的目录文件为/README.md
                file_create(root, "./_dirs.md", dirsArr)

    # 根目录生成目录
    # 头部描述和内容目录之间加上笔记总数/应该完成的笔记总数（工作天数/10）以及自2017-02-20以来的工作天数
    rootDirsArr[0] = rootDirsArr[0] + "\n> 目前笔记总篇数：" + str(count) + " / <font size='2px' color='#ccc'>" + str(
        totalPlannotes) + "-" + str(math.floor(day_num)) + "</font>"
    # 根目录中间加上子目录和子目录的子文件

    # 根目录末尾加上文档工具来源
    rootDirsArr.append("#\n#\n>文档工具docsify：[官方文档-中文](https://docsify.js.org/#/zh-cn/)")
    file_create("./", "/README.md", rootDirsArr)


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

# XJ-Labelme

基于 [labelme](https://github.com/wkentaro/labelme) 的增强版图像标注工具。

## 新增功能

- 右键复制文件名：在文件列表右键可复制文件名或完整路径
- 删除标签文件后自动重新加载图片
- 修复了删除标签后图片不显示的 bug
- 修复了切换图片时跳转到第一张的 bug

## 安装

```bash
pip install xj-labelme
```

## 使用

```bash
# 启动图形界面
xj-labelme

# 或者使用原命令
labelme
```

## 开发安装

```bash
git clone https://github.com/your-username/xj-labelme.git
cd xj-labelme
pip install -e .
```

## 许可证

GPL-3.0

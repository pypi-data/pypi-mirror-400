"""图片网格浏览器组件"""
from __future__ import annotations

import json
import os
import os.path as osp
from typing import Callable

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class ImageCard(QtWidgets.QWidget):
    """图片卡片组件"""
    
    clicked = QtCore.pyqtSignal(str)  # 发送文件路径
    
    def __init__(self, filepath: str, has_annotation: bool, label_file_path: str | None = None, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.has_annotation = has_annotation
        self.label_file_path = label_file_path
        
        self.setFixedSize(200, 240)
        self.setCursor(Qt.PointingHandCursor)
        
        # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # 布局
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 缩略图标签
        self.thumbnail_label = QtWidgets.QLabel()
        self.thumbnail_label.setFixedSize(190, 190)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        layout.addWidget(self.thumbnail_label)
        
        # 底部信息栏
        info_layout = QtWidgets.QHBoxLayout()
        
        # 文件名
        filename = os.path.basename(filepath)
        self.name_label = QtWidgets.QLabel(filename)
        self.name_label.setToolTip(filepath)
        font_metrics = self.name_label.fontMetrics()
        elided_text = font_metrics.elidedText(filename, Qt.ElideMiddle, 150)
        self.name_label.setText(elided_text)
        info_layout.addWidget(self.name_label, 1)
        
        # 状态图标
        self.status_label = QtWidgets.QLabel()
        if has_annotation:
            self.status_label.setText("✓")
            self.status_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
            self.status_label.setToolTip("已标注")
        else:
            self.status_label.setText("○")
            self.status_label.setStyleSheet("color: #ccc; font-size: 16px;")
            self.status_label.setToolTip("未标注")
        info_layout.addWidget(self.status_label)
        
        layout.addLayout(info_layout)
        
        # 加载缩略图（异步）
        self._load_thumbnail()
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QtWidgets.QMenu(self)
        
        # 复制文件名
        copy_filename_action = menu.addAction("复制文件名")
        copy_filename_action.triggered.connect(self._copy_filename)
        
        # 复制完整路径
        copy_fullpath_action = menu.addAction("复制完整路径")
        copy_fullpath_action.triggered.connect(self._copy_fullpath)
        
        # 显示菜单
        menu.exec_(self.mapToGlobal(pos))
    
    def _copy_filename(self):
        """复制文件名到剪贴板"""
        filename = os.path.basename(self.filepath)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(filename)
    
    def _copy_fullpath(self):
        """复制完整路径到剪贴板"""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.filepath)
    
    def _load_thumbnail(self):
        """加载缩略图并绘制标注"""
        pixmap = QtGui.QPixmap(self.filepath)
        if pixmap.isNull():
            self.thumbnail_label.setText("加载失败")
            return
        
        # 如果有标注，绘制标注框
        if self.has_annotation and self.label_file_path and osp.exists(self.label_file_path):
            pixmap = self._draw_annotations(pixmap)
        
        # 缩放
        scaled_pixmap = pixmap.scaled(
            190, 190,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.thumbnail_label.setPixmap(scaled_pixmap)
    
    def _draw_annotations(self, pixmap: QtGui.QPixmap) -> QtGui.QPixmap:
        """在缩略图上绘制标注框"""
        try:
            # 读取标注文件
            with open(self.label_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            shapes = data.get('shapes', [])
            if not shapes:
                return pixmap
            
            # 创建画笔
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            # 设置画笔样式
            pen = QtGui.QPen(QtGui.QColor(0, 255, 0), 2)  # 绿色，2像素宽
            painter.setPen(pen)
            
            # 绘制每个形状
            for shape in shapes:
                points = shape.get('points', [])
                shape_type = shape.get('shape_type', 'polygon')
                
                if shape_type == 'rectangle' and len(points) == 2:
                    # 矩形
                    x1, y1 = points[0]
                    x2, y2 = points[1]
                    painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))
                elif shape_type == 'polygon' and len(points) >= 3:
                    # 多边形
                    qpoints = [QtCore.QPoint(int(p[0]), int(p[1])) for p in points]
                    painter.drawPolygon(*qpoints)
                elif shape_type == 'circle' and len(points) == 2:
                    # 圆形
                    center = points[0]
                    edge = points[1]
                    radius = ((edge[0] - center[0])**2 + (edge[1] - center[1])**2)**0.5
                    painter.drawEllipse(
                        QtCore.QPointF(center[0], center[1]),
                        radius, radius
                    )
            
            painter.end()
            return pixmap
            
        except Exception as e:
            # 如果读取或绘制失败，返回原图
            print(f"绘制标注失败: {e}")
            return pixmap
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.filepath)
        super().mousePressEvent(event)


class ImageGridViewer(QtWidgets.QWidget):
    """图片网格浏览器组件（嵌入式）"""
    
    imageClicked = QtCore.pyqtSignal(str)  # 图片被点击时发送信号
    
    CARD_WIDTH = 200  # 卡片宽度
    CARD_SPACING = 10  # 卡片间距
    
    def __init__(
        self, 
        image_list: list[str], 
        get_annotation_status: Callable[[str], bool],
        get_label_file_path: Callable[[str], str | None] = None,
        parent=None
    ):
        super().__init__(parent)
        self.image_list = image_list
        self.get_annotation_status = get_annotation_status
        self.get_label_file_path = get_label_file_path
        self._cached_cards = []  # 缓存卡片以便重新布局
        
        self._setup_ui()
        self._load_images()
    
    def _setup_ui(self):
        """设置界面"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 顶部工具栏
        toolbar = QtWidgets.QHBoxLayout()
        
        # 搜索框
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("搜索文件名...")
        self.search_box.textChanged.connect(self._filter_images)
        toolbar.addWidget(QtWidgets.QLabel("搜索:"))
        toolbar.addWidget(self.search_box, 1)
        
        # 过滤器
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["全部", "仅已标注", "仅未标注"])
        self.filter_combo.currentTextChanged.connect(self._filter_images)
        toolbar.addWidget(QtWidgets.QLabel("过滤:"))
        toolbar.addWidget(self.filter_combo)
        
        # 图片计数
        self.count_label = QtWidgets.QLabel()
        toolbar.addWidget(self.count_label)
        
        layout.addLayout(toolbar)
        
        # 滚动区域
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 网格容器
        self.grid_widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(self.CARD_SPACING)
        
        self.scroll_area.setWidget(self.grid_widget)
        layout.addWidget(self.scroll_area)
    
    def _calculate_columns(self) -> int:
        """根据当前宽度计算列数"""
        # 获取可用宽度（减去边距和滚动条宽度）
        available_width = self.scroll_area.viewport().width() - 20
        # 计算可以放下多少列（至少1列）
        columns = max(1, available_width // (self.CARD_WIDTH + self.CARD_SPACING))
        return columns
    
    def _load_images(self):
        """加载图片到网格"""
        self._clear_grid()
        
        # 应用过滤
        filtered_images = self._get_filtered_images()
        
        # 更新计数
        self.count_label.setText(f"共 {len(filtered_images)} 张图片")
        
        # 计算列数
        columns = self._calculate_columns()
        
        # 清空缓存
        self._cached_cards = []
        
        # 添加图片卡片
        for index, filepath in enumerate(filtered_images):
            has_annotation = self.get_annotation_status(filepath)
            label_file_path = self.get_label_file_path(filepath) if self.get_label_file_path else None
            card = ImageCard(filepath, has_annotation, label_file_path)
            card.clicked.connect(self.imageClicked.emit)
            
            row = index // columns
            col = index % columns
            self.grid_layout.addWidget(card, row, col)
            self._cached_cards.append((card, filepath))
        
        # 添加弹性空间
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)
        self.grid_layout.setColumnStretch(columns, 1)
    
    def resizeEvent(self, event):
        """窗口大小变化时重新布局"""
        super().resizeEvent(event)
        if self._cached_cards:
            self._relayout_cards()
    
    def _relayout_cards(self):
        """重新布局卡片"""
        # 计算新的列数
        new_columns = self._calculate_columns()
        
        # 重新排列卡片
        for index, (card, _) in enumerate(self._cached_cards):
            row = index // new_columns
            col = index % new_columns
            # 移除旧位置
            self.grid_layout.removeWidget(card)
            # 添加到新位置
            self.grid_layout.addWidget(card, row, col)
        
        # 更新弹性空间
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)
        self.grid_layout.setColumnStretch(new_columns, 1)
    
    def _clear_grid(self):
        """清空网格"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
    
    def _get_filtered_images(self) -> list[str]:
        """获取过滤后的图片列表"""
        filtered = self.image_list
        
        # 搜索过滤
        search_text = self.search_box.text().lower()
        if search_text:
            filtered = [f for f in filtered if search_text in os.path.basename(f).lower()]
        
        # 状态过滤
        filter_type = self.filter_combo.currentText()
        if filter_type == "仅已标注":
            filtered = [f for f in filtered if self.get_annotation_status(f)]
        elif filter_type == "仅未标注":
            filtered = [f for f in filtered if not self.get_annotation_status(f)]
        
        return filtered
    
    def _filter_images(self):
        """过滤图片"""
        self._load_images()
    
    def refresh(self):
        """刷新网格视图"""
        self._load_images()

import random
import sys
from threading import Thread
from typing import Tuple
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np


class GraphWidget(QWidget):
    def __init__(self, parent: QWidget = None, data: np.ndarray = None):
        super().__init__(parent)
        self.grabKeyboard()
        self.setMouseTracking(True)
        
        # Массив с данными
        self._source_data = data
        self._prepared_data = data.copy() if data is not None else None
        
        # Коэффициент масштабирования 
        self._scale_factor = 1
        # Шаг к-фа масштабирования
        self._scale_factor_step = 0.5
        self._ctrl_pressed = False
        
        # Минимальное расстояние между делениями
        self._min_dist_btw_divs = 20
        # Минимальное расстояние между текстом делений
        self._min_dist_btw_divs_text = 5
        # Размер линии деления
        self._div_line_size = (1, 5)
        # Переключение отрисовки текста координат на осях
        self._show_axis_div_text = True
        
        # Для перемещения графика мышью
        self._lmb_pressed = False
        self._offset_x = 0
        self._offset_y = 0
        self._start_offset_click_pos = None
        
        # Включает отрисовку точек
        self._is_show_points = False
        
        # Переключение округления числа
        self._is_float_round = True
        # Кол-во знаков после запятой
        self._digits_after_comma = 3
        # СКМ нажата?
        self._mmb_pressed = False
    
    def _restore_painter_props(func):
        def wrapper(self, qp: QPainter, *args, **kwargs):
            # Сохраняем предыдущий цвет и шрифт
            old_pen = qp.pen()
            old_font = qp.font()
            # Вызываем функцию отрисовки
            func(self, qp, *args, *kwargs)
            # Возвращаем предыдущий цвет и шрифт
            qp.setPen(old_pen)
            qp.setFont(old_font)
        return wrapper
              
    @_restore_painter_props
    def _draw_cursor_pos_at_graph(self, qp: QPainter):
        if not self._mmb_pressed:
            return
        ocx, ocy = self.get_offset_axis_center()
        pos = self.mapFromGlobal(self.cursor().pos())
        x = (pos.x() - ocx) / self._scale_factor
        y = (pos.y() - ocy) / self._scale_factor
        dadp = self._digits_after_comma
        text = f'%.{dadp}f, %.{dadp}f'
        text = text % (x, -y)
        
        fm = QFontMetrics(qp.font())
        text_size = QSize(fm.width(text, len(text)), fm.height())
        
        qp.setBrush(QColor(30, 30, 30))
        qp.drawRect(QRect(pos - QPoint(5, 5) + QPoint(15, 30), text_size + QSize(10, 15)))
        qp.setPen(QColor(220, 220, 220))
        qp.drawText(pos + QPoint(15, 45), text)
        
    @_restore_painter_props
    def _draw_points_of_graph(self, qp: QPainter):
        if not self._is_show_points:
            return
        ocx, ocy = self.get_offset_axis_center()
        qp.setPen(QPen())
        qp.setBrush(QBrush(Qt.GlobalColor.red))
        for point in [QPointF(ocx + pos[1], ocy - pos[0]) for pos in self._prepared_data]:
            qp.drawEllipse(point, 2.5, 2.5)
        # qp.drawPoints()

    @_restore_painter_props
    def _draw_graph_properties_text(self, qp: QPainter):
        step = 15
        x = 5
        c_pos = self.mapFromGlobal(self.cursor().pos())
        values = (f'Scale: {self._scale_factor}',
                  f'LMB Pressed: {self._lmb_pressed}',
                  f'MMB Pressed: {self._mmb_pressed}',
                  f'Show points (P): {self._is_show_points}',
                  f'Show axis div text (T): {self._show_axis_div_text}',
                  f'Off-center axis: {self.get_offset_axis_center()}',
                  f'Center: {self.get_center()}',
                  f'Max X-value in data: {self._source_data[:, 1::2].max()}',
                  f'Min X-value in data: {self._source_data[:, 1::2].min()}',
                  f'Max Y-value in data: {self._source_data[:, ::2].max()}',
                  f'Min Y-value in data: {self._source_data[:, ::2].min()}',
                  f'Cursor pos: {max(c_pos.x(), 0), max(c_pos.y(), 0)}')
        
        qp.setPen(Qt.GlobalColor.gray)
        
        # Рисуем текст со свойствами графика
        for i, text in enumerate(values, 1):
            qp.drawText(QPoint(x, step * i), text)
        
    @_restore_painter_props
    def _draw_axis(self, qp: QPainter):
        qp.setPen(Qt.GlobalColor.white)
        
        # Отрисовка осей
        cx, cy = self.get_offset_axis_center()
        # X-axis
        qp.drawLine(0, cy, self.width(), cy)
        self._draw_x_axis_divs(qp)
        # Y-axis
        qp.drawLine(cx, 0, cx, self.height())
        self._draw_y_axis_divs(qp)
    
    @_restore_painter_props
    def _draw_axis_div_text(self, qp: QPainter):
        # Рисуем координаты
        if self._show_axis_div_text:
            self._draw_x_axis_divs_text(qp)
            self._draw_y_axis_divs_text(qp)
    
    @_restore_painter_props
    def _draw_x_axis_divs(self, qp: QPainter):
        qp.setPen(Qt.GlobalColor.white)
        f = QFont('', 7)
        qp.setFont(f)
        
        ocx, ocy = self.get_offset_axis_center()
        
        for x in np.arange(ocx, 0, -self._min_dist_btw_divs * self._scale_factor):
            qp.drawLine(QLineF(x, ocy - self._div_line_size[1], x, ocy + self._div_line_size[1]))
            
        for x in np.arange(ocx, self.width(), self._min_dist_btw_divs * self._scale_factor):
            qp.drawLine(QLineF(x, ocy - self._div_line_size[1], x, ocy + self._div_line_size[1]))
            
    @_restore_painter_props
    def _draw_y_axis_divs(self, qp: QPainter):
        qp.setPen(Qt.GlobalColor.white)
        cx, cy = self.get_offset_axis_center()
        
        for y in np.arange(cy, 0, -self._min_dist_btw_divs * self._scale_factor):
            qp.drawLine(QLineF(cx - self._div_line_size[1], y, cx + self._div_line_size[1], y))
            
        for y in np.arange(cy, self.height(), self._min_dist_btw_divs * self._scale_factor):
            qp.drawLine(QLineF(cx - self._div_line_size[1], y, cx + self._div_line_size[1], y))
 
    @_restore_painter_props
    def _draw_x_axis_divs_text(self, qp: QPainter):
        qp.setPen(Qt.GlobalColor.white)
        f = QFont('', 7)
        qp.setFont(f)

        ocx, ocy = self.get_offset_axis_center()
        cx, _ = self.get_center()
        
        step = self._min_dist_btw_divs * self._scale_factor
        for x in np.arange(step, abs(ocx) + self.width(), step):
            # x = (x - self._offset_x) + cx
            # x = x - self._offset_x - cx
            x = -(x + self._offset_x) - cx
            y = ocy + self._div_line_size[1] + 2
            # y = 10

            qp.rotate(90)
            qp.drawText(QRectF(y + 5, x - 5, 30, 10),
                        Qt.AlignmentFlag.AlignLeft,
                        str((abs(ocx + x)) / self._scale_factor))
            qp.rotate(-90)
            
    @_restore_painter_props
    def _draw_y_axis_divs_text(self, qp: QPainter):
        qp.setPen(Qt.GlobalColor.white)
        f = QFont('', 7)
        qp.setFont(f)
        
        ocx, ocy = self.get_offset_axis_center()
        cx, cy = self.get_center()
        
        step = self._min_dist_btw_divs * self._scale_factor
        for y in np.arange(step, ocy, step):
            # x = -(x + self._offset_x) - cx
            x = ocx + self._div_line_size[1] + 2
            # y = ocy + self._div_line_size[1] + 2
            y = -(y - self._offset_y) + cy
            qp.drawText(QRectF(x - 45, y - 5, 30, 10),
                        Qt.AlignmentFlag.AlignRight,
                        str((ocy - y) / self._scale_factor))
 
    def _apply_scale_factor(self):
        # Применяем масштабирование к данным
        self._prepared_data = self._source_data * self._scale_factor
 
    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            self._scale_factor += self._scale_factor_step

        elif event.angleDelta().y() < 0:
            self._scale_factor = max(self._scale_factor - self._scale_factor_step,
                                     self._scale_factor_step)
        
        self._apply_scale_factor()
        
        self.update()
        return super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        btn = event.button()
        if btn == Qt.MouseButton.LeftButton:
            self._lmb_pressed = True
            self._start_offset_click_pos = event.pos()
        
        elif btn == Qt.MouseButton.RightButton:
            self._offset_x = self._offset_y = 0
        
        if btn == Qt.MouseButton.MiddleButton:
            self._mmb_pressed = True
        
        self.update()
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        btn = event.button()
        if btn == Qt.MouseButton.LeftButton:
            self._lmb_pressed = False
            self._start_offset_click_pos = None
        
        if btn == Qt.MouseButton.MiddleButton:
            self._mmb_pressed = False
        
        self.update()
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._lmb_pressed:
            pos = event.pos() - self._start_offset_click_pos
            
            self._offset_x += pos.x()
            self._offset_y += pos.y()
            
            self._start_offset_click_pos = event.pos()
            
        self.update()
        return super().mouseMoveEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        
        if key == Qt.Key.Key_Control:
            self._ctrl_pressed = True
        if key == Qt.Key.Key_T:
            self._show_axis_div_text = not self._show_axis_div_text
        if key == Qt.Key.Key_P:
            self._is_show_points = not self._is_show_points
            
        self.update()
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        
        if key == Qt.Key.Key_Control:
            self._ctrl_pressed = False

        self.update()
        return super().keyReleaseEvent(event)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        # Если Массив с данными не задан,
        # то вызываем родительский метод
        if self._source_data is None:
            return super().paintEvent(event)
        
        # Начинаем отрисовку данных, 
        # если есть массив данных _data
        qp = QPainter()
        qp.begin(self)
        
        ocx, ocy = self.get_offset_axis_center()
        
        # Закрашиваем всё чёрным
        qp.fillRect(self.rect(), Qt.GlobalColor.black)
        qp.setPen(Qt.GlobalColor.green)
        
        # Рисуем координатную ось
        self._draw_axis(qp)
        self._draw_axis_div_text(qp)
        
        # Рисуем свойства графика
        self._draw_graph_properties_text(qp)
        
        # Рисуем график
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.drawPolyline(QPolygonF([QPointF(ocx + pos[1], ocy - pos[0]) for pos in self._prepared_data]))
        self._draw_points_of_graph(qp)
        qp.setRenderHint(QPainter.Antialiasing, False)
        
        self._draw_cursor_pos_at_graph(qp)
        
        # Заканчиваем отрисовку данных
        qp.end()
   
    def set_data(self, data: np.ndarray):
        self._source_data = data
        self._apply_scale_factor()
        self.update()

    def get_offset_axis_center(self) -> Tuple[int, int]:
        """ Возвращает координаты центра оси со смещением
            относительно центра виджета """
        center = self.rect().center()
        cx = center.x() + self._offset_x
        cy = center.y() + self._offset_y
        return cx, cy
    
    def get_center(self) -> Tuple[int, int]:
        """ Возвращает центр виджета (центр оси без смещения) """
        center = self.rect().center()
        return center.x(), center.y()
    
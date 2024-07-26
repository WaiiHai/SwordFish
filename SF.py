import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.Qt import *
import math
import networkx as nx


class Node(QGraphicsObject):
    hoverEntered = pyqtSignal()
    hoverLeft = pyqtSignal()

    def __init__(self, name: str, position: str, parent=None):
        super().__init__(parent)
        self._name = name
        self._edges = []
        self._color = "#007682"
        self._radius = 20
        self._rect = QRectF(0, 0, self._radius * 2, self._radius * 2)
        self._rect2 = QRectF(self._rect.x() + (self._radius / 4), self._rect.y() + self._radius / 3.5,
                             self._radius * 1.5, self._radius * 1.5)
        self._position = position
        self._prioritet = "#007682"
        self.font = QFont()
        self.font.setPointSize(4)
        self._main_name = ""
        self._main_info = ""
        self._date_days = ""
        self._start_day = ""
        self._end_day = ""
        self._accept = 0
        self._border = "#CDF4D5"
        self._scale = 150
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setAcceptHoverEvents(True)

    def time(self):
        if self._end_day != "" and self._accept == 0:
            v = QDateTime.currentDateTime()
            s = v.date()
            g = v.time()
            year, mount, day, hour, min = self._end_day.split(":")
            time = (int(year) - s.year()) * 365 + (int(mount) - s.month()) * 12 + int(day) - s.day()
            self._date_days = str(time) + " дн"
            if time <= 0:
                time_hour = int(hour) - g.hour()
                self._date_days = str(time_hour) + " час"
                if time_hour <= 0:
                    time_min = int(min) - g.minute()
                    self._date_days = str(time_min) + " мин"
                    if time_min <= 0:
                        self._date_days = "0 мин"
                        self._accept = -1
                        self._color = "red"
                        self._prioritet = "red"
            self.update()
            return self._date_days

    def hoverEnterEvent(self, event):
        self.hoverEntered.emit()
        self._border = ""
        self.update()

    def hoverLeaveEvent(self, event):
        self.hoverLeft.emit()
        self._border = "#CDF4D5"
        self.update()

    def boundingRect(self) -> QRectF:
        """Override from QGraphicsItem

        Returns:
            QRect: Return node bounding rect
        """
        return self._rect

    def boundingRect2(self) -> QRectF:
        """Override from QGraphicsItem

        Returns:
            QRect: Return node bounding rect
        """
        return self._rect2

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """Override from QGraphicsItem

        Draw node

        Args:
            painter (QPainter)
            option (QStyleOptionGraphicsItem)
        """
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(
            QPen(
                QColor(self._border),
                2,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )
        painter.setBrush(QBrush(QColor(self._color)))
        painter.drawEllipse(self.boundingRect())
        painter.setPen(
            QPen(
                QColor(self._prioritet),
                8,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )
        painter.drawArc(self.boundingRect2(), 0, -95 * 30)
        painter.setPen(
            QPen(
                QColor("white"),
                6,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )
        painter.setFont(self.font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self._main_name)
        painter.drawText(self.boundingRect(), Qt.AlignHCenter, self._date_days)

    def add_edge(self, edge):
        """Add an edge to this node

        Args:
            edge (Edge)
        """
        self._edges.append(edge)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """Override from QGraphicsItem

        Args:
            change (QGraphicsItem.GraphicsItemChange)
            value (Any)

        Returns:
            Any
        """

        self.timer = QTimer()
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.timer.singleShot(300, ui.main.view.connect)
            self.timer.singleShot(300, ui.main.view.DrawColorGraph)
            if ui.main.view.starter == 1:
                ui.move_node()
            for edge in self._edges:
                edge.adjust()
            pos_in_vie = self.mapToScene(self.pos())
            self._position = f"{int(pos_in_vie.x())}:{int(pos_in_vie.y())}"

        return super().itemChange(change, value)


class GraphView(QGraphicsView):
    def __init__(self, graph: nx.DiGraph, parent=None):
        super().__init__()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSceneRect(0, 0, 4000, 2000)
        self.setDragMode(QGraphicsView.NoDrag)
        self._graph = graph
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self._graph_scale = 200
        self._nodes_map = {}
        self.setMouseTracking(True)
        self.lbl = QLabel()
        self.pxp = QPixmap("Vector.png")
        self.range = 225
        self.scale(0.5, 0.5)
        self.check_node = 1
        self.check_tree = 1
        self.starter = 0

        self.ui_MainWindow = Ui_MainWindow()
        menu = QMenu()

        self.action1 = menu.addAction("Добавить")
        self.action1.triggered.connect(self.ui_MainWindow.make_node)

        self.action4 = menu.addAction("Просмотр")
        self.action4.triggered.connect(self.viewing)

        self.action2 = menu.addAction("Удалить")
        self.action2.triggered.connect(self.del_node)

        self.action3 = menu.addAction("Повернуть")
        self.action3.triggered.connect(self.EdgeReverse)

        self.action5 = menu.addAction("Перейти")
        self.action5.triggered.connect(self.go_node)

        self.action6 = menu.addAction("Просмотр дерева")
        self.action6.triggered.connect(self.DeepTree)

        self.action7 = menu.addAction("Просмотр")
        self.action7.triggered.connect(self.ZoomHeadFish)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pos: self.on_context_menu(pos, menu))

        self.timer = QTimer()
        self.timer.timeout.connect(self.connect)

        self.check = 2
        self.check2 = 1

        # def get_nx_layouts(self) -> list:
        # """Return all layout names
        #
        # Returns:
        #     list: layout name (str)
        # """
        # return self._nx_layout.keys()

        # def set_nx_layout(self, name: str):
        #     if name in self._nx_layout:
        #         self._nx_layout_function = self._nx_layout[name]
        #
        #         # Compute node position from layout function
        #         positions = self._nx_layout_function(self._graph)
        #
        #         # Change position of all nodes using an animation
        #         self.animations = QParallelAnimationGroup()
        #         for node, pos in positions.items():
        #             x, y = pos
        #             x *= self._graph_scale
        #             y *= self._graph_scale
        #             item = self._nodes_map[node]
        #
        #             animation = QPropertyAnimation(item, b"pos")
        #             animation.setDuration(1000)
        #             animation.setEndValue(QPointF(x, y))
        #             animation.setEasingCurve(QEasingCurve.OutExpo)
        #             self.animations.addAnimation(animation)
        #
        #         self.animations.start()
        self.timer = QTimer()
        self.timer.timeout.connect(self.UpTime)
        self.timer.start(10000)

    def UpTime(self):
        if len(self._nodes_map) >= 9:
            for i in range(len(self._nodes_map)):
                self._nodes_map[f"{i + 1}"].time()

    def on_context_menu(self, pos, menu):
        self.cursor_pos = QCursor.pos()
        point = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        item = self.scene().itemAt(point, self.transform())
        global_pos = self.mapToGlobal(pos)
        self.pos_in_main = self.mapToScene(self.mapFromGlobal(global_pos))
        if (self.check == 0 or self.check2 == 0):
            # Режим переноса
            if item != None and isinstance(item, QGraphicsPixmapItem) == 1:
                self.action1.setVisible(False)
                self.action2.setVisible(False)
                self.action3.setVisible(False)
                self.action4.setVisible(False)
                self.action5.setVisible(False)
                self.action6.setVisible(False)
                self.action7.setVisible(False)
                menu.exec(global_pos)
            elif (item != None) and (item._color == "#424242" or item._color == "#66ff00"):
                self.action1.setVisible(False)
                self.action2.setVisible(False)
                self.action3.setVisible(True)
                self.action4.setVisible(False)
                self.action5.setVisible(False)
                self.action6.setVisible(False)
                self.action7.setVisible(False)
                menu.exec(global_pos)
        elif item != None and isinstance(item, QGraphicsPixmapItem) == 1:
            self.action1.setVisible(False)
            self.action2.setVisible(False)
            self.action3.setVisible(False)
            self.action4.setVisible(False)
            self.action5.setVisible(False)
            self.action6.setVisible(False)
            self.action7.setVisible(True)
            menu.exec(global_pos)
        elif (item != None) and (
                item._color == "#007682" or item._color == "green" or item._color == "red") and self.check_node == 1 and self.check_tree == 1:
            # Нормальный режим(Нажатие на ребро)
            self.action1.setVisible(False)
            self.action2.setVisible(True)
            self.action3.setVisible(False)
            self.action4.setVisible(True)
            self.action5.setVisible(False)
            self.action6.setVisible(False)
            self.action7.setVisible(False)
            menu.exec(global_pos)
        elif item != None and item._color == "#424242" and self.check_node == 1 and self.check_tree == 1:
            # Нормальный режим(Нажатие на ребро)
            self.action1.setVisible(False)
            self.action2.setVisible(False)
            self.action3.setVisible(False)
            self.action4.setVisible(False)
            self.action5.setVisible(False)
            self.action6.setVisible(True)
            self.action7.setVisible(False)
            menu.exec(global_pos)
        elif self.check_tree == 0:
            # Режим Tree
            if (item != None) and (item._color == "#424242"):
                self.action1.setVisible(False)
                self.action2.setVisible(False)
                self.action3.setVisible(False)
                self.action4.setVisible(False)
                self.action6.setVisible(False)
                self.action5.setVisible(True)
                self.action7.setVisible(False)
                menu.exec(global_pos)
            elif item != None and item._color == "#007682":
                self.action1.setVisible(False)
                self.action2.setVisible(False)
                self.action3.setVisible(False)
                self.action4.setVisible(False)
                self.action6.setVisible(False)
                self.action5.setVisible(False)
                self.action7.setVisible(False)
                menu.exec(global_pos)
        elif self.check_node == 0:
            # Режим просмотра вершины
            if (item != None) and (item._color == "#424242"):
                self.action1.setVisible(False)
                self.action2.setVisible(False)
                self.action3.setVisible(False)
                self.action4.setVisible(False)
                self.action6.setVisible(False)
                self.action5.setVisible(True)
                self.action7.setVisible(False)
                menu.exec(global_pos)
            elif item != None and item._color == "#007682":
                self.action1.setVisible(False)
                self.action2.setVisible(False)
                self.action3.setVisible(False)
                self.action4.setVisible(False)
                self.action6.setVisible(False)
                self.action5.setVisible(False)
                self.action7.setVisible(False)
                menu.exec(global_pos)
        elif self.check_node == 1:
            self.action1.setVisible(True)
            self.action2.setVisible(False)
            self.action3.setVisible(False)
            self.action4.setVisible(False)
            self.action6.setVisible(False)
            self.action5.setVisible(False)
            self.action7.setVisible(False)
            menu.exec(global_pos)


        else:
            self.action1.setVisible(True)
            self.action2.setVisible(False)
            self.action3.setVisible(False)
            self.action4.setVisible(False)
            self.action5.setVisible(False)
            self.action6.setVisible(False)
            menu.exec(global_pos)

    def keyPressEvent(self, e):
        self.cursor_pos = QCursor.pos()
        pos_in_vie = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        if e.key() == Qt.Key_E:
            self.add_node(str(len(self._nodes_map) + 1), pos_in_vie.x(), pos_in_vie.y(), "#007682", "", "", "",
                          f"{pos_in_vie.x()}:{pos_in_vie.y()}", "", "")
        if e.key() == Qt.Key_Q:
            self.del_node()

    def CheckTime(self):
        point = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        item = self.scene().itemAt(point, self.transform())
        if item != None:
            item.time()

    def ZoomHeadFish(self):
        scene_point = QPointF(2200, 350)
        rect_item = self.scene().addRect(scene_point.x(), scene_point.y(), 1500, 700)
        self.scene().setSceneRect(rect_item.boundingRect())
        self.fitInView(QRectF(rect_item.rect()), Qt.KeepAspectRatio)
        self.scene().removeItem(rect_item)
        ui.showHead()

    def Starter(self):
        scene_point = QPointF(2200, 350)
        rect_item = self.scene().addRect(scene_point.x(), scene_point.y(), 1500, 700)
        self.scene().setSceneRect(rect_item.boundingRect())
        self.fitInView(QRectF(rect_item.rect()), Qt.KeepAspectRatio)
        self.scene().removeItem(rect_item)
        ui.showHeadEditor()
        self.starter = 1

    def DeepTree(self):
        point = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        item = self.scene().itemAt(point, self.transform())
        self.MaxX = 0
        self.MaxY = 0
        self.MinX = 9999
        self.MinY = 9999
        if item != None:
            item._color = "yellow"
            node = item._dest
            self.NodeNotMovible()
            self.TreeFind(node)
        scene_point = QPointF(self.MinX, self.MinY)
        rect_item = self.scene().addRect(scene_point.x() + 150, scene_point.y(), self.MaxX - self.MinX + 80,
                                         self.MaxY - self.MinY + 120)
        self.scene().setSceneRect(rect_item.boundingRect())
        self.fitInView(QRectF(rect_item.rect()), Qt.KeepAspectRatio)
        self.scene().removeItem(rect_item)
        ui.showTree(item)

    def NodeMovible(self):
        for i in range(len(self._nodes_map)):
            self._nodes_map[f"{i + 1}"].setFlag(self._nodes_map[f"{i + 1}"].ItemIsMovable, True)

    def NodeNotMovible(self):
        for i in range(len(self._nodes_map)):
            self._nodes_map[f"{i + 1}"].setFlag(self._nodes_map[f"{i + 1}"].ItemIsMovable, False)

    def TreeFind(self, node):
        x, y = node._position.split(":")
        scene_point = QPointF(int(x), int(y))
        widget_pos = self.mapFromScene(scene_point)

        if widget_pos.x() < self.MinX:
            self.MinX = widget_pos.x()
        if widget_pos.y() < self.MinY:
            self.MinY = widget_pos.y()
        if widget_pos.x() > self.MaxX:
            self.MaxX = widget_pos.x()
        if widget_pos.y() > self.MaxY:
            self.MaxY = widget_pos.y()
        if len(node._edges) == 1:
            return
        for i in range(len(node._edges)):
            if node._edges[i]._dest != node:
                node._edges[i]._color = "yellow"
                self.TreeFind(node._edges[i]._dest)

    def go_node(self):
        point = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        item = self.scene().itemAt(point, self.transform())
        if item != None:
            self.check_node = 0
            ui.MenuClose()
            self.next_item = item._dest
            if ui.g == item._dest:
                for i in range(len(ui.g._edges)):
                    if ui.g._edges[i]._dest == item._dest:
                        self.next_item = ui.g._edges[i]._source
            # for i in range(len(ui.g._edges))
            #     if item._dest == ui.g._edges[i]:

            self.zoom(self.next_item)
            ui.viewing(self.next_item)
            timer = QTimer()
            timer.singleShot(0, self.NextNode)

    def NextNode(self):
        ui.viewing(self.next_item)

    def viewing(self):
        point = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        item = self.scene().itemAt(point, self.transform())
        if item != None:
            self.check_node = 0
            self.zoom(item)
            ui.viewing(item)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            pass
        else:
            pass

    def zoom(self, item):
        self.fitInView(item, Qt.KeepAspectRatio)
        self.scale(0.6, 0.6)

    def _load_graph(self):
        self.scene().clear()
        self._nodes_map.clear()

        # Add nodes
        for node in self._graph:
            item = Node(node)
            self.scene().addItem(item)
            self._nodes_map[node] = item

        # Add edges
        for a, b in self._graph.edges:
            source = self._nodes_map[a]
            dest = self._nodes_map[b]
            self.scene().addItem(Edge(source, dest))

    def add_node(self, name, x, y, prioritet, main_name, main_info, date_days, position, start_day, end_day, radius=20):
        item = Node(name, [x, y])
        item._prioritet = prioritet
        item._main_name = main_name
        item._main_info = main_info
        item._date_days = date_days
        item._position = position
        item._radius = radius
        item._start_day = start_day
        item._end_day = end_day
        item._rect = QRectF(0, 0, item._radius * 2, item._radius * 2)
        item._rect2 = QRectF(item._rect.x() + (item._radius / 4), item._rect.y() + item._radius / 3.5,
                             item._radius * 1.5, item._radius * 1.5)

        item.update()
        self.scene().addItem(item)
        self._graph.add_node(item._name)
        self._nodes_map[str(len(self._nodes_map) + 1)] = item
        item.moveBy(x, y)
        self.connect()

    def add_fish(self, x, y):
        img = QPixmap("Vector.png")
        img2 = QPixmap("Group.png")
        img = img.scaled(2000, 500, QtCore.Qt.KeepAspectRatio)
        img2 = img2.scaled(1000, 300, QtCore.Qt.KeepAspectRatio)
        self.pixmap_item = QGraphicsPixmapItem(img)
        self.pixmap_item2 = QGraphicsPixmapItem(img2)
        self.fish = Fish('1', [x, y], self.pixmap_item, self.pixmap_item2)
        self.text_item = QGraphicsTextItem()
        self.text_item.setPlainText("")
        self.text_item.setDefaultTextColor(Qt.white)
        font = QFont()
        font.setPointSize(20)
        self.text_item.setFont(font)
        self.text_item.setPos(2880, 460)
        self.text_item.setZValue(1)
        self.scene().addItem(self.text_item)
        self.fish.moveimg()
        k = self.pixmap_item.boundingRect().width() / 7.68 + x
        g = ((self.pixmap_item.boundingRect().width() - (self.pixmap_item.boundingRect().width() / 2.4)) / 10)
        # int((pixmap_item.boundingRect().width()-(pixmap_item.boundingRect().width()/2.4))/(self.range+50))
        for i in range(8):
            self.add_node(f"{i + 1}", x + int(k), y - 5, "", "", "", "", f"{x + k}:{y}", "", "", 0)
            k = k + g
            self._nodes_map[f"{i + 1}"].setFlag(self._nodes_map[f"{i + 1}"].ItemIsMovable, False)
        for q, e in (self._graph.edges):
            x1 = self._nodes_map[f"{q}"]
            y1 = self._nodes_map[f"{e}"]
            for j in range(len(x1._edges)):
                if x1._edges[j]._dest == y1:
                    x1._edges[j]._arrow_size = 0
                    x1._edges[j]._tickness = 0
                    x1._edges[j].update()
        self.scene().addItem(self.fish)
        self.scene().addItem(self.pixmap_item)
        self.scene().addItem(self.pixmap_item2)

    def del_node(self):
        point = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        item = self.scene().itemAt(point, self.transform())
        if item != None:
            if item._color == "#007682" or item._color == "green" or item._color == "red":
                for i in range(len(item._edges)):
                    self.scene().removeItem(item._edges[i])

                for i in range(len(item._edges)):
                    if item._edges[i]._dest != item:
                        for j in range(len(item._edges)):
                            if item._edges[i]._dest._edges[j]._source == item:
                                self.scene().removeItem(item._edges[i]._dest._edges[j])
                                item._edges[i]._dest._edges.remove(item._edges[i]._dest._edges[j])
                                break
                    else:
                        for f in range(len(item._edges)):
                            if item._edges[i]._source._edges[f]._dest == item:
                                item._edges[i]._source._edges.remove(item._edges[i]._source._edges[f])
                                break

                arr = []
                for a, b in (self._graph.edges):
                    if a == item._name or b == item._name:
                        arr.append(f"{a}:{b}")

                for i in range(len(arr)):
                    a, b = arr[i].split(":")
                    self._graph.remove_edge(a, b)
                self.scene().removeItem(item)
                item._position = None
                self._graph.remove_node(item._name)
                item._name = -1

    def add_edge(self, item1, item2):
        if self._graph.has_edge(item1._name, item2._name) == False and self._graph.has_edge(item2._name,
                                                                                            item1._name) == False:
            self._graph.add_edge(item1._name, item2._name)
            self.scene().addItem(Edge(item1, item2))

    def DrawColorGraph(self):
        arr2 = []
        k = 0
        for node in self._graph.nodes():
            if len(list(self._graph.in_edges(node))) >= 2:
                arr2.append(list(self._graph.in_edges(node)))
                k = len(list(self._graph.in_edges(node)))

        for x, y in (self._graph.edges):
            x1 = self._nodes_map[f"{x}"]
            y1 = self._nodes_map[f"{y}"]
            for j in range(len(x1._edges)):
                if x1._edges[j]._dest == y1:
                    x1._edges[j]._color = "#424242"
                    x1._edges[j].update()

        k = len(arr2)
        for i in range(k):
            m = len(arr2[i - 1])
            for u in range(m):
                z = arr2[i - 1][u - 1]
                x = z[0]
                y = z[1]
                x1 = self._nodes_map[f"{x}"]
                y1 = self._nodes_map[f"{y}"]
                for j in range(len(x1._edges)):
                    if x1._edges[j]._dest == y1:
                        x1._edges[j]._color = "#66ff00"
                        x1._edges[j].update()
        c = 0
        for x, y in (self._graph.edges):
            x1 = self._nodes_map[f"{x}"]
            for j in range(len(x1._edges)):
                if x1._edges[j]._color == "#66ff00":
                    ui.pushButton_accept.setEnabled(False)
                    ui.pushButton_accept.setStyleSheet("QPushButton\n"
                                                       "{\n"
                                                       "   text-decoration: none;\n"
                                                       "  display: inline-block;\n"
                                                       "  width: 140px;\n"
                                                       "  height: 45px;\n"
                                                       "  line-height: 45px;\n"
                                                       "  border-radius: 45px;\n"
                                                       "  margin: 10px 20px;\n"
                                                       "  font-family: \'Montserrat\', sans-serif;\n"
                                                       "  font-size: 8px;\n"
                                                       "  text-transform: uppercase;\n"
                                                       "  text-align: center;\n"
                                                       "  letter-spacing: 3px;\n"
                                                       "  font-weight: 600;\n"
                                                       "  color: white;\n"
                                                       "  background: #1E5945;\n"
                                                       "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                                       "  transition: .3s;\n"
                                                       "}\n"
                                                       "QPushButton:hover\n"
                                                       "{\n"
                                                       "  background: #2EE59D;\n"
                                                       "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                                       "  color: white;\n"
                                                       "  transform: translateY(-7px);}")
                    c = c + 1
        if c == 0:
            ui.pushButton_accept.setEnabled(True)
            ui.pushButton_accept.setStyleSheet("QPushButton\n"
                                               "{\n"
                                               "   text-decoration: none;\n"
                                               "  display: inline-block;\n"
                                               "  width: 140px;\n"
                                               "  height: 45px;\n"
                                               "  line-height: 45px;\n"
                                               "  border-radius: 45px;\n"
                                               "  margin: 10px 20px;\n"
                                               "  font-family: \'Montserrat\', sans-serif;\n"
                                               "  font-size: 8px;\n"
                                               "  text-transform: uppercase;\n"
                                               "  text-align: center;\n"
                                               "  letter-spacing: 3px;\n"
                                               "  font-weight: 600;\n"
                                               "  color: white;\n"
                                               "  background: #1F5B63;\n"
                                               "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                               "  transition: .3s;\n"
                                               "}\n"
                                               "QPushButton:hover\n"
                                               "{\n"
                                               "  background: #2EE59D;\n"
                                               "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                               "  color: white;\n"
                                               "  transform: translateY(-7px);}")

    def remove_edge(self, item, item2):
        for i in range(len(item._edges)):
            if item._edges[i]._dest == item2:
                self.scene().removeItem(item._edges[i])
                item._edges.pop(i)
                break
        for i in range(len(item2._edges)):
            if item2._edges[i]._source == item:
                self.scene().removeItem(item2._edges[i])
                item2._edges.pop(i)
                break
        self._graph.remove_edge(item._name, item2._name)

    def connect(self):
        for i in range(1, len(self._nodes_map)):
            x = self._nodes_map[f"{i}"]._position
            if x is not None:
                x1, y1 = x.split(":")
                x1 = int(x1)
                y1 = int(y1)
                for j in range(i + 1, len(self._nodes_map) + 1):
                    y = self._nodes_map[f"{j}"]._position
                    if y is not None:
                        x2, y2 = y.split(":")
                        x2 = int(x2)
                        y2 = int(y2)
                        if ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 < self.range:
                            self.add_edge(self._nodes_map[f"{i}"], self._nodes_map[f"{j}"])
                        else:
                            if self._graph.has_edge(self._nodes_map[f"{i}"]._name,
                                                    self._nodes_map[f"{j}"]._name) == True:
                                self.remove_edge(self._nodes_map[f"{i}"], self._nodes_map[f"{j}"])
                            elif self._graph.has_edge(self._nodes_map[f"{j}"]._name,
                                                      self._nodes_map[f"{i}"]._name) == True:
                                self.remove_edge(self._nodes_map[f"{j}"], self._nodes_map[f"{i}"])

    def EdgeReverse(self):
        point = self.mapToScene(self.mapFromGlobal(self.cursor_pos))
        item = self.scene().itemAt(point, self.transform())
        if item != None:
            if item._color == "#424242" or item._color == "#66ff00":
                u = item._dest
                v = item._source
                s = (v, u)
                self.scene().removeItem(item)
                self.remove_edge(*s)
                self.add_edge(*s[::-1])
                self.DrawColorGraph()


class Edge(QGraphicsItem):
    def __init__(self, source: Node, dest: Node, parent: QGraphicsItem = None):
        """Edge constructor

        Args:
            source (Node): source node
            dest (Node): destination node
        """
        super().__init__(parent)
        self._source = source
        self._dest = dest
        self._name = ""

        self._tickness = 2
        self._color = "#424242"
        self._arrow_size = 10

        self._source.add_edge(self)
        self._dest.add_edge(self)

        self._line = QLineF()
        self.setZValue(-1)
        self.adjust()

    def boundingRect(self) -> QRectF:
        """Override from QGraphicsItem

        Returns:
            QRect: Return node bounding rect
        """
        return (
            QRectF(self._line.p1(), self._line.p2())
            .normalized()
            .adjusted(
                -self._tickness - self._arrow_size,
                -self._tickness - self._arrow_size,
                self._tickness + self._arrow_size,
                self._tickness + self._arrow_size,
            )
        )

    def adjust(self):
        """
        Update edge position from source and destination node.
        This method is called from Node::itemChange
        """
        self.prepareGeometryChange()
        self._line = QLineF(
            self._source.pos() + self._source.boundingRect().center(),
            self._dest.pos() + self._dest.boundingRect().center(),
        )

    def _draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF):
        """Draw arrow from start point to end point.

        Args:
            painter (QPainter)
            start (QPointF): start position
            end (QPointF): end position
        """
        painter.setBrush(QBrush(QColor(self._color)))

        line = QLineF(end, start)

        angle = math.atan2(-line.dy(), line.dx())
        arrow_p1 = line.p1() + QPointF(
            math.sin(angle + math.pi / 3) * self._arrow_size,
            math.cos(angle + math.pi / 3) * self._arrow_size,
        )
        arrow_p2 = line.p1() + QPointF(
            math.sin(angle + math.pi - math.pi / 3) * self._arrow_size,
            math.cos(angle + math.pi - math.pi / 3) * self._arrow_size,
        )

        arrow_head = QPolygonF()
        arrow_head.clear()
        arrow_head.append(line.p1())
        arrow_head.append(arrow_p1)
        arrow_head.append(arrow_p2)
        painter.drawLine(line)
        painter.drawPolygon(arrow_head)

    def _arrow_target(self) -> QPointF:
        """Calculate the position of the arrow taking into account the size of the destination node

        Returns:
            QPointF
        """
        target = self._line.p1()
        center = self._line.p2()
        radius = self._dest._radius
        vector = target - center
        length = math.sqrt(vector.x() ** 2 + vector.y() ** 2)
        if length == 0:
            return target
        normal = vector / length
        target = QPointF(center.x() + (normal.x() * radius), center.y() + (normal.y() * radius))

        return target

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Override from QGraphicsItem

        Draw Edge. This method is called from Edge.adjust()

        Args:
            painter (QPainter)
            option (QStyleOptionGraphicsItem)
        """

        if self._source and self._dest:
            painter.setRenderHints(QPainter.Antialiasing)
            painter.setPen(
                QPen(
                    QColor(self._color),
                    self._tickness,
                    Qt.SolidLine,
                    Qt.RoundCap,
                    Qt.RoundJoin,
                )
            )
            painter.drawLine(self._line)
            self._draw_arrow(painter, self._line.p1(), self._arrow_target())


class SecondWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.graph = nx.DiGraph()
        self.setStyleSheet("background-color: #2E8B57;")

        # self.graph.add_edges_from(
        #     [
        #         ("1", "2"),
        #         ("2", "3"),
        #         ("3", "4"),
        #         ("1", "5"),
        #         ("1", "6"),
        #         ("1", "7"),
        #     ]
        # )
        self.view = GraphView(self.graph)
        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.view)


class Ui_MainWindow(QtWidgets.QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1680, 1024)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.Cont_Menu = QtWidgets.QFrame(self.frame_3)
        self.Cont_Menu.setMinimumSize(QtCore.QSize(0, 0))
        self.Cont_Menu.setMaximumSize(QtCore.QSize(16777215, 0))
        self.Cont_Menu.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.Cont_Menu.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Cont_Menu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Cont_Menu.setObjectName("Cont_Menu")

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.Cont_Menu)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        self.pushButton_accept = QtWidgets.QPushButton(self.Cont_Menu)
        self.pushButton_accept.setMinimumSize(QtCore.QSize(200, 50))
        self.pushButton_accept.setStyleSheet("QPushButton\n"
                                             "{\n"
                                             "   text-decoration: none;\n"
                                             "  display: inline-block;\n"
                                             "  width: 140px;\n"
                                             "  height: 45px;\n"
                                             "  line-height: 45px;\n"
                                             "  border-radius: 45px;\n"
                                             "  margin: 10px 20px;\n"
                                             "  font-family: \'Montserrat\', sans-serif;\n"
                                             "  font-size: 8px;\n"
                                             "  text-transform: uppercase;\n"
                                             "  text-align: center;\n"
                                             "  letter-spacing: 3px;\n"
                                             "  font-weight: 600;\n"
                                             "  color: white;\n"
                                             "  background: #1F5B63;\n"
                                             "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                             "  transition: .3s;\n"
                                             "}\n"
                                             "QPushButton:hover\n"
                                             "{\n"
                                             "  background: #2EE59D;\n"
                                             "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                             "  color: white;\n"
                                             "  transform: translateY(-7px);}")
        self.pushButton_accept.setObjectName("pushButton_accept")
        self.horizontalLayout_4.addWidget(self.pushButton_accept)

        self.frame_6 = QtWidgets.QFrame(self.frame_3)

        self.frame_6.setMinimumSize(QtCore.QSize(0, 60))
        self.frame_6.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.pushButton_9 = QtWidgets.QPushButton(self.frame_6)
        self.pushButton_9.setMinimumSize(QtCore.QSize(40, 40))
        self.pushButton_9.setMaximumSize(QtCore.QSize(40, 40))
        self.pushButton_9.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_9.setObjectName("pushButton_9")
        self.horizontalLayout_3.addWidget(self.pushButton_9)
        self.horizontalLayout_3.setSpacing(15)
        self.verticalLayout_3.addWidget(self.frame_6, 0, QtCore.Qt.AlignRight)
        self.verticalLayout_3.addWidget(self.Cont_Menu, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.main = SecondWindow(self.frame_3)
        self.main.setStyleSheet("QWidget { border: none;background-color: rgb(46, 139, 87);}")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main.sizePolicy().hasHeightForWidth())
        self.main.setSizePolicy(sizePolicy)
        self.main.setObjectName("main")
        self.verticalLayout_3.addWidget(self.main)

        self.frame_7 = QtWidgets.QFrame(self.frame_3)
        self.frame_7.setMinimumSize(QtCore.QSize(0, 25))
        self.frame_7.setMaximumSize(QtCore.QSize(16777215, 25))
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_7 = QtWidgets.QPushButton(self.frame_7)
        self.pushButton_7.setMaximumSize(QtCore.QSize(25, 25))
        self.pushButton_7.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_7.setObjectName("pushButton_7")
        self.horizontalLayout_4.addWidget(self.pushButton_7)
        self.pushButton_8 = QtWidgets.QPushButton(self.frame_7)
        self.pushButton_8.setMaximumSize(QtCore.QSize(25, 25))
        self.pushButton_8.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_8.setObjectName("pushButton_8")
        self.horizontalLayout_4.addWidget(self.pushButton_8)
        self.verticalLayout_3.addWidget(self.frame_7, 0, QtCore.Qt.AlignRight)
        self.horizontalLayout.addWidget(self.frame_3)

        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 140))
        self.frame_2.setMaximumSize(QtCore.QSize(0, 16777215))
        self.frame_2.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.Create = ThWindow(self.frame_2)
        self.Create.setMaximumSize(QtCore.QSize(16777215, 200))
        self.verticalLayout.addWidget(self.Create)

        self.frame_4 = QtWidgets.QFrame(self.frame_2)
        self.frame_4.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setContentsMargins(0, 25, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.frame_4)
        self.pushButton.setStyleSheet("QPushButton\n"
                                      "{\n"
                                      "   text-decoration: none;\n"
                                      "  display: inline-block;\n"
                                      "  width: 140px;\n"
                                      "  height: 45px;\n"
                                      "  line-height: 45px;\n"
                                      "  border-radius: 45px;\n"
                                      "  margin: 10px 20px;\n"
                                      "  font-family: \'Montserrat\', sans-serif;\n"
                                      "  font-size: 6px;\n"
                                      "  text-transform: uppercase;\n"
                                      "  text-align: center;\n"
                                      "  letter-spacing: 3px;\n"
                                      "  font-weight: 600;\n"
                                      "  color: white;\n"
                                      "  background: #1F5B63;\n"
                                      "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                      "  transition: .3s;\n"
                                      "}\n"
                                      "QPushButton:hover\n"
                                      "{\n"
                                      "  background: #2EE59D;\n"
                                      "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                      "  color: white;\n"
                                      "  transform: translateY(-7px);}")
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_2.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  margin: 10px 20px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_3.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  margin: 10px 20px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_4.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  margin: 10px 20px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout_2.addWidget(self.pushButton_4)
        self.frame_5 = QtWidgets.QFrame(self.frame_4)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_5.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_2.addWidget(self.pushButton_5)
        self.pushButton_6 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_6.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_2.addWidget(self.pushButton_6)
        self.verticalLayout_2.addWidget(self.frame_5, 0, QtCore.Qt.AlignTop)
        self.verticalLayout.addWidget(self.frame_4)
        self.horizontalLayout.addWidget(self.frame_2, 0, QtCore.Qt.AlignRight)

        # frame_2 = frame_viewing_2
        # verticalLayout = verticalLayoutViewing
        # frame_4 = frame_viewing_4
        # frame_5 = frame_viewing_5
        # verticalLayout_2 = verticalLayoutViewing_2
        # horizontalLayout_2 = horizontalLayoutViewing_2

        self.frame_viewing_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_viewing_2.setMinimumSize(QtCore.QSize(0, 140))
        self.frame_viewing_2.setMaximumSize(QtCore.QSize(0, 16777215))
        self.frame_viewing_2.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_viewing_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_viewing_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_viewing_2.setObjectName("frame_viewing_2")

        self.verticalLayoutViewing = QtWidgets.QVBoxLayout(self.frame_viewing_2)
        self.verticalLayoutViewing.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutViewing.setSpacing(0)
        self.verticalLayoutViewing.setObjectName("verticalLayout")

        self.frame_viewing_4 = QtWidgets.QFrame(self.frame_viewing_2)
        self.frame_viewing_4.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_viewing_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_viewing_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_viewing_4.setObjectName("frame_viewing_4")
        self.verticalLayoutViewing_2 = QtWidgets.QVBoxLayout(self.frame_viewing_4)
        self.verticalLayoutViewing_2.setContentsMargins(0, 250, 0, 0)
        self.verticalLayoutViewing_2.setSpacing(15)
        self.verticalLayoutViewing_2.setObjectName("verticalLayout_2")
        self.pushButtonViewing_1 = QtWidgets.QPushButton(self.frame_viewing_4)
        self.pushButtonViewing_1.setStyleSheet("QPushButton\n"
                                               "{\n"
                                               "   text-decoration: none;\n"
                                               "  display: inline-block;\n"
                                               "  width: 140px;\n"
                                               "  height: 45px;\n"
                                               "  line-height: 45px;\n"
                                               "  border-radius: 45px;\n"
                                               "  margin: 10px 20px;\n"
                                               "  font-family: \'Montserrat\', sans-serif;\n"
                                               "  font-size: 6px;\n"
                                               "  text-transform: uppercase;\n"
                                               "  text-align: center;\n"
                                               "  letter-spacing: 3px;\n"
                                               "  font-weight: 600;\n"
                                               "  color: white;\n"
                                               "  background: #1F5B63;\n"
                                               "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                               "  transition: .3s;\n"
                                               "}\n"
                                               "QPushButton:hover\n"
                                               "{\n"
                                               "  background: #2EE59D;\n"
                                               "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                               "  color: white;\n"
                                               "  transform: translateY(-7px);}")
        self.pushButtonViewing_1.setObjectName("pushButtonViewing_1")
        self.verticalLayoutViewing_2.addWidget(self.pushButtonViewing_1)
        self.pushButtonViewing_2 = QtWidgets.QPushButton(self.frame_viewing_4)
        self.pushButtonViewing_2.setStyleSheet("QPushButton\n"
                                               "{\n"
                                               "   text-decoration: none;\n"
                                               "  display: inline-block;\n"
                                               "  width: 140px;\n"
                                               "  height: 45px;\n"
                                               "  line-height: 45px;\n"
                                               "  border-radius: 45px;\n"
                                               "  margin: 10px 20px;\n"
                                               "  font-family: \'Montserrat\', sans-serif;\n"
                                               "  font-size: 6px;\n"
                                               "  text-transform: uppercase;\n"
                                               "  text-align: center;\n"
                                               "  letter-spacing: 3px;\n"
                                               "  font-weight: 600;\n"
                                               "  color: white;\n"
                                               "  background: #1F5B63;\n"
                                               "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                               "  transition: .3s;\n"
                                               "}\n"
                                               "QPushButton:hover\n"
                                               "{\n"
                                               "  background: #2EE59D;\n"
                                               "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                               "  color: white;\n"
                                               "  transform: translateY(-7px);}")
        self.pushButtonViewing_2.setObjectName("pushButtonViewing_2")
        self.verticalLayoutViewing_2.addWidget(self.pushButtonViewing_2)
        self.pushButtonViewing_3 = QtWidgets.QPushButton(self.frame_viewing_4)
        self.pushButtonViewing_3.setStyleSheet("QPushButton\n"
                                               "{\n"
                                               "   text-decoration: none;\n"
                                               "  display: inline-block;\n"
                                               "  width: 140px;\n"
                                               "  height: 45px;\n"
                                               "  line-height: 45px;\n"
                                               "  border-radius: 45px;\n"
                                               "  margin: 10px 20px;\n"
                                               "  font-family: \'Montserrat\', sans-serif;\n"
                                               "  font-size: 6px;\n"
                                               "  text-transform: uppercase;\n"
                                               "  text-align: center;\n"
                                               "  letter-spacing: 3px;\n"
                                               "  font-weight: 600;\n"
                                               "  color: white;\n"
                                               "  background: #1F5B63;\n"
                                               "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                               "  transition: .3s;\n"
                                               "}\n"
                                               "QPushButton:hover\n"
                                               "{\n"
                                               "  background: #2EE59D;\n"
                                               "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                               "  color: white;\n"
                                               "  transform: translateY(-7px);}")
        self.pushButtonViewing_3.setObjectName("pushButtonViewing_2")
        self.verticalLayoutViewing_2.addWidget(self.pushButtonViewing_3)
        self.pushButtonViewing_4 = QtWidgets.QPushButton(self.frame_viewing_4)
        self.pushButtonViewing_4.setStyleSheet("QPushButton\n"
                                               "{\n"
                                               "   text-decoration: none;\n"
                                               "  display: inline-block;\n"
                                               "  width: 140px;\n"
                                               "  height: 45px;\n"
                                               "  line-height: 45px;\n"
                                               "  border-radius: 45px;\n"
                                               "  margin: 10px 20px;\n"
                                               "  font-family: \'Montserrat\', sans-serif;\n"
                                               "  font-size: 6px;\n"
                                               "  text-transform: uppercase;\n"
                                               "  text-align: center;\n"
                                               "  letter-spacing: 3px;\n"
                                               "  font-weight: 600;\n"
                                               "  color: white;\n"
                                               "  background: #1F5B63;\n"
                                               "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                               "  transition: .3s;\n"
                                               "}\n"
                                               "QPushButton:hover\n"
                                               "{\n"
                                               "  background: #2EE59D;\n"
                                               "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                               "  color: white;\n"
                                               "  transform: translateY(-7px);}")
        self.pushButtonViewing_4.setObjectName("pushButtonViewing_4")
        self.verticalLayoutViewing_2.addWidget(self.pushButtonViewing_4)
        self.frame_viewing_5 = QtWidgets.QFrame(self.frame_viewing_4)
        self.frame_viewing_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_viewing_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_viewing_5.setObjectName("frame_5")
        self.horizontalLayoutViewing_2 = QtWidgets.QHBoxLayout(self.frame_viewing_5)
        self.horizontalLayoutViewing_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutViewing_2.setSpacing(0)
        self.horizontalLayoutViewing_2.setObjectName("horizontalLayoutViewing_2")
        self.verticalLayoutViewing_2.addWidget(self.frame_viewing_5, 0, QtCore.Qt.AlignTop)
        self.verticalLayoutViewing.addWidget(self.frame_viewing_4)
        self.horizontalLayout.addWidget(self.frame_viewing_2, 0, QtCore.Qt.AlignRight)

        ###################################################################################

        # frame_2 = frame_Ch_2
        # verticalLayout = verticalLayoutCh
        # frame_4 = frame_ch_4
        # frame_5 = frame_ch_5
        # verticalLayout_2 = verticalLayoutCh_2
        # horizontalLayout_2 = horizontalLayoutCh_2

        self.frame_Ch_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_Ch_2.setMinimumSize(QtCore.QSize(0, 140))
        self.frame_Ch_2.setMaximumSize(QtCore.QSize(0, 16777215))
        self.frame_Ch_2.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_Ch_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Ch_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Ch_2.setObjectName("frame_Ch_2")

        self.verticalLayoutCh = QtWidgets.QVBoxLayout(self.frame_Ch_2)
        self.verticalLayoutCh.setContentsMargins(0, 200, 0, 0)
        self.verticalLayoutCh.setSpacing(0)
        self.verticalLayoutCh.setObjectName("verticalLayoutCh")

        self.frame_Ch_4 = QtWidgets.QFrame(self.frame_Ch_2)
        self.frame_Ch_4.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_Ch_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Ch_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Ch_4.setObjectName("frame_Ch_4")
        self.verticalLayoutCh_2 = QtWidgets.QVBoxLayout(self.frame_Ch_4)
        self.verticalLayoutCh_2.setContentsMargins(0, 25, 0, 0)
        self.verticalLayoutCh_2.setSpacing(0)
        self.verticalLayoutCh_2.setObjectName("verticalLayoutCh_2")
        self.pushChButton = QtWidgets.QPushButton(self.frame_Ch_4)
        self.pushChButton.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  margin: 10px 20px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1F5B63;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        self.pushChButton.setObjectName("pushChButton")
        self.verticalLayoutCh_2.addWidget(self.pushChButton)
        self.pushChButton_2 = QtWidgets.QPushButton(self.frame_Ch_4)
        self.pushChButton_2.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "   text-decoration: none;\n"
                                          "  display: inline-block;\n"
                                          "  width: 140px;\n"
                                          "  height: 45px;\n"
                                          "  line-height: 45px;\n"
                                          "  border-radius: 45px;\n"
                                          "  margin: 10px 20px;\n"
                                          "  font-family: \'Montserrat\', sans-serif;\n"
                                          "  font-size: 6px;\n"
                                          "  text-transform: uppercase;\n"
                                          "  text-align: center;\n"
                                          "  letter-spacing: 3px;\n"
                                          "  font-weight: 600;\n"
                                          "  color: white;\n"
                                          "  background: #1F5B63;\n"
                                          "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                          "  transition: .3s;\n"
                                          "}\n"
                                          "QPushButton:hover\n"
                                          "{\n"
                                          "  background: #2EE59D;\n"
                                          "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                          "  color: white;\n"
                                          "  transform: translateY(-7px);}")
        self.pushChButton_2.setObjectName("pushChButton_2")
        self.verticalLayoutCh_2.addWidget(self.pushChButton_2)
        self.pushChButton_3 = QtWidgets.QPushButton(self.frame_Ch_4)
        self.pushChButton_3.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "   text-decoration: none;\n"
                                          "  display: inline-block;\n"
                                          "  width: 140px;\n"
                                          "  height: 45px;\n"
                                          "  line-height: 45px;\n"
                                          "  border-radius: 45px;\n"
                                          "  margin: 10px 20px;\n"
                                          "  font-family: \'Montserrat\', sans-serif;\n"
                                          "  font-size: 6px;\n"
                                          "  text-transform: uppercase;\n"
                                          "  text-align: center;\n"
                                          "  letter-spacing: 3px;\n"
                                          "  font-weight: 600;\n"
                                          "  color: white;\n"
                                          "  background: #1F5B63;\n"
                                          "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                          "  transition: .3s;\n"
                                          "}\n"
                                          "QPushButton:hover\n"
                                          "{\n"
                                          "  background: #2EE59D;\n"
                                          "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                          "  color: white;\n"
                                          "  transform: translateY(-7px);}")
        self.pushChButton_3.setObjectName("pushButton_3")
        self.verticalLayoutCh_2.addWidget(self.pushChButton_3)
        self.pushChButton_4 = QtWidgets.QPushButton(self.frame_Ch_4)
        self.pushChButton_4.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "   text-decoration: none;\n"
                                          "  display: inline-block;\n"
                                          "  width: 140px;\n"
                                          "  height: 45px;\n"
                                          "  line-height: 45px;\n"
                                          "  border-radius: 45px;\n"
                                          "  margin: 10px 20px;\n"
                                          "  font-family: \'Montserrat\', sans-serif;\n"
                                          "  font-size: 6px;\n"
                                          "  text-transform: uppercase;\n"
                                          "  text-align: center;\n"
                                          "  letter-spacing: 3px;\n"
                                          "  font-weight: 600;\n"
                                          "  color: white;\n"
                                          "  background: #1F5B63;\n"
                                          "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                          "  transition: .3s;\n"
                                          "}\n"
                                          "QPushButton:hover\n"
                                          "{\n"
                                          "  background: #2EE59D;\n"
                                          "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                          "  color: white;\n"
                                          "  transform: translateY(-7px);}")
        self.pushChButton_4.setObjectName("pushChButton_4")
        self.verticalLayoutCh_2.addWidget(self.pushChButton_4)
        self.frame_Ch_5 = QtWidgets.QFrame(self.frame_Ch_4)
        self.frame_Ch_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Ch_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Ch_5.setObjectName("frame_Ch_5")
        self.horizontalLayoutCh_2 = QtWidgets.QHBoxLayout(self.frame_Ch_5)
        self.horizontalLayoutCh_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutCh_2.setSpacing(0)
        self.horizontalLayoutCh_2.setObjectName("horizontalLayoutCh_2")
        self.pushChButton_5 = QtWidgets.QPushButton(self.frame_Ch_5)
        self.pushChButton_5.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "   text-decoration: none;\n"
                                          "  display: inline-block;\n"
                                          "  width: 140px;\n"
                                          "  height: 45px;\n"
                                          "  line-height: 45px;\n"
                                          "  border-radius: 45px;\n"
                                          "  font-family: \'Montserrat\', sans-serif;\n"
                                          "  font-size: 6px;\n"
                                          "  text-transform: uppercase;\n"
                                          "  text-align: center;\n"
                                          "  letter-spacing: 3px;\n"
                                          "  font-weight: 600;\n"
                                          "  color: white;\n"
                                          "  background: #1F5B63;\n"
                                          "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                          "  transition: .3s;\n"
                                          "}\n"
                                          "QPushButton:hover\n"
                                          "{\n"
                                          "  background: #2EE59D;\n"
                                          "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                          "  color: white;\n"
                                          "  transform: translateY(-7px);}")
        self.pushChButton_5.setObjectName("pushChButton_5")
        self.horizontalLayoutCh_2.addWidget(self.pushChButton_5)
        self.pushChButton_6 = QtWidgets.QPushButton(self.frame_Ch_5)
        self.pushChButton_6.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "   text-decoration: none;\n"
                                          "  display: inline-block;\n"
                                          "  width: 140px;\n"
                                          "  height: 45px;\n"
                                          "  line-height: 45px;\n"
                                          "  border-radius: 45px;\n"
                                          "  font-family: \'Montserrat\', sans-serif;\n"
                                          "  font-size: 6px;\n"
                                          "  text-transform: uppercase;\n"
                                          "  text-align: center;\n"
                                          "  letter-spacing: 3px;\n"
                                          "  font-weight: 600;\n"
                                          "  color: white;\n"
                                          "  background: #1F5B63;\n"
                                          "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                          "  transition: .3s;\n"
                                          "}\n"
                                          "QPushButton:hover\n"
                                          "{\n"
                                          "  background: #2EE59D;\n"
                                          "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                          "  color: white;\n"
                                          "  transform: translateY(-7px);}")
        self.pushChButton_6.setObjectName("pushChButton_6")
        self.horizontalLayoutCh_2.addWidget(self.pushChButton_6)
        self.verticalLayoutCh_2.addWidget(self.frame_Ch_5, 0, QtCore.Qt.AlignTop)
        self.verticalLayoutCh.addWidget(self.frame_Ch_4)
        self.horizontalLayout.addWidget(self.frame_Ch_2, 0, QtCore.Qt.AlignRight)

        ###########################################################################

        # frame_Ch_2 = frame_Tree_2
        # verticalLayoutCh = verticalLayoutTree
        # frame_ch_4 = frame_tree_4
        # frame_ch_5 = frame_tree_5
        # verticalLayoutCh_2 = verticalLayoutTree_2
        # horizontalLayoutCh_2 = horizontalLayoutTree_2

        self.frame_Tree_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_Tree_2.setMinimumSize(QtCore.QSize(0, 140))
        self.frame_Tree_2.setMaximumSize(QtCore.QSize(0, 16777215))
        self.frame_Tree_2.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_Tree_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Tree_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Tree_2.setObjectName("frame_Tree_2")

        self.verticalLayoutTree = QtWidgets.QVBoxLayout(self.frame_Tree_2)
        self.verticalLayoutTree.setContentsMargins(0, 200, 0, 0)
        self.verticalLayoutTree.setSpacing(0)
        self.verticalLayoutTree.setObjectName("verticalLayoutTree")

        self.frame_Tree_4 = QtWidgets.QFrame(self.frame_Tree_2)
        self.frame_Tree_4.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_Tree_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Tree_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Tree_4.setObjectName("frame_Tree_4")
        self.verticalLayoutTree_2 = QtWidgets.QVBoxLayout(self.frame_Tree_4)
        self.verticalLayoutTree_2.setContentsMargins(0, 25, 0, 0)
        self.verticalLayoutTree_2.setSpacing(0)
        self.verticalLayoutTree_2.setObjectName("verticalLayoutTree_2")
        self.pushTreeButton = QtWidgets.QPushButton(self.frame_Tree_4)
        self.pushTreeButton.setStyleSheet("QPushButton\n"
                                          "{\n"
                                          "   text-decoration: none;\n"
                                          "  display: inline-block;\n"
                                          "  width: 140px;\n"
                                          "  height: 45px;\n"
                                          "  line-height: 45px;\n"
                                          "  border-radius: 45px;\n"
                                          "  margin: 10px 20px;\n"
                                          "  font-family: \'Montserrat\', sans-serif;\n"
                                          "  font-size: 6px;\n"
                                          "  text-transform: uppercase;\n"
                                          "  text-align: center;\n"
                                          "  letter-spacing: 3px;\n"
                                          "  font-weight: 600;\n"
                                          "  color: white;\n"
                                          "  background: #1F5B63;\n"
                                          "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                          "  transition: .3s;\n"
                                          "}\n"
                                          "QPushButton:hover\n"
                                          "{\n"
                                          "  background: #2EE59D;\n"
                                          "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                          "  color: white;\n"
                                          "  transform: translateY(-7px);}")
        self.pushTreeButton.setObjectName("pushTreeButton")
        self.verticalLayoutTree_2.addWidget(self.pushTreeButton)
        self.pushTreeButton_2 = QtWidgets.QPushButton(self.frame_Tree_4)
        self.pushTreeButton_2.setStyleSheet("QPushButton\n"
                                            "{\n"
                                            "   text-decoration: none;\n"
                                            "  display: inline-block;\n"
                                            "  width: 140px;\n"
                                            "  height: 45px;\n"
                                            "  line-height: 45px;\n"
                                            "  border-radius: 45px;\n"
                                            "  margin: 10px 20px;\n"
                                            "  font-family: \'Montserrat\', sans-serif;\n"
                                            "  font-size: 6px;\n"
                                            "  text-transform: uppercase;\n"
                                            "  text-align: center;\n"
                                            "  letter-spacing: 3px;\n"
                                            "  font-weight: 600;\n"
                                            "  color: white;\n"
                                            "  background: #1F5B63;\n"
                                            "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                            "  transition: .3s;\n"
                                            "}\n"
                                            "QPushButton:hover\n"
                                            "{\n"
                                            "  background: #2EE59D;\n"
                                            "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                            "  color: white;\n"
                                            "  transform: translateY(-7px);}")
        self.pushTreeButton_2.setObjectName("pushTreeButton_2")
        self.verticalLayoutTree_2.addWidget(self.pushTreeButton_2)
        self.pushTreeButton_3 = QtWidgets.QPushButton(self.frame_Tree_4)
        self.pushTreeButton_3.setStyleSheet("QPushButton\n"
                                            "{\n"
                                            "   text-decoration: none;\n"
                                            "  display: inline-block;\n"
                                            "  width: 140px;\n"
                                            "  height: 45px;\n"
                                            "  line-height: 45px;\n"
                                            "  border-radius: 45px;\n"
                                            "  margin: 10px 20px;\n"
                                            "  font-family: \'Montserrat\', sans-serif;\n"
                                            "  font-size: 6px;\n"
                                            "  text-transform: uppercase;\n"
                                            "  text-align: center;\n"
                                            "  letter-spacing: 3px;\n"
                                            "  font-weight: 600;\n"
                                            "  color: white;\n"
                                            "  background: #1F5B63;\n"
                                            "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                            "  transition: .3s;\n"
                                            "}\n"
                                            "QPushButton:hover\n"
                                            "{\n"
                                            "  background: #2EE59D;\n"
                                            "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                            "  color: white;\n"
                                            "  transform: translateY(-7px);}")
        self.pushTreeButton_3.setObjectName("pushTreeButton_3")
        self.verticalLayoutTree_2.addWidget(self.pushTreeButton_3)
        self.frame_Tree_5 = QtWidgets.QFrame(self.frame_Tree_4)
        self.frame_Tree_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Tree_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Tree_5.setObjectName("frame_Tree_5")
        self.horizontalLayoutTree_2 = QtWidgets.QHBoxLayout(self.frame_Tree_5)
        self.horizontalLayoutTree_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutTree_2.setSpacing(0)
        self.horizontalLayoutTree_2.setObjectName("horizontalLayoutTree_2")
        self.verticalLayoutTree_2.addWidget(self.frame_Tree_5, 0, QtCore.Qt.AlignTop)
        self.verticalLayoutTree.addWidget(self.frame_Tree_4)
        self.horizontalLayout.addWidget(self.frame_Tree_2, 0, QtCore.Qt.AlignRight)

        ###########################################################################

        # frame_Tree_2 = frame_Head_2
        # verticalLayoutTree = verticalLayoutHead
        # frame_tree_4 = frame_Head_4
        # frame_tree_5 = frame_Head_5
        # verticalLayoutTree_2 = verticalLayoutHead_2
        # horizontalLayoutTree_2 = horizontalLayoutHead_2

        self.frame_Head_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_Head_2.setMinimumSize(QtCore.QSize(0, 140))
        self.frame_Head_2.setMaximumSize(QtCore.QSize(0, 16777215))
        self.frame_Head_2.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_Head_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Head_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Head_2.setObjectName("frame_Head_2")

        self.verticalLayoutHead = QtWidgets.QVBoxLayout(self.frame_Head_2)
        self.verticalLayoutHead.setContentsMargins(0, 200, 0, 0)
        self.verticalLayoutHead.setSpacing(0)
        self.verticalLayoutHead.setObjectName("verticalLayoutHead")

        self.frame_Head_4 = QtWidgets.QFrame(self.frame_Head_2)
        self.frame_Head_4.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_Head_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Head_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Head_4.setObjectName("frame_Head_4")
        self.verticalLayoutHead_2 = QtWidgets.QVBoxLayout(self.frame_Head_4)
        self.verticalLayoutHead_2.setContentsMargins(0, 25, 0, 0)
        self.verticalLayoutHead_2.setSpacing(0)
        self.verticalLayoutHead_2.setObjectName("verticalLayoutHead_2")
        self.pushHeadButton_1 = QtWidgets.QPushButton(self.frame_Head_4)
        self.pushHeadButton_1.setStyleSheet("QPushButton\n"
                                            "{\n"
                                            "   text-decoration: none;\n"
                                            "  display: inline-block;\n"
                                            "  width: 140px;\n"
                                            "  height: 45px;\n"
                                            "  line-height: 45px;\n"
                                            "  border-radius: 45px;\n"
                                            "  margin: 10px 20px;\n"
                                            "  font-family: \'Montserrat\', sans-serif;\n"
                                            "  font-size: 6px;\n"
                                            "  text-transform: uppercase;\n"
                                            "  text-align: center;\n"
                                            "  letter-spacing: 3px;\n"
                                            "  font-weight: 600;\n"
                                            "  color: white;\n"
                                            "  background: #1F5B63;\n"
                                            "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                            "  transition: .3s;\n"
                                            "}\n"
                                            "QPushButton:hover\n"
                                            "{\n"
                                            "  background: #2EE59D;\n"
                                            "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                            "  color: white;\n"
                                            "  transform: translateY(-7px);}")
        self.pushHeadButton_1.setObjectName("pushHeadButton_1")
        self.verticalLayoutHead_2.addWidget(self.pushHeadButton_1)
        self.pushHeadButton_2 = QtWidgets.QPushButton(self.frame_Head_4)
        self.pushHeadButton_2.setStyleSheet("QPushButton\n"
                                            "{\n"
                                            "   text-decoration: none;\n"
                                            "  display: inline-block;\n"
                                            "  width: 140px;\n"
                                            "  height: 45px;\n"
                                            "  line-height: 45px;\n"
                                            "  border-radius: 45px;\n"
                                            "  margin: 10px 20px;\n"
                                            "  font-family: \'Montserrat\', sans-serif;\n"
                                            "  font-size: 6px;\n"
                                            "  text-transform: uppercase;\n"
                                            "  text-align: center;\n"
                                            "  letter-spacing: 3px;\n"
                                            "  font-weight: 600;\n"
                                            "  color: white;\n"
                                            "  background: #1F5B63;\n"
                                            "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                            "  transition: .3s;\n"
                                            "}\n"
                                            "QPushButton:hover\n"
                                            "{\n"
                                            "  background: #2EE59D;\n"
                                            "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                            "  color: white;\n"
                                            "  transform: translateY(-7px);}")
        self.pushHeadButton_2.setObjectName("pushHeadButton_2")
        self.verticalLayoutHead_2.addWidget(self.pushHeadButton_2)
        self.pushHeadButton_3 = QtWidgets.QPushButton(self.frame_Head_4)
        self.pushHeadButton_3.setStyleSheet("QPushButton\n"
                                            "{\n"
                                            "   text-decoration: none;\n"
                                            "  display: inline-block;\n"
                                            "  width: 140px;\n"
                                            "  height: 45px;\n"
                                            "  line-height: 45px;\n"
                                            "  border-radius: 45px;\n"
                                            "  margin: 10px 20px;\n"
                                            "  font-family: \'Montserrat\', sans-serif;\n"
                                            "  font-size: 6px;\n"
                                            "  text-transform: uppercase;\n"
                                            "  text-align: center;\n"
                                            "  letter-spacing: 3px;\n"
                                            "  font-weight: 600;\n"
                                            "  color: white;\n"
                                            "  background: #1F5B63;\n"
                                            "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                            "  transition: .3s;\n"
                                            "}\n"
                                            "QPushButton:hover\n"
                                            "{\n"
                                            "  background: #2EE59D;\n"
                                            "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                            "  color: white;\n"
                                            "  transform: translateY(-7px);}")
        self.pushHeadButton_3.setObjectName("pushTreeButton_3")
        self.verticalLayoutHead_2.addWidget(self.pushHeadButton_3)
        self.frame_Head_5 = QtWidgets.QFrame(self.frame_Head_4)
        self.frame_Head_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_Head_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_Head_5.setObjectName("frame_Head_5")

        self.verticalLayoutHead_2.addWidget(self.frame_Head_5, 0, QtCore.Qt.AlignTop)
        self.verticalLayoutHead.addWidget(self.frame_Head_4)
        self.horizontalLayout.addWidget(self.frame_Head_2, 0, QtCore.Qt.AlignRight)

        ###########################################################################

        # frame_Head_2 = frame_HeadCh_2
        # verticalLayoutHead = verticalLayoutHeadCh
        # frame_Head_4 = frame_HeadCh_4
        # frame_Head_5 = frame_HeadCh_5
        # verticalLayoutHead_2 = verticalLayoutHeadCh_2
        # horizontalLayoutHead_2 = horizontalLayoutHeadCh_2

        self.frame_HeadCh_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_HeadCh_2.setMinimumSize(QtCore.QSize(0, 140))
        self.frame_HeadCh_2.setMaximumSize(QtCore.QSize(0, 16777215))
        self.frame_HeadCh_2.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_HeadCh_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_HeadCh_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_HeadCh_2.setObjectName("frame_HeadCh_2")

        self.verticalLayoutHeadCh = QtWidgets.QVBoxLayout(self.frame_HeadCh_2)
        self.verticalLayoutHeadCh.setContentsMargins(0, 200, 0, 0)
        self.verticalLayoutHeadCh.setSpacing(0)
        self.verticalLayoutHeadCh.setObjectName("verticalLayoutHeadCh")

        self.frame_HeadCh_4 = QtWidgets.QFrame(self.frame_HeadCh_2)
        self.frame_HeadCh_4.setStyleSheet("background-color: rgb(77, 185, 136);")
        self.frame_HeadCh_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_HeadCh_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_HeadCh_4.setObjectName("frame_HeadCh_4")
        self.verticalLayoutHeadCh_2 = QtWidgets.QVBoxLayout(self.frame_HeadCh_4)
        self.verticalLayoutHeadCh_2.setContentsMargins(0, 25, 0, 0)
        self.verticalLayoutHeadCh_2.setSpacing(0)
        self.verticalLayoutHeadCh_2.setObjectName("verticalLayoutHeadCh_2")
        self.pushHeadChButton_1 = QtWidgets.QPushButton(self.frame_HeadCh_4)
        self.pushHeadChButton_1.setStyleSheet("QPushButton\n"
                                              "{\n"
                                              "   text-decoration: none;\n"
                                              "  display: inline-block;\n"
                                              "  width: 140px;\n"
                                              "  height: 45px;\n"
                                              "  line-height: 45px;\n"
                                              "  border-radius: 45px;\n"
                                              "  margin: 10px 20px;\n"
                                              "  font-family: \'Montserrat\', sans-serif;\n"
                                              "  font-size: 6px;\n"
                                              "  text-transform: uppercase;\n"
                                              "  text-align: center;\n"
                                              "  letter-spacing: 3px;\n"
                                              "  font-weight: 600;\n"
                                              "  color: white;\n"
                                              "  background: #1F5B63;\n"
                                              "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                              "  transition: .3s;\n"
                                              "}\n"
                                              "QPushButton:hover\n"
                                              "{\n"
                                              "  background: #2EE59D;\n"
                                              "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                              "  color: white;\n"
                                              "  transform: translateY(-7px);}")
        self.pushHeadChButton_1.setObjectName("pushHeadChButton_1")
        self.verticalLayoutHeadCh_2.addWidget(self.pushHeadChButton_1)
        self.pushHeadChButton_2 = QtWidgets.QPushButton(self.frame_HeadCh_4)
        self.pushHeadChButton_2.setStyleSheet("QPushButton\n"
                                              "{\n"
                                              "   text-decoration: none;\n"
                                              "  display: inline-block;\n"
                                              "  width: 140px;\n"
                                              "  height: 45px;\n"
                                              "  line-height: 45px;\n"
                                              "  border-radius: 45px;\n"
                                              "  margin: 10px 20px;\n"
                                              "  font-family: \'Montserrat\', sans-serif;\n"
                                              "  font-size: 6px;\n"
                                              "  text-transform: uppercase;\n"
                                              "  text-align: center;\n"
                                              "  letter-spacing: 3px;\n"
                                              "  font-weight: 600;\n"
                                              "  color: white;\n"
                                              "  background: #1F5B63;\n"
                                              "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                              "  transition: .3s;\n"
                                              "}\n"
                                              "QPushButton:hover\n"
                                              "{\n"
                                              "  background: #2EE59D;\n"
                                              "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                              "  color: white;\n"
                                              "  transform: translateY(-7px);}")
        self.pushHeadChButton_2.setObjectName("pushHeadChButton_2")
        self.verticalLayoutHeadCh_2.addWidget(self.pushHeadChButton_2)
        self.pushHeadChButton_3 = QtWidgets.QPushButton(self.frame_HeadCh_4)
        self.pushHeadChButton_3.setStyleSheet("QPushButton\n"
                                              "{\n"
                                              "   text-decoration: none;\n"
                                              "  display: inline-block;\n"
                                              "  width: 140px;\n"
                                              "  height: 45px;\n"
                                              "  line-height: 45px;\n"
                                              "  border-radius: 45px;\n"
                                              "  margin: 10px 20px;\n"
                                              "  font-family: \'Montserrat\', sans-serif;\n"
                                              "  font-size: 6px;\n"
                                              "  text-transform: uppercase;\n"
                                              "  text-align: center;\n"
                                              "  letter-spacing: 3px;\n"
                                              "  font-weight: 600;\n"
                                              "  color: white;\n"
                                              "  background: #1F5B63;\n"
                                              "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                              "  transition: .3s;\n"
                                              "}\n"
                                              "QPushButton:hover\n"
                                              "{\n"
                                              "  background: #2EE59D;\n"
                                              "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                              "  color: white;\n"
                                              "  transform: translateY(-7px);}")
        self.pushHeadChButton_3.setObjectName("pushHeadChButton_3")
        self.verticalLayoutHeadCh_2.addWidget(self.pushHeadChButton_3)
        self.frame_HeadCh_5 = QtWidgets.QFrame(self.frame_HeadCh_4)
        self.frame_HeadCh_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_HeadCh_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_HeadCh_5.setObjectName("frame_HeadCh_5")

        self.frame_HeadCh_5 = QtWidgets.QFrame(self.frame_HeadCh_4)
        self.frame_HeadCh_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_HeadCh_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_HeadCh_5.setObjectName("frame_Head_5")

        self.verticalLayoutHeadCh_2.addWidget(self.frame_HeadCh_5, 0, QtCore.Qt.AlignTop)
        self.verticalLayoutHeadCh.addWidget(self.frame_HeadCh_4)
        self.horizontalLayout.addWidget(self.frame_HeadCh_2, 0, QtCore.Qt.AlignRight)

        MainWindow.setCentralWidget(self.centralwidget)
        self.main.view.add_fish(600, 800)
        timer = QTimer()
        timer.singleShot(100, self.main.view.Starter)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_9.setText(_translate("MainWindow", "?"))
        self.pushButton_7.setText(_translate("MainWindow", "S"))
        self.pushButton_8.setText(_translate("MainWindow", "L"))

        self.pushButton.setText(_translate("MainWindow", "Указать название"))
        self.pushButton_2.setText(_translate("MainWindow", "Указать содержание"))
        self.pushButton_3.setText(_translate("MainWindow", "Указать приоритет"))
        self.pushButton_4.setText(_translate("MainWindow", "Указать дедлайн"))
        self.pushButton_5.setText(_translate("MainWindow", "Подтвердить"))
        self.pushButton_6.setText(_translate("MainWindow", "Вернуться"))

        self.pushChButton.setText(_translate("MainWindow", "Указать название"))
        self.pushChButton_2.setText(_translate("MainWindow", "Указать содержание"))
        self.pushChButton_3.setText(_translate("MainWindow", "Указать приоритет"))
        self.pushChButton_4.setText(_translate("MainWindow", "Указать дедлайн"))
        self.pushChButton_5.setText(_translate("MainWindow", "Подтвердить"))
        self.pushChButton_6.setText(_translate("MainWindow", "Вернуться"))

        self.pushTreeButton.setText(_translate("MainWindow", "Просмотр"))
        self.pushTreeButton_2.setText(_translate("MainWindow", "Указать название"))
        self.pushTreeButton_3.setText(_translate("MainWindow", "Вернуться"))

        self.pushButtonViewing_1.setText(_translate("MainWindow", "Просмотр"))
        self.pushButtonViewing_2.setText(_translate("MainWindow", "Редактировать"))
        self.pushButtonViewing_3.setText(_translate("MainWindow", "Выполнить"))
        self.pushButtonViewing_4.setText(_translate("MainWindow", "Вернуться"))

        self.pushHeadButton_1.setText(_translate("MainWindow", "Просмотр"))
        self.pushHeadButton_2.setText(_translate("MainWindow", "Редактировать"))
        self.pushHeadButton_3.setText(_translate("MainWindow", "Вернуться"))

        self.pushHeadChButton_1.setText(_translate("MainWindow", "Указать название"))
        self.pushHeadChButton_2.setText(_translate("MainWindow", "Указать содержание"))
        self.pushHeadChButton_3.setText(_translate("MainWindow", "Приянть"))

        self.pushButton_accept.setText(_translate("MainWindow", "Принять"))

        self.pushButton.clicked.connect(self.setName)
        self.pushButton_6.clicked.connect(self.close)
        self.pushButton_2.clicked.connect(self.setInfo)
        self.pushButton_3.clicked.connect(self.setPrioritet)
        self.pushButton_4.clicked.connect(self.setDeadLine)
        self.pushButton_5.clicked.connect(self.PAccept)
        self.pushButton_7.clicked.connect(self.SaveInfo)
        self.pushButton_8.clicked.connect(self.LoadInfo)
        self.pushButton_5.setEnabled(False)
        self.pushButton_5.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1E5945;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n")
        self.pushButton_accept.clicked.connect(self.move_node_close)
        self.pushButtonViewing_4.clicked.connect(self.viewingClose)
        self.pushButtonViewing_1.clicked.connect(self.show_info)
        self.pushButtonViewing_2.clicked.connect(self.showEditor)
        self.pushButtonViewing_3.clicked.connect(self.complete)
        self.pushChButton.clicked.connect(self.setNameEditor)
        self.pushChButton_2.clicked.connect(self.setInfoEditor)
        self.pushChButton_3.clicked.connect(self.setPrioritetEditor)
        self.pushChButton_4.clicked.connect(self.setDeadLineEditor)
        self.pushChButton_5.clicked.connect(self.AccepterEditor)
        self.pushChButton_6.clicked.connect(self.closeEditor)

        self.pushTreeButton.clicked.connect(self.showInfoFish)
        self.pushTreeButton_2.clicked.connect(self.setNameTree)
        self.pushTreeButton_3.clicked.connect(self.TreeClose)

        self.pushHeadButton_2.clicked.connect(self.showHeadEditor)
        self.pushHeadButton_3.clicked.connect(self.HeadClose)
        self.pushHeadChButton_1.clicked.connect(self.setNameFish)
        self.pushHeadChButton_2.clicked.connect(self.setInfoFish)
        self.pushHeadChButton_3.clicked.connect(self.HeadChClose)
        self.pushHeadButton_1.clicked.connect(self.show_info_fish)

    def setNameTree(self):
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint
        input_dialog, ok = QInputDialog.getText(self, 'Input Dialog', 'Название:', flags=flags)
        if ok:
            self.tree._name = input_dialog
        else:
            self.tree._name = ""

    def showInfoFish(self):
        info = ShowTree(self.tree)
        info.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        info.exec_()

    def SaveInfo(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "unnamed", "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                for i in range(8, len(ui.main.view._nodes_map)):
                    name = ui.main.view._nodes_map[f"{i + 1}"]._name
                    if name == -1:
                        continue
                    position = ui.main.view._nodes_map[f"{i + 1}"]._position
                    prioritet = ui.main.view._nodes_map[f"{i + 1}"]._prioritet
                    main_name = ui.main.view._nodes_map[f"{i + 1}"]._main_name
                    main_info = ui.main.view._nodes_map[f"{i + 1}"]._main_info
                    date_days = ui.main.view._nodes_map[f"{i + 1}"]._date_days
                    end_day = ui.main.view._nodes_map[f"{i + 1}"]._end_day
                    accept = ui.main.view._nodes_map[f"{i + 1}"]._accept
                    file.write(
                        f"{name}:{position}:{prioritet}:{main_name}:{main_info}:{date_days}:{end_day}:{accept}" + "\n")
                file.write("\n")
                for i in range(len(ui.main.graph.adj)):
                    edge = ui.main.graph.adj[f"{i + 1}"]
                    file.write(str(edge) + "\n")

    def LoadInfo(self):
        f = open("nodes.txt")
        file_dialog = QFileDialog()
        file_name, _ = file_dialog.lo(self, "Save File", "unnamed", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'w') as file:
                f.writelines(file.readlines())

    def complete(self):
        self.g._accept = 1
        self.g._color = "green"
        self.g._prioritet = "green"
        self.g.update()
        self.pushButtonViewing_3.setEnabled(False)
        self.pushButtonViewing_3.setStyleSheet("QPushButton\n"
                                               "{\n"
                                               "   text-decoration: none;\n"
                                               "  display: inline-block;\n"
                                               "  width: 140px;\n"
                                               "  height: 45px;\n"
                                               "  line-height: 45px;\n"
                                               "  border-radius: 45px;\n"
                                               "  margin: 10px 20px;\n"
                                               "  font-family: \'Montserrat\', sans-serif;\n"
                                               "  font-size: 6px;\n"
                                               "  text-transform: uppercase;\n"
                                               "  text-align: center;\n"
                                               "  letter-spacing: 3px;\n"
                                               "  font-weight: 600;\n"
                                               "  color: white;\n"
                                               "  background: #1E5945;\n"
                                               "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                               "  transition: .3s;\n"
                                               "}\n"
                                               "QPushButton:hover\n"
                                               "{\n"
                                               "  background: green;\n"
                                               "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                               "  color: white;\n"
                                               "  transform: translateY(-7px);}")
        self.pushButtonViewing_2.setEnabled(False)
        self.pushButtonViewing_2.setStyleSheet("QPushButton\n"
                                               "{\n"
                                               "   text-decoration: none;\n"
                                               "  display: inline-block;\n"
                                               "  width: 140px;\n"
                                               "  height: 45px;\n"
                                               "  line-height: 45px;\n"
                                               "  border-radius: 45px;\n"
                                               "  margin: 10px 20px;\n"
                                               "  font-family: \'Montserrat\', sans-serif;\n"
                                               "  font-size: 6px;\n"
                                               "  text-transform: uppercase;\n"
                                               "  text-align: center;\n"
                                               "  letter-spacing: 3px;\n"
                                               "  font-weight: 600;\n"
                                               "  color: white;\n"
                                               "  background: #1E5945;\n"
                                               "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                               "  transition: .3s;\n"
                                               "}\n"
                                               "QPushButton:hover\n"
                                               "{\n"
                                               "  background: #2EE59D;\n"
                                               "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                               "  color: white;\n"
                                               "  transform: translateY(-7px);}")

    def showHeadEditor(self):
        toggleHeadMenu(ui, 0, True)
        toggleHeadChMenu(ui, 170, True)

    def showEditor(self):
        toggleViewingMenu(ui, 0, True)
        self.prioritet = self.g._prioritet
        self.main_name = self.g._main_name
        self.main_info = self.g._main_info
        self._date_days = self.g._date_days
        toggleChangeMenu(ui, 170, True)

    def showTree(self,item):
        self.tree = item
        self.main.view.check_tree = 0
        toggleTreeMenu(ui, 170, True)

    def setNameFish(self):
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint
        input_dialog, ok = QInputDialog.getText(self, 'Input Dialog', 'Название:', flags=flags)
        if ok:
            self.main.view.fish._main_name = input_dialog
            self.main.view.text_item.setPlainText(f"{input_dialog}")
            self.main.view.text_item.setPos(2880 - len(input_dialog) * 5, self.main.view.text_item.pos().y())
            self.main.view.text_item.update()
        else:
            self.main.view.fish._main_name = ""
            self.main.view.text_item.setPlainText("")

    def setInfoFish(self):
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint
        input_dialog, ok = QInputDialog.getText(self, 'Input Dialog', 'Название:', flags=flags)
        if ok:
            self.main.view.fish._main_info = input_dialog
        else:
            self.main.view.fish._main_info = ""

    def showHead(self):
        toggleHeadMenu(ui, 170, True)

    def show_info(self):
        info = ShowInfo(self.g)
        info.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        info.exec_()

    def show_info_fish(self):
        info = ShowFish(self.main.view.fish)
        info.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        info.exec_()

    def make_node(self):
        ui.main.view.check = 0
        toggleMenu(ui, 170, True)
        ui.Create.view.add_node()
        ui.Create.view._nodes_map[0].update()

    def viewing(self, item):
        self.g = item
        toggleViewingMenu(ui, 170, True)
        self.main.view.NodeNotMovible()
        if self.g._accept == 1 or self.g._accept == -1:
            self.pushButtonViewing_2.setEnabled(False)
            self.pushButtonViewing_2.setStyleSheet("QPushButton\n"
                                                   "{\n"
                                                   "   text-decoration: none;\n"
                                                   "  display: inline-block;\n"
                                                   "  width: 140px;\n"
                                                   "  height: 45px;\n"
                                                   "  line-height: 45px;\n"
                                                   "  border-radius: 45px;\n"
                                                   "  margin: 10px 20px;\n"
                                                   "  font-family: \'Montserrat\', sans-serif;\n"
                                                   "  font-size: 6px;\n"
                                                   "  text-transform: uppercase;\n"
                                                   "  text-align: center;\n"
                                                   "  letter-spacing: 3px;\n"
                                                   "  font-weight: 600;\n"
                                                   "  color: white;\n"
                                                   "  background: #1E5945;\n"
                                                   "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                                   "  transition: .3s;\n"
                                                   "}\n"
                                                   "QPushButton:hover\n"
                                                   "{\n"
                                                   "  background: #2EE59D;\n"
                                                   "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                                   "  color: white;\n"
                                                   "  transform: translateY(-7px);}")
            self.pushButtonViewing_3.setEnabled(False)
            self.pushButtonViewing_3.setStyleSheet("QPushButton\n"
                                                   "{\n"
                                                   "   text-decoration: none;\n"
                                                   "  display: inline-block;\n"
                                                   "  width: 140px;\n"
                                                   "  height: 45px;\n"
                                                   "  line-height: 45px;\n"
                                                   "  border-radius: 45px;\n"
                                                   "  margin: 10px 20px;\n"
                                                   "  font-family: \'Montserrat\', sans-serif;\n"
                                                   "  font-size: 6px;\n"
                                                   "  text-transform: uppercase;\n"
                                                   "  text-align: center;\n"
                                                   "  letter-spacing: 3px;\n"
                                                   "  font-weight: 600;\n"
                                                   "  color: white;\n"
                                                   "  background: #1E5945;\n"
                                                   "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                                   "  transition: .3s;\n"
                                                   "}\n"
                                                   "QPushButton:hover\n"
                                                   "{\n"
                                                   "  background: green;\n"
                                                   "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                                   "  color: white;\n"
                                                   "  transform: translateY(-7px);}")
        else:
            self.pushButtonViewing_2.setEnabled(True)
            self.pushButtonViewing_2.setStyleSheet("QPushButton\n"
                                                   "{\n"
                                                   "   text-decoration: none;\n"
                                                   "  display: inline-block;\n"
                                                   "  width: 140px;\n"
                                                   "  height: 45px;\n"
                                                   "  line-height: 45px;\n"
                                                   "  border-radius: 45px;\n"
                                                   "  margin: 10px 20px;\n"
                                                   "  font-family: \'Montserrat\', sans-serif;\n"
                                                   "  font-size: 6px;\n"
                                                   "  text-transform: uppercase;\n"
                                                   "  text-align: center;\n"
                                                   "  letter-spacing: 3px;\n"
                                                   "  font-weight: 600;\n"
                                                   "  color: white;\n"
                                                   "  background: #1F5B63;\n"
                                                   "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                                   "  transition: .3s;\n"
                                                   "}\n"
                                                   "QPushButton:hover\n"
                                                   "{\n"
                                                   "  background: #2EE59D;\n"
                                                   "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                                   "  color: white;\n"
                                                   "  transform: translateY(-7px);}")
            self.pushButtonViewing_3.setEnabled(True)
            self.pushButtonViewing_3.setStyleSheet("QPushButton\n"
                                                   "{\n"
                                                   "   text-decoration: none;\n"
                                                   "  display: inline-block;\n"
                                                   "  width: 140px;\n"
                                                   "  height: 45px;\n"
                                                   "  line-height: 45px;\n"
                                                   "  border-radius: 45px;\n"
                                                   "  margin: 10px 20px;\n"
                                                   "  font-family: \'Montserrat\', sans-serif;\n"
                                                   "  font-size: 6px;\n"
                                                   "  text-transform: uppercase;\n"
                                                   "  text-align: center;\n"
                                                   "  letter-spacing: 3px;\n"
                                                   "  font-weight: 600;\n"
                                                   "  color: white;\n"
                                                   "  background: #1F5B63;\n"
                                                   "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                                   "  transition: .3s;\n"
                                                   "}\n"
                                                   "QPushButton:hover\n"
                                                   "{\n"
                                                   "  background: #2EE59D;\n"
                                                   "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                                   "  color: white;\n"
                                                   "  transform: translateY(-7px);}")

    def viewingClose(self):
        toggleViewingMenu(ui, 0, True)
        self.main.view.check_node = 1
        timer = QTimer()
        timer.singleShot(100, self.MenuClose)
        self.main.view.NodeMovible()

    def HeadChClose(self):
        toggleHeadChMenu(ui, 0, True)
        timer = QTimer()
        timer.singleShot(100, self.MenuHeadClose)

    def HeadClose(self):
        toggleHeadMenu(ui, 0, True)
        timer = QTimer()
        timer.singleShot(100, self.MenuHeadClose)

    def MenuHeadClose(self):
        ui.main.view.resetTransform()
        ui.main.view.centerOn(self.main.view.sceneRect().width() / 2, self.main.view.sceneRect().height() / 2)
        self.main.view.scale(0.5, 0.5)

    def TreeClose(self):
        toggleTreeMenu(ui, 0, True)
        self.main.view.NodeMovible()
        self.main.view.check_tree = 1
        timer = QTimer()
        timer.singleShot(100, self.MenuTreeClose)

    def AccepterEditor(self):
        toggleChangeMenu(ui, 0, True)
        toggleViewingMenu(ui, 170, True)

    def closeEditor(self):
        self.g._prioritet = self.prioritet
        self.g._main_name = self.main_name
        self.g._main_info = self.main_info
        self.g._date_days = self._date_days
        self.g.update()
        toggleChangeMenu(ui, 0, True)
        toggleViewingMenu(ui, 170, True)

    def MenuTreeClose(self):
        self.main.view.DrawColorGraph()
        ui.main.view.resetTransform()
        ui.main.view.centerOn(self.main.view.sceneRect().width() / 2, self.main.view.sceneRect().height() / 2)
        self.main.view.scale(0.5, 0.5)

    def MenuClose(self):
        self.g.setFlag(QGraphicsItem.ItemIsMovable, True)
        ui.main.view.resetTransform()
        ui.main.view.centerOn(self.main.view.sceneRect().width() / 2, self.main.view.sceneRect().height() / 2)
        self.main.view.scale(0.5, 0.5)

    def setName(self):
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint
        input_dialog, ok = QInputDialog.getText(self, 'Input Dialog', 'Название:', flags=flags)
        if ok:
            ui.Create.view._nodes_map[0]._main_name = input_dialog
            ui.Create.view._nodes_map[0].update()
            self.Accept()
        else:
            ui.Create.view._nodes_map[0]._main_name = ""
            ui.Create.view._nodes_map[0].update()
            self.Accept()

    def close(self):
        toggleMenu(ui, 0, True)
        ui.main.view.check = 2
        ui.Create.view.setStyleSheet("background-color: #1E5945;")
        self.pushButton_5.setEnabled(False)
        self.pushButton_5.setStyleSheet("QPushButton\n"
                                        "{\n"
                                        "   text-decoration: none;\n"
                                        "  display: inline-block;\n"
                                        "  width: 140px;\n"
                                        "  height: 45px;\n"
                                        "  line-height: 45px;\n"
                                        "  border-radius: 45px;\n"
                                        "  font-family: \'Montserrat\', sans-serif;\n"
                                        "  font-size: 6px;\n"
                                        "  text-transform: uppercase;\n"
                                        "  text-align: center;\n"
                                        "  letter-spacing: 3px;\n"
                                        "  font-weight: 600;\n"
                                        "  color: white;\n"
                                        "  background: #1E5945;\n"
                                        "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                        "  transition: .3s;\n"
                                        "}\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "  background: #2EE59D;\n"
                                        "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                        "  color: white;\n"
                                        "  transform: translateY(-7px);}")
        ui.Create.view._nodes_map[0].setFlag(QGraphicsItem.ItemIsMovable, False)
        ui.Create.view._nodes_map[0].setPos(75, 30)

    def setInfo(self):
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint
        input_dialog, ok = QInputDialog.getText(self, 'Input Dialog', 'Содержание:', flags=flags)
        if ok:
            ui.Create.view._nodes_map[0]._main_info = input_dialog
            ui.Create.view._nodes_map[0].update()
            self.Accept()
        else:
            ui.Create.view._nodes_map[0]._main_info = ""
            ui.Create.view._nodes_map[0].update()
            self.Accept()

    def setPrioritet(self):
        dialog = ChangeColor()
        dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        dialog.exec_()
        ui.Create.view._nodes_map[0]._prioritet = dialog._color
        ui.Create.view._nodes_map[0].update()
        self.Accept()

    def setDeadLine(self):
        time = TimeWidget(ui.Create.view._nodes_map[0])
        time.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        time.exec_()
        v = time.days
        ui.Create.view._nodes_map[0]._date_days = v
        ui.Create.view._nodes_map[0].update()
        self.Accept()

    def Accept(self):
        if (ui.Create.view._nodes_map[0]._date_days != "") and (
                ui.Create.view._nodes_map[0]._prioritet != "#007682") and (
                ui.Create.view._nodes_map[0]._main_info != "") and (ui.Create.view._nodes_map[0]._main_name != ""):
            self.pushButton_5.setEnabled(True)
            self.pushButton_5.setStyleSheet("QPushButton\n"
                                            "{\n"
                                            "   text-decoration: none;\n"
                                            "  display: inline-block;\n"
                                            "  width: 140px;\n"
                                            "  height: 45px;\n"
                                            "  line-height: 45px;\n"
                                            "  border-radius: 45px;\n"
                                            "  font-family: \'Montserrat\', sans-serif;\n"
                                            "  font-size: 6px;\n"
                                            "  text-transform: uppercase;\n"
                                            "  text-align: center;\n"
                                            "  letter-spacing: 3px;\n"
                                            "  font-weight: 600;\n"
                                            "  color: white;\n"
                                            "  background: #1F5B63;\n"
                                            "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                            "  transition: .3s;\n"
                                            "}\n"
                                            "QPushButton:hover\n"
                                            "{\n"
                                            "  background: #2EE59D;\n"
                                            "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                            "  color: white;\n"
                                            "  transform: translateY(-7px);}")
        else:
            ui.Create.view.setStyleSheet("background-color: #1E5945;")
            self.pushButton_5.setEnabled(False)
            self.pushButton_5.setStyleSheet("QPushButton\n"
                                            "{\n"
                                            "   text-decoration: none;\n"
                                            "  display: inline-block;\n"
                                            "  width: 140px;\n"
                                            "  height: 45px;\n"
                                            "  line-height: 45px;\n"
                                            "  border-radius: 45px;\n"
                                            "  font-family: \'Montserrat\', sans-serif;\n"
                                            "  font-size: 6px;\n"
                                            "  text-transform: uppercase;\n"
                                            "  text-align: center;\n"
                                            "  letter-spacing: 3px;\n"
                                            "  font-weight: 600;\n"
                                            "  color: white;\n"
                                            "  background: #1E5945;\n"
                                            "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                            "  transition: .3s;\n"
                                            "}\n"
                                            "QPushButton:hover\n"
                                            "{\n"
                                            "  background: #2EE59D;\n"
                                            "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                            "  color: white;\n"
                                            "  transform: translateY(-7px);}")
            ui.Create.view._nodes_map[0].setFlag(QGraphicsItem.ItemIsMovable, False)
            ui.Create.view._nodes_map[0].setPos(75, 30)

    def PAccept(self):
        ui.Create.view.setStyleSheet("background-color: #2E8B57;")
        ui.Create.view._nodes_map[0].setFlag(QGraphicsItem.ItemIsMovable, True)
        ui.Create.view.Timer()

    def move_node(self):
        if ui.main.view.check == 2:
            toggleTopMenu(ui, 60, True)
            ui.main.view.check2 = 0
            ui.frame_6.hide()
            ui.frame_7.hide()
            ui.verticalLayout_3.setContentsMargins(0, 0, 0, 25)

    def move_node_close(self):
        toggleTopMenu(ui, 0, True)
        ui.frame_6.show()
        ui.frame_7.show()
        ui.main.view.check2 = 1
        ui.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

    def setNameEditor(self):
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint
        input_dialog, ok = QInputDialog.getText(self, 'Input Dialog', 'Название:', flags=flags)
        if ok:
            self.g._main_name = input_dialog
            self.g.update()
            self.AcceptEditor()

        else:
            self.g._main_name = ""
            self.g.update()
            self.AcceptEditor()

    def setInfoEditor(self):
        flags = QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint
        input_dialog, ok = QInputDialog.getText(self, 'Input Dialog', 'Содержание:', flags=flags)
        if ok:
            self.g._main_info = input_dialog
            self.g.update()
            self.AcceptEditor()
        else:
            self.g._main_info = ""
            self.g.update()
            self.AcceptEditor()

    def setDeadLineEditor(self):
        time = TimeWidget(self.g)
        time.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        time.exec_()
        self.g.time()
        self.AcceptEditor()

    def setPrioritetEditor(self):
        dialog = ChangeColor()
        dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        dialog.exec_()
        self.g._prioritet = dialog._color
        self.g.update()
        self.AcceptEditor()

    def AcceptEditor(self):
        if (self.g._date_days != "") and (self.g._prioritet != "#007682") and (self.g._main_info != "") and (
                self.g._main_name != ""):
            self.pushChButton_5.setEnabled(True)
            self.pushChButton_5.setStyleSheet("QPushButton\n"
                                              "{\n"
                                              "   text-decoration: none;\n"
                                              "  display: inline-block;\n"
                                              "  width: 140px;\n"
                                              "  height: 45px;\n"
                                              "  line-height: 45px;\n"
                                              "  border-radius: 45px;\n"
                                              "  font-family: \'Montserrat\', sans-serif;\n"
                                              "  font-size: 6px;\n"
                                              "  text-transform: uppercase;\n"
                                              "  text-align: center;\n"
                                              "  letter-spacing: 3px;\n"
                                              "  font-weight: 600;\n"
                                              "  color: white;\n"
                                              "  background: #1F5B63;\n"
                                              "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                              "  transition: .3s;\n"
                                              "}\n"
                                              "QPushButton:hover\n"
                                              "{\n"
                                              "  background: #2EE59D;\n"
                                              "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                              "  color: white;\n"
                                              "  transform: translateY(-7px);}")
        else:
            self.pushChButton_5.setEnabled(False)
            self.pushChButton_5.setStyleSheet("QPushButton\n"
                                              "{\n"
                                              "   text-decoration: none;\n"
                                              "  display: inline-block;\n"
                                              "  width: 140px;\n"
                                              "  height: 45px;\n"
                                              "  line-height: 45px;\n"
                                              "  border-radius: 45px;\n"
                                              "  font-family: \'Montserrat\', sans-serif;\n"
                                              "  font-size: 6px;\n"
                                              "  text-transform: uppercase;\n"
                                              "  text-align: center;\n"
                                              "  letter-spacing: 3px;\n"
                                              "  font-weight: 600;\n"
                                              "  color: white;\n"
                                              "  background: #1E5945;\n"
                                              "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                              "  transition: .3s;\n"
                                              "}\n"
                                              "QPushButton:hover\n"
                                              "{\n"
                                              "  background: #2EE59D;\n"
                                              "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                              "  color: white;\n"
                                              "  transform: translateY(-7px);}")


class ChangeColor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._color = "#007682"
        self.button1 = QPushButton("")
        self.button2 = QPushButton("")
        self.button3 = QPushButton("")
        self.button4 = QPushButton("Принять")
        self.button5 = QPushButton("Отменить")

        self.button1.setStyleSheet("background:green")
        self.button2.setStyleSheet("background:yellow")
        self.button3.setStyleSheet("background:Red")

        # Создаем компоновщик QHBoxLayout и добавляем кнопки
        vlayout = QHBoxLayout()
        vlayout.addWidget(self.button4)
        vlayout.addWidget(self.button5)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.button1)
        hlayout.addWidget(self.button2)
        hlayout.addWidget(self.button3)

        # Создаем компоновщик QVBoxLayout и добавляем два предыдущих компоновщика
        layout = QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addLayout(vlayout)

        self.button5.clicked.connect(self.Back)
        self.button1.clicked.connect(self.green)
        self.button2.clicked.connect(self.yellow)
        self.button3.clicked.connect(self.Red)
        self.button4.clicked.connect(self.Acept)

        # Устанавливаем компоновщик для диалога
        self.setLayout(layout)

    def Back(self):
        self._color = "#007682"
        self.close()

    def Red(self):
        self._color = "red"

    def yellow(self):
        self._color = "yellow"

    def green(self):
        self._color = "green"

    def Acept(self):
        self.close()

class TimeWidget(QDialog):
    def __init__(self, node, parent=None):
        super().__init__(parent)

        # Создаем виджет QTimeEdit
        self._date = ""
        self.node = node
        self.time_edit = QDateTimeEdit(self)
        self.time_edit.setDisplayFormat('yyyy:MM:dd:hh:mm')  # Формат отображения времени
        self.current_datetime = QDateTime.currentDateTime()
        self.time_edit.setDateTime(self.current_datetime)

        # Создаем метку с описанием
        self.label = QLabel('Выберите дату:', self)

        self.btn = QPushButton("Сохранить")
        self.btn2 = QPushButton("Отменить")

        self.btn.clicked.connect(self.SaveWindow)
        self.btn2.clicked.connect(self.CloseWindow)

        # Добавляем виджеты на окно
        layout = QVBoxLayout(self)
        layout2 = QHBoxLayout(self)
        layout2.addWidget(self.btn)
        layout2.addWidget(self.btn2)
        layout.addWidget(self.label)
        layout.addWidget(self.time_edit)

        layout.addLayout(layout2)

    def SaveWindow(self):
        self._date = self.time_edit.dateTime()
        v = self._date.date()
        s = self.current_datetime.date()
        l = self._date.time()
        self.node._end_day = str(v.year()) + ":" + str(v.month()) + ":" + str(v.day()) + ":" + str(
            l.hour()) + ":" + str(l.minute())
        self.days = ((v.year() - s.year()) * 365) + ((v.month() - s.month()) * 12) + v.day() - s.day()
        if self.days >= 0:
            self.days = str(self.days) + " дней"
            self.close()
        else:
            self.days = ""
            self.close()

    def CloseWindow(self):
        self.days = ""
        self.close()

class ThWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.graph = nx.DiGraph()
        self.setGeometry(0, 0, 200, 170)
        self.view = MiniGraphView(self.graph)
        self.setStyleSheet("background-color: #1E5945;")

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.view)

class MiniGraphView(QGraphicsView):
    def __init__(self, graph: nx.DiGraph, parent=None):
        super().__init__()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSceneRect(0, 0, 200, 170)
        self.setDragMode(QGraphicsView.NoDrag)
        self._graph = graph
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self._graph_scale = 200
        self._nodes_map = {}
        self.setMouseTracking(True)
        self.is_held = False

    def Timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.MoveItem)
        self.timer.start(500)

    def add_node(self):
        self.scene().clear()
        self.item = Node("1", f"{self.width()}:{self.height()}")

        self.item.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.item._radius = 50
        self.item._rect = QRectF(0, 0, self.item._radius * 2, self.item._radius * 2)
        self.item._rect2 = QRectF(self.item._rect.x() + (self.item._radius / 4),
                                  self.item._rect.y() + self.item._radius / 3.5, self.item._radius * 1.5,
                                  self.item._radius * 1.5)

        self.item.font.setPointSize(10)
        self.scene().addItem(self.item)
        self._graph.add_node("1")
        self._nodes_map[0] = self.item
        self.item.setPos(75, 30)

    def MoveItem(self):
        self.x = self.item.pos().x()
        self.y = self.item.pos().y()
        if self.x <= 0 or self.y <= 0 or self.x >= 150 or self.y >= 150:
            toggleMenu(ui, 0, True)
            self.timer.stop()
            timer = QTimer()
            timer.singleShot(1000, self.change_style)
            self.item._radius = self.item._radius
            self.item._rect = QRectF(0, 0, self.item._radius * 2, self.item._radius * 2)
            self.item._rect2 = QRectF(self.item._rect.x() + (self.item._radius / 4),
                                      self.item._rect.y() + self.item._radius / 3.5, self.item._radius * 1.5,
                                      self.item._radius * 1.5)

            self.new_pos = ui.main.view.mapFromGlobal(QCursor.pos())
            self.sec_pos = self.mapToScene(self.new_pos)
            self.item.setParentItem(None)
            self.item.setPos(self.new_pos)

            ui.main.view.add_node(str(len(ui.main.view._nodes_map) + 1), ui.main.view.pos_in_main.x(),
                                  ui.main.view.pos_in_main.y(), self.item._prioritet,
                                  self.item._main_name, self.item._main_info, self.item._date_days, "0:0",
                                  self.item._start_day,
                                  self.item._end_day)
            ui.main.view.check = 2
            ui.close()

    def change_style(self):
        ui.Create.view.setStyleSheet("background-color: #1E5945;")
        ui.pushButton_5.setEnabled(False)
        ui.pushButton_5.setStyleSheet("QPushButton\n"
                                      "{\n"
                                      "   text-decoration: none;\n"
                                      "  display: inline-block;\n"
                                      "  width: 140px;\n"
                                      "  height: 45px;\n"
                                      "  line-height: 45px;\n"
                                      "  border-radius: 45px;\n"
                                      "  font-family: \'Montserrat\', sans-serif;\n"
                                      "  font-size: 6px;\n"
                                      "  text-transform: uppercase;\n"
                                      "  text-align: center;\n"
                                      "  letter-spacing: 3px;\n"
                                      "  font-weight: 600;\n"
                                      "  color: white;\n"
                                      "  background: #1E5945;\n"
                                      "  box-shadow: 0 8px 15px rgba(0, 0, 0, .1);\n"
                                      "  transition: .3s;\n"
                                      "}\n"
                                      "QPushButton:hover\n"
                                      "{\n"
                                      "  background: #2EE59D;\n"
                                      "  box-shadow: 0 15px 20px rgba(46, 229, 157, .4);\n"
                                      "  color: white;\n"
                                      "  transform: translateY(-7px);}")


def toggleMenu(self, maxWidth, enable):
    if enable:
        # GET WIDTH
        width = self.frame_2.width()
        maxExtend = maxWidth
        standard = 0

        # SET MAX WIDTH
        if width == 0:
            widthExtended = maxExtend
        else:
            widthExtended = standard

        # ANIMATION
        self.animation = QPropertyAnimation(self.frame_2, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


def toggleHeadChMenu(self, maxWidth, enable):
    if enable:
        # GET WIDTH
        width = self.frame_HeadCh_2.width()
        maxExtend = maxWidth
        standard = 0

        # SET MAX WIDTH
        if width == 0:
            widthExtended = maxExtend
        else:
            widthExtended = standard

        # ANIMATION
        self.animation = QPropertyAnimation(self.frame_HeadCh_2, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


def toggleHeadMenu(self, maxWidth, enable):
    if enable:
        # GET WIDTH
        width = self.frame_Head_2.width()
        maxExtend = maxWidth
        standard = 0

        # SET MAX WIDTH
        if width == 0:
            widthExtended = maxExtend
        else:
            widthExtended = standard

        # ANIMATION
        self.animation = QPropertyAnimation((self.frame_Head_2), b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


def toggleTreeMenu(self, maxWidth, enable):
    if enable:
        # GET WIDTH
        width = self.frame_Tree_2.width()
        maxExtend = maxWidth
        standard = 0

        # SET MAX WIDTH
        if width == 0:
            widthExtended = maxExtend
        else:
            widthExtended = standard

        # ANIMATION
        self.animation = QPropertyAnimation(self.frame_Tree_2, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


def toggleViewingMenu(self, maxWidth, enable):
    if enable:
        # GET WIDTH
        width = self.frame_viewing_2.width()
        maxExtend = maxWidth
        standard = 0

        # SET MAX WIDTH
        if width == 0:
            widthExtended = maxExtend
        else:
            widthExtended = standard

        # ANIMATION
        self.animation = QPropertyAnimation(self.frame_viewing_2, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


def toggleChangeMenu(self, maxWidth, enable):
    if enable:
        # GET WIDTH
        width = self.frame_Ch_2.width()
        maxExtend = maxWidth
        standard = 0

        # SET MAX WIDTH
        if width == 0:
            widthExtended = maxExtend
        else:
            widthExtended = standard

        # ANIMATION
        self.animation = QPropertyAnimation(self.frame_Ch_2, b"minimumWidth")
        self.animation.setDuration(0)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


def toggleTopMenu(self, maxHeight, enable):
    if enable:
        height = self.Cont_Menu.height()
        maxExtend = maxHeight
        heightExtended = maxExtend

        self.animation = QPropertyAnimation(self.Cont_Menu, b"minimumHeight")
        self.animation.setDuration(0)
        self.animation.setStartValue(height)
        self.animation.setEndValue(heightExtended)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


class Fish(QGraphicsObject):
    def __init__(self, name: str, position: str, img, img2, parent=None):
        super().__init__(parent)
        self._name = name
        self._main_name = ""
        self._main_info = ""
        self._tickness = 0
        self._radius = 1
        self._color = "#2E8B57"
        self._position = position
        self._edges = []
        self.img = img
        self.img2 = img2

        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        self._tickness = self.img.boundingRect().width()
        return QRectF(0, 0, self._tickness, 0)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        brush = QBrush(QColor(self._color))
        painter.fillRect(self.boundingRect(), brush)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        pos_in_vie = self.mapToScene(self.pos())
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._position = f"{int(pos_in_vie.x())}:{int(pos_in_vie.y())}"

        return super().itemChange(change, value)

    def moveimg(self):
        pos_in_vie = self.mapToScene(self.pos())
        self._position = f"{int(pos_in_vie.x())}:{int(pos_in_vie.y())}"
        x1, y1 = self._position.split(":")
        self.img.setPos(int(x1) + 1200, (int(y1) + 540))
        self.img2.setPos(int(x1) + 2450, int(y1) + 350)


class ShowInfo(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self._prioritet = item._prioritet
        self._main_name = item._main_name
        self._main_info = item._main_info
        self._date_days = item._date_days
        label1 = QLabel(self)
        label2 = QLabel(self)
        label3 = QLabel(self)
        label4 = QLabel(self)

        btn = QPushButton("Вернуться")
        label1.setText(f"Задача:{self._main_name}")
        label2.setText(f"Описание:{self._main_info}")
        label3.setText(f"Приоритет:{self.color()}")
        label4.setText(f"Дедлайн:{self._date_days}")
        label3.setStyleSheet(f"color:{self.stylee}")
        btn.clicked.connect(self.CloseMenu)

        vbox = QVBoxLayout()
        vbox.addWidget(label1)
        vbox.addWidget(label2)
        vbox.addWidget(label3)
        vbox.addWidget(label4)
        vbox.addWidget(btn)
        self.setLayout(vbox)

    def CloseMenu(self):
        self.close()

    def color(self):
        self.prt_to_txt = ""
        self.stylee = ""
        if self._prioritet == "red":
            self.prt_to_txt = "Срочно и важно"
            self.stylee = "red"
        elif self._prioritet == "yellow":
            self.prt_to_txt = "Важно ,но не срочно"
            self.stylee = "orange"
        elif self._prioritet == "green":
            self.prt_to_txt = "Не срочно и не важно"
            self.stylee = "green"
        return self.prt_to_txt


class ShowFish(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self._main_name = item._main_name
        self._main_info = item._main_info
        label1 = QLabel(self)
        label2 = QLabel(self)

        btn = QPushButton("Вернуться")
        label1.setText(f"Задача:{self._main_name}")
        label2.setText(f"Описание:{self._main_info}")
        btn.clicked.connect(self.CloseMenu)

        vbox = QVBoxLayout()
        vbox.addWidget(label1)
        vbox.addWidget(label2)
        vbox.addWidget(btn)
        self.setLayout(vbox)

    def CloseMenu(self):
        self.close()

class ShowTree(QDialog):
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self._main_name = item._name
        label1 = QLabel(self)

        btn = QPushButton("Вернуться")
        label1.setText(f"Название:{self._main_name}")
        btn.clicked.connect(self.CloseMenu)

        vbox = QVBoxLayout()
        vbox.addWidget(label1)
        vbox.addWidget(btn)
        self.setLayout(vbox)

    def CloseMenu(self):
        self.close()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
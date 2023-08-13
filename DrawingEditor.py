import sys, math
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox, \
QGraphicsItem, QComboBox, QWidget, QGridLayout, QAction, QColorDialog, QInputDialog, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsLineItem, QGraphicsPolygonItem
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QTransform, QPainter, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint, QEvent, QPointF, QLineF

 
 
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        top = 400
        left = 400
        width = 800
        height = 600

        self.setWindowTitle("HW1 - Drawing Application")
        self.setGeometry(top, left, width, height)
        self.penSize = 2
        self.brushColor = Qt.white
        self.penColor = Qt.black
        self.lastPoint = QPoint()
        self.lastShapes = []

        self.startPoint = None
        self.endPoint = None

 
        self.createScene()
        self.createActions()
        self.createMenu()
 
 
        self.show()

    def resizeEvent(self, event):
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode(1))
        return super().resizeEvent(event)
    

    def eventFilter(self, source, event):
        text = self.shape_comboBox.currentText()
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            if text == "Line":
                self.startPoint = self.graphicsView.mapToScene(event.pos())
                pen = QPen(self.penColor, self.penSize)
                line = self.scene.addLine(self.startPoint.x(), self.startPoint.y(), self.startPoint.x(), self.startPoint.y(), pen)
                line.setFlag(QGraphicsItem.ItemIsMovable)
                line.setFlag(QGraphicsItem.ItemIsSelectable)
                self.lastShapes.append(line)
                self.update()
                self.endPoint = None
            else:
                mouse_pos = self.graphicsView.mapToScene(event.pos())
                self.addShape(mouse_pos)
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.RightButton:
            if text == "Line" and self.startPoint and self.endPoint:
                self.endPoint = self.graphicsView.mapToScene(event.pos())
                line = self.lastShapes[-1]
                line.setLine(self.startPoint.x(), self.startPoint.y(), self.endPoint.x(), self.endPoint.y())
                self.update()
                self.startPoint = None
                self.endPoint = None
            
        elif event.type() == QEvent.MouseMove and event.buttons() & Qt.RightButton:
            if text == "Line" and self.startPoint:
                self.endPoint = self.graphicsView.mapToScene(event.pos())
                line = self.lastShapes[-1]
                line.setLine(self.startPoint.x(), self.startPoint.y(), self.endPoint.x(), self.endPoint.y())
                self.update()
            elif text == "Circle":
                mouse_pos = self.graphicsView.mapToScene(event.pos())
                circle = self.lastShapes[-1]
                self.resizeCircle(circle, mouse_pos)
                self.update()
            elif text == "Rectangle":
                mouse_pos = self.graphicsView.mapToScene(event.pos())
                circle = self.lastShapes[-1]
                self.resizeRectangle(circle, mouse_pos)
                self.update()
            else:
                mouse_pos = self.graphicsView.mapToScene(event.pos())
                hexagon = self.lastShapes[-1]
                self.resizeHexagon(hexagon, mouse_pos)
                self.update()

        elif event.type() == QEvent.MouseMove and event.buttons() & Qt.MiddleButton and self.scene.selectedItems():
            selected_items = self.scene.selectedItems()
            for item in selected_items:
                mouse_pos = self.graphicsView.mapToScene(event.pos())
                if isinstance(item, QGraphicsEllipseItem):
                    self.resizeCircle(item, mouse_pos)
                elif isinstance(item, QGraphicsRectItem):
                    self.resizeRectangle(item, mouse_pos)
                elif isinstance(item, QGraphicsPolygonItem):
                    if len(item.polygon()) == 6:
                        self.resizeHexagon(item, mouse_pos)
                elif isinstance(item, QGraphicsLineItem):
                    item.setLine(item.line().p1().x(), item.line().p1().y(), mouse_pos.x(), mouse_pos.y())
            self.update()
 

        elif event.type() == QEvent.Wheel:
            # Check if any items are selected
            if len(self.scene.selectedItems()) > 0:
                # Increase or decrease size based on scrolling direction
                scroll_delta = event.angleDelta().y()
                if scroll_delta > 0:
                    self.increaseShapeSize()
                else:
                    self.decreaseShapeSize()
        return super().eventFilter(source, event)

    def createScene(self):
 
        self.scene = QGraphicsScene(self)
        self.graphicsView = QGraphicsView(self.scene, self)
        self.graphicsView.viewport().installEventFilter(self)
        self.setCentralWidget(self.graphicsView)

    def createMenu(self):
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(self.exitAction)
        fileMenu.addAction(self.saveImageAction)

        optionsMenu = menubar.addMenu('Options')
        optionsMenu.addAction(self.colorAction)
        optionsMenu.addAction(self.PenSizeAction)
        optionsMenu.addAction(self.clearAction)
        optionsMenu.addAction(self.increasePenSizeAction)
        optionsMenu.addAction(self.decreasePenSizeAction)
        optionsMenu.addAction(self.removeLastItemAction)
        optionsMenu.addAction(self.increaseShapeSizeAction)
        optionsMenu.addAction(self.decreaseShapeSizeAction)
        optionsMenu.addAction(self.paintAction)
        optionsMenu.addAction(self.changePenColorAction)
        optionsMenu.addAction(self.deleteItemAction)
        optionsMenu.addAction(self.increaseBoundaryAction)
        optionsMenu.addAction(self.decreaseBoundaryAction)
        optionsMenu.addAction(self.changeBoundaryColorAction)
        

        self.shape_comboBox = QComboBox()
        self.shape_comboBox.addItem("Circle")
        self.shape_comboBox.addItem("Rectangle")
        self.shape_comboBox.addItem("Line")
        self.shape_comboBox.addItem("Hexagon")


        widget = QWidget()
        layout = QGridLayout(widget)
        layout.addWidget(self.shape_comboBox, 0, 0)
        menubar.setCornerWidget(widget)

    def createActions(self):

        self.exitAction = QAction('Exit', self, triggered=self.close)
        self.exitAction.setShortcut("ctrl+esc")

        self.colorAction = QAction('Change Brush Color', self, triggered=self.setBrushColor)

        self.PenSizeAction = QAction('Set Pen Size', self, triggered=self.setPenSize)

        self.clearAction = QAction('Clear', self, triggered=self.clear)
        self.clearAction.setShortcut("ctrl+n")

        self.increasePenSizeAction = QAction('Increase Pen Size', self, triggered=self.increasePenSize)
        self.increasePenSizeAction.setShortcut("+")

        self.decreasePenSizeAction = QAction('Decrease Pen Size', self, triggered=self.decreasePenSize)
        self.decreasePenSizeAction.setShortcut("-")
        
        self.removeLastItemAction = QAction('Remove Last Item', self, triggered=self.removeLastItem)
        self.removeLastItemAction.setShortcut("ctrl+z")
        
        self.increaseShapeSizeAction = QAction('Increase Shape Size', self, triggered=self.increaseShapeSize)
        self.increaseShapeSizeAction.setShortcut("Ctrl++")

        self.decreaseShapeSizeAction = QAction('Decrease Size', self, triggered=self.decreaseShapeSize)
        self.decreaseShapeSizeAction.setShortcut("Ctrl+-")
        
        self.paintAction = QAction('Paint', self, triggered=self.paint)
        self.paintAction.setShortcut("ctrl+d")

        self.changePenColorAction = QAction('Change Pen Color', self, triggered = self.changePenColor)

        self.deleteItemAction = QAction('Delete Item', self, triggered = self.deleteShape)
        self.deleteItemAction.setShortcut("del")

        self.increaseBoundaryAction = QAction('Increase Boundary', self, triggered = self.increaseBoundary)
        self.increaseBoundaryAction.setShortcut("shift++")
        self.decreaseBoundaryAction = QAction('Decrease Boundary', self, triggered = self.decreaseBoundary)
        self.decreaseBoundaryAction.setShortcut("shift+-")

        self.changeBoundaryColorAction = QAction("Change Boundary COlor", self, triggered = self.changeBoundaryColor)
        self.saveImageAction = QAction('Save Image', self, triggered=self.saveImage)
        self.saveImageAction.setShortcut('Ctrl+S')

    def decreaseBoundary(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            pen = item.pen()
            if pen.width() > 1:
                pen.setWidth(pen.width() - 1)
                item.setPen(pen)

    
    def increaseBoundary(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            pen = item.pen()
            if pen.width() < 1000:
                pen.setWidth(pen.width() + 1)
                item.setPen(pen)
    
    
    def changePenColor(self):
        color = QColorDialog.getColor(self.brushColor, self, 'Select Pen Color')
        if color.isValid():
            self.penColor = color
    
    def removeLastItem(self):
        if len(self.lastShapes) != 0:
            self.scene.removeItem(self.lastShapes[-1])
            self.lastShapes.pop()


    def decreasePenSize(self):
        self.penSize = max(1, self.penSize - 1)

    def increasePenSize(self):
        try:
            self.penSize += 1
        except:
            pass
    def setBrushColor(self):
        color = QColorDialog.getColor(self.brushColor, self, 'Select Brush Color')
        if color.isValid():
            self.brushColor = color

    def setPenSize(self):
        penSize, ok = QInputDialog.getInt(self, 'Pen Size', 'Enter Pen size:', self.penSize, 1)
        if ok:
            self.penSize = penSize

    def clear(self):
        self.scene.clear()
        self.lastShapes.clear()
        self.update()
    
    def changeBoundaryColor(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            pen = QPen(self.penColor, self.penSize)
            item.setPen(pen)
    
    def paint(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if type(item) != QGraphicsLineItem:
                brush = item.brush()
                brush.setColor(self.brushColor)
                item.setBrush(brush)
    
    def deleteShape(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if item in self.lastShapes:
                self.scene.removeItem(self.lastShapes.pop(self.lastShapes.index(item)))
        self.update()

    def resizeCircle(self, circle, mouse_pos):
        # Calculate the distance between the circle's center and the mouse position
        center = circle.rect().center()
        dx = mouse_pos.x() - center.x()
        dy = mouse_pos.y() - center.y()
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Update the circle's radius
        circle.setRect(center.x() - distance, center.y() - distance, 2 * distance, 2 * distance)

    def resizeRectangle(self, rectangle, mouse_pos):
        center = rectangle.rect().center()
        dx = mouse_pos.x() - center.x()
        dy = mouse_pos.y() - center.y()
        width = abs(dx) * 2
        height = abs(dy) * 2
        rectangle.setRect(center.x() - width / 2, center.y() - height / 2, width, height)

    
    def addShape(self, pos):
        shape = self.shape_comboBox.currentText()
        if shape == "Circle":
            brush = QBrush(self.brushColor)
            pen = QPen(self.penColor, self.penSize)
            ellipse = self.scene.addEllipse(pos.x() - 100, pos.y() - 100, 200, 200, pen, brush)
            ellipse.setFlag(QGraphicsItem.ItemIsMovable)
            ellipse.setFlag(QGraphicsItem.ItemIsSelectable)
            self.lastShapes.append(ellipse)
        elif shape == "Rectangle":
            brush = QBrush(self.brushColor)
            pen = QPen(self.penColor, self.penSize)
            rect = self.scene.addRect(pos.x() - 100, pos.y() - 100, 200, 200, pen, brush)
            rect.setFlag(QGraphicsItem.ItemIsMovable)
            rect.setFlag(QGraphicsItem.ItemIsSelectable)
            self.lastShapes.append(rect)
        elif shape == "Hexagon":
            brush = QBrush(self.brushColor)
            pen = QPen(self.penColor, self.penSize)
            polygon = QPolygonF()
            for i in range(6):
                angle = 2 * math.pi * i / 6
                x = pos.x() + 100 * math.cos(angle)
                y = pos.y() + 100 * math.sin(angle)
                polygon.append(QPointF(x, y))
            hexagon = self.scene.addPolygon(polygon, pen, brush)
            hexagon.setFlag(QGraphicsItem.ItemIsMovable)
            hexagon.setFlag(QGraphicsItem.ItemIsSelectable)
            self.lastShapes.append(hexagon)
    

    def increaseShapeSize(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, QGraphicsEllipseItem) or isinstance(item, QGraphicsRectItem) or isinstance(item, QGraphicsLineItem):
                if isinstance(item, QGraphicsLineItem):
                    line = item.line()
                    new_line = QLineF(line.p1(), line.p2())
                    new_line.setLength(line.length() + 1)
                    item.setLine(new_line)
                else:
                    rect = item.rect()
                    center = rect.center()
                    if rect.width() < 1000 and rect.height() < 1000:
                        new_rect = rect.adjusted(-1, -1, 1, 1)
                        new_rect.moveCenter(center)
                        item.setRect(new_rect)
            elif isinstance(item, QGraphicsPolygonItem):
                polygon = item.polygon()
                center = polygon.boundingRect().center()
                scaled_polygon = QPolygonF(polygon)
                transform = QTransform()
                transform.translate(center.x(), center.y())
                transform.scale(1.02, 1.02)
                transform.translate(-center.x(), -center.y())
                scaled_polygon = transform.map(scaled_polygon)
                item.setPolygon(scaled_polygon)


    def decreaseShapeSize(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, QGraphicsEllipseItem) or isinstance(item, QGraphicsRectItem) or isinstance(item, QGraphicsLineItem):
                if isinstance(item, QGraphicsLineItem):
                    line = item.line()
                    new_line = QLineF(line.p1(), line.p2())
                    new_line.setLength(max(2, line.length() - 1))
                    item.setLine(new_line)
                else:
                    rect = item.rect()
                    center = rect.center()
                    if rect.width() > 2 and rect.height() > 2:
                        new_rect = rect.adjusted(1, 1, -1, -1)
                        new_rect.moveCenter(center)
                        item.setRect(new_rect)
            elif isinstance(item, QGraphicsPolygonItem):
                polygon = item.polygon()
                center = polygon.boundingRect().center()
                scaled_polygon = QPolygonF(polygon)
                transform = QTransform()
                transform.translate(center.x(), center.y())
                transform.scale(0.98, 0.98)
                transform.translate(-center.x(), -center.y())
                scaled_polygon = transform.map(scaled_polygon)
                item.setPolygon(scaled_polygon)

    def resizeHexagon(self, hexagon, mouse_pos):
        # Calculate the new size based on the distance between the mouse position and the hexagon's position
        dx = mouse_pos.x() - hexagon.pos().x()
        dy = mouse_pos.y() - hexagon.pos().y()
        size = math.sqrt(dx * dx + dy * dy) # Euclidian Distance

        polygon = QPolygonF()
        pos = hexagon.pos()

        for i in range(6):
            angle = 2 * math.pi * i / 6 # 2pi / 6
            x = pos.x() + size * math.cos(angle)
            y = pos.y() + size * math.sin(angle)
            polygon.append(QPointF(x, y))
        hexagon.setPolygon(polygon)

    def saveImage(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)')
        if filename:
            if ".jpg" in filename or ".jpeg" in filename or ".png" in filename:
                pixmap = QPixmap(self.graphicsView.viewport().size())
                pixmap.fill(Qt.white)
                painter = QPainter(pixmap)
                self.graphicsView.render(painter)
                painter.end()
                pixmap.save(filename)
            else:
                QMessageBox.warning(self, 'Invalid File Format', 'Please save the image in JPG or PNG format.')

    

app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())

from PySide6 import  QtWidgets
from PySide6.QtGui import QResizeEvent
from nanosurf.lib.gui import nsf_colors

class _NSFLine(QtWidgets.QFrame):
    def __init__(self, show:bool, width:int, color:str="", **kwargs):
        super().__init__(**kwargs)
        self._line_color = color if color != "" else nsf_colors.NSFColorHexStr.Orange
        self._line_width = width
        self._is_visible = show
        self.set_line_color(self._line_color)
        self.set_visible(self._is_visible)
    
    def set_line_color(self, color:str):
        self._line_color = color
        self.setStyleSheet(f"background-color:#{self._line_color};")

    def get_line_color(self) -> str:
        return self._line_color

    def get_line_width(self):
         return self._line_width
    
    def set_visible(self, show:bool=True):
        self._is_visible = show
        self.setHidden(not show)

    def is_visible(self) -> bool:
        return self._is_visible

class NSFHLine(_NSFLine):
    def __init__(self, show:bool = True, width:int = 1, color:str="", **kwargs):
        self._line_size = width
        super().__init__(show, width, color, **kwargs)
        self.setFrameStyle(QtWidgets.QFrame.Shape.HLine | QtWidgets.QFrame.Shadow.Plain)

    def set_line_width(self, width:int):
        self._line_size = width
        self.updateGeometry()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.setFixedHeight(self._line_size)
        return super().resizeEvent(event)

class NSFVLine(_NSFLine):
    def __init__(self, show:bool = True, width:int = 1, color:str="", **kwargs):
        self._line_size = width
        super().__init__(show, width, color, **kwargs)
        self.setFrameStyle(QtWidgets.QFrame.Shape.VLine | QtWidgets.QFrame.Shadow.Plain)

    def set_line_width(self, width:int):
        self._line_size = width
        self.updateGeometry()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.setFixedWidth(self._line_size)
        return super().resizeEvent(event)
        

class NSFVSpacer(QtWidgets.QSpacerItem):
    def __init__(self, width:int=1, minimal_height:int=40):
        super().__init__(width, minimal_height, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.MinimumExpanding)

class NSFHSpacer(QtWidgets.QSpacerItem):
    def __init__(self, minimal_width:int=200, height:int=1):
        super().__init__(minimal_width, height, QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Fixed)

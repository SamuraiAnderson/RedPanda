
from typing import Callable

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QProgressBar
)
from PyQt5.QtCore import pyqtSlot



from utils.ModelFileRead import read_step_file_with_names_colors, OpenFile


from OCC.Core.TColStd import (
    TColStd_ListOfInteger,
    TColStd_ListIteratorOfListOfInteger
)
from OCC.Core.TDF import (
    TDF_AttributeIterator,
    TDF_LabelList,
    TDF_ChildIterator,
    TDF_Label,
    TDF_Attribute
)
from OCC.Core.TDocStd import TDocStd_Document

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal


from widgets.Ui_Main import Ui_MainWindow
from widgets.Logic_DocTree import ModelTree
from widgets.Logic_Application import Logic_Application
from utils.logger import Logger
from utils.Driver.Sym_ShapeDriver import Sym_BoxDriver
from utils.Driver.Sym_AlgoDriver import Sym_CutDriver
from utils.Sym_ParamBuilder import Sym_NewBuilder

class MainWindow(QMainWindow):
    sig_Construct = pyqtSignal(Sym_NewBuilder)
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setupUi()

        self.ui.retranslateUi(self)
        self.connnectAction()

        self._modelMenu_dict = dict()
        self._MakeShapeMenu_def()

    def setupUi(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Main Struct
        self.logic_Viewer = self.ui.logic_View
        self.logic_Viewer.InitDriver()
        self.logic_app = Logic_Application(self.logic_Viewer._display)
        self._model_menu = self.ui.menu

        self.logic_ViewData = self.ui.logic_ViewData
        self.logic_ConstructView = self.ui.logic_Construct
        self.logic_DocData = self.ui.logic_DocData

        self.logic_DocTree = self.logic_DocData.ui.treeWidget

        return 

    def connnectAction(self):
        # start menu
        self.ui.actionstep.triggered.connect(self.openFileSTEP)
        self.ui.actionxml.triggered.connect(lambda:self.logic_app.NewDocument("XmlOcaf"))

        # self sig
        self.sig_Construct.connect(self.logic_ConstructView.NewConstruct)

        # construct sig
        self.logic_ConstructView.sig_NewShape.connect(self.logic_app.NewShape)
        self.logic_ConstructView.sig_ChangeShape.connect(self.logic_app.ChangeDoc)

        self.logic_app.sig_DocChanged.connect(self.logic_DocTree.Show)
        self.logic_app.sig_DocUpdate.connect(self.logic_DocTree.Update)
        self.logic_DocTree.sig_select.connect(self.logic_ConstructView.ShowShape) 


    def _MakeShapeMenu_def(self):
        self.add_menu('PrimAPI')
        self.add_menu('AlgoAPI')
        self.add_menu('GeomAPI')

        self.add_function_to_menu('PrimAPI', 'Box', lambda:self.ShapeConstruct("Box"))
        self.add_function_to_menu('AlgoAPI', 'Cut', lambda:self.ShapeConstruct("Cut"))
        self.add_function_to_menu('GeomAPI', 'bezier', lambda:self.ShapeConstruct("bezier"))

    def add_menu(self, menu_name: str) -> None:
        _menu = self._model_menu.addMenu("&" + menu_name)
        self._modelMenu_dict[menu_name] = _menu

    def add_function_to_menu(self, menu_name: str, action_name:str, _callable: Callable) -> None:
        try:
            _action = QtWidgets.QAction(
                action_name, self
            )
            # if not, the "exit" action is now shown...
            _action.setMenuRole(QtWidgets.QAction.NoRole)
            _action.triggered.connect(_callable)

            self._modelMenu_dict[menu_name].addAction(_action)
        except KeyError:
            raise ValueError("the menu item %s does not exist" % menu_name)

    @pyqtSlot()
    def ShapeConstruct(self, type:str):
        from utils.Driver.Sym_DataDriver import Sym_ArrayDriver
        from utils.Driver.Sym_GeomDriver import Sym_BezierDriver
        if type == "Box":
            param = Sym_NewBuilder(Sym_BoxDriver())
        elif type == 'Cut':
            param = Sym_NewBuilder(Sym_CutDriver())
        elif type == 'Array':
            param = Sym_NewBuilder(Sym_ArrayDriver())
        elif type == 'bezier':
            param = Sym_NewBuilder(Sym_BezierDriver())
        else:
            Logger().info(f'ShapeCnstruct unknow type:{type}')
        self.sig_Construct.emit(param)

    @pyqtSlot()
    def openFileSTEP(self):
        self.choose_document = QFileDialog.getOpenFileName(self, '打开文件', './resource',
                                                              " STP files(*.stp , *.step);;(*.iges);;(*.stl)")  # 选择转换的文价夹

        filepath = self.choose_document[0]
        end_with = str(filepath).lower()
        if end_with.endswith(".step") or end_with.endswith("stp"):
            self.read_file(filepath)

    def read_file(self, file):
        doc = OpenFile(file)
        self.dict_shape = read_step_file_with_names_colors(doc)
        # progressShow = QProgressBar(self)
        iter = self.dict_shape.items()

        from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
        from OCC.Core.TopoDS import TopoDS_Solid
        count = 0
        for shape, dict in iter:
            color = dict["color"]

            if  not isinstance(shape, TopoDS_Solid):#排除非solid
                continue

            color = Quantity_Color(color.Red(),
                                    color.Green(),
                                    color.Blue(),
                                    Quantity_TOC_RGB)

            count += 1
            self.viewer._display.DisplayShape(shape, color=color)

        self.viewer._display.FitAll()
        print("count: {}".format(count))
        self.treeView.Create_ModelTree(doc)

    def read_doc(self, doc:TDocStd_Document):
        # read doc
        rootLabel = doc.Main()
        level = 0
        stack_label = list()
        stack_label.append((rootLabel, level))
        def GetAttributeType(attri: TDF_Attribute):
            list_type = TDF_Attribute.__subclasses__()
            for type in list_type:
                try:
                    if attri.ID() == type.GetID():
                        return type
                except :
                    pass
            return TDF_Attribute

        while len(stack_label) != 0:
            label : TDF_Label
            label, level = stack_label.pop()
            it_attr = TDF_AttributeIterator(label)
            while it_attr.More():
                print(" "*(level+1), GetAttributeType(it_attr.Value()))
                it_attr.Next()
                        
            children = list()
            it_child = TDF_ChildIterator(label)

            while it_child.More():
                children.append( (it_child.Value(), level+1) )
                it_child.Next()

            children.reverse()
            stack_label.extend(children)


if __name__ == "__main__":
    import sys
    import logging
    import time

    log = Logger()
    log.debug("Application Start")
    app = QApplication(sys.argv)
    myWin = MainWindow()
    myWin.show()
    
    sys.exit(app.exec_())

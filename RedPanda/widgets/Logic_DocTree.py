# _*_ coding: utf-8 _*_
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeySequence as QKSec
from PyQt5.QtGui import QIcon,QBrush
from PyQt5.QtCore import  Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QTreeWidgetItem, 
    QTreeWidget,
    QAbstractItemView,
    
)
from OCC.Core.TDF import (
    TDF_ChildIterator
)
from RedPanda.Sym_ParamBuilder import (
    Sym_ChangeBuilder
)
from RedPanda.logger import Logger
from RedPanda.RPAF.Document import Document
from RedPanda.RPAF.RD_Label import Label
from RedPanda.RPAF.DataDriver import DataDriver
from RedPanda.RPAF.DataDriver.BaseDriver import DataLabelState

class ModelTree(QtWidgets.QTreeWidget):
    sig_select = pyqtSignal(Sym_ChangeBuilder)
    sig_labelSelect = pyqtSignal(Label)
    def __init__(self, *args):
        super(ModelTree, self).__init__(*args)
        self.tree = self
        self.tree.expandAll()# 节点全部展开
        self.tree.setStyle(QtWidgets.QStyleFactory.create('windows'))#有加号
        self.tree.setColumnCount(3) # 设置列数
        self.tree.setHeaderLabels(['name', 'type', 'state'])# 设置树形控件头部的标题

        self.item_lookup = dict()
        self.main_doc = None
        self.dataRoot = None
        self._Selected_item = None
        self.item_defaultBackground = None

        # 设置根节点
        self.root = QTreeWidgetItem(self.tree)
        self._Selected_item = self.root
        self.item_defaultBackground = self.root.background(0)    
        self.root.setText(0, 'RedPanda')
        # self.root.setIcon(0, QIcon('sync.ico'))

        # tool_root = QTreeWidgetItem(self.root)
        # tool_root.setText(0, '辅助工具')
        # # wcs_root.setIcon(0, QIcon('sync.ico'))
        # tool_root.setCheckState(0, Qt.Checked)
        # self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置树形控件的列的宽度
        self.tree.setColumnWidth(0, 150)

        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

        # todo 优化2 设置根节点的背景颜色
        #brush_red = QBrush(Qt.red)
        #root.setBackground(0, brush_red)
        #brush_blue = QBrush(Qt.blue)
        #root.setBackground(1, brush_blue)
        # 加载根节点的所有属性与子控件
        # self.tree.addTopLevelItem(root)


    @pyqtSlot(Document)
    def Show(self, doc:Document):
        self.main_doc = doc
        self.Update()

    @pyqtSlot()
    def Update(self):
        self.ClearItems()
        self.Create_ModelTree(self.main_doc)
        self.tree.expandAll()

    def ClearItems(self):
        self._Selected_item = self.root
        if self.dataRoot:
            self.root.removeChild(self.dataRoot)
        self.items.clear()


    def Create_ModelTree(self, doc:Document):
        # 设置根节点
        rootLabel = doc.Main()

        def treeNode(theLabel:Label, father):
            name = theLabel.GetLabelName()
            if len(name) <= 0:
                return

            aDriver:DataDriver = theLabel.GetDriver()

            item = QTreeWidgetItem(father)
            father = item
            self.items.append(item)

            item.setText(0, f'{theLabel.GetEntry()} {name}')
            if aDriver:
                item.setText(1, f'{aDriver.Type}')
                flag = 'OK' if DataLabelState.IsOK(theLabel) else 'Error'
                item.setText(2, f'{flag}')
            self.SetDataLabel(item, theLabel)

            item.setCheckState(0, Qt.Checked)

            it_child = TDF_ChildIterator(theLabel)
            while it_child.More():
                treeNode(it_child.Value(), father)
                it_child.Next()

            return father

        self.dataRoot = treeNode(rootLabel, self.root)

    @staticmethod
    def SetDataLabel(item:QTreeWidgetItem, theLabel:Label):
        print(f'{theLabel.GetEntry()} TOOO set data Label')
        if theLabel.GetFunctionID():
            print(f'{theLabel.GetEntry()} set data Label')
            item.setData(2, Qt.ItemDataRole.UserRole+1, True)
        item.setData(2, Qt.ItemDataRole.UserRole, theLabel)

    @staticmethod
    def IsNamedShape(item:QTreeWidgetItem):
        return item.data(2, Qt.ItemDataRole.UserRole+1)

    @staticmethod
    def GetLabel(item:QTreeWidgetItem):
        return item.data(2, Qt.ItemDataRole.UserRole)

    # -- new -- 
    @pyqtSlot(Label)
    def Update(self, theLabel):
        item = self.item_lookup[theLabel]

        name = theLabel.GetLabelName()        
        item.setText(0, f'{theLabel.GetEntry()} {name}')

        aDriver:DataDriver = theLabel.GetDriver()
        if aDriver:
            item.setText(1, f'{aDriver.Type}')
            flag = 'OK' if DataLabelState.IsOK(theLabel) else 'Error'
            item.setText(2, f'{flag}')

        self.SetDataLabel(item, theLabel)
        item.setCheckState(0, Qt.Checked)

    @pyqtSlot(Label, Label)
    def Create_TreeItem(self, theLabel:Label, fatherLabel=None):
        if fatherLabel is None:
            fatheritem = self.root
        else:
            fatheritem = self.item_lookup[fatherLabel]

        item = QTreeWidgetItem(fatheritem)
        self._regist_LabelItem(theLabel, item)
        self.Update(theLabel)
        return item

    def _regist_LabelItem(self, label, item):
        self.item_lookup[label] = item
        # self.item_lookup[item] = label

    def onItemDoubleClicked(self, item: QTreeWidgetItem, column: int) -> None:
        self._Selected_item.setBackground(0, self.item_defaultBackground)
        self._Selected_item = item

        if self.IsNamedShape(item):
            aLabel = self.GetLabel(item)
            name = aLabel.GetLabelName()
            Logger().info(f'Selected Item:{name}')

            self._Selected_item.setBackground(0, QBrush(Qt.GlobalColor.lightGray))
            # self.sig_select.emit(Sym_ChangeBuilder(aLabel))
            self.sig_labelSelect.emit(aLabel)

import inspect

from OCC.Core.Standard import (
    Standard_GUID
)
from OCC.Core.TDataStd import TDataStd_TreeNode
from OCC.Core.TDF import (
    TDF_Attribute,
    TDF_Label,
    TDF_AttributeIterator
)

from utils.GUID import (
    IDcolCurvGUID,
    IDcolGUID,
    IDcolSurfGUID,
    AssemblyGUID,
    ShapeRefGUID
)

def FindAttribute(label:TDF_Label, GUID:Standard_GUID, attribute: TDF_Attribute):
    it_attr = TDF_AttributeIterator(label)
    while it_attr.More():
        if it_attr.Value().ID() == GUID:
            attribute.Restore(it_attr.Value())
            # .Paste(attribute,)
            return True 
        it_attr.Next()

    attribute = None
    return False

class Assembly(TDataStd_TreeNode):
    def GetID():
        return AssemblyGUID

class ShapeRef(TDataStd_TreeNode):
    """
    label0 ref Label1.Shape
    => label0 is Label1.Shape
    """
    def GetID():
        return ShapeRefGUID

class IDcol(TDataStd_TreeNode):
    def GetID():
        return IDcolGUID

class IDcolSurf(TDataStd_TreeNode):
    def GetID():
        return IDcolSurfGUID

class IDcolCurv(TDataStd_TreeNode):
    def GetID():
        return IDcolCurvGUID



# from types import ModuleType
# from typing import NoReturn
# from utils import Singleton

# class DictAttributeType(Singleton):
#     dict_attributeType = None
#     def __init__(self):
#         super(DictAttributeType, self).__init__()
#         if self.dict_attributeType is None:
#             self.dict_attributeType = dict()

#             # lcaf
#             import OCC.Core.TDF as TDF
#             import OCC.Core.TDocStd as TDocStd
#             import OCC.Core.TFunction as TFunction
#             import OCC.Core.TPrsStd as TPrsStd
#             import OCC.Core.TDataStd as TDataStd
#             # caf
#             import OCC.Core.TDataXtd as TDataXtd
#             import OCC.Core.TNaming as TNaming
#             # xcaf
#             import OCC.Core.XCAFDoc as XCAFDoc
#             # Tobj
#             import OCC.Core.TObj as TObj
#             # my
#             import MyAttribute as MyAttribute
#             list_AttributeModule = [
#                 TDF, TDocStd, TFunction, TPrsStd, TDataStd,
#                 TDataXtd, TNaming, XCAFDoc, TObj,
#                 MyAttribute
#             ]
#             for module in list_AttributeModule:
#                 self._addClassFromModule(module)

#     def _IsAtributeClass(object:type)->bool:
#         return  (hasattr(object, "ID") 
#               or hasattr(object, "GetID"))
        
#     def Add(self, objet: type)->bool:
#         if DictAttributeType._IsAtributeClass(object):
#             if hasattr(object, "GetID"):
#                 self.dict_attributeType[object.GetID()] = object
#             elif object == TDataStd_TreeNode:
#                 self.dict_attributeType[object.GetDefaultTreeID()] = object
#             else:
#                 return False
#         return False

#     def _addClassFromModule(self, module: ModuleType)-> NoReturn:
#         dict_name_type = inspect.getmembers(module, 
#             lambda x: inspect.isclass(x) and DictAttributeType._IsAtributeClass(x))
#         for name, value in dict_name_type:
#             self.Add(value)

#     def GetType(self, guid:Standard_GUID)->type:
#         return self.dict_attributeType.get(guid, TDF_Attribute)


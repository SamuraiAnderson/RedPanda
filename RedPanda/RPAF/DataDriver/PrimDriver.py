
__all__ = [
    'TransformDriver',
    'BoxDriver',
    'TransShapeDriver'
]

from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.AIS import AIS_ColoredShape, AIS_InteractiveContext

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.RPAF.GUID import *


from RedPanda.Core.data import RP_AsciiStr
from RedPanda.Core.Euclid import (
    RP_Pnt,
    RP_Ax1,
    RP_Trsf,
)
from RedPanda.Core.topogy import VertexAnalyst

from ..Attribute import (
    XCAFDoc_Location,
    TNaming_NamedShape,
    TNaming_Builder,
)
from ..RD_Label import Label
from .BaseDriver import (
    DataDriver,
    Argument,
    Param,
    DataEnum,
    ShapeRefDriver,
    DataLabelState
)
from .VarDriver import (
    RealDriver,
)
from .VertexDriver import (
    PntDriver,
)
from .ShapeBaseDriver import ShapeDriver

from ..DriverTable import DataDriverTable

class BoxDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['l'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['h'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['w'] = Argument(self.tagResource, RealDriver.ID)

    def myExecute(self, theLabel:Label)->int:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)
        trsf:RP_Trsf = dict_param['transform']
        dx = dict_param['l']
        dy = dict_param['h']
        dz = dict_param['w']

        try:
            shape = BRepPrimAPI_MakeBox(dx, dy, dz).Shape()
        except:
            DataLabelState.SetError(theLabel, f'{dx}, {dy}, {dz} is error', True)
            return 1

        shape = BRepBuilderAPI_Transform(shape, trsf).Shape()

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def ID(self):
        return  Sym_BoxDriver_GUID #

    @classproperty
    def Type(self):
        return "Box"

class TransShapeDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['shape'] = Argument(self.tagResource, ShapeRefDriver.ID)

    def myExecute(self, theLabel:Label)->int:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            dict_param[name] = aLabel.GetAttrValue(self.Attributes['value'].id)
        try:
            trsf:RP_Trsf = dict_param['transform']
            shape = dict_param['transform']

            shape = BRepBuilderAPI_Transform(shape, trsf).Shape()

        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def ID(self):
        return  Sym_TransShapeDriver_GUID #

    @classproperty
    def Type(self):
        return "TransShape"

class ConeDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['c0'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['c1'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['H'] = Argument(self.tagResource, ShapeRefDriver.ID)

    
    def myExecute(self, theLabel:Label)->int:
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            dict_param[name] = aLabel.GetAttrValue(self.Attributes['value'].id)
        try:
            c0 = dict_param['c0']
            c1 = dict_param['c1']
            h = dict_param['H']

            shape = BRepPrimAPI_MakeCone(c0, c1, h).Shape()

        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def ID(self):
        from ..GUID import Sym_ConeDriver_GUID
        return  Sym_ConeDriver_GUID #

    @classproperty
    def Type(self):
        return "Cone"



__all__ = ['BezierDriver']

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.RPAF.GUID import *

from RedPanda.Core.Make import (
    make_box,
    make_edge,
    make_transform,
    boolean_cut,
    points_to_bspline
)

from ..Attribute import (
    XCAFDoc_Location,
    TNaming_NamedShape,
    TNaming_Builder,
)
from ..RD_Label import Label
from .BaseDriver import (
    Argument,
    Param,
    DataEnum
)
from .ShapeBaseDriver import BareShapeDriver
from .VertexDriver import (
    PntArrayDriver,
)

class BezierDriver(BareShapeDriver):
    OutputType = DataEnum.Edge
    ViewType = '2D'
    
    def __init__(self) -> None:
        super().__init__()
        self.Attr = Param(TNaming_NamedShape.GetID())
        self.Attributes['value'] = self.Attr
        self.Arguments = {
            'pnts': Argument(self.tagResource, PntArrayDriver.ID)
        }

    def Execute(self, theLabel: Label) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pnts = dict_param['pnts']
        curve = points_to_bspline(pnts)
        shape = make_edge(curve)

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def Type(self):
        return 'bspline'

    @classproperty
    def ID(self):
        return Sym_BezierDriver_GUID

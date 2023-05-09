from OCC.Core.TNaming import TNaming_Builder, TNaming_NamedShape
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.gp import gp_Ax1, gp_Trsf, gp_Ax2, gp_Ax3
from OCC.Core.AIS import AIS_ColoredShape, AIS_Shaded, AIS_Plane, AIS_TOPL_XYPlane
from OCC.Core.Geom import Geom_Axis2Placement

from RedPanda.RPAF.DisplayContext import DisplayCtx
from RedPanda.logger import Logger
from RedPanda.RPAF.RD_Label import Label
from RedPanda.decorator import classproperty


from .BaseDriver import (
    ShapeRefDriver,
    Argument,
    DataLabelState,
)
from .VarDriver import IntDriver

from .ShapeBaseDriver import (
    BareShapeDriver,
)
from .VertexDriver import PntDriver


class RefSubDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Shape'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['TopoType'] = Argument(self.tagResource, IntDriver.ID)
        self.Arguments['Index'] = Argument(self.tagResource, IntDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.TopAbs import TopAbs_COMPOUND, TopAbs_VERTEX
        from OCC.Core.TopExp import TopExp_Explorer

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        if dict_param['TopoType'] < TopAbs_COMPOUND or  dict_param['TopoType'] > TopAbs_VERTEX:
            DataLabelState.SetError(theLabel, 'TopoEnum Error', True)
            return 1
 
        dict_param['Shape']:TopoDS_Shape
        if dict_param['TopoType'] < dict_param['Shape'].ShapeType():
            DataLabelState.SetError(theLabel, 'TopoEnum is must be sub of Shape')
            return 1

        sub = None
        try:
            explorer = TopExp_Explorer(dict_param['Shape'], dict_param['TopoType'])
            i = 0
            while explorer.More():
                i += 1
                if i == dict_param['Index']:
                    sub = explorer.Value()
                    break
                explorer.Next()
        except Exception as Error:
            DataLabelState.SetError(theLabel, 'Explorer Error', True)
            return 1

        if sub is None:
            DataLabelState.SetError(theLabel, 'Sub Error', True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(sub)
        return 0

    @classproperty
    def ID(self):
        from ..GUID import Sym_RefSubDriver_GUID
        return  Sym_RefSubDriver_GUID #

    @classproperty
    def Type(self):
        return "RefSub"


class MirrorDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()

        self.Arguments['Pnt'] = Argument(self.tagResource, PntDriver.ID)
        self.Arguments['Dir'] = Argument(self.tagResource, PntDriver.ID)
        
        self.Arguments['Shape'] = Argument(self.tagResource, ShapeRefDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform        
        from RedPanda.Core.Make import mirror_axe2

        
        shape = self.Arguments['Shape'].Value(theLabel)

        try:
            
            ax2 = self.ax2(theLabel)
            shape = mirror_axe2(shape, ax2)
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)
        return 0

    def ax2(self, theLabel):
        from RedPanda.Core.topogy import VertexAnalyst
        vt = self.Arguments['Pnt'].Value(theLabel)
        pnt = VertexAnalyst(vt).as_pnt
        vt = self.Arguments['Dir'].Value(theLabel)
        dir = VertexAnalyst(vt).as_dir
        ax2 = gp_Ax2(pnt, dir)

    def Prs3d(self, theLabel) -> DisplayCtx:
        ctx = super().Prs3d(theLabel)
        from OCC.Core.Geom import Geom_Plane

        aLabel = theLabel.Argument['Shape']
        ais  = AIS_ColoredShape(TopoDS_Shape())
        ais.SetDisplayMode(AIS_Shaded)
        ctx[(aLabel, 'shape')] = ais


        plane = Geom_Plane(gp_Ax3())
        ais = AIS_Plane(plane)
        ctx[(theLabel, 'plane')] = ais

        return ctx

    def UpdatePrs3d(self, theLabel:Label, ctx: DisplayCtx):
        super().UpdatePrs3d(theLabel, ctx)

        if not DataLabelState.IsOK(theLabel):
            return False

        # 2
        aLabel = theLabel.Argument['Shape']
        ais:AIS_ColoredShape = ctx[(aLabel, 'shape')]
        ais.SetShape(aLabel.GetAttrValue(TNaming_NamedShape.GetID()))

        # 3
        place = Geom_Axis2Placement(self.ax2(theLabel))
        ais:AIS_Plane = ctx[(theLabel, 'plane')]
        ais.SetAxis2Placement(place, AIS_TOPL_XYPlane)

        return True

    @classproperty
    def Type(self):
        return 'MirAx2'

    @classproperty
    def ID(self):
        from ..GUID import Sym_MirAx2Driver_GUID
        return Sym_MirAx2Driver_GUID

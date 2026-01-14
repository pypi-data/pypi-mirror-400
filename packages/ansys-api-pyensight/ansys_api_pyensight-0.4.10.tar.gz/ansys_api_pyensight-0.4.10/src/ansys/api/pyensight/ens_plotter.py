"""ens_plotter module

The ens_plotter module provides a proxy interface to EnSight ENS_PLOTTER instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_PLOTTER(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_PLOTTER

    Args:
        *args:
            Superclass (ENSOBJ) arguments
        **kwargs:
            Superclass (ENSOBJ) keyword arguments

    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._update_attr_list(self._session, self._objid)

    @classmethod
    def _update_attr_list(cls, session: 'Session', id: int) -> None:
        if hasattr(cls, 'attr_list'):
            return
        cmd = session.remote_obj(id) + '.__ids__'
        cls.attr_list = session.cmd(cmd)

    @property
    def objid(self) -> int:  # noqa: N802
        """
        Return the EnSight object proxy ID (__OBJID__).
        """
        return self._objid

    def createplotter(self, *args, **kwargs) -> Any:
        """Create a new plotter

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.createplotter({arg_string})"
        return self._session.cmd(cmd)

    def rescale(self, *args, **kwargs) -> Any:
        """Rescale to current queries

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.rescale({arg_string})"
        return self._session.cmd(cmd)

    def attrgroupinfo(self, *args, **kwargs) -> Any:
        """Get information about GUI groups for this plotter's attributes

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.attrgroupinfo({arg_string})"
        return self._session.cmd(cmd)

    @property
    def METADATA(self) -> Dict[Any, Any]:
        """METADATA property
        
        metadata
        
        Supported operations:
            getattr
        Datatype:
            CEI Metadata, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.METADATA)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def metadata(self) -> Dict[Any, Any]:
        """METADATA property
        
        metadata
        
        Supported operations:
            getattr
        Datatype:
            CEI Metadata, scalar
        
        Note: both 'metadata' and 'METADATA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.METADATA)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def UUID(self) -> str:
        """UUID property
        
        universal unique id
        
        Supported operations:
            getattr
        Datatype:
            String, 37 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.UUID)
        _value = cast(str, value)
        return _value

    @property
    def uuid(self) -> str:
        """UUID property
        
        universal unique id
        
        Supported operations:
            getattr
        Datatype:
            String, 37 characters maximum
        
        Note: both 'uuid' and 'UUID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.UUID)
        _value = cast(str, value)
        return _value

    @property
    def EDIT_TARGET(self) -> int:
        """EDIT_TARGET property
        
        currently an edit target
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.EDIT_TARGET)
        _value = cast(int, value)
        return _value

    @property
    def edit_target(self) -> int:
        """EDIT_TARGET property
        
        currently an edit target
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'edit_target' and 'EDIT_TARGET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.EDIT_TARGET)
        _value = cast(int, value)
        return _value

    @property
    def PROJECT_MASK(self) -> int:
        """PROJECT_MASK property
        
        object project mask
        
        Supported operations:
            getattr, setattr
        Datatype:
            64bit integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PROJECT_MASK)
        _value = cast(int, value)
        return _value

    @PROJECT_MASK.setter
    def PROJECT_MASK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROJECT_MASK, value)

    @property
    def project_mask(self) -> int:
        """PROJECT_MASK property
        
        object project mask
        
        Supported operations:
            getattr, setattr
        Datatype:
            64bit integer, scalar
        
        Note: both 'project_mask' and 'PROJECT_MASK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PROJECT_MASK)
        _value = cast(int, value)
        return _value

    @project_mask.setter
    def project_mask(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROJECT_MASK, value)

    @property
    def HANDLES_ENABLED(self) -> int:
        """Control the display and use of EnSight click and go handles for an object
        
        EnSight allows for direct interaction with many objects via click and go handles.
        The handles allow things like annotations and viewports to be moved or resized.
        They allow for the adjustment of values for clip planes and palette dynamic ranges.
        In some situations, allowing the user to directly adjust these values can be
        undesirable.  Setting this attribute to zero disables display of and interaction
        with click and go handles for the specific object instance.
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HANDLES_ENABLED)
        _value = cast(int, value)
        return _value

    @HANDLES_ENABLED.setter
    def HANDLES_ENABLED(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HANDLES_ENABLED, value)

    @property
    def handles_enabled(self) -> int:
        """Control the display and use of EnSight click and go handles for an object
        
        EnSight allows for direct interaction with many objects via click and go handles.
        The handles allow things like annotations and viewports to be moved or resized.
        They allow for the adjustment of values for clip planes and palette dynamic ranges.
        In some situations, allowing the user to directly adjust these values can be
        undesirable.  Setting this attribute to zero disables display of and interaction
        with click and go handles for the specific object instance.
        
        Note: both 'handles_enabled' and 'HANDLES_ENABLED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HANDLES_ENABLED)
        _value = cast(int, value)
        return _value

    @handles_enabled.setter
    def handles_enabled(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HANDLES_ENABLED, value)

    @property
    def SELECTED(self) -> int:
        """SELECTED property
        
        selected
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SELECTED)
        _value = cast(int, value)
        return _value

    @SELECTED.setter
    def SELECTED(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SELECTED, value)

    @property
    def selected(self) -> int:
        """SELECTED property
        
        selected
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'selected' and 'SELECTED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SELECTED)
        _value = cast(int, value)
        return _value

    @selected.setter
    def selected(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SELECTED, value)

    @property
    def INDEX(self) -> int:
        """INDEX property
        
        index
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.INDEX)
        _value = cast(int, value)
        return _value

    @property
    def index(self) -> int:
        """INDEX property
        
        index
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'index' and 'INDEX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.INDEX)
        _value = cast(int, value)
        return _value

    @property
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        Description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 80 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @DESCRIPTION.setter
    def DESCRIPTION(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DESCRIPTION, value)

    @property
    def description(self) -> str:
        """DESCRIPTION property
        
        Description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 80 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @description.setter
    def description(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DESCRIPTION, value)

    @property
    def UNIQUENAME(self) -> str:
        """UNIQUENAME property
        
        Unique plotter name
        
        Supported operations:
            getattr
        Datatype:
            String, 80 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.UNIQUENAME)
        _value = cast(str, value)
        return _value

    @property
    def uniquename(self) -> str:
        """UNIQUENAME property
        
        Unique plotter name
        
        Supported operations:
            getattr
        Datatype:
            String, 80 characters maximum
        
        Note: both 'uniquename' and 'UNIQUENAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.UNIQUENAME)
        _value = cast(str, value)
        return _value

    @property
    def QUERIES(self) -> ensobjlist['ENS_QUERY']:
        """QUERIES property
        
        Plotted queries
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERIES)
        _value = cast(ensobjlist['ENS_QUERY'], value)
        return _value

    @property
    def queries(self) -> ensobjlist['ENS_QUERY']:
        """QUERIES property
        
        Plotted queries
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'queries' and 'QUERIES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERIES)
        _value = cast(ensobjlist['ENS_QUERY'], value)
        return _value

    @property
    def VAR_XAXIS(self) -> str:
        """VAR_XAXIS property
        
        X variable
        
        Supported operations:
            getattr
        Datatype:
            String, 50 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_XAXIS)
        _value = cast(str, value)
        return _value

    @property
    def var_xaxis(self) -> str:
        """VAR_XAXIS property
        
        X variable
        
        Supported operations:
            getattr
        Datatype:
            String, 50 characters maximum
        
        Note: both 'var_xaxis' and 'VAR_XAXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_XAXIS)
        _value = cast(str, value)
        return _value

    @property
    def VAR_YAXIS_RIGHT(self) -> str:
        """VAR_YAXIS_RIGHT property
        
        Y2 variable
        
        Supported operations:
            getattr
        Datatype:
            String, 50 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_RIGHT)
        _value = cast(str, value)
        return _value

    @property
    def var_yaxis_right(self) -> str:
        """VAR_YAXIS_RIGHT property
        
        Y2 variable
        
        Supported operations:
            getattr
        Datatype:
            String, 50 characters maximum
        
        Note: both 'var_yaxis_right' and 'VAR_YAXIS_RIGHT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_RIGHT)
        _value = cast(str, value)
        return _value

    @property
    def VAR_YAXIS_LEFT(self) -> str:
        """VAR_YAXIS_LEFT property
        
        Y variable
        
        Supported operations:
            getattr
        Datatype:
            String, 50 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_LEFT)
        _value = cast(str, value)
        return _value

    @property
    def var_yaxis_left(self) -> str:
        """VAR_YAXIS_LEFT property
        
        Y variable
        
        Supported operations:
            getattr
        Datatype:
            String, 50 characters maximum
        
        Note: both 'var_yaxis_left' and 'VAR_YAXIS_LEFT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_LEFT)
        _value = cast(str, value)
        return _value

    @property
    def VAR_XAXIS_OBJ(self) -> object:
        """VAR_XAXIS_OBJ property
        
        X variable object
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_XAXIS_OBJ)
        _value = cast(object, value)
        return _value

    @property
    def var_xaxis_obj(self) -> object:
        """VAR_XAXIS_OBJ property
        
        X variable object
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'var_xaxis_obj' and 'VAR_XAXIS_OBJ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_XAXIS_OBJ)
        _value = cast(object, value)
        return _value

    @property
    def VAR_YAXIS_RIGHT_OBJ(self) -> object:
        """VAR_YAXIS_RIGHT_OBJ property
        
        Y2 variable object
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_RIGHT_OBJ)
        _value = cast(object, value)
        return _value

    @property
    def var_yaxis_right_obj(self) -> object:
        """VAR_YAXIS_RIGHT_OBJ property
        
        Y2 variable object
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'var_yaxis_right_obj' and 'VAR_YAXIS_RIGHT_OBJ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_RIGHT_OBJ)
        _value = cast(object, value)
        return _value

    @property
    def VAR_YAXIS_LEFT_OBJ(self) -> object:
        """VAR_YAXIS_LEFT_OBJ property
        
        Y variable object
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_LEFT_OBJ)
        _value = cast(object, value)
        return _value

    @property
    def var_yaxis_left_obj(self) -> object:
        """VAR_YAXIS_LEFT_OBJ property
        
        Y variable object
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'var_yaxis_left_obj' and 'VAR_YAXIS_LEFT_OBJ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VAR_YAXIS_LEFT_OBJ)
        _value = cast(object, value)
        return _value

    @property
    def VISIBLE(self) -> int:
        """VISIBLE property
        
        Show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBLE)
        _value = cast(int, value)
        return _value

    @VISIBLE.setter
    def VISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBLE, value)

    @property
    def visible(self) -> int:
        """VISIBLE property
        
        Show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'visible' and 'VISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBLE)
        _value = cast(int, value)
        return _value

    @visible.setter
    def visible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBLE, value)

    @property
    def PLOTTITLE(self) -> str:
        """PLOTTITLE property
        
        Plot title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 80 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTTITLE)
        _value = cast(str, value)
        return _value

    @PLOTTITLE.setter
    def PLOTTITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PLOTTITLE, value)

    @property
    def plottitle(self) -> str:
        """PLOTTITLE property
        
        Plot title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 80 characters maximum
        
        Note: both 'plottitle' and 'PLOTTITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTTITLE)
        _value = cast(str, value)
        return _value

    @plottitle.setter
    def plottitle(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PLOTTITLE, value)

    @property
    def WIDTH(self) -> float:
        """WIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.WIDTH)
        _value = cast(float, value)
        return _value

    @WIDTH.setter
    def WIDTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.WIDTH, value)

    @property
    def width(self) -> float:
        """WIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'width' and 'WIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.WIDTH)
        _value = cast(float, value)
        return _value

    @width.setter
    def width(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.WIDTH, value)

    @property
    def HEIGHT(self) -> float:
        """HEIGHT property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HEIGHT)
        _value = cast(float, value)
        return _value

    @HEIGHT.setter
    def HEIGHT(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEIGHT, value)

    @property
    def height(self) -> float:
        """HEIGHT property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'height' and 'HEIGHT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HEIGHT)
        _value = cast(float, value)
        return _value

    @height.setter
    def height(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEIGHT, value)

    @property
    def BACKGROUNDRGB(self) -> List[float]:
        """BACKGROUNDRGB property
        
        Background color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDRGB)
        _value = cast(List[float], value)
        return _value

    @BACKGROUNDRGB.setter
    def BACKGROUNDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDRGB, value)

    @property
    def backgroundrgb(self) -> List[float]:
        """BACKGROUNDRGB property
        
        Background color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'backgroundrgb' and 'BACKGROUNDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDRGB)
        _value = cast(List[float], value)
        return _value

    @backgroundrgb.setter
    def backgroundrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDRGB, value)

    @property
    def ORIGINX(self) -> float:
        """ORIGINX property
        
        Location X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINX)
        _value = cast(float, value)
        return _value

    @ORIGINX.setter
    def ORIGINX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINX, value)

    @property
    def originx(self) -> float:
        """ORIGINX property
        
        Location X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'originx' and 'ORIGINX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINX)
        _value = cast(float, value)
        return _value

    @originx.setter
    def originx(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINX, value)

    @property
    def ORIGINY(self) -> float:
        """ORIGINY property
        
        Location Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINY)
        _value = cast(float, value)
        return _value

    @ORIGINY.setter
    def ORIGINY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINY, value)

    @property
    def originy(self) -> float:
        """ORIGINY property
        
        Location Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'originy' and 'ORIGINY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINY)
        _value = cast(float, value)
        return _value

    @originy.setter
    def originy(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINY, value)

    @property
    def BACKGROUNDTYPE(self) -> int:
        """BACKGROUNDTYPE property
        
        Background type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PLOT_BG_SOLID - solid
            * ensight.objs.enums.PLOT_BG_NONE - none
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDTYPE)
        _value = cast(int, value)
        return _value

    @BACKGROUNDTYPE.setter
    def BACKGROUNDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDTYPE, value)

    @property
    def backgroundtype(self) -> int:
        """BACKGROUNDTYPE property
        
        Background type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PLOT_BG_SOLID - solid
            * ensight.objs.enums.PLOT_BG_NONE - none
        
        Note: both 'backgroundtype' and 'BACKGROUNDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDTYPE)
        _value = cast(int, value)
        return _value

    @backgroundtype.setter
    def backgroundtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDTYPE, value)

    @property
    def BORDERVISIBLE(self) -> int:
        """BORDERVISIBLE property
        
        Border visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERVISIBLE)
        _value = cast(int, value)
        return _value

    @BORDERVISIBLE.setter
    def BORDERVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERVISIBLE, value)

    @property
    def bordervisible(self) -> int:
        """BORDERVISIBLE property
        
        Border visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'bordervisible' and 'BORDERVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERVISIBLE)
        _value = cast(int, value)
        return _value

    @bordervisible.setter
    def bordervisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERVISIBLE, value)

    @property
    def AXISLINEWIDTH(self) -> int:
        """AXISLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISLINEWIDTH)
        _value = cast(int, value)
        return _value

    @AXISLINEWIDTH.setter
    def AXISLINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISLINEWIDTH, value)

    @property
    def axislinewidth(self) -> int:
        """AXISLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'axislinewidth' and 'AXISLINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISLINEWIDTH)
        _value = cast(int, value)
        return _value

    @axislinewidth.setter
    def axislinewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISLINEWIDTH, value)

    @property
    def AXISRGB(self) -> List[float]:
        """AXISRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISRGB)
        _value = cast(List[float], value)
        return _value

    @AXISRGB.setter
    def AXISRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISRGB, value)

    @property
    def axisrgb(self) -> List[float]:
        """AXISRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisrgb' and 'AXISRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISRGB)
        _value = cast(List[float], value)
        return _value

    @axisrgb.setter
    def axisrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISRGB, value)

    @property
    def GRIDLINEWIDTH(self) -> int:
        """GRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @GRIDLINEWIDTH.setter
    def GRIDLINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINEWIDTH, value)

    @property
    def gridlinewidth(self) -> int:
        """GRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'gridlinewidth' and 'GRIDLINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @gridlinewidth.setter
    def gridlinewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINEWIDTH, value)

    @property
    def GRIDLINETYPE(self) -> int:
        """GRIDLINETYPE property
        
        Line type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @GRIDLINETYPE.setter
    def GRIDLINETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINETYPE, value)

    @property
    def gridlinetype(self) -> int:
        """GRIDLINETYPE property
        
        Line type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        Note: both 'gridlinetype' and 'GRIDLINETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @gridlinetype.setter
    def gridlinetype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINETYPE, value)

    @property
    def GRIDRGB(self) -> List[float]:
        """GRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDRGB)
        _value = cast(List[float], value)
        return _value

    @GRIDRGB.setter
    def GRIDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDRGB, value)

    @property
    def gridrgb(self) -> List[float]:
        """GRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'gridrgb' and 'GRIDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDRGB)
        _value = cast(List[float], value)
        return _value

    @gridrgb.setter
    def gridrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDRGB, value)

    @property
    def SUBGRIDLINEWIDTH(self) -> int:
        """SUBGRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @SUBGRIDLINEWIDTH.setter
    def SUBGRIDLINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH, value)

    @property
    def subgridlinewidth(self) -> int:
        """SUBGRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'subgridlinewidth' and 'SUBGRIDLINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @subgridlinewidth.setter
    def subgridlinewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH, value)

    @property
    def SUBGRIDLINETYPE(self) -> int:
        """SUBGRIDLINETYPE property
        
        Line type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @SUBGRIDLINETYPE.setter
    def SUBGRIDLINETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE, value)

    @property
    def subgridlinetype(self) -> int:
        """SUBGRIDLINETYPE property
        
        Line type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        Note: both 'subgridlinetype' and 'SUBGRIDLINETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @subgridlinetype.setter
    def subgridlinetype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE, value)

    @property
    def SUBGRIDRGB(self) -> List[float]:
        """SUBGRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDRGB)
        _value = cast(List[float], value)
        return _value

    @SUBGRIDRGB.setter
    def SUBGRIDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDRGB, value)

    @property
    def subgridrgb(self) -> List[float]:
        """SUBGRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'subgridrgb' and 'SUBGRIDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDRGB)
        _value = cast(List[float], value)
        return _value

    @subgridrgb.setter
    def subgridrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDRGB, value)

    @property
    def AXISXTITLE(self) -> str:
        """AXISXTITLE property
        
        Title text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLE)
        _value = cast(str, value)
        return _value

    @AXISXTITLE.setter
    def AXISXTITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLE, value)

    @property
    def axisxtitle(self) -> str:
        """AXISXTITLE property
        
        Title text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisxtitle' and 'AXISXTITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLE)
        _value = cast(str, value)
        return _value

    @axisxtitle.setter
    def axisxtitle(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLE, value)

    @property
    def AXISYTITLE(self) -> str:
        """AXISYTITLE property
        
        Title text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLE)
        _value = cast(str, value)
        return _value

    @AXISYTITLE.setter
    def AXISYTITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLE, value)

    @property
    def axisytitle(self) -> str:
        """AXISYTITLE property
        
        Title text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisytitle' and 'AXISYTITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLE)
        _value = cast(str, value)
        return _value

    @axisytitle.setter
    def axisytitle(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLE, value)

    @property
    def AXISXTITLESIZE(self) -> int:
        """AXISXTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLESIZE)
        _value = cast(int, value)
        return _value

    @AXISXTITLESIZE.setter
    def AXISXTITLESIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLESIZE, value)

    @property
    def axisxtitlesize(self) -> int:
        """AXISXTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axisxtitlesize' and 'AXISXTITLESIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLESIZE)
        _value = cast(int, value)
        return _value

    @axisxtitlesize.setter
    def axisxtitlesize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLESIZE, value)

    @property
    def AXISXMIN(self) -> float:
        """AXISXMIN property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMIN)
        _value = cast(float, value)
        return _value

    @AXISXMIN.setter
    def AXISXMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMIN, value)

    @property
    def axisxmin(self) -> float:
        """AXISXMIN property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisxmin' and 'AXISXMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMIN)
        _value = cast(float, value)
        return _value

    @axisxmin.setter
    def axisxmin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMIN, value)

    @property
    def AXISXMAX(self) -> float:
        """AXISXMAX property
        
        Maximum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMAX)
        _value = cast(float, value)
        return _value

    @AXISXMAX.setter
    def AXISXMAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMAX, value)

    @property
    def axisxmax(self) -> float:
        """AXISXMAX property
        
        Maximum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisxmax' and 'AXISXMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMAX)
        _value = cast(float, value)
        return _value

    @axisxmax.setter
    def axisxmax(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMAX, value)

    @property
    def AXISXLABELRGB(self) -> List[float]:
        """AXISXLABELRGB property
        
        Label color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELRGB)
        _value = cast(List[float], value)
        return _value

    @AXISXLABELRGB.setter
    def AXISXLABELRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELRGB, value)

    @property
    def axisxlabelrgb(self) -> List[float]:
        """AXISXLABELRGB property
        
        Label color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisxlabelrgb' and 'AXISXLABELRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELRGB)
        _value = cast(List[float], value)
        return _value

    @axisxlabelrgb.setter
    def axisxlabelrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELRGB, value)

    @property
    def AXISXGRIDTYPE(self) -> int:
        """AXISXGRIDTYPE property
        
        Grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISXGRIDTYPE.setter
    def AXISXGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXGRIDTYPE, value)

    @property
    def axisxgridtype(self) -> int:
        """AXISXGRIDTYPE property
        
        Grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisxgridtype' and 'AXISXGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisxgridtype.setter
    def axisxgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXGRIDTYPE, value)

    @property
    def AXISXNUMGRID(self) -> float:
        """AXISXNUMGRID property
        
        Grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMGRID)
        _value = cast(float, value)
        return _value

    @AXISXNUMGRID.setter
    def AXISXNUMGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMGRID, value)

    @property
    def axisxnumgrid(self) -> float:
        """AXISXNUMGRID property
        
        Grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisxnumgrid' and 'AXISXNUMGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMGRID)
        _value = cast(float, value)
        return _value

    @axisxnumgrid.setter
    def axisxnumgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMGRID, value)

    @property
    def AXISXSGRIDTYPE(self) -> int:
        """AXISXSGRIDTYPE property
        
        Sub-grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISXSGRIDTYPE.setter
    def AXISXSGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE, value)

    @property
    def axisxsgridtype(self) -> int:
        """AXISXSGRIDTYPE property
        
        Sub-grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisxsgridtype' and 'AXISXSGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisxsgridtype.setter
    def axisxsgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE, value)

    @property
    def AXISXNUMSUBGRID(self) -> float:
        """AXISXNUMSUBGRID property
        
        Sub-grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @AXISXNUMSUBGRID.setter
    def AXISXNUMSUBGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID, value)

    @property
    def axisxnumsubgrid(self) -> float:
        """AXISXNUMSUBGRID property
        
        Sub-grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisxnumsubgrid' and 'AXISXNUMSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @axisxnumsubgrid.setter
    def axisxnumsubgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID, value)

    @property
    def AXISYTITLESIZE(self) -> int:
        """AXISYTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLESIZE)
        _value = cast(int, value)
        return _value

    @AXISYTITLESIZE.setter
    def AXISYTITLESIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLESIZE, value)

    @property
    def axisytitlesize(self) -> int:
        """AXISYTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axisytitlesize' and 'AXISYTITLESIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLESIZE)
        _value = cast(int, value)
        return _value

    @axisytitlesize.setter
    def axisytitlesize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLESIZE, value)

    @property
    def AXISYMIN(self) -> float:
        """AXISYMIN property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMIN)
        _value = cast(float, value)
        return _value

    @AXISYMIN.setter
    def AXISYMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMIN, value)

    @property
    def axisymin(self) -> float:
        """AXISYMIN property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisymin' and 'AXISYMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMIN)
        _value = cast(float, value)
        return _value

    @axisymin.setter
    def axisymin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMIN, value)

    @property
    def AXISYMAX(self) -> float:
        """AXISYMAX property
        
        Maximum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMAX)
        _value = cast(float, value)
        return _value

    @AXISYMAX.setter
    def AXISYMAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMAX, value)

    @property
    def axisymax(self) -> float:
        """AXISYMAX property
        
        Maximum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisymax' and 'AXISYMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMAX)
        _value = cast(float, value)
        return _value

    @axisymax.setter
    def axisymax(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMAX, value)

    @property
    def AXISYLABELRGB(self) -> List[float]:
        """AXISYLABELRGB property
        
        Label color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELRGB)
        _value = cast(List[float], value)
        return _value

    @AXISYLABELRGB.setter
    def AXISYLABELRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELRGB, value)

    @property
    def axisylabelrgb(self) -> List[float]:
        """AXISYLABELRGB property
        
        Label color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisylabelrgb' and 'AXISYLABELRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELRGB)
        _value = cast(List[float], value)
        return _value

    @axisylabelrgb.setter
    def axisylabelrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELRGB, value)

    @property
    def AXISYGRIDTYPE(self) -> int:
        """AXISYGRIDTYPE property
        
        Grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISYGRIDTYPE.setter
    def AXISYGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYGRIDTYPE, value)

    @property
    def axisygridtype(self) -> int:
        """AXISYGRIDTYPE property
        
        Grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisygridtype' and 'AXISYGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisygridtype.setter
    def axisygridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYGRIDTYPE, value)

    @property
    def AXISYNUMGRID(self) -> float:
        """AXISYNUMGRID property
        
        Grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMGRID)
        _value = cast(float, value)
        return _value

    @AXISYNUMGRID.setter
    def AXISYNUMGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMGRID, value)

    @property
    def axisynumgrid(self) -> float:
        """AXISYNUMGRID property
        
        Grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisynumgrid' and 'AXISYNUMGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMGRID)
        _value = cast(float, value)
        return _value

    @axisynumgrid.setter
    def axisynumgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMGRID, value)

    @property
    def AXISYSGRIDTYPE(self) -> int:
        """AXISYSGRIDTYPE property
        
        Sub-grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISYSGRIDTYPE.setter
    def AXISYSGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE, value)

    @property
    def axisysgridtype(self) -> int:
        """AXISYSGRIDTYPE property
        
        Sub-grid type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisysgridtype' and 'AXISYSGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisysgridtype.setter
    def axisysgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE, value)

    @property
    def AXISYNUMSUBGRID(self) -> float:
        """AXISYNUMSUBGRID property
        
        Sub-grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @AXISYNUMSUBGRID.setter
    def AXISYNUMSUBGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID, value)

    @property
    def axisynumsubgrid(self) -> float:
        """AXISYNUMSUBGRID property
        
        Sub-grid # lines(Linear)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisynumsubgrid' and 'AXISYNUMSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @axisynumsubgrid.setter
    def axisynumsubgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID, value)

    @property
    def TITLETEXTSIZE(self) -> int:
        """TITLETEXTSIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TITLETEXTSIZE)
        _value = cast(int, value)
        return _value

    @TITLETEXTSIZE.setter
    def TITLETEXTSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TITLETEXTSIZE, value)

    @property
    def titletextsize(self) -> int:
        """TITLETEXTSIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'titletextsize' and 'TITLETEXTSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TITLETEXTSIZE)
        _value = cast(int, value)
        return _value

    @titletextsize.setter
    def titletextsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TITLETEXTSIZE, value)

    @property
    def TITLERGB(self) -> List[float]:
        """TITLERGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TITLERGB)
        _value = cast(List[float], value)
        return _value

    @TITLERGB.setter
    def TITLERGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TITLERGB, value)

    @property
    def titlergb(self) -> List[float]:
        """TITLERGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'titlergb' and 'TITLERGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TITLERGB)
        _value = cast(List[float], value)
        return _value

    @titlergb.setter
    def titlergb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TITLERGB, value)

    @property
    def ANIMATECURVES(self) -> int:
        """ANIMATECURVES property
        
        Animate curves
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANIMATECURVES)
        _value = cast(int, value)
        return _value

    @ANIMATECURVES.setter
    def ANIMATECURVES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANIMATECURVES, value)

    @property
    def animatecurves(self) -> int:
        """ANIMATECURVES property
        
        Animate curves
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'animatecurves' and 'ANIMATECURVES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANIMATECURVES)
        _value = cast(int, value)
        return _value

    @animatecurves.setter
    def animatecurves(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANIMATECURVES, value)

    @property
    def TIMEMARKER(self) -> int:
        """TIMEMARKER property
        
        Marker
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKER)
        _value = cast(int, value)
        return _value

    @TIMEMARKER.setter
    def TIMEMARKER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKER, value)

    @property
    def timemarker(self) -> int:
        """TIMEMARKER property
        
        Marker
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'timemarker' and 'TIMEMARKER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKER)
        _value = cast(int, value)
        return _value

    @timemarker.setter
    def timemarker(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKER, value)

    @property
    def TIMEMARKERRGB(self) -> List[float]:
        """TIMEMARKERRGB property
        
        Marker color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERRGB)
        _value = cast(List[float], value)
        return _value

    @TIMEMARKERRGB.setter
    def TIMEMARKERRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERRGB, value)

    @property
    def timemarkerrgb(self) -> List[float]:
        """TIMEMARKERRGB property
        
        Marker color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'timemarkerrgb' and 'TIMEMARKERRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERRGB)
        _value = cast(List[float], value)
        return _value

    @timemarkerrgb.setter
    def timemarkerrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERRGB, value)

    @property
    def TIMEMARKERWIDTH(self) -> int:
        """TIMEMARKERWIDTH property
        
        Marker width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERWIDTH)
        _value = cast(int, value)
        return _value

    @TIMEMARKERWIDTH.setter
    def TIMEMARKERWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERWIDTH, value)

    @property
    def timemarkerwidth(self) -> int:
        """TIMEMARKERWIDTH property
        
        Marker width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'timemarkerwidth' and 'TIMEMARKERWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERWIDTH)
        _value = cast(int, value)
        return _value

    @timemarkerwidth.setter
    def timemarkerwidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERWIDTH, value)

    @property
    def TIMEMARKERSTYLE(self) -> int:
        """TIMEMARKERSTYLE property
        
        Marker style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERSTYLE)
        _value = cast(int, value)
        return _value

    @TIMEMARKERSTYLE.setter
    def TIMEMARKERSTYLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERSTYLE, value)

    @property
    def timemarkerstyle(self) -> int:
        """TIMEMARKERSTYLE property
        
        Marker style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        Note: both 'timemarkerstyle' and 'TIMEMARKERSTYLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERSTYLE)
        _value = cast(int, value)
        return _value

    @timemarkerstyle.setter
    def timemarkerstyle(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERSTYLE, value)

    @property
    def TIMEMARKERVALUE(self) -> int:
        """TIMEMARKERVALUE property
        
        Marker value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERVALUE)
        _value = cast(int, value)
        return _value

    @TIMEMARKERVALUE.setter
    def TIMEMARKERVALUE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERVALUE, value)

    @property
    def timemarkervalue(self) -> int:
        """TIMEMARKERVALUE property
        
        Marker value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'timemarkervalue' and 'TIMEMARKERVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEMARKERVALUE)
        _value = cast(int, value)
        return _value

    @timemarkervalue.setter
    def timemarkervalue(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEMARKERVALUE, value)

    @property
    def BACKGROUNDTRANSPARENCY(self) -> float:
        """BACKGROUNDTRANSPARENCY property
        
        Background transparency
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDTRANSPARENCY)
        _value = cast(float, value)
        return _value

    @BACKGROUNDTRANSPARENCY.setter
    def BACKGROUNDTRANSPARENCY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDTRANSPARENCY, value)

    @property
    def backgroundtransparency(self) -> float:
        """BACKGROUNDTRANSPARENCY property
        
        Background transparency
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'backgroundtransparency' and 'BACKGROUNDTRANSPARENCY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDTRANSPARENCY)
        _value = cast(float, value)
        return _value

    @backgroundtransparency.setter
    def backgroundtransparency(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDTRANSPARENCY, value)

    @property
    def BORDERRGB(self) -> List[float]:
        """BORDERRGB property
        
        Border color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERRGB)
        _value = cast(List[float], value)
        return _value

    @BORDERRGB.setter
    def BORDERRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERRGB, value)

    @property
    def borderrgb(self) -> List[float]:
        """BORDERRGB property
        
        Border color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'borderrgb' and 'BORDERRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERRGB)
        _value = cast(List[float], value)
        return _value

    @borderrgb.setter
    def borderrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERRGB, value)

    @property
    def LEGENDVISIBLE(self) -> int:
        """LEGENDVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDVISIBLE)
        _value = cast(int, value)
        return _value

    @LEGENDVISIBLE.setter
    def LEGENDVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDVISIBLE, value)

    @property
    def legendvisible(self) -> int:
        """LEGENDVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'legendvisible' and 'LEGENDVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDVISIBLE)
        _value = cast(int, value)
        return _value

    @legendvisible.setter
    def legendvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDVISIBLE, value)

    @property
    def LEGENDORIGINX(self) -> float:
        """LEGENDORIGINX property
        
        Location X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDORIGINX)
        _value = cast(float, value)
        return _value

    @LEGENDORIGINX.setter
    def LEGENDORIGINX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDORIGINX, value)

    @property
    def legendoriginx(self) -> float:
        """LEGENDORIGINX property
        
        Location X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'legendoriginx' and 'LEGENDORIGINX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDORIGINX)
        _value = cast(float, value)
        return _value

    @legendoriginx.setter
    def legendoriginx(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDORIGINX, value)

    @property
    def LEGENDORIGINY(self) -> float:
        """LEGENDORIGINY property
        
        Location Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDORIGINY)
        _value = cast(float, value)
        return _value

    @LEGENDORIGINY.setter
    def LEGENDORIGINY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDORIGINY, value)

    @property
    def legendoriginy(self) -> float:
        """LEGENDORIGINY property
        
        Location Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'legendoriginy' and 'LEGENDORIGINY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDORIGINY)
        _value = cast(float, value)
        return _value

    @legendoriginy.setter
    def legendoriginy(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDORIGINY, value)

    @property
    def LEGENDTEXTSIZE(self) -> int:
        """LEGENDTEXTSIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDTEXTSIZE)
        _value = cast(int, value)
        return _value

    @LEGENDTEXTSIZE.setter
    def LEGENDTEXTSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDTEXTSIZE, value)

    @property
    def legendtextsize(self) -> int:
        """LEGENDTEXTSIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'legendtextsize' and 'LEGENDTEXTSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDTEXTSIZE)
        _value = cast(int, value)
        return _value

    @legendtextsize.setter
    def legendtextsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDTEXTSIZE, value)

    @property
    def LEGENDCOLORBY(self) -> int:
        """LEGENDCOLORBY property
        
        Color by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PLOTTER_LEGEND_COLOR_USE_CURVE - curve_color
            * ensight.objs.enums.PLOTTER_LEGEND_COLOR_RGB - specified_rgb
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDCOLORBY)
        _value = cast(int, value)
        return _value

    @LEGENDCOLORBY.setter
    def LEGENDCOLORBY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDCOLORBY, value)

    @property
    def legendcolorby(self) -> int:
        """LEGENDCOLORBY property
        
        Color by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PLOTTER_LEGEND_COLOR_USE_CURVE - curve_color
            * ensight.objs.enums.PLOTTER_LEGEND_COLOR_RGB - specified_rgb
        
        Note: both 'legendcolorby' and 'LEGENDCOLORBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDCOLORBY)
        _value = cast(int, value)
        return _value

    @legendcolorby.setter
    def legendcolorby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDCOLORBY, value)

    @property
    def LEGENDRGB(self) -> List[float]:
        """LEGENDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDRGB)
        _value = cast(List[float], value)
        return _value

    @LEGENDRGB.setter
    def LEGENDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDRGB, value)

    @property
    def legendrgb(self) -> List[float]:
        """LEGENDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'legendrgb' and 'LEGENDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDRGB)
        _value = cast(List[float], value)
        return _value

    @legendrgb.setter
    def legendrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDRGB, value)

    @property
    def LEGENDMINMAXVISIBLE(self) -> int:
        """LEGENDMINMAXVISIBLE property
        
        Min/max text
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXVISIBLE)
        _value = cast(int, value)
        return _value

    @LEGENDMINMAXVISIBLE.setter
    def LEGENDMINMAXVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXVISIBLE, value)

    @property
    def legendminmaxvisible(self) -> int:
        """LEGENDMINMAXVISIBLE property
        
        Min/max text
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'legendminmaxvisible' and 'LEGENDMINMAXVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXVISIBLE)
        _value = cast(int, value)
        return _value

    @legendminmaxvisible.setter
    def legendminmaxvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXVISIBLE, value)

    @property
    def LEGENDMINMAXORIGINX(self) -> float:
        """LEGENDMINMAXORIGINX property
        
        Min/max location X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINX)
        _value = cast(float, value)
        return _value

    @LEGENDMINMAXORIGINX.setter
    def LEGENDMINMAXORIGINX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINX, value)

    @property
    def legendminmaxoriginx(self) -> float:
        """LEGENDMINMAXORIGINX property
        
        Min/max location X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'legendminmaxoriginx' and 'LEGENDMINMAXORIGINX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINX)
        _value = cast(float, value)
        return _value

    @legendminmaxoriginx.setter
    def legendminmaxoriginx(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINX, value)

    @property
    def LEGENDMINMAXORIGINY(self) -> float:
        """LEGENDMINMAXORIGINY property
        
        Min/max location Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINY)
        _value = cast(float, value)
        return _value

    @LEGENDMINMAXORIGINY.setter
    def LEGENDMINMAXORIGINY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINY, value)

    @property
    def legendminmaxoriginy(self) -> float:
        """LEGENDMINMAXORIGINY property
        
        Min/max location Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'legendminmaxoriginy' and 'LEGENDMINMAXORIGINY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINY)
        _value = cast(float, value)
        return _value

    @legendminmaxoriginy.setter
    def legendminmaxoriginy(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXORIGINY, value)

    @property
    def LEGENDMINMAXTEXTSIZE(self) -> int:
        """LEGENDMINMAXTEXTSIZE property
        
        Min/max text size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXTEXTSIZE)
        _value = cast(int, value)
        return _value

    @LEGENDMINMAXTEXTSIZE.setter
    def LEGENDMINMAXTEXTSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXTEXTSIZE, value)

    @property
    def legendminmaxtextsize(self) -> int:
        """LEGENDMINMAXTEXTSIZE property
        
        Min/max text size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'legendminmaxtextsize' and 'LEGENDMINMAXTEXTSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDMINMAXTEXTSIZE)
        _value = cast(int, value)
        return _value

    @legendminmaxtextsize.setter
    def legendminmaxtextsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDMINMAXTEXTSIZE, value)

    @property
    def AXISAUTOLAYOUT(self) -> int:
        """AXISAUTOLAYOUT property
        
        Auto layout
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISAUTOLAYOUT)
        _value = cast(int, value)
        return _value

    @AXISAUTOLAYOUT.setter
    def AXISAUTOLAYOUT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISAUTOLAYOUT, value)

    @property
    def axisautolayout(self) -> int:
        """AXISAUTOLAYOUT property
        
        Auto layout
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisautolayout' and 'AXISAUTOLAYOUT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISAUTOLAYOUT)
        _value = cast(int, value)
        return _value

    @axisautolayout.setter
    def axisautolayout(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISAUTOLAYOUT, value)

    @property
    def AXISAUTOUPDATE(self) -> int:
        """AXISAUTOUPDATE property
        
        Auto Update
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISAUTOUPDATE)
        _value = cast(int, value)
        return _value

    @AXISAUTOUPDATE.setter
    def AXISAUTOUPDATE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISAUTOUPDATE, value)

    @property
    def axisautoupdate(self) -> int:
        """AXISAUTOUPDATE property
        
        Auto Update
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisautoupdate' and 'AXISAUTOUPDATE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISAUTOUPDATE)
        _value = cast(int, value)
        return _value

    @axisautoupdate.setter
    def axisautoupdate(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISAUTOUPDATE, value)

    @property
    def AXISSWAP(self) -> int:
        """AXISSWAP property
        
        Swap
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISSWAP)
        _value = cast(int, value)
        return _value

    @AXISSWAP.setter
    def AXISSWAP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISSWAP, value)

    @property
    def axisswap(self) -> int:
        """AXISSWAP property
        
        Swap
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisswap' and 'AXISSWAP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISSWAP)
        _value = cast(int, value)
        return _value

    @axisswap.setter
    def axisswap(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISSWAP, value)

    @property
    def AXISXTITLERGB(self) -> List[float]:
        """AXISXTITLERGB property
        
        Title color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLERGB)
        _value = cast(List[float], value)
        return _value

    @AXISXTITLERGB.setter
    def AXISXTITLERGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLERGB, value)

    @property
    def axisxtitlergb(self) -> List[float]:
        """AXISXTITLERGB property
        
        Title color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisxtitlergb' and 'AXISXTITLERGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLERGB)
        _value = cast(List[float], value)
        return _value

    @axisxtitlergb.setter
    def axisxtitlergb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLERGB, value)

    @property
    def AXISXLABELTYPE(self) -> int:
        """AXISXLABELTYPE property
        
        Label type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELTYPE)
        _value = cast(int, value)
        return _value

    @AXISXLABELTYPE.setter
    def AXISXLABELTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELTYPE, value)

    @property
    def axisxlabeltype(self) -> int:
        """AXISXLABELTYPE property
        
        Label type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        Note: both 'axisxlabeltype' and 'AXISXLABELTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELTYPE)
        _value = cast(int, value)
        return _value

    @axisxlabeltype.setter
    def axisxlabeltype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELTYPE, value)

    @property
    def AXISXLABELSIZE(self) -> int:
        """AXISXLABELSIZE property
        
        Label size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELSIZE)
        _value = cast(int, value)
        return _value

    @AXISXLABELSIZE.setter
    def AXISXLABELSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELSIZE, value)

    @property
    def axisxlabelsize(self) -> int:
        """AXISXLABELSIZE property
        
        Label size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axisxlabelsize' and 'AXISXLABELSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELSIZE)
        _value = cast(int, value)
        return _value

    @axisxlabelsize.setter
    def axisxlabelsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELSIZE, value)

    @property
    def AXISXSCALE(self) -> int:
        """AXISXSCALE property
        
        Label scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - linear
            * ensight.objs.enums.TRUE - logarithmic
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSCALE)
        _value = cast(int, value)
        return _value

    @AXISXSCALE.setter
    def AXISXSCALE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSCALE, value)

    @property
    def axisxscale(self) -> int:
        """AXISXSCALE property
        
        Label scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - linear
            * ensight.objs.enums.TRUE - logarithmic
        
        Note: both 'axisxscale' and 'AXISXSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSCALE)
        _value = cast(int, value)
        return _value

    @axisxscale.setter
    def axisxscale(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSCALE, value)

    @property
    def AXISXLABELFORMAT(self) -> str:
        """AXISXLABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELFORMAT)
        _value = cast(str, value)
        return _value

    @AXISXLABELFORMAT.setter
    def AXISXLABELFORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELFORMAT, value)

    @property
    def axisxlabelformat(self) -> str:
        """AXISXLABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisxlabelformat' and 'AXISXLABELFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELFORMAT)
        _value = cast(str, value)
        return _value

    @axisxlabelformat.setter
    def axisxlabelformat(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELFORMAT, value)

    @property
    def AXISXNUMGRIDLOG(self) -> float:
        """AXISXNUMGRIDLOG property
        
        Grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMGRIDLOG)
        _value = cast(float, value)
        return _value

    @AXISXNUMGRIDLOG.setter
    def AXISXNUMGRIDLOG(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMGRIDLOG, value)

    @property
    def axisxnumgridlog(self) -> float:
        """AXISXNUMGRIDLOG property
        
        Grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisxnumgridlog' and 'AXISXNUMGRIDLOG' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMGRIDLOG)
        _value = cast(float, value)
        return _value

    @axisxnumgridlog.setter
    def axisxnumgridlog(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMGRIDLOG, value)

    @property
    def AXISXNUMSUBGRIDLOG(self) -> float:
        """AXISXNUMSUBGRIDLOG property
        
        Sub-grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMSUBGRIDLOG)
        _value = cast(float, value)
        return _value

    @AXISXNUMSUBGRIDLOG.setter
    def AXISXNUMSUBGRIDLOG(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMSUBGRIDLOG, value)

    @property
    def axisxnumsubgridlog(self) -> float:
        """AXISXNUMSUBGRIDLOG property
        
        Sub-grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisxnumsubgridlog' and 'AXISXNUMSUBGRIDLOG' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMSUBGRIDLOG)
        _value = cast(float, value)
        return _value

    @axisxnumsubgridlog.setter
    def axisxnumsubgridlog(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMSUBGRIDLOG, value)

    @property
    def AXISXVISIBLE(self) -> int:
        """AXISXVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXVISIBLE)
        _value = cast(int, value)
        return _value

    @AXISXVISIBLE.setter
    def AXISXVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXVISIBLE, value)

    @property
    def axisxvisible(self) -> int:
        """AXISXVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxvisible' and 'AXISXVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXVISIBLE)
        _value = cast(int, value)
        return _value

    @axisxvisible.setter
    def axisxvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXVISIBLE, value)

    @property
    def AXISXAUTOSCALE(self) -> int:
        """AXISXAUTOSCALE property
        
        Auto scaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXAUTOSCALE)
        _value = cast(int, value)
        return _value

    @AXISXAUTOSCALE.setter
    def AXISXAUTOSCALE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXAUTOSCALE, value)

    @property
    def axisxautoscale(self) -> int:
        """AXISXAUTOSCALE property
        
        Auto scaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxautoscale' and 'AXISXAUTOSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXAUTOSCALE)
        _value = cast(int, value)
        return _value

    @axisxautoscale.setter
    def axisxautoscale(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXAUTOSCALE, value)

    @property
    def AXISXORIGIN(self) -> float:
        """AXISXORIGIN property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXORIGIN)
        _value = cast(float, value)
        return _value

    @AXISXORIGIN.setter
    def AXISXORIGIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXORIGIN, value)

    @property
    def axisxorigin(self) -> float:
        """AXISXORIGIN property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'axisxorigin' and 'AXISXORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXORIGIN)
        _value = cast(float, value)
        return _value

    @axisxorigin.setter
    def axisxorigin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXORIGIN, value)

    @property
    def AXISXSIZE(self) -> float:
        """AXISXSIZE property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSIZE)
        _value = cast(float, value)
        return _value

    @AXISXSIZE.setter
    def AXISXSIZE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSIZE, value)

    @property
    def axisxsize(self) -> float:
        """AXISXSIZE property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'axisxsize' and 'AXISXSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSIZE)
        _value = cast(float, value)
        return _value

    @axisxsize.setter
    def axisxsize(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSIZE, value)

    @property
    def AXISYTITLERGB(self) -> List[float]:
        """AXISYTITLERGB property
        
        Title color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLERGB)
        _value = cast(List[float], value)
        return _value

    @AXISYTITLERGB.setter
    def AXISYTITLERGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLERGB, value)

    @property
    def axisytitlergb(self) -> List[float]:
        """AXISYTITLERGB property
        
        Title color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisytitlergb' and 'AXISYTITLERGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLERGB)
        _value = cast(List[float], value)
        return _value

    @axisytitlergb.setter
    def axisytitlergb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLERGB, value)

    @property
    def AXISYLABELTYPE(self) -> int:
        """AXISYLABELTYPE property
        
        Label type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELTYPE)
        _value = cast(int, value)
        return _value

    @AXISYLABELTYPE.setter
    def AXISYLABELTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELTYPE, value)

    @property
    def axisylabeltype(self) -> int:
        """AXISYLABELTYPE property
        
        Label type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        Note: both 'axisylabeltype' and 'AXISYLABELTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELTYPE)
        _value = cast(int, value)
        return _value

    @axisylabeltype.setter
    def axisylabeltype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELTYPE, value)

    @property
    def AXISYLABELSIZE(self) -> int:
        """AXISYLABELSIZE property
        
        Label size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELSIZE)
        _value = cast(int, value)
        return _value

    @AXISYLABELSIZE.setter
    def AXISYLABELSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELSIZE, value)

    @property
    def axisylabelsize(self) -> int:
        """AXISYLABELSIZE property
        
        Label size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axisylabelsize' and 'AXISYLABELSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELSIZE)
        _value = cast(int, value)
        return _value

    @axisylabelsize.setter
    def axisylabelsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELSIZE, value)

    @property
    def AXISYSCALE(self) -> int:
        """AXISYSCALE property
        
        Label scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - linear
            * ensight.objs.enums.TRUE - logarithmic
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSCALE)
        _value = cast(int, value)
        return _value

    @AXISYSCALE.setter
    def AXISYSCALE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSCALE, value)

    @property
    def axisyscale(self) -> int:
        """AXISYSCALE property
        
        Label scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - linear
            * ensight.objs.enums.TRUE - logarithmic
        
        Note: both 'axisyscale' and 'AXISYSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSCALE)
        _value = cast(int, value)
        return _value

    @axisyscale.setter
    def axisyscale(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSCALE, value)

    @property
    def AXISYLABELFORMAT(self) -> str:
        """AXISYLABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELFORMAT)
        _value = cast(str, value)
        return _value

    @AXISYLABELFORMAT.setter
    def AXISYLABELFORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELFORMAT, value)

    @property
    def axisylabelformat(self) -> str:
        """AXISYLABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisylabelformat' and 'AXISYLABELFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELFORMAT)
        _value = cast(str, value)
        return _value

    @axisylabelformat.setter
    def axisylabelformat(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELFORMAT, value)

    @property
    def AXISYNUMGRIDLOG(self) -> float:
        """AXISYNUMGRIDLOG property
        
        Grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMGRIDLOG)
        _value = cast(float, value)
        return _value

    @AXISYNUMGRIDLOG.setter
    def AXISYNUMGRIDLOG(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMGRIDLOG, value)

    @property
    def axisynumgridlog(self) -> float:
        """AXISYNUMGRIDLOG property
        
        Grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisynumgridlog' and 'AXISYNUMGRIDLOG' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMGRIDLOG)
        _value = cast(float, value)
        return _value

    @axisynumgridlog.setter
    def axisynumgridlog(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMGRIDLOG, value)

    @property
    def AXISYNUMSUBGRIDLOG(self) -> float:
        """AXISYNUMSUBGRIDLOG property
        
        Sub-grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMSUBGRIDLOG)
        _value = cast(float, value)
        return _value

    @AXISYNUMSUBGRIDLOG.setter
    def AXISYNUMSUBGRIDLOG(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMSUBGRIDLOG, value)

    @property
    def axisynumsubgridlog(self) -> float:
        """AXISYNUMSUBGRIDLOG property
        
        Sub-grid # lines(Log.)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisynumsubgridlog' and 'AXISYNUMSUBGRIDLOG' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMSUBGRIDLOG)
        _value = cast(float, value)
        return _value

    @axisynumsubgridlog.setter
    def axisynumsubgridlog(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMSUBGRIDLOG, value)

    @property
    def AXISYVISIBLE(self) -> int:
        """AXISYVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYVISIBLE)
        _value = cast(int, value)
        return _value

    @AXISYVISIBLE.setter
    def AXISYVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYVISIBLE, value)

    @property
    def axisyvisible(self) -> int:
        """AXISYVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisyvisible' and 'AXISYVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYVISIBLE)
        _value = cast(int, value)
        return _value

    @axisyvisible.setter
    def axisyvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYVISIBLE, value)

    @property
    def AXISYAUTOSCALE(self) -> int:
        """AXISYAUTOSCALE property
        
        Auto scaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYAUTOSCALE)
        _value = cast(int, value)
        return _value

    @AXISYAUTOSCALE.setter
    def AXISYAUTOSCALE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYAUTOSCALE, value)

    @property
    def axisyautoscale(self) -> int:
        """AXISYAUTOSCALE property
        
        Auto scaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisyautoscale' and 'AXISYAUTOSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYAUTOSCALE)
        _value = cast(int, value)
        return _value

    @axisyautoscale.setter
    def axisyautoscale(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYAUTOSCALE, value)

    @property
    def AXISYORIGIN(self) -> float:
        """AXISYORIGIN property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYORIGIN)
        _value = cast(float, value)
        return _value

    @AXISYORIGIN.setter
    def AXISYORIGIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYORIGIN, value)

    @property
    def axisyorigin(self) -> float:
        """AXISYORIGIN property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'axisyorigin' and 'AXISYORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYORIGIN)
        _value = cast(float, value)
        return _value

    @axisyorigin.setter
    def axisyorigin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYORIGIN, value)

    @property
    def AXISYSIZE(self) -> float:
        """AXISYSIZE property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSIZE)
        _value = cast(float, value)
        return _value

    @AXISYSIZE.setter
    def AXISYSIZE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSIZE, value)

    @property
    def axisysize(self) -> float:
        """AXISYSIZE property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'axisysize' and 'AXISYSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSIZE)
        _value = cast(float, value)
        return _value

    @axisysize.setter
    def axisysize(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSIZE, value)

    @property
    def AXIS2TITLE(self) -> str:
        """AXIS2TITLE property
        
        Title text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2TITLE)
        _value = cast(str, value)
        return _value

    @AXIS2TITLE.setter
    def AXIS2TITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2TITLE, value)

    @property
    def axis2title(self) -> str:
        """AXIS2TITLE property
        
        Title text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axis2title' and 'AXIS2TITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2TITLE)
        _value = cast(str, value)
        return _value

    @axis2title.setter
    def axis2title(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2TITLE, value)

    @property
    def AXIS2TITLESIZE(self) -> int:
        """AXIS2TITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2TITLESIZE)
        _value = cast(int, value)
        return _value

    @AXIS2TITLESIZE.setter
    def AXIS2TITLESIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2TITLESIZE, value)

    @property
    def axis2titlesize(self) -> int:
        """AXIS2TITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axis2titlesize' and 'AXIS2TITLESIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2TITLESIZE)
        _value = cast(int, value)
        return _value

    @axis2titlesize.setter
    def axis2titlesize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2TITLESIZE, value)

    @property
    def AXIS2TITLERGB(self) -> List[float]:
        """AXIS2TITLERGB property
        
        Title color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2TITLERGB)
        _value = cast(List[float], value)
        return _value

    @AXIS2TITLERGB.setter
    def AXIS2TITLERGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2TITLERGB, value)

    @property
    def axis2titlergb(self) -> List[float]:
        """AXIS2TITLERGB property
        
        Title color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axis2titlergb' and 'AXIS2TITLERGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2TITLERGB)
        _value = cast(List[float], value)
        return _value

    @axis2titlergb.setter
    def axis2titlergb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2TITLERGB, value)

    @property
    def AXIS2LABELTYPE(self) -> int:
        """AXIS2LABELTYPE property
        
        Label type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELTYPE)
        _value = cast(int, value)
        return _value

    @AXIS2LABELTYPE.setter
    def AXIS2LABELTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELTYPE, value)

    @property
    def axis2labeltype(self) -> int:
        """AXIS2LABELTYPE property
        
        Label type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        Note: both 'axis2labeltype' and 'AXIS2LABELTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELTYPE)
        _value = cast(int, value)
        return _value

    @axis2labeltype.setter
    def axis2labeltype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELTYPE, value)

    @property
    def AXIS2LABELSIZE(self) -> int:
        """AXIS2LABELSIZE property
        
        Label size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELSIZE)
        _value = cast(int, value)
        return _value

    @AXIS2LABELSIZE.setter
    def AXIS2LABELSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELSIZE, value)

    @property
    def axis2labelsize(self) -> int:
        """AXIS2LABELSIZE property
        
        Label size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axis2labelsize' and 'AXIS2LABELSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELSIZE)
        _value = cast(int, value)
        return _value

    @axis2labelsize.setter
    def axis2labelsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELSIZE, value)

    @property
    def AXIS2LABELRGB(self) -> List[float]:
        """AXIS2LABELRGB property
        
        Label color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELRGB)
        _value = cast(List[float], value)
        return _value

    @AXIS2LABELRGB.setter
    def AXIS2LABELRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELRGB, value)

    @property
    def axis2labelrgb(self) -> List[float]:
        """AXIS2LABELRGB property
        
        Label color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axis2labelrgb' and 'AXIS2LABELRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELRGB)
        _value = cast(List[float], value)
        return _value

    @axis2labelrgb.setter
    def axis2labelrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELRGB, value)

    @property
    def AXIS2LABELFORMAT(self) -> str:
        """AXIS2LABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELFORMAT)
        _value = cast(str, value)
        return _value

    @AXIS2LABELFORMAT.setter
    def AXIS2LABELFORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELFORMAT, value)

    @property
    def axis2labelformat(self) -> str:
        """AXIS2LABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axis2labelformat' and 'AXIS2LABELFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2LABELFORMAT)
        _value = cast(str, value)
        return _value

    @axis2labelformat.setter
    def axis2labelformat(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2LABELFORMAT, value)

    @property
    def AXIS2VISIBLE(self) -> int:
        """AXIS2VISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2VISIBLE)
        _value = cast(int, value)
        return _value

    @AXIS2VISIBLE.setter
    def AXIS2VISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2VISIBLE, value)

    @property
    def axis2visible(self) -> int:
        """AXIS2VISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axis2visible' and 'AXIS2VISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2VISIBLE)
        _value = cast(int, value)
        return _value

    @axis2visible.setter
    def axis2visible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2VISIBLE, value)

    @property
    def AXIS2AUTOSCALE(self) -> int:
        """AXIS2AUTOSCALE property
        
        Auto scaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2AUTOSCALE)
        _value = cast(int, value)
        return _value

    @AXIS2AUTOSCALE.setter
    def AXIS2AUTOSCALE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2AUTOSCALE, value)

    @property
    def axis2autoscale(self) -> int:
        """AXIS2AUTOSCALE property
        
        Auto scaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axis2autoscale' and 'AXIS2AUTOSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2AUTOSCALE)
        _value = cast(int, value)
        return _value

    @axis2autoscale.setter
    def axis2autoscale(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2AUTOSCALE, value)

    @property
    def AXIS2MIN(self) -> float:
        """AXIS2MIN property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2MIN)
        _value = cast(float, value)
        return _value

    @AXIS2MIN.setter
    def AXIS2MIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2MIN, value)

    @property
    def axis2min(self) -> float:
        """AXIS2MIN property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axis2min' and 'AXIS2MIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2MIN)
        _value = cast(float, value)
        return _value

    @axis2min.setter
    def axis2min(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2MIN, value)

    @property
    def AXIS2MAX(self) -> float:
        """AXIS2MAX property
        
        Maximum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2MAX)
        _value = cast(float, value)
        return _value

    @AXIS2MAX.setter
    def AXIS2MAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2MAX, value)

    @property
    def axis2max(self) -> float:
        """AXIS2MAX property
        
        Maximum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axis2max' and 'AXIS2MAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS2MAX)
        _value = cast(float, value)
        return _value

    @axis2max.setter
    def axis2max(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS2MAX, value)

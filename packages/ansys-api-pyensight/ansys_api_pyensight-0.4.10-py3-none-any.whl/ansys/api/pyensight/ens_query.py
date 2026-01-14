"""ens_query module

The ens_query module provides a proxy interface to EnSight ENS_QUERY instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_QUERY(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_QUERY

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

    def addtoplot(self, *args, **kwargs) -> Any:
        """Add this query to plots

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.addtoplot({arg_string})"
        return self._session.cmd(cmd)

    def removefromplot(self, *args, **kwargs) -> Any:
        """Remove this query from some plots

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.removefromplot({arg_string})"
        return self._session.cmd(cmd)

    def attrgroupinfo(self, *args, **kwargs) -> Any:
        """Get information about GUI groups for this query's attributes

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
    def ID(self) -> int:
        """ID property
        
        ID
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ID)
        _value = cast(int, value)
        return _value

    @property
    def id(self) -> int:
        """ID property
        
        ID
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'id' and 'ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ID)
        _value = cast(int, value)
        return _value

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
    def PLOTS(self) -> ensobjlist['ENS_PLOTTER']:
        """PLOTS property
        
        visible plots
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTS)
        _value = cast(ensobjlist['ENS_PLOTTER'], value)
        return _value

    @property
    def plots(self) -> ensobjlist['ENS_PLOTTER']:
        """PLOTS property
        
        visible plots
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'plots' and 'PLOTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTS)
        _value = cast(ensobjlist['ENS_PLOTTER'], value)
        return _value

    @property
    def QUERY_DATA(self) -> Dict[Any, Any]:
        """QUERY_DATA property
        
        query data
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERY_DATA)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def query_data(self) -> Dict[Any, Any]:
        """QUERY_DATA property
        
        query data
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'query_data' and 'QUERY_DATA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERY_DATA)
        _value = cast(Dict[Any, Any], value)
        return _value

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
    def XAXIS_TYPE(self) -> int:
        """XAXIS_TYPE property
        
        form of the x axis
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_VARIABLE_DIST - distance
            * ensight.objs.enums.QRY_VARIABLE_TIME - time
            * ensight.objs.enums.QRY_VARIABLE_VAR - variable
            * ensight.objs.enums.QRY_VARIABLE_UNKNOWN - unknown
        
        """
        value = self.getattr(self._session.ensight.objs.enums.XAXIS_TYPE)
        _value = cast(int, value)
        return _value

    @property
    def xaxis_type(self) -> int:
        """XAXIS_TYPE property
        
        form of the x axis
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_VARIABLE_DIST - distance
            * ensight.objs.enums.QRY_VARIABLE_TIME - time
            * ensight.objs.enums.QRY_VARIABLE_VAR - variable
            * ensight.objs.enums.QRY_VARIABLE_UNKNOWN - unknown
        
        Note: both 'xaxis_type' and 'XAXIS_TYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.XAXIS_TYPE)
        _value = cast(int, value)
        return _value

    @property
    def CASES(self) -> ensobjlist['ENS_CASE']:
        """CASES property
        
        cases
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CASES)
        _value = cast(ensobjlist['ENS_CASE'], value)
        return _value

    @property
    def cases(self) -> ensobjlist['ENS_CASE']:
        """CASES property
        
        cases
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'cases' and 'CASES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CASES)
        _value = cast(ensobjlist['ENS_CASE'], value)
        return _value

    @property
    def PARTS(self) -> ensobjlist['ENS_PART']:
        """PARTS property
        
        parent parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def parts(self) -> ensobjlist['ENS_PART']:
        """PARTS property
        
        parent parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'parts' and 'PARTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        Description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
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
            String, 1024 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @description.setter
    def description(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DESCRIPTION, value)

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
    def OFFSET(self) -> List[float]:
        """OFFSET property
        
        Query offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OFFSET)
        _value = cast(List[float], value)
        return _value

    @OFFSET.setter
    def OFFSET(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OFFSET, value)

    @property
    def offset(self) -> List[float]:
        """OFFSET property
        
        Query offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'offset' and 'OFFSET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OFFSET)
        _value = cast(List[float], value)
        return _value

    @offset.setter
    def offset(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OFFSET, value)

    @property
    def SCALE(self) -> List[float]:
        """SCALE property
        
        Query scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(List[float], value)
        return _value

    @SCALE.setter
    def SCALE(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def scale(self) -> List[float]:
        """SCALE property
        
        Query scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'scale' and 'SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(List[float], value)
        return _value

    @scale.setter
    def scale(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def LINEWIDTH(self) -> int:
        """LINEWIDTH property
        
        Query width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(int, value)
        return _value

    @LINEWIDTH.setter
    def LINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def linewidth(self) -> int:
        """LINEWIDTH property
        
        Query width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'linewidth' and 'LINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(int, value)
        return _value

    @linewidth.setter
    def linewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def DISTANCE(self) -> int:
        """DISTANCE property
        
        Distance
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_DIST_X - x_arc_length
            * ensight.objs.enums.QRY_DIST_Y - y_arc_length
            * ensight.objs.enums.QRY_DIST_Z - z_arc_length
            * ensight.objs.enums.QRY_DIST_ALL - arc_length
            * ensight.objs.enums.QRY_DIST_X_ORIGIN - x_from_origin
            * ensight.objs.enums.QRY_DIST_Y_ORIGIN - y_from_origin
            * ensight.objs.enums.QRY_DIST_Z_ORIGIN - z_from_origin
            * ensight.objs.enums.QRY_DIST_ALL_ORIGIN - from_origin
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DISTANCE)
        _value = cast(int, value)
        return _value

    @DISTANCE.setter
    def DISTANCE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DISTANCE, value)

    @property
    def distance(self) -> int:
        """DISTANCE property
        
        Distance
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_DIST_X - x_arc_length
            * ensight.objs.enums.QRY_DIST_Y - y_arc_length
            * ensight.objs.enums.QRY_DIST_Z - z_arc_length
            * ensight.objs.enums.QRY_DIST_ALL - arc_length
            * ensight.objs.enums.QRY_DIST_X_ORIGIN - x_from_origin
            * ensight.objs.enums.QRY_DIST_Y_ORIGIN - y_from_origin
            * ensight.objs.enums.QRY_DIST_Z_ORIGIN - z_from_origin
            * ensight.objs.enums.QRY_DIST_ALL_ORIGIN - from_origin
        
        Note: both 'distance' and 'DISTANCE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DISTANCE)
        _value = cast(int, value)
        return _value

    @distance.setter
    def distance(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DISTANCE, value)

    @property
    def LINESTYLE(self) -> int:
        """LINESTYLE property
        
        Query line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINESTYLE)
        _value = cast(int, value)
        return _value

    @LINESTYLE.setter
    def LINESTYLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINESTYLE, value)

    @property
    def linestyle(self) -> int:
        """LINESTYLE property
        
        Query line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        Note: both 'linestyle' and 'LINESTYLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINESTYLE)
        _value = cast(int, value)
        return _value

    @linestyle.setter
    def linestyle(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINESTYLE, value)

    @property
    def SPLINEID(self) -> int:
        """SPLINEID property
        
        Spline id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPLINEID)
        _value = cast(int, value)
        return _value

    @SPLINEID.setter
    def SPLINEID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPLINEID, value)

    @property
    def splineid(self) -> int:
        """SPLINEID property
        
        Spline id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'splineid' and 'SPLINEID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPLINEID)
        _value = cast(int, value)
        return _value

    @splineid.setter
    def splineid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPLINEID, value)

    @property
    def ORIGIN(self) -> List[float]:
        """ORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN)
        _value = cast(List[float], value)
        return _value

    @ORIGIN.setter
    def ORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN, value)

    @property
    def origin(self) -> List[float]:
        """ORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'origin' and 'ORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN)
        _value = cast(List[float], value)
        return _value

    @origin.setter
    def origin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN, value)

    @property
    def NODEID(self) -> int:
        """NODEID property
        
        Node id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEID)
        _value = cast(int, value)
        return _value

    @NODEID.setter
    def NODEID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEID, value)

    @property
    def nodeid(self) -> int:
        """NODEID property
        
        Node id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'nodeid' and 'NODEID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEID)
        _value = cast(int, value)
        return _value

    @nodeid.setter
    def nodeid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEID, value)

    @property
    def PARTID(self) -> ensobjlist['ENS_PART']:
        """PARTID property
        
        Part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_PART Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTID)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @PARTID.setter
    def PARTID(self, value: ensobjlist['ENS_PART']) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTID, value)

    @property
    def partid(self) -> ensobjlist['ENS_PART']:
        """PARTID property
        
        Part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_PART Object, scalar
        
        Note: both 'partid' and 'PARTID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTID)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @partid.setter
    def partid(self, value: ensobjlist['ENS_PART']) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTID, value)

    @property
    def RGB(self) -> List[float]:
        """RGB property
        
        Query color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RGB)
        _value = cast(List[float], value)
        return _value

    @RGB.setter
    def RGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RGB, value)

    @property
    def rgb(self) -> List[float]:
        """RGB property
        
        Query color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'rgb' and 'RGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RGB)
        _value = cast(List[float], value)
        return _value

    @rgb.setter
    def rgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RGB, value)

    @property
    def LEGENDTITLE(self) -> str:
        """LEGENDTITLE property
        
        Legend title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDTITLE)
        _value = cast(str, value)
        return _value

    @LEGENDTITLE.setter
    def LEGENDTITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDTITLE, value)

    @property
    def legendtitle(self) -> str:
        """LEGENDTITLE property
        
        Legend title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'legendtitle' and 'LEGENDTITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDTITLE)
        _value = cast(str, value)
        return _value

    @legendtitle.setter
    def legendtitle(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDTITLE, value)

    @property
    def LINETYPE(self) -> int:
        """LINETYPE property
        
        Query line type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CURVE_LINE_NONE - none
            * ensight.objs.enums.CURVE_LINE_CONNECT - connect_dots
            * ensight.objs.enums.CURVE_LINE_SMOOTH - smooth
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINETYPE)
        _value = cast(int, value)
        return _value

    @LINETYPE.setter
    def LINETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINETYPE, value)

    @property
    def linetype(self) -> int:
        """LINETYPE property
        
        Query line type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CURVE_LINE_NONE - none
            * ensight.objs.enums.CURVE_LINE_CONNECT - connect_dots
            * ensight.objs.enums.CURVE_LINE_SMOOTH - smooth
        
        Note: both 'linetype' and 'LINETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINETYPE)
        _value = cast(int, value)
        return _value

    @linetype.setter
    def linetype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINETYPE, value)

    @property
    def SMOOTHSUBPOINTS(self) -> float:
        """SMOOTHSUBPOINTS property
        
           Smooth sub-points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SMOOTHSUBPOINTS)
        _value = cast(float, value)
        return _value

    @SMOOTHSUBPOINTS.setter
    def SMOOTHSUBPOINTS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SMOOTHSUBPOINTS, value)

    @property
    def smoothsubpoints(self) -> float:
        """SMOOTHSUBPOINTS property
        
           Smooth sub-points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'smoothsubpoints' and 'SMOOTHSUBPOINTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SMOOTHSUBPOINTS)
        _value = cast(float, value)
        return _value

    @smoothsubpoints.setter
    def smoothsubpoints(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SMOOTHSUBPOINTS, value)

    @property
    def MARKER(self) -> int:
        """MARKER property
        
        Marker type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CURVE_MARKER_NONE - none
            * ensight.objs.enums.CURVE_MARKER_DOT - dot
            * ensight.objs.enums.CURVE_MARKER_CIRCLE - circle
            * ensight.objs.enums.CURVE_MARKER_TRIANGLE - triangle
            * ensight.objs.enums.CURVE_MARKER_SQUARE - square
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKER)
        _value = cast(int, value)
        return _value

    @MARKER.setter
    def MARKER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKER, value)

    @property
    def marker(self) -> int:
        """MARKER property
        
        Marker type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CURVE_MARKER_NONE - none
            * ensight.objs.enums.CURVE_MARKER_DOT - dot
            * ensight.objs.enums.CURVE_MARKER_CIRCLE - circle
            * ensight.objs.enums.CURVE_MARKER_TRIANGLE - triangle
            * ensight.objs.enums.CURVE_MARKER_SQUARE - square
        
        Note: both 'marker' and 'MARKER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKER)
        _value = cast(int, value)
        return _value

    @marker.setter
    def marker(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKER, value)

    @property
    def MARKERSCALE(self) -> float:
        """MARKERSCALE property
        
        Marker scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERSCALE)
        _value = cast(float, value)
        return _value

    @MARKERSCALE.setter
    def MARKERSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERSCALE, value)

    @property
    def markerscale(self) -> float:
        """MARKERSCALE property
        
        Marker scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'markerscale' and 'MARKERSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERSCALE)
        _value = cast(float, value)
        return _value

    @markerscale.setter
    def markerscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERSCALE, value)

    @property
    def NORMALIZEX(self) -> int:
        """NORMALIZEX property
        
        Normalize X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NORMALIZEX)
        _value = cast(int, value)
        return _value

    @NORMALIZEX.setter
    def NORMALIZEX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NORMALIZEX, value)

    @property
    def normalizex(self) -> int:
        """NORMALIZEX property
        
        Normalize X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'normalizex' and 'NORMALIZEX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NORMALIZEX)
        _value = cast(int, value)
        return _value

    @normalizex.setter
    def normalizex(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NORMALIZEX, value)

    @property
    def NORMALIZEY(self) -> int:
        """NORMALIZEY property
        
        Normalize Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NORMALIZEY)
        _value = cast(int, value)
        return _value

    @NORMALIZEY.setter
    def NORMALIZEY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NORMALIZEY, value)

    @property
    def normalizey(self) -> int:
        """NORMALIZEY property
        
        Normalize Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'normalizey' and 'NORMALIZEY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NORMALIZEY)
        _value = cast(int, value)
        return _value

    @normalizey.setter
    def normalizey(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NORMALIZEY, value)

    @property
    def ASSIGNTOYAXIS(self) -> int:
        """ASSIGNTOYAXIS property
        
        Assign to y axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_ASSIGN_TO_Y_AXIS_AUTO - auto
            * ensight.objs.enums.QRY_ASSIGN_TO_Y_LEFT - left
            * ensight.objs.enums.QRY_ASSIGN_TO_Y_RIGHT - right
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ASSIGNTOYAXIS)
        _value = cast(int, value)
        return _value

    @ASSIGNTOYAXIS.setter
    def ASSIGNTOYAXIS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ASSIGNTOYAXIS, value)

    @property
    def assigntoyaxis(self) -> int:
        """ASSIGNTOYAXIS property
        
        Assign to y axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_ASSIGN_TO_Y_AXIS_AUTO - auto
            * ensight.objs.enums.QRY_ASSIGN_TO_Y_LEFT - left
            * ensight.objs.enums.QRY_ASSIGN_TO_Y_RIGHT - right
        
        Note: both 'assigntoyaxis' and 'ASSIGNTOYAXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ASSIGNTOYAXIS)
        _value = cast(int, value)
        return _value

    @assigntoyaxis.setter
    def assigntoyaxis(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ASSIGNTOYAXIS, value)

    @property
    def MARKERVISIBLE(self) -> int:
        """MARKERVISIBLE property
        
        Marker visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERVISIBLE)
        _value = cast(int, value)
        return _value

    @MARKERVISIBLE.setter
    def MARKERVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERVISIBLE, value)

    @property
    def markervisible(self) -> int:
        """MARKERVISIBLE property
        
        Marker visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'markervisible' and 'MARKERVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERVISIBLE)
        _value = cast(int, value)
        return _value

    @markervisible.setter
    def markervisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERVISIBLE, value)

    @property
    def MARKERRGB(self) -> List[float]:
        """MARKERRGB property
        
        Marker color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERRGB)
        _value = cast(List[float], value)
        return _value

    @MARKERRGB.setter
    def MARKERRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERRGB, value)

    @property
    def markerrgb(self) -> List[float]:
        """MARKERRGB property
        
        Marker color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'markerrgb' and 'MARKERRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERRGB)
        _value = cast(List[float], value)
        return _value

    @markerrgb.setter
    def markerrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERRGB, value)

    @property
    def MARKERSIZENORMALIZED(self) -> float:
        """MARKERSIZENORMALIZED property
        
        Marker size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERSIZENORMALIZED)
        _value = cast(float, value)
        return _value

    @MARKERSIZENORMALIZED.setter
    def MARKERSIZENORMALIZED(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERSIZENORMALIZED, value)

    @property
    def markersizenormalized(self) -> float:
        """MARKERSIZENORMALIZED property
        
        Marker size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'markersizenormalized' and 'MARKERSIZENORMALIZED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERSIZENORMALIZED)
        _value = cast(float, value)
        return _value

    @markersizenormalized.setter
    def markersizenormalized(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERSIZENORMALIZED, value)

    @property
    def VARIABLE1(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE1 property
        
        Variable 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Constant
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE1)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @VARIABLE1.setter
    def VARIABLE1(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE1, value)

    @property
    def variable1(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE1 property
        
        Variable 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Constant
            * Nodal
            * Element
        
        Note: both 'variable1' and 'VARIABLE1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE1)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @variable1.setter
    def variable1(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE1, value)

    @property
    def VARIABLE2(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE2 property
        
        Variable 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Constant
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE2)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @VARIABLE2.setter
    def VARIABLE2(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE2, value)

    @property
    def variable2(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE2 property
        
        Variable 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Constant
            * Nodal
            * Element
        
        Note: both 'variable2' and 'VARIABLE2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE2)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @variable2.setter
    def variable2(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE2, value)

    @property
    def BEGINSIMTIME(self) -> float:
        """BEGINSIMTIME property
        
        Begin simtime
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BEGINSIMTIME)
        _value = cast(float, value)
        return _value

    @BEGINSIMTIME.setter
    def BEGINSIMTIME(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BEGINSIMTIME, value)

    @property
    def beginsimtime(self) -> float:
        """BEGINSIMTIME property
        
        Begin simtime
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'beginsimtime' and 'BEGINSIMTIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BEGINSIMTIME)
        _value = cast(float, value)
        return _value

    @beginsimtime.setter
    def beginsimtime(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BEGINSIMTIME, value)

    @property
    def ENDSIMTIME(self) -> float:
        """ENDSIMTIME property
        
        End simtime
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENDSIMTIME)
        _value = cast(float, value)
        return _value

    @ENDSIMTIME.setter
    def ENDSIMTIME(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ENDSIMTIME, value)

    @property
    def endsimtime(self) -> float:
        """ENDSIMTIME property
        
        End simtime
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'endsimtime' and 'ENDSIMTIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENDSIMTIME)
        _value = cast(float, value)
        return _value

    @endsimtime.setter
    def endsimtime(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ENDSIMTIME, value)

    @property
    def SAMPLEBY(self) -> int:
        """SAMPLEBY property
        
        Sample by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_VALUE - value
            * ensight.objs.enums.QRY_FFT - fft
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEBY)
        _value = cast(int, value)
        return _value

    @SAMPLEBY.setter
    def SAMPLEBY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEBY, value)

    @property
    def sampleby(self) -> int:
        """SAMPLEBY property
        
        Sample by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_VALUE - value
            * ensight.objs.enums.QRY_FFT - fft
        
        Note: both 'sampleby' and 'SAMPLEBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEBY)
        _value = cast(int, value)
        return _value

    @sampleby.setter
    def sampleby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEBY, value)

    @property
    def NUMOFSAMPLEPTS(self) -> int:
        """NUMOFSAMPLEPTS property
        
        Samples
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMOFSAMPLEPTS)
        _value = cast(int, value)
        return _value

    @NUMOFSAMPLEPTS.setter
    def NUMOFSAMPLEPTS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NUMOFSAMPLEPTS, value)

    @property
    def numofsamplepts(self) -> int:
        """NUMOFSAMPLEPTS property
        
        Samples
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, inf]
        
        Note: both 'numofsamplepts' and 'NUMOFSAMPLEPTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMOFSAMPLEPTS)
        _value = cast(int, value)
        return _value

    @numofsamplepts.setter
    def numofsamplepts(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NUMOFSAMPLEPTS, value)

    @property
    def MULTIPLESEGMENTSBY(self) -> int:
        """MULTIPLESEGMENTSBY property
        
        Multiple segments by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_MSEG_ACCUMU - accumulation
            * ensight.objs.enums.QRY_MSEG_RESET - reset_each
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MULTIPLESEGMENTSBY)
        _value = cast(int, value)
        return _value

    @MULTIPLESEGMENTSBY.setter
    def MULTIPLESEGMENTSBY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MULTIPLESEGMENTSBY, value)

    @property
    def multiplesegmentsby(self) -> int:
        """MULTIPLESEGMENTSBY property
        
        Multiple segments by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_MSEG_ACCUMU - accumulation
            * ensight.objs.enums.QRY_MSEG_RESET - reset_each
        
        Note: both 'multiplesegmentsby' and 'MULTIPLESEGMENTSBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MULTIPLESEGMENTSBY)
        _value = cast(int, value)
        return _value

    @multiplesegmentsby.setter
    def multiplesegmentsby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MULTIPLESEGMENTSBY, value)

    @property
    def QUERYLINETOOLPOINT1(self) -> List[float]:
        """QUERYLINETOOLPOINT1 property
        
        Endpoint1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT1)
        _value = cast(List[float], value)
        return _value

    @QUERYLINETOOLPOINT1.setter
    def QUERYLINETOOLPOINT1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT1, value)

    @property
    def querylinetoolpoint1(self) -> List[float]:
        """QUERYLINETOOLPOINT1 property
        
        Endpoint1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'querylinetoolpoint1' and 'QUERYLINETOOLPOINT1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT1)
        _value = cast(List[float], value)
        return _value

    @querylinetoolpoint1.setter
    def querylinetoolpoint1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT1, value)

    @property
    def QUERYLINETOOLPOINT2(self) -> List[float]:
        """QUERYLINETOOLPOINT2 property
        
        Endpoint2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT2)
        _value = cast(List[float], value)
        return _value

    @QUERYLINETOOLPOINT2.setter
    def QUERYLINETOOLPOINT2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT2, value)

    @property
    def querylinetoolpoint2(self) -> List[float]:
        """QUERYLINETOOLPOINT2 property
        
        Endpoint2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'querylinetoolpoint2' and 'QUERYLINETOOLPOINT2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT2)
        _value = cast(List[float], value)
        return _value

    @querylinetoolpoint2.setter
    def querylinetoolpoint2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERYLINETOOLPOINT2, value)

    @property
    def PARTMINVALUE(self) -> float:
        """PARTMINVALUE property
        
        Part min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTMINVALUE)
        _value = cast(float, value)
        return _value

    @PARTMINVALUE.setter
    def PARTMINVALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTMINVALUE, value)

    @property
    def partminvalue(self) -> float:
        """PARTMINVALUE property
        
        Part min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'partminvalue' and 'PARTMINVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTMINVALUE)
        _value = cast(float, value)
        return _value

    @partminvalue.setter
    def partminvalue(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTMINVALUE, value)

    @property
    def PARTMAXVALUE(self) -> float:
        """PARTMAXVALUE property
        
        Part max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTMAXVALUE)
        _value = cast(float, value)
        return _value

    @PARTMAXVALUE.setter
    def PARTMAXVALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTMAXVALUE, value)

    @property
    def partmaxvalue(self) -> float:
        """PARTMAXVALUE property
        
        Part max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'partmaxvalue' and 'PARTMAXVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTMAXVALUE)
        _value = cast(float, value)
        return _value

    @partmaxvalue.setter
    def partmaxvalue(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTMAXVALUE, value)

    @property
    def PARTDELTAVALUE(self) -> float:
        """PARTDELTAVALUE property
        
        Part delta value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTDELTAVALUE)
        _value = cast(float, value)
        return _value

    @PARTDELTAVALUE.setter
    def PARTDELTAVALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTDELTAVALUE, value)

    @property
    def partdeltavalue(self) -> float:
        """PARTDELTAVALUE property
        
        Part delta value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'partdeltavalue' and 'PARTDELTAVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTDELTAVALUE)
        _value = cast(float, value)
        return _value

    @partdeltavalue.setter
    def partdeltavalue(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTDELTAVALUE, value)

    @property
    def IJK(self) -> List[int]:
        """IJK property
        
        Ijk
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        Range:
            [1, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.IJK)
        _value = cast(List[int], value)
        return _value

    @IJK.setter
    def IJK(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.IJK, value)

    @property
    def ijk(self) -> List[int]:
        """IJK property
        
        Ijk
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        Range:
            [1, inf]
        
        Note: both 'ijk' and 'IJK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.IJK)
        _value = cast(List[int], value)
        return _value

    @ijk.setter
    def ijk(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.IJK, value)

    @property
    def ELEMID(self) -> int:
        """ELEMID property
        
        Elem id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ELEMID)
        _value = cast(int, value)
        return _value

    @ELEMID.setter
    def ELEMID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELEMID, value)

    @property
    def elemid(self) -> int:
        """ELEMID property
        
        Elem id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, inf]
        
        Note: both 'elemid' and 'ELEMID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ELEMID)
        _value = cast(int, value)
        return _value

    @elemid.setter
    def elemid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELEMID, value)

    @property
    def CURSORLOC(self) -> List[float]:
        """CURSORLOC property
        
        XYZ location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CURSORLOC)
        _value = cast(List[float], value)
        return _value

    @CURSORLOC.setter
    def CURSORLOC(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CURSORLOC, value)

    @property
    def cursorloc(self) -> List[float]:
        """CURSORLOC property
        
        XYZ location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'cursorloc' and 'CURSORLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CURSORLOC)
        _value = cast(List[float], value)
        return _value

    @cursorloc.setter
    def cursorloc(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CURSORLOC, value)

    @property
    def SCALARVARIABLE(self) -> ensobjlist['ENS_VAR']:
        """SCALARVARIABLE property
        
        Scalar variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALARVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @SCALARVARIABLE.setter
    def SCALARVARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALARVARIABLE, value)

    @property
    def scalarvariable(self) -> ensobjlist['ENS_VAR']:
        """SCALARVARIABLE property
        
        Scalar variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'scalarvariable' and 'SCALARVARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALARVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @scalarvariable.setter
    def scalarvariable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALARVARIABLE, value)

    @property
    def SCALARVALUE(self) -> int:
        """SCALARVALUE property
        
        Scalar value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALARVALUE)
        _value = cast(int, value)
        return _value

    @SCALARVALUE.setter
    def SCALARVALUE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALARVALUE, value)

    @property
    def scalarvalue(self) -> int:
        """SCALARVALUE property
        
        Scalar value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'scalarvalue' and 'SCALARVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALARVALUE)
        _value = cast(int, value)
        return _value

    @scalarvalue.setter
    def scalarvalue(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALARVALUE, value)

    @property
    def OPERATIONFACTOR1(self) -> float:
        """OPERATIONFACTOR1 property
        
        Operation factor1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONFACTOR1)
        _value = cast(float, value)
        return _value

    @OPERATIONFACTOR1.setter
    def OPERATIONFACTOR1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONFACTOR1, value)

    @property
    def operationfactor1(self) -> float:
        """OPERATIONFACTOR1 property
        
        Operation factor1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'operationfactor1' and 'OPERATIONFACTOR1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONFACTOR1)
        _value = cast(float, value)
        return _value

    @operationfactor1.setter
    def operationfactor1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONFACTOR1, value)

    @property
    def OPERATIONFACTOR2(self) -> float:
        """OPERATIONFACTOR2 property
        
        Operation factor2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONFACTOR2)
        _value = cast(float, value)
        return _value

    @OPERATIONFACTOR2.setter
    def OPERATIONFACTOR2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONFACTOR2, value)

    @property
    def operationfactor2(self) -> float:
        """OPERATIONFACTOR2 property
        
        Operation factor2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'operationfactor2' and 'OPERATIONFACTOR2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONFACTOR2)
        _value = cast(float, value)
        return _value

    @operationfactor2.setter
    def operationfactor2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONFACTOR2, value)

    @property
    def OPERATIONQUERY1BYNAME(self) -> int:
        """OPERATIONQUERY1BYNAME property
        
        Operation query1byname
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONQUERY1BYNAME)
        _value = cast(int, value)
        return _value

    @OPERATIONQUERY1BYNAME.setter
    def OPERATIONQUERY1BYNAME(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONQUERY1BYNAME, value)

    @property
    def operationquery1byname(self) -> int:
        """OPERATIONQUERY1BYNAME property
        
        Operation query1byname
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'operationquery1byname' and 'OPERATIONQUERY1BYNAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONQUERY1BYNAME)
        _value = cast(int, value)
        return _value

    @operationquery1byname.setter
    def operationquery1byname(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONQUERY1BYNAME, value)

    @property
    def OPERATIONQUERY2BYNAME(self) -> int:
        """OPERATIONQUERY2BYNAME property
        
        Operation query2byname
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONQUERY2BYNAME)
        _value = cast(int, value)
        return _value

    @OPERATIONQUERY2BYNAME.setter
    def OPERATIONQUERY2BYNAME(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONQUERY2BYNAME, value)

    @property
    def operationquery2byname(self) -> int:
        """OPERATIONQUERY2BYNAME property
        
        Operation query2byname
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'operationquery2byname' and 'OPERATIONQUERY2BYNAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATIONQUERY2BYNAME)
        _value = cast(int, value)
        return _value

    @operationquery2byname.setter
    def operationquery2byname(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATIONQUERY2BYNAME, value)

    @property
    def OPERATION(self) -> int:
        """OPERATION property
        
        Operation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QY_CMB - combine
            * ensight.objs.enums.QY_DIF - differentiate
            * ensight.objs.enums.QY_INT - integrate
            * ensight.objs.enums.QY_DIV - divide
            * ensight.objs.enums.QY_MLT - multiply
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATION)
        _value = cast(int, value)
        return _value

    @OPERATION.setter
    def OPERATION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATION, value)

    @property
    def operation(self) -> int:
        """OPERATION property
        
        Operation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QY_CMB - combine
            * ensight.objs.enums.QY_DIF - differentiate
            * ensight.objs.enums.QY_INT - integrate
            * ensight.objs.enums.QY_DIV - divide
            * ensight.objs.enums.QY_MLT - multiply
        
        Note: both 'operation' and 'OPERATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OPERATION)
        _value = cast(int, value)
        return _value

    @operation.setter
    def operation(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OPERATION, value)

    @property
    def QUERYTYPE(self) -> int:
        """QUERYTYPE property
        
        Query type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_GENERATED - generated
            * ensight.objs.enums.QRY_OPERATE - operation
            * ensight.objs.enums.QRY_EXTERNAL - external
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERYTYPE)
        _value = cast(int, value)
        return _value

    @QUERYTYPE.setter
    def QUERYTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERYTYPE, value)

    @property
    def querytype(self) -> int:
        """QUERYTYPE property
        
        Query type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_GENERATED - generated
            * ensight.objs.enums.QRY_OPERATE - operation
            * ensight.objs.enums.QRY_EXTERNAL - external
        
        Note: both 'querytype' and 'QUERYTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERYTYPE)
        _value = cast(int, value)
        return _value

    @querytype.setter
    def querytype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERYTYPE, value)

    @property
    def GENERATEOVER(self) -> int:
        """GENERATEOVER property
        
        Generate over
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_SCATTER_GEN_OVER_DISTANCE - distance
            * ensight.objs.enums.QRY_SCATTER_GEN_OVER_TIME - time
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GENERATEOVER)
        _value = cast(int, value)
        return _value

    @GENERATEOVER.setter
    def GENERATEOVER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GENERATEOVER, value)

    @property
    def generateover(self) -> int:
        """GENERATEOVER property
        
        Generate over
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_SCATTER_GEN_OVER_DISTANCE - distance
            * ensight.objs.enums.QRY_SCATTER_GEN_OVER_TIME - time
        
        Note: both 'generateover' and 'GENERATEOVER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GENERATEOVER)
        _value = cast(int, value)
        return _value

    @generateover.setter
    def generateover(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GENERATEOVER, value)

    @property
    def CONSTRAINDISTANCE(self) -> int:
        """CONSTRAINDISTANCE property
        
        Constrain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_CONS_MIN_VALUE - min
            * ensight.objs.enums.QRY_CONS_MAX_VALUE - max
            * ensight.objs.enums.QRY_CONS_IJK - ijk
            * ensight.objs.enums.QRY_CONS_POINT - cursor
            * ensight.objs.enums.QRY_CONS_NODE - node
            * ensight.objs.enums.QRY_CONS_ELEM - element
            * ensight.objs.enums.QRY_CONS_LINE_TOOL - line_tool
            * ensight.objs.enums.QRY_CONS_PART - 1d_part
            * ensight.objs.enums.QRY_CONS_SCALAR - scalar
            * ensight.objs.enums.QRY_PART_VS_CONSTANT - by_constant_on_part
            * ensight.objs.enums.QRY_CONS_SPLINE - spline
            * ensight.objs.enums.QRY_CONS_NO - no
            * ensight.objs.enums.QRY_CONS_BY_POINT - by_point
            * ensight.objs.enums.QRY_CONS_BY_NODE - by_node
            * ensight.objs.enums.QRY_CONS_BY_PART - by_part
            * ensight.objs.enums.QRY_CONS_SCATTER_ON_PART - by_part_elem_rep
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTRAINDISTANCE)
        _value = cast(int, value)
        return _value

    @CONSTRAINDISTANCE.setter
    def CONSTRAINDISTANCE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CONSTRAINDISTANCE, value)

    @property
    def constraindistance(self) -> int:
        """CONSTRAINDISTANCE property
        
        Constrain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_CONS_MIN_VALUE - min
            * ensight.objs.enums.QRY_CONS_MAX_VALUE - max
            * ensight.objs.enums.QRY_CONS_IJK - ijk
            * ensight.objs.enums.QRY_CONS_POINT - cursor
            * ensight.objs.enums.QRY_CONS_NODE - node
            * ensight.objs.enums.QRY_CONS_ELEM - element
            * ensight.objs.enums.QRY_CONS_LINE_TOOL - line_tool
            * ensight.objs.enums.QRY_CONS_PART - 1d_part
            * ensight.objs.enums.QRY_CONS_SCALAR - scalar
            * ensight.objs.enums.QRY_PART_VS_CONSTANT - by_constant_on_part
            * ensight.objs.enums.QRY_CONS_SPLINE - spline
            * ensight.objs.enums.QRY_CONS_NO - no
            * ensight.objs.enums.QRY_CONS_BY_POINT - by_point
            * ensight.objs.enums.QRY_CONS_BY_NODE - by_node
            * ensight.objs.enums.QRY_CONS_BY_PART - by_part
            * ensight.objs.enums.QRY_CONS_SCATTER_ON_PART - by_part_elem_rep
        
        Note: both 'constraindistance' and 'CONSTRAINDISTANCE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTRAINDISTANCE)
        _value = cast(int, value)
        return _value

    @constraindistance.setter
    def constraindistance(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CONSTRAINDISTANCE, value)

    @property
    def CONSTRAINTIME(self) -> int:
        """CONSTRAINTIME property
        
        Constrain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_CONS_MIN_VALUE - min
            * ensight.objs.enums.QRY_CONS_MAX_VALUE - max
            * ensight.objs.enums.QRY_CONS_IJK - ijk
            * ensight.objs.enums.QRY_CONS_POINT - cursor
            * ensight.objs.enums.QRY_CONS_NODE - node
            * ensight.objs.enums.QRY_CONS_ELEM - element
            * ensight.objs.enums.QRY_CONS_LINE_TOOL - line_tool
            * ensight.objs.enums.QRY_CONS_PART - 1d_part
            * ensight.objs.enums.QRY_CONS_SCALAR - scalar
            * ensight.objs.enums.QRY_PART_VS_CONSTANT - by_constant_on_part
            * ensight.objs.enums.QRY_CONS_SPLINE - spline
            * ensight.objs.enums.QRY_CONS_NO - no
            * ensight.objs.enums.QRY_CONS_BY_POINT - by_point
            * ensight.objs.enums.QRY_CONS_BY_NODE - by_node
            * ensight.objs.enums.QRY_CONS_BY_PART - by_part
            * ensight.objs.enums.QRY_CONS_SCATTER_ON_PART - by_part_elem_rep
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTRAINTIME)
        _value = cast(int, value)
        return _value

    @CONSTRAINTIME.setter
    def CONSTRAINTIME(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CONSTRAINTIME, value)

    @property
    def constraintime(self) -> int:
        """CONSTRAINTIME property
        
        Constrain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.QRY_CONS_MIN_VALUE - min
            * ensight.objs.enums.QRY_CONS_MAX_VALUE - max
            * ensight.objs.enums.QRY_CONS_IJK - ijk
            * ensight.objs.enums.QRY_CONS_POINT - cursor
            * ensight.objs.enums.QRY_CONS_NODE - node
            * ensight.objs.enums.QRY_CONS_ELEM - element
            * ensight.objs.enums.QRY_CONS_LINE_TOOL - line_tool
            * ensight.objs.enums.QRY_CONS_PART - 1d_part
            * ensight.objs.enums.QRY_CONS_SCALAR - scalar
            * ensight.objs.enums.QRY_PART_VS_CONSTANT - by_constant_on_part
            * ensight.objs.enums.QRY_CONS_SPLINE - spline
            * ensight.objs.enums.QRY_CONS_NO - no
            * ensight.objs.enums.QRY_CONS_BY_POINT - by_point
            * ensight.objs.enums.QRY_CONS_BY_NODE - by_node
            * ensight.objs.enums.QRY_CONS_BY_PART - by_part
            * ensight.objs.enums.QRY_CONS_SCATTER_ON_PART - by_part_elem_rep
        
        Note: both 'constraintime' and 'CONSTRAINTIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTRAINTIME)
        _value = cast(int, value)
        return _value

    @constraintime.setter
    def constraintime(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CONSTRAINTIME, value)

    @property
    def UPDATEWITHNEWTIMESTEPS(self) -> int:
        """UPDATEWITHNEWTIMESTEPS property
        
        Update with newtimesteps
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.UPDATEWITHNEWTIMESTEPS)
        _value = cast(int, value)
        return _value

    @UPDATEWITHNEWTIMESTEPS.setter
    def UPDATEWITHNEWTIMESTEPS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.UPDATEWITHNEWTIMESTEPS, value)

    @property
    def updatewithnewtimesteps(self) -> int:
        """UPDATEWITHNEWTIMESTEPS property
        
        Update with newtimesteps
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'updatewithnewtimesteps' and 'UPDATEWITHNEWTIMESTEPS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.UPDATEWITHNEWTIMESTEPS)
        _value = cast(int, value)
        return _value

    @updatewithnewtimesteps.setter
    def updatewithnewtimesteps(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.UPDATEWITHNEWTIMESTEPS, value)

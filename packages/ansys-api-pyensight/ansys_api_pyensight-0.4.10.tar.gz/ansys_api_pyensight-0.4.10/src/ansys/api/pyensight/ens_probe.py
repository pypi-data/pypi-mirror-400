"""ens_probe module

The ens_probe module provides a proxy interface to EnSight ENS_PROBE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_PROBE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_PROBE

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

    def remove(self, *args, **kwargs) -> Any:
        """Remove one probe

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.remove({arg_string})"
        return self._session.cmd(cmd)

    def surface_pick(self, *args, **kwargs) -> Any:
        """Pick at given mouse position

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.surface_pick({arg_string})"
        return self._session.cmd(cmd)

    def attrgroupinfo(self, *args, **kwargs) -> Any:
        """Get information about GUI groups for this probe's attributes

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
    def VARIABLES(self) -> List[dict]:
        """VARIABLES property
        
        variables
        
        Supported operations:
            getattr, setattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLES)
        _value = cast(List[dict], value)
        return _value

    @VARIABLES.setter
    def VARIABLES(self, value: List[dict]) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLES, value)

    @property
    def variables(self) -> List[dict]:
        """VARIABLES property
        
        variables
        
        Supported operations:
            getattr, setattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'variables' and 'VARIABLES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLES)
        _value = cast(List[dict], value)
        return _value

    @variables.setter
    def variables(self, value: List[dict]) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLES, value)

    @property
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
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
        
        description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @description.setter
    def description(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DESCRIPTION, value)

    @property
    def PROBE_DATA(self) -> List[dict]:
        """PROBE_DATA property
        
        probe data
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PROBE_DATA)
        _value = cast(List[dict], value)
        return _value

    @property
    def probe_data(self) -> List[dict]:
        """PROBE_DATA property
        
        probe data
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'probe_data' and 'PROBE_DATA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PROBE_DATA)
        _value = cast(List[dict], value)
        return _value

    @property
    def LABELVISIBLE(self) -> int:
        """LABELVISIBLE property
        
        Label Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELVISIBLE)
        _value = cast(int, value)
        return _value

    @LABELVISIBLE.setter
    def LABELVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELVISIBLE, value)

    @property
    def labelvisible(self) -> int:
        """LABELVISIBLE property
        
        Label Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'labelvisible' and 'LABELVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELVISIBLE)
        _value = cast(int, value)
        return _value

    @labelvisible.setter
    def labelvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELVISIBLE, value)

    @property
    def LABELRGB(self) -> List[float]:
        """LABELRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELRGB)
        _value = cast(List[float], value)
        return _value

    @LABELRGB.setter
    def LABELRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELRGB, value)

    @property
    def labelrgb(self) -> List[float]:
        """LABELRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        Note: both 'labelrgb' and 'LABELRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELRGB)
        _value = cast(List[float], value)
        return _value

    @labelrgb.setter
    def labelrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELRGB, value)

    @property
    def LABELFORMAT(self) -> int:
        """LABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.F_FORMAT - floating_point
            * ensight.objs.enums.E_FORMAT - exponential
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELFORMAT)
        _value = cast(int, value)
        return _value

    @LABELFORMAT.setter
    def LABELFORMAT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELFORMAT, value)

    @property
    def labelformat(self) -> int:
        """LABELFORMAT property
        
        Label format
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.F_FORMAT - floating_point
            * ensight.objs.enums.E_FORMAT - exponential
        
        Note: both 'labelformat' and 'LABELFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELFORMAT)
        _value = cast(int, value)
        return _value

    @labelformat.setter
    def labelformat(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELFORMAT, value)

    @property
    def LABELDECIMALPLACES(self) -> int:
        """LABELDECIMALPLACES property
        
        Label decimal places
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 6]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELDECIMALPLACES)
        _value = cast(int, value)
        return _value

    @LABELDECIMALPLACES.setter
    def LABELDECIMALPLACES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELDECIMALPLACES, value)

    @property
    def labeldecimalplaces(self) -> int:
        """LABELDECIMALPLACES property
        
        Label decimal places
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 6]
        
        Note: both 'labeldecimalplaces' and 'LABELDECIMALPLACES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELDECIMALPLACES)
        _value = cast(int, value)
        return _value

    @labeldecimalplaces.setter
    def labeldecimalplaces(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELDECIMALPLACES, value)

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
        
        Marker normalize
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
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
        
        Marker normalize
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'markersizenormalized' and 'MARKERSIZENORMALIZED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKERSIZENORMALIZED)
        _value = cast(float, value)
        return _value

    @markersizenormalized.setter
    def markersizenormalized(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKERSIZENORMALIZED, value)

    @property
    def QUERY(self) -> int:
        """QUERY property
        
        Action
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.INT_QUERY_SURFACE - surface
            * ensight.objs.enums.INT_QUERY_POINT - cursor
            * ensight.objs.enums.INT_QUERY_NODEID - node
            * ensight.objs.enums.INT_QUERY_IJK - ijk
            * ensight.objs.enums.INT_QUERY_ELEMID - element
            * ensight.objs.enums.INT_QUERY_XYZ - xyz
            * ensight.objs.enums.INT_QUERY_MIN - min
            * ensight.objs.enums.INT_QUERY_MAX - max
            * ensight.objs.enums.INT_QUERY_NONE - none
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERY)
        _value = cast(int, value)
        return _value

    @QUERY.setter
    def QUERY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERY, value)

    @property
    def query(self) -> int:
        """QUERY property
        
        Action
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.INT_QUERY_SURFACE - surface
            * ensight.objs.enums.INT_QUERY_POINT - cursor
            * ensight.objs.enums.INT_QUERY_NODEID - node
            * ensight.objs.enums.INT_QUERY_IJK - ijk
            * ensight.objs.enums.INT_QUERY_ELEMID - element
            * ensight.objs.enums.INT_QUERY_XYZ - xyz
            * ensight.objs.enums.INT_QUERY_MIN - min
            * ensight.objs.enums.INT_QUERY_MAX - max
            * ensight.objs.enums.INT_QUERY_NONE - none
        
        Note: both 'query' and 'QUERY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERY)
        _value = cast(int, value)
        return _value

    @query.setter
    def query(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.QUERY, value)

    @property
    def SEARCH(self) -> int:
        """SEARCH property
        
        Search
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.INT_QUERY_EXACT - exact
            * ensight.objs.enums.INT_QUERY_NODE - closest_node
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SEARCH)
        _value = cast(int, value)
        return _value

    @SEARCH.setter
    def SEARCH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SEARCH, value)

    @property
    def search(self) -> int:
        """SEARCH property
        
        Search
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.INT_QUERY_EXACT - exact
            * ensight.objs.enums.INT_QUERY_NODE - closest_node
        
        Note: both 'search' and 'SEARCH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SEARCH)
        _value = cast(int, value)
        return _value

    @search.setter
    def search(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SEARCH, value)

    @property
    def REQUESTMETHOD(self) -> int:
        """REQUESTMETHOD property
        
        Request
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - continuous
            * ensight.objs.enums.TRUE - pick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REQUESTMETHOD)
        _value = cast(int, value)
        return _value

    @REQUESTMETHOD.setter
    def REQUESTMETHOD(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REQUESTMETHOD, value)

    @property
    def requestmethod(self) -> int:
        """REQUESTMETHOD property
        
        Request
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - continuous
            * ensight.objs.enums.TRUE - pick
        
        Note: both 'requestmethod' and 'REQUESTMETHOD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REQUESTMETHOD)
        _value = cast(int, value)
        return _value

    @requestmethod.setter
    def requestmethod(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REQUESTMETHOD, value)

    @property
    def LABELALWAYSONTOP(self) -> int:
        """LABELALWAYSONTOP property
        
        Always on top
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELALWAYSONTOP)
        _value = cast(int, value)
        return _value

    @LABELALWAYSONTOP.setter
    def LABELALWAYSONTOP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELALWAYSONTOP, value)

    @property
    def labelalwaysontop(self) -> int:
        """LABELALWAYSONTOP property
        
        Always on top
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'labelalwaysontop' and 'LABELALWAYSONTOP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELALWAYSONTOP)
        _value = cast(int, value)
        return _value

    @labelalwaysontop.setter
    def labelalwaysontop(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELALWAYSONTOP, value)

    @property
    def NUMDISPLAYED(self) -> int:
        """NUMDISPLAYED property
        
        Marker number
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMDISPLAYED)
        _value = cast(int, value)
        return _value

    @NUMDISPLAYED.setter
    def NUMDISPLAYED(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NUMDISPLAYED, value)

    @property
    def numdisplayed(self) -> int:
        """NUMDISPLAYED property
        
        Marker number
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'numdisplayed' and 'NUMDISPLAYED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMDISPLAYED)
        _value = cast(int, value)
        return _value

    @numdisplayed.setter
    def numdisplayed(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NUMDISPLAYED, value)

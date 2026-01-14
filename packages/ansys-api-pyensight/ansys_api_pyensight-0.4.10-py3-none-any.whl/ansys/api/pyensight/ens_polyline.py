"""ens_polyline module

The ens_polyline module provides a proxy interface to EnSight ENS_POLYLINE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_POLYLINE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_POLYLINE

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

    def attrgroupinfo(self, *args, **kwargs) -> Any:
        """Get information about GUI groups for object attributes

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

    def interpolate(self, *args, **kwargs) -> Any:
        """Interpolate polyline points

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.interpolate({arg_string})"
        return self._session.cmd(cmd)

    def createpolyline(self, *args, **kwargs) -> Any:
        """Create a new polyline object

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.createpolyline({arg_string})"
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
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        description
        
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
        
        description
        
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
    def COLOR(self) -> List[float]:
        """COLOR property
        
        color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COLOR)
        _value = cast(List[float], value)
        return _value

    @COLOR.setter
    def COLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.COLOR, value)

    @property
    def color(self) -> List[float]:
        """COLOR property
        
        color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        Note: both 'color' and 'COLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COLOR)
        _value = cast(List[float], value)
        return _value

    @color.setter
    def color(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.COLOR, value)

    @property
    def VISIBLE(self) -> int:
        """VISIBLE property
        
        line visible
        
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
        
        line visible
        
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
    def POINTVISIBLE(self) -> int:
        """POINTVISIBLE property
        
        points visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.POINTVISIBLE)
        _value = cast(int, value)
        return _value

    @POINTVISIBLE.setter
    def POINTVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.POINTVISIBLE, value)

    @property
    def pointvisible(self) -> int:
        """POINTVISIBLE property
        
        points visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'pointvisible' and 'POINTVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.POINTVISIBLE)
        _value = cast(int, value)
        return _value

    @pointvisible.setter
    def pointvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.POINTVISIBLE, value)

    @property
    def POINTSIZE(self) -> float:
        """POINTSIZE property
        
        point size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.POINTSIZE)
        _value = cast(float, value)
        return _value

    @POINTSIZE.setter
    def POINTSIZE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.POINTSIZE, value)

    @property
    def pointsize(self) -> float:
        """POINTSIZE property
        
        point size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'pointsize' and 'POINTSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.POINTSIZE)
        _value = cast(float, value)
        return _value

    @pointsize.setter
    def pointsize(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.POINTSIZE, value)

    @property
    def LINEWIDTH(self) -> float:
        """LINEWIDTH property
        
        line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(float, value)
        return _value

    @LINEWIDTH.setter
    def LINEWIDTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def linewidth(self) -> float:
        """LINEWIDTH property
        
        line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'linewidth' and 'LINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(float, value)
        return _value

    @linewidth.setter
    def linewidth(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def NUMCONTROLPOINTS(self) -> int:
        """NUMCONTROLPOINTS property
        
        number of control points
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMCONTROLPOINTS)
        _value = cast(int, value)
        return _value

    @property
    def numcontrolpoints(self) -> int:
        """NUMCONTROLPOINTS property
        
        number of control points
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'numcontrolpoints' and 'NUMCONTROLPOINTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMCONTROLPOINTS)
        _value = cast(int, value)
        return _value

    @property
    def CONTROLPOINTS(self) -> object:
        """CONTROLPOINTS property
        
        control points
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONTROLPOINTS)
        _value = cast(object, value)
        return _value

    @property
    def controlpoints(self) -> object:
        """CONTROLPOINTS property
        
        control points
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'controlpoints' and 'CONTROLPOINTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONTROLPOINTS)
        _value = cast(object, value)
        return _value

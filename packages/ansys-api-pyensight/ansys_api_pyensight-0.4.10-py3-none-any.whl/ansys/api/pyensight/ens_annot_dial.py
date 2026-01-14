"""ens_annot_dial module

The ens_annot_dial module provides a proxy interface to EnSight ENS_ANNOT_DIAL instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from ansys.api.pyensight.ens_annot import ENS_ANNOT
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_ANNOT_DIAL(ENS_ANNOT):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_ANNOT

    Args:
        *args:
            Superclass (ENS_ANNOT) arguments
        **kwargs:
            Superclass (ENS_ANNOT) keyword arguments

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

    def createannot(self, *args, **kwargs) -> Any:
        """Create a new annotation

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.createannot({arg_string})"
        return self._session.cmd(cmd)

    def attrgroupinfo(self, *args, **kwargs) -> Any:
        """Get information about GUI groups for this annot's attributes

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
    def ANNOTTYPE(self) -> int:
        """ANNOTTYPE property
        
        Type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNO_TEXT - text annotation
            * ensight.objs.enums.ANNO_LINE - line annotation
            * ensight.objs.enums.ANNO_LOGO - logo annotation
            * ensight.objs.enums.ANNO_LGND - legend annotation
            * ensight.objs.enums.ANNO_ARROW - 3D arrow annotation
            * ensight.objs.enums.ANNO_DIAL - dial annotation
            * ensight.objs.enums.ANNO_GAUGE - gauge annotation
            * ensight.objs.enums.ANNO_SHAPE - 2D shape annotation
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTTYPE)
        _value = cast(int, value)
        return _value

    @property
    def annottype(self) -> int:
        """ANNOTTYPE property
        
        Type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNO_TEXT - text annotation
            * ensight.objs.enums.ANNO_LINE - line annotation
            * ensight.objs.enums.ANNO_LOGO - logo annotation
            * ensight.objs.enums.ANNO_LGND - legend annotation
            * ensight.objs.enums.ANNO_ARROW - 3D arrow annotation
            * ensight.objs.enums.ANNO_DIAL - dial annotation
            * ensight.objs.enums.ANNO_GAUGE - gauge annotation
            * ensight.objs.enums.ANNO_SHAPE - 2D shape annotation
        
        Note: both 'annottype' and 'ANNOTTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTTYPE)
        _value = cast(int, value)
        return _value

    @property
    def ANNOTINDEX(self) -> int:
        """ANNOTINDEX property
        
        annotation index
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTINDEX)
        _value = cast(int, value)
        return _value

    @property
    def annotindex(self) -> int:
        """ANNOTINDEX property
        
        annotation index
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'annotindex' and 'ANNOTINDEX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTINDEX)
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
        
        Visible
        
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
        
        Visible
        
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
    def VARIABLE(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE property
        
        Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Constant
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @VARIABLE.setter
    def VARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE, value)

    @property
    def variable(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE property
        
        Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Constant
        
        Note: both 'variable' and 'VARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @variable.setter
    def variable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE, value)

    @property
    def RADIUS(self) -> float:
        """RADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RADIUS)
        _value = cast(float, value)
        return _value

    @RADIUS.setter
    def RADIUS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.RADIUS, value)

    @property
    def radius(self) -> float:
        """RADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'radius' and 'RADIUS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RADIUS)
        _value = cast(float, value)
        return _value

    @radius.setter
    def radius(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.RADIUS, value)

    @property
    def VALUE(self) -> int:
        """VALUE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUE)
        _value = cast(int, value)
        return _value

    @VALUE.setter
    def VALUE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUE, value)

    @property
    def value(self) -> int:
        """VALUE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'value' and 'VALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUE)
        _value = cast(int, value)
        return _value

    @value.setter
    def value(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUE, value)

    @property
    def LOCATIONX(self) -> float:
        """LOCATIONX property
        
        X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONX)
        _value = cast(float, value)
        return _value

    @LOCATIONX.setter
    def LOCATIONX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONX, value)

    @property
    def locationx(self) -> float:
        """LOCATIONX property
        
        X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'locationx' and 'LOCATIONX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONX)
        _value = cast(float, value)
        return _value

    @locationx.setter
    def locationx(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONX, value)

    @property
    def LOCATIONY(self) -> float:
        """LOCATIONY property
        
        Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONY)
        _value = cast(float, value)
        return _value

    @LOCATIONY.setter
    def LOCATIONY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONY, value)

    @property
    def locationy(self) -> float:
        """LOCATIONY property
        
        Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'locationy' and 'LOCATIONY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONY)
        _value = cast(float, value)
        return _value

    @locationy.setter
    def locationy(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONY, value)

    @property
    def BORDER(self) -> int:
        """BORDER property
        
        Border
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDER)
        _value = cast(int, value)
        return _value

    @BORDER.setter
    def BORDER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDER, value)

    @property
    def border(self) -> int:
        """BORDER property
        
        Border
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'border' and 'BORDER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDER)
        _value = cast(int, value)
        return _value

    @border.setter
    def border(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDER, value)

    @property
    def TICKMARKS(self) -> int:
        """TICKMARKS property
        
        Tick marks
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TICKMARKS)
        _value = cast(int, value)
        return _value

    @TICKMARKS.setter
    def TICKMARKS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TICKMARKS, value)

    @property
    def tickmarks(self) -> int:
        """TICKMARKS property
        
        Tick marks
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'tickmarks' and 'TICKMARKS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TICKMARKS)
        _value = cast(int, value)
        return _value

    @tickmarks.setter
    def tickmarks(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TICKMARKS, value)

    @property
    def BIGHANDRGB(self) -> List[float]:
        """BIGHANDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BIGHANDRGB)
        _value = cast(List[float], value)
        return _value

    @BIGHANDRGB.setter
    def BIGHANDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BIGHANDRGB, value)

    @property
    def bighandrgb(self) -> List[float]:
        """BIGHANDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        Note: both 'bighandrgb' and 'BIGHANDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BIGHANDRGB)
        _value = cast(List[float], value)
        return _value

    @bighandrgb.setter
    def bighandrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BIGHANDRGB, value)

    @property
    def MINIMUM(self) -> float:
        """MINIMUM property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MINIMUM)
        _value = cast(float, value)
        return _value

    @MINIMUM.setter
    def MINIMUM(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MINIMUM, value)

    @property
    def minimum(self) -> float:
        """MINIMUM property
        
        Minimum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'minimum' and 'MINIMUM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MINIMUM)
        _value = cast(float, value)
        return _value

    @minimum.setter
    def minimum(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MINIMUM, value)

    @property
    def BIGHANDRANGE(self) -> float:
        """BIGHANDRANGE property
        
        Range
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BIGHANDRANGE)
        _value = cast(float, value)
        return _value

    @BIGHANDRANGE.setter
    def BIGHANDRANGE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BIGHANDRANGE, value)

    @property
    def bighandrange(self) -> float:
        """BIGHANDRANGE property
        
        Range
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'bighandrange' and 'BIGHANDRANGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BIGHANDRANGE)
        _value = cast(float, value)
        return _value

    @bighandrange.setter
    def bighandrange(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BIGHANDRANGE, value)

    @property
    def LITTLEHAND(self) -> int:
        """LITTLEHAND property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LITTLEHAND)
        _value = cast(int, value)
        return _value

    @LITTLEHAND.setter
    def LITTLEHAND(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LITTLEHAND, value)

    @property
    def littlehand(self) -> int:
        """LITTLEHAND property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'littlehand' and 'LITTLEHAND' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LITTLEHAND)
        _value = cast(int, value)
        return _value

    @littlehand.setter
    def littlehand(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LITTLEHAND, value)

    @property
    def LITTLEHANDRGB(self) -> List[float]:
        """LITTLEHANDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LITTLEHANDRGB)
        _value = cast(List[float], value)
        return _value

    @LITTLEHANDRGB.setter
    def LITTLEHANDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LITTLEHANDRGB, value)

    @property
    def littlehandrgb(self) -> List[float]:
        """LITTLEHANDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        Note: both 'littlehandrgb' and 'LITTLEHANDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LITTLEHANDRGB)
        _value = cast(List[float], value)
        return _value

    @littlehandrgb.setter
    def littlehandrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LITTLEHANDRGB, value)

    @property
    def LITTLEHANDRANGE(self) -> float:
        """LITTLEHANDRANGE property
        
        Range
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LITTLEHANDRANGE)
        _value = cast(float, value)
        return _value

    @LITTLEHANDRANGE.setter
    def LITTLEHANDRANGE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LITTLEHANDRANGE, value)

    @property
    def littlehandrange(self) -> float:
        """LITTLEHANDRANGE property
        
        Range
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'littlehandrange' and 'LITTLEHANDRANGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LITTLEHANDRANGE)
        _value = cast(float, value)
        return _value

    @littlehandrange.setter
    def littlehandrange(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LITTLEHANDRANGE, value)

    @property
    def BACKGROUND(self) -> int:
        """BACKGROUND property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUND)
        _value = cast(int, value)
        return _value

    @BACKGROUND.setter
    def BACKGROUND(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUND, value)

    @property
    def background(self) -> int:
        """BACKGROUND property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'background' and 'BACKGROUND' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUND)
        _value = cast(int, value)
        return _value

    @background.setter
    def background(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUND, value)

    @property
    def VALUERGB(self) -> List[float]:
        """VALUERGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUERGB)
        _value = cast(List[float], value)
        return _value

    @VALUERGB.setter
    def VALUERGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUERGB, value)

    @property
    def valuergb(self) -> List[float]:
        """VALUERGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        Note: both 'valuergb' and 'VALUERGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUERGB)
        _value = cast(List[float], value)
        return _value

    @valuergb.setter
    def valuergb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUERGB, value)

    @property
    def BACKGROUNDRGB(self) -> List[float]:
        """BACKGROUNDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
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
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        
        Note: both 'backgroundrgb' and 'BACKGROUNDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDRGB)
        _value = cast(List[float], value)
        return _value

    @backgroundrgb.setter
    def backgroundrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDRGB, value)

    @property
    def VALUESIZE(self) -> int:
        """VALUESIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUESIZE)
        _value = cast(int, value)
        return _value

    @VALUESIZE.setter
    def VALUESIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUESIZE, value)

    @property
    def valuesize(self) -> int:
        """VALUESIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'valuesize' and 'VALUESIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUESIZE)
        _value = cast(int, value)
        return _value

    @valuesize.setter
    def valuesize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUESIZE, value)

    @property
    def SHOWAS(self) -> int:
        """SHOWAS property
        
        Show as
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - revolutions
            * ensight.objs.enums.FALSE - value
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWAS)
        _value = cast(int, value)
        return _value

    @SHOWAS.setter
    def SHOWAS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWAS, value)

    @property
    def showas(self) -> int:
        """SHOWAS property
        
        Show as
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - revolutions
            * ensight.objs.enums.FALSE - value
        
        Note: both 'showas' and 'SHOWAS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWAS)
        _value = cast(int, value)
        return _value

    @showas.setter
    def showas(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWAS, value)

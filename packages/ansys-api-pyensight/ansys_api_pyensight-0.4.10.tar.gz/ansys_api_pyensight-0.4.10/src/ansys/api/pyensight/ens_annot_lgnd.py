"""ens_annot_lgnd module

The ens_annot_lgnd module provides a proxy interface to EnSight ENS_ANNOT_LGND instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from ansys.api.pyensight.ens_annot import ENS_ANNOT
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_ANNOT_LGND(ENS_ANNOT):
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
    def VARCOMP(self) -> List[Tuple['ENS_VAR', int]]:
        """VARCOMP property
        
        Legend variable
        
        Supported operations:
            getattr
        Datatype:
            ENS_VAR + component, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARCOMP)
        _value = cast(List[Tuple['ENS_VAR', int]], value)
        return _value

    @property
    def varcomp(self) -> List[Tuple['ENS_VAR', int]]:
        """VARCOMP property
        
        Legend variable
        
        Supported operations:
            getattr
        Datatype:
            ENS_VAR + component, 2 element array
        
        Note: both 'varcomp' and 'VARCOMP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARCOMP)
        _value = cast(List[Tuple['ENS_VAR', int]], value)
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
    def SCALE(self) -> int:
        """SCALE property
        
        Scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FNC_LINEAR - linear
            * ensight.objs.enums.FNC_QUAD - quadratic
            * ensight.objs.enums.FNC_LOG - logarithmic
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(int, value)
        return _value

    @SCALE.setter
    def SCALE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def scale(self) -> int:
        """SCALE property
        
        Scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FNC_LINEAR - linear
            * ensight.objs.enums.FNC_QUAD - quadratic
            * ensight.objs.enums.FNC_LOG - logarithmic
        
        Note: both 'scale' and 'SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(int, value)
        return _value

    @scale.setter
    def scale(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def TYPE(self) -> int:
        """TYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FNC_CONTIN - continuous
            * ensight.objs.enums.FNC_BAND - banded
            * ensight.objs.enums.FNC_CONST - constant
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TYPE)
        _value = cast(int, value)
        return _value

    @TYPE.setter
    def TYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TYPE, value)

    @property
    def type(self) -> int:
        """TYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FNC_CONTIN - continuous
            * ensight.objs.enums.FNC_BAND - banded
            * ensight.objs.enums.FNC_CONST - constant
        
        Note: both 'type' and 'TYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TYPE)
        _value = cast(int, value)
        return _value

    @type.setter
    def type(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TYPE, value)

    @property
    def RANGE(self) -> List[float]:
        """RANGE property
        
        Range
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RANGE)
        _value = cast(List[float], value)
        return _value

    @RANGE.setter
    def RANGE(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RANGE, value)

    @property
    def range(self) -> List[float]:
        """RANGE property
        
        Range
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'range' and 'RANGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RANGE)
        _value = cast(List[float], value)
        return _value

    @range.setter
    def range(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RANGE, value)

    @property
    def RGB(self) -> List[float]:
        """RGB property
        
        Color
        
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
        
        Color
        
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
    def RELATIVETO(self) -> int:
        """RELATIVETO property
        
        Relative to
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TS_VIEWPORT_RELATIVE - specific_viewport
            * ensight.objs.enums.TS_SCREEN_RELATIVE - entire_view
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVETO)
        _value = cast(int, value)
        return _value

    @RELATIVETO.setter
    def RELATIVETO(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVETO, value)

    @property
    def relativeto(self) -> int:
        """RELATIVETO property
        
        Relative to
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TS_VIEWPORT_RELATIVE - specific_viewport
            * ensight.objs.enums.TS_SCREEN_RELATIVE - entire_view
        
        Note: both 'relativeto' and 'RELATIVETO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVETO)
        _value = cast(int, value)
        return _value

    @relativeto.setter
    def relativeto(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVETO, value)

    @property
    def RELATIVEVIEWPORT(self) -> int:
        """RELATIVEVIEWPORT property
        
        Relative viewport
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT)
        _value = cast(int, value)
        return _value

    @RELATIVEVIEWPORT.setter
    def RELATIVEVIEWPORT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT, value)

    @property
    def relativeviewport(self) -> int:
        """RELATIVEVIEWPORT property
        
        Relative viewport
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'relativeviewport' and 'RELATIVEVIEWPORT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT)
        _value = cast(int, value)
        return _value

    @relativeviewport.setter
    def relativeviewport(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT, value)

    @property
    def SHADOWOFFSET(self) -> int:
        """SHADOWOFFSET property
        
        Shadow offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 10]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHADOWOFFSET)
        _value = cast(int, value)
        return _value

    @SHADOWOFFSET.setter
    def SHADOWOFFSET(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHADOWOFFSET, value)

    @property
    def shadowoffset(self) -> int:
        """SHADOWOFFSET property
        
        Shadow offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 10]
        
        Note: both 'shadowoffset' and 'SHADOWOFFSET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHADOWOFFSET)
        _value = cast(int, value)
        return _value

    @shadowoffset.setter
    def shadowoffset(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHADOWOFFSET, value)

    @property
    def SHADOWINTENSITY(self) -> float:
        """SHADOWINTENSITY property
        
        Shadow intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHADOWINTENSITY)
        _value = cast(float, value)
        return _value

    @SHADOWINTENSITY.setter
    def SHADOWINTENSITY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SHADOWINTENSITY, value)

    @property
    def shadowintensity(self) -> float:
        """SHADOWINTENSITY property
        
        Shadow intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'shadowintensity' and 'SHADOWINTENSITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHADOWINTENSITY)
        _value = cast(float, value)
        return _value

    @shadowintensity.setter
    def shadowintensity(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SHADOWINTENSITY, value)

    @property
    def LOCATIONX(self) -> float:
        """LOCATIONX property
        
        X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
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
        Range:
            [0.0, 1.0]
        
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
        Range:
            [0.0, 1.0]
        
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
        Range:
            [0.0, 1.0]
        
        Note: both 'locationy' and 'LOCATIONY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONY)
        _value = cast(float, value)
        return _value

    @locationy.setter
    def locationy(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONY, value)

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
    def ORIENTATION(self) -> int:
        """ORIENTATION property
        
        Orientation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - vertical
            * ensight.objs.enums.TRUE - horizontal
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIENTATION)
        _value = cast(int, value)
        return _value

    @ORIENTATION.setter
    def ORIENTATION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIENTATION, value)

    @property
    def orientation(self) -> int:
        """ORIENTATION property
        
        Orientation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FALSE - vertical
            * ensight.objs.enums.TRUE - horizontal
        
        Note: both 'orientation' and 'ORIENTATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIENTATION)
        _value = cast(int, value)
        return _value

    @orientation.setter
    def orientation(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIENTATION, value)

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
    def TEXTSIZE(self) -> int:
        """TEXTSIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTSIZE)
        _value = cast(int, value)
        return _value

    @TEXTSIZE.setter
    def TEXTSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTSIZE, value)

    @property
    def textsize(self) -> int:
        """TEXTSIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'textsize' and 'TEXTSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTSIZE)
        _value = cast(int, value)
        return _value

    @textsize.setter
    def textsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTSIZE, value)

    @property
    def TEXTRGB(self) -> List[float]:
        """TEXTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTRGB)
        _value = cast(List[float], value)
        return _value

    @TEXTRGB.setter
    def TEXTRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTRGB, value)

    @property
    def textrgb(self) -> List[float]:
        """TEXTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'textrgb' and 'TEXTRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTRGB)
        _value = cast(List[float], value)
        return _value

    @textrgb.setter
    def textrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTRGB, value)

    @property
    def TEXTPOSITION(self) -> int:
        """TEXTPOSITION property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_LEFT - left
            * ensight.objs.enums.LEGEND_RIGHT - right
            * ensight.objs.enums.LEGEND_LEFT - bottom
            * ensight.objs.enums.LEGEND_RIGHT - top
            * ensight.objs.enums.LEGEND_TXT_VISOFF - none
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTPOSITION)
        _value = cast(int, value)
        return _value

    @TEXTPOSITION.setter
    def TEXTPOSITION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTPOSITION, value)

    @property
    def textposition(self) -> int:
        """TEXTPOSITION property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_LEFT - left
            * ensight.objs.enums.LEGEND_RIGHT - right
            * ensight.objs.enums.LEGEND_LEFT - bottom
            * ensight.objs.enums.LEGEND_RIGHT - top
            * ensight.objs.enums.LEGEND_TXT_VISOFF - none
        
        Note: both 'textposition' and 'TEXTPOSITION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTPOSITION)
        _value = cast(int, value)
        return _value

    @textposition.setter
    def textposition(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTPOSITION, value)

    @property
    def TEXTTYPE(self) -> int:
        """TEXTTYPE property
        
        Text type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - off
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - normal
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - graphics_font
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTTYPE)
        _value = cast(int, value)
        return _value

    @TEXTTYPE.setter
    def TEXTTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTTYPE, value)

    @property
    def texttype(self) -> int:
        """TEXTTYPE property
        
        Text type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - off
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - normal
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - graphics_font
        
        Note: both 'texttype' and 'TEXTTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTTYPE)
        _value = cast(int, value)
        return _value

    @texttype.setter
    def texttype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTTYPE, value)

    @property
    def FORMAT(self) -> str:
        """FORMAT property
        
        Format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FORMAT)
        _value = cast(str, value)
        return _value

    @FORMAT.setter
    def FORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.FORMAT, value)

    @property
    def format(self) -> str:
        """FORMAT property
        
        Format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'format' and 'FORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FORMAT)
        _value = cast(str, value)
        return _value

    @format.setter
    def format(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.FORMAT, value)

    @property
    def TITLELOCATION(self) -> int:
        """TITLELOCATION property
        
        Title location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_TITLE_TOP - above
            * ensight.objs.enums.LEGEND_TITLE_BOTTOM - below
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - none
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TITLELOCATION)
        _value = cast(int, value)
        return _value

    @TITLELOCATION.setter
    def TITLELOCATION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TITLELOCATION, value)

    @property
    def titlelocation(self) -> int:
        """TITLELOCATION property
        
        Title location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_TITLE_TOP - above
            * ensight.objs.enums.LEGEND_TITLE_BOTTOM - below
            * ensight.objs.enums.LEGEND_TITLE_VISOFF - none
        
        Note: both 'titlelocation' and 'TITLELOCATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TITLELOCATION)
        _value = cast(int, value)
        return _value

    @titlelocation.setter
    def titlelocation(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TITLELOCATION, value)

    @property
    def SHOWMINMAXMARKER(self) -> int:
        """SHOWMINMAXMARKER property
        
        Show minmax marker
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWMINMAXMARKER)
        _value = cast(int, value)
        return _value

    @SHOWMINMAXMARKER.setter
    def SHOWMINMAXMARKER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWMINMAXMARKER, value)

    @property
    def showminmaxmarker(self) -> int:
        """SHOWMINMAXMARKER property
        
        Show minmax marker
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'showminmaxmarker' and 'SHOWMINMAXMARKER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWMINMAXMARKER)
        _value = cast(int, value)
        return _value

    @showminmaxmarker.setter
    def showminmaxmarker(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWMINMAXMARKER, value)

    @property
    def LEGENDTYPE(self) -> int:
        """LEGENDTYPE property
        
        Legend type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_CONT - continuous
            * ensight.objs.enums.LEGEND_DISC - discrete
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDTYPE)
        _value = cast(int, value)
        return _value

    @LEGENDTYPE.setter
    def LEGENDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDTYPE, value)

    @property
    def legendtype(self) -> int:
        """LEGENDTYPE property
        
        Legend type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LEGEND_CONT - continuous
            * ensight.objs.enums.LEGEND_DISC - discrete
        
        Note: both 'legendtype' and 'LEGENDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGENDTYPE)
        _value = cast(int, value)
        return _value

    @legendtype.setter
    def legendtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEGENDTYPE, value)

    @property
    def SHOWBACKGROUND(self) -> int:
        """SHOWBACKGROUND property
        
        Show background
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWBACKGROUND)
        _value = cast(int, value)
        return _value

    @SHOWBACKGROUND.setter
    def SHOWBACKGROUND(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWBACKGROUND, value)

    @property
    def showbackground(self) -> int:
        """SHOWBACKGROUND property
        
        Show background
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'showbackground' and 'SHOWBACKGROUND' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWBACKGROUND)
        _value = cast(int, value)
        return _value

    @showbackground.setter
    def showbackground(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWBACKGROUND, value)

    @property
    def SPECIFYLABELCOUNT(self) -> int:
        """SPECIFYLABELCOUNT property
        
        Specify label count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPECIFYLABELCOUNT)
        _value = cast(int, value)
        return _value

    @SPECIFYLABELCOUNT.setter
    def SPECIFYLABELCOUNT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPECIFYLABELCOUNT, value)

    @property
    def specifylabelcount(self) -> int:
        """SPECIFYLABELCOUNT property
        
        Specify label count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'specifylabelcount' and 'SPECIFYLABELCOUNT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPECIFYLABELCOUNT)
        _value = cast(int, value)
        return _value

    @specifylabelcount.setter
    def specifylabelcount(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPECIFYLABELCOUNT, value)

    @property
    def LABELCOUNT(self) -> int:
        """LABELCOUNT property
        
        Label count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, 50]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELCOUNT)
        _value = cast(int, value)
        return _value

    @LABELCOUNT.setter
    def LABELCOUNT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELCOUNT, value)

    @property
    def labelcount(self) -> int:
        """LABELCOUNT property
        
        Label count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, 50]
        
        Note: both 'labelcount' and 'LABELCOUNT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELCOUNT)
        _value = cast(int, value)
        return _value

    @labelcount.setter
    def labelcount(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELCOUNT, value)

    @property
    def NUMOFLEVELS(self) -> int:
        """NUMOFLEVELS property
        
        Number of levels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, 21]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMOFLEVELS)
        _value = cast(int, value)
        return _value

    @NUMOFLEVELS.setter
    def NUMOFLEVELS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NUMOFLEVELS, value)

    @property
    def numoflevels(self) -> int:
        """NUMOFLEVELS property
        
        Number of levels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, 21]
        
        Note: both 'numoflevels' and 'NUMOFLEVELS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMOFLEVELS)
        _value = cast(int, value)
        return _value

    @numoflevels.setter
    def numoflevels(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NUMOFLEVELS, value)

    @property
    def LIMITFRINGES(self) -> int:
        """LIMITFRINGES property
        
        Outside range display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FNC_NOLIMIT - no
            * ensight.objs.enums.FNC_LIMCOL - by_part_color
            * ensight.objs.enums.FNC_LIMVIS - by_invisible
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIMITFRINGES)
        _value = cast(int, value)
        return _value

    @LIMITFRINGES.setter
    def LIMITFRINGES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIMITFRINGES, value)

    @property
    def limitfringes(self) -> int:
        """LIMITFRINGES property
        
        Outside range display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FNC_NOLIMIT - no
            * ensight.objs.enums.FNC_LIMCOL - by_part_color
            * ensight.objs.enums.FNC_LIMVIS - by_invisible
        
        Note: both 'limitfringes' and 'LIMITFRINGES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIMITFRINGES)
        _value = cast(int, value)
        return _value

    @limitfringes.setter
    def limitfringes(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIMITFRINGES, value)

    @property
    def DISPLAYUNDEFINED(self) -> int:
        """DISPLAYUNDEFINED property
        
        Undefined value display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_BY_PART_COLOR - by_part_color
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_BY_INVISIBLE - by_invisible
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_AS_ZERO_VALUE - as_zero_value
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_BY_UNDEF_COLOR - by_specified_color
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLAYUNDEFINED)
        _value = cast(int, value)
        return _value

    @DISPLAYUNDEFINED.setter
    def DISPLAYUNDEFINED(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLAYUNDEFINED, value)

    @property
    def displayundefined(self) -> int:
        """DISPLAYUNDEFINED property
        
        Undefined value display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_BY_PART_COLOR - by_part_color
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_BY_INVISIBLE - by_invisible
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_AS_ZERO_VALUE - as_zero_value
            * ensight.objs.enums.CVF_PALETTE_UNDEFINED_BY_UNDEF_COLOR - by_specified_color
        
        Note: both 'displayundefined' and 'DISPLAYUNDEFINED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLAYUNDEFINED)
        _value = cast(int, value)
        return _value

    @displayundefined.setter
    def displayundefined(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLAYUNDEFINED, value)

    @property
    def UNDEFINEDCOLOR(self) -> List[float]:
        """UNDEFINEDCOLOR property
        
        Undefined color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.UNDEFINEDCOLOR)
        _value = cast(List[float], value)
        return _value

    @UNDEFINEDCOLOR.setter
    def UNDEFINEDCOLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.UNDEFINEDCOLOR, value)

    @property
    def undefinedcolor(self) -> List[float]:
        """UNDEFINEDCOLOR property
        
        Undefined color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'undefinedcolor' and 'UNDEFINEDCOLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.UNDEFINEDCOLOR)
        _value = cast(List[float], value)
        return _value

    @undefinedcolor.setter
    def undefinedcolor(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.UNDEFINEDCOLOR, value)

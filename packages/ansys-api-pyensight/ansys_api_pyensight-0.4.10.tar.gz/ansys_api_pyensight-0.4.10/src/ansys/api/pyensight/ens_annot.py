"""ens_annot module

The ens_annot module provides a proxy interface to EnSight ENS_ANNOT instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_ANNOT(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_ANNOT

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
    def SIZE(self) -> int:
        """SIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SIZE)
        _value = cast(int, value)
        return _value

    @SIZE.setter
    def SIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SIZE, value)

    @property
    def size(self) -> int:
        """SIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'size' and 'SIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SIZE)
        _value = cast(int, value)
        return _value

    @size.setter
    def size(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SIZE, value)

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
    def JUSTIFICATION(self) -> int:
        """JUSTIFICATION property
        
        Justification
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TS_LEFT - left
            * ensight.objs.enums.TS_CENTER - center
            * ensight.objs.enums.TS_RIGHT - right
        
        """
        value = self.getattr(self._session.ensight.objs.enums.JUSTIFICATION)
        _value = cast(int, value)
        return _value

    @JUSTIFICATION.setter
    def JUSTIFICATION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.JUSTIFICATION, value)

    @property
    def justification(self) -> int:
        """JUSTIFICATION property
        
        Justification
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TS_LEFT - left
            * ensight.objs.enums.TS_CENTER - center
            * ensight.objs.enums.TS_RIGHT - right
        
        Note: both 'justification' and 'JUSTIFICATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.JUSTIFICATION)
        _value = cast(int, value)
        return _value

    @justification.setter
    def justification(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.JUSTIFICATION, value)

    @property
    def ROTATIONALANGLE(self) -> float:
        """ROTATIONALANGLE property
        
        Rotational angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [-360.0, 360.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ROTATIONALANGLE)
        _value = cast(float, value)
        return _value

    @ROTATIONALANGLE.setter
    def ROTATIONALANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ROTATIONALANGLE, value)

    @property
    def rotationalangle(self) -> float:
        """ROTATIONALANGLE property
        
        Rotational angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [-360.0, 360.0]
        
        Note: both 'rotationalangle' and 'ROTATIONALANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ROTATIONALANGLE)
        _value = cast(float, value)
        return _value

    @rotationalangle.setter
    def rotationalangle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ROTATIONALANGLE, value)

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
    def ORIGINBY(self) -> int:
        """ORIGINBY property
        
        Origin by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNOT_2D_SPACE - screen_coords
            * ensight.objs.enums.ANNOT_3D_SPACE - 3d_coords
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINBY)
        _value = cast(int, value)
        return _value

    @ORIGINBY.setter
    def ORIGINBY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINBY, value)

    @property
    def originby(self) -> int:
        """ORIGINBY property
        
        Origin by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNOT_2D_SPACE - screen_coords
            * ensight.objs.enums.ANNOT_3D_SPACE - 3d_coords
        
        Note: both 'originby' and 'ORIGINBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINBY)
        _value = cast(int, value)
        return _value

    @originby.setter
    def originby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINBY, value)

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
    def ORIGINFRAME(self) -> int:
        """ORIGINFRAME property
        
        Origin frame
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINFRAME)
        _value = cast(int, value)
        return _value

    @ORIGINFRAME.setter
    def ORIGINFRAME(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINFRAME, value)

    @property
    def originframe(self) -> int:
        """ORIGINFRAME property
        
        Origin frame
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'originframe' and 'ORIGINFRAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINFRAME)
        _value = cast(int, value)
        return _value

    @originframe.setter
    def originframe(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINFRAME, value)

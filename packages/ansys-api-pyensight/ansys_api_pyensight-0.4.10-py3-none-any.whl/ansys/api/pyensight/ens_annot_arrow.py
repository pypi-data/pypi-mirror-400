"""ens_annot_arrow module

The ens_annot_arrow module provides a proxy interface to EnSight ENS_ANNOT_ARROW instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from ansys.api.pyensight.ens_annot import ENS_ANNOT
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_ANNOT_ARROW(ENS_ANNOT):
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
    def VIEWPORTVIS(self) -> int:
        """VIEWPORTVIS property
        
        Per viewport
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums (bitfield):
            * ensight.objs.enums.VIEWPORT00 - Viewport 0
            * ensight.objs.enums.VIEWPORT01 - Viewport 1
            * ensight.objs.enums.VIEWPORT02 - Viewport 2
            * ensight.objs.enums.VIEWPORT03 - Viewport 3
            * ensight.objs.enums.VIEWPORT04 - Viewport 4
            * ensight.objs.enums.VIEWPORT05 - Viewport 5
            * ensight.objs.enums.VIEWPORT06 - Viewport 6
            * ensight.objs.enums.VIEWPORT07 - Viewport 7
            * ensight.objs.enums.VIEWPORT08 - Viewport 8
            * ensight.objs.enums.VIEWPORT09 - Viewport 9
            * ensight.objs.enums.VIEWPORT10 - Viewport 10
            * ensight.objs.enums.VIEWPORT11 - Viewport 11
            * ensight.objs.enums.VIEWPORT12 - Viewport 12
            * ensight.objs.enums.VIEWPORT13 - Viewport 13
            * ensight.objs.enums.VIEWPORT14 - Viewport 14
            * ensight.objs.enums.VIEWPORT15 - Viewport 15
            * ensight.objs.enums.VIEWPORT16 - Viewport 16
            * ensight.objs.enums.VIEWPORT17 - Viewport 17
            * ensight.objs.enums.VIEWPORT18 - Viewport 18
            * ensight.objs.enums.VIEWPORT19 - Viewport 19
            * ensight.objs.enums.VIEWPORT20 - Viewport 20
            * ensight.objs.enums.VIEWPORT21 - Viewport 21
            * ensight.objs.enums.VIEWPORT22 - Viewport 22
            * ensight.objs.enums.VIEWPORT23 - Viewport 23
            * ensight.objs.enums.VIEWPORT24 - Viewport 24
            * ensight.objs.enums.VIEWPORT25 - Viewport 25
            * ensight.objs.enums.VIEWPORT26 - Viewport 26
            * ensight.objs.enums.VIEWPORT27 - Viewport 27
            * ensight.objs.enums.VIEWPORT28 - Viewport 28
            * ensight.objs.enums.VIEWPORT29 - Viewport 29
            * ensight.objs.enums.VIEWPORT30 - Viewport 30
            * ensight.objs.enums.VIEWPORT31 - Viewport 31
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VIEWPORTVIS)
        _value = cast(int, value)
        return _value

    @VIEWPORTVIS.setter
    def VIEWPORTVIS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VIEWPORTVIS, value)

    @property
    def viewportvis(self) -> int:
        """VIEWPORTVIS property
        
        Per viewport
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums (bitfield):
            * ensight.objs.enums.VIEWPORT00 - Viewport 0
            * ensight.objs.enums.VIEWPORT01 - Viewport 1
            * ensight.objs.enums.VIEWPORT02 - Viewport 2
            * ensight.objs.enums.VIEWPORT03 - Viewport 3
            * ensight.objs.enums.VIEWPORT04 - Viewport 4
            * ensight.objs.enums.VIEWPORT05 - Viewport 5
            * ensight.objs.enums.VIEWPORT06 - Viewport 6
            * ensight.objs.enums.VIEWPORT07 - Viewport 7
            * ensight.objs.enums.VIEWPORT08 - Viewport 8
            * ensight.objs.enums.VIEWPORT09 - Viewport 9
            * ensight.objs.enums.VIEWPORT10 - Viewport 10
            * ensight.objs.enums.VIEWPORT11 - Viewport 11
            * ensight.objs.enums.VIEWPORT12 - Viewport 12
            * ensight.objs.enums.VIEWPORT13 - Viewport 13
            * ensight.objs.enums.VIEWPORT14 - Viewport 14
            * ensight.objs.enums.VIEWPORT15 - Viewport 15
            * ensight.objs.enums.VIEWPORT16 - Viewport 16
            * ensight.objs.enums.VIEWPORT17 - Viewport 17
            * ensight.objs.enums.VIEWPORT18 - Viewport 18
            * ensight.objs.enums.VIEWPORT19 - Viewport 19
            * ensight.objs.enums.VIEWPORT20 - Viewport 20
            * ensight.objs.enums.VIEWPORT21 - Viewport 21
            * ensight.objs.enums.VIEWPORT22 - Viewport 22
            * ensight.objs.enums.VIEWPORT23 - Viewport 23
            * ensight.objs.enums.VIEWPORT24 - Viewport 24
            * ensight.objs.enums.VIEWPORT25 - Viewport 25
            * ensight.objs.enums.VIEWPORT26 - Viewport 26
            * ensight.objs.enums.VIEWPORT27 - Viewport 27
            * ensight.objs.enums.VIEWPORT28 - Viewport 28
            * ensight.objs.enums.VIEWPORT29 - Viewport 29
            * ensight.objs.enums.VIEWPORT30 - Viewport 30
            * ensight.objs.enums.VIEWPORT31 - Viewport 31
        
        Note: both 'viewportvis' and 'VIEWPORTVIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VIEWPORTVIS)
        _value = cast(int, value)
        return _value

    @viewportvis.setter
    def viewportvis(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VIEWPORTVIS, value)

    @property
    def OFFSET(self) -> float:
        """OFFSET property
        
        Offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OFFSET)
        _value = cast(float, value)
        return _value

    @OFFSET.setter
    def OFFSET(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OFFSET, value)

    @property
    def offset(self) -> float:
        """OFFSET property
        
        Offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'offset' and 'OFFSET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OFFSET)
        _value = cast(float, value)
        return _value

    @offset.setter
    def offset(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OFFSET, value)

    @property
    def LOCATION(self) -> List[float]:
        """LOCATION property
        
        Origin XYZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATION)
        _value = cast(List[float], value)
        return _value

    @LOCATION.setter
    def LOCATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATION, value)

    @property
    def location(self) -> List[float]:
        """LOCATION property
        
        Origin XYZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'location' and 'LOCATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATION)
        _value = cast(List[float], value)
        return _value

    @location.setter
    def location(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATION, value)

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
    def SIZE(self) -> float:
        """SIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SIZE)
        _value = cast(float, value)
        return _value

    @SIZE.setter
    def SIZE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SIZE, value)

    @property
    def size(self) -> float:
        """SIZE property
        
        Size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'size' and 'SIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SIZE)
        _value = cast(float, value)
        return _value

    @size.setter
    def size(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SIZE, value)

    @property
    def NORMAL(self) -> List[float]:
        """NORMAL property
        
        Normal
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NORMAL)
        _value = cast(List[float], value)
        return _value

    @NORMAL.setter
    def NORMAL(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.NORMAL, value)

    @property
    def normal(self) -> List[float]:
        """NORMAL property
        
        Normal
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'normal' and 'NORMAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NORMAL)
        _value = cast(List[float], value)
        return _value

    @normal.setter
    def normal(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.NORMAL, value)

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
    def LABELSIZE(self) -> int:
        """LABELSIZE property
        
        Font size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE)
        _value = cast(int, value)
        return _value

    @LABELSIZE.setter
    def LABELSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE, value)

    @property
    def labelsize(self) -> int:
        """LABELSIZE property
        
        Font size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'labelsize' and 'LABELSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE)
        _value = cast(int, value)
        return _value

    @labelsize.setter
    def labelsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE, value)

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
    def ORIGINBY(self) -> int:
        """ORIGINBY property
        
        Origin by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ARROW_3D_QUERY_LOCAT - probe_query
            * ensight.objs.enums.ARROW_3D_XYZ_LOCAT - XYZ
            * ensight.objs.enums.ARROW_3D_FORCES - forces
            * ensight.objs.enums.ARROW_3D_MOMENTS - moments
        
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
            * ensight.objs.enums.ARROW_3D_QUERY_LOCAT - probe_query
            * ensight.objs.enums.ARROW_3D_XYZ_LOCAT - XYZ
            * ensight.objs.enums.ARROW_3D_FORCES - forces
            * ensight.objs.enums.ARROW_3D_MOMENTS - moments
        
        Note: both 'originby' and 'ORIGINBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINBY)
        _value = cast(int, value)
        return _value

    @originby.setter
    def originby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINBY, value)

    @property
    def LIGHTDIFF(self) -> float:
        """LIGHTDIFF property
        
        Diffused/Ambient
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTDIFF)
        _value = cast(float, value)
        return _value

    @LIGHTDIFF.setter
    def LIGHTDIFF(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTDIFF, value)

    @property
    def lightdiff(self) -> float:
        """LIGHTDIFF property
        
        Diffused/Ambient
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'lightdiff' and 'LIGHTDIFF' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTDIFF)
        _value = cast(float, value)
        return _value

    @lightdiff.setter
    def lightdiff(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTDIFF, value)

    @property
    def LIGHTSHIN(self) -> float:
        """LIGHTSHIN property
        
        Shininess
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 20.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSHIN)
        _value = cast(float, value)
        return _value

    @LIGHTSHIN.setter
    def LIGHTSHIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSHIN, value)

    @property
    def lightshin(self) -> float:
        """LIGHTSHIN property
        
        Shininess
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 20.0]
        
        Note: both 'lightshin' and 'LIGHTSHIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSHIN)
        _value = cast(float, value)
        return _value

    @lightshin.setter
    def lightshin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSHIN, value)

    @property
    def LIGHTHINT(self) -> float:
        """LIGHTHINT property
        
        Intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTHINT)
        _value = cast(float, value)
        return _value

    @LIGHTHINT.setter
    def LIGHTHINT(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTHINT, value)

    @property
    def lighthint(self) -> float:
        """LIGHTHINT property
        
        Intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'lighthint' and 'LIGHTHINT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTHINT)
        _value = cast(float, value)
        return _value

    @lighthint.setter
    def lighthint(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTHINT, value)

    @property
    def PROBENUMBER(self) -> int:
        """PROBENUMBER property
        
        Probe number
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PROBENUMBER)
        _value = cast(int, value)
        return _value

    @PROBENUMBER.setter
    def PROBENUMBER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROBENUMBER, value)

    @property
    def probenumber(self) -> int:
        """PROBENUMBER property
        
        Probe number
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'probenumber' and 'PROBENUMBER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PROBENUMBER)
        _value = cast(int, value)
        return _value

    @probenumber.setter
    def probenumber(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROBENUMBER, value)

    @property
    def TIPLENGTH(self) -> float:
        """TIPLENGTH property
        
        Tip length
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIPLENGTH)
        _value = cast(float, value)
        return _value

    @TIPLENGTH.setter
    def TIPLENGTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TIPLENGTH, value)

    @property
    def tiplength(self) -> float:
        """TIPLENGTH property
        
        Tip length
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'tiplength' and 'TIPLENGTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIPLENGTH)
        _value = cast(float, value)
        return _value

    @tiplength.setter
    def tiplength(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TIPLENGTH, value)

    @property
    def TIPRADIUS(self) -> float:
        """TIPRADIUS property
        
        Tip radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIPRADIUS)
        _value = cast(float, value)
        return _value

    @TIPRADIUS.setter
    def TIPRADIUS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TIPRADIUS, value)

    @property
    def tipradius(self) -> float:
        """TIPRADIUS property
        
        Tip radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'tipradius' and 'TIPRADIUS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIPRADIUS)
        _value = cast(float, value)
        return _value

    @tipradius.setter
    def tipradius(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TIPRADIUS, value)

    @property
    def SCALEBYLOCATIONVALUE(self) -> int:
        """SCALEBYLOCATIONVALUE property
        
        Scale by location value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEBYLOCATIONVALUE)
        _value = cast(int, value)
        return _value

    @SCALEBYLOCATIONVALUE.setter
    def SCALEBYLOCATIONVALUE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEBYLOCATIONVALUE, value)

    @property
    def scalebylocationvalue(self) -> int:
        """SCALEBYLOCATIONVALUE property
        
        Scale by location value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'scalebylocationvalue' and 'SCALEBYLOCATIONVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEBYLOCATIONVALUE)
        _value = cast(int, value)
        return _value

    @scalebylocationvalue.setter
    def scalebylocationvalue(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEBYLOCATIONVALUE, value)

    @property
    def SCALEMINVALUE(self) -> float:
        """SCALEMINVALUE property
        
          If value <=
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMINVALUE)
        _value = cast(float, value)
        return _value

    @SCALEMINVALUE.setter
    def SCALEMINVALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMINVALUE, value)

    @property
    def scaleminvalue(self) -> float:
        """SCALEMINVALUE property
        
          If value <=
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'scaleminvalue' and 'SCALEMINVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMINVALUE)
        _value = cast(float, value)
        return _value

    @scaleminvalue.setter
    def scaleminvalue(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMINVALUE, value)

    @property
    def SCALEMINFACTOR(self) -> float:
        """SCALEMINFACTOR property
        
            then scale by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMINFACTOR)
        _value = cast(float, value)
        return _value

    @SCALEMINFACTOR.setter
    def SCALEMINFACTOR(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMINFACTOR, value)

    @property
    def scaleminfactor(self) -> float:
        """SCALEMINFACTOR property
        
            then scale by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'scaleminfactor' and 'SCALEMINFACTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMINFACTOR)
        _value = cast(float, value)
        return _value

    @scaleminfactor.setter
    def scaleminfactor(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMINFACTOR, value)

    @property
    def SCALEMAXVALUE(self) -> float:
        """SCALEMAXVALUE property
        
          If value >=
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMAXVALUE)
        _value = cast(float, value)
        return _value

    @SCALEMAXVALUE.setter
    def SCALEMAXVALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMAXVALUE, value)

    @property
    def scalemaxvalue(self) -> float:
        """SCALEMAXVALUE property
        
          If value >=
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'scalemaxvalue' and 'SCALEMAXVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMAXVALUE)
        _value = cast(float, value)
        return _value

    @scalemaxvalue.setter
    def scalemaxvalue(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMAXVALUE, value)

    @property
    def SCALEMAXFACTOR(self) -> float:
        """SCALEMAXFACTOR property
        
            then scale by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMAXFACTOR)
        _value = cast(float, value)
        return _value

    @SCALEMAXFACTOR.setter
    def SCALEMAXFACTOR(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMAXFACTOR, value)

    @property
    def scalemaxfactor(self) -> float:
        """SCALEMAXFACTOR property
        
            then scale by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'scalemaxfactor' and 'SCALEMAXFACTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALEMAXFACTOR)
        _value = cast(float, value)
        return _value

    @scalemaxfactor.setter
    def scalemaxfactor(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALEMAXFACTOR, value)

    @property
    def LABELTEXT(self) -> str:
        """LABELTEXT property
        
        Text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELTEXT)
        _value = cast(str, value)
        return _value

    @LABELTEXT.setter
    def LABELTEXT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELTEXT, value)

    @property
    def labeltext(self) -> str:
        """LABELTEXT property
        
        Text
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'labeltext' and 'LABELTEXT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELTEXT)
        _value = cast(str, value)
        return _value

    @labeltext.setter
    def labeltext(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELTEXT, value)

    @property
    def APPENDLOCATIONVALUE(self) -> int:
        """APPENDLOCATIONVALUE property
        
        Append probe value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.APPENDLOCATIONVALUE)
        _value = cast(int, value)
        return _value

    @APPENDLOCATIONVALUE.setter
    def APPENDLOCATIONVALUE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.APPENDLOCATIONVALUE, value)

    @property
    def appendlocationvalue(self) -> int:
        """APPENDLOCATIONVALUE property
        
        Append probe value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'appendlocationvalue' and 'APPENDLOCATIONVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.APPENDLOCATIONVALUE)
        _value = cast(int, value)
        return _value

    @appendlocationvalue.setter
    def appendlocationvalue(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.APPENDLOCATIONVALUE, value)

    @property
    def USEANNOTATIONTEXT(self) -> int:
        """USEANNOTATIONTEXT property
        
        Use annotation text
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.USEANNOTATIONTEXT)
        _value = cast(int, value)
        return _value

    @USEANNOTATIONTEXT.setter
    def USEANNOTATIONTEXT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.USEANNOTATIONTEXT, value)

    @property
    def useannotationtext(self) -> int:
        """USEANNOTATIONTEXT property
        
        Use annotation text
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'useannotationtext' and 'USEANNOTATIONTEXT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.USEANNOTATIONTEXT)
        _value = cast(int, value)
        return _value

    @useannotationtext.setter
    def useannotationtext(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.USEANNOTATIONTEXT, value)

    @property
    def ANNOTATIONTEXTID(self) -> int:
        """ANNOTATIONTEXTID property
        
        Annotation text id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTATIONTEXTID)
        _value = cast(int, value)
        return _value

    @ANNOTATIONTEXTID.setter
    def ANNOTATIONTEXTID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANNOTATIONTEXTID, value)

    @property
    def annotationtextid(self) -> int:
        """ANNOTATIONTEXTID property
        
        Annotation text id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'annotationtextid' and 'ANNOTATIONTEXTID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTATIONTEXTID)
        _value = cast(int, value)
        return _value

    @annotationtextid.setter
    def annotationtextid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANNOTATIONTEXTID, value)

    @property
    def LABELOFFSET(self) -> float:
        """LABELOFFSET property
        
        Offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELOFFSET)
        _value = cast(float, value)
        return _value

    @LABELOFFSET.setter
    def LABELOFFSET(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELOFFSET, value)

    @property
    def labeloffset(self) -> float:
        """LABELOFFSET property
        
        Offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'labeloffset' and 'LABELOFFSET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELOFFSET)
        _value = cast(float, value)
        return _value

    @labeloffset.setter
    def labeloffset(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELOFFSET, value)

"""ens_annot_line module

The ens_annot_line module provides a proxy interface to EnSight ENS_ANNOT_LINE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from ansys.api.pyensight.ens_annot import ENS_ANNOT
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_ANNOT_LINE(ENS_ANNOT):
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

    @property
    def ARROWHEAD(self) -> int:
        """ARROWHEAD property
        
        Arrowhead
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.NO_ARRW - none
            * ensight.objs.enums.FRST_ARRW - on_first_end
            * ensight.objs.enums.SCND_ARRW - on_second_end
            * ensight.objs.enums.BOTH_ARRW - on_both_ends
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ARROWHEAD)
        _value = cast(int, value)
        return _value

    @ARROWHEAD.setter
    def ARROWHEAD(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ARROWHEAD, value)

    @property
    def arrowhead(self) -> int:
        """ARROWHEAD property
        
        Arrowhead
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.NO_ARRW - none
            * ensight.objs.enums.FRST_ARRW - on_first_end
            * ensight.objs.enums.SCND_ARRW - on_second_end
            * ensight.objs.enums.BOTH_ARRW - on_both_ends
        
        Note: both 'arrowhead' and 'ARROWHEAD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ARROWHEAD)
        _value = cast(int, value)
        return _value

    @arrowhead.setter
    def arrowhead(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ARROWHEAD, value)

    @property
    def WIDTH(self) -> int:
        """WIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.WIDTH)
        _value = cast(int, value)
        return _value

    @WIDTH.setter
    def WIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.WIDTH, value)

    @property
    def width(self) -> int:
        """WIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'width' and 'WIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.WIDTH)
        _value = cast(int, value)
        return _value

    @width.setter
    def width(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.WIDTH, value)

    @property
    def LABELTEXTID(self) -> int:
        """LABELTEXTID property
        
        Label text id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELTEXTID)
        _value = cast(int, value)
        return _value

    @LABELTEXTID.setter
    def LABELTEXTID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELTEXTID, value)

    @property
    def labeltextid(self) -> int:
        """LABELTEXTID property
        
        Label text id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'labeltextid' and 'LABELTEXTID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELTEXTID)
        _value = cast(int, value)
        return _value

    @labeltextid.setter
    def labeltextid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELTEXTID, value)

    @property
    def LOCATIONX1(self) -> float:
        """LOCATIONX1 property
        
        X 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONX1)
        _value = cast(float, value)
        return _value

    @LOCATIONX1.setter
    def LOCATIONX1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONX1, value)

    @property
    def locationx1(self) -> float:
        """LOCATIONX1 property
        
        X 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'locationx1' and 'LOCATIONX1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONX1)
        _value = cast(float, value)
        return _value

    @locationx1.setter
    def locationx1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONX1, value)

    @property
    def LOCATIONY1(self) -> float:
        """LOCATIONY1 property
        
        Y 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONY1)
        _value = cast(float, value)
        return _value

    @LOCATIONY1.setter
    def LOCATIONY1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONY1, value)

    @property
    def locationy1(self) -> float:
        """LOCATIONY1 property
        
        Y 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'locationy1' and 'LOCATIONY1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONY1)
        _value = cast(float, value)
        return _value

    @locationy1.setter
    def locationy1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONY1, value)

    @property
    def LOCATIONX2(self) -> float:
        """LOCATIONX2 property
        
        X 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONX2)
        _value = cast(float, value)
        return _value

    @LOCATIONX2.setter
    def LOCATIONX2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONX2, value)

    @property
    def locationx2(self) -> float:
        """LOCATIONX2 property
        
        X 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'locationx2' and 'LOCATIONX2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONX2)
        _value = cast(float, value)
        return _value

    @locationx2.setter
    def locationx2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONX2, value)

    @property
    def LOCATIONY2(self) -> float:
        """LOCATIONY2 property
        
        Y 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONY2)
        _value = cast(float, value)
        return _value

    @LOCATIONY2.setter
    def LOCATIONY2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONY2, value)

    @property
    def locationy2(self) -> float:
        """LOCATIONY2 property
        
        Y 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'locationy2' and 'LOCATIONY2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATIONY2)
        _value = cast(float, value)
        return _value

    @locationy2.setter
    def locationy2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCATIONY2, value)

    @property
    def RELATIVEVIEWPORT1(self) -> int:
        """RELATIVEVIEWPORT1 property
        
        Relative viewport 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.OPTION_NONE - all
            * ensight.objs.enums.VPORT_0 - 0
            * ensight.objs.enums.VPORT_1 - 1
            * ensight.objs.enums.VPORT_2 - 2
            * ensight.objs.enums.VPORT_3 - 3
            * ensight.objs.enums.VPORT_4 - 4
            * ensight.objs.enums.VPORT_5 - 5
            * ensight.objs.enums.VPORT_6 - 6
            * ensight.objs.enums.VPORT_7 - 7
            * ensight.objs.enums.VPORT_8 - 8
            * ensight.objs.enums.VPORT_9 - 9
            * ensight.objs.enums.VPORT_10 - 10
            * ensight.objs.enums.VPORT_11 - 11
            * ensight.objs.enums.VPORT_12 - 12
            * ensight.objs.enums.VPORT_13 - 13
            * ensight.objs.enums.VPORT_14 - 14
            * ensight.objs.enums.VPORT_15 - 15
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT1)
        _value = cast(int, value)
        return _value

    @RELATIVEVIEWPORT1.setter
    def RELATIVEVIEWPORT1(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT1, value)

    @property
    def relativeviewport1(self) -> int:
        """RELATIVEVIEWPORT1 property
        
        Relative viewport 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.OPTION_NONE - all
            * ensight.objs.enums.VPORT_0 - 0
            * ensight.objs.enums.VPORT_1 - 1
            * ensight.objs.enums.VPORT_2 - 2
            * ensight.objs.enums.VPORT_3 - 3
            * ensight.objs.enums.VPORT_4 - 4
            * ensight.objs.enums.VPORT_5 - 5
            * ensight.objs.enums.VPORT_6 - 6
            * ensight.objs.enums.VPORT_7 - 7
            * ensight.objs.enums.VPORT_8 - 8
            * ensight.objs.enums.VPORT_9 - 9
            * ensight.objs.enums.VPORT_10 - 10
            * ensight.objs.enums.VPORT_11 - 11
            * ensight.objs.enums.VPORT_12 - 12
            * ensight.objs.enums.VPORT_13 - 13
            * ensight.objs.enums.VPORT_14 - 14
            * ensight.objs.enums.VPORT_15 - 15
        
        Note: both 'relativeviewport1' and 'RELATIVEVIEWPORT1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT1)
        _value = cast(int, value)
        return _value

    @relativeviewport1.setter
    def relativeviewport1(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT1, value)

    @property
    def RELATIVEVIEWPORT2(self) -> int:
        """RELATIVEVIEWPORT2 property
        
        Relative viewport 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.OPTION_NONE - all
            * ensight.objs.enums.VPORT_0 - 0
            * ensight.objs.enums.VPORT_1 - 1
            * ensight.objs.enums.VPORT_2 - 2
            * ensight.objs.enums.VPORT_3 - 3
            * ensight.objs.enums.VPORT_4 - 4
            * ensight.objs.enums.VPORT_5 - 5
            * ensight.objs.enums.VPORT_6 - 6
            * ensight.objs.enums.VPORT_7 - 7
            * ensight.objs.enums.VPORT_8 - 8
            * ensight.objs.enums.VPORT_9 - 9
            * ensight.objs.enums.VPORT_10 - 10
            * ensight.objs.enums.VPORT_11 - 11
            * ensight.objs.enums.VPORT_12 - 12
            * ensight.objs.enums.VPORT_13 - 13
            * ensight.objs.enums.VPORT_14 - 14
            * ensight.objs.enums.VPORT_15 - 15
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT2)
        _value = cast(int, value)
        return _value

    @RELATIVEVIEWPORT2.setter
    def RELATIVEVIEWPORT2(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT2, value)

    @property
    def relativeviewport2(self) -> int:
        """RELATIVEVIEWPORT2 property
        
        Relative viewport 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.OPTION_NONE - all
            * ensight.objs.enums.VPORT_0 - 0
            * ensight.objs.enums.VPORT_1 - 1
            * ensight.objs.enums.VPORT_2 - 2
            * ensight.objs.enums.VPORT_3 - 3
            * ensight.objs.enums.VPORT_4 - 4
            * ensight.objs.enums.VPORT_5 - 5
            * ensight.objs.enums.VPORT_6 - 6
            * ensight.objs.enums.VPORT_7 - 7
            * ensight.objs.enums.VPORT_8 - 8
            * ensight.objs.enums.VPORT_9 - 9
            * ensight.objs.enums.VPORT_10 - 10
            * ensight.objs.enums.VPORT_11 - 11
            * ensight.objs.enums.VPORT_12 - 12
            * ensight.objs.enums.VPORT_13 - 13
            * ensight.objs.enums.VPORT_14 - 14
            * ensight.objs.enums.VPORT_15 - 15
        
        Note: both 'relativeviewport2' and 'RELATIVEVIEWPORT2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT2)
        _value = cast(int, value)
        return _value

    @relativeviewport2.setter
    def relativeviewport2(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RELATIVEVIEWPORT2, value)

    @property
    def ORIGIN1(self) -> List[float]:
        """ORIGIN1 property
        
        Origin 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN1)
        _value = cast(List[float], value)
        return _value

    @ORIGIN1.setter
    def ORIGIN1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN1, value)

    @property
    def origin1(self) -> List[float]:
        """ORIGIN1 property
        
        Origin 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'origin1' and 'ORIGIN1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN1)
        _value = cast(List[float], value)
        return _value

    @origin1.setter
    def origin1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN1, value)

    @property
    def ORIGIN2(self) -> List[float]:
        """ORIGIN2 property
        
        Origin 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN2)
        _value = cast(List[float], value)
        return _value

    @ORIGIN2.setter
    def ORIGIN2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN2, value)

    @property
    def origin2(self) -> List[float]:
        """ORIGIN2 property
        
        Origin 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'origin2' and 'ORIGIN2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN2)
        _value = cast(List[float], value)
        return _value

    @origin2.setter
    def origin2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN2, value)

    @property
    def ORIGINBY2(self) -> int:
        """ORIGINBY2 property
        
        Origin by 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNOT_2D_SPACE - screen_coords
            * ensight.objs.enums.ANNOT_3D_SPACE - 3d_coords
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINBY2)
        _value = cast(int, value)
        return _value

    @ORIGINBY2.setter
    def ORIGINBY2(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINBY2, value)

    @property
    def originby2(self) -> int:
        """ORIGINBY2 property
        
        Origin by 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNOT_2D_SPACE - screen_coords
            * ensight.objs.enums.ANNOT_3D_SPACE - 3d_coords
        
        Note: both 'originby2' and 'ORIGINBY2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINBY2)
        _value = cast(int, value)
        return _value

    @originby2.setter
    def originby2(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINBY2, value)

    @property
    def ORIGINBY1(self) -> int:
        """ORIGINBY1 property
        
        Origin by 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNOT_2D_SPACE - screen_coords
            * ensight.objs.enums.ANNOT_3D_SPACE - 3d_coords
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINBY1)
        _value = cast(int, value)
        return _value

    @ORIGINBY1.setter
    def ORIGINBY1(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINBY1, value)

    @property
    def originby1(self) -> int:
        """ORIGINBY1 property
        
        Origin by 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ANNOT_2D_SPACE - screen_coords
            * ensight.objs.enums.ANNOT_3D_SPACE - 3d_coords
        
        Note: both 'originby1' and 'ORIGINBY1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINBY1)
        _value = cast(int, value)
        return _value

    @originby1.setter
    def originby1(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINBY1, value)

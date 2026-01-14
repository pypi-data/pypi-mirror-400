"""ens_camera module

The ens_camera module provides a proxy interface to EnSight ENS_CAMERA instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_CAMERA(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_CAMERA

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
    def VISIBLE(self) -> int:
        """VISIBLE property
        
        visible
        
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
        
        visible
        
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
    def LENS(self) -> int:
        """LENS property
        
        lens type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CAMERA_LENS_NORMAL - normal
            * ensight.objs.enums.CAMERA_LENS_VIEW_PYRAMID - view pyramid
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LENS)
        _value = cast(int, value)
        return _value

    @LENS.setter
    def LENS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LENS, value)

    @property
    def lens(self) -> int:
        """LENS property
        
        lens type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CAMERA_LENS_NORMAL - normal
            * ensight.objs.enums.CAMERA_LENS_VIEW_PYRAMID - view pyramid
        
        Note: both 'lens' and 'LENS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LENS)
        _value = cast(int, value)
        return _value

    @lens.setter
    def lens(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LENS, value)

    @property
    def ANGLE(self) -> float:
        """ANGLE property
        
        perspective angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANGLE)
        _value = cast(float, value)
        return _value

    @ANGLE.setter
    def ANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANGLE, value)

    @property
    def angle(self) -> float:
        """ANGLE property
        
        perspective angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'angle' and 'ANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANGLE)
        _value = cast(float, value)
        return _value

    @angle.setter
    def angle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANGLE, value)

    @property
    def CLIP(self) -> int:
        """CLIP property
        
        view pyramid clipping
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIP)
        _value = cast(int, value)
        return _value

    @CLIP.setter
    def CLIP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIP, value)

    @property
    def clip(self) -> int:
        """CLIP property
        
        view pyramid clipping
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'clip' and 'CLIP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIP)
        _value = cast(int, value)
        return _value

    @clip.setter
    def clip(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIP, value)

    @property
    def LOOKAT_OPTION(self) -> int:
        """LOOKAT_OPTION property
        
        lookat option
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CAMERA_LOOK_AT_FORWARD - forward
            * ensight.objs.enums.CAMERA_LOOK_AT_NODE - node
            * ensight.objs.enums.CAMERA_LOOK_AT_XYZ - xyz
            * ensight.objs.enums.CAMERA_LOOK_AT_SPLINE - spline
            * ensight.objs.enums.CAMERA_LOOK_AT_PLANE_TOOL - plane tool
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_OPTION)
        _value = cast(int, value)
        return _value

    @LOOKAT_OPTION.setter
    def LOOKAT_OPTION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_OPTION, value)

    @property
    def lookat_option(self) -> int:
        """LOOKAT_OPTION property
        
        lookat option
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CAMERA_LOOK_AT_FORWARD - forward
            * ensight.objs.enums.CAMERA_LOOK_AT_NODE - node
            * ensight.objs.enums.CAMERA_LOOK_AT_XYZ - xyz
            * ensight.objs.enums.CAMERA_LOOK_AT_SPLINE - spline
            * ensight.objs.enums.CAMERA_LOOK_AT_PLANE_TOOL - plane tool
        
        Note: both 'lookat_option' and 'LOOKAT_OPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_OPTION)
        _value = cast(int, value)
        return _value

    @lookat_option.setter
    def lookat_option(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_OPTION, value)

    @property
    def LOOKAT_PART_ID(self) -> int:
        """LOOKAT_PART_ID property
        
        lookat part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_PART_ID)
        _value = cast(int, value)
        return _value

    @LOOKAT_PART_ID.setter
    def LOOKAT_PART_ID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_PART_ID, value)

    @property
    def lookat_part_id(self) -> int:
        """LOOKAT_PART_ID property
        
        lookat part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'lookat_part_id' and 'LOOKAT_PART_ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_PART_ID)
        _value = cast(int, value)
        return _value

    @lookat_part_id.setter
    def lookat_part_id(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_PART_ID, value)

    @property
    def LOOKAT_NODE_ID(self) -> int:
        """LOOKAT_NODE_ID property
        
        lookat node id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_NODE_ID)
        _value = cast(int, value)
        return _value

    @LOOKAT_NODE_ID.setter
    def LOOKAT_NODE_ID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_NODE_ID, value)

    @property
    def lookat_node_id(self) -> int:
        """LOOKAT_NODE_ID property
        
        lookat node id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'lookat_node_id' and 'LOOKAT_NODE_ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_NODE_ID)
        _value = cast(int, value)
        return _value

    @lookat_node_id.setter
    def lookat_node_id(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_NODE_ID, value)

    @property
    def LOOKAT_SPLINE_ID(self) -> int:
        """LOOKAT_SPLINE_ID property
        
        lookat spline id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_ID)
        _value = cast(int, value)
        return _value

    @LOOKAT_SPLINE_ID.setter
    def LOOKAT_SPLINE_ID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_ID, value)

    @property
    def lookat_spline_id(self) -> int:
        """LOOKAT_SPLINE_ID property
        
        lookat spline id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'lookat_spline_id' and 'LOOKAT_SPLINE_ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_ID)
        _value = cast(int, value)
        return _value

    @lookat_spline_id.setter
    def lookat_spline_id(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_ID, value)

    @property
    def LOOKAT_SPLINE_VALUE(self) -> float:
        """LOOKAT_SPLINE_VALUE property
        
        lookat spline value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_VALUE)
        _value = cast(float, value)
        return _value

    @LOOKAT_SPLINE_VALUE.setter
    def LOOKAT_SPLINE_VALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_VALUE, value)

    @property
    def lookat_spline_value(self) -> float:
        """LOOKAT_SPLINE_VALUE property
        
        lookat spline value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'lookat_spline_value' and 'LOOKAT_SPLINE_VALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_VALUE)
        _value = cast(float, value)
        return _value

    @lookat_spline_value.setter
    def lookat_spline_value(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_SPLINE_VALUE, value)

    @property
    def LOOKAT_XYZ(self) -> List[float]:
        """LOOKAT_XYZ property
        
        lookat location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_XYZ)
        _value = cast(List[float], value)
        return _value

    @LOOKAT_XYZ.setter
    def LOOKAT_XYZ(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_XYZ, value)

    @property
    def lookat_xyz(self) -> List[float]:
        """LOOKAT_XYZ property
        
        lookat location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'lookat_xyz' and 'LOOKAT_XYZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKAT_XYZ)
        _value = cast(List[float], value)
        return _value

    @lookat_xyz.setter
    def lookat_xyz(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKAT_XYZ, value)

    @property
    def ORIGIN_OPTION(self) -> int:
        """ORIGIN_OPTION property
        
        origin option
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CAMERA_LOOK_FROM_NODE - node
            * ensight.objs.enums.CAMERA_LOOK_FROM_XYZ - xyz
            * ensight.objs.enums.CAMERA_LOOK_FROM_SPLINE - spline
            * ensight.objs.enums.CAMERA_LOOK_FROM_PLANE_TOOL - plane tool
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_OPTION)
        _value = cast(int, value)
        return _value

    @ORIGIN_OPTION.setter
    def ORIGIN_OPTION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_OPTION, value)

    @property
    def origin_option(self) -> int:
        """ORIGIN_OPTION property
        
        origin option
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CAMERA_LOOK_FROM_NODE - node
            * ensight.objs.enums.CAMERA_LOOK_FROM_XYZ - xyz
            * ensight.objs.enums.CAMERA_LOOK_FROM_SPLINE - spline
            * ensight.objs.enums.CAMERA_LOOK_FROM_PLANE_TOOL - plane tool
        
        Note: both 'origin_option' and 'ORIGIN_OPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_OPTION)
        _value = cast(int, value)
        return _value

    @origin_option.setter
    def origin_option(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_OPTION, value)

    @property
    def ORIGIN_PART_ID(self) -> int:
        """ORIGIN_PART_ID property
        
        origin part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_PART_ID)
        _value = cast(int, value)
        return _value

    @ORIGIN_PART_ID.setter
    def ORIGIN_PART_ID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_PART_ID, value)

    @property
    def origin_part_id(self) -> int:
        """ORIGIN_PART_ID property
        
        origin part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'origin_part_id' and 'ORIGIN_PART_ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_PART_ID)
        _value = cast(int, value)
        return _value

    @origin_part_id.setter
    def origin_part_id(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_PART_ID, value)

    @property
    def ORIGIN_NODE_ID(self) -> int:
        """ORIGIN_NODE_ID property
        
        origin node id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_NODE_ID)
        _value = cast(int, value)
        return _value

    @ORIGIN_NODE_ID.setter
    def ORIGIN_NODE_ID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_NODE_ID, value)

    @property
    def origin_node_id(self) -> int:
        """ORIGIN_NODE_ID property
        
        origin node id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'origin_node_id' and 'ORIGIN_NODE_ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_NODE_ID)
        _value = cast(int, value)
        return _value

    @origin_node_id.setter
    def origin_node_id(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_NODE_ID, value)

    @property
    def ORIGIN_SPLINE_ID(self) -> int:
        """ORIGIN_SPLINE_ID property
        
        origin spline id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_ID)
        _value = cast(int, value)
        return _value

    @ORIGIN_SPLINE_ID.setter
    def ORIGIN_SPLINE_ID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_ID, value)

    @property
    def origin_spline_id(self) -> int:
        """ORIGIN_SPLINE_ID property
        
        origin spline id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'origin_spline_id' and 'ORIGIN_SPLINE_ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_ID)
        _value = cast(int, value)
        return _value

    @origin_spline_id.setter
    def origin_spline_id(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_ID, value)

    @property
    def ORIGIN_SPLINE_VALUE(self) -> float:
        """ORIGIN_SPLINE_VALUE property
        
        origin spline value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_VALUE)
        _value = cast(float, value)
        return _value

    @ORIGIN_SPLINE_VALUE.setter
    def ORIGIN_SPLINE_VALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_VALUE, value)

    @property
    def origin_spline_value(self) -> float:
        """ORIGIN_SPLINE_VALUE property
        
        origin spline value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'origin_spline_value' and 'ORIGIN_SPLINE_VALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_VALUE)
        _value = cast(float, value)
        return _value

    @origin_spline_value.setter
    def origin_spline_value(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_SPLINE_VALUE, value)

    @property
    def ORIGIN_XYZ_DELTA(self) -> List[float]:
        """ORIGIN_XYZ_DELTA property
        
        origin location delta
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_XYZ_DELTA)
        _value = cast(List[float], value)
        return _value

    @ORIGIN_XYZ_DELTA.setter
    def ORIGIN_XYZ_DELTA(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_XYZ_DELTA, value)

    @property
    def origin_xyz_delta(self) -> List[float]:
        """ORIGIN_XYZ_DELTA property
        
        origin location delta
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'origin_xyz_delta' and 'ORIGIN_XYZ_DELTA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN_XYZ_DELTA)
        _value = cast(List[float], value)
        return _value

    @origin_xyz_delta.setter
    def origin_xyz_delta(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN_XYZ_DELTA, value)

    @property
    def DISTANCE_SCALE(self) -> float:
        """DISTANCE_SCALE property
        
        distance scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DISTANCE_SCALE)
        _value = cast(float, value)
        return _value

    @DISTANCE_SCALE.setter
    def DISTANCE_SCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DISTANCE_SCALE, value)

    @property
    def distance_scale(self) -> float:
        """DISTANCE_SCALE property
        
        distance scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'distance_scale' and 'DISTANCE_SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DISTANCE_SCALE)
        _value = cast(float, value)
        return _value

    @distance_scale.setter
    def distance_scale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DISTANCE_SCALE, value)

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
    def VIEWPORT_USE(self) -> List[int]:
        """VIEWPORT_USE property
        
        use in viewports
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, 16 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VIEWPORT_USE)
        _value = cast(List[int], value)
        return _value

    @VIEWPORT_USE.setter
    def VIEWPORT_USE(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.VIEWPORT_USE, value)

    @property
    def viewport_use(self) -> List[int]:
        """VIEWPORT_USE property
        
        use in viewports
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, 16 element array
        
        Note: both 'viewport_use' and 'VIEWPORT_USE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VIEWPORT_USE)
        _value = cast(List[int], value)
        return _value

    @viewport_use.setter
    def viewport_use(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.VIEWPORT_USE, value)

    @property
    def TOOL_ORIENTATION(self) -> List[float]:
        """TOOL_ORIENTATION property
        
        tool orientation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 9 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TOOL_ORIENTATION)
        _value = cast(List[float], value)
        return _value

    @TOOL_ORIENTATION.setter
    def TOOL_ORIENTATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TOOL_ORIENTATION, value)

    @property
    def tool_orientation(self) -> List[float]:
        """TOOL_ORIENTATION property
        
        tool orientation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 9 element array
        
        Note: both 'tool_orientation' and 'TOOL_ORIENTATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TOOL_ORIENTATION)
        _value = cast(List[float], value)
        return _value

    @tool_orientation.setter
    def tool_orientation(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TOOL_ORIENTATION, value)

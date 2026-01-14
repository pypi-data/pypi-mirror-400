"""ens_scene module

The ens_scene module provides a proxy interface to EnSight ENS_SCENE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_SCENE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_SCENE

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
    def ACTIVE(self) -> int:
        """ACTIVE property
        
        scene active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ACTIVE)
        _value = cast(int, value)
        return _value

    @ACTIVE.setter
    def ACTIVE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ACTIVE, value)

    @property
    def active(self) -> int:
        """ACTIVE property
        
        scene active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'active' and 'ACTIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ACTIVE)
        _value = cast(int, value)
        return _value

    @active.setter
    def active(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ACTIVE, value)

    @property
    def LOCATION(self) -> List[float]:
        """LOCATION property
        
        scene origin
        
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
        
        scene origin
        
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
        
        scene radius
        
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
        
        scene radius
        
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
    def RADIUS_SCALE(self) -> float:
        """RADIUS_SCALE property
        
        scene radius scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RADIUS_SCALE)
        _value = cast(float, value)
        return _value

    @RADIUS_SCALE.setter
    def RADIUS_SCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.RADIUS_SCALE, value)

    @property
    def radius_scale(self) -> float:
        """RADIUS_SCALE property
        
        scene radius scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'radius_scale' and 'RADIUS_SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RADIUS_SCALE)
        _value = cast(float, value)
        return _value

    @radius_scale.setter
    def radius_scale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.RADIUS_SCALE, value)

    @property
    def LIGHT_ENV_TEXNUM(self) -> int:
        """LIGHT_ENV_TEXNUM property
        
        for environment light source: index of HDR images
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_ENV_TEXNUM)
        _value = cast(int, value)
        return _value

    @LIGHT_ENV_TEXNUM.setter
    def LIGHT_ENV_TEXNUM(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_ENV_TEXNUM, value)

    @property
    def light_env_texnum(self) -> int:
        """LIGHT_ENV_TEXNUM property
        
        for environment light source: index of HDR images
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'light_env_texnum' and 'LIGHT_ENV_TEXNUM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_ENV_TEXNUM)
        _value = cast(int, value)
        return _value

    @light_env_texnum.setter
    def light_env_texnum(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_ENV_TEXNUM, value)

    @property
    def SHOW_LOCATION(self) -> int:
        """SHOW_LOCATION property
        
        show scene's center location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOW_LOCATION)
        _value = cast(int, value)
        return _value

    @SHOW_LOCATION.setter
    def SHOW_LOCATION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOW_LOCATION, value)

    @property
    def show_location(self) -> int:
        """SHOW_LOCATION property
        
        show scene's center location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'show_location' and 'SHOW_LOCATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOW_LOCATION)
        _value = cast(int, value)
        return _value

    @show_location.setter
    def show_location(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOW_LOCATION, value)

    @property
    def GROUND_ACTIVE(self) -> int:
        """GROUND_ACTIVE property
        
        show ground plane
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_ACTIVE)
        _value = cast(int, value)
        return _value

    @GROUND_ACTIVE.setter
    def GROUND_ACTIVE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_ACTIVE, value)

    @property
    def ground_active(self) -> int:
        """GROUND_ACTIVE property
        
        show ground plane
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'ground_active' and 'GROUND_ACTIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_ACTIVE)
        _value = cast(int, value)
        return _value

    @ground_active.setter
    def ground_active(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_ACTIVE, value)

    @property
    def GROUND_UPDIR(self) -> int:
        """GROUND_UPDIR property
        
        ground plane's up vector enum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.UPVEC_X - x axis
            * ensight.objs.enums.UPVEC_NX - -x axis
            * ensight.objs.enums.UPVEC_Y - y axis
            * ensight.objs.enums.UPVEC_NY - -y axis
            * ensight.objs.enums.UPVEC_Z - z axis
            * ensight.objs.enums.UPVEC_NZ - -z axis
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_UPDIR)
        _value = cast(int, value)
        return _value

    @GROUND_UPDIR.setter
    def GROUND_UPDIR(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_UPDIR, value)

    @property
    def ground_updir(self) -> int:
        """GROUND_UPDIR property
        
        ground plane's up vector enum
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.UPVEC_X - x axis
            * ensight.objs.enums.UPVEC_NX - -x axis
            * ensight.objs.enums.UPVEC_Y - y axis
            * ensight.objs.enums.UPVEC_NY - -y axis
            * ensight.objs.enums.UPVEC_Z - z axis
            * ensight.objs.enums.UPVEC_NZ - -z axis
        
        Note: both 'ground_updir' and 'GROUND_UPDIR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_UPDIR)
        _value = cast(int, value)
        return _value

    @ground_updir.setter
    def ground_updir(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_UPDIR, value)

    @property
    def GROUND_BLENDSCALE(self) -> float:
        """GROUND_BLENDSCALE property
        
        ground plane's blending scale factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_BLENDSCALE)
        _value = cast(float, value)
        return _value

    @GROUND_BLENDSCALE.setter
    def GROUND_BLENDSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_BLENDSCALE, value)

    @property
    def ground_blendscale(self) -> float:
        """GROUND_BLENDSCALE property
        
        ground plane's blending scale factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'ground_blendscale' and 'GROUND_BLENDSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_BLENDSCALE)
        _value = cast(float, value)
        return _value

    @ground_blendscale.setter
    def ground_blendscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_BLENDSCALE, value)

    @property
    def GROUND_TEXSCALE(self) -> float:
        """GROUND_TEXSCALE property
        
        ground plane's texture scale factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_TEXSCALE)
        _value = cast(float, value)
        return _value

    @GROUND_TEXSCALE.setter
    def GROUND_TEXSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_TEXSCALE, value)

    @property
    def ground_texscale(self) -> float:
        """GROUND_TEXSCALE property
        
        ground plane's texture scale factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'ground_texscale' and 'GROUND_TEXSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_TEXSCALE)
        _value = cast(float, value)
        return _value

    @ground_texscale.setter
    def ground_texscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_TEXSCALE, value)

    @property
    def GROUND_GRIDSCALE(self) -> float:
        """GROUND_GRIDSCALE property
        
        ground plane's grid scale factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_GRIDSCALE)
        _value = cast(float, value)
        return _value

    @GROUND_GRIDSCALE.setter
    def GROUND_GRIDSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_GRIDSCALE, value)

    @property
    def ground_gridscale(self) -> float:
        """GROUND_GRIDSCALE property
        
        ground plane's grid scale factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'ground_gridscale' and 'GROUND_GRIDSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_GRIDSCALE)
        _value = cast(float, value)
        return _value

    @ground_gridscale.setter
    def ground_gridscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_GRIDSCALE, value)

    @property
    def GROUND_COLOR(self) -> List[float]:
        """GROUND_COLOR property
        
        ground plane's color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_COLOR)
        _value = cast(List[float], value)
        return _value

    @GROUND_COLOR.setter
    def GROUND_COLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_COLOR, value)

    @property
    def ground_color(self) -> List[float]:
        """GROUND_COLOR property
        
        ground plane's color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'ground_color' and 'GROUND_COLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_COLOR)
        _value = cast(List[float], value)
        return _value

    @ground_color.setter
    def ground_color(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_COLOR, value)

    @property
    def GROUND_GRIDCOLORA(self) -> List[float]:
        """GROUND_GRIDCOLORA property
        
        ground plane's gridcolor A
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORA)
        _value = cast(List[float], value)
        return _value

    @GROUND_GRIDCOLORA.setter
    def GROUND_GRIDCOLORA(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORA, value)

    @property
    def ground_gridcolora(self) -> List[float]:
        """GROUND_GRIDCOLORA property
        
        ground plane's gridcolor A
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'ground_gridcolora' and 'GROUND_GRIDCOLORA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORA)
        _value = cast(List[float], value)
        return _value

    @ground_gridcolora.setter
    def ground_gridcolora(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORA, value)

    @property
    def GROUND_GRIDCOLORB(self) -> List[float]:
        """GROUND_GRIDCOLORB property
        
        ground plane's gridcolor B
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORB)
        _value = cast(List[float], value)
        return _value

    @GROUND_GRIDCOLORB.setter
    def GROUND_GRIDCOLORB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORB, value)

    @property
    def ground_gridcolorb(self) -> List[float]:
        """GROUND_GRIDCOLORB property
        
        ground plane's gridcolor B
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'ground_gridcolorb' and 'GROUND_GRIDCOLORB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORB)
        _value = cast(List[float], value)
        return _value

    @ground_gridcolorb.setter
    def ground_gridcolorb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_GRIDCOLORB, value)

    @property
    def GROUND_HASREFL(self) -> int:
        """GROUND_HASREFL property
        
        ground plane receives reflection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASREFL)
        _value = cast(int, value)
        return _value

    @GROUND_HASREFL.setter
    def GROUND_HASREFL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASREFL, value)

    @property
    def ground_hasrefl(self) -> int:
        """GROUND_HASREFL property
        
        ground plane receives reflection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'ground_hasrefl' and 'GROUND_HASREFL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASREFL)
        _value = cast(int, value)
        return _value

    @ground_hasrefl.setter
    def ground_hasrefl(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASREFL, value)

    @property
    def GROUND_HASSHADOW(self) -> int:
        """GROUND_HASSHADOW property
        
        ground plane receives shadow
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASSHADOW)
        _value = cast(int, value)
        return _value

    @GROUND_HASSHADOW.setter
    def GROUND_HASSHADOW(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASSHADOW, value)

    @property
    def ground_hasshadow(self) -> int:
        """GROUND_HASSHADOW property
        
        ground plane receives shadow
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'ground_hasshadow' and 'GROUND_HASSHADOW' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASSHADOW)
        _value = cast(int, value)
        return _value

    @ground_hasshadow.setter
    def ground_hasshadow(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASSHADOW, value)

    @property
    def GROUND_LOCK(self) -> int:
        """GROUND_LOCK property
        
        ground plane lock plane parameters
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_LOCK)
        _value = cast(int, value)
        return _value

    @GROUND_LOCK.setter
    def GROUND_LOCK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_LOCK, value)

    @property
    def ground_lock(self) -> int:
        """GROUND_LOCK property
        
        ground plane lock plane parameters
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'ground_lock' and 'GROUND_LOCK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_LOCK)
        _value = cast(int, value)
        return _value

    @ground_lock.setter
    def ground_lock(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_LOCK, value)

    @property
    def GROUND_HASTEXTURE(self) -> int:
        """GROUND_HASTEXTURE property
        
        ground plane has texture
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASTEXTURE)
        _value = cast(int, value)
        return _value

    @GROUND_HASTEXTURE.setter
    def GROUND_HASTEXTURE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASTEXTURE, value)

    @property
    def ground_hastexture(self) -> int:
        """GROUND_HASTEXTURE property
        
        ground plane has texture
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'ground_hastexture' and 'GROUND_HASTEXTURE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASTEXTURE)
        _value = cast(int, value)
        return _value

    @ground_hastexture.setter
    def ground_hastexture(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASTEXTURE, value)

    @property
    def GROUND_HASGRID(self) -> int:
        """GROUND_HASGRID property
        
        ground plane has grid lines
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASGRID)
        _value = cast(int, value)
        return _value

    @GROUND_HASGRID.setter
    def GROUND_HASGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASGRID, value)

    @property
    def ground_hasgrid(self) -> int:
        """GROUND_HASGRID property
        
        ground plane has grid lines
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'ground_hasgrid' and 'GROUND_HASGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HASGRID)
        _value = cast(int, value)
        return _value

    @ground_hasgrid.setter
    def ground_hasgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HASGRID, value)

    @property
    def GROUND_HEIGHTOFFSET(self) -> float:
        """GROUND_HEIGHTOFFSET property
        
        ground plane's height offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HEIGHTOFFSET)
        _value = cast(float, value)
        return _value

    @GROUND_HEIGHTOFFSET.setter
    def GROUND_HEIGHTOFFSET(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HEIGHTOFFSET, value)

    @property
    def ground_heightoffset(self) -> float:
        """GROUND_HEIGHTOFFSET property
        
        ground plane's height offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'ground_heightoffset' and 'GROUND_HEIGHTOFFSET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_HEIGHTOFFSET)
        _value = cast(float, value)
        return _value

    @ground_heightoffset.setter
    def ground_heightoffset(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_HEIGHTOFFSET, value)

    @property
    def GROUND_SAVEDINFO(self) -> List[float]:
        """GROUND_SAVEDINFO property
        
        ground plane saved plane parameters
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 160 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_SAVEDINFO)
        _value = cast(List[float], value)
        return _value

    @GROUND_SAVEDINFO.setter
    def GROUND_SAVEDINFO(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_SAVEDINFO, value)

    @property
    def ground_savedinfo(self) -> List[float]:
        """GROUND_SAVEDINFO property
        
        ground plane saved plane parameters
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 160 element array
        
        Note: both 'ground_savedinfo' and 'GROUND_SAVEDINFO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUND_SAVEDINFO)
        _value = cast(List[float], value)
        return _value

    @ground_savedinfo.setter
    def ground_savedinfo(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GROUND_SAVEDINFO, value)

    @property
    def ENVMAP_SAVEDINFO(self) -> List[float]:
        """ENVMAP_SAVEDINFO property
        
        envmap saved rotation parameters
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 64 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENVMAP_SAVEDINFO)
        _value = cast(List[float], value)
        return _value

    @ENVMAP_SAVEDINFO.setter
    def ENVMAP_SAVEDINFO(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ENVMAP_SAVEDINFO, value)

    @property
    def envmap_savedinfo(self) -> List[float]:
        """ENVMAP_SAVEDINFO property
        
        envmap saved rotation parameters
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 64 element array
        
        Note: both 'envmap_savedinfo' and 'ENVMAP_SAVEDINFO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENVMAP_SAVEDINFO)
        _value = cast(List[float], value)
        return _value

    @envmap_savedinfo.setter
    def envmap_savedinfo(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ENVMAP_SAVEDINFO, value)

"""ens_lightsource module

The ens_lightsource module provides a proxy interface to EnSight ENS_LIGHTSOURCE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_LIGHTSOURCE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_LIGHTSOURCE

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

    def set_preset(self, *args, **kwargs) -> Any:
        """Set lighting preset
        
        Set up all light sources according to the specified predefined lighting scheme.
        
        Args:
            preset_name:
                The name of the preset to apply.
        
                * 'Camera lighting' - A directional light at the camera position
                * 'Three-point lighting' - A typical three-point lighting setup with one key light, one fill light and one back light
                * 'Top lighting' - Key light from the top
                * 'Back lighting' - Key light from the back
                * 'Spot lighting' - A spot light as key light from the right side
                * 'Shadow lighting' - A directional light casting shadow from top

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.set_preset({arg_string})"
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
        
        Description
        
        Supported operations:
            getattr
        Datatype:
            String, 80 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @property
    def description(self) -> str:
        """DESCRIPTION property
        
        Description
        
        Supported operations:
            getattr
        Datatype:
            String, 80 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @property
    def SELECTED(self) -> int:
        """SELECTED property
        
        light source selected
        
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
        
        light source selected
        
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
    def VISIBLE(self) -> int:
        """VISIBLE property
        
        light source visible
        
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
        
        light source visible
        
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
    def ACTIVE(self) -> int:
        """ACTIVE property
        
        light source active
        
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
        
        light source active
        
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
    def INDEX(self) -> int:
        """INDEX property
        
        light index
        
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
        
        light index
        
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
    def TRANSFORM_WITH_MODEL(self) -> int:
        """TRANSFORM_WITH_MODEL property
        
        light moves with model
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSFORM_WITH_MODEL)
        _value = cast(int, value)
        return _value

    @TRANSFORM_WITH_MODEL.setter
    def TRANSFORM_WITH_MODEL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSFORM_WITH_MODEL, value)

    @property
    def transform_with_model(self) -> int:
        """TRANSFORM_WITH_MODEL property
        
        light moves with model
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'transform_with_model' and 'TRANSFORM_WITH_MODEL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSFORM_WITH_MODEL)
        _value = cast(int, value)
        return _value

    @transform_with_model.setter
    def transform_with_model(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSFORM_WITH_MODEL, value)

    @property
    def LIGHT_TYPE(self) -> int:
        """LIGHT_TYPE property
        
        light type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LIGHT_DIRECTIONAL - directional
            * ensight.objs.enums.LIGHT_SPOT - spot
            * ensight.objs.enums.LIGHT_POINT - point
            * ensight.objs.enums.LIGHT_AREA_QUAD - quad
            * ensight.objs.enums.LIGHT_AT_CAMERA - directional
            * ensight.objs.enums.LIGHT_AREA_ENV - env
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_TYPE)
        _value = cast(int, value)
        return _value

    @LIGHT_TYPE.setter
    def LIGHT_TYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_TYPE, value)

    @property
    def light_type(self) -> int:
        """LIGHT_TYPE property
        
        light type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LIGHT_DIRECTIONAL - directional
            * ensight.objs.enums.LIGHT_SPOT - spot
            * ensight.objs.enums.LIGHT_POINT - point
            * ensight.objs.enums.LIGHT_AREA_QUAD - quad
            * ensight.objs.enums.LIGHT_AT_CAMERA - directional
            * ensight.objs.enums.LIGHT_AREA_ENV - env
        
        Note: both 'light_type' and 'LIGHT_TYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_TYPE)
        _value = cast(int, value)
        return _value

    @light_type.setter
    def light_type(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_TYPE, value)

    @property
    def DIRECTION(self) -> List[float]:
        """DIRECTION property
        
        light source direction
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        Range:
            [-1.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DIRECTION)
        _value = cast(List[float], value)
        return _value

    @DIRECTION.setter
    def DIRECTION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.DIRECTION, value)

    @property
    def direction(self) -> List[float]:
        """DIRECTION property
        
        light source direction
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        Range:
            [-1.0, 1.0]
        
        Note: both 'direction' and 'DIRECTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DIRECTION)
        _value = cast(List[float], value)
        return _value

    @direction.setter
    def direction(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.DIRECTION, value)

    @property
    def LOCATION(self) -> List[float]:
        """LOCATION property
        
        light source origin
        
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
        
        light source origin
        
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
    def CENTROID(self) -> List[float]:
        """CENTROID property
        
        light source centroid
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CENTROID)
        _value = cast(List[float], value)
        return _value

    @CENTROID.setter
    def CENTROID(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CENTROID, value)

    @property
    def centroid(self) -> List[float]:
        """CENTROID property
        
        light source centroid
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'centroid' and 'CENTROID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CENTROID)
        _value = cast(List[float], value)
        return _value

    @centroid.setter
    def centroid(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CENTROID, value)

    @property
    def SPOT_ANGLE(self) -> float:
        """SPOT_ANGLE property
        
        spotlight source angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 180.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPOT_ANGLE)
        _value = cast(float, value)
        return _value

    @SPOT_ANGLE.setter
    def SPOT_ANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SPOT_ANGLE, value)

    @property
    def spot_angle(self) -> float:
        """SPOT_ANGLE property
        
        spotlight source angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 180.0]
        
        Note: both 'spot_angle' and 'SPOT_ANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPOT_ANGLE)
        _value = cast(float, value)
        return _value

    @spot_angle.setter
    def spot_angle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SPOT_ANGLE, value)

    @property
    def SPOT_FALLOFF(self) -> float:
        """SPOT_FALLOFF property
        
        spotlight source falloff
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPOT_FALLOFF)
        _value = cast(float, value)
        return _value

    @SPOT_FALLOFF.setter
    def SPOT_FALLOFF(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SPOT_FALLOFF, value)

    @property
    def spot_falloff(self) -> float:
        """SPOT_FALLOFF property
        
        spotlight source falloff
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'spot_falloff' and 'SPOT_FALLOFF' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPOT_FALLOFF)
        _value = cast(float, value)
        return _value

    @spot_falloff.setter
    def spot_falloff(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SPOT_FALLOFF, value)

    @property
    def INTENSITY(self) -> float:
        """INTENSITY property
        
        light source intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.INTENSITY)
        _value = cast(float, value)
        return _value

    @INTENSITY.setter
    def INTENSITY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.INTENSITY, value)

    @property
    def intensity(self) -> float:
        """INTENSITY property
        
        light source intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'intensity' and 'INTENSITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.INTENSITY)
        _value = cast(float, value)
        return _value

    @intensity.setter
    def intensity(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.INTENSITY, value)

    @property
    def COLOR(self) -> List[float]:
        """COLOR property
        
        light source color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
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
        
        light source color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'color' and 'COLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COLOR)
        _value = cast(List[float], value)
        return _value

    @color.setter
    def color(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.COLOR, value)

    @property
    def CASTS_SHADOWS(self) -> int:
        """CASTS_SHADOWS property
        
        light casts shadows
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CASTS_SHADOWS)
        _value = cast(int, value)
        return _value

    @CASTS_SHADOWS.setter
    def CASTS_SHADOWS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CASTS_SHADOWS, value)

    @property
    def casts_shadows(self) -> int:
        """CASTS_SHADOWS property
        
        light casts shadows
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'casts_shadows' and 'CASTS_SHADOWS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CASTS_SHADOWS)
        _value = cast(int, value)
        return _value

    @casts_shadows.setter
    def casts_shadows(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CASTS_SHADOWS, value)

    @property
    def ICON_SIZE(self) -> float:
        """ICON_SIZE property
        
        light source icon size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ICON_SIZE)
        _value = cast(float, value)
        return _value

    @ICON_SIZE.setter
    def ICON_SIZE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ICON_SIZE, value)

    @property
    def icon_size(self) -> float:
        """ICON_SIZE property
        
        light source icon size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'icon_size' and 'ICON_SIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ICON_SIZE)
        _value = cast(float, value)
        return _value

    @icon_size.setter
    def icon_size(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ICON_SIZE, value)

    @property
    def RAY_END(self) -> List[float]:
        """RAY_END property
        
        light source directional intersection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RAY_END)
        _value = cast(List[float], value)
        return _value

    @RAY_END.setter
    def RAY_END(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RAY_END, value)

    @property
    def ray_end(self) -> List[float]:
        """RAY_END property
        
        light source directional intersection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'ray_end' and 'RAY_END' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RAY_END)
        _value = cast(List[float], value)
        return _value

    @ray_end.setter
    def ray_end(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RAY_END, value)

    @property
    def LOCK_DIRECTION(self) -> int:
        """LOCK_DIRECTION property
        
        light lock direction
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCK_DIRECTION)
        _value = cast(int, value)
        return _value

    @LOCK_DIRECTION.setter
    def LOCK_DIRECTION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCK_DIRECTION, value)

    @property
    def lock_direction(self) -> int:
        """LOCK_DIRECTION property
        
        light lock direction
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'lock_direction' and 'LOCK_DIRECTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCK_DIRECTION)
        _value = cast(int, value)
        return _value

    @lock_direction.setter
    def lock_direction(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LOCK_DIRECTION, value)

    @property
    def LIGHT_QUAD_XDIR(self) -> List[float]:
        """LIGHT_QUAD_XDIR property
        
        quad shape's x-axis in world for quad/environment light
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_QUAD_XDIR)
        _value = cast(List[float], value)
        return _value

    @LIGHT_QUAD_XDIR.setter
    def LIGHT_QUAD_XDIR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_QUAD_XDIR, value)

    @property
    def light_quad_xdir(self) -> List[float]:
        """LIGHT_QUAD_XDIR property
        
        quad shape's x-axis in world for quad/environment light
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'light_quad_xdir' and 'LIGHT_QUAD_XDIR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_QUAD_XDIR)
        _value = cast(List[float], value)
        return _value

    @light_quad_xdir.setter
    def light_quad_xdir(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_QUAD_XDIR, value)

    @property
    def LIGHT_QUAD_SIZE(self) -> List[float]:
        """LIGHT_QUAD_SIZE property
        
        quad shape's width/height for quad/environment light
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_QUAD_SIZE)
        _value = cast(List[float], value)
        return _value

    @LIGHT_QUAD_SIZE.setter
    def LIGHT_QUAD_SIZE(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_QUAD_SIZE, value)

    @property
    def light_quad_size(self) -> List[float]:
        """LIGHT_QUAD_SIZE property
        
        quad shape's width/height for quad/environment light
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'light_quad_size' and 'LIGHT_QUAD_SIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT_QUAD_SIZE)
        _value = cast(List[float], value)
        return _value

    @light_quad_size.setter
    def light_quad_size(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT_QUAD_SIZE, value)

    @property
    def LIGHT_ENV_TEXNUM(self) -> int:
        """LIGHT_ENV_TEXNUM property
        
        for environment light: index of HDR image list
        
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
        
        for environment light: index of HDR image list
        
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
    def PRESETS(self) -> object:
        """PRESETS property
        
        preset lighting names
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PRESETS)
        _value = cast(object, value)
        return _value

    @property
    def presets(self) -> object:
        """PRESETS property
        
        preset lighting names
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'presets' and 'PRESETS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PRESETS)
        _value = cast(object, value)
        return _value

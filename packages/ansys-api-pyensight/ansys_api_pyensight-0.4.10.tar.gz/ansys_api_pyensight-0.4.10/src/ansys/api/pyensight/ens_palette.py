"""ens_palette module

The ens_palette module provides a proxy interface to EnSight ENS_PALETTE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_PALETTE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_PALETTE

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

    def cmd_record(self, *args, **kwargs) -> Any:
        """Record a command

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.cmd_record({arg_string})"
        return self._session.cmd(cmd)

    def get_histogram(self, *args, **kwargs) -> Any:
        """Get a histogram

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_histogram({arg_string})"
        return self._session.cmd(cmd)

    def get_natural_texture_size(self, *args, **kwargs) -> Any:
        """Get the natural texture size

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_natural_texture_size({arg_string})"
        return self._session.cmd(cmd)

    def make_texture(self, *args, **kwargs) -> Any:
        """Make a texture

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.make_texture({arg_string})"
        return self._session.cmd(cmd)

    def set_minmax(self, *args, **kwargs) -> Any:
        """Set the min & max levels with option to record

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.set_minmax({arg_string})"
        return self._session.cmd(cmd)

    def set_point(self, *args, **kwargs) -> Any:
        """Set a point's position and value for a single channel

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.set_point({arg_string})"
        return self._session.cmd(cmd)

    def get_point(self, *args, **kwargs) -> Any:
        """Get a point's position and value for a single channel

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_point({arg_string})"
        return self._session.cmd(cmd)

    def get_end_point_colors(self, *args, **kwargs) -> Any:
        """Get colors of the end points

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_end_point_colors({arg_string})"
        return self._session.cmd(cmd)

    def invert_colors(self, *args, **kwargs) -> Any:
        """Invert the colors from min to max

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.invert_colors({arg_string})"
        return self._session.cmd(cmd)

    def reverse_levels(self, *args, **kwargs) -> Any:
        """Reverse the levels

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.reverse_levels({arg_string})"
        return self._session.cmd(cmd)

    def set_range_to_part_minmax(self, *args, **kwargs) -> Any:
        """Set the palette range to the min/max of the selected parts

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.set_range_to_part_minmax({arg_string})"
        return self._session.cmd(cmd)

    def set_range_to_viewport_minmax(self, *args, **kwargs) -> Any:
        """Set the palette range to the min/max of the parts in the current viewport

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.set_range_to_viewport_minmax({arg_string})"
        return self._session.cmd(cmd)

    def get_time_step_range(self, *args, **kwargs) -> Any:
        """Get the beginning and ending time steps

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_time_step_range({arg_string})"
        return self._session.cmd(cmd)

    def set_range_to_over_time_minmax(self, *args, **kwargs) -> Any:
        """Set the palette range to the min/max over time
        Function requires 2 arguments given: start timestep (int), and end timestep (int) 
        over which to determine the palette min/max values.
        
        Args:
            start timestep (int)  
            end timestep (int)
        
        Example:
            ::
            # Determine min/max range using timesteps 0 through 159
            ENS_PALETTE.set_range_to_over_time_minmax(0,159)
        
        Control the display and use of EnSight click and go handles for an object
        
        EnSight allows for direct interaction with many objects via click and go handles.
        The handles allow things like annotations and viewports to be moved or resized.
        They allow for the adjustment of values for clip planes and palette dynamic ranges.
        In some situations, allowing the user to directly adjust these values can be
        undesirable.  Setting this attribute to zero disables display of and interaction
        with click and go handles for the specific object instance.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.set_range_to_over_time_minmax({arg_string})"
        return self._session.cmd(cmd)

    def clear_last_marker(self, *args, **kwargs) -> Any:
        """Clear the last added marker

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.clear_last_marker({arg_string})"
        return self._session.cmd(cmd)

    def clear_all_markers(self, *args, **kwargs) -> Any:
        """Clear all markers

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.clear_all_markers({arg_string})"
        return self._session.cmd(cmd)

    def add_marker_at_value(self, *args, **kwargs) -> Any:
        """Add a marker at a value

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_marker_at_value({arg_string})"
        return self._session.cmd(cmd)

    def add_nuniform_markers(self, *args, **kwargs) -> Any:
        """Add n uniform markers

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_nuniform_markers({arg_string})"
        return self._session.cmd(cmd)

    def add_markers_at_levels(self, *args, **kwargs) -> Any:
        """Add markers at levels

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_markers_at_levels({arg_string})"
        return self._session.cmd(cmd)

    def add_knot(self, *args, **kwargs) -> Any:
        """Add a knot

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_knot({arg_string})"
        return self._session.cmd(cmd)

    def delete_knot(self, *args, **kwargs) -> Any:
        """Delete a knot

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.delete_knot({arg_string})"
        return self._session.cmd(cmd)

    def get_predefined_palettes(self, *args, **kwargs) -> Any:
        """Get the names of the stored palettes

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_predefined_palettes({arg_string})"
        return self._session.cmd(cmd)

    def restore_palette_named(self, *args, **kwargs) -> Any:
        """Restore a named palette

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.restore_palette_named({arg_string})"
        return self._session.cmd(cmd)

    def undo_restored_palette(self, *args, **kwargs) -> Any:
        """Undo the previously restored palette

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.undo_restored_palette({arg_string})"
        return self._session.cmd(cmd)

    def save_palette_named(self, *args, **kwargs) -> Any:
        """Save a named palette

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.save_palette_named({arg_string})"
        return self._session.cmd(cmd)

    def reset_range_on_time_change_all(self, *args, **kwargs) -> Any:
        """Apply the current reset range on time change setting to all palettes

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.reset_range_on_time_change_all({arg_string})"
        return self._session.cmd(cmd)

    def use_continuous_all(self, *args, **kwargs) -> Any:
        """Apply the current use continuous palette for element vars setting to all palettes

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.use_continuous_all({arg_string})"
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
        
        Palette name
        
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
        
        Palette name
        
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
    def INTERP(self) -> int:
        """INTERP property
        
        Palette interpolation method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_BANDED - Banded
            * ensight.objs.enums.PALETTE_CONTINUOUS - Continuous
            * ensight.objs.enums.PALETTE_CONSTANT - Constant
        
        """
        value = self.getattr(self._session.ensight.objs.enums.INTERP)
        _value = cast(int, value)
        return _value

    @INTERP.setter
    def INTERP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.INTERP, value)

    @property
    def interp(self) -> int:
        """INTERP property
        
        Palette interpolation method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_BANDED - Banded
            * ensight.objs.enums.PALETTE_CONTINUOUS - Continuous
            * ensight.objs.enums.PALETTE_CONSTANT - Constant
        
        Note: both 'interp' and 'INTERP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.INTERP)
        _value = cast(int, value)
        return _value

    @interp.setter
    def interp(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.INTERP, value)

    @property
    def COLORS_PER_LEVEL(self) -> int:
        """COLORS_PER_LEVEL property
        
        Colors per level
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORS_PER_LEVEL)
        _value = cast(int, value)
        return _value

    @COLORS_PER_LEVEL.setter
    def COLORS_PER_LEVEL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORS_PER_LEVEL, value)

    @property
    def colors_per_level(self) -> int:
        """COLORS_PER_LEVEL property
        
        Colors per level
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'colors_per_level' and 'COLORS_PER_LEVEL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORS_PER_LEVEL)
        _value = cast(int, value)
        return _value

    @colors_per_level.setter
    def colors_per_level(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORS_PER_LEVEL, value)

    @property
    def COLOR_SPACE(self) -> int:
        """COLOR_SPACE property
        
        Palette color space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_RGB - RGB
            * ensight.objs.enums.PALETTE_HSV - HSV
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COLOR_SPACE)
        _value = cast(int, value)
        return _value

    @COLOR_SPACE.setter
    def COLOR_SPACE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COLOR_SPACE, value)

    @property
    def color_space(self) -> int:
        """COLOR_SPACE property
        
        Palette color space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_RGB - RGB
            * ensight.objs.enums.PALETTE_HSV - HSV
        
        Note: both 'color_space' and 'COLOR_SPACE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COLOR_SPACE)
        _value = cast(int, value)
        return _value

    @color_space.setter
    def color_space(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COLOR_SPACE, value)

    @property
    def SCALE_METHOD(self) -> int:
        """SCALE_METHOD property
        
        Palette scaling method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_SCALE_LINEAR - Linear
            * ensight.objs.enums.PALETTE_SCALE_LOG - Log
            * ensight.objs.enums.PALETTE_SCALE_QUADRATIC - Quadratic
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE_METHOD)
        _value = cast(int, value)
        return _value

    @SCALE_METHOD.setter
    def SCALE_METHOD(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE_METHOD, value)

    @property
    def scale_method(self) -> int:
        """SCALE_METHOD property
        
        Palette scaling method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_SCALE_LINEAR - Linear
            * ensight.objs.enums.PALETTE_SCALE_LOG - Log
            * ensight.objs.enums.PALETTE_SCALE_QUADRATIC - Quadratic
        
        Note: both 'scale_method' and 'SCALE_METHOD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE_METHOD)
        _value = cast(int, value)
        return _value

    @scale_method.setter
    def scale_method(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE_METHOD, value)

    @property
    def MINMAX(self) -> List[float]:
        """MINMAX property
        
        Palette minimum / maximum values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MINMAX)
        _value = cast(List[float], value)
        return _value

    @MINMAX.setter
    def MINMAX(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.MINMAX, value)

    @property
    def minmax(self) -> List[float]:
        """MINMAX property
        
        Palette minimum / maximum values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'minmax' and 'MINMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MINMAX)
        _value = cast(List[float], value)
        return _value

    @minmax.setter
    def minmax(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.MINMAX, value)

    @property
    def DEGREE(self) -> int:
        """DEGREE property
        
        Palette interpolation degree
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_LINEAR - Linear
            * ensight.objs.enums.PALETTE_SPLINE - Spline
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEGREE)
        _value = cast(int, value)
        return _value

    @DEGREE.setter
    def DEGREE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEGREE, value)

    @property
    def degree(self) -> int:
        """DEGREE property
        
        Palette interpolation degree
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_LINEAR - Linear
            * ensight.objs.enums.PALETTE_SPLINE - Spline
        
        Note: both 'degree' and 'DEGREE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEGREE)
        _value = cast(int, value)
        return _value

    @degree.setter
    def degree(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEGREE, value)

    @property
    def HANDLE_UNDEFINED_VALUE(self) -> int:
        """HANDLE_UNDEFINED_VALUE property
        
        Palette handle undefined value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_UNDEFINED_BY_PART_COLOR - By part color
            * ensight.objs.enums.PALETTE_UNDEFINED_BY_INVISIBLE - By invisible
            * ensight.objs.enums.PALETTE_UNDEFINED_AS_ZERO_VALUE - As zero value
            * ensight.objs.enums.PALETTE_UNDEFINED_BY_UNDEF_COLOR - By undefined color
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HANDLE_UNDEFINED_VALUE)
        _value = cast(int, value)
        return _value

    @HANDLE_UNDEFINED_VALUE.setter
    def HANDLE_UNDEFINED_VALUE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HANDLE_UNDEFINED_VALUE, value)

    @property
    def handle_undefined_value(self) -> int:
        """HANDLE_UNDEFINED_VALUE property
        
        Palette handle undefined value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_UNDEFINED_BY_PART_COLOR - By part color
            * ensight.objs.enums.PALETTE_UNDEFINED_BY_INVISIBLE - By invisible
            * ensight.objs.enums.PALETTE_UNDEFINED_AS_ZERO_VALUE - As zero value
            * ensight.objs.enums.PALETTE_UNDEFINED_BY_UNDEF_COLOR - By undefined color
        
        Note: both 'handle_undefined_value' and 'HANDLE_UNDEFINED_VALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HANDLE_UNDEFINED_VALUE)
        _value = cast(int, value)
        return _value

    @handle_undefined_value.setter
    def handle_undefined_value(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HANDLE_UNDEFINED_VALUE, value)

    @property
    def UNDEFINED_COLOR(self) -> List[float]:
        """UNDEFINED_COLOR property
        
        Palette undefined color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.UNDEFINED_COLOR)
        _value = cast(List[float], value)
        return _value

    @UNDEFINED_COLOR.setter
    def UNDEFINED_COLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.UNDEFINED_COLOR, value)

    @property
    def undefined_color(self) -> List[float]:
        """UNDEFINED_COLOR property
        
        Palette undefined color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'undefined_color' and 'UNDEFINED_COLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.UNDEFINED_COLOR)
        _value = cast(List[float], value)
        return _value

    @undefined_color.setter
    def undefined_color(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.UNDEFINED_COLOR, value)

    @property
    def LIMIT_FRINGES(self) -> int:
        """LIMIT_FRINGES property
        
        Palette limit fringes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_LIMIT_FRINGES_NO - No
            * ensight.objs.enums.PALETTE_LIMIT_FRINGES_PART_COLOR - By part color
            * ensight.objs.enums.PALETTE_LIMIT_FRINGES_INVISIBLE - By invisible
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIMIT_FRINGES)
        _value = cast(int, value)
        return _value

    @LIMIT_FRINGES.setter
    def LIMIT_FRINGES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIMIT_FRINGES, value)

    @property
    def limit_fringes(self) -> int:
        """LIMIT_FRINGES property
        
        Palette limit fringes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_LIMIT_FRINGES_NO - No
            * ensight.objs.enums.PALETTE_LIMIT_FRINGES_PART_COLOR - By part color
            * ensight.objs.enums.PALETTE_LIMIT_FRINGES_INVISIBLE - By invisible
        
        Note: both 'limit_fringes' and 'LIMIT_FRINGES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIMIT_FRINGES)
        _value = cast(int, value)
        return _value

    @limit_fringes.setter
    def limit_fringes(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIMIT_FRINGES, value)

    @property
    def NODE_LOCK(self) -> int:
        """NODE_LOCK property
        
        Palette node lock
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_NODE_LOCK_ALL - All
            * ensight.objs.enums.PALETTE_NODE_LOCK_COLOR - Color
            * ensight.objs.enums.PALETTE_NODE_LOCK_NONE - None
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODE_LOCK)
        _value = cast(int, value)
        return _value

    @NODE_LOCK.setter
    def NODE_LOCK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODE_LOCK, value)

    @property
    def node_lock(self) -> int:
        """NODE_LOCK property
        
        Palette node lock
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_NODE_LOCK_ALL - All
            * ensight.objs.enums.PALETTE_NODE_LOCK_COLOR - Color
            * ensight.objs.enums.PALETTE_NODE_LOCK_NONE - None
        
        Note: both 'node_lock' and 'NODE_LOCK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODE_LOCK)
        _value = cast(int, value)
        return _value

    @node_lock.setter
    def node_lock(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODE_LOCK, value)

    @property
    def C1_POINTS(self) -> object:
        """C1_POINTS property
        
        component 1 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.C1_POINTS)
        _value = cast(object, value)
        return _value

    @C1_POINTS.setter
    def C1_POINTS(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C1_POINTS, value)

    @property
    def c1_points(self) -> object:
        """C1_POINTS property
        
        component 1 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'c1_points' and 'C1_POINTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.C1_POINTS)
        _value = cast(object, value)
        return _value

    @c1_points.setter
    def c1_points(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C1_POINTS, value)

    @property
    def C2_POINTS(self) -> object:
        """C2_POINTS property
        
        component 2 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.C2_POINTS)
        _value = cast(object, value)
        return _value

    @C2_POINTS.setter
    def C2_POINTS(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C2_POINTS, value)

    @property
    def c2_points(self) -> object:
        """C2_POINTS property
        
        component 2 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'c2_points' and 'C2_POINTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.C2_POINTS)
        _value = cast(object, value)
        return _value

    @c2_points.setter
    def c2_points(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C2_POINTS, value)

    @property
    def C3_POINTS(self) -> object:
        """C3_POINTS property
        
        component 3 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.C3_POINTS)
        _value = cast(object, value)
        return _value

    @C3_POINTS.setter
    def C3_POINTS(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C3_POINTS, value)

    @property
    def c3_points(self) -> object:
        """C3_POINTS property
        
        component 3 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'c3_points' and 'C3_POINTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.C3_POINTS)
        _value = cast(object, value)
        return _value

    @c3_points.setter
    def c3_points(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C3_POINTS, value)

    @property
    def C4_POINTS(self) -> object:
        """C4_POINTS property
        
        component 4 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.C4_POINTS)
        _value = cast(object, value)
        return _value

    @C4_POINTS.setter
    def C4_POINTS(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C4_POINTS, value)

    @property
    def c4_points(self) -> object:
        """C4_POINTS property
        
        component 4 nodes
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'c4_points' and 'C4_POINTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.C4_POINTS)
        _value = cast(object, value)
        return _value

    @c4_points.setter
    def c4_points(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.C4_POINTS, value)

    @property
    def MAX_MARKERS(self) -> int:
        """MAX_MARKERS property
        
        Palette max number of markers
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MAX_MARKERS)
        _value = cast(int, value)
        return _value

    @MAX_MARKERS.setter
    def MAX_MARKERS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MAX_MARKERS, value)

    @property
    def max_markers(self) -> int:
        """MAX_MARKERS property
        
        Palette max number of markers
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'max_markers' and 'MAX_MARKERS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MAX_MARKERS)
        _value = cast(int, value)
        return _value

    @max_markers.setter
    def max_markers(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MAX_MARKERS, value)

    @property
    def MARKER_COLOR(self) -> List[float]:
        """MARKER_COLOR property
        
        Palette marker color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKER_COLOR)
        _value = cast(List[float], value)
        return _value

    @MARKER_COLOR.setter
    def MARKER_COLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKER_COLOR, value)

    @property
    def marker_color(self) -> List[float]:
        """MARKER_COLOR property
        
        Palette marker color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'marker_color' and 'MARKER_COLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKER_COLOR)
        _value = cast(List[float], value)
        return _value

    @marker_color.setter
    def marker_color(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKER_COLOR, value)

    @property
    def MARKER_WIDTH(self) -> int:
        """MARKER_WIDTH property
        
        Palette marker width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKER_WIDTH)
        _value = cast(int, value)
        return _value

    @MARKER_WIDTH.setter
    def MARKER_WIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKER_WIDTH, value)

    @property
    def marker_width(self) -> int:
        """MARKER_WIDTH property
        
        Palette marker width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'marker_width' and 'MARKER_WIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MARKER_WIDTH)
        _value = cast(int, value)
        return _value

    @marker_width.setter
    def marker_width(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MARKER_WIDTH, value)

    @property
    def NLEVELS(self) -> int:
        """NLEVELS property
        
        Palette number of levels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NLEVELS)
        _value = cast(int, value)
        return _value

    @NLEVELS.setter
    def NLEVELS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NLEVELS, value)

    @property
    def nlevels(self) -> int:
        """NLEVELS property
        
        Palette number of levels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'nlevels' and 'NLEVELS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NLEVELS)
        _value = cast(int, value)
        return _value

    @nlevels.setter
    def nlevels(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NLEVELS, value)

    @property
    def LEVELS_AND_COLORS(self) -> object:
        """LEVELS_AND_COLORS property
        
        levels and colors
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEVELS_AND_COLORS)
        _value = cast(object, value)
        return _value

    @LEVELS_AND_COLORS.setter
    def LEVELS_AND_COLORS(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.LEVELS_AND_COLORS, value)

    @property
    def levels_and_colors(self) -> object:
        """LEVELS_AND_COLORS property
        
        levels and colors
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'levels_and_colors' and 'LEVELS_AND_COLORS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEVELS_AND_COLORS)
        _value = cast(object, value)
        return _value

    @levels_and_colors.setter
    def levels_and_colors(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.LEVELS_AND_COLORS, value)

    @property
    def LEVELS_LOCK(self) -> int:
        """LEVELS_LOCK property
        
        Palette levels lock
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEVELS_LOCK)
        _value = cast(int, value)
        return _value

    @LEVELS_LOCK.setter
    def LEVELS_LOCK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEVELS_LOCK, value)

    @property
    def levels_lock(self) -> int:
        """LEVELS_LOCK property
        
        Palette levels lock
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'levels_lock' and 'LEVELS_LOCK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEVELS_LOCK)
        _value = cast(int, value)
        return _value

    @levels_lock.setter
    def levels_lock(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LEVELS_LOCK, value)

    @property
    def ALPHA_VOLUME_SCALE(self) -> float:
        """ALPHA_VOLUME_SCALE property
        
        Palette alpha volume scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ALPHA_VOLUME_SCALE)
        _value = cast(float, value)
        return _value

    @ALPHA_VOLUME_SCALE.setter
    def ALPHA_VOLUME_SCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ALPHA_VOLUME_SCALE, value)

    @property
    def alpha_volume_scale(self) -> float:
        """ALPHA_VOLUME_SCALE property
        
        Palette alpha volume scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'alpha_volume_scale' and 'ALPHA_VOLUME_SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ALPHA_VOLUME_SCALE)
        _value = cast(float, value)
        return _value

    @alpha_volume_scale.setter
    def alpha_volume_scale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ALPHA_VOLUME_SCALE, value)

    @property
    def HISTO_SCALE(self) -> float:
        """HISTO_SCALE property
        
        Palette histogram scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HISTO_SCALE)
        _value = cast(float, value)
        return _value

    @HISTO_SCALE.setter
    def HISTO_SCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HISTO_SCALE, value)

    @property
    def histo_scale(self) -> float:
        """HISTO_SCALE property
        
        Palette histogram scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'histo_scale' and 'HISTO_SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HISTO_SCALE)
        _value = cast(float, value)
        return _value

    @histo_scale.setter
    def histo_scale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HISTO_SCALE, value)

    @property
    def TIME_RANGE(self) -> List[int]:
        """TIME_RANGE property
        
        Palette time range values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIME_RANGE)
        _value = cast(List[int], value)
        return _value

    @TIME_RANGE.setter
    def TIME_RANGE(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIME_RANGE, value)

    @property
    def time_range(self) -> List[int]:
        """TIME_RANGE property
        
        Palette time range values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        Note: both 'time_range' and 'TIME_RANGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIME_RANGE)
        _value = cast(List[int], value)
        return _value

    @time_range.setter
    def time_range(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIME_RANGE, value)

    @property
    def PALMISC(self) -> int:
        """PALMISC property
        
        Palette catch-all for signaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PALMISC)
        _value = cast(int, value)
        return _value

    @PALMISC.setter
    def PALMISC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PALMISC, value)

    @property
    def palmisc(self) -> int:
        """PALMISC property
        
        Palette catch-all for signaling
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'palmisc' and 'PALMISC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PALMISC)
        _value = cast(int, value)
        return _value

    @palmisc.setter
    def palmisc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PALMISC, value)

    @property
    def VARIABLE(self) -> ensobjlist:
        """VARIABLE property
        
        variable
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def variable(self) -> ensobjlist:
        """VARIABLE property
        
        variable
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'variable' and 'VARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def RESET_RANGE_ON_TIME_CHANGE(self) -> int:
        """RESET_RANGE_ON_TIME_CHANGE property
        
        Palette reset range on time change
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RESET_RANGE_ON_TIME_CHANGE)
        _value = cast(int, value)
        return _value

    @RESET_RANGE_ON_TIME_CHANGE.setter
    def RESET_RANGE_ON_TIME_CHANGE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RESET_RANGE_ON_TIME_CHANGE, value)

    @property
    def reset_range_on_time_change(self) -> int:
        """RESET_RANGE_ON_TIME_CHANGE property
        
        Palette reset range on time change
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'reset_range_on_time_change' and 'RESET_RANGE_ON_TIME_CHANGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RESET_RANGE_ON_TIME_CHANGE)
        _value = cast(int, value)
        return _value

    @reset_range_on_time_change.setter
    def reset_range_on_time_change(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RESET_RANGE_ON_TIME_CHANGE, value)

    @property
    def USE_CONTINUOUS(self) -> int:
        """USE_CONTINUOUS property
        
        Palette use continuous values for per element variables
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.USE_CONTINUOUS)
        _value = cast(int, value)
        return _value

    @USE_CONTINUOUS.setter
    def USE_CONTINUOUS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.USE_CONTINUOUS, value)

    @property
    def use_continuous(self) -> int:
        """USE_CONTINUOUS property
        
        Palette use continuous values for per element variables
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'use_continuous' and 'USE_CONTINUOUS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.USE_CONTINUOUS)
        _value = cast(int, value)
        return _value

    @use_continuous.setter
    def use_continuous(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.USE_CONTINUOUS, value)

"""ens_texture module

The ens_texture module provides a proxy interface to EnSight ENS_TEXTURE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_TEXTURE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_TEXTURE

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
    def FILENAME(self) -> str:
        """FILENAME property
        
        Filename
        
        Supported operations:
            getattr
        Datatype:
            String, 256 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FILENAME)
        _value = cast(str, value)
        return _value

    @property
    def filename(self) -> str:
        """FILENAME property
        
        Filename
        
        Supported operations:
            getattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'filename' and 'FILENAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FILENAME)
        _value = cast(str, value)
        return _value

    @property
    def IMAGE(self) -> object:
        """IMAGE property
        
        Texture image
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.IMAGE)
        _value = cast(object, value)
        return _value

    @IMAGE.setter
    def IMAGE(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.IMAGE, value)

    @property
    def image(self) -> object:
        """IMAGE property
        
        Texture image
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'image' and 'IMAGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.IMAGE)
        _value = cast(object, value)
        return _value

    @image.setter
    def image(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.IMAGE, value)

    @property
    def COMPRESSION(self) -> int:
        """COMPRESSION property
        
        Compression
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.COMPRESSION_NONE - None
            * ensight.objs.enums.COMPRESSION_RLE - RLE
            * ensight.objs.enums.COMPRESSION_GZ - GZ
            * ensight.objs.enums.COMPRESSION_JPEG - JPEG
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COMPRESSION)
        _value = cast(int, value)
        return _value

    @COMPRESSION.setter
    def COMPRESSION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COMPRESSION, value)

    @property
    def compression(self) -> int:
        """COMPRESSION property
        
        Compression
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.COMPRESSION_NONE - None
            * ensight.objs.enums.COMPRESSION_RLE - RLE
            * ensight.objs.enums.COMPRESSION_GZ - GZ
            * ensight.objs.enums.COMPRESSION_JPEG - JPEG
        
        Note: both 'compression' and 'COMPRESSION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COMPRESSION)
        _value = cast(int, value)
        return _value

    @compression.setter
    def compression(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COMPRESSION, value)

    @property
    def NUMFRAMES(self) -> int:
        """NUMFRAMES property
        
        Number of frames in the texture
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMFRAMES)
        _value = cast(int, value)
        return _value

    @property
    def numframes(self) -> int:
        """NUMFRAMES property
        
        Number of frames in the texture
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'numframes' and 'NUMFRAMES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NUMFRAMES)
        _value = cast(int, value)
        return _value

    @property
    def CURRENTFRAME(self) -> int:
        """CURRENTFRAME property
        
        Current texture frame number
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENTFRAME)
        _value = cast(int, value)
        return _value

    @property
    def currentframe(self) -> int:
        """CURRENTFRAME property
        
        Current texture frame number
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'currentframe' and 'CURRENTFRAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENTFRAME)
        _value = cast(int, value)
        return _value

    @property
    def HASTRANSPARENT(self) -> int:
        """HASTRANSPARENT property
        
        Texture has transparent colors
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HASTRANSPARENT)
        _value = cast(int, value)
        return _value

    @property
    def hastransparent(self) -> int:
        """HASTRANSPARENT property
        
        Texture has transparent colors
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'hastransparent' and 'HASTRANSPARENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HASTRANSPARENT)
        _value = cast(int, value)
        return _value

    @property
    def FRAMES(self) -> List[int]:
        """FRAMES property
        
        Animation frame limits
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FRAMES)
        _value = cast(List[int], value)
        return _value

    @FRAMES.setter
    def FRAMES(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.FRAMES, value)

    @property
    def frames(self) -> List[int]:
        """FRAMES property
        
        Animation frame limits
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        Note: both 'frames' and 'FRAMES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FRAMES)
        _value = cast(List[int], value)
        return _value

    @frames.setter
    def frames(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.FRAMES, value)

    @property
    def TIMES(self) -> List[float]:
        """TIMES property
        
        Animation time limits
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMES)
        _value = cast(List[float], value)
        return _value

    @TIMES.setter
    def TIMES(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMES, value)

    @property
    def times(self) -> List[float]:
        """TIMES property
        
        Animation time limits
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'times' and 'TIMES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMES)
        _value = cast(List[float], value)
        return _value

    @times.setter
    def times(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMES, value)

    @property
    def AUTOSCALE(self) -> int:
        """AUTOSCALE property
        
        Autoscale time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AUTOSCALE)
        _value = cast(int, value)
        return _value

    @AUTOSCALE.setter
    def AUTOSCALE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AUTOSCALE, value)

    @property
    def autoscale(self) -> int:
        """AUTOSCALE property
        
        Autoscale time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'autoscale' and 'AUTOSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AUTOSCALE)
        _value = cast(int, value)
        return _value

    @autoscale.setter
    def autoscale(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AUTOSCALE, value)

    @property
    def BORDERCOLOR(self) -> List[float]:
        """BORDERCOLOR property
        
        Border color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERCOLOR)
        _value = cast(List[float], value)
        return _value

    @BORDERCOLOR.setter
    def BORDERCOLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERCOLOR, value)

    @property
    def bordercolor(self) -> List[float]:
        """BORDERCOLOR property
        
        Border color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        Note: both 'bordercolor' and 'BORDERCOLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERCOLOR)
        _value = cast(List[float], value)
        return _value

    @bordercolor.setter
    def bordercolor(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERCOLOR, value)

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

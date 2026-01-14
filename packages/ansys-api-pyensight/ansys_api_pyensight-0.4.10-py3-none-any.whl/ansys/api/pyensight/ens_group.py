"""ens_group module

The ens_group module provides a proxy interface to EnSight ENS_GROUP instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_GROUP(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_GROUP

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

    def addchild(self, *args, **kwargs) -> Any:
        """Add a child to an object

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.addchild({arg_string})"
        return self._session.cmd(cmd)

    def setchildattr(self, *args, **kwargs) -> Any:
        """Set attribute on object children

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.setchildattr({arg_string})"
        return self._session.cmd(cmd)

    def setchildattrs(self, *args, **kwargs) -> Any:
        """Set attributes on object children

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.setchildattrs({arg_string})"
        return self._session.cmd(cmd)

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

    def removechild(self, *args, **kwargs) -> Any:
        """Remove child from this group

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.removechild({arg_string})"
        return self._session.cmd(cmd)

    def refreshgui(self, *args, **kwargs) -> Any:
        """Refresh the selection GUI

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.refreshgui({arg_string})"
        return self._session.cmd(cmd)

    def creategroup(self, *args, **kwargs) -> Any:
        """Create a group (ENS_GROUP) child

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.creategroup({arg_string})"
        return self._session.cmd(cmd)

    def transform(self, *args, **kwargs) -> Any:
        """Apply an incremental transform

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.transform({arg_string})"
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
        
        description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
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
            String, 256 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @description.setter
    def description(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DESCRIPTION, value)

    @property
    def UNIQUENAME(self) -> str:
        """UNIQUENAME property
        
        unique name
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.UNIQUENAME)
        _value = cast(str, value)
        return _value

    @UNIQUENAME.setter
    def UNIQUENAME(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.UNIQUENAME, value)

    @property
    def uniquename(self) -> str:
        """UNIQUENAME property
        
        unique name
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'uniquename' and 'UNIQUENAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.UNIQUENAME)
        _value = cast(str, value)
        return _value

    @uniquename.setter
    def uniquename(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.UNIQUENAME, value)

    @property
    def PATHNAME(self) -> str:
        """PATHNAME property
        
        full name
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 2048 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PATHNAME)
        _value = cast(str, value)
        return _value

    @PATHNAME.setter
    def PATHNAME(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PATHNAME, value)

    @property
    def pathname(self) -> str:
        """PATHNAME property
        
        full name
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 2048 characters maximum
        
        Note: both 'pathname' and 'PATHNAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PATHNAME)
        _value = cast(str, value)
        return _value

    @pathname.setter
    def pathname(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PATHNAME, value)

    @property
    def PARENT(self) -> ensobjlist:
        """PARENT property
        
        parent
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARENT)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def parent(self) -> ensobjlist:
        """PARENT property
        
        parent
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'parent' and 'PARENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARENT)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def CHILDREN(self) -> ensobjlist:
        """CHILDREN property
        
        children
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CHILDREN)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def children(self) -> ensobjlist:
        """CHILDREN property
        
        children
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'children' and 'CHILDREN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CHILDREN)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def SELECTIONS(self) -> int:
        """SELECTIONS property
        
        is selection
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SELECTIONS)
        _value = cast(int, value)
        return _value

    @property
    def selections(self) -> int:
        """SELECTIONS property
        
        is selection
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'selections' and 'SELECTIONS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SELECTIONS)
        _value = cast(int, value)
        return _value

    @property
    def ROTATION(self) -> List[float]:
        """ROTATION property
        
        rotation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Normalized Quaternion, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ROTATION)
        _value = cast(List[float], value)
        return _value

    @ROTATION.setter
    def ROTATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ROTATION, value)

    @property
    def rotation(self) -> List[float]:
        """ROTATION property
        
        rotation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Normalized Quaternion, 4 element array
        
        Note: both 'rotation' and 'ROTATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ROTATION)
        _value = cast(List[float], value)
        return _value

    @rotation.setter
    def rotation(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ROTATION, value)

    @property
    def TRANSLATION(self) -> List[float]:
        """TRANSLATION property
        
        translation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSLATION)
        _value = cast(List[float], value)
        return _value

    @TRANSLATION.setter
    def TRANSLATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSLATION, value)

    @property
    def translation(self) -> List[float]:
        """TRANSLATION property
        
        translation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'translation' and 'TRANSLATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSLATION)
        _value = cast(List[float], value)
        return _value

    @translation.setter
    def translation(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSLATION, value)

    @property
    def SCALE(self) -> List[float]:
        """SCALE property
        
        scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(List[float], value)
        return _value

    @SCALE.setter
    def SCALE(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def scale(self) -> List[float]:
        """SCALE property
        
        scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'scale' and 'SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(List[float], value)
        return _value

    @scale.setter
    def scale(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def POLYGON_OFFSET(self) -> int:
        """POLYGON_OFFSET property
        
        use polygon offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.POLYGON_OFFSET)
        _value = cast(int, value)
        return _value

    @POLYGON_OFFSET.setter
    def POLYGON_OFFSET(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.POLYGON_OFFSET, value)

    @property
    def polygon_offset(self) -> int:
        """POLYGON_OFFSET property
        
        use polygon offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'polygon_offset' and 'POLYGON_OFFSET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.POLYGON_OFFSET)
        _value = cast(int, value)
        return _value

    @polygon_offset.setter
    def polygon_offset(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.POLYGON_OFFSET, value)

    @property
    def OFFSET(self) -> List[float]:
        """OFFSET property
        
        offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OFFSET)
        _value = cast(List[float], value)
        return _value

    @OFFSET.setter
    def OFFSET(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OFFSET, value)

    @property
    def offset(self) -> List[float]:
        """OFFSET property
        
        offset
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'offset' and 'OFFSET' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OFFSET)
        _value = cast(List[float], value)
        return _value

    @offset.setter
    def offset(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OFFSET, value)

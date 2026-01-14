"""ens_source module

The ens_source module provides a proxy interface to EnSight ENS_SOURCE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj, ReportItemSourceInterface

class ENS_SOURCE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_SOURCE

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
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        Description
        
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
        
        Description
        
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
    def TAGS(self) -> str:
        """TAGS property
        
        Report tags
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 2048 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TAGS)
        _value = cast(str, value)
        return _value

    @TAGS.setter
    def TAGS(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.TAGS, value)

    @property
    def tags(self) -> str:
        """TAGS property
        
        Report tags
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 2048 characters maximum
        
        Note: both 'tags' and 'TAGS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TAGS)
        _value = cast(str, value)
        return _value

    @tags.setter
    def tags(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.TAGS, value)

    @property
    def ACTIVE(self) -> int:
        """ACTIVE property
        
        Active
        
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
        
        Active
        
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
    def PARENT(self) -> ensobjlist:
        """PARENT property
        
        Parent state object
        
        Supported operations:
            getattr, setattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARENT)
        _value = cast(ensobjlist, value)
        return _value

    @PARENT.setter
    def PARENT(self, value: ensobjlist) -> None:
        self.setattr(self._session.ensight.objs.enums.PARENT, value)

    @property
    def parent(self) -> ensobjlist:
        """PARENT property
        
        Parent state object
        
        Supported operations:
            getattr, setattr
        Datatype:
            Object, scalar
        
        Note: both 'parent' and 'PARENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARENT)
        _value = cast(ensobjlist, value)
        return _value

    @parent.setter
    def parent(self, value: ensobjlist) -> None:
        self.setattr(self._session.ensight.objs.enums.PARENT, value)

    @property
    def GENERATION_PENDING(self) -> int:
        """GENERATION_PENDING property
        
        Report generation pending
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GENERATION_PENDING)
        _value = cast(int, value)
        return _value

    @GENERATION_PENDING.setter
    def GENERATION_PENDING(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GENERATION_PENDING, value)

    @property
    def generation_pending(self) -> int:
        """GENERATION_PENDING property
        
        Report generation pending
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'generation_pending' and 'GENERATION_PENDING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GENERATION_PENDING)
        _value = cast(int, value)
        return _value

    @generation_pending.setter
    def generation_pending(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GENERATION_PENDING, value)

    @property
    def SOURCE(self) -> 'ReportItemSourceInterface':
        """SOURCE property
        
        Source object
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SOURCE)
        _value = cast('ReportItemSourceInterface', value)
        return _value

    @SOURCE.setter
    def SOURCE(self, value: 'ReportItemSourceInterface') -> None:
        self.setattr(self._session.ensight.objs.enums.SOURCE, value)

    @property
    def source(self) -> 'ReportItemSourceInterface':
        """SOURCE property
        
        Source object
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'source' and 'SOURCE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SOURCE)
        _value = cast('ReportItemSourceInterface', value)
        return _value

    @source.setter
    def source(self, value: 'ReportItemSourceInterface') -> None:
        self.setattr(self._session.ensight.objs.enums.SOURCE, value)

    @property
    def CMDLANG_REFERENCE(self) -> object:
        """CMDLANG_REFERENCE property
        
        Command language object name
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CMDLANG_REFERENCE)
        _value = cast(object, value)
        return _value

    @property
    def cmdlang_reference(self) -> object:
        """CMDLANG_REFERENCE property
        
        Command language object name
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'cmdlang_reference' and 'CMDLANG_REFERENCE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CMDLANG_REFERENCE)
        _value = cast(object, value)
        return _value

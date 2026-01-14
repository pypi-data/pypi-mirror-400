"""ens_state module

The ens_state module provides a proxy interface to EnSight ENS_STATE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ens_emitterobj

class ENS_STATE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_STATE

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

    def capture(self, *args, **kwargs) -> Any:
        """Snapshot attributes from current objects.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.capture({arg_string})"
        return self._session.cmd(cmd)

    def apply(self, *args, **kwargs) -> Any:
        """Appy attributes to current objects.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.apply({arg_string})"
        return self._session.cmd(cmd)

    def save(self, *args, **kwargs) -> Any:
        """Save an attribute set to a file.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.save({arg_string})"
        return self._session.cmd(cmd)

    def read(self, *args, **kwargs) -> Any:
        """Read an attribute set from a file.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.read({arg_string})"
        return self._session.cmd(cmd)

    def generate_report(self, *args, **kwargs) -> Any:
        """Generate a Nexus report.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.generate_report({arg_string})"
        return self._session.cmd(cmd)

    def add_state(self, *args, **kwargs) -> Any:
        """Add a new state.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_state({arg_string})"
        return self._session.cmd(cmd)

    def create_state(self, *args, **kwargs) -> Any:
        """Create a new state owned by Python proxy.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.create_state({arg_string})"
        return self._session.cmd(cmd)

    def add_source(self, *args, **kwargs) -> Any:
        """Add a new source to a state.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_source({arg_string})"
        return self._session.cmd(cmd)

    def move(self, *args, **kwargs) -> Any:
        """Change the ordering of state/source children.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.move({arg_string})"
        return self._session.cmd(cmd)

    def set_logo_file(self, *args, **kwargs) -> Any:
        """Specify the file to use as a logo.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.set_logo_file({arg_string})"
        return self._session.cmd(cmd)

    def undo(self, *args, **kwargs) -> Any:
        """Revert to the state before the last apply.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.undo({arg_string})"
        return self._session.cmd(cmd)

    def update_tags(self, *args, **kwargs) -> Any:
        """Update the TAGS property and optionally the session ID.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.update_tags({arg_string})"
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
            getattr, setattr
        Datatype:
            String, 37 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.UUID)
        _value = cast(str, value)
        return _value

    @UUID.setter
    def UUID(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.UUID, value)

    @property
    def uuid(self) -> str:
        """UUID property
        
        universal unique id
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 37 characters maximum
        
        Note: both 'uuid' and 'UUID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.UUID)
        _value = cast(str, value)
        return _value

    @uuid.setter
    def uuid(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.UUID, value)

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
    def CHILDREN(self) -> ensobjlist['ENS_SOURCE']:
        """CHILDREN property
        
        Children
        
        Supported operations:
            getattr
        Datatype:
            Unknown:1610612720, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CHILDREN)
        _value = cast(ensobjlist['ENS_SOURCE'], value)
        return _value

    @property
    def children(self) -> ensobjlist['ENS_SOURCE']:
        """CHILDREN property
        
        Children
        
        Supported operations:
            getattr
        Datatype:
            Unknown:1610612720, scalar
        
        Note: both 'children' and 'CHILDREN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CHILDREN)
        _value = cast(ensobjlist['ENS_SOURCE'], value)
        return _value

    @property
    def HTML(self) -> str:
        """HTML property
        
        HTML header
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 2048 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HTML)
        _value = cast(str, value)
        return _value

    @HTML.setter
    def HTML(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.HTML, value)

    @property
    def html(self) -> str:
        """HTML property
        
        HTML header
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 2048 characters maximum
        
        Note: both 'html' and 'HTML' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HTML)
        _value = cast(str, value)
        return _value

    @html.setter
    def html(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.HTML, value)

    @property
    def TAGS(self) -> str:
        """TAGS property
        
        Tags
        
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
        
        Tags
        
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
    def CURRENT(self) -> int:
        """CURRENT property
        
        Current
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENT)
        _value = cast(int, value)
        return _value

    @CURRENT.setter
    def CURRENT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CURRENT, value)

    @property
    def current(self) -> int:
        """CURRENT property
        
        Current
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'current' and 'CURRENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENT)
        _value = cast(int, value)
        return _value

    @current.setter
    def current(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CURRENT, value)

    @property
    def TIMETRACK(self) -> int:
        """TIMETRACK property
        
        Track time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMETRACK)
        _value = cast(int, value)
        return _value

    @TIMETRACK.setter
    def TIMETRACK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMETRACK, value)

    @property
    def timetrack(self) -> int:
        """TIMETRACK property
        
        Track time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'timetrack' and 'TIMETRACK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMETRACK)
        _value = cast(int, value)
        return _value

    @timetrack.setter
    def timetrack(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMETRACK, value)

    @property
    def USE_LOGO(self) -> int:
        """USE_LOGO property
        
        Include logo in report
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.USE_LOGO)
        _value = cast(int, value)
        return _value

    @USE_LOGO.setter
    def USE_LOGO(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.USE_LOGO, value)

    @property
    def use_logo(self) -> int:
        """USE_LOGO property
        
        Include logo in report
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'use_logo' and 'USE_LOGO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.USE_LOGO)
        _value = cast(int, value)
        return _value

    @use_logo.setter
    def use_logo(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.USE_LOGO, value)

    @property
    def LOGO_DATA(self) -> object:
        """LOGO_DATA property
        
        Logo data
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOGO_DATA)
        _value = cast(object, value)
        return _value

    @property
    def logo_data(self) -> object:
        """LOGO_DATA property
        
        Logo data
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'logo_data' and 'LOGO_DATA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOGO_DATA)
        _value = cast(object, value)
        return _value

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

    @property
    def TARGETS(self) -> object:
        """TARGETS property
        
        Target objects and attributes
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TARGETS)
        _value = cast(object, value)
        return _value

    @property
    def targets(self) -> object:
        """TARGETS property
        
        Target objects and attributes
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'targets' and 'TARGETS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TARGETS)
        _value = cast(object, value)
        return _value

    @property
    def TEMPLATE_NAME(self) -> str:
        """TEMPLATE_NAME property
        
        Report template name
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEMPLATE_NAME)
        _value = cast(str, value)
        return _value

    @TEMPLATE_NAME.setter
    def TEMPLATE_NAME(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.TEMPLATE_NAME, value)

    @property
    def template_name(self) -> str:
        """TEMPLATE_NAME property
        
        Report template name
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'template_name' and 'TEMPLATE_NAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEMPLATE_NAME)
        _value = cast(str, value)
        return _value

    @template_name.setter
    def template_name(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.TEMPLATE_NAME, value)

    @property
    def CREATE_REPORT_TEMPLATE(self) -> int:
        """CREATE_REPORT_TEMPLATE property
        
        Include a report template during generation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CREATE_REPORT_TEMPLATE)
        _value = cast(int, value)
        return _value

    @CREATE_REPORT_TEMPLATE.setter
    def CREATE_REPORT_TEMPLATE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CREATE_REPORT_TEMPLATE, value)

    @property
    def create_report_template(self) -> int:
        """CREATE_REPORT_TEMPLATE property
        
        Include a report template during generation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'create_report_template' and 'CREATE_REPORT_TEMPLATE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CREATE_REPORT_TEMPLATE)
        _value = cast(int, value)
        return _value

    @create_report_template.setter
    def create_report_template(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CREATE_REPORT_TEMPLATE, value)

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

"""ens_case module

The ens_case module provides a proxy interface to EnSight ENS_CASE instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_CASE(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_CASE

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

    def queryparts(self, *args, **kwargs) -> Any:
        """List part children of this case

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.queryparts({arg_string})"
        return self._session.cmd(cmd)

    def queryreaders(self, *args, **kwargs) -> Any:
        """List readers supported by this case

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.queryreaders({arg_string})"
        return self._session.cmd(cmd)

    def setextraguidefault(self, *args, **kwargs) -> Any:
        """Change reader xtra GUI option defaults

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.setextraguidefault({arg_string})"
        return self._session.cmd(cmd)

    def queryfileformat(self, *args, **kwargs) -> Any:
        """Query file format info

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.queryfileformat({arg_string})"
        return self._session.cmd(cmd)

    def queryfileformats(self, *args, **kwargs) -> Any:
        """Query all matching file format info

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.queryfileformats({arg_string})"
        return self._session.cmd(cmd)

    def queryactualformat(self, *args, **kwargs) -> Any:
        """Query actual (SOS case) file format

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.queryactualformat({arg_string})"
        return self._session.cmd(cmd)

    def queryfilemap(self, *args, **kwargs) -> Any:
        """Query filemap info

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.queryfilemap({arg_string})"
        return self._session.cmd(cmd)

    def directorylisting(self, *args, **kwargs) -> Any:
        """Query file format info

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.directorylisting({arg_string})"
        return self._session.cmd(cmd)

    def reload_data(self, *args, **kwargs) -> Any:
        """Allow the server/reader to change the definition of the currently loaded dataset

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.reload_data({arg_string})"
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

    def remote_io(self, *args, **kwargs) -> Any:
        """Perform remote file I/O

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.remote_io({arg_string})"
        return self._session.cmd(cmd)

    def remote_launch(self, *args, **kwargs) -> Any:
        """Run a program on a remote system

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.remote_launch({arg_string})"
        return self._session.cmd(cmd)

    def update_lookup_table(self, *args, **kwargs) -> Any:
        """Redefine a table for the LOOKUP() calculator function

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.update_lookup_table({arg_string})"
        return self._session.cmd(cmd)

    def get_server_userdata(self, *args, **kwargs) -> Any:
        """Get any pending server-side userdata

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_server_userdata({arg_string})"
        return self._session.cmd(cmd)

    def mcf_clear(self, *args, **kwargs) -> Any:
        """Clear the Multi-File Information

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.mcf_clear({arg_string})"
        return self._session.cmd(cmd)

    def mcf_append(self, *args, **kwargs) -> Any:
        """Add a file to the Multi-File Information

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.mcf_append({arg_string})"
        return self._session.cmd(cmd)

    def mcf_setgeneratefile(self, *args, **kwargs) -> Any:
        """Create a MCF file with the files specified

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.mcf_setgeneratefile({arg_string})"
        return self._session.cmd(cmd)

    def mcf_setgeneratefilename(self, *args, **kwargs) -> Any:
        """Name of the MCF file to create

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.mcf_setgeneratefilename({arg_string})"
        return self._session.cmd(cmd)

    def datapath_history(self, *args, **kwargs) -> Any:
        """Cache paths for data read history

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.datapath_history({arg_string})"
        return self._session.cmd(cmd)

    def datapath_history_add(self, *args, **kwargs) -> Any:
        """Cache data path to add to history

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.datapath_history_add({arg_string})"
        return self._session.cmd(cmd)

    def client_command(self, *args, **kwargs) -> Any:
        """Send a generic command to the server
        
        Generic string commands can be sent to the server.  If the current reader supports commands,
        the reader can interpret them and send back a reply.  The reply is wrapped
        in a JSON encoded object with separate keys for each servers reply.
        
        Args:
            command:
                The string to be sent to the server.
        Return:
            A JSON encoded object of the form: {"N":OUTPUT} where N is the server
            index (multiple in SOS mode) and OUTPUT is the server/reader specific reply string.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.client_command({arg_string})"
        return self._session.cmd(cmd)

    def client_command_callback(self, *args, **kwargs) -> Any:
        """Set the client command callback function.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.client_command_callback({arg_string})"
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
    def ENS_KIND(self) -> str:
        """ENS_KIND property
        
        Kind
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_KIND)
        _value = cast(str, value)
        return _value

    @ENS_KIND.setter
    def ENS_KIND(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_KIND, value)

    @property
    def ens_kind(self) -> str:
        """ENS_KIND property
        
        Kind
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_kind' and 'ENS_KIND' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_KIND)
        _value = cast(str, value)
        return _value

    @ens_kind.setter
    def ens_kind(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_KIND, value)

    @property
    def ENS_DETAILS(self) -> str:
        """ENS_DETAILS property
        
        Details
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_DETAILS)
        _value = cast(str, value)
        return _value

    @ENS_DETAILS.setter
    def ENS_DETAILS(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_DETAILS, value)

    @property
    def ens_details(self) -> str:
        """ENS_DETAILS property
        
        Details
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_details' and 'ENS_DETAILS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_DETAILS)
        _value = cast(str, value)
        return _value

    @ens_details.setter
    def ens_details(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_DETAILS, value)

    @property
    def ENS_UNITS_SYSTEM_NAME(self) -> str:
        """ENS_UNITS_SYSTEM_NAME property
        
        Units System
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_UNITS_SYSTEM_NAME)
        _value = cast(str, value)
        return _value

    @ENS_UNITS_SYSTEM_NAME.setter
    def ENS_UNITS_SYSTEM_NAME(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_UNITS_SYSTEM_NAME, value)

    @property
    def ens_units_system_name(self) -> str:
        """ENS_UNITS_SYSTEM_NAME property
        
        Units System
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_units_system_name' and 'ENS_UNITS_SYSTEM_NAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_UNITS_SYSTEM_NAME)
        _value = cast(str, value)
        return _value

    @ens_units_system_name.setter
    def ens_units_system_name(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_UNITS_SYSTEM_NAME, value)

    @property
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 20 characters maximum
        
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
            String, 20 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @description.setter
    def description(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DESCRIPTION, value)

    @property
    def PATHNAME(self) -> str:
        """PATHNAME property
        
        pathname
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 20 characters maximum
        
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
        
        pathname
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 20 characters maximum
        
        Note: both 'pathname' and 'PATHNAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PATHNAME)
        _value = cast(str, value)
        return _value

    @pathname.setter
    def pathname(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PATHNAME, value)

    @property
    def ACTIVE(self) -> int:
        """ACTIVE property
        
        active
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ACTIVE)
        _value = cast(int, value)
        return _value

    @property
    def active(self) -> int:
        """ACTIVE property
        
        active
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'active' and 'ACTIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ACTIVE)
        _value = cast(int, value)
        return _value

    @property
    def CASENUMBER(self) -> int:
        """CASENUMBER property
        
        number
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CASENUMBER)
        _value = cast(int, value)
        return _value

    @property
    def casenumber(self) -> int:
        """CASENUMBER property
        
        number
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'casenumber' and 'CASENUMBER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CASENUMBER)
        _value = cast(int, value)
        return _value

    @property
    def CHILDREN(self) -> ensobjlist:
        """CHILDREN property
        
        children
        
        Supported operations:
            getattr
        Datatype:
            Object, 2 element array
        
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
            Object, 2 element array
        
        Note: both 'children' and 'CHILDREN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CHILDREN)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def MACHINEARCH(self) -> str:
        """MACHINEARCH property
        
        machinearch
        
        Supported operations:
            getattr
        Datatype:
            String, 80 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MACHINEARCH)
        _value = cast(str, value)
        return _value

    @property
    def machinearch(self) -> str:
        """MACHINEARCH property
        
        machinearch
        
        Supported operations:
            getattr
        Datatype:
            String, 80 characters maximum
        
        Note: both 'machinearch' and 'MACHINEARCH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MACHINEARCH)
        _value = cast(str, value)
        return _value

    @property
    def SERVERDIR(self) -> str:
        """SERVERDIR property
        
        server directory
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERDIR)
        _value = cast(str, value)
        return _value

    @SERVERDIR.setter
    def SERVERDIR(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.SERVERDIR, value)

    @property
    def serverdir(self) -> str:
        """SERVERDIR property
        
        server directory
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'serverdir' and 'SERVERDIR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERDIR)
        _value = cast(str, value)
        return _value

    @serverdir.setter
    def serverdir(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.SERVERDIR, value)

    @property
    def SERVERCWD(self) -> object:
        """SERVERCWD property
        
        server working directory
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERCWD)
        _value = cast(object, value)
        return _value

    @property
    def servercwd(self) -> object:
        """SERVERCWD property
        
        server working directory
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'servercwd' and 'SERVERCWD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERCWD)
        _value = cast(object, value)
        return _value

    @property
    def SERVERCEIHOME(self) -> object:
        """SERVERCEIHOME property
        
        server CEI_HOME directory
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERCEIHOME)
        _value = cast(object, value)
        return _value

    @property
    def serverceihome(self) -> object:
        """SERVERCEIHOME property
        
        server CEI_HOME directory
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'serverceihome' and 'SERVERCEIHOME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERCEIHOME)
        _value = cast(object, value)
        return _value

    @property
    def DEFAULTREADERID(self) -> int:
        """DEFAULTREADERID property
        
        default reader ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTREADERID)
        _value = cast(int, value)
        return _value

    @DEFAULTREADERID.setter
    def DEFAULTREADERID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULTREADERID, value)

    @property
    def defaultreaderid(self) -> int:
        """DEFAULTREADERID property
        
        default reader ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'defaultreaderid' and 'DEFAULTREADERID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTREADERID)
        _value = cast(int, value)
        return _value

    @defaultreaderid.setter
    def defaultreaderid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULTREADERID, value)

    @property
    def SERVERBYTESWAP(self) -> int:
        """SERVERBYTESWAP property
        
        server byte swap
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.DATA_BIGENDIAN - big endian
            * ensight.objs.enums.DATA_LITTLEENDIAN - little endian
            * ensight.objs.enums.DATA_NATIVE - native endian
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERBYTESWAP)
        _value = cast(int, value)
        return _value

    @SERVERBYTESWAP.setter
    def SERVERBYTESWAP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SERVERBYTESWAP, value)

    @property
    def serverbyteswap(self) -> int:
        """SERVERBYTESWAP property
        
        server byte swap
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.DATA_BIGENDIAN - big endian
            * ensight.objs.enums.DATA_LITTLEENDIAN - little endian
            * ensight.objs.enums.DATA_NATIVE - native endian
        
        Note: both 'serverbyteswap' and 'SERVERBYTESWAP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERBYTESWAP)
        _value = cast(int, value)
        return _value

    @serverbyteswap.setter
    def serverbyteswap(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SERVERBYTESWAP, value)

    @property
    def JOBINFO(self) -> Dict[Any, Any]:
        """JOBINFO property
        
        Job Information
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.JOBINFO)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def jobinfo(self) -> Dict[Any, Any]:
        """JOBINFO property
        
        Job Information
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'jobinfo' and 'JOBINFO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.JOBINFO)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def SERVERINFO(self) -> Dict[Any, Any]:
        """SERVERINFO property
        
        server information
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERINFO)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def serverinfo(self) -> Dict[Any, Any]:
        """SERVERINFO property
        
        server information
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'serverinfo' and 'SERVERINFO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERINFO)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def REMOTEHOST(self) -> str:
        """REMOTEHOST property
        
        server host
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REMOTEHOST)
        _value = cast(str, value)
        return _value

    @REMOTEHOST.setter
    def REMOTEHOST(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.REMOTEHOST, value)

    @property
    def remotehost(self) -> str:
        """REMOTEHOST property
        
        server host
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'remotehost' and 'REMOTEHOST' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REMOTEHOST)
        _value = cast(str, value)
        return _value

    @remotehost.setter
    def remotehost(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.REMOTEHOST, value)

    @property
    def LPARTS(self) -> ensobjlist['ENS_LPART']:
        """LPARTS property
        
        partloader objects
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LPARTS)
        _value = cast(ensobjlist['ENS_LPART'], value)
        return _value

    @property
    def lparts(self) -> ensobjlist['ENS_LPART']:
        """LPARTS property
        
        partloader objects
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'lparts' and 'LPARTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LPARTS)
        _value = cast(ensobjlist['ENS_LPART'], value)
        return _value

    @property
    def GEOMETRY_FORM(self) -> int:
        """GEOMETRY_FORM property
        
        temporal geometry form
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.GEOM_NO_CHANGE - static
            * ensight.objs.enums.GEOM_COORD_CHANGE - changing coordinates
            * ensight.objs.enums.GEOM_CONN_CHANGE - changing connectivity
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GEOMETRY_FORM)
        _value = cast(int, value)
        return _value

    @property
    def geometry_form(self) -> int:
        """GEOMETRY_FORM property
        
        temporal geometry form
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.GEOM_NO_CHANGE - static
            * ensight.objs.enums.GEOM_COORD_CHANGE - changing coordinates
            * ensight.objs.enums.GEOM_CONN_CHANGE - changing connectivity
        
        Note: both 'geometry_form' and 'GEOMETRY_FORM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GEOMETRY_FORM)
        _value = cast(int, value)
        return _value

    @property
    def TIMEVALUES(self) -> object:
        """TIMEVALUES property
        
        master timeset values
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEVALUES)
        _value = cast(object, value)
        return _value

    @property
    def timevalues(self) -> object:
        """TIMEVALUES property
        
        master timeset values
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'timevalues' and 'TIMEVALUES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEVALUES)
        _value = cast(object, value)
        return _value

    @property
    def TIMESETS(self) -> List[dict]:
        """TIMESETS property
        
        timesets
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMESETS)
        _value = cast(List[dict], value)
        return _value

    @property
    def timesets(self) -> List[dict]:
        """TIMESETS property
        
        timesets
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'timesets' and 'TIMESETS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMESETS)
        _value = cast(List[dict], value)
        return _value

    @property
    def LINKED(self) -> int:
        """LINKED property
        
        linked
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINKED)
        _value = cast(int, value)
        return _value

    @LINKED.setter
    def LINKED(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINKED, value)

    @property
    def linked(self) -> int:
        """LINKED property
        
        linked
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'linked' and 'LINKED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINKED)
        _value = cast(int, value)
        return _value

    @linked.setter
    def linked(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINKED, value)

    @property
    def PARTNUMELE(self) -> Dict[Any, Any]:
        """PARTNUMELE property
        
        number of server elements
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTNUMELE)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def partnumele(self) -> Dict[Any, Any]:
        """PARTNUMELE property
        
        number of server elements
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'partnumele' and 'PARTNUMELE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTNUMELE)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def PARTNUMELECLIENT(self) -> Dict[Any, Any]:
        """PARTNUMELECLIENT property
        
        number of client elements
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTNUMELECLIENT)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def partnumeleclient(self) -> Dict[Any, Any]:
        """PARTNUMELECLIENT property
        
        number of client elements
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'partnumeleclient' and 'PARTNUMELECLIENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTNUMELECLIENT)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def LPARTNUMELE(self) -> Dict[Any, Any]:
        """LPARTNUMELE property
        
        number of lpart elements
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LPARTNUMELE)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def lpartnumele(self) -> Dict[Any, Any]:
        """LPARTNUMELE property
        
        number of lpart elements
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'lpartnumele' and 'LPARTNUMELE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LPARTNUMELE)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def VIEWPORTVIS(self) -> int:
        """VIEWPORTVIS property
        
        viewport case visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
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
        
        viewport case visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
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
    def SFTVARIABLE(self) -> ensobjlist['ENS_VAR']:
        """SFTVARIABLE property
        
        SFT vector variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @SFTVARIABLE.setter
    def SFTVARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTVARIABLE, value)

    @property
    def sftvariable(self) -> ensobjlist['ENS_VAR']:
        """SFTVARIABLE property
        
        SFT vector variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        
        Note: both 'sftvariable' and 'SFTVARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @sftvariable.setter
    def sftvariable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTVARIABLE, value)

    @property
    def SFTNORMALIZE(self) -> int:
        """SFTNORMALIZE property
        
        SFT normalize vector field
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTNORMALIZE)
        _value = cast(int, value)
        return _value

    @SFTNORMALIZE.setter
    def SFTNORMALIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTNORMALIZE, value)

    @property
    def sftnormalize(self) -> int:
        """SFTNORMALIZE property
        
        SFT normalize vector field
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'sftnormalize' and 'SFTNORMALIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTNORMALIZE)
        _value = cast(int, value)
        return _value

    @sftnormalize.setter
    def sftnormalize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTNORMALIZE, value)

    @property
    def SFTCONTRAST(self) -> int:
        """SFTCONTRAST property
        
        SFT contrast
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTCONTRAST)
        _value = cast(int, value)
        return _value

    @SFTCONTRAST.setter
    def SFTCONTRAST(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTCONTRAST, value)

    @property
    def sftcontrast(self) -> int:
        """SFTCONTRAST property
        
        SFT contrast
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'sftcontrast' and 'SFTCONTRAST' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTCONTRAST)
        _value = cast(int, value)
        return _value

    @sftcontrast.setter
    def sftcontrast(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTCONTRAST, value)

    @property
    def SFTDENSITY(self) -> float:
        """SFTDENSITY property
        
        SFT density
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTDENSITY)
        _value = cast(float, value)
        return _value

    @SFTDENSITY.setter
    def SFTDENSITY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTDENSITY, value)

    @property
    def sftdensity(self) -> float:
        """SFTDENSITY property
        
        SFT density
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'sftdensity' and 'SFTDENSITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTDENSITY)
        _value = cast(float, value)
        return _value

    @sftdensity.setter
    def sftdensity(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTDENSITY, value)

    @property
    def SFTBRIGHTNESS(self) -> float:
        """SFTBRIGHTNESS property
        
        SFT brightness
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTBRIGHTNESS)
        _value = cast(float, value)
        return _value

    @SFTBRIGHTNESS.setter
    def SFTBRIGHTNESS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTBRIGHTNESS, value)

    @property
    def sftbrightness(self) -> float:
        """SFTBRIGHTNESS property
        
        SFT brightness
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'sftbrightness' and 'SFTBRIGHTNESS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTBRIGHTNESS)
        _value = cast(float, value)
        return _value

    @sftbrightness.setter
    def sftbrightness(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTBRIGHTNESS, value)

    @property
    def SFTNORMLENGTH(self) -> float:
        """SFTNORMLENGTH property
        
        SFT length when field normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTNORMLENGTH)
        _value = cast(float, value)
        return _value

    @SFTNORMLENGTH.setter
    def SFTNORMLENGTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTNORMLENGTH, value)

    @property
    def sftnormlength(self) -> float:
        """SFTNORMLENGTH property
        
        SFT length when field normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'sftnormlength' and 'SFTNORMLENGTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTNORMLENGTH)
        _value = cast(float, value)
        return _value

    @sftnormlength.setter
    def sftnormlength(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTNORMLENGTH, value)

    @property
    def SFTNORMINTEGRATIONSTEP(self) -> float:
        """SFTNORMINTEGRATIONSTEP property
        
        SFT integration step when field normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTNORMINTEGRATIONSTEP)
        _value = cast(float, value)
        return _value

    @SFTNORMINTEGRATIONSTEP.setter
    def SFTNORMINTEGRATIONSTEP(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTNORMINTEGRATIONSTEP, value)

    @property
    def sftnormintegrationstep(self) -> float:
        """SFTNORMINTEGRATIONSTEP property
        
        SFT integration step when field normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'sftnormintegrationstep' and 'SFTNORMINTEGRATIONSTEP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTNORMINTEGRATIONSTEP)
        _value = cast(float, value)
        return _value

    @sftnormintegrationstep.setter
    def sftnormintegrationstep(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTNORMINTEGRATIONSTEP, value)

    @property
    def SFTLENGTH(self) -> float:
        """SFTLENGTH property
        
        SFT length when field is not normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTLENGTH)
        _value = cast(float, value)
        return _value

    @SFTLENGTH.setter
    def SFTLENGTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTLENGTH, value)

    @property
    def sftlength(self) -> float:
        """SFTLENGTH property
        
        SFT length when field is not normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'sftlength' and 'SFTLENGTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTLENGTH)
        _value = cast(float, value)
        return _value

    @sftlength.setter
    def sftlength(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTLENGTH, value)

    @property
    def SFTINTEGRATIONSTEP(self) -> float:
        """SFTINTEGRATIONSTEP property
        
        SFT integration step when field is not normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTINTEGRATIONSTEP)
        _value = cast(float, value)
        return _value

    @SFTINTEGRATIONSTEP.setter
    def SFTINTEGRATIONSTEP(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTINTEGRATIONSTEP, value)

    @property
    def sftintegrationstep(self) -> float:
        """SFTINTEGRATIONSTEP property
        
        SFT integration step when field is not normalized
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'sftintegrationstep' and 'SFTINTEGRATIONSTEP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SFTINTEGRATIONSTEP)
        _value = cast(float, value)
        return _value

    @sftintegrationstep.setter
    def sftintegrationstep(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SFTINTEGRATIONSTEP, value)

    @property
    def SERVERXML(self) -> str:
        """SERVERXML property
        
        server metadata (xml)
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERXML)
        _value = cast(str, value)
        return _value

    @property
    def serverxml(self) -> str:
        """SERVERXML property
        
        server metadata (xml)
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        Note: both 'serverxml' and 'SERVERXML' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SERVERXML)
        _value = cast(str, value)
        return _value

    @property
    def TEMPORAL_XY_QUERIES(self) -> int:
        """TEMPORAL_XY_QUERIES property
        
        Temporal state of server XY queries
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEMPORAL_XY_QUERIES)
        _value = cast(int, value)
        return _value

    @TEMPORAL_XY_QUERIES.setter
    def TEMPORAL_XY_QUERIES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEMPORAL_XY_QUERIES, value)

    @property
    def temporal_xy_queries(self) -> int:
        """TEMPORAL_XY_QUERIES property
        
        Temporal state of server XY queries
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'temporal_xy_queries' and 'TEMPORAL_XY_QUERIES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEMPORAL_XY_QUERIES)
        _value = cast(int, value)
        return _value

    @temporal_xy_queries.setter
    def temporal_xy_queries(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEMPORAL_XY_QUERIES, value)

    @property
    def LAST_DATA_RELOAD(self) -> int:
        """LAST_DATA_RELOAD property
        
        State of last reload_data() call
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums (bitfield):
            * ensight.objs.enums.RELOAD_NONE - No new information loaded
            * ensight.objs.enums.RELOAD_VARS - New variables have been loaded
            * ensight.objs.enums.RELOAD_QUERIES - New queries have been loaded
            * ensight.objs.enums.RELOAD_PARTS - New parts have been loaded
            * ensight.objs.enums.RELOAD_DATA - New data has been loaded
            * ensight.objs.enums.RELOAD_TIME - New timesteps have been loaded
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LAST_DATA_RELOAD)
        _value = cast(int, value)
        return _value

    @LAST_DATA_RELOAD.setter
    def LAST_DATA_RELOAD(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LAST_DATA_RELOAD, value)

    @property
    def last_data_reload(self) -> int:
        """LAST_DATA_RELOAD property
        
        State of last reload_data() call
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums (bitfield):
            * ensight.objs.enums.RELOAD_NONE - No new information loaded
            * ensight.objs.enums.RELOAD_VARS - New variables have been loaded
            * ensight.objs.enums.RELOAD_QUERIES - New queries have been loaded
            * ensight.objs.enums.RELOAD_PARTS - New parts have been loaded
            * ensight.objs.enums.RELOAD_DATA - New data has been loaded
            * ensight.objs.enums.RELOAD_TIME - New timesteps have been loaded
        
        Note: both 'last_data_reload' and 'LAST_DATA_RELOAD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LAST_DATA_RELOAD)
        _value = cast(int, value)
        return _value

    @last_data_reload.setter
    def last_data_reload(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LAST_DATA_RELOAD, value)

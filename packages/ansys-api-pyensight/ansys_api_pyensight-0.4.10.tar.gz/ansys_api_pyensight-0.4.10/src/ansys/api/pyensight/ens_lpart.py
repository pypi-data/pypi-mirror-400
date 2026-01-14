"""ens_lpart module

The ens_lpart module provides a proxy interface to EnSight ENS_LPART instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_STATE, ens_emitterobj

class ENS_LPART(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_LPART

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

    def load(self, *args, **kwargs) -> Any:
        """Load the part

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.load({arg_string})"
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
    def DTA_BLOCK(self) -> int:
        """DTA_BLOCK property
        
        Block
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DTA_BLOCK)
        _value = cast(int, value)
        return _value

    @property
    def dta_block(self) -> int:
        """DTA_BLOCK property
        
        Block
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'dta_block' and 'DTA_BLOCK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DTA_BLOCK)
        _value = cast(int, value)
        return _value

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
    def ENS_MATERIAL(self) -> str:
        """ENS_MATERIAL property
        
        Material
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_MATERIAL)
        _value = cast(str, value)
        return _value

    @ENS_MATERIAL.setter
    def ENS_MATERIAL(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_MATERIAL, value)

    @property
    def ens_material(self) -> str:
        """ENS_MATERIAL property
        
        Material
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_material' and 'ENS_MATERIAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_MATERIAL)
        _value = cast(str, value)
        return _value

    @ens_material.setter
    def ens_material(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_MATERIAL, value)

    @property
    def ENS_PARENT_PART(self) -> str:
        """ENS_PARENT_PART property
        
        Parent
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PARENT_PART)
        _value = cast(str, value)
        return _value

    @ENS_PARENT_PART.setter
    def ENS_PARENT_PART(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PARENT_PART, value)

    @property
    def ens_parent_part(self) -> str:
        """ENS_PARENT_PART property
        
        Parent
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_parent_part' and 'ENS_PARENT_PART' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PARENT_PART)
        _value = cast(str, value)
        return _value

    @ens_parent_part.setter
    def ens_parent_part(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PARENT_PART, value)

    @property
    def ENS_SYMMETRY_AXIS(self) -> str:
        """ENS_SYMMETRY_AXIS property
        
        Sym Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_SYMMETRY_AXIS)
        _value = cast(str, value)
        return _value

    @ENS_SYMMETRY_AXIS.setter
    def ENS_SYMMETRY_AXIS(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_SYMMETRY_AXIS, value)

    @property
    def ens_symmetry_axis(self) -> str:
        """ENS_SYMMETRY_AXIS property
        
        Sym Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_symmetry_axis' and 'ENS_SYMMETRY_AXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_SYMMETRY_AXIS)
        _value = cast(str, value)
        return _value

    @ens_symmetry_axis.setter
    def ens_symmetry_axis(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_SYMMETRY_AXIS, value)

    @property
    def ENS_SYMMETRY_COUNT(self) -> int:
        """ENS_SYMMETRY_COUNT property
        
        Sym Count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_SYMMETRY_COUNT)
        _value = cast(int, value)
        return _value

    @ENS_SYMMETRY_COUNT.setter
    def ENS_SYMMETRY_COUNT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_SYMMETRY_COUNT, value)

    @property
    def ens_symmetry_count(self) -> int:
        """ENS_SYMMETRY_COUNT property
        
        Sym Count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_symmetry_count' and 'ENS_SYMMETRY_COUNT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_SYMMETRY_COUNT)
        _value = cast(int, value)
        return _value

    @ens_symmetry_count.setter
    def ens_symmetry_count(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_SYMMETRY_COUNT, value)

    @property
    def ENS_TURBO_STAGE(self) -> str:
        """ENS_TURBO_STAGE property
        
        Turbo Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_STAGE)
        _value = cast(str, value)
        return _value

    @ENS_TURBO_STAGE.setter
    def ENS_TURBO_STAGE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_STAGE, value)

    @property
    def ens_turbo_stage(self) -> str:
        """ENS_TURBO_STAGE property
        
        Turbo Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_turbo_stage' and 'ENS_TURBO_STAGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_STAGE)
        _value = cast(str, value)
        return _value

    @ens_turbo_stage.setter
    def ens_turbo_stage(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_STAGE, value)

    @property
    def ENS_TURBO_VIEW(self) -> str:
        """ENS_TURBO_VIEW property
        
        Turbo Kind
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_VIEW)
        _value = cast(str, value)
        return _value

    @ENS_TURBO_VIEW.setter
    def ENS_TURBO_VIEW(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_VIEW, value)

    @property
    def ens_turbo_view(self) -> str:
        """ENS_TURBO_VIEW property
        
        Turbo Kind
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_turbo_view' and 'ENS_TURBO_VIEW' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_VIEW)
        _value = cast(str, value)
        return _value

    @ens_turbo_view.setter
    def ens_turbo_view(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_VIEW, value)

    @property
    def ENS_TURBO_VDIM(self) -> str:
        """ENS_TURBO_VDIM property
        
        Turbo Vports
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_VDIM)
        _value = cast(str, value)
        return _value

    @ENS_TURBO_VDIM.setter
    def ENS_TURBO_VDIM(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_VDIM, value)

    @property
    def ens_turbo_vdim(self) -> str:
        """ENS_TURBO_VDIM property
        
        Turbo Vports
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_turbo_vdim' and 'ENS_TURBO_VDIM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_VDIM)
        _value = cast(str, value)
        return _value

    @ens_turbo_vdim.setter
    def ens_turbo_vdim(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_VDIM, value)

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
    def MESHTYPE(self) -> int:
        """MESHTYPE property
        
        meshtype
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHTYPE)
        _value = cast(int, value)
        return _value

    @property
    def meshtype(self) -> int:
        """MESHTYPE property
        
        meshtype
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'meshtype' and 'MESHTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHTYPE)
        _value = cast(int, value)
        return _value

    @property
    def DIMENSIONS(self) -> List[int]:
        """DIMENSIONS property
        
        structured dimensions
        
        Supported operations:
            getattr
        Datatype:
            Integer, 6 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSIONS)
        _value = cast(List[int], value)
        return _value

    @property
    def dimensions(self) -> List[int]:
        """DIMENSIONS property
        
        structured dimensions
        
        Supported operations:
            getattr
        Datatype:
            Integer, 6 element array
        
        Note: both 'dimensions' and 'DIMENSIONS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSIONS)
        _value = cast(List[int], value)
        return _value

    @property
    def ELEMCOUNT(self) -> List[int]:
        """ELEMCOUNT property
        
        element count
        
        Supported operations:
            getattr
        Datatype:
            Integer, 40 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ELEMCOUNT)
        _value = cast(List[int], value)
        return _value

    @property
    def elemcount(self) -> List[int]:
        """ELEMCOUNT property
        
        element count
        
        Supported operations:
            getattr
        Datatype:
            Integer, 40 element array
        
        Note: both 'elemcount' and 'ELEMCOUNT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ELEMCOUNT)
        _value = cast(List[int], value)
        return _value

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
    def DELTA(self) -> List[int]:
        """DELTA property
        
        load delta
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DELTA)
        _value = cast(List[int], value)
        return _value

    @DELTA.setter
    def DELTA(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.DELTA, value)

    @property
    def delta(self) -> List[int]:
        """DELTA property
        
        load delta
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        Note: both 'delta' and 'DELTA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DELTA)
        _value = cast(List[int], value)
        return _value

    @delta.setter
    def delta(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.DELTA, value)

    @property
    def NODEMIN(self) -> List[int]:
        """NODEMIN property
        
        minimum node numbers
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEMIN)
        _value = cast(List[int], value)
        return _value

    @NODEMIN.setter
    def NODEMIN(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEMIN, value)

    @property
    def nodemin(self) -> List[int]:
        """NODEMIN property
        
        minimum node numbers
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        Note: both 'nodemin' and 'NODEMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEMIN)
        _value = cast(List[int], value)
        return _value

    @nodemin.setter
    def nodemin(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEMIN, value)

    @property
    def NODEMAX(self) -> List[int]:
        """NODEMAX property
        
        maximum node numbers
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEMAX)
        _value = cast(List[int], value)
        return _value

    @NODEMAX.setter
    def NODEMAX(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEMAX, value)

    @property
    def nodemax(self) -> List[int]:
        """NODEMAX property
        
        maximum node numbers
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        Note: both 'nodemax' and 'NODEMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEMAX)
        _value = cast(List[int], value)
        return _value

    @nodemax.setter
    def nodemax(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEMAX, value)

    @property
    def NODESTEP(self) -> List[int]:
        """NODESTEP property
        
        step factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODESTEP)
        _value = cast(List[int], value)
        return _value

    @NODESTEP.setter
    def NODESTEP(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.NODESTEP, value)

    @property
    def nodestep(self) -> List[int]:
        """NODESTEP property
        
        step factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        
        Note: both 'nodestep' and 'NODESTEP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODESTEP)
        _value = cast(List[int], value)
        return _value

    @nodestep.setter
    def nodestep(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.NODESTEP, value)

    @property
    def DOMAIN(self) -> int:
        """DOMAIN property
        
        domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ZONES_DEF - Default Zones
            * ensight.objs.enums.ZONES_EXT - External Zones
            * ensight.objs.enums.ZONES_INT - Internal Zones
            * ensight.objs.enums.ZONES_BOTH - All Zones
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DOMAIN)
        _value = cast(int, value)
        return _value

    @DOMAIN.setter
    def DOMAIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOMAIN, value)

    @property
    def domain(self) -> int:
        """DOMAIN property
        
        domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ZONES_DEF - Default Zones
            * ensight.objs.enums.ZONES_EXT - External Zones
            * ensight.objs.enums.ZONES_INT - Internal Zones
            * ensight.objs.enums.ZONES_BOTH - All Zones
        
        Note: both 'domain' and 'DOMAIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DOMAIN)
        _value = cast(int, value)
        return _value

    @domain.setter
    def domain(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOMAIN, value)

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
    def FLOW3DINFO(self) -> object:
        """FLOW3DINFO property
        
        Flow3D dataset information
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FLOW3DINFO)
        _value = cast(object, value)
        return _value

    @property
    def flow3dinfo(self) -> object:
        """FLOW3DINFO property
        
        Flow3D dataset information
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'flow3dinfo' and 'FLOW3DINFO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FLOW3DINFO)
        _value = cast(object, value)
        return _value

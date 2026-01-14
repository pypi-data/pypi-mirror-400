"""ens_var module

The ens_var module provides a proxy interface to EnSight ENS_VAR instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_VAR(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_VAR

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

    def realize(self, *args, **kwargs) -> Any:
        """Activate a stub computed variable

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.realize({arg_string})"
        return self._session.cmd(cmd)

    def histogram(self, *args, **kwargs) -> Any:
        """Compute the histogram of a variable

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.histogram({arg_string})"
        return self._session.cmd(cmd)

    def dependent_vars(self, *args, **kwargs) -> Any:
        """Add dependent temporary variable list

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.dependent_vars({arg_string})"
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
    def CFD_VAR(self) -> str:
        """CFD_VAR property
        
        CFD Type
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CFD_VAR)
        _value = cast(str, value)
        return _value

    @property
    def cfd_var(self) -> str:
        """CFD_VAR property
        
        CFD Type
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        Note: both 'cfd_var' and 'CFD_VAR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CFD_VAR)
        _value = cast(str, value)
        return _value

    @property
    def ENS_UNITS_LABEL(self) -> str:
        """ENS_UNITS_LABEL property
        
        Units
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_UNITS_LABEL)
        _value = cast(str, value)
        return _value

    @ENS_UNITS_LABEL.setter
    def ENS_UNITS_LABEL(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_UNITS_LABEL, value)

    @property
    def ens_units_label(self) -> str:
        """ENS_UNITS_LABEL property
        
        Units
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_units_label' and 'ENS_UNITS_LABEL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_UNITS_LABEL)
        _value = cast(str, value)
        return _value

    @ens_units_label.setter
    def ens_units_label(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_UNITS_LABEL, value)

    @property
    def ENS_UNITS_DIMS(self) -> str:
        """ENS_UNITS_DIMS property
        
        Unit Dimensions
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_UNITS_DIMS)
        _value = cast(str, value)
        return _value

    @ENS_UNITS_DIMS.setter
    def ENS_UNITS_DIMS(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_UNITS_DIMS, value)

    @property
    def ens_units_dims(self) -> str:
        """ENS_UNITS_DIMS property
        
        Unit Dimensions
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_units_dims' and 'ENS_UNITS_DIMS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_UNITS_DIMS)
        _value = cast(str, value)
        return _value

    @ens_units_dims.setter
    def ens_units_dims(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_UNITS_DIMS, value)

    @property
    def FEA_VAR(self) -> str:
        """FEA_VAR property
        
        FEA Type
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FEA_VAR)
        _value = cast(str, value)
        return _value

    @property
    def fea_var(self) -> str:
        """FEA_VAR property
        
        FEA Type
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        Note: both 'fea_var' and 'FEA_VAR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FEA_VAR)
        _value = cast(str, value)
        return _value

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
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        Description
        
        Supported operations:
            getattr
        Datatype:
            String, 50 characters maximum
        
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
            String, 50 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

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
    def ACTIVE(self) -> int:
        """ACTIVE property
        
        Activated
        
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
        
        Activated
        
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
    def WHICH_HISTOGRAM(self) -> int:
        """WHICH_HISTOGRAM property
        
        Use dynamic histogram
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.WHICH_HISTOGRAM)
        _value = cast(int, value)
        return _value

    @WHICH_HISTOGRAM.setter
    def WHICH_HISTOGRAM(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.WHICH_HISTOGRAM, value)

    @property
    def which_histogram(self) -> int:
        """WHICH_HISTOGRAM property
        
        Use dynamic histogram
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'which_histogram' and 'WHICH_HISTOGRAM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.WHICH_HISTOGRAM)
        _value = cast(int, value)
        return _value

    @which_histogram.setter
    def which_histogram(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.WHICH_HISTOGRAM, value)

    @property
    def ORDER(self) -> int:
        """ORDER property
        
        Variable order
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORDER)
        _value = cast(int, value)
        return _value

    @property
    def order(self) -> int:
        """ORDER property
        
        Variable order
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'order' and 'ORDER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORDER)
        _value = cast(int, value)
        return _value

    @property
    def LOCATION(self) -> int:
        """LOCATION property
        
        Location
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ENS_VAR_CASE - Case
            * ensight.objs.enums.ENS_VAR_ELEM - Element
            * ensight.objs.enums.ENS_VAR_NODE - Node
            * ensight.objs.enums.ENS_VAR_ENOD - Point element
            * ensight.objs.enums.ENS_VAR_CONSTANT_PER_PART - Part
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATION)
        _value = cast(int, value)
        return _value

    @property
    def location(self) -> int:
        """LOCATION property
        
        Location
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ENS_VAR_CASE - Case
            * ensight.objs.enums.ENS_VAR_ELEM - Element
            * ensight.objs.enums.ENS_VAR_NODE - Node
            * ensight.objs.enums.ENS_VAR_ENOD - Point element
            * ensight.objs.enums.ENS_VAR_CONSTANT_PER_PART - Part
        
        Note: both 'location' and 'LOCATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOCATION)
        _value = cast(int, value)
        return _value

    @property
    def VARTYPE(self) -> int:
        """VARTYPE property
        
        Variable type
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARTYPE)
        _value = cast(int, value)
        return _value

    @property
    def vartype(self) -> int:
        """VARTYPE property
        
        Variable type
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'vartype' and 'VARTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARTYPE)
        _value = cast(int, value)
        return _value

    @property
    def VARTYPEENUM(self) -> int:
        """VARTYPEENUM property
        
        Type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ENS_VAR_SCALAR - Scalar
            * ensight.objs.enums.ENS_VAR_VECTOR - Vector
            * ensight.objs.enums.ENS_VAR_TENSOR - Tensor
            * ensight.objs.enums.ENS_VAR_SCALAR_COMPLEX - Scalar complex
            * ensight.objs.enums.ENS_VAR_VECTOR_COMPLEX - Vector complex
            * ensight.objs.enums.ENS_VAR_CONSTANT - Constant
            * ensight.objs.enums.ENS_VAR_TIME_FUNC - Time
            * ensight.objs.enums.ENS_VAR_COORDS - Coordinates
            * ensight.objs.enums.ENS_VAR_CONSTANT_PER_PART - Constant per part
            * ensight.objs.enums.ENS_VAR_UNKNOWN - Unknown
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARTYPEENUM)
        _value = cast(int, value)
        return _value

    @property
    def vartypeenum(self) -> int:
        """VARTYPEENUM property
        
        Type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ENS_VAR_SCALAR - Scalar
            * ensight.objs.enums.ENS_VAR_VECTOR - Vector
            * ensight.objs.enums.ENS_VAR_TENSOR - Tensor
            * ensight.objs.enums.ENS_VAR_SCALAR_COMPLEX - Scalar complex
            * ensight.objs.enums.ENS_VAR_VECTOR_COMPLEX - Vector complex
            * ensight.objs.enums.ENS_VAR_CONSTANT - Constant
            * ensight.objs.enums.ENS_VAR_TIME_FUNC - Time
            * ensight.objs.enums.ENS_VAR_COORDS - Coordinates
            * ensight.objs.enums.ENS_VAR_CONSTANT_PER_PART - Constant per part
            * ensight.objs.enums.ENS_VAR_UNKNOWN - Unknown
        
        Note: both 'vartypeenum' and 'VARTYPEENUM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARTYPEENUM)
        _value = cast(int, value)
        return _value

    @property
    def COMPUTED(self) -> int:
        """COMPUTED property
        
        Computed
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COMPUTED)
        _value = cast(int, value)
        return _value

    @property
    def computed(self) -> int:
        """COMPUTED property
        
        Computed
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'computed' and 'COMPUTED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COMPUTED)
        _value = cast(int, value)
        return _value

    @property
    def EXPRESSION(self) -> str:
        """EXPRESSION property
        
        Computed expression
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.EXPRESSION)
        _value = cast(str, value)
        return _value

    @property
    def expression(self) -> str:
        """EXPRESSION property
        
        Computed expression
        
        Supported operations:
            getattr
        Datatype:
            String, scalar
        
        Note: both 'expression' and 'EXPRESSION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.EXPRESSION)
        _value = cast(str, value)
        return _value

    @property
    def ID(self) -> int:
        """ID property
        
        Variable ID
        
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
        
        Variable ID
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'id' and 'ID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ID)
        _value = cast(int, value)
        return _value

    @property
    def MINMAX(self) -> float:
        """MINMAX property
        
        Min/Max
        
        Supported operations:
            getattr
        Datatype:
            Float, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MINMAX)
        _value = cast(float, value)
        return _value

    @property
    def minmax(self) -> float:
        """MINMAX property
        
        Min/Max
        
        Supported operations:
            getattr
        Datatype:
            Float, 0 element array
        
        Note: both 'minmax' and 'MINMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MINMAX)
        _value = cast(float, value)
        return _value

    @property
    def PALID(self) -> int:
        """PALID property
        
        Palette ID
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PALID)
        _value = cast(int, value)
        return _value

    @property
    def palid(self) -> int:
        """PALID property
        
        Palette ID
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'palid' and 'PALID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PALID)
        _value = cast(int, value)
        return _value

    @property
    def LEGEND(self) -> List['ENS_ANNOT']:
        """LEGEND property
        
        Legends
        
        Supported operations:
            getattr
        Datatype:
            ENS_ANNOT Legend, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGEND)
        _value = cast(List['ENS_ANNOT'], value)
        return _value

    @property
    def legend(self) -> List['ENS_ANNOT']:
        """LEGEND property
        
        Legends
        
        Supported operations:
            getattr
        Datatype:
            ENS_ANNOT Legend, 0 element array
        
        Note: both 'legend' and 'LEGEND' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LEGEND)
        _value = cast(List['ENS_ANNOT'], value)
        return _value

    @property
    def EXIST_CASE(self) -> List[int]:
        """EXIST_CASE property
        
        Exists in case
        
        Supported operations:
            getattr
        Datatype:
            Boolean, 32 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.EXIST_CASE)
        _value = cast(List[int], value)
        return _value

    @property
    def exist_case(self) -> List[int]:
        """EXIST_CASE property
        
        Exists in case
        
        Supported operations:
            getattr
        Datatype:
            Boolean, 32 element array
        
        Note: both 'exist_case' and 'EXIST_CASE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.EXIST_CASE)
        _value = cast(List[int], value)
        return _value

    @property
    def PRIVATE(self) -> int:
        """PRIVATE property
        
        EnSight 'hidden' variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PRIVATE)
        _value = cast(int, value)
        return _value

    @PRIVATE.setter
    def PRIVATE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PRIVATE, value)

    @property
    def private(self) -> int:
        """PRIVATE property
        
        EnSight 'hidden' variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'private' and 'PRIVATE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PRIVATE)
        _value = cast(int, value)
        return _value

    @private.setter
    def private(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PRIVATE, value)

    @property
    def SEQUENCE(self) -> int:
        """SEQUENCE property
        
        Recompute sequence number
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SEQUENCE)
        _value = cast(int, value)
        return _value

    @property
    def sequence(self) -> int:
        """SEQUENCE property
        
        Recompute sequence number
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'sequence' and 'SEQUENCE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SEQUENCE)
        _value = cast(int, value)
        return _value

    @property
    def PALETTE(self) -> ensobjlist['ENS_PALETTE']:
        """PALETTE property
        
        Palette
        
        Supported operations:
            getattr
        Datatype:
            ENS_PALETTE Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PALETTE)
        _value = cast(ensobjlist['ENS_PALETTE'], value)
        return _value

    @property
    def palette(self) -> ensobjlist['ENS_PALETTE']:
        """PALETTE property
        
        Palette
        
        Supported operations:
            getattr
        Datatype:
            ENS_PALETTE Object, 0 element array
        
        Note: both 'palette' and 'PALETTE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PALETTE)
        _value = cast(ensobjlist['ENS_PALETTE'], value)
        return _value

    @property
    def PARTS(self) -> ensobjlist['ENS_PART']:
        """PARTS property
        
        Parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def parts(self) -> ensobjlist['ENS_PART']:
        """PARTS property
        
        Parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'parts' and 'PARTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def CONSTANT_VALUE(self) -> float:
        """CONSTANT_VALUE property
        
        Constant value
        
        Supported operations:
            getattr
        Datatype:
            Float, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTANT_VALUE)
        _value = cast(float, value)
        return _value

    @property
    def constant_value(self) -> float:
        """CONSTANT_VALUE property
        
        Constant value
        
        Supported operations:
            getattr
        Datatype:
            Float, 0 element array
        
        Note: both 'constant_value' and 'CONSTANT_VALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTANT_VALUE)
        _value = cast(float, value)
        return _value

    @property
    def MINMAXCONST(self) -> float:
        """MINMAXCONST property
        
        Range
        
        Supported operations:
            getattr
        Datatype:
            Float, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MINMAXCONST)
        _value = cast(float, value)
        return _value

    @property
    def minmaxconst(self) -> float:
        """MINMAXCONST property
        
        Range
        
        Supported operations:
            getattr
        Datatype:
            Float, 0 element array
        
        Note: both 'minmaxconst' and 'MINMAXCONST' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MINMAXCONST)
        _value = cast(float, value)
        return _value

    @property
    def OVERRIDELTACTIVE(self) -> int:
        """OVERRIDELTACTIVE property
        
        Active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTACTIVE)
        _value = cast(int, value)
        return _value

    @OVERRIDELTACTIVE.setter
    def OVERRIDELTACTIVE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTACTIVE, value)

    @property
    def overrideltactive(self) -> int:
        """OVERRIDELTACTIVE property
        
        Active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'overrideltactive' and 'OVERRIDELTACTIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTACTIVE)
        _value = cast(int, value)
        return _value

    @overrideltactive.setter
    def overrideltactive(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTACTIVE, value)

    @property
    def OVERRIDELTUSEABS(self) -> int:
        """OVERRIDELTUSEABS property
        
        Use abs(constant)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTUSEABS)
        _value = cast(int, value)
        return _value

    @OVERRIDELTUSEABS.setter
    def OVERRIDELTUSEABS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTUSEABS, value)

    @property
    def overrideltuseabs(self) -> int:
        """OVERRIDELTUSEABS property
        
        Use abs(constant)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'overrideltuseabs' and 'OVERRIDELTUSEABS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTUSEABS)
        _value = cast(int, value)
        return _value

    @overrideltuseabs.setter
    def overrideltuseabs(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTUSEABS, value)

    @property
    def OVERRIDELTMIN(self) -> float:
        """OVERRIDELTMIN property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTMIN)
        _value = cast(float, value)
        return _value

    @OVERRIDELTMIN.setter
    def OVERRIDELTMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTMIN, value)

    @property
    def overrideltmin(self) -> float:
        """OVERRIDELTMIN property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'overrideltmin' and 'OVERRIDELTMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTMIN)
        _value = cast(float, value)
        return _value

    @overrideltmin.setter
    def overrideltmin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTMIN, value)

    @property
    def OVERRIDELTRGB(self) -> List[float]:
        """OVERRIDELTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTRGB)
        _value = cast(List[float], value)
        return _value

    @OVERRIDELTRGB.setter
    def OVERRIDELTRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTRGB, value)

    @property
    def overrideltrgb(self) -> List[float]:
        """OVERRIDELTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'overrideltrgb' and 'OVERRIDELTRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDELTRGB)
        _value = cast(List[float], value)
        return _value

    @overrideltrgb.setter
    def overrideltrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDELTRGB, value)

    @property
    def OVERRIDEGTACTIVE(self) -> int:
        """OVERRIDEGTACTIVE property
        
        Active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTACTIVE)
        _value = cast(int, value)
        return _value

    @OVERRIDEGTACTIVE.setter
    def OVERRIDEGTACTIVE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTACTIVE, value)

    @property
    def overridegtactive(self) -> int:
        """OVERRIDEGTACTIVE property
        
        Active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'overridegtactive' and 'OVERRIDEGTACTIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTACTIVE)
        _value = cast(int, value)
        return _value

    @overridegtactive.setter
    def overridegtactive(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTACTIVE, value)

    @property
    def OVERRIDEGTUSEABS(self) -> int:
        """OVERRIDEGTUSEABS property
        
        Use abs(constant)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTUSEABS)
        _value = cast(int, value)
        return _value

    @OVERRIDEGTUSEABS.setter
    def OVERRIDEGTUSEABS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTUSEABS, value)

    @property
    def overridegtuseabs(self) -> int:
        """OVERRIDEGTUSEABS property
        
        Use abs(constant)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'overridegtuseabs' and 'OVERRIDEGTUSEABS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTUSEABS)
        _value = cast(int, value)
        return _value

    @overridegtuseabs.setter
    def overridegtuseabs(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTUSEABS, value)

    @property
    def OVERRIDEGTMIN(self) -> float:
        """OVERRIDEGTMIN property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTMIN)
        _value = cast(float, value)
        return _value

    @OVERRIDEGTMIN.setter
    def OVERRIDEGTMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTMIN, value)

    @property
    def overridegtmin(self) -> float:
        """OVERRIDEGTMIN property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'overridegtmin' and 'OVERRIDEGTMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTMIN)
        _value = cast(float, value)
        return _value

    @overridegtmin.setter
    def overridegtmin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTMIN, value)

    @property
    def OVERRIDEGTRGB(self) -> List[float]:
        """OVERRIDEGTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTRGB)
        _value = cast(List[float], value)
        return _value

    @OVERRIDEGTRGB.setter
    def OVERRIDEGTRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTRGB, value)

    @property
    def overridegtrgb(self) -> List[float]:
        """OVERRIDEGTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'overridegtrgb' and 'OVERRIDEGTRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDEGTRGB)
        _value = cast(List[float], value)
        return _value

    @overridegtrgb.setter
    def overridegtrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDEGTRGB, value)

    @property
    def OVERRIDERANGEACTIVE(self) -> int:
        """OVERRIDERANGEACTIVE property
        
        Active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEACTIVE)
        _value = cast(int, value)
        return _value

    @OVERRIDERANGEACTIVE.setter
    def OVERRIDERANGEACTIVE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEACTIVE, value)

    @property
    def overriderangeactive(self) -> int:
        """OVERRIDERANGEACTIVE property
        
        Active
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'overriderangeactive' and 'OVERRIDERANGEACTIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEACTIVE)
        _value = cast(int, value)
        return _value

    @overriderangeactive.setter
    def overriderangeactive(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEACTIVE, value)

    @property
    def OVERRIDERANGEUSEABS(self) -> int:
        """OVERRIDERANGEUSEABS property
        
        Use abs(constant)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEUSEABS)
        _value = cast(int, value)
        return _value

    @OVERRIDERANGEUSEABS.setter
    def OVERRIDERANGEUSEABS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEUSEABS, value)

    @property
    def overriderangeuseabs(self) -> int:
        """OVERRIDERANGEUSEABS property
        
        Use abs(constant)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'overriderangeuseabs' and 'OVERRIDERANGEUSEABS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEUSEABS)
        _value = cast(int, value)
        return _value

    @overriderangeuseabs.setter
    def overriderangeuseabs(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEUSEABS, value)

    @property
    def OVERRIDERANGEMIN(self) -> float:
        """OVERRIDERANGEMIN property
        
        Min Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEMIN)
        _value = cast(float, value)
        return _value

    @OVERRIDERANGEMIN.setter
    def OVERRIDERANGEMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEMIN, value)

    @property
    def overriderangemin(self) -> float:
        """OVERRIDERANGEMIN property
        
        Min Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'overriderangemin' and 'OVERRIDERANGEMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEMIN)
        _value = cast(float, value)
        return _value

    @overriderangemin.setter
    def overriderangemin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEMIN, value)

    @property
    def OVERRIDERANGEMAX(self) -> float:
        """OVERRIDERANGEMAX property
        
        Max Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEMAX)
        _value = cast(float, value)
        return _value

    @OVERRIDERANGEMAX.setter
    def OVERRIDERANGEMAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEMAX, value)

    @property
    def overriderangemax(self) -> float:
        """OVERRIDERANGEMAX property
        
        Max Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'overriderangemax' and 'OVERRIDERANGEMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGEMAX)
        _value = cast(float, value)
        return _value

    @overriderangemax.setter
    def overriderangemax(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGEMAX, value)

    @property
    def OVERRIDERANGERGB(self) -> List[float]:
        """OVERRIDERANGERGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGERGB)
        _value = cast(List[float], value)
        return _value

    @OVERRIDERANGERGB.setter
    def OVERRIDERANGERGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGERGB, value)

    @property
    def overriderangergb(self) -> List[float]:
        """OVERRIDERANGERGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'overriderangergb' and 'OVERRIDERANGERGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OVERRIDERANGERGB)
        _value = cast(List[float], value)
        return _value

    @overriderangergb.setter
    def overriderangergb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.OVERRIDERANGERGB, value)

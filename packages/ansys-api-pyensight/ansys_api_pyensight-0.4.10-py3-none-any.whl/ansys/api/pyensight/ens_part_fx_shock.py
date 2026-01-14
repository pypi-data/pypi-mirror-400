"""ens_part_fx_shock module

The ens_part_fx_shock module provides a proxy interface to EnSight ENS_PART_FX_SHOCK instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from ansys.api.pyensight.ens_part import ENS_PART
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_PART_FX_SHOCK(ENS_PART):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_PART

    Args:
        *args:
            Superclass (ENS_PART) arguments
        **kwargs:
            Superclass (ENS_PART) keyword arguments

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

    def createpart(self, *args, **kwargs) -> Any:
        """Create a new dependent part
        
        Create a new part using the attributes on a default part.
        
        Args:
            name:
                The name of the new part to be created.
            parent:
                The (optional) object (case or group object) that should become the tree parent.
            sources:
                A list of objects that will become the computational parents of the new part.
            record:
                If set to a non-zero value, the operation should be journaled.
            raw_defaults:
                By default some part creation will use things like current tool locations to set up initial attributes.
                If set to a non-zero value, current ENS_TOOL settings will be ignored and the default part attributes used instead.
            attributes:
                Set to a list of attributes to be set and restored on the default part before/after the creation operation.
        
        Returns:
            The newly created part object.
        
        Examples:
            ::
        
                clip = ensight.objs.core.DEFAULTPARTS[ensight.PART_CLIP_PLANE]
                attrs = []
                attrs.append(['MESHPLANE', 1])
                attrs.append(['TOOL', 9])
                attrs.append(['VALUE', 0.55])
                attrs.append(['DOMAIN', 0])
                parent = ensight.objs.core.PARTS[2]
                new_part = clip.createpart(name='Hello', sources=[parent], attributes=attrs)

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.createpart({arg_string})"
        return self._session.cmd(cmd)

    def attrgroupinfo(self, *args, **kwargs) -> Any:
        """Get information about GUI groups for this part's attributes

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

    def realtimemode(self, *args, **kwargs) -> Any:
        """Change the realtime mode

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.realtimemode({arg_string})"
        return self._session.cmd(cmd)

    def tracepaths(self, variables: Optional[List[Any]] = None) -> List[Any]:
        """This method returns the point and time values of particle traces.
        
        For an :class:`pyensight.ens_part_particle_trace.ENS_PART_PARTICLE_TRACE`
        instance, this method will return the data spce coordinates and time of each
        particle trace point.  Optionally, it can return variable values sampled at
        those coordinates.
        
        Args:
            variables:
                An optional list of variable references.  A mixture of ENS_VAR objects,
                variable names (string) or variable ids (integers) is allowed.
        
        Returns:
            If ``variables`` is not specified, the return value is a list of lists.  There
            is one list for each trace.   Each point withing the trace list is represented
            as a list of four floats representing the x,y,z,t values for the point::
        
                [[[x0,y0,z0,t0], [x1,y1,z1,t1], ...], [trace 2], ... ]
        
        
            If ``variables`` is specified, the return value is a list of lists of lists.
            There is one list for each trace, one list for each point and a list of
            lists for each variable.  For a scalar field 'a' and a vector field 'b'::
        
                [[[[a0], [b0x,b0y,b0z]], [[a1], [b1,b1y,b1z]], ...], [trace 2], ...]
        
        Example:
            ::
        
                # get the particle trace part
                p = session.ensight.objs.core.PARTS["particletrace"][0]
                # get the coordinates of the 5th trace
                traces = p.tracepaths()
                coords = []
                # walk the 5th trace
                for point in traces[5]:
                    coords.append(point[0:3])
                print(f"Coords = {coords}")
                # get the velocity (vector) and pressure (scalar) values
                # on the particle trace points from the 5th trace
                traces = p.tracepaths(variables=["velocity", "pressure"])
                pressure = []
                velocity = []
                # walk the 5th trace
                for point in traces[5]:
                    velocity.append(point[0])   # velocity is first in variables
                    pressure.append(point[1][0])  # grab just the pressure scalar value
                print(f"Velocities = {velocity}")
                print(f"Pressure = {pressure}")

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(f"variables={variables.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.tracepaths({arg_string})"
        return self._session.cmd(cmd)

    def simba_tracepaths(self, variables: Optional[List[Any]]=None) -> dict:
        """Return the paths for a particle trace part as needed by Fluids UI

        """
        import numpy
        arg_obj = f"{self._remote_obj()}"
        arg_list = []
        arg_list.append(variables.__repr__())
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.simba_tracepaths({arg_string})"
        if variables:
            self._session.cmd(f"enscl._simba_traces={cmd}", do_eval=False)
            cmd = "{key:[value.shape, value.dtype.str, value.tobytes()] for (key, value)"
            cmd += " in enscl._simba_traces.items() if key !='variables'}"
            ret_dict_coords = self._session.cmd(cmd)
            cmd = "{key:[value.shape, value.dtype.str, value.tobytes()] for (key, value)"
            cmd += " in enscl._simba_traces['variables'].items()}"
            ret_dict_vars = self._session.cmd(cmd)
            ret_dict = {}
            for key, value in ret_dict_coords.items():
                ret_dict[key] = numpy.frombuffer(value[2], dtype=value[1]).reshape(value[0])
            ret_dict["variables"] = {}
            for key, value in ret_dict_vars.items():
                ret_dict["variables"][key] = numpy.frombuffer(value[2], dtype=value[1]).reshape(value[0])
        else:
            cmd_wrap = f"{{key:[value.shape, value.dtype.str, value.tobytes()] for (key, value) in {cmd}.items()}}"
            ret_dict = self._session.cmd(cmd_wrap)
            for key, value in ret_dict.items():
                ret_dict[key] = numpy.frombuffer(value[2], dtype=value[1]).reshape(value[0])
        return ret_dict

    def cmdlang_rec_info(self, *args, **kwargs) -> Any:
        """Return command language bits for part selection

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.cmdlang_rec_info({arg_string})"
        return self._session.cmd(cmd)

    def get_values(self, variables: List[Any], ids: Optional[List[int]] = None,            use_nan: int = 0, activate: int = 0) -> dict:
        """This method returns nodal or element values for specified variables on the part.
        
        Args:
            variables:
                A list of variable references.  A mixture of ENS_VAR objects,
                variable names (string) or variable ids (integers).
            ids:
                This keyword can be used to restrict the output
                to a specific collection of element or node ids. If you restrict
                to a given list of ids and ids are not present then an empty
                dictionary will be returned. It is not possible to specify
                separate lists for both node and element ids, so the caller
                must separate these into two calls. Select your part in the
                part list and query the part.  The resulting dialog will
                tell you if you have ids and the ranges of the node and/or
                element ids.  This feature can also be used to "batch" the
                operation.
            use_nan:
                EnSight uses a specific value for the 'Undefined' value
                (ensight.Undefined), ``use_nan`` is set to 1, the API will
                return NumPy NaN values wherever this value would be returned.
            activate:
                By default, if a variable specified in ``variables`` is not active,
                this method will throw an exception.  If 1 is specified,
                any inactive variables will be activated as needed.
        
        Returns:
            The returned value is a dictionary.  The keys to the dictionary
            are the objects passed in ``variables`` and the values are
            NumPy Float arrays.  For constants the value is a one dimensional
            array with a single value.  For other scalar variables, the value
            will be a 1D array of values (complex values are returned as
            NumPy complex types). For vector, tensor and Coordinate variables,
            a 2D array is returned.  The first dimension is the element or
            node count and the second dimension will be 3, 9 or 3 respectively
            Note: Tensor variables will always be expanded to 9 values when
            returned. If any nodal variables are returned, an additional
            key "NODAL_IDS" will be present and will contain a NumPy array
            of integers that are the EnSight node IDs for any returned node value.
            Similarly, if any element variables are returned, "ELEMENT_IDS"
            will be present.  Note if the part does not have element or
            nodal ids then a list of [-1,-1,-1,....] will be returned.
            If the variable is a case constant, the value is returned.
            If the variable is a part constant, the value for this part
            is returned.
        
        Example:
            ::
        
                s = LocalLauncher().start()
                s.load_data(f"{s.cei_home}/ensight{s.cei_suffix}/data/guard_rail/crash.case")
                p = s.ensight.objs.core.PARTS['guardrail'][0]
                v = s.ensight.objs.core.VARIABLES[('Coordinates', 'plastic')]
                p.get_values(v, activate=1)
                # returned dictionary includes all the nodal Coordinates and plastic values
                # as well as the node IDs.  Note: the ENS_VAR 'Coordinates' is object id 1034.
                {ensight.objs.wrap_id(1034): array([[ 0.0000e+00, -8.1700e+00,  3.7600e+02],
                   [ 0.0000e+00, -4.8670e+01,  3.9850e+02],
                   [ 0.0000e+00, -8.9170e+01,  4.2100e+02],
                   ...,
                   [ 1.1335e+04, -8.1700e+00,  6.9000e+02],
                   [ 1.1430e+04, -4.8670e+01,  6.6750e+02],
                   [ 1.1430e+04, -8.1700e+00,  6.9000e+02]], dtype=float32),
                   'NODE_IDS': array([   1,    2,    3, ..., 1818, 1819, 1820]),
                   ensight.objs.wrap_id(1022): array([2.3110e-03, 1.2812e-03, 3.5511e-04, ..., 8.2598e-06, 8.2598e-06,
                   1.6520e-05], dtype=float32)}

        """
        import numpy
        arg_obj = f"{self._remote_obj()}"
        arg_list = []
        arg_list.append(variables.__repr__())
        if ids is not None:
            arg_list.append(f"ids={ids.__repr__()}")
        arg_list.append(f"use_nan={use_nan.__repr__()}")
        arg_list.append(f"activate={activate.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_values({arg_string})"
        # use dictionary completion to convert to [shape, string]
        cmd_wrap = f"{{key:[value.shape, value.dtype.str, value.tobytes()] for (key, value) in {cmd}.items()}}"
        ret_dict = self._session.cmd(cmd_wrap)
        # unwrap the dictionary
        for key, value in ret_dict.items():
            ret_dict[key] = numpy.frombuffer(value[2], dtype=value[1]).reshape(value[0])
        return ret_dict

    def removechild(self, *args, **kwargs) -> Any:
        """Remove a child from this part

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

    def addchild(self, *args, **kwargs) -> Any:
        """Add a child to this part

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
    def ENS_PLIST_KEY_SEL_0(self) -> int:
        """ENS_PLIST_KEY_SEL_0 property
        
        Tag 0
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_0)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_0.setter
    def ENS_PLIST_KEY_SEL_0(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_0, value)

    @property
    def ens_plist_key_sel_0(self) -> int:
        """ENS_PLIST_KEY_SEL_0 property
        
        Tag 0
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_0' and 'ENS_PLIST_KEY_SEL_0' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_0)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_0.setter
    def ens_plist_key_sel_0(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_0, value)

    @property
    def ENS_PLIST_KEY_SEL_1(self) -> int:
        """ENS_PLIST_KEY_SEL_1 property
        
        Tag 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_1)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_1.setter
    def ENS_PLIST_KEY_SEL_1(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_1, value)

    @property
    def ens_plist_key_sel_1(self) -> int:
        """ENS_PLIST_KEY_SEL_1 property
        
        Tag 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_1' and 'ENS_PLIST_KEY_SEL_1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_1)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_1.setter
    def ens_plist_key_sel_1(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_1, value)

    @property
    def ENS_PLIST_KEY_SEL_2(self) -> int:
        """ENS_PLIST_KEY_SEL_2 property
        
        Tag 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_2)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_2.setter
    def ENS_PLIST_KEY_SEL_2(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_2, value)

    @property
    def ens_plist_key_sel_2(self) -> int:
        """ENS_PLIST_KEY_SEL_2 property
        
        Tag 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_2' and 'ENS_PLIST_KEY_SEL_2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_2)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_2.setter
    def ens_plist_key_sel_2(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_2, value)

    @property
    def ENS_PLIST_KEY_SEL_3(self) -> int:
        """ENS_PLIST_KEY_SEL_3 property
        
        Tag 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_3)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_3.setter
    def ENS_PLIST_KEY_SEL_3(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_3, value)

    @property
    def ens_plist_key_sel_3(self) -> int:
        """ENS_PLIST_KEY_SEL_3 property
        
        Tag 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_3' and 'ENS_PLIST_KEY_SEL_3' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_3)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_3.setter
    def ens_plist_key_sel_3(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_3, value)

    @property
    def ENS_PLIST_KEY_SEL_4(self) -> int:
        """ENS_PLIST_KEY_SEL_4 property
        
        Tag 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_4)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_4.setter
    def ENS_PLIST_KEY_SEL_4(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_4, value)

    @property
    def ens_plist_key_sel_4(self) -> int:
        """ENS_PLIST_KEY_SEL_4 property
        
        Tag 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_4' and 'ENS_PLIST_KEY_SEL_4' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_4)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_4.setter
    def ens_plist_key_sel_4(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_4, value)

    @property
    def ENS_PLIST_KEY_SEL_5(self) -> int:
        """ENS_PLIST_KEY_SEL_5 property
        
        Tag 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_5)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_5.setter
    def ENS_PLIST_KEY_SEL_5(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_5, value)

    @property
    def ens_plist_key_sel_5(self) -> int:
        """ENS_PLIST_KEY_SEL_5 property
        
        Tag 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_5' and 'ENS_PLIST_KEY_SEL_5' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_5)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_5.setter
    def ens_plist_key_sel_5(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_5, value)

    @property
    def ENS_PLIST_KEY_SEL_6(self) -> int:
        """ENS_PLIST_KEY_SEL_6 property
        
        Tag 6
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_6)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_6.setter
    def ENS_PLIST_KEY_SEL_6(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_6, value)

    @property
    def ens_plist_key_sel_6(self) -> int:
        """ENS_PLIST_KEY_SEL_6 property
        
        Tag 6
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_6' and 'ENS_PLIST_KEY_SEL_6' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_6)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_6.setter
    def ens_plist_key_sel_6(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_6, value)

    @property
    def ENS_PLIST_KEY_SEL_7(self) -> int:
        """ENS_PLIST_KEY_SEL_7 property
        
        Tag 7
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_7)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_7.setter
    def ENS_PLIST_KEY_SEL_7(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_7, value)

    @property
    def ens_plist_key_sel_7(self) -> int:
        """ENS_PLIST_KEY_SEL_7 property
        
        Tag 7
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_7' and 'ENS_PLIST_KEY_SEL_7' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_7)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_7.setter
    def ens_plist_key_sel_7(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_7, value)

    @property
    def ENS_PLIST_KEY_SEL_8(self) -> int:
        """ENS_PLIST_KEY_SEL_8 property
        
        Tag 8
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_8)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_8.setter
    def ENS_PLIST_KEY_SEL_8(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_8, value)

    @property
    def ens_plist_key_sel_8(self) -> int:
        """ENS_PLIST_KEY_SEL_8 property
        
        Tag 8
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_8' and 'ENS_PLIST_KEY_SEL_8' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_8)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_8.setter
    def ens_plist_key_sel_8(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_8, value)

    @property
    def ENS_PLIST_KEY_SEL_9(self) -> int:
        """ENS_PLIST_KEY_SEL_9 property
        
        Tag 9
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_9)
        _value = cast(int, value)
        return _value

    @ENS_PLIST_KEY_SEL_9.setter
    def ENS_PLIST_KEY_SEL_9(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_9, value)

    @property
    def ens_plist_key_sel_9(self) -> int:
        """ENS_PLIST_KEY_SEL_9 property
        
        Tag 9
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ens_plist_key_sel_9' and 'ENS_PLIST_KEY_SEL_9' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_9)
        _value = cast(int, value)
        return _value

    @ens_plist_key_sel_9.setter
    def ens_plist_key_sel_9(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_PLIST_KEY_SEL_9, value)

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
    def CASENUMBER(self) -> int:
        """CASENUMBER property
        
        Case number
        
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
        
        Case number
        
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
    def PARTNUMBER(self) -> int:
        """PARTNUMBER property
        
        Id
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTNUMBER)
        _value = cast(int, value)
        return _value

    @property
    def partnumber(self) -> int:
        """PARTNUMBER property
        
        Id
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'partnumber' and 'PARTNUMBER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTNUMBER)
        _value = cast(int, value)
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
    def PARTTYPE(self) -> int:
        """PARTTYPE property
        
        Part type
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTTYPE)
        _value = cast(int, value)
        return _value

    @property
    def parttype(self) -> int:
        """PARTTYPE property
        
        Part type
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'parttype' and 'PARTTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTTYPE)
        _value = cast(int, value)
        return _value

    @property
    def PARTTYPEENUM(self) -> int:
        """PARTTYPEENUM property
        
        Type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PART_MODEL - Model
            * ensight.objs.enums.PART_CLIP_PLANE - Clip
            * ensight.objs.enums.PART_CONTOUR - Contour
            * ensight.objs.enums.PART_DISCRETE_PARTICLE - Discrete particle
            * ensight.objs.enums.PART_FRAME - Frame
            * ensight.objs.enums.PART_ISO_SURFACE - Isosurface
            * ensight.objs.enums.PART_PARTICLE_TRACE - Particle trace
            * ensight.objs.enums.PART_PROFILE - Profile
            * ensight.objs.enums.PART_VECTOR_ARROW - Vector arrow
            * ensight.objs.enums.PART_ELEVATED_SURFACE - Elevated surface
            * ensight.objs.enums.PART_DEVELOPED_SURFACE - Developed surface
            * ensight.objs.enums.PART_MODEL_EXTRACT - Extracted node/element
            * ensight.objs.enums.PART_MODEL_CUT - Clip
            * ensight.objs.enums.PART_MODEL_BOUNDARY - Boundary
            * ensight.objs.enums.PART_ISO_VOLUME - Isovolume
            * ensight.objs.enums.PART_BUILT_UP - Extracted node/element
            * ensight.objs.enums.PART_TENSOR_GLYPH - Tensor glyph
            * ensight.objs.enums.PART_FX_VORTEX_CORE - Vortex core
            * ensight.objs.enums.PART_FX_SHOCK - Shock surface
            * ensight.objs.enums.PART_FX_SEP_ATT - Sep/attach lines
            * ensight.objs.enums.PART_MATERIAL_INTERFACE - Material interface
            * ensight.objs.enums.PART_POINT - Point
            * ensight.objs.enums.PART_AXI_SYMMETRIC - Extrusion
            * ensight.objs.enums.PART_MODEL_MERGE - Merge
            * ensight.objs.enums.PART_VOF - Volume interface
            * ensight.objs.enums.PART_AUX_GEOM - Auxiliary geometry
            * ensight.objs.enums.PART_FILTER_PART - Filter part
            * ensight.objs.enums.PART_MULT - Group
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTTYPEENUM)
        _value = cast(int, value)
        return _value

    @property
    def parttypeenum(self) -> int:
        """PARTTYPEENUM property
        
        Type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PART_MODEL - Model
            * ensight.objs.enums.PART_CLIP_PLANE - Clip
            * ensight.objs.enums.PART_CONTOUR - Contour
            * ensight.objs.enums.PART_DISCRETE_PARTICLE - Discrete particle
            * ensight.objs.enums.PART_FRAME - Frame
            * ensight.objs.enums.PART_ISO_SURFACE - Isosurface
            * ensight.objs.enums.PART_PARTICLE_TRACE - Particle trace
            * ensight.objs.enums.PART_PROFILE - Profile
            * ensight.objs.enums.PART_VECTOR_ARROW - Vector arrow
            * ensight.objs.enums.PART_ELEVATED_SURFACE - Elevated surface
            * ensight.objs.enums.PART_DEVELOPED_SURFACE - Developed surface
            * ensight.objs.enums.PART_MODEL_EXTRACT - Extracted node/element
            * ensight.objs.enums.PART_MODEL_CUT - Clip
            * ensight.objs.enums.PART_MODEL_BOUNDARY - Boundary
            * ensight.objs.enums.PART_ISO_VOLUME - Isovolume
            * ensight.objs.enums.PART_BUILT_UP - Extracted node/element
            * ensight.objs.enums.PART_TENSOR_GLYPH - Tensor glyph
            * ensight.objs.enums.PART_FX_VORTEX_CORE - Vortex core
            * ensight.objs.enums.PART_FX_SHOCK - Shock surface
            * ensight.objs.enums.PART_FX_SEP_ATT - Sep/attach lines
            * ensight.objs.enums.PART_MATERIAL_INTERFACE - Material interface
            * ensight.objs.enums.PART_POINT - Point
            * ensight.objs.enums.PART_AXI_SYMMETRIC - Extrusion
            * ensight.objs.enums.PART_MODEL_MERGE - Merge
            * ensight.objs.enums.PART_VOF - Volume interface
            * ensight.objs.enums.PART_AUX_GEOM - Auxiliary geometry
            * ensight.objs.enums.PART_FILTER_PART - Filter part
            * ensight.objs.enums.PART_MULT - Group
        
        Note: both 'parttypeenum' and 'PARTTYPEENUM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTTYPEENUM)
        _value = cast(int, value)
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
    def MESHTYPE(self) -> int:
        """MESHTYPE property
        
        Mesh type
        
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
        
        Mesh type
        
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
    def SELECTED(self) -> int:
        """SELECTED property
        
        Selected
        
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
        
        Selected
        
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
    def LPARTPARENT(self) -> ensobjlist:
        """LPARTPARENT property
        
        lpart parent
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LPARTPARENT)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def lpartparent(self) -> ensobjlist:
        """LPARTPARENT property
        
        lpart parent
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'lpartparent' and 'LPARTPARENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LPARTPARENT)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def SOURCES(self) -> ensobjlist:
        """SOURCES property
        
        source parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SOURCES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def sources(self) -> ensobjlist:
        """SOURCES property
        
        source parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'sources' and 'SOURCES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SOURCES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def ISGROUP(self) -> int:
        """ISGROUP property
        
        Part is a group
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ISGROUP)
        _value = cast(int, value)
        return _value

    @property
    def isgroup(self) -> int:
        """ISGROUP property
        
        Part is a group
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'isgroup' and 'ISGROUP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ISGROUP)
        _value = cast(int, value)
        return _value

    @property
    def HAS0DELEMENTS(self) -> int:
        """HAS0DELEMENTS property
        
        Part has point elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS0DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def has0delements(self) -> int:
        """HAS0DELEMENTS property
        
        Part has point elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'has0delements' and 'HAS0DELEMENTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS0DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def HAS1DELEMENTS(self) -> int:
        """HAS1DELEMENTS property
        
        Part has line elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS1DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def has1delements(self) -> int:
        """HAS1DELEMENTS property
        
        Part has line elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'has1delements' and 'HAS1DELEMENTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS1DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def HAS2DELEMENTS(self) -> int:
        """HAS2DELEMENTS property
        
        Part has surface elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS2DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def has2delements(self) -> int:
        """HAS2DELEMENTS property
        
        Part has surface elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'has2delements' and 'HAS2DELEMENTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS2DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def HAS3DELEMENTS(self) -> int:
        """HAS3DELEMENTS property
        
        Part has volumetric elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS3DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def has3delements(self) -> int:
        """HAS3DELEMENTS property
        
        Part has volumetric elements
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'has3delements' and 'HAS3DELEMENTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HAS3DELEMENTS)
        _value = cast(int, value)
        return _value

    @property
    def VOLUMERENDERINGTYPE(self) -> int:
        """VOLUMERENDERINGTYPE property
        
        Volume rendering type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VOLREND_UNSTRUCTURED - Unstructured
            * ensight.objs.enums.VOLREND_STRUCTURED - Structured
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUMERENDERINGTYPE)
        _value = cast(int, value)
        return _value

    @property
    def volumerenderingtype(self) -> int:
        """VOLUMERENDERINGTYPE property
        
        Volume rendering type
        
        Supported operations:
            getattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VOLREND_UNSTRUCTURED - Unstructured
            * ensight.objs.enums.VOLREND_STRUCTURED - Structured
        
        Note: both 'volumerenderingtype' and 'VOLUMERENDERINGTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUMERENDERINGTYPE)
        _value = cast(int, value)
        return _value

    @property
    def MATERIALDESCRIPTION(self) -> str:
        """MATERIALDESCRIPTION property
        
        material description
        
        Supported operations:
            getattr
        Datatype:
            String, 2048 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MATERIALDESCRIPTION)
        _value = cast(str, value)
        return _value

    @property
    def materialdescription(self) -> str:
        """MATERIALDESCRIPTION property
        
        material description
        
        Supported operations:
            getattr
        Datatype:
            String, 2048 characters maximum
        
        Note: both 'materialdescription' and 'MATERIALDESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MATERIALDESCRIPTION)
        _value = cast(str, value)
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
    def ACTIVE(self) -> int:
        """ACTIVE property
        
        Update with time change
        
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
        
        Update with time change
        
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
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        Description
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
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
            String, 1024 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @description.setter
    def description(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DESCRIPTION, value)

    @property
    def VISIBLE(self) -> int:
        """VISIBLE property
        
        Show
        
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
        
        Show
        
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
    def VIEWPORTVIS(self) -> int:
        """VIEWPORTVIS property
        
        Per viewport
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums (bitfield):
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
        
        Per viewport
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums (bitfield):
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
    def COLORBYPALETTE(self) -> List[Tuple['ENS_VAR', int]]:
        """COLORBYPALETTE property
        
        Color by
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR + component, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORBYPALETTE)
        _value = cast(List[Tuple['ENS_VAR', int]], value)
        return _value

    @COLORBYPALETTE.setter
    def COLORBYPALETTE(self, value: List[Tuple['ENS_VAR', int]]) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORBYPALETTE, value)

    @property
    def colorbypalette(self) -> List[Tuple['ENS_VAR', int]]:
        """COLORBYPALETTE property
        
        Color by
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR + component, 2 element array
        
        Note: both 'colorbypalette' and 'COLORBYPALETTE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORBYPALETTE)
        _value = cast(List[Tuple['ENS_VAR', int]], value)
        return _value

    @colorbypalette.setter
    def colorbypalette(self, value: List[Tuple['ENS_VAR', int]]) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORBYPALETTE, value)

    @property
    def ALPHABYPALETTE(self) -> List[Tuple['ENS_VAR', int]]:
        """ALPHABYPALETTE property
        
        Variable for alpha palette
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR + component, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ALPHABYPALETTE)
        _value = cast(List[Tuple['ENS_VAR', int]], value)
        return _value

    @ALPHABYPALETTE.setter
    def ALPHABYPALETTE(self, value: List[Tuple['ENS_VAR', int]]) -> None:
        self.setattr(self._session.ensight.objs.enums.ALPHABYPALETTE, value)

    @property
    def alphabypalette(self) -> List[Tuple['ENS_VAR', int]]:
        """ALPHABYPALETTE property
        
        Variable for alpha palette
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR + component, 2 element array
        
        Note: both 'alphabypalette' and 'ALPHABYPALETTE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ALPHABYPALETTE)
        _value = cast(List[Tuple['ENS_VAR', int]], value)
        return _value

    @alphabypalette.setter
    def alphabypalette(self, value: List[Tuple['ENS_VAR', int]]) -> None:
        self.setattr(self._session.ensight.objs.enums.ALPHABYPALETTE, value)

    @property
    def SHADING(self) -> int:
        """SHADING property
        
        Shading type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.SHAD_FLAT - flat
            * ensight.objs.enums.SHAD_GOURAUD - gouraud
            * ensight.objs.enums.SHAD_SMOOTH - smooth
            * ensight.objs.enums.SHAD_SMOOTH_REFINED - smooth_high_quality
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHADING)
        _value = cast(int, value)
        return _value

    @SHADING.setter
    def SHADING(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHADING, value)

    @property
    def shading(self) -> int:
        """SHADING property
        
        Shading type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.SHAD_FLAT - flat
            * ensight.objs.enums.SHAD_GOURAUD - gouraud
            * ensight.objs.enums.SHAD_SMOOTH - smooth
            * ensight.objs.enums.SHAD_SMOOTH_REFINED - smooth_high_quality
        
        Note: both 'shading' and 'SHADING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHADING)
        _value = cast(int, value)
        return _value

    @shading.setter
    def shading(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHADING, value)

    @property
    def HIDDENLINE(self) -> int:
        """HIDDENLINE property
        
        Hidden line
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE)
        _value = cast(int, value)
        return _value

    @HIDDENLINE.setter
    def HIDDENLINE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE, value)

    @property
    def hiddenline(self) -> int:
        """HIDDENLINE property
        
        Hidden line
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'hiddenline' and 'HIDDENLINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE)
        _value = cast(int, value)
        return _value

    @hiddenline.setter
    def hiddenline(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE, value)

    @property
    def VARIABLE(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE property
        
        Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
            * Python None is not allowed
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @VARIABLE.setter
    def VARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE, value)

    @property
    def variable(self) -> ensobjlist['ENS_VAR']:
        """VARIABLE property
        
        Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
            * Python None is not allowed
        
        Note: both 'variable' and 'VARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @variable.setter
    def variable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VARIABLE, value)

    @property
    def LINEWIDTH(self) -> int:
        """LINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 20]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(int, value)
        return _value

    @LINEWIDTH.setter
    def LINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def linewidth(self) -> int:
        """LINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 20]
        
        Note: both 'linewidth' and 'LINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(int, value)
        return _value

    @linewidth.setter
    def linewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def CLIP(self) -> int:
        """CLIP property
        
        Auxiliary clipping
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIP)
        _value = cast(int, value)
        return _value

    @CLIP.setter
    def CLIP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIP, value)

    @property
    def clip(self) -> int:
        """CLIP property
        
        Auxiliary clipping
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'clip' and 'CLIP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIP)
        _value = cast(int, value)
        return _value

    @clip.setter
    def clip(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIP, value)

    @property
    def COLORBYRGB(self) -> List[float]:
        """COLORBYRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORBYRGB)
        _value = cast(List[float], value)
        return _value

    @COLORBYRGB.setter
    def COLORBYRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORBYRGB, value)

    @property
    def colorbyrgb(self) -> List[float]:
        """COLORBYRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'colorbyrgb' and 'COLORBYRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORBYRGB)
        _value = cast(List[float], value)
        return _value

    @colorbyrgb.setter
    def colorbyrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORBYRGB, value)

    @property
    def MATERIALBASETYPE(self) -> int:
        """MATERIALBASETYPE property
        
        Material base type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MATTE_MATERIAL - Matte
            * ensight.objs.enums.GLASS_MATERIAL - Glass
            * ensight.objs.enums.METAL_MATERIAL - Metal
            * ensight.objs.enums.METALLICPAINT_MATERIAL - MetalicPaint
            * ensight.objs.enums.MIRROR_MATERIAL - Mirror
            * ensight.objs.enums.PLASTIC_MATERIAL - Plastic
            * ensight.objs.enums.SHINYMETAL_MATERIAL - ShinyMetal
            * ensight.objs.enums.SUBSTRATE_MATERIAL - Substrate
            * ensight.objs.enums.TRANSLUCENT_MATERIAL - Translucent
            * ensight.objs.enums.UBER_MATERIAL - MultiType
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MATERIALBASETYPE)
        _value = cast(int, value)
        return _value

    @MATERIALBASETYPE.setter
    def MATERIALBASETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MATERIALBASETYPE, value)

    @property
    def materialbasetype(self) -> int:
        """MATERIALBASETYPE property
        
        Material base type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MATTE_MATERIAL - Matte
            * ensight.objs.enums.GLASS_MATERIAL - Glass
            * ensight.objs.enums.METAL_MATERIAL - Metal
            * ensight.objs.enums.METALLICPAINT_MATERIAL - MetalicPaint
            * ensight.objs.enums.MIRROR_MATERIAL - Mirror
            * ensight.objs.enums.PLASTIC_MATERIAL - Plastic
            * ensight.objs.enums.SHINYMETAL_MATERIAL - ShinyMetal
            * ensight.objs.enums.SUBSTRATE_MATERIAL - Substrate
            * ensight.objs.enums.TRANSLUCENT_MATERIAL - Translucent
            * ensight.objs.enums.UBER_MATERIAL - MultiType
        
        Note: both 'materialbasetype' and 'MATERIALBASETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MATERIALBASETYPE)
        _value = cast(int, value)
        return _value

    @materialbasetype.setter
    def materialbasetype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MATERIALBASETYPE, value)

    @property
    def ALPHABY(self) -> int:
        """ALPHABY property
        
        Alpha by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_ALPHA_NONE - constant
            * ensight.objs.enums.PALETTE_ALPHA_BY_COLOR_PALETTE - color_palette
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ALPHABY)
        _value = cast(int, value)
        return _value

    @ALPHABY.setter
    def ALPHABY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ALPHABY, value)

    @property
    def alphaby(self) -> int:
        """ALPHABY property
        
        Alpha by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PALETTE_ALPHA_NONE - constant
            * ensight.objs.enums.PALETTE_ALPHA_BY_COLOR_PALETTE - color_palette
        
        Note: both 'alphaby' and 'ALPHABY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ALPHABY)
        _value = cast(int, value)
        return _value

    @alphaby.setter
    def alphaby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ALPHABY, value)

    @property
    def OPAQUENESS(self) -> float:
        """OPAQUENESS property
        
        Opacity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OPAQUENESS)
        _value = cast(float, value)
        return _value

    @OPAQUENESS.setter
    def OPAQUENESS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OPAQUENESS, value)

    @property
    def opaqueness(self) -> float:
        """OPAQUENESS property
        
        Opacity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'opaqueness' and 'OPAQUENESS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OPAQUENESS)
        _value = cast(float, value)
        return _value

    @opaqueness.setter
    def opaqueness(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.OPAQUENESS, value)

    @property
    def FILLPATTERN(self) -> int:
        """FILLPATTERN property
        
        Fill pattern
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FILLPATTERN)
        _value = cast(int, value)
        return _value

    @FILLPATTERN.setter
    def FILLPATTERN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FILLPATTERN, value)

    @property
    def fillpattern(self) -> int:
        """FILLPATTERN property
        
        Fill pattern
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 4]
        
        Note: both 'fillpattern' and 'FILLPATTERN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FILLPATTERN)
        _value = cast(int, value)
        return _value

    @fillpattern.setter
    def fillpattern(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FILLPATTERN, value)

    @property
    def LIGHTAMBIENT(self) -> float:
        """LIGHTAMBIENT property
        
        Ambient
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTAMBIENT)
        _value = cast(float, value)
        return _value

    @LIGHTAMBIENT.setter
    def LIGHTAMBIENT(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTAMBIENT, value)

    @property
    def lightambient(self) -> float:
        """LIGHTAMBIENT property
        
        Ambient
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'lightambient' and 'LIGHTAMBIENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTAMBIENT)
        _value = cast(float, value)
        return _value

    @lightambient.setter
    def lightambient(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTAMBIENT, value)

    @property
    def LIGHTDIFFUSE(self) -> float:
        """LIGHTDIFFUSE property
        
        Diffuse
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTDIFFUSE)
        _value = cast(float, value)
        return _value

    @LIGHTDIFFUSE.setter
    def LIGHTDIFFUSE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTDIFFUSE, value)

    @property
    def lightdiffuse(self) -> float:
        """LIGHTDIFFUSE property
        
        Diffuse
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'lightdiffuse' and 'LIGHTDIFFUSE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTDIFFUSE)
        _value = cast(float, value)
        return _value

    @lightdiffuse.setter
    def lightdiffuse(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTDIFFUSE, value)

    @property
    def LIGHTEMISSIVE(self) -> float:
        """LIGHTEMISSIVE property
        
        Emissive
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTEMISSIVE)
        _value = cast(float, value)
        return _value

    @LIGHTEMISSIVE.setter
    def LIGHTEMISSIVE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTEMISSIVE, value)

    @property
    def lightemissive(self) -> float:
        """LIGHTEMISSIVE property
        
        Emissive
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'lightemissive' and 'LIGHTEMISSIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTEMISSIVE)
        _value = cast(float, value)
        return _value

    @lightemissive.setter
    def lightemissive(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTEMISSIVE, value)

    @property
    def LIGHTSPECULARSHINE(self) -> float:
        """LIGHTSPECULARSHINE property
        
        Specular shine
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 400.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARSHINE)
        _value = cast(float, value)
        return _value

    @LIGHTSPECULARSHINE.setter
    def LIGHTSPECULARSHINE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARSHINE, value)

    @property
    def lightspecularshine(self) -> float:
        """LIGHTSPECULARSHINE property
        
        Specular shine
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 400.0]
        
        Note: both 'lightspecularshine' and 'LIGHTSPECULARSHINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARSHINE)
        _value = cast(float, value)
        return _value

    @lightspecularshine.setter
    def lightspecularshine(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARSHINE, value)

    @property
    def LIGHTSPECULARINTENSITY(self) -> float:
        """LIGHTSPECULARINTENSITY property
        
        Specular intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARINTENSITY)
        _value = cast(float, value)
        return _value

    @LIGHTSPECULARINTENSITY.setter
    def LIGHTSPECULARINTENSITY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARINTENSITY, value)

    @property
    def lightspecularintensity(self) -> float:
        """LIGHTSPECULARINTENSITY property
        
        Specular intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'lightspecularintensity' and 'LIGHTSPECULARINTENSITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARINTENSITY)
        _value = cast(float, value)
        return _value

    @lightspecularintensity.setter
    def lightspecularintensity(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARINTENSITY, value)

    @property
    def LIGHTSPECULARREFLECTION(self) -> float:
        """LIGHTSPECULARREFLECTION property
        
        Specular reflection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARREFLECTION)
        _value = cast(float, value)
        return _value

    @LIGHTSPECULARREFLECTION.setter
    def LIGHTSPECULARREFLECTION(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARREFLECTION, value)

    @property
    def lightspecularreflection(self) -> float:
        """LIGHTSPECULARREFLECTION property
        
        Specular reflection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'lightspecularreflection' and 'LIGHTSPECULARREFLECTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARREFLECTION)
        _value = cast(float, value)
        return _value

    @lightspecularreflection.setter
    def lightspecularreflection(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARREFLECTION, value)

    @property
    def LIGHTSPECULARTINT(self) -> float:
        """LIGHTSPECULARTINT property
        
        Specular tint
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARTINT)
        _value = cast(float, value)
        return _value

    @LIGHTSPECULARTINT.setter
    def LIGHTSPECULARTINT(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARTINT, value)

    @property
    def lightspeculartint(self) -> float:
        """LIGHTSPECULARTINT property
        
        Specular tint
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'lightspeculartint' and 'LIGHTSPECULARTINT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSPECULARTINT)
        _value = cast(float, value)
        return _value

    @lightspeculartint.setter
    def lightspeculartint(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTSPECULARTINT, value)

    @property
    def LIGHTREFRACTION(self) -> float:
        """LIGHTREFRACTION property
        
        Refraction
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 3.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTREFRACTION)
        _value = cast(float, value)
        return _value

    @LIGHTREFRACTION.setter
    def LIGHTREFRACTION(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTREFRACTION, value)

    @property
    def lightrefraction(self) -> float:
        """LIGHTREFRACTION property
        
        Refraction
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 3.0]
        
        Note: both 'lightrefraction' and 'LIGHTREFRACTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTREFRACTION)
        _value = cast(float, value)
        return _value

    @lightrefraction.setter
    def lightrefraction(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHTREFRACTION, value)

    @property
    def PREDEFINEDMATERIAL(self) -> int:
        """PREDEFINEDMATERIAL property
        
        Predefined material
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PREDEFINEDMATERIAL)
        _value = cast(int, value)
        return _value

    @PREDEFINEDMATERIAL.setter
    def PREDEFINEDMATERIAL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PREDEFINEDMATERIAL, value)

    @property
    def predefinedmaterial(self) -> int:
        """PREDEFINEDMATERIAL property
        
        Predefined material
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'predefinedmaterial' and 'PREDEFINEDMATERIAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PREDEFINEDMATERIAL)
        _value = cast(int, value)
        return _value

    @predefinedmaterial.setter
    def predefinedmaterial(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PREDEFINEDMATERIAL, value)

    @property
    def RENDERINGREFLECTIONID(self) -> int:
        """RENDERINGREFLECTIONID property
        
        Material library id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RENDERINGREFLECTIONID)
        _value = cast(int, value)
        return _value

    @RENDERINGREFLECTIONID.setter
    def RENDERINGREFLECTIONID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RENDERINGREFLECTIONID, value)

    @property
    def renderingreflectionid(self) -> int:
        """RENDERINGREFLECTIONID property
        
        Material library id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'renderingreflectionid' and 'RENDERINGREFLECTIONID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RENDERINGREFLECTIONID)
        _value = cast(int, value)
        return _value

    @renderingreflectionid.setter
    def renderingreflectionid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RENDERINGREFLECTIONID, value)

    @property
    def DOUBLESIDED(self) -> int:
        """DOUBLESIDED property
        
        Double sided
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DOUBLESIDED)
        _value = cast(int, value)
        return _value

    @DOUBLESIDED.setter
    def DOUBLESIDED(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOUBLESIDED, value)

    @property
    def doublesided(self) -> int:
        """DOUBLESIDED property
        
        Double sided
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'doublesided' and 'DOUBLESIDED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DOUBLESIDED)
        _value = cast(int, value)
        return _value

    @doublesided.setter
    def doublesided(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOUBLESIDED, value)

    @property
    def REVERSENORMAL(self) -> int:
        """REVERSENORMAL property
        
        Reverse normal
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVERSENORMAL)
        _value = cast(int, value)
        return _value

    @REVERSENORMAL.setter
    def REVERSENORMAL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REVERSENORMAL, value)

    @property
    def reversenormal(self) -> int:
        """REVERSENORMAL property
        
        Reverse normal
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'reversenormal' and 'REVERSENORMAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVERSENORMAL)
        _value = cast(int, value)
        return _value

    @reversenormal.setter
    def reversenormal(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REVERSENORMAL, value)

    @property
    def TEXTUREOBJECT(self) -> int:
        """TEXTUREOBJECT property
        
        Texture
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 32]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREOBJECT)
        _value = cast(int, value)
        return _value

    @TEXTUREOBJECT.setter
    def TEXTUREOBJECT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREOBJECT, value)

    @property
    def textureobject(self) -> int:
        """TEXTUREOBJECT property
        
        Texture
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 32]
        
        Note: both 'textureobject' and 'TEXTUREOBJECT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREOBJECT)
        _value = cast(int, value)
        return _value

    @textureobject.setter
    def textureobject(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREOBJECT, value)

    @property
    def TEXTUREMODE(self) -> int:
        """TEXTUREMODE property
        
        Mode
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_MODE_REPLACE - replace
            * ensight.objs.enums.TEXTURE_MODE_DECAL - decal
            * ensight.objs.enums.TEXTURE_MODE_MODULATE - modulate
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREMODE)
        _value = cast(int, value)
        return _value

    @TEXTUREMODE.setter
    def TEXTUREMODE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREMODE, value)

    @property
    def texturemode(self) -> int:
        """TEXTUREMODE property
        
        Mode
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_MODE_REPLACE - replace
            * ensight.objs.enums.TEXTURE_MODE_DECAL - decal
            * ensight.objs.enums.TEXTURE_MODE_MODULATE - modulate
        
        Note: both 'texturemode' and 'TEXTUREMODE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREMODE)
        _value = cast(int, value)
        return _value

    @texturemode.setter
    def texturemode(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREMODE, value)

    @property
    def TEXTUREREPEATMODE(self) -> int:
        """TEXTUREREPEATMODE property
        
        Repeat type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_REPEAT_REPEAT - repeat
            * ensight.objs.enums.TEXTURE_REPEAT_CLAMPED - clamp
            * ensight.objs.enums.TEXTURE_REPEAT_CLAMPTEXTURE - clamptexture
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREREPEATMODE)
        _value = cast(int, value)
        return _value

    @TEXTUREREPEATMODE.setter
    def TEXTUREREPEATMODE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREREPEATMODE, value)

    @property
    def texturerepeatmode(self) -> int:
        """TEXTUREREPEATMODE property
        
        Repeat type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_REPEAT_REPEAT - repeat
            * ensight.objs.enums.TEXTURE_REPEAT_CLAMPED - clamp
            * ensight.objs.enums.TEXTURE_REPEAT_CLAMPTEXTURE - clamptexture
        
        Note: both 'texturerepeatmode' and 'TEXTUREREPEATMODE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREREPEATMODE)
        _value = cast(int, value)
        return _value

    @texturerepeatmode.setter
    def texturerepeatmode(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREREPEATMODE, value)

    @property
    def TEXTUREINTERPOLATION(self) -> int:
        """TEXTUREINTERPOLATION property
        
        Interpolation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_INTERPOLATE_NEAREST - nearest
            * ensight.objs.enums.TEXTURE_INTERPOLATE_LINEAR - linear
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREINTERPOLATION)
        _value = cast(int, value)
        return _value

    @TEXTUREINTERPOLATION.setter
    def TEXTUREINTERPOLATION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREINTERPOLATION, value)

    @property
    def textureinterpolation(self) -> int:
        """TEXTUREINTERPOLATION property
        
        Interpolation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_INTERPOLATE_NEAREST - nearest
            * ensight.objs.enums.TEXTURE_INTERPOLATE_LINEAR - linear
        
        Note: both 'textureinterpolation' and 'TEXTUREINTERPOLATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREINTERPOLATION)
        _value = cast(int, value)
        return _value

    @textureinterpolation.setter
    def textureinterpolation(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREINTERPOLATION, value)

    @property
    def TEXTURECOORDTYPE(self) -> int:
        """TEXTURECOORDTYPE property
        
        Compute coordinates by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_COORDS_BY_PROJECTION - projection
            * ensight.objs.enums.TEXTURE_COORDS_BY_TWOSCALARS - variables
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURECOORDTYPE)
        _value = cast(int, value)
        return _value

    @TEXTURECOORDTYPE.setter
    def TEXTURECOORDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURECOORDTYPE, value)

    @property
    def texturecoordtype(self) -> int:
        """TEXTURECOORDTYPE property
        
        Compute coordinates by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TEXTURE_COORDS_BY_PROJECTION - projection
            * ensight.objs.enums.TEXTURE_COORDS_BY_TWOSCALARS - variables
        
        Note: both 'texturecoordtype' and 'TEXTURECOORDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURECOORDTYPE)
        _value = cast(int, value)
        return _value

    @texturecoordtype.setter
    def texturecoordtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURECOORDTYPE, value)

    @property
    def TEXTUREORIGIN(self) -> List[float]:
        """TEXTUREORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREORIGIN)
        _value = cast(List[float], value)
        return _value

    @TEXTUREORIGIN.setter
    def TEXTUREORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREORIGIN, value)

    @property
    def textureorigin(self) -> List[float]:
        """TEXTUREORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'textureorigin' and 'TEXTUREORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREORIGIN)
        _value = cast(List[float], value)
        return _value

    @textureorigin.setter
    def textureorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREORIGIN, value)

    @property
    def TEXTURESVECTOR(self) -> List[float]:
        """TEXTURESVECTOR property
        
        S-Vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURESVECTOR)
        _value = cast(List[float], value)
        return _value

    @TEXTURESVECTOR.setter
    def TEXTURESVECTOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURESVECTOR, value)

    @property
    def texturesvector(self) -> List[float]:
        """TEXTURESVECTOR property
        
        S-Vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'texturesvector' and 'TEXTURESVECTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURESVECTOR)
        _value = cast(List[float], value)
        return _value

    @texturesvector.setter
    def texturesvector(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURESVECTOR, value)

    @property
    def TEXTURETVECTOR(self) -> List[float]:
        """TEXTURETVECTOR property
        
        T-Vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURETVECTOR)
        _value = cast(List[float], value)
        return _value

    @TEXTURETVECTOR.setter
    def TEXTURETVECTOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURETVECTOR, value)

    @property
    def texturetvector(self) -> List[float]:
        """TEXTURETVECTOR property
        
        T-Vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'texturetvector' and 'TEXTURETVECTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURETVECTOR)
        _value = cast(List[float], value)
        return _value

    @texturetvector.setter
    def texturetvector(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURETVECTOR, value)

    @property
    def TEXTURESVARIABLE(self) -> ensobjlist['ENS_VAR']:
        """TEXTURESVARIABLE property
        
        S-Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURESVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @TEXTURESVARIABLE.setter
    def TEXTURESVARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURESVARIABLE, value)

    @property
    def texturesvariable(self) -> ensobjlist['ENS_VAR']:
        """TEXTURESVARIABLE property
        
        S-Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
        
        Note: both 'texturesvariable' and 'TEXTURESVARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURESVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @texturesvariable.setter
    def texturesvariable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURESVARIABLE, value)

    @property
    def TEXTURETVARIABLE(self) -> ensobjlist['ENS_VAR']:
        """TEXTURETVARIABLE property
        
        T-Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURETVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @TEXTURETVARIABLE.setter
    def TEXTURETVARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURETVARIABLE, value)

    @property
    def texturetvariable(self) -> ensobjlist['ENS_VAR']:
        """TEXTURETVARIABLE property
        
        T-Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
        
        Note: both 'texturetvariable' and 'TEXTURETVARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURETVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @texturetvariable.setter
    def texturetvariable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURETVARIABLE, value)

    @property
    def TEXTUREORIGINUSE(self) -> int:
        """TEXTUREORIGINUSE property
        
        Projection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ZERO - absolute
            * ensight.objs.enums.ONE - offset_by_nodeid
            * ensight.objs.enums.SEVEN - offsetvectors_by_nodeid
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREORIGINUSE)
        _value = cast(int, value)
        return _value

    @TEXTUREORIGINUSE.setter
    def TEXTUREORIGINUSE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREORIGINUSE, value)

    @property
    def textureoriginuse(self) -> int:
        """TEXTUREORIGINUSE property
        
        Projection
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ZERO - absolute
            * ensight.objs.enums.ONE - offset_by_nodeid
            * ensight.objs.enums.SEVEN - offsetvectors_by_nodeid
        
        Note: both 'textureoriginuse' and 'TEXTUREORIGINUSE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREORIGINUSE)
        _value = cast(int, value)
        return _value

    @textureoriginuse.setter
    def textureoriginuse(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREORIGINUSE, value)

    @property
    def TEXTUREORIGINNODEID(self) -> int:
        """TEXTUREORIGINNODEID property
        
        Projection origin node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREORIGINNODEID)
        _value = cast(int, value)
        return _value

    @TEXTUREORIGINNODEID.setter
    def TEXTUREORIGINNODEID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREORIGINNODEID, value)

    @property
    def textureoriginnodeid(self) -> int:
        """TEXTUREORIGINNODEID property
        
        Projection origin node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'textureoriginnodeid' and 'TEXTUREORIGINNODEID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTUREORIGINNODEID)
        _value = cast(int, value)
        return _value

    @textureoriginnodeid.setter
    def textureoriginnodeid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTUREORIGINNODEID, value)

    @property
    def TEXTURESORIGINNODEID(self) -> int:
        """TEXTURESORIGINNODEID property
        
        Projection S-node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURESORIGINNODEID)
        _value = cast(int, value)
        return _value

    @TEXTURESORIGINNODEID.setter
    def TEXTURESORIGINNODEID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURESORIGINNODEID, value)

    @property
    def texturesoriginnodeid(self) -> int:
        """TEXTURESORIGINNODEID property
        
        Projection S-node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'texturesoriginnodeid' and 'TEXTURESORIGINNODEID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURESORIGINNODEID)
        _value = cast(int, value)
        return _value

    @texturesoriginnodeid.setter
    def texturesoriginnodeid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURESORIGINNODEID, value)

    @property
    def TEXTURETORIGINNODEID(self) -> int:
        """TEXTURETORIGINNODEID property
        
        Projection T-node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURETORIGINNODEID)
        _value = cast(int, value)
        return _value

    @TEXTURETORIGINNODEID.setter
    def TEXTURETORIGINNODEID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURETORIGINNODEID, value)

    @property
    def texturetoriginnodeid(self) -> int:
        """TEXTURETORIGINNODEID property
        
        Projection T-node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'texturetoriginnodeid' and 'TEXTURETORIGINNODEID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURETORIGINNODEID)
        _value = cast(int, value)
        return _value

    @texturetoriginnodeid.setter
    def texturetoriginnodeid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TEXTURETORIGINNODEID, value)

    @property
    def SHOWSFT(self) -> int:
        """SHOWSFT property
        
        Show surface flow texture
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWSFT)
        _value = cast(int, value)
        return _value

    @SHOWSFT.setter
    def SHOWSFT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWSFT, value)

    @property
    def showsft(self) -> int:
        """SHOWSFT property
        
        Show surface flow texture
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'showsft' and 'SHOWSFT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SHOWSFT)
        _value = cast(int, value)
        return _value

    @showsft.setter
    def showsft(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SHOWSFT, value)

    @property
    def MIRRORORIGINAL(self) -> int:
        """MIRRORORIGINAL property
        
        Show original section
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MIRRORORIGINAL)
        _value = cast(int, value)
        return _value

    @MIRRORORIGINAL.setter
    def MIRRORORIGINAL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MIRRORORIGINAL, value)

    @property
    def mirrororiginal(self) -> int:
        """MIRRORORIGINAL property
        
        Show original section
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'mirrororiginal' and 'MIRRORORIGINAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MIRRORORIGINAL)
        _value = cast(int, value)
        return _value

    @mirrororiginal.setter
    def mirrororiginal(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MIRRORORIGINAL, value)

    @property
    def SYMMETRYTYPE(self) -> int:
        """SYMMETRYTYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VISUAL_SYMM_MIRROR - mirror
            * ensight.objs.enums.VISUAL_SYMM_ROTATE - rotational
            * ensight.objs.enums.VISUAL_SYMM_TRANSLATE - translational
            * ensight.objs.enums.VISUAL_SYMM_NONE - none
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYTYPE)
        _value = cast(int, value)
        return _value

    @SYMMETRYTYPE.setter
    def SYMMETRYTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYTYPE, value)

    @property
    def symmetrytype(self) -> int:
        """SYMMETRYTYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VISUAL_SYMM_MIRROR - mirror
            * ensight.objs.enums.VISUAL_SYMM_ROTATE - rotational
            * ensight.objs.enums.VISUAL_SYMM_TRANSLATE - translational
            * ensight.objs.enums.VISUAL_SYMM_NONE - none
        
        Note: both 'symmetrytype' and 'SYMMETRYTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYTYPE)
        _value = cast(int, value)
        return _value

    @symmetrytype.setter
    def symmetrytype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYTYPE, value)

    @property
    def SYMMETRYMIRRORX(self) -> int:
        """SYMMETRYMIRRORX property
        
        Mirror X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORX)
        _value = cast(int, value)
        return _value

    @SYMMETRYMIRRORX.setter
    def SYMMETRYMIRRORX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORX, value)

    @property
    def symmetrymirrorx(self) -> int:
        """SYMMETRYMIRRORX property
        
        Mirror X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'symmetrymirrorx' and 'SYMMETRYMIRRORX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORX)
        _value = cast(int, value)
        return _value

    @symmetrymirrorx.setter
    def symmetrymirrorx(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORX, value)

    @property
    def SYMMETRYMIRRORY(self) -> int:
        """SYMMETRYMIRRORY property
        
        Mirror Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORY)
        _value = cast(int, value)
        return _value

    @SYMMETRYMIRRORY.setter
    def SYMMETRYMIRRORY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORY, value)

    @property
    def symmetrymirrory(self) -> int:
        """SYMMETRYMIRRORY property
        
        Mirror Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'symmetrymirrory' and 'SYMMETRYMIRRORY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORY)
        _value = cast(int, value)
        return _value

    @symmetrymirrory.setter
    def symmetrymirrory(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORY, value)

    @property
    def SYMMETRYMIRRORZ(self) -> int:
        """SYMMETRYMIRRORZ property
        
        Mirror Z
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORZ)
        _value = cast(int, value)
        return _value

    @SYMMETRYMIRRORZ.setter
    def SYMMETRYMIRRORZ(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORZ, value)

    @property
    def symmetrymirrorz(self) -> int:
        """SYMMETRYMIRRORZ property
        
        Mirror Z
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'symmetrymirrorz' and 'SYMMETRYMIRRORZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORZ)
        _value = cast(int, value)
        return _value

    @symmetrymirrorz.setter
    def symmetrymirrorz(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORZ, value)

    @property
    def SYMMETRYMIRRORXY(self) -> int:
        """SYMMETRYMIRRORXY property
        
        Mirror XY
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXY)
        _value = cast(int, value)
        return _value

    @SYMMETRYMIRRORXY.setter
    def SYMMETRYMIRRORXY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXY, value)

    @property
    def symmetrymirrorxy(self) -> int:
        """SYMMETRYMIRRORXY property
        
        Mirror XY
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'symmetrymirrorxy' and 'SYMMETRYMIRRORXY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXY)
        _value = cast(int, value)
        return _value

    @symmetrymirrorxy.setter
    def symmetrymirrorxy(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXY, value)

    @property
    def SYMMETRYMIRRORYZ(self) -> int:
        """SYMMETRYMIRRORYZ property
        
        Mirror YZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORYZ)
        _value = cast(int, value)
        return _value

    @SYMMETRYMIRRORYZ.setter
    def SYMMETRYMIRRORYZ(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORYZ, value)

    @property
    def symmetrymirroryz(self) -> int:
        """SYMMETRYMIRRORYZ property
        
        Mirror YZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'symmetrymirroryz' and 'SYMMETRYMIRRORYZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORYZ)
        _value = cast(int, value)
        return _value

    @symmetrymirroryz.setter
    def symmetrymirroryz(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORYZ, value)

    @property
    def SYMMETRYMIRRORXZ(self) -> int:
        """SYMMETRYMIRRORXZ property
        
        Mirror XZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXZ)
        _value = cast(int, value)
        return _value

    @SYMMETRYMIRRORXZ.setter
    def SYMMETRYMIRRORXZ(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXZ, value)

    @property
    def symmetrymirrorxz(self) -> int:
        """SYMMETRYMIRRORXZ property
        
        Mirror XZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'symmetrymirrorxz' and 'SYMMETRYMIRRORXZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXZ)
        _value = cast(int, value)
        return _value

    @symmetrymirrorxz.setter
    def symmetrymirrorxz(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXZ, value)

    @property
    def SYMMETRYMIRRORXYZ(self) -> int:
        """SYMMETRYMIRRORXYZ property
        
        Mirror XYZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXYZ)
        _value = cast(int, value)
        return _value

    @SYMMETRYMIRRORXYZ.setter
    def SYMMETRYMIRRORXYZ(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXYZ, value)

    @property
    def symmetrymirrorxyz(self) -> int:
        """SYMMETRYMIRRORXYZ property
        
        Mirror XYZ
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'symmetrymirrorxyz' and 'SYMMETRYMIRRORXYZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXYZ)
        _value = cast(int, value)
        return _value

    @symmetrymirrorxyz.setter
    def symmetrymirrorxyz(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYMIRRORXYZ, value)

    @property
    def SYMMETRYRINSTANCES(self) -> int:
        """SYMMETRYRINSTANCES property
        
        Instances
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 360]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYRINSTANCES)
        _value = cast(int, value)
        return _value

    @SYMMETRYRINSTANCES.setter
    def SYMMETRYRINSTANCES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYRINSTANCES, value)

    @property
    def symmetryrinstances(self) -> int:
        """SYMMETRYRINSTANCES property
        
        Instances
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 360]
        
        Note: both 'symmetryrinstances' and 'SYMMETRYRINSTANCES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYRINSTANCES)
        _value = cast(int, value)
        return _value

    @symmetryrinstances.setter
    def symmetryrinstances(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYRINSTANCES, value)

    @property
    def SYMMETRYAXIS(self) -> int:
        """SYMMETRYAXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ROT_SYMM_X_AXIS - x
            * ensight.objs.enums.ROT_SYMM_Y_AXIS - y
            * ensight.objs.enums.ROT_SYMM_Z_AXIS - z
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYAXIS)
        _value = cast(int, value)
        return _value

    @SYMMETRYAXIS.setter
    def SYMMETRYAXIS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYAXIS, value)

    @property
    def symmetryaxis(self) -> int:
        """SYMMETRYAXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ROT_SYMM_X_AXIS - x
            * ensight.objs.enums.ROT_SYMM_Y_AXIS - y
            * ensight.objs.enums.ROT_SYMM_Z_AXIS - z
        
        Note: both 'symmetryaxis' and 'SYMMETRYAXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYAXIS)
        _value = cast(int, value)
        return _value

    @symmetryaxis.setter
    def symmetryaxis(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYAXIS, value)

    @property
    def SPECIFYSYMMETRYORIGIN(self) -> int:
        """SPECIFYSYMMETRYORIGIN property
        
        Specify origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPECIFYSYMMETRYORIGIN)
        _value = cast(int, value)
        return _value

    @SPECIFYSYMMETRYORIGIN.setter
    def SPECIFYSYMMETRYORIGIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPECIFYSYMMETRYORIGIN, value)

    @property
    def specifysymmetryorigin(self) -> int:
        """SPECIFYSYMMETRYORIGIN property
        
        Specify origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'specifysymmetryorigin' and 'SPECIFYSYMMETRYORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPECIFYSYMMETRYORIGIN)
        _value = cast(int, value)
        return _value

    @specifysymmetryorigin.setter
    def specifysymmetryorigin(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPECIFYSYMMETRYORIGIN, value)

    @property
    def SYMMETRYORIGIN(self) -> List[float]:
        """SYMMETRYORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYORIGIN)
        _value = cast(List[float], value)
        return _value

    @SYMMETRYORIGIN.setter
    def SYMMETRYORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYORIGIN, value)

    @property
    def symmetryorigin(self) -> List[float]:
        """SYMMETRYORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'symmetryorigin' and 'SYMMETRYORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYORIGIN)
        _value = cast(List[float], value)
        return _value

    @symmetryorigin.setter
    def symmetryorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYORIGIN, value)

    @property
    def PERIODICSECTIONS(self) -> int:
        """PERIODICSECTIONS property
        
        Periodic sections
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PERIODICSECTIONS)
        _value = cast(int, value)
        return _value

    @PERIODICSECTIONS.setter
    def PERIODICSECTIONS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PERIODICSECTIONS, value)

    @property
    def periodicsections(self) -> int:
        """PERIODICSECTIONS property
        
        Periodic sections
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'periodicsections' and 'PERIODICSECTIONS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PERIODICSECTIONS)
        _value = cast(int, value)
        return _value

    @periodicsections.setter
    def periodicsections(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PERIODICSECTIONS, value)

    @property
    def SYMMETRYDELTA(self) -> List[float]:
        """SYMMETRYDELTA property
        
        Delta
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYDELTA)
        _value = cast(List[float], value)
        return _value

    @SYMMETRYDELTA.setter
    def SYMMETRYDELTA(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYDELTA, value)

    @property
    def symmetrydelta(self) -> List[float]:
        """SYMMETRYDELTA property
        
        Delta
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'symmetrydelta' and 'SYMMETRYDELTA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYDELTA)
        _value = cast(List[float], value)
        return _value

    @symmetrydelta.setter
    def symmetrydelta(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYDELTA, value)

    @property
    def DISPLACEBY(self) -> ensobjlist['ENS_VAR']:
        """DISPLACEBY property
        
        Displace by
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLACEBY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @DISPLACEBY.setter
    def DISPLACEBY(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLACEBY, value)

    @property
    def displaceby(self) -> ensobjlist['ENS_VAR']:
        """DISPLACEBY property
        
        Displace by
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
        
        Note: both 'displaceby' and 'DISPLACEBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLACEBY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @displaceby.setter
    def displaceby(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLACEBY, value)

    @property
    def DISPLACEFACTOR(self) -> float:
        """DISPLACEFACTOR property
        
        Factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLACEFACTOR)
        _value = cast(float, value)
        return _value

    @DISPLACEFACTOR.setter
    def DISPLACEFACTOR(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLACEFACTOR, value)

    @property
    def displacefactor(self) -> float:
        """DISPLACEFACTOR property
        
        Factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'displacefactor' and 'DISPLACEFACTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLACEFACTOR)
        _value = cast(float, value)
        return _value

    @displacefactor.setter
    def displacefactor(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLACEFACTOR, value)

    @property
    def VISIBILITYNODE(self) -> int:
        """VISIBILITYNODE property
        
        Nodes visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBILITYNODE)
        _value = cast(int, value)
        return _value

    @VISIBILITYNODE.setter
    def VISIBILITYNODE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBILITYNODE, value)

    @property
    def visibilitynode(self) -> int:
        """VISIBILITYNODE property
        
        Nodes visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'visibilitynode' and 'VISIBILITYNODE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBILITYNODE)
        _value = cast(int, value)
        return _value

    @visibilitynode.setter
    def visibilitynode(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBILITYNODE, value)

    @property
    def ENTITYLABELNODE(self) -> int:
        """ENTITYLABELNODE property
        
        Node labels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENTITYLABELNODE)
        _value = cast(int, value)
        return _value

    @ENTITYLABELNODE.setter
    def ENTITYLABELNODE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENTITYLABELNODE, value)

    @property
    def entitylabelnode(self) -> int:
        """ENTITYLABELNODE property
        
        Node labels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'entitylabelnode' and 'ENTITYLABELNODE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENTITYLABELNODE)
        _value = cast(int, value)
        return _value

    @entitylabelnode.setter
    def entitylabelnode(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENTITYLABELNODE, value)

    @property
    def NODETYPE(self) -> int:
        """NODETYPE property
        
        Node type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MARKER_DOT - dot
            * ensight.objs.enums.MARKER_CROSS - cross
            * ensight.objs.enums.MARKER_SPHER - sphere
            * ensight.objs.enums.MARKER_SCREENSPACE_SURFACE - sph_screensurface
            * ensight.objs.enums.MARKER_USER_DEFINED - user_defined
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODETYPE)
        _value = cast(int, value)
        return _value

    @NODETYPE.setter
    def NODETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODETYPE, value)

    @property
    def nodetype(self) -> int:
        """NODETYPE property
        
        Node type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MARKER_DOT - dot
            * ensight.objs.enums.MARKER_CROSS - cross
            * ensight.objs.enums.MARKER_SPHER - sphere
            * ensight.objs.enums.MARKER_SCREENSPACE_SURFACE - sph_screensurface
            * ensight.objs.enums.MARKER_USER_DEFINED - user_defined
        
        Note: both 'nodetype' and 'NODETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODETYPE)
        _value = cast(int, value)
        return _value

    @nodetype.setter
    def nodetype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODETYPE, value)

    @property
    def NODESIZEBY(self) -> int:
        """NODESIZEBY property
        
        Nodes sized by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MARKER_SIZE_CONSTANT - constant
            * ensight.objs.enums.MARKER_SIZE_SCALAR - scalar
            * ensight.objs.enums.MARKER_SIZE_VECMAG - vector_mag
            * ensight.objs.enums.MARKER_SIZE_VECXCOMP - vector_xcomp
            * ensight.objs.enums.MARKER_SIZE_VECYCOMP - vector_ycomp
            * ensight.objs.enums.MARKER_SIZE_VECZCOMP - vector_zcomp
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODESIZEBY)
        _value = cast(int, value)
        return _value

    @NODESIZEBY.setter
    def NODESIZEBY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODESIZEBY, value)

    @property
    def nodesizeby(self) -> int:
        """NODESIZEBY property
        
        Nodes sized by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MARKER_SIZE_CONSTANT - constant
            * ensight.objs.enums.MARKER_SIZE_SCALAR - scalar
            * ensight.objs.enums.MARKER_SIZE_VECMAG - vector_mag
            * ensight.objs.enums.MARKER_SIZE_VECXCOMP - vector_xcomp
            * ensight.objs.enums.MARKER_SIZE_VECYCOMP - vector_ycomp
            * ensight.objs.enums.MARKER_SIZE_VECZCOMP - vector_zcomp
        
        Note: both 'nodesizeby' and 'NODESIZEBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODESIZEBY)
        _value = cast(int, value)
        return _value

    @nodesizeby.setter
    def nodesizeby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODESIZEBY, value)

    @property
    def NODEVARIABLE(self) -> ensobjlist['ENS_VAR']:
        """NODEVARIABLE property
        
        Node variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Nodal
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @NODEVARIABLE.setter
    def NODEVARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEVARIABLE, value)

    @property
    def nodevariable(self) -> ensobjlist['ENS_VAR']:
        """NODEVARIABLE property
        
        Node variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Nodal
        
        Note: both 'nodevariable' and 'NODEVARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @nodevariable.setter
    def nodevariable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEVARIABLE, value)

    @property
    def NODESCALE(self) -> float:
        """NODESCALE property
        
        Node scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODESCALE)
        _value = cast(float, value)
        return _value

    @NODESCALE.setter
    def NODESCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.NODESCALE, value)

    @property
    def nodescale(self) -> float:
        """NODESCALE property
        
        Node scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'nodescale' and 'NODESCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODESCALE)
        _value = cast(float, value)
        return _value

    @nodescale.setter
    def nodescale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.NODESCALE, value)

    @property
    def NODEDETAIL(self) -> int:
        """NODEDETAIL property
        
        Type detail
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, 10]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEDETAIL)
        _value = cast(int, value)
        return _value

    @NODEDETAIL.setter
    def NODEDETAIL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEDETAIL, value)

    @property
    def nodedetail(self) -> int:
        """NODEDETAIL property
        
        Type detail
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, 10]
        
        Note: both 'nodedetail' and 'NODEDETAIL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEDETAIL)
        _value = cast(int, value)
        return _value

    @nodedetail.setter
    def nodedetail(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEDETAIL, value)

    @property
    def NODEORIENTATIONAXIS(self) -> ensobjlist['ENS_VAR']:
        """NODEORIENTATIONAXIS property
        
        Node axis variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEORIENTATIONAXIS)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @NODEORIENTATIONAXIS.setter
    def NODEORIENTATIONAXIS(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEORIENTATIONAXIS, value)

    @property
    def nodeorientationaxis(self) -> ensobjlist['ENS_VAR']:
        """NODEORIENTATIONAXIS property
        
        Node axis variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
        
        Note: both 'nodeorientationaxis' and 'NODEORIENTATIONAXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEORIENTATIONAXIS)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @nodeorientationaxis.setter
    def nodeorientationaxis(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEORIENTATIONAXIS, value)

    @property
    def NODEORIENTATIONANGLE(self) -> ensobjlist['ENS_VAR']:
        """NODEORIENTATIONANGLE property
        
        Node angle variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
        
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEORIENTATIONANGLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @NODEORIENTATIONANGLE.setter
    def NODEORIENTATIONANGLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEORIENTATIONANGLE, value)

    @property
    def nodeorientationangle(self) -> ensobjlist['ENS_VAR']:
        """NODEORIENTATIONANGLE property
        
        Node angle variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
        
        Note: both 'nodeorientationangle' and 'NODEORIENTATIONANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.NODEORIENTATIONANGLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @nodeorientationangle.setter
    def nodeorientationangle(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.NODEORIENTATIONANGLE, value)

    @property
    def VISIBILITYLINE(self) -> int:
        """VISIBILITYLINE property
        
        Lines visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBILITYLINE)
        _value = cast(int, value)
        return _value

    @VISIBILITYLINE.setter
    def VISIBILITYLINE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBILITYLINE, value)

    @property
    def visibilityline(self) -> int:
        """VISIBILITYLINE property
        
        Lines visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'visibilityline' and 'VISIBILITYLINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBILITYLINE)
        _value = cast(int, value)
        return _value

    @visibilityline.setter
    def visibilityline(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBILITYLINE, value)

    @property
    def LINESTYLE(self) -> int:
        """LINESTYLE property
        
        Line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dot_dash
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINESTYLE)
        _value = cast(int, value)
        return _value

    @LINESTYLE.setter
    def LINESTYLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINESTYLE, value)

    @property
    def linestyle(self) -> int:
        """LINESTYLE property
        
        Line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dot_dash
        
        Note: both 'linestyle' and 'LINESTYLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINESTYLE)
        _value = cast(int, value)
        return _value

    @linestyle.setter
    def linestyle(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINESTYLE, value)

    @property
    def VISIBILITYELT(self) -> int:
        """VISIBILITYELT property
        
        Elements visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBILITYELT)
        _value = cast(int, value)
        return _value

    @VISIBILITYELT.setter
    def VISIBILITYELT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBILITYELT, value)

    @property
    def visibilityelt(self) -> int:
        """VISIBILITYELT property
        
        Elements visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'visibilityelt' and 'VISIBILITYELT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VISIBILITYELT)
        _value = cast(int, value)
        return _value

    @visibilityelt.setter
    def visibilityelt(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VISIBILITYELT, value)

    @property
    def ENTITYLABELELT(self) -> int:
        """ENTITYLABELELT property
        
        Element labels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENTITYLABELELT)
        _value = cast(int, value)
        return _value

    @ENTITYLABELELT.setter
    def ENTITYLABELELT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENTITYLABELELT, value)

    @property
    def entitylabelelt(self) -> int:
        """ENTITYLABELELT property
        
        Element labels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'entitylabelelt' and 'ENTITYLABELELT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENTITYLABELELT)
        _value = cast(int, value)
        return _value

    @entitylabelelt.setter
    def entitylabelelt(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ENTITYLABELELT, value)

    @property
    def ELTREPRESENTATION(self) -> int:
        """ELTREPRESENTATION property
        
        Representation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.BORD_FULL - 3D_border_2D_full
            * ensight.objs.enums.BORDERREP - border
            * ensight.objs.enums.FEATURE_ANGLE - feature_angle
            * ensight.objs.enums.FULL - full
            * ensight.objs.enums.NOT_LOADED - not_loaded
            * ensight.objs.enums.BOUNDING_BOX - bounding_box
            * ensight.objs.enums.FEATURE_FULL - 3D_feature_2D_full
            * ensight.objs.enums.NOTLOAD_FULL - 3D_notloaded_2D_full
            * ensight.objs.enums.VOLUME - volume
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTREPRESENTATION)
        _value = cast(int, value)
        return _value

    @ELTREPRESENTATION.setter
    def ELTREPRESENTATION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTREPRESENTATION, value)

    @property
    def eltrepresentation(self) -> int:
        """ELTREPRESENTATION property
        
        Representation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.BORD_FULL - 3D_border_2D_full
            * ensight.objs.enums.BORDERREP - border
            * ensight.objs.enums.FEATURE_ANGLE - feature_angle
            * ensight.objs.enums.FULL - full
            * ensight.objs.enums.NOT_LOADED - not_loaded
            * ensight.objs.enums.BOUNDING_BOX - bounding_box
            * ensight.objs.enums.FEATURE_FULL - 3D_feature_2D_full
            * ensight.objs.enums.NOTLOAD_FULL - 3D_notloaded_2D_full
            * ensight.objs.enums.VOLUME - volume
        
        Note: both 'eltrepresentation' and 'ELTREPRESENTATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTREPRESENTATION)
        _value = cast(int, value)
        return _value

    @eltrepresentation.setter
    def eltrepresentation(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTREPRESENTATION, value)

    @property
    def ELTFEATUREANGLE(self) -> float:
        """ELTFEATUREANGLE property
        
        Feature angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 180.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTFEATUREANGLE)
        _value = cast(float, value)
        return _value

    @ELTFEATUREANGLE.setter
    def ELTFEATUREANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTFEATUREANGLE, value)

    @property
    def eltfeatureangle(self) -> float:
        """ELTFEATUREANGLE property
        
        Feature angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 180.0]
        
        Note: both 'eltfeatureangle' and 'ELTFEATUREANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTFEATUREANGLE)
        _value = cast(float, value)
        return _value

    @eltfeatureangle.setter
    def eltfeatureangle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTFEATUREANGLE, value)

    @property
    def ELTREPPOINTSNORMALS(self) -> int:
        """ELTREPPOINTSNORMALS property
        
        Load only points/normals
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTREPPOINTSNORMALS)
        _value = cast(int, value)
        return _value

    @ELTREPPOINTSNORMALS.setter
    def ELTREPPOINTSNORMALS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTREPPOINTSNORMALS, value)

    @property
    def eltreppointsnormals(self) -> int:
        """ELTREPPOINTSNORMALS property
        
        Load only points/normals
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'eltreppointsnormals' and 'ELTREPPOINTSNORMALS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTREPPOINTSNORMALS)
        _value = cast(int, value)
        return _value

    @eltreppointsnormals.setter
    def eltreppointsnormals(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTREPPOINTSNORMALS, value)

    @property
    def REDUCEPOLYGONS(self) -> int:
        """REDUCEPOLYGONS property
        
        Reduce polygons
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REDUCEPOLYGONS)
        _value = cast(int, value)
        return _value

    @REDUCEPOLYGONS.setter
    def REDUCEPOLYGONS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REDUCEPOLYGONS, value)

    @property
    def reducepolygons(self) -> int:
        """REDUCEPOLYGONS property
        
        Reduce polygons
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'reducepolygons' and 'REDUCEPOLYGONS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REDUCEPOLYGONS)
        _value = cast(int, value)
        return _value

    @reducepolygons.setter
    def reducepolygons(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REDUCEPOLYGONS, value)

    @property
    def REDUCEPOLYGONSFACTOR(self) -> int:
        """REDUCEPOLYGONSFACTOR property
        
        Reduction factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 10]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REDUCEPOLYGONSFACTOR)
        _value = cast(int, value)
        return _value

    @REDUCEPOLYGONSFACTOR.setter
    def REDUCEPOLYGONSFACTOR(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REDUCEPOLYGONSFACTOR, value)

    @property
    def reducepolygonsfactor(self) -> int:
        """REDUCEPOLYGONSFACTOR property
        
        Reduction factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, 10]
        
        Note: both 'reducepolygonsfactor' and 'REDUCEPOLYGONSFACTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REDUCEPOLYGONSFACTOR)
        _value = cast(int, value)
        return _value

    @reducepolygonsfactor.setter
    def reducepolygonsfactor(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REDUCEPOLYGONSFACTOR, value)

    @property
    def ELTSHRINKFACTOR(self) -> float:
        """ELTSHRINKFACTOR property
        
        Shrink factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTSHRINKFACTOR)
        _value = cast(float, value)
        return _value

    @ELTSHRINKFACTOR.setter
    def ELTSHRINKFACTOR(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTSHRINKFACTOR, value)

    @property
    def eltshrinkfactor(self) -> float:
        """ELTSHRINKFACTOR property
        
        Shrink factor
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'eltshrinkfactor' and 'ELTSHRINKFACTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTSHRINKFACTOR)
        _value = cast(float, value)
        return _value

    @eltshrinkfactor.setter
    def eltshrinkfactor(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTSHRINKFACTOR, value)

    @property
    def ELTBLANKING(self) -> int:
        """ELTBLANKING property
        
        Do not show elements
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTBLANKING)
        _value = cast(int, value)
        return _value

    @ELTBLANKING.setter
    def ELTBLANKING(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTBLANKING, value)

    @property
    def eltblanking(self) -> int:
        """ELTBLANKING property
        
        Do not show elements
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'eltblanking' and 'ELTBLANKING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ELTBLANKING)
        _value = cast(int, value)
        return _value

    @eltblanking.setter
    def eltblanking(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ELTBLANKING, value)

    @property
    def CULLELEMENTS(self) -> int:
        """CULLELEMENTS property
        
        Do not show elements
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CULL_BACK_FACE - facing_back
            * ensight.objs.enums.CULL_FRONT_FACE - facing_front
            * ensight.objs.enums.CULL_NO_FACE - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CULLELEMENTS)
        _value = cast(int, value)
        return _value

    @CULLELEMENTS.setter
    def CULLELEMENTS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CULLELEMENTS, value)

    @property
    def cullelements(self) -> int:
        """CULLELEMENTS property
        
        Do not show elements
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CULL_BACK_FACE - facing_back
            * ensight.objs.enums.CULL_FRONT_FACE - facing_front
            * ensight.objs.enums.CULL_NO_FACE - off
        
        Note: both 'cullelements' and 'CULLELEMENTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CULLELEMENTS)
        _value = cast(int, value)
        return _value

    @cullelements.setter
    def cullelements(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CULLELEMENTS, value)

    @property
    def HIDDENSURFACE(self) -> int:
        """HIDDENSURFACE property
        
        Hidden surface
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENSURFACE)
        _value = cast(int, value)
        return _value

    @HIDDENSURFACE.setter
    def HIDDENSURFACE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENSURFACE, value)

    @property
    def hiddensurface(self) -> int:
        """HIDDENSURFACE property
        
        Hidden surface
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'hiddensurface' and 'HIDDENSURFACE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENSURFACE)
        _value = cast(int, value)
        return _value

    @hiddensurface.setter
    def hiddensurface(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENSURFACE, value)

    @property
    def BOUNDINGREP(self) -> int:
        """BOUNDINGREP property
        
        Bounding Rep(Fast display)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.BOX_DRAW_MODEL - off
            * ensight.objs.enums.BOX_DRAW_BOX - box
            * ensight.objs.enums.BOX_DRAW_POINTS - points
            * ensight.objs.enums.BOX_DRAW_SPARSE_MODEL - sparse_model
            * ensight.objs.enums.BOX_DRAW_REDUCED - reduced
            * ensight.objs.enums.BOX_DRAW_NOTHING - invisible
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOUNDINGREP)
        _value = cast(int, value)
        return _value

    @BOUNDINGREP.setter
    def BOUNDINGREP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BOUNDINGREP, value)

    @property
    def boundingrep(self) -> int:
        """BOUNDINGREP property
        
        Bounding Rep(Fast display)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.BOX_DRAW_MODEL - off
            * ensight.objs.enums.BOX_DRAW_BOX - box
            * ensight.objs.enums.BOX_DRAW_POINTS - points
            * ensight.objs.enums.BOX_DRAW_SPARSE_MODEL - sparse_model
            * ensight.objs.enums.BOX_DRAW_REDUCED - reduced
            * ensight.objs.enums.BOX_DRAW_NOTHING - invisible
        
        Note: both 'boundingrep' and 'BOUNDINGREP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOUNDINGREP)
        _value = cast(int, value)
        return _value

    @boundingrep.setter
    def boundingrep(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BOUNDINGREP, value)

    @property
    def REFFRAME(self) -> int:
        """REFFRAME property
        
        Reference frame
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REFFRAME)
        _value = cast(int, value)
        return _value

    @REFFRAME.setter
    def REFFRAME(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REFFRAME, value)

    @property
    def refframe(self) -> int:
        """REFFRAME property
        
        Reference frame
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'refframe' and 'REFFRAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REFFRAME)
        _value = cast(int, value)
        return _value

    @refframe.setter
    def refframe(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REFFRAME, value)

    @property
    def VOLUMEQUALITY(self) -> int:
        """VOLUMEQUALITY property
        
        Volume quality
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VOL_RENDER_QUALITY_LOW - low
            * ensight.objs.enums.VOL_RENDER_QUALITY_MEDIUM - medium
            * ensight.objs.enums.VOL_RENDER_QUALITY_HIGH - high
            * ensight.objs.enums.VOL_RENDER_QUALITY_BEST - best
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUMEQUALITY)
        _value = cast(int, value)
        return _value

    @VOLUMEQUALITY.setter
    def VOLUMEQUALITY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VOLUMEQUALITY, value)

    @property
    def volumequality(self) -> int:
        """VOLUMEQUALITY property
        
        Volume quality
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VOL_RENDER_QUALITY_LOW - low
            * ensight.objs.enums.VOL_RENDER_QUALITY_MEDIUM - medium
            * ensight.objs.enums.VOL_RENDER_QUALITY_HIGH - high
            * ensight.objs.enums.VOL_RENDER_QUALITY_BEST - best
        
        Note: both 'volumequality' and 'VOLUMEQUALITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUMEQUALITY)
        _value = cast(int, value)
        return _value

    @volumequality.setter
    def volumequality(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VOLUMEQUALITY, value)

    @property
    def IJKAXIS(self) -> int:
        """IJKAXIS property
        
        IJK axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.IJKAXIS)
        _value = cast(int, value)
        return _value

    @IJKAXIS.setter
    def IJKAXIS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.IJKAXIS, value)

    @property
    def ijkaxis(self) -> int:
        """IJKAXIS property
        
        IJK axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'ijkaxis' and 'IJKAXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.IJKAXIS)
        _value = cast(int, value)
        return _value

    @ijkaxis.setter
    def ijkaxis(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.IJKAXIS, value)

    @property
    def IJKAXISSCALE(self) -> float:
        """IJKAXISSCALE property
        
        IJK axis scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.IJKAXISSCALE)
        _value = cast(float, value)
        return _value

    @IJKAXISSCALE.setter
    def IJKAXISSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.IJKAXISSCALE, value)

    @property
    def ijkaxisscale(self) -> float:
        """IJKAXISSCALE property
        
        IJK axis scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'ijkaxisscale' and 'IJKAXISSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.IJKAXISSCALE)
        _value = cast(float, value)
        return _value

    @ijkaxisscale.setter
    def ijkaxisscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.IJKAXISSCALE, value)

    @property
    def SYMMETRYANGLE(self) -> float:
        """SYMMETRYANGLE property
        
        Symmetry angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 180.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYANGLE)
        _value = cast(float, value)
        return _value

    @SYMMETRYANGLE.setter
    def SYMMETRYANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYANGLE, value)

    @property
    def symmetryangle(self) -> float:
        """SYMMETRYANGLE property
        
        Symmetry angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 180.0]
        
        Note: both 'symmetryangle' and 'SYMMETRYANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYMMETRYANGLE)
        _value = cast(float, value)
        return _value

    @symmetryangle.setter
    def symmetryangle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SYMMETRYANGLE, value)

    @property
    def DENSITY(self) -> ensobjlist['ENS_VAR']:
        """DENSITY property
        
        Density
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DENSITY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @DENSITY.setter
    def DENSITY(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.DENSITY, value)

    @property
    def density(self) -> ensobjlist['ENS_VAR']:
        """DENSITY property
        
        Density
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'density' and 'DENSITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DENSITY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @density.setter
    def density(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.DENSITY, value)

    @property
    def MOMENTUM(self) -> ensobjlist['ENS_VAR']:
        """MOMENTUM property
        
        Momentum
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MOMENTUM)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @MOMENTUM.setter
    def MOMENTUM(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.MOMENTUM, value)

    @property
    def momentum(self) -> ensobjlist['ENS_VAR']:
        """MOMENTUM property
        
        Momentum
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
            * Element
        
        Note: both 'momentum' and 'MOMENTUM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MOMENTUM)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @momentum.setter
    def momentum(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.MOMENTUM, value)

    @property
    def VELOCITY(self) -> ensobjlist['ENS_VAR']:
        """VELOCITY property
        
        Velocity
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VELOCITY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @VELOCITY.setter
    def VELOCITY(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VELOCITY, value)

    @property
    def velocity(self) -> ensobjlist['ENS_VAR']:
        """VELOCITY property
        
        Velocity
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Vector
            * Nodal
            * Element
        
        Note: both 'velocity' and 'VELOCITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VELOCITY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @velocity.setter
    def velocity(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.VELOCITY, value)

    @property
    def RATIOOFSPECHEAT(self) -> ensobjlist['ENS_VAR']:
        """RATIOOFSPECHEAT property
        
        Ratio of spec heat
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RATIOOFSPECHEAT)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @RATIOOFSPECHEAT.setter
    def RATIOOFSPECHEAT(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.RATIOOFSPECHEAT, value)

    @property
    def ratioofspecheat(self) -> ensobjlist['ENS_VAR']:
        """RATIOOFSPECHEAT property
        
        Ratio of spec heat
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'ratioofspecheat' and 'RATIOOFSPECHEAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RATIOOFSPECHEAT)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @ratioofspecheat.setter
    def ratioofspecheat(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.RATIOOFSPECHEAT, value)

    @property
    def METHOD(self) -> int:
        """METHOD property
        
        Method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FX_SHOCK_REGION - region
            * ensight.objs.enums.FX_SHOCK_SURFACE - surface
        
        """
        value = self.getattr(self._session.ensight.objs.enums.METHOD)
        _value = cast(int, value)
        return _value

    @METHOD.setter
    def METHOD(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.METHOD, value)

    @property
    def method(self) -> int:
        """METHOD property
        
        Method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.FX_SHOCK_REGION - region
            * ensight.objs.enums.FX_SHOCK_SURFACE - surface
        
        Note: both 'method' and 'METHOD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.METHOD)
        _value = cast(int, value)
        return _value

    @method.setter
    def method(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.METHOD, value)

    @property
    def THRESHOLD(self) -> ensobjlist['ENS_VAR']:
        """THRESHOLD property
        
        Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLD)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @THRESHOLD.setter
    def THRESHOLD(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLD, value)

    @property
    def threshold(self) -> ensobjlist['ENS_VAR']:
        """THRESHOLD property
        
        Variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Vector
            * Nodal
            * Element
        
        Note: both 'threshold' and 'THRESHOLD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLD)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @threshold.setter
    def threshold(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLD, value)

    @property
    def THRESHOLDFILTER(self) -> int:
        """THRESHOLDFILTER property
        
        Filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ROP_LTEQ - <=
            * ensight.objs.enums.ROP_GTEQ - >=
        
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDFILTER)
        _value = cast(int, value)
        return _value

    @THRESHOLDFILTER.setter
    def THRESHOLDFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDFILTER, value)

    @property
    def thresholdfilter(self) -> int:
        """THRESHOLDFILTER property
        
        Filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ROP_LTEQ - <=
            * ensight.objs.enums.ROP_GTEQ - >=
        
        Note: both 'thresholdfilter' and 'THRESHOLDFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDFILTER)
        _value = cast(int, value)
        return _value

    @thresholdfilter.setter
    def thresholdfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDFILTER, value)

    @property
    def THRESHOLDVALUE(self) -> float:
        """THRESHOLDVALUE property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDVALUE)
        _value = cast(float, value)
        return _value

    @THRESHOLDVALUE.setter
    def THRESHOLDVALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDVALUE, value)

    @property
    def thresholdvalue(self) -> float:
        """THRESHOLDVALUE property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'thresholdvalue' and 'THRESHOLDVALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDVALUE)
        _value = cast(float, value)
        return _value

    @thresholdvalue.setter
    def thresholdvalue(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDVALUE, value)

    @property
    def THRESHOLDMIN(self) -> float:
        """THRESHOLDMIN property
        
        Min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDMIN)
        _value = cast(float, value)
        return _value

    @THRESHOLDMIN.setter
    def THRESHOLDMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDMIN, value)

    @property
    def thresholdmin(self) -> float:
        """THRESHOLDMIN property
        
        Min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'thresholdmin' and 'THRESHOLDMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDMIN)
        _value = cast(float, value)
        return _value

    @thresholdmin.setter
    def thresholdmin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDMIN, value)

    @property
    def THRESHOLDMAX(self) -> float:
        """THRESHOLDMAX property
        
        Max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDMAX)
        _value = cast(float, value)
        return _value

    @THRESHOLDMAX.setter
    def THRESHOLDMAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDMAX, value)

    @property
    def thresholdmax(self) -> float:
        """THRESHOLDMAX property
        
        Max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'thresholdmax' and 'THRESHOLDMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.THRESHOLDMAX)
        _value = cast(float, value)
        return _value

    @thresholdmax.setter
    def thresholdmax(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.THRESHOLDMAX, value)

    @property
    def TOTALENERGY(self) -> ensobjlist['ENS_VAR']:
        """TOTALENERGY property
        
        Total energy
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TOTALENERGY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @TOTALENERGY.setter
    def TOTALENERGY(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TOTALENERGY, value)

    @property
    def totalenergy(self) -> ensobjlist['ENS_VAR']:
        """TOTALENERGY property
        
        Total energy
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'totalenergy' and 'TOTALENERGY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TOTALENERGY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @totalenergy.setter
    def totalenergy(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TOTALENERGY, value)

    @property
    def ENTHALPY(self) -> ensobjlist['ENS_VAR']:
        """ENTHALPY property
        
        Enthalpy
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENTHALPY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @ENTHALPY.setter
    def ENTHALPY(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.ENTHALPY, value)

    @property
    def enthalpy(self) -> ensobjlist['ENS_VAR']:
        """ENTHALPY property
        
        Enthalpy
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'enthalpy' and 'ENTHALPY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENTHALPY)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @enthalpy.setter
    def enthalpy(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.ENTHALPY, value)

    @property
    def MACH(self) -> ensobjlist['ENS_VAR']:
        """MACH property
        
        Mach
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MACH)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @MACH.setter
    def MACH(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.MACH, value)

    @property
    def mach(self) -> ensobjlist['ENS_VAR']:
        """MACH property
        
        Mach
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'mach' and 'MACH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MACH)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @mach.setter
    def mach(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.MACH, value)

    @property
    def PRESSURE(self) -> ensobjlist['ENS_VAR']:
        """PRESSURE property
        
        Pressure
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PRESSURE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @PRESSURE.setter
    def PRESSURE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.PRESSURE, value)

    @property
    def pressure(self) -> ensobjlist['ENS_VAR']:
        """PRESSURE property
        
        Pressure
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'pressure' and 'PRESSURE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PRESSURE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @pressure.setter
    def pressure(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.PRESSURE, value)

    @property
    def GASCONSTANT(self) -> ensobjlist['ENS_VAR']:
        """GASCONSTANT property
        
        Gas constant
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GASCONSTANT)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @GASCONSTANT.setter
    def GASCONSTANT(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.GASCONSTANT, value)

    @property
    def gasconstant(self) -> ensobjlist['ENS_VAR']:
        """GASCONSTANT property
        
        Gas constant
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'gasconstant' and 'GASCONSTANT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GASCONSTANT)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @gasconstant.setter
    def gasconstant(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.GASCONSTANT, value)

    @property
    def TEMPERATURE(self) -> ensobjlist['ENS_VAR']:
        """TEMPERATURE property
        
        Temperature
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEMPERATURE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @TEMPERATURE.setter
    def TEMPERATURE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TEMPERATURE, value)

    @property
    def temperature(self) -> ensobjlist['ENS_VAR']:
        """TEMPERATURE property
        
        Temperature
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'temperature' and 'TEMPERATURE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEMPERATURE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @temperature.setter
    def temperature(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.TEMPERATURE, value)

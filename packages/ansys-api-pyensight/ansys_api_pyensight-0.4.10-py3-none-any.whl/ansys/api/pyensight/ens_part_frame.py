"""ens_part_frame module

The ens_part_frame module provides a proxy interface to EnSight ENS_PART_FRAME instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from ansys.api.pyensight.ens_part import ENS_PART
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_PART_FRAME(ENS_PART):
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

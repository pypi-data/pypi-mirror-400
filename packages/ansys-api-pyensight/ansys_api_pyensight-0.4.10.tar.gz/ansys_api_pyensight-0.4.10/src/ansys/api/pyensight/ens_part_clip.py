"""ens_part_clip module

The ens_part_clip module provides a proxy interface to EnSight ENS_PART_CLIP instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from ansys.api.pyensight.ens_part import ENS_PART
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_PART_CLIP(ENS_PART):
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
    def DOMAIN(self) -> int:
        """DOMAIN property
        
        Domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_DOMAIN_INTER - intersect
            * ensight.objs.enums.CLIP_DOMAIN_IN - inside
            * ensight.objs.enums.CLIP_DOMAIN_OUT - outside
            * ensight.objs.enums.CLIP_DOMAIN_CRINKLY - crinkly
        
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
        
        Domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_DOMAIN_INTER - intersect
            * ensight.objs.enums.CLIP_DOMAIN_IN - inside
            * ensight.objs.enums.CLIP_DOMAIN_OUT - outside
            * ensight.objs.enums.CLIP_DOMAIN_CRINKLY - crinkly
        
        Note: both 'domain' and 'DOMAIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DOMAIN)
        _value = cast(int, value)
        return _value

    @domain.setter
    def domain(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOMAIN, value)

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
    def RADIUS(self) -> float:
        """RADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RADIUS)
        _value = cast(float, value)
        return _value

    @RADIUS.setter
    def RADIUS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.RADIUS, value)

    @property
    def radius(self) -> float:
        """RADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'radius' and 'RADIUS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RADIUS)
        _value = cast(float, value)
        return _value

    @radius.setter
    def radius(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.RADIUS, value)

    @property
    def ANGLE(self) -> float:
        """ANGLE property
        
        Angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANGLE)
        _value = cast(float, value)
        return _value

    @ANGLE.setter
    def ANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANGLE, value)

    @property
    def angle(self) -> float:
        """ANGLE property
        
        Angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'angle' and 'ANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANGLE)
        _value = cast(float, value)
        return _value

    @angle.setter
    def angle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANGLE, value)

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
        
        Show axis
        
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
        
        Show axis
        
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
    def TOOL(self) -> int:
        """TOOL property
        
        Clipping tool
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CT_IJK - ijk
            * ensight.objs.enums.CT_LINE - line
            * ensight.objs.enums.CT_PLNE - plane
            * ensight.objs.enums.CT_CYLD - cylinder
            * ensight.objs.enums.CT_SPHR - sphere
            * ensight.objs.enums.CT_CONE - cone
            * ensight.objs.enums.CT_REVO - revolution
            * ensight.objs.enums.CT_PART - 1d_part
            * ensight.objs.enums.CT_GENQ - general_quadric
            * ensight.objs.enums.CT_XYZ - xyz
            * ensight.objs.enums.CT_BOX - xyz_box
            * ensight.objs.enums.CT_RTZ - rtz
            * ensight.objs.enums.CT_SPLINE - spline
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TOOL)
        _value = cast(int, value)
        return _value

    @TOOL.setter
    def TOOL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TOOL, value)

    @property
    def tool(self) -> int:
        """TOOL property
        
        Clipping tool
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CT_IJK - ijk
            * ensight.objs.enums.CT_LINE - line
            * ensight.objs.enums.CT_PLNE - plane
            * ensight.objs.enums.CT_CYLD - cylinder
            * ensight.objs.enums.CT_SPHR - sphere
            * ensight.objs.enums.CT_CONE - cone
            * ensight.objs.enums.CT_REVO - revolution
            * ensight.objs.enums.CT_PART - 1d_part
            * ensight.objs.enums.CT_GENQ - general_quadric
            * ensight.objs.enums.CT_XYZ - xyz
            * ensight.objs.enums.CT_BOX - xyz_box
            * ensight.objs.enums.CT_RTZ - rtz
            * ensight.objs.enums.CT_SPLINE - spline
        
        Note: both 'tool' and 'TOOL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TOOL)
        _value = cast(int, value)
        return _value

    @tool.setter
    def tool(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TOOL, value)

    @property
    def TYPE(self) -> int:
        """TYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PL_TYPE_MESH - mesh
            * ensight.objs.enums.PL_TYPE_GRID - grid
            * ensight.objs.enums.PL_TYPE_GRID_FULL - grid_full
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TYPE)
        _value = cast(int, value)
        return _value

    @TYPE.setter
    def TYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TYPE, value)

    @property
    def type(self) -> int:
        """TYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.PL_TYPE_MESH - mesh
            * ensight.objs.enums.PL_TYPE_GRID - grid
            * ensight.objs.enums.PL_TYPE_GRID_FULL - grid_full
        
        Note: both 'type' and 'TYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TYPE)
        _value = cast(int, value)
        return _value

    @type.setter
    def type(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TYPE, value)

    @property
    def EXTENTS(self) -> int:
        """EXTENTS property
        
        Extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_PLANE_FINITE - finite
            * ensight.objs.enums.CLIP_PLANE_INFINITE - infinite
        
        """
        value = self.getattr(self._session.ensight.objs.enums.EXTENTS)
        _value = cast(int, value)
        return _value

    @EXTENTS.setter
    def EXTENTS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.EXTENTS, value)

    @property
    def extents(self) -> int:
        """EXTENTS property
        
        Extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_PLANE_FINITE - finite
            * ensight.objs.enums.CLIP_PLANE_INFINITE - infinite
        
        Note: both 'extents' and 'EXTENTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.EXTENTS)
        _value = cast(int, value)
        return _value

    @extents.setter
    def extents(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.EXTENTS, value)

    @property
    def DOMAINXYZRTZLINE(self) -> int:
        """DOMAINXYZRTZLINE property
        
        Domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_DOMAIN_INTER - intersect
            * ensight.objs.enums.CLIP_DOMAIN_CRINKLY - crinkly
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DOMAINXYZRTZLINE)
        _value = cast(int, value)
        return _value

    @DOMAINXYZRTZLINE.setter
    def DOMAINXYZRTZLINE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOMAINXYZRTZLINE, value)

    @property
    def domainxyzrtzline(self) -> int:
        """DOMAINXYZRTZLINE property
        
        Domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_DOMAIN_INTER - intersect
            * ensight.objs.enums.CLIP_DOMAIN_CRINKLY - crinkly
        
        Note: both 'domainxyzrtzline' and 'DOMAINXYZRTZLINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DOMAINXYZRTZLINE)
        _value = cast(int, value)
        return _value

    @domainxyzrtzline.setter
    def domainxyzrtzline(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOMAINXYZRTZLINE, value)

    @property
    def MESHPLANEIJK(self) -> int:
        """MESHPLANEIJK property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICEI - I
            * ensight.objs.enums.MESH_SLICEJ - J
            * ensight.objs.enums.MESH_SLICEK - K
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANEIJK)
        _value = cast(int, value)
        return _value

    @MESHPLANEIJK.setter
    def MESHPLANEIJK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANEIJK, value)

    @property
    def meshplaneijk(self) -> int:
        """MESHPLANEIJK property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICEI - I
            * ensight.objs.enums.MESH_SLICEJ - J
            * ensight.objs.enums.MESH_SLICEK - K
        
        Note: both 'meshplaneijk' and 'MESHPLANEIJK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANEIJK)
        _value = cast(int, value)
        return _value

    @meshplaneijk.setter
    def meshplaneijk(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANEIJK, value)

    @property
    def VALUEIJK(self) -> float:
        """VALUEIJK property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUEIJK)
        _value = cast(float, value)
        return _value

    @VALUEIJK.setter
    def VALUEIJK(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUEIJK, value)

    @property
    def valueijk(self) -> float:
        """VALUEIJK property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'valueijk' and 'VALUEIJK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUEIJK)
        _value = cast(float, value)
        return _value

    @valueijk.setter
    def valueijk(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUEIJK, value)

    @property
    def DIMENSION2(self) -> List[float]:
        """DIMENSION2 property
        
        Dimension 2 limit
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION2)
        _value = cast(List[float], value)
        return _value

    @DIMENSION2.setter
    def DIMENSION2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION2, value)

    @property
    def dimension2(self) -> List[float]:
        """DIMENSION2 property
        
        Dimension 2 limit
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'dimension2' and 'DIMENSION2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION2)
        _value = cast(List[float], value)
        return _value

    @dimension2.setter
    def dimension2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION2, value)

    @property
    def DIMENSION2STEP(self) -> float:
        """DIMENSION2STEP property
        
        Dimension 2 step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION2STEP)
        _value = cast(float, value)
        return _value

    @DIMENSION2STEP.setter
    def DIMENSION2STEP(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION2STEP, value)

    @property
    def dimension2step(self) -> float:
        """DIMENSION2STEP property
        
        Dimension 2 step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'dimension2step' and 'DIMENSION2STEP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION2STEP)
        _value = cast(float, value)
        return _value

    @dimension2step.setter
    def dimension2step(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION2STEP, value)

    @property
    def DIMENSION3(self) -> List[float]:
        """DIMENSION3 property
        
        Dimension 3 limit
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION3)
        _value = cast(List[float], value)
        return _value

    @DIMENSION3.setter
    def DIMENSION3(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION3, value)

    @property
    def dimension3(self) -> List[float]:
        """DIMENSION3 property
        
        Dimension 3 limit
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'dimension3' and 'DIMENSION3' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION3)
        _value = cast(List[float], value)
        return _value

    @dimension3.setter
    def dimension3(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION3, value)

    @property
    def DIMENSION3STEP(self) -> float:
        """DIMENSION3STEP property
        
        Dimension 3 step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION3STEP)
        _value = cast(float, value)
        return _value

    @DIMENSION3STEP.setter
    def DIMENSION3STEP(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION3STEP, value)

    @property
    def dimension3step(self) -> float:
        """DIMENSION3STEP property
        
        Dimension 3 step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'dimension3step' and 'DIMENSION3STEP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION3STEP)
        _value = cast(float, value)
        return _value

    @dimension3step.setter
    def dimension3step(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION3STEP, value)

    @property
    def IJKSCALE(self) -> float:
        """IJKSCALE property
        
        Axis scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.IJKSCALE)
        _value = cast(float, value)
        return _value

    @IJKSCALE.setter
    def IJKSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.IJKSCALE, value)

    @property
    def ijkscale(self) -> float:
        """IJKSCALE property
        
        Axis scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'ijkscale' and 'IJKSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.IJKSCALE)
        _value = cast(float, value)
        return _value

    @ijkscale.setter
    def ijkscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.IJKSCALE, value)

    @property
    def VALUEXYZ(self) -> float:
        """VALUEXYZ property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUEXYZ)
        _value = cast(float, value)
        return _value

    @VALUEXYZ.setter
    def VALUEXYZ(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUEXYZ, value)

    @property
    def valuexyz(self) -> float:
        """VALUEXYZ property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'valuexyz' and 'VALUEXYZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUEXYZ)
        _value = cast(float, value)
        return _value

    @valuexyz.setter
    def valuexyz(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUEXYZ, value)

    @property
    def MESHPLANEXYZ(self) -> int:
        """MESHPLANEXYZ property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICE_X - X
            * ensight.objs.enums.MESH_SLICE_Y - Y
            * ensight.objs.enums.MESH_SLICE_Z - Z
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANEXYZ)
        _value = cast(int, value)
        return _value

    @MESHPLANEXYZ.setter
    def MESHPLANEXYZ(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANEXYZ, value)

    @property
    def meshplanexyz(self) -> int:
        """MESHPLANEXYZ property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICE_X - X
            * ensight.objs.enums.MESH_SLICE_Y - Y
            * ensight.objs.enums.MESH_SLICE_Z - Z
        
        Note: both 'meshplanexyz' and 'MESHPLANEXYZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANEXYZ)
        _value = cast(int, value)
        return _value

    @meshplanexyz.setter
    def meshplanexyz(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANEXYZ, value)

    @property
    def MESHPLANERTZ(self) -> int:
        """MESHPLANERTZ property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICE_RTZ_R - R
            * ensight.objs.enums.MESH_SLICE_RTZ_T - T
            * ensight.objs.enums.MESH_SLICE_RTZ_Z - Z
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANERTZ)
        _value = cast(int, value)
        return _value

    @MESHPLANERTZ.setter
    def MESHPLANERTZ(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANERTZ, value)

    @property
    def meshplanertz(self) -> int:
        """MESHPLANERTZ property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICE_RTZ_R - R
            * ensight.objs.enums.MESH_SLICE_RTZ_T - T
            * ensight.objs.enums.MESH_SLICE_RTZ_Z - Z
        
        Note: both 'meshplanertz' and 'MESHPLANERTZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANERTZ)
        _value = cast(int, value)
        return _value

    @meshplanertz.setter
    def meshplanertz(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANERTZ, value)

    @property
    def VALUERTZ(self) -> float:
        """VALUERTZ property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUERTZ)
        _value = cast(float, value)
        return _value

    @VALUERTZ.setter
    def VALUERTZ(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUERTZ, value)

    @property
    def valuertz(self) -> float:
        """VALUERTZ property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'valuertz' and 'VALUERTZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUERTZ)
        _value = cast(float, value)
        return _value

    @valuertz.setter
    def valuertz(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUERTZ, value)

    @property
    def RTZAXIS(self) -> int:
        """RTZAXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ROT_SYMM_X_AXIS - X
            * ensight.objs.enums.ROT_SYMM_Y_AXIS - Y
            * ensight.objs.enums.ROT_SYMM_Z_AXIS - Z
            * ensight.objs.enums.ROT_SYMM_X_AXIS - R
            * ensight.objs.enums.ROT_SYMM_Y_AXIS - T
            * ensight.objs.enums.ROT_SYMM_Z_AXIS - Z
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RTZAXIS)
        _value = cast(int, value)
        return _value

    @RTZAXIS.setter
    def RTZAXIS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RTZAXIS, value)

    @property
    def rtzaxis(self) -> int:
        """RTZAXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ROT_SYMM_X_AXIS - X
            * ensight.objs.enums.ROT_SYMM_Y_AXIS - Y
            * ensight.objs.enums.ROT_SYMM_Z_AXIS - Z
            * ensight.objs.enums.ROT_SYMM_X_AXIS - R
            * ensight.objs.enums.ROT_SYMM_Y_AXIS - T
            * ensight.objs.enums.ROT_SYMM_Z_AXIS - Z
        
        Note: both 'rtzaxis' and 'RTZAXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RTZAXIS)
        _value = cast(int, value)
        return _value

    @rtzaxis.setter
    def rtzaxis(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.RTZAXIS, value)

    @property
    def VALUESPLINE(self) -> float:
        """VALUESPLINE property
        
        Spline value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUESPLINE)
        _value = cast(float, value)
        return _value

    @VALUESPLINE.setter
    def VALUESPLINE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUESPLINE, value)

    @property
    def valuespline(self) -> float:
        """VALUESPLINE property
        
        Spline value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'valuespline' and 'VALUESPLINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUESPLINE)
        _value = cast(float, value)
        return _value

    @valuespline.setter
    def valuespline(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUESPLINE, value)

    @property
    def SPLINEID(self) -> int:
        """SPLINEID property
        
        Spline ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPLINEID)
        _value = cast(int, value)
        return _value

    @SPLINEID.setter
    def SPLINEID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPLINEID, value)

    @property
    def splineid(self) -> int:
        """SPLINEID property
        
        Spline ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'splineid' and 'SPLINEID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPLINEID)
        _value = cast(int, value)
        return _value

    @splineid.setter
    def splineid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SPLINEID, value)

    @property
    def SAMPLEPOINTSSPLINE(self) -> int:
        """SAMPLEPOINTSSPLINE property
        
        Sample points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEPOINTSSPLINE)
        _value = cast(int, value)
        return _value

    @SAMPLEPOINTSSPLINE.setter
    def SAMPLEPOINTSSPLINE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEPOINTSSPLINE, value)

    @property
    def samplepointsspline(self) -> int:
        """SAMPLEPOINTSSPLINE property
        
        Sample points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, inf]
        
        Note: both 'samplepointsspline' and 'SAMPLEPOINTSSPLINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEPOINTSSPLINE)
        _value = cast(int, value)
        return _value

    @samplepointsspline.setter
    def samplepointsspline(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEPOINTSSPLINE, value)

    @property
    def SAMPLEPOINTSLINE(self) -> int:
        """SAMPLEPOINTSLINE property
        
        Sample points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEPOINTSLINE)
        _value = cast(int, value)
        return _value

    @SAMPLEPOINTSLINE.setter
    def SAMPLEPOINTSLINE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEPOINTSLINE, value)

    @property
    def samplepointsline(self) -> int:
        """SAMPLEPOINTSLINE property
        
        Sample points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [2, inf]
        
        Note: both 'samplepointsline' and 'SAMPLEPOINTSLINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEPOINTSLINE)
        _value = cast(int, value)
        return _value

    @samplepointsline.setter
    def samplepointsline(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEPOINTSLINE, value)

    @property
    def CLIPLINEPT1(self) -> List[float]:
        """CLIPLINEPT1 property
        
        Point 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPLINEPT1)
        _value = cast(List[float], value)
        return _value

    @CLIPLINEPT1.setter
    def CLIPLINEPT1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPLINEPT1, value)

    @property
    def cliplinept1(self) -> List[float]:
        """CLIPLINEPT1 property
        
        Point 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'cliplinept1' and 'CLIPLINEPT1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPLINEPT1)
        _value = cast(List[float], value)
        return _value

    @cliplinept1.setter
    def cliplinept1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPLINEPT1, value)

    @property
    def CLIPLINEPT2(self) -> List[float]:
        """CLIPLINEPT2 property
        
        Point 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPLINEPT2)
        _value = cast(List[float], value)
        return _value

    @CLIPLINEPT2.setter
    def CLIPLINEPT2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPLINEPT2, value)

    @property
    def cliplinept2(self) -> List[float]:
        """CLIPLINEPT2 property
        
        Point 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'cliplinept2' and 'CLIPLINEPT2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPLINEPT2)
        _value = cast(List[float], value)
        return _value

    @cliplinept2.setter
    def cliplinept2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPLINEPT2, value)

    @property
    def GRIDPTS(self) -> List[int]:
        """GRIDPTS property
        
        Grid XY points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDPTS)
        _value = cast(List[int], value)
        return _value

    @GRIDPTS.setter
    def GRIDPTS(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDPTS, value)

    @property
    def gridpts(self) -> List[int]:
        """GRIDPTS property
        
        Grid XY points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        Note: both 'gridpts' and 'GRIDPTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDPTS)
        _value = cast(List[int], value)
        return _value

    @gridpts.setter
    def gridpts(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDPTS, value)

    @property
    def CLIPPLANEPT1(self) -> List[float]:
        """CLIPPLANEPT1 property
        
        Point 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPPLANEPT1)
        _value = cast(List[float], value)
        return _value

    @CLIPPLANEPT1.setter
    def CLIPPLANEPT1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPPLANEPT1, value)

    @property
    def clipplanept1(self) -> List[float]:
        """CLIPPLANEPT1 property
        
        Point 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'clipplanept1' and 'CLIPPLANEPT1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPPLANEPT1)
        _value = cast(List[float], value)
        return _value

    @clipplanept1.setter
    def clipplanept1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPPLANEPT1, value)

    @property
    def CLIPPLANEPT2(self) -> List[float]:
        """CLIPPLANEPT2 property
        
        Point 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPPLANEPT2)
        _value = cast(List[float], value)
        return _value

    @CLIPPLANEPT2.setter
    def CLIPPLANEPT2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPPLANEPT2, value)

    @property
    def clipplanept2(self) -> List[float]:
        """CLIPPLANEPT2 property
        
        Point 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'clipplanept2' and 'CLIPPLANEPT2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPPLANEPT2)
        _value = cast(List[float], value)
        return _value

    @clipplanept2.setter
    def clipplanept2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPPLANEPT2, value)

    @property
    def CLIPPLANEPT3(self) -> List[float]:
        """CLIPPLANEPT3 property
        
        Point 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPPLANEPT3)
        _value = cast(List[float], value)
        return _value

    @CLIPPLANEPT3.setter
    def CLIPPLANEPT3(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPPLANEPT3, value)

    @property
    def clipplanept3(self) -> List[float]:
        """CLIPPLANEPT3 property
        
        Point 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'clipplanept3' and 'CLIPPLANEPT3' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLIPPLANEPT3)
        _value = cast(List[float], value)
        return _value

    @clipplanept3.setter
    def clipplanept3(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLIPPLANEPT3, value)

    @property
    def DOMAINBOX(self) -> int:
        """DOMAINBOX property
        
        Domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_DOMAIN_INTER - intersect
            * ensight.objs.enums.CLIP_DOMAIN_IN - inside
            * ensight.objs.enums.CLIP_DOMAIN_OUT - outside
            * ensight.objs.enums.CLIP_DOMAIN_INOUT - in_out
            * ensight.objs.enums.CLIP_DOMAIN_CRINKLY - crinkly
            * ensight.objs.enums.CLIP_DOMAIN_VOLUME - volume
            * ensight.objs.enums.CLIP_DOMAIN_RECT - rectilinear
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DOMAINBOX)
        _value = cast(int, value)
        return _value

    @DOMAINBOX.setter
    def DOMAINBOX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOMAINBOX, value)

    @property
    def domainbox(self) -> int:
        """DOMAINBOX property
        
        Domain
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.CLIP_DOMAIN_INTER - intersect
            * ensight.objs.enums.CLIP_DOMAIN_IN - inside
            * ensight.objs.enums.CLIP_DOMAIN_OUT - outside
            * ensight.objs.enums.CLIP_DOMAIN_INOUT - in_out
            * ensight.objs.enums.CLIP_DOMAIN_CRINKLY - crinkly
            * ensight.objs.enums.CLIP_DOMAIN_VOLUME - volume
            * ensight.objs.enums.CLIP_DOMAIN_RECT - rectilinear
        
        Note: both 'domainbox' and 'DOMAINBOX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DOMAINBOX)
        _value = cast(int, value)
        return _value

    @domainbox.setter
    def domainbox(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DOMAINBOX, value)

    @property
    def SAMPLETYPE(self) -> int:
        """SAMPLETYPE property
        
        Sample
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.SAMPLE_UNIFORM - uniform
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLETYPE)
        _value = cast(int, value)
        return _value

    @SAMPLETYPE.setter
    def SAMPLETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLETYPE, value)

    @property
    def sampletype(self) -> int:
        """SAMPLETYPE property
        
        Sample
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.SAMPLE_UNIFORM - uniform
        
        Note: both 'sampletype' and 'SAMPLETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLETYPE)
        _value = cast(int, value)
        return _value

    @sampletype.setter
    def sampletype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLETYPE, value)

    @property
    def SAMPLEXYZ(self) -> List[int]:
        """SAMPLEXYZ property
        
        Sample step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        Range:
            [6, 4096]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEXYZ)
        _value = cast(List[int], value)
        return _value

    @SAMPLEXYZ.setter
    def SAMPLEXYZ(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEXYZ, value)

    @property
    def samplexyz(self) -> List[int]:
        """SAMPLEXYZ property
        
        Sample step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 3 element array
        Range:
            [6, 4096]
        
        Note: both 'samplexyz' and 'SAMPLEXYZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SAMPLEXYZ)
        _value = cast(List[int], value)
        return _value

    @samplexyz.setter
    def samplexyz(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.SAMPLEXYZ, value)

    @property
    def BOXORIGIN(self) -> List[float]:
        """BOXORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXORIGIN)
        _value = cast(List[float], value)
        return _value

    @BOXORIGIN.setter
    def BOXORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXORIGIN, value)

    @property
    def boxorigin(self) -> List[float]:
        """BOXORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'boxorigin' and 'BOXORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXORIGIN)
        _value = cast(List[float], value)
        return _value

    @boxorigin.setter
    def boxorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXORIGIN, value)

    @property
    def BOXLENGTH(self) -> List[float]:
        """BOXLENGTH property
        
        Length
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXLENGTH)
        _value = cast(List[float], value)
        return _value

    @BOXLENGTH.setter
    def BOXLENGTH(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXLENGTH, value)

    @property
    def boxlength(self) -> List[float]:
        """BOXLENGTH property
        
        Length
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        Range:
            [0.0, inf]
        
        Note: both 'boxlength' and 'BOXLENGTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXLENGTH)
        _value = cast(List[float], value)
        return _value

    @boxlength.setter
    def boxlength(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXLENGTH, value)

    @property
    def BOXAXISX(self) -> List[float]:
        """BOXAXISX property
        
        Orient X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXAXISX)
        _value = cast(List[float], value)
        return _value

    @BOXAXISX.setter
    def BOXAXISX(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXAXISX, value)

    @property
    def boxaxisx(self) -> List[float]:
        """BOXAXISX property
        
        Orient X
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'boxaxisx' and 'BOXAXISX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXAXISX)
        _value = cast(List[float], value)
        return _value

    @boxaxisx.setter
    def boxaxisx(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXAXISX, value)

    @property
    def BOXAXISY(self) -> List[float]:
        """BOXAXISY property
        
        Orient Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXAXISY)
        _value = cast(List[float], value)
        return _value

    @BOXAXISY.setter
    def BOXAXISY(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXAXISY, value)

    @property
    def boxaxisy(self) -> List[float]:
        """BOXAXISY property
        
        Orient Y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'boxaxisy' and 'BOXAXISY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXAXISY)
        _value = cast(List[float], value)
        return _value

    @boxaxisy.setter
    def boxaxisy(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXAXISY, value)

    @property
    def BOXAXISZ(self) -> List[float]:
        """BOXAXISZ property
        
        Orient Z
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXAXISZ)
        _value = cast(List[float], value)
        return _value

    @BOXAXISZ.setter
    def BOXAXISZ(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXAXISZ, value)

    @property
    def boxaxisz(self) -> List[float]:
        """BOXAXISZ property
        
        Orient Z
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'boxaxisz' and 'BOXAXISZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOXAXISZ)
        _value = cast(List[float], value)
        return _value

    @boxaxisz.setter
    def boxaxisz(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BOXAXISZ, value)

    @property
    def CYLDRADIUS(self) -> float:
        """CYLDRADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDRADIUS)
        _value = cast(float, value)
        return _value

    @CYLDRADIUS.setter
    def CYLDRADIUS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDRADIUS, value)

    @property
    def cyldradius(self) -> float:
        """CYLDRADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'cyldradius' and 'CYLDRADIUS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDRADIUS)
        _value = cast(float, value)
        return _value

    @cyldradius.setter
    def cyldradius(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDRADIUS, value)

    @property
    def CYLDORIGIN(self) -> List[float]:
        """CYLDORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDORIGIN)
        _value = cast(List[float], value)
        return _value

    @CYLDORIGIN.setter
    def CYLDORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDORIGIN, value)

    @property
    def cyldorigin(self) -> List[float]:
        """CYLDORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'cyldorigin' and 'CYLDORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDORIGIN)
        _value = cast(List[float], value)
        return _value

    @cyldorigin.setter
    def cyldorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDORIGIN, value)

    @property
    def CYLDENDPOINT(self) -> List[float]:
        """CYLDENDPOINT property
        
        End point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDENDPOINT)
        _value = cast(List[float], value)
        return _value

    @CYLDENDPOINT.setter
    def CYLDENDPOINT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDENDPOINT, value)

    @property
    def cyldendpoint(self) -> List[float]:
        """CYLDENDPOINT property
        
        End point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'cyldendpoint' and 'CYLDENDPOINT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDENDPOINT)
        _value = cast(List[float], value)
        return _value

    @cyldendpoint.setter
    def cyldendpoint(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDENDPOINT, value)

    @property
    def CYLDAXISVECT(self) -> List[float]:
        """CYLDAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDAXISVECT)
        _value = cast(List[float], value)
        return _value

    @CYLDAXISVECT.setter
    def CYLDAXISVECT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDAXISVECT, value)

    @property
    def cyldaxisvect(self) -> List[float]:
        """CYLDAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'cyldaxisvect' and 'CYLDAXISVECT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CYLDAXISVECT)
        _value = cast(List[float], value)
        return _value

    @cyldaxisvect.setter
    def cyldaxisvect(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CYLDAXISVECT, value)

    @property
    def CONEANGLE(self) -> float:
        """CONEANGLE property
        
        Cone angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEANGLE)
        _value = cast(float, value)
        return _value

    @CONEANGLE.setter
    def CONEANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEANGLE, value)

    @property
    def coneangle(self) -> float:
        """CONEANGLE property
        
        Cone angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'coneangle' and 'CONEANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEANGLE)
        _value = cast(float, value)
        return _value

    @coneangle.setter
    def coneangle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEANGLE, value)

    @property
    def CONEORIGIN(self) -> List[float]:
        """CONEORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEORIGIN)
        _value = cast(List[float], value)
        return _value

    @CONEORIGIN.setter
    def CONEORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEORIGIN, value)

    @property
    def coneorigin(self) -> List[float]:
        """CONEORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'coneorigin' and 'CONEORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEORIGIN)
        _value = cast(List[float], value)
        return _value

    @coneorigin.setter
    def coneorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEORIGIN, value)

    @property
    def CONEAXISVECT(self) -> List[float]:
        """CONEAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEAXISVECT)
        _value = cast(List[float], value)
        return _value

    @CONEAXISVECT.setter
    def CONEAXISVECT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEAXISVECT, value)

    @property
    def coneaxisvect(self) -> List[float]:
        """CONEAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'coneaxisvect' and 'CONEAXISVECT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEAXISVECT)
        _value = cast(List[float], value)
        return _value

    @coneaxisvect.setter
    def coneaxisvect(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEAXISVECT, value)

    @property
    def CONEENDPOINT(self) -> List[float]:
        """CONEENDPOINT property
        
        End point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEENDPOINT)
        _value = cast(List[float], value)
        return _value

    @CONEENDPOINT.setter
    def CONEENDPOINT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEENDPOINT, value)

    @property
    def coneendpoint(self) -> List[float]:
        """CONEENDPOINT property
        
        End point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'coneendpoint' and 'CONEENDPOINT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONEENDPOINT)
        _value = cast(List[float], value)
        return _value

    @coneendpoint.setter
    def coneendpoint(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONEENDPOINT, value)

    @property
    def SPHRRADIUS(self) -> float:
        """SPHRRADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRRADIUS)
        _value = cast(float, value)
        return _value

    @SPHRRADIUS.setter
    def SPHRRADIUS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRRADIUS, value)

    @property
    def sphrradius(self) -> float:
        """SPHRRADIUS property
        
        Radius
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'sphrradius' and 'SPHRRADIUS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRRADIUS)
        _value = cast(float, value)
        return _value

    @sphrradius.setter
    def sphrradius(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRRADIUS, value)

    @property
    def SPHRORIGIN(self) -> List[float]:
        """SPHRORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRORIGIN)
        _value = cast(List[float], value)
        return _value

    @SPHRORIGIN.setter
    def SPHRORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRORIGIN, value)

    @property
    def sphrorigin(self) -> List[float]:
        """SPHRORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'sphrorigin' and 'SPHRORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRORIGIN)
        _value = cast(List[float], value)
        return _value

    @sphrorigin.setter
    def sphrorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRORIGIN, value)

    @property
    def SPHRAXISVECT(self) -> List[float]:
        """SPHRAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRAXISVECT)
        _value = cast(List[float], value)
        return _value

    @SPHRAXISVECT.setter
    def SPHRAXISVECT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRAXISVECT, value)

    @property
    def sphraxisvect(self) -> List[float]:
        """SPHRAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'sphraxisvect' and 'SPHRAXISVECT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRAXISVECT)
        _value = cast(List[float], value)
        return _value

    @sphraxisvect.setter
    def sphraxisvect(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRAXISVECT, value)

    @property
    def SPHRAXISENDPOINT1(self) -> List[float]:
        """SPHRAXISENDPOINT1 property
        
        Axis point 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT1)
        _value = cast(List[float], value)
        return _value

    @SPHRAXISENDPOINT1.setter
    def SPHRAXISENDPOINT1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT1, value)

    @property
    def sphraxisendpoint1(self) -> List[float]:
        """SPHRAXISENDPOINT1 property
        
        Axis point 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'sphraxisendpoint1' and 'SPHRAXISENDPOINT1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT1)
        _value = cast(List[float], value)
        return _value

    @sphraxisendpoint1.setter
    def sphraxisendpoint1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT1, value)

    @property
    def SPHRAXISENDPOINT2(self) -> List[float]:
        """SPHRAXISENDPOINT2 property
        
        Axis point 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT2)
        _value = cast(List[float], value)
        return _value

    @SPHRAXISENDPOINT2.setter
    def SPHRAXISENDPOINT2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT2, value)

    @property
    def sphraxisendpoint2(self) -> List[float]:
        """SPHRAXISENDPOINT2 property
        
        Axis point 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'sphraxisendpoint2' and 'SPHRAXISENDPOINT2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT2)
        _value = cast(List[float], value)
        return _value

    @sphraxisendpoint2.setter
    def sphraxisendpoint2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SPHRAXISENDPOINT2, value)

    @property
    def REVOLVEPART(self) -> int:
        """REVOLVEPART property
        
        Revolve part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVOLVEPART)
        _value = cast(int, value)
        return _value

    @REVOLVEPART.setter
    def REVOLVEPART(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REVOLVEPART, value)

    @property
    def revolvepart(self) -> int:
        """REVOLVEPART property
        
        Revolve part id
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [0, inf]
        
        Note: both 'revolvepart' and 'REVOLVEPART' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVOLVEPART)
        _value = cast(int, value)
        return _value

    @revolvepart.setter
    def revolvepart(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.REVOLVEPART, value)

    @property
    def REV1DORIGIN(self) -> List[float]:
        """REV1DORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REV1DORIGIN)
        _value = cast(List[float], value)
        return _value

    @REV1DORIGIN.setter
    def REV1DORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REV1DORIGIN, value)

    @property
    def rev1dorigin(self) -> List[float]:
        """REV1DORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'rev1dorigin' and 'REV1DORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REV1DORIGIN)
        _value = cast(List[float], value)
        return _value

    @rev1dorigin.setter
    def rev1dorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REV1DORIGIN, value)

    @property
    def REV1DAXISVECT(self) -> List[float]:
        """REV1DAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REV1DAXISVECT)
        _value = cast(List[float], value)
        return _value

    @REV1DAXISVECT.setter
    def REV1DAXISVECT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REV1DAXISVECT, value)

    @property
    def rev1daxisvect(self) -> List[float]:
        """REV1DAXISVECT property
        
        Axis vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'rev1daxisvect' and 'REV1DAXISVECT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REV1DAXISVECT)
        _value = cast(List[float], value)
        return _value

    @rev1daxisvect.setter
    def rev1daxisvect(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REV1DAXISVECT, value)

    @property
    def REVTOOLNUMPTS(self) -> float:
        """REVTOOLNUMPTS property
        
        Number of points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVTOOLNUMPTS)
        _value = cast(float, value)
        return _value

    @REVTOOLNUMPTS.setter
    def REVTOOLNUMPTS(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVTOOLNUMPTS, value)

    @property
    def revtoolnumpts(self) -> float:
        """REVTOOLNUMPTS property
        
        Number of points
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'revtoolnumpts' and 'REVTOOLNUMPTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVTOOLNUMPTS)
        _value = cast(float, value)
        return _value

    @revtoolnumpts.setter
    def revtoolnumpts(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVTOOLNUMPTS, value)

    @property
    def REVTOOLORIGIN(self) -> List[float]:
        """REVTOOLORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVTOOLORIGIN)
        _value = cast(List[float], value)
        return _value

    @REVTOOLORIGIN.setter
    def REVTOOLORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REVTOOLORIGIN, value)

    @property
    def revtoolorigin(self) -> List[float]:
        """REVTOOLORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'revtoolorigin' and 'REVTOOLORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVTOOLORIGIN)
        _value = cast(List[float], value)
        return _value

    @revtoolorigin.setter
    def revtoolorigin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REVTOOLORIGIN, value)

    @property
    def REVTOOLAXIS(self) -> List[float]:
        """REVTOOLAXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVTOOLAXIS)
        _value = cast(List[float], value)
        return _value

    @REVTOOLAXIS.setter
    def REVTOOLAXIS(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REVTOOLAXIS, value)

    @property
    def revtoolaxis(self) -> List[float]:
        """REVTOOLAXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'revtoolaxis' and 'REVTOOLAXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVTOOLAXIS)
        _value = cast(List[float], value)
        return _value

    @revtoolaxis.setter
    def revtoolaxis(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.REVTOOLAXIS, value)

    @property
    def REVPOINTRADII1(self) -> float:
        """REVPOINTRADII1 property
        
        Point radii 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII1)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII1.setter
    def REVPOINTRADII1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII1, value)

    @property
    def revpointradii1(self) -> float:
        """REVPOINTRADII1 property
        
        Point radii 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii1' and 'REVPOINTRADII1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII1)
        _value = cast(float, value)
        return _value

    @revpointradii1.setter
    def revpointradii1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII1, value)

    @property
    def REVPOINTRADII2(self) -> float:
        """REVPOINTRADII2 property
        
        Point radii 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII2)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII2.setter
    def REVPOINTRADII2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII2, value)

    @property
    def revpointradii2(self) -> float:
        """REVPOINTRADII2 property
        
        Point radii 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii2' and 'REVPOINTRADII2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII2)
        _value = cast(float, value)
        return _value

    @revpointradii2.setter
    def revpointradii2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII2, value)

    @property
    def REVPOINTRADII3(self) -> float:
        """REVPOINTRADII3 property
        
        Point radii 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII3)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII3.setter
    def REVPOINTRADII3(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII3, value)

    @property
    def revpointradii3(self) -> float:
        """REVPOINTRADII3 property
        
        Point radii 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii3' and 'REVPOINTRADII3' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII3)
        _value = cast(float, value)
        return _value

    @revpointradii3.setter
    def revpointradii3(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII3, value)

    @property
    def REVPOINTRADII4(self) -> float:
        """REVPOINTRADII4 property
        
        Point radii 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII4)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII4.setter
    def REVPOINTRADII4(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII4, value)

    @property
    def revpointradii4(self) -> float:
        """REVPOINTRADII4 property
        
        Point radii 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii4' and 'REVPOINTRADII4' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII4)
        _value = cast(float, value)
        return _value

    @revpointradii4.setter
    def revpointradii4(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII4, value)

    @property
    def REVPOINTRADII5(self) -> float:
        """REVPOINTRADII5 property
        
        Point radii 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII5)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII5.setter
    def REVPOINTRADII5(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII5, value)

    @property
    def revpointradii5(self) -> float:
        """REVPOINTRADII5 property
        
        Point radii 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii5' and 'REVPOINTRADII5' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII5)
        _value = cast(float, value)
        return _value

    @revpointradii5.setter
    def revpointradii5(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII5, value)

    @property
    def REVPOINTRADII6(self) -> float:
        """REVPOINTRADII6 property
        
        Point radii 6
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII6)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII6.setter
    def REVPOINTRADII6(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII6, value)

    @property
    def revpointradii6(self) -> float:
        """REVPOINTRADII6 property
        
        Point radii 6
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii6' and 'REVPOINTRADII6' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII6)
        _value = cast(float, value)
        return _value

    @revpointradii6.setter
    def revpointradii6(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII6, value)

    @property
    def REVPOINTRADII7(self) -> float:
        """REVPOINTRADII7 property
        
        Point radii 7
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII7)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII7.setter
    def REVPOINTRADII7(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII7, value)

    @property
    def revpointradii7(self) -> float:
        """REVPOINTRADII7 property
        
        Point radii 7
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii7' and 'REVPOINTRADII7' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII7)
        _value = cast(float, value)
        return _value

    @revpointradii7.setter
    def revpointradii7(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII7, value)

    @property
    def REVPOINTRADII8(self) -> float:
        """REVPOINTRADII8 property
        
        Point radii 8
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII8)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII8.setter
    def REVPOINTRADII8(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII8, value)

    @property
    def revpointradii8(self) -> float:
        """REVPOINTRADII8 property
        
        Point radii 8
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii8' and 'REVPOINTRADII8' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII8)
        _value = cast(float, value)
        return _value

    @revpointradii8.setter
    def revpointradii8(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII8, value)

    @property
    def REVPOINTRADII9(self) -> float:
        """REVPOINTRADII9 property
        
        Point radii 9
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII9)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII9.setter
    def REVPOINTRADII9(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII9, value)

    @property
    def revpointradii9(self) -> float:
        """REVPOINTRADII9 property
        
        Point radii 9
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii9' and 'REVPOINTRADII9' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII9)
        _value = cast(float, value)
        return _value

    @revpointradii9.setter
    def revpointradii9(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII9, value)

    @property
    def REVPOINTRADII10(self) -> float:
        """REVPOINTRADII10 property
        
        Point radii 10
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII10)
        _value = cast(float, value)
        return _value

    @REVPOINTRADII10.setter
    def REVPOINTRADII10(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII10, value)

    @property
    def revpointradii10(self) -> float:
        """REVPOINTRADII10 property
        
        Point radii 10
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointradii10' and 'REVPOINTRADII10' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTRADII10)
        _value = cast(float, value)
        return _value

    @revpointradii10.setter
    def revpointradii10(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTRADII10, value)

    @property
    def REVPOINTDISTANCE1(self) -> float:
        """REVPOINTDISTANCE1 property
        
        Point distance 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE1)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE1.setter
    def REVPOINTDISTANCE1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE1, value)

    @property
    def revpointdistance1(self) -> float:
        """REVPOINTDISTANCE1 property
        
        Point distance 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance1' and 'REVPOINTDISTANCE1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE1)
        _value = cast(float, value)
        return _value

    @revpointdistance1.setter
    def revpointdistance1(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE1, value)

    @property
    def REVPOINTDISTANCE2(self) -> float:
        """REVPOINTDISTANCE2 property
        
        Point distance 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE2)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE2.setter
    def REVPOINTDISTANCE2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE2, value)

    @property
    def revpointdistance2(self) -> float:
        """REVPOINTDISTANCE2 property
        
        Point distance 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance2' and 'REVPOINTDISTANCE2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE2)
        _value = cast(float, value)
        return _value

    @revpointdistance2.setter
    def revpointdistance2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE2, value)

    @property
    def REVPOINTDISTANCE3(self) -> float:
        """REVPOINTDISTANCE3 property
        
        Point distance 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE3)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE3.setter
    def REVPOINTDISTANCE3(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE3, value)

    @property
    def revpointdistance3(self) -> float:
        """REVPOINTDISTANCE3 property
        
        Point distance 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance3' and 'REVPOINTDISTANCE3' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE3)
        _value = cast(float, value)
        return _value

    @revpointdistance3.setter
    def revpointdistance3(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE3, value)

    @property
    def REVPOINTDISTANCE4(self) -> float:
        """REVPOINTDISTANCE4 property
        
        Point distance 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE4)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE4.setter
    def REVPOINTDISTANCE4(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE4, value)

    @property
    def revpointdistance4(self) -> float:
        """REVPOINTDISTANCE4 property
        
        Point distance 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance4' and 'REVPOINTDISTANCE4' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE4)
        _value = cast(float, value)
        return _value

    @revpointdistance4.setter
    def revpointdistance4(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE4, value)

    @property
    def REVPOINTDISTANCE5(self) -> float:
        """REVPOINTDISTANCE5 property
        
        Point distance 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE5)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE5.setter
    def REVPOINTDISTANCE5(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE5, value)

    @property
    def revpointdistance5(self) -> float:
        """REVPOINTDISTANCE5 property
        
        Point distance 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance5' and 'REVPOINTDISTANCE5' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE5)
        _value = cast(float, value)
        return _value

    @revpointdistance5.setter
    def revpointdistance5(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE5, value)

    @property
    def REVPOINTDISTANCE6(self) -> float:
        """REVPOINTDISTANCE6 property
        
        Point distance 6
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE6)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE6.setter
    def REVPOINTDISTANCE6(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE6, value)

    @property
    def revpointdistance6(self) -> float:
        """REVPOINTDISTANCE6 property
        
        Point distance 6
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance6' and 'REVPOINTDISTANCE6' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE6)
        _value = cast(float, value)
        return _value

    @revpointdistance6.setter
    def revpointdistance6(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE6, value)

    @property
    def REVPOINTDISTANCE7(self) -> float:
        """REVPOINTDISTANCE7 property
        
        Point distance 7
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE7)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE7.setter
    def REVPOINTDISTANCE7(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE7, value)

    @property
    def revpointdistance7(self) -> float:
        """REVPOINTDISTANCE7 property
        
        Point distance 7
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance7' and 'REVPOINTDISTANCE7' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE7)
        _value = cast(float, value)
        return _value

    @revpointdistance7.setter
    def revpointdistance7(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE7, value)

    @property
    def REVPOINTDISTANCE8(self) -> float:
        """REVPOINTDISTANCE8 property
        
        Point distance 8
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE8)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE8.setter
    def REVPOINTDISTANCE8(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE8, value)

    @property
    def revpointdistance8(self) -> float:
        """REVPOINTDISTANCE8 property
        
        Point distance 8
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance8' and 'REVPOINTDISTANCE8' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE8)
        _value = cast(float, value)
        return _value

    @revpointdistance8.setter
    def revpointdistance8(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE8, value)

    @property
    def REVPOINTDISTANCE9(self) -> float:
        """REVPOINTDISTANCE9 property
        
        Point distance 9
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE9)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE9.setter
    def REVPOINTDISTANCE9(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE9, value)

    @property
    def revpointdistance9(self) -> float:
        """REVPOINTDISTANCE9 property
        
        Point distance 9
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance9' and 'REVPOINTDISTANCE9' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE9)
        _value = cast(float, value)
        return _value

    @revpointdistance9.setter
    def revpointdistance9(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE9, value)

    @property
    def REVPOINTDISTANCE10(self) -> float:
        """REVPOINTDISTANCE10 property
        
        Point distance 10
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE10)
        _value = cast(float, value)
        return _value

    @REVPOINTDISTANCE10.setter
    def REVPOINTDISTANCE10(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE10, value)

    @property
    def revpointdistance10(self) -> float:
        """REVPOINTDISTANCE10 property
        
        Point distance 10
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, inf]
        
        Note: both 'revpointdistance10' and 'REVPOINTDISTANCE10' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REVPOINTDISTANCE10)
        _value = cast(float, value)
        return _value

    @revpointdistance10.setter
    def revpointdistance10(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.REVPOINTDISTANCE10, value)

    @property
    def EQUATION(self) -> List[float]:
        """EQUATION property
        
        Equation values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 10 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.EQUATION)
        _value = cast(List[float], value)
        return _value

    @EQUATION.setter
    def EQUATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.EQUATION, value)

    @property
    def equation(self) -> List[float]:
        """EQUATION property
        
        Equation values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 10 element array
        
        Note: both 'equation' and 'EQUATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.EQUATION)
        _value = cast(List[float], value)
        return _value

    @equation.setter
    def equation(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.EQUATION, value)

    @property
    def SLIDERX(self) -> List[float]:
        """SLIDERX property
        
        X extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERX)
        _value = cast(List[float], value)
        return _value

    @SLIDERX.setter
    def SLIDERX(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERX, value)

    @property
    def sliderx(self) -> List[float]:
        """SLIDERX property
        
        X extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'sliderx' and 'SLIDERX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERX)
        _value = cast(List[float], value)
        return _value

    @sliderx.setter
    def sliderx(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERX, value)

    @property
    def SLIDERY(self) -> List[float]:
        """SLIDERY property
        
        Y extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERY)
        _value = cast(List[float], value)
        return _value

    @SLIDERY.setter
    def SLIDERY(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERY, value)

    @property
    def slidery(self) -> List[float]:
        """SLIDERY property
        
        Y extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'slidery' and 'SLIDERY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERY)
        _value = cast(List[float], value)
        return _value

    @slidery.setter
    def slidery(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERY, value)

    @property
    def SLIDERZ(self) -> List[float]:
        """SLIDERZ property
        
        Z extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERZ)
        _value = cast(List[float], value)
        return _value

    @SLIDERZ.setter
    def SLIDERZ(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERZ, value)

    @property
    def sliderz(self) -> List[float]:
        """SLIDERZ property
        
        Z extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'sliderz' and 'SLIDERZ' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERZ)
        _value = cast(List[float], value)
        return _value

    @sliderz.setter
    def sliderz(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERZ, value)

    @property
    def SLIDERRANGEIJK(self) -> List[int]:
        """SLIDERRANGEIJK property
        
        IJK extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERRANGEIJK)
        _value = cast(List[int], value)
        return _value

    @SLIDERRANGEIJK.setter
    def SLIDERRANGEIJK(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERRANGEIJK, value)

    @property
    def sliderrangeijk(self) -> List[int]:
        """SLIDERRANGEIJK property
        
        IJK extents
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        Note: both 'sliderrangeijk' and 'SLIDERRANGEIJK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERRANGEIJK)
        _value = cast(List[int], value)
        return _value

    @sliderrangeijk.setter
    def sliderrangeijk(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERRANGEIJK, value)

    @property
    def SLIDERSTEP(self) -> float:
        """SLIDERSTEP property
        
        Slider step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERSTEP)
        _value = cast(float, value)
        return _value

    @SLIDERSTEP.setter
    def SLIDERSTEP(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERSTEP, value)

    @property
    def sliderstep(self) -> float:
        """SLIDERSTEP property
        
        Slider step
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'sliderstep' and 'SLIDERSTEP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERSTEP)
        _value = cast(float, value)
        return _value

    @sliderstep.setter
    def sliderstep(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERSTEP, value)

    @property
    def SLIDERSTEPIJK(self) -> int:
        """SLIDERSTEPIJK property
        
        Slider step ijk
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERSTEPIJK)
        _value = cast(int, value)
        return _value

    @SLIDERSTEPIJK.setter
    def SLIDERSTEPIJK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERSTEPIJK, value)

    @property
    def sliderstepijk(self) -> int:
        """SLIDERSTEPIJK property
        
        Slider step ijk
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'sliderstepijk' and 'SLIDERSTEPIJK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIDERSTEPIJK)
        _value = cast(int, value)
        return _value

    @sliderstepijk.setter
    def sliderstepijk(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIDERSTEPIJK, value)

    @property
    def MESHPLANE(self) -> int:
        """MESHPLANE property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICEI - I
            * ensight.objs.enums.MESH_SLICEJ - J
            * ensight.objs.enums.MESH_SLICEK - K
            * ensight.objs.enums.MESH_SLICE_X - X
            * ensight.objs.enums.MESH_SLICE_Y - Y
            * ensight.objs.enums.MESH_SLICE_Z - Z
            * ensight.objs.enums.MESH_SLICE_RTZ_R - R
            * ensight.objs.enums.MESH_SLICE_RTZ_T - T
            * ensight.objs.enums.MESH_SLICE_RTZ_Z - Z
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANE)
        _value = cast(int, value)
        return _value

    @MESHPLANE.setter
    def MESHPLANE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANE, value)

    @property
    def meshplane(self) -> int:
        """MESHPLANE property
        
        Which slice
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MESH_SLICEI - I
            * ensight.objs.enums.MESH_SLICEJ - J
            * ensight.objs.enums.MESH_SLICEK - K
            * ensight.objs.enums.MESH_SLICE_X - X
            * ensight.objs.enums.MESH_SLICE_Y - Y
            * ensight.objs.enums.MESH_SLICE_Z - Z
            * ensight.objs.enums.MESH_SLICE_RTZ_R - R
            * ensight.objs.enums.MESH_SLICE_RTZ_T - T
            * ensight.objs.enums.MESH_SLICE_RTZ_Z - Z
        
        Note: both 'meshplane' and 'MESHPLANE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MESHPLANE)
        _value = cast(int, value)
        return _value

    @meshplane.setter
    def meshplane(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MESHPLANE, value)

    @property
    def VALUE(self) -> float:
        """VALUE property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUE)
        _value = cast(float, value)
        return _value

    @VALUE.setter
    def VALUE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUE, value)

    @property
    def value(self) -> float:
        """VALUE property
        
        Value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'value' and 'VALUE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VALUE)
        _value = cast(float, value)
        return _value

    @value.setter
    def value(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VALUE, value)

    @property
    def ORIGIN(self) -> List[float]:
        """ORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN)
        _value = cast(List[float], value)
        return _value

    @ORIGIN.setter
    def ORIGIN(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN, value)

    @property
    def origin(self) -> List[float]:
        """ORIGIN property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'origin' and 'ORIGIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGIN)
        _value = cast(List[float], value)
        return _value

    @origin.setter
    def origin(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGIN, value)

    @property
    def AXIS(self) -> List[float]:
        """AXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS)
        _value = cast(List[float], value)
        return _value

    @AXIS.setter
    def AXIS(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS, value)

    @property
    def axis(self) -> List[float]:
        """AXIS property
        
        Axis
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'axis' and 'AXIS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXIS)
        _value = cast(List[float], value)
        return _value

    @axis.setter
    def axis(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXIS, value)

    @property
    def ENDPOINT(self) -> List[float]:
        """ENDPOINT property
        
        End point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENDPOINT)
        _value = cast(List[float], value)
        return _value

    @ENDPOINT.setter
    def ENDPOINT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ENDPOINT, value)

    @property
    def endpoint(self) -> List[float]:
        """ENDPOINT property
        
        End point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'endpoint' and 'ENDPOINT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENDPOINT)
        _value = cast(List[float], value)
        return _value

    @endpoint.setter
    def endpoint(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ENDPOINT, value)

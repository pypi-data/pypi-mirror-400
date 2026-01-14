"""ens_globals module

The ens_globals module provides a proxy interface to EnSight ENS_GLOBALS instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_VPORT, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_GLOBALS(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_GLOBALS

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

    def setchildattrs(self, *args, **kwargs) -> Any:
        """Set attributes on children list

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

    def create_jlc(self, *args, **kwargs) -> Any:
        """Add a new launch configuration

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.create_jlc({arg_string})"
        return self._session.cmd(cmd)

    def selection(self, *args, **kwargs) -> Any:
        """Access the EnSight selection objects::
        
            ENS_GLOBALS.selection(name: str = None, type: Type[ENSOBJ] = None) -> ENS_GROUP
        
        
        Returns an ENS_GROUP object representing the current selection in EnSight.
        The method supports two keyword: 'name' and 'type'.  Only one of these
        can set specified.  They specify which selection ENS_GROUP to return.
        If no keyword is specified, name='ENS_PART' is the default.
        
        
        Args:
            name:
                This keyword can be 'ENS_PART', 'ENS_VAR', 'ENS_ANNOT' to select a specific class.
            type:
                This keyword can be ensight.objs.ENS_PART, ensight.objs.ENS_VAR, ensight.objs.ENS_ANNOT.
        
        
        Returns:
            An :class:`ENS_GROUP<pyensight.ens_group.ENS_GROUP>` instance.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.selection({arg_string})"
        return self._session.cmd(cmd)

    def pick_operation(self, *args, **kwargs) -> Any:
        """Perform pick operation

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.pick_operation({arg_string})"
        return self._session.cmd(cmd)

    def get_units(self, obj: Union["ENS_VAR", str], format: int = 0, utf8: int = 0,            prefix: str = "", suffix: str = "") -> Union[str, bytes]:
        """Generate a string that represents the appropriate label for a given object.
        
        
        This method will look at the specified :class:`ENS_VAR <pyensight.ensobj.ENS_VAR>` object
        and get any unit information specified by the UNIT schema.  The API can generate labels from DIMS
        and SYSTEM values if no explicit label string has been specified for the variable object.
        It will then return a string with the specified prefix and suffix strings added before
        the units and after the unit string. It is also legal to pass a dimensions string
        instead of a variable object.  For example :samp:`ensight.objs.core.get_units("L/TT")`.
        
        The format and utf8 keywords control the specific format of the string.
        The format can be: 0=raw, 1=Unicode or 2=EnSight annotation string.  If Unicode is
        selected, the string will be in unicode unless utf8=2 is specified, in which case
        an UTF8 encoded bytes object will be returned.
        
        
        Args:
            obj:
                A variable/part object or a string representing units by dimensional specification.  For
                example, "L/TT" (length/time*time) for acceleration.
            format:
                The specific string format.  0=simple raw ASCII, 1=Unicode string, 2=EnSight annotation.
            utf8:
                By default, the returned string is in Unicode.  If set to 2, a bytes object of the
                UTF8 representation is returned.
            prefix:
                A string used to prefix the unit string.
            suffix:
                A string used to suffix the unit string.
        
        Returns:
            A string or bytes array.
        
        
        Example:
            ::
        
                # For an ENS_VAR ('var') with the ENS_UNITS_LABEL and version 2.0 of the schema specified
                ensight.objs.core.get_units(var)
                'm^2 s^-2'
        
                ensight.objs.core.get_units(var, format=1)
                'm²/s²'
        
                ensight.objs.core.get_units(var, format=1, utf8=2)
                b'kg/m\\xc2\\xb3'
        
        
        See also:
            `EnSight units <https://nexusdemo.ensight.com/docs/python/html/Python.html?ENS_UNITSSchema.html>`_

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(obj.__repr__())
        arg_list.append(f"format={format.__repr__()}")
        arg_list.append(f"utf8={utf8.__repr__()}")
        arg_list.append(f"prefix={prefix.__repr__()}")
        arg_list.append(f"suffix={suffix.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_units({arg_string})"
        return self._session.cmd(cmd)

    def get_unit_dimensions(self, obj: "ENS_VAR", normalized: bool = False) -> str:
        """This method will return the units dimension string for a given variable object.
        
        
        The dimension string is a collection of characters that represent fundamental quantities, mass,
        length, time, etc.  The string repeats a character if the quantity is of another order (e.g.
        volume would be "LL") and quantities with a negative exponent, will appear after a '/'
        character.  These quantity characters include:
        
        ========== ======================
        Character  Quantity (SI value)
        ========== ======================
        M          Mass (Kilogram)
        L          Length (Meter)
        I          Intensity (Candela)
        D          Angle (Radian)
        K          Temperature (Kelvin)
        Q          Current (Ampere)
        T          Time (Second)
        A          Substance amount (Mol)
        ========== ======================
        
        
        If there is a variable 'v' that is velocity,
        the call :samp:`ensight.object.core.get_unit_dimensions(v)` will return the
        dimension string: "L/T".
        
        
        Args:
            obj:
                An ENS_VAR object instance.
            normalized:
                If normalized is set to True, the form of the dimension string will be standardized.
                For example:  'LT/TT' would be converted to 'L/T' and the ordering of the dimension
                characters will be sorted to a standard order (MLIDKQTA).  This allows for the direct
                comparison of variable unit dimensions.
        
        
        Returns:
            A string describing the dimensionality of the variable.
        
        
        See also:
            `EnSight units <https://nexusdemo.ensight.com/docs/python/html/Python.html?ENS_UNITSSchema.html>`_

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(obj.__repr__())
        arg_list.append(f"normalized={normalized.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_unit_dimensions({arg_string})"
        return self._session.cmd(cmd)

    def get_unit_conversion(self, from_system: str, to_system: str,            dimensionality: str) -> Tuple[float, float]:
        """Return the linear conversion parameters for converting a variable from one unit system to
        another.
        
        
        This method will return the M and B linear equation parameters for the equation:
        :samp:`y = Mx + b` that can be used to convert an entity of the dimensionality specified by
        dimension_string (e.g. L/TT) from the first unit system to the second (e.g. "SI" to "BIN").
        If the conversion fails, this function will raise an exception.  Otherwise,  it returns a
        tuple of two floats.  The list of valid unit systems can be obtained using:
        :samp:`ensight.objs.core.unit_system()`.
        
        
        Args:
            from_system:
                The unit system to convert from.
            to_system:
                The unit system to convert to.
            dimensionality:
                The unit quantity dimension string to convert.
                See: :meth:`pyensight.ens_globals.ENS_GLOBALS.get_unit_dimensions`
        
        
        Returns:
            A string describing the dimensionality of the variable.
        
        
        Examples:
            ::
        
                # An example use case for a volume variable from the current unit system to BFT might be:
                var_dims = ensight.objs.core.get_unit_dimensions(ensight.objs.core.VARIABLES['EleSize'][0])
                unit_system = ensight.objs.core.unit_system()[0]
                print(ensight.objs.core.get_unit_conversion(unit_system, "BFT", var_dims))
        
                # Outputs:
                (35.31466672148858, 0.0)
        
        
        See also:
            `EnSight units <https://nexusdemo.ensight.com/docs/python/html/Python.html?ENS_UNITSSchema.html>`_

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(from_system.__repr__())
        arg_list.append(to_system.__repr__())
        arg_list.append(dimensionality.__repr__())
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.get_unit_conversion({arg_string})"
        return self._session.cmd(cmd)

    def unit_system(self, name: Optional[str] = None, silent: int = 1, enumerate: int = -1,            record: int = 0) -> Tuple[str, str, bool, dict]:
        """Get/set the current unit system to the named value (see ENS_UNITS_SYSTEM).
        
        
        With no arguments, this method simply returns a tuple:
        :samp:`('unit system string', 'unit system name', True if this is the session unit system,
        a dictionary of the unit labels)`.  If a units system name is passed as 'name',
        the method will attempt to set the current unit system. In this case, 'name' should
        be set to the simple string name of the unit system (e.g. 'SI').  If the unit system
        has been locked (e.g. a dataset has been loaded), the method will throw an
        exception unless 'silent=1' (the default) has been specified. If 'record' is non-zero
        and the unit system was changed, the change will be recorded in command language.
        If enumerate is set to a number greater than -1, it will walk the list of known
        unit systems.  When the end of the list is reached, an exception will be thrown.
        
        
        Args:
            name:
                The name of a unit system, optional.
            silent:
                If non-zero suppress exceptions.
            enumerate:
                If 0 or greater, return details of the 'n-th' unit system.
            record:
                If non-zero, any operation that changes the unit system will be recorded to
                command language.
        
        Returns:
            A tuple describing the selected unit system
        
        
        Example:
            ::
        
                # The following snippet will dump the unit system table in EnSight.
                idx = 0
                while True:
                    try:
                        print(ensight.objs.core.unit_system(enumerate=idx))
                    except:
                        break
                    idx += 1
        
                # Outputs:
                ('USER', 'User defined units', False, {'A': '', 'D': '', 'I': '', 'K': '', 'M': '', 'L': '', 'Q': '', 'T': ''})
                ('SI', 'Metric SI', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'K', 'M': 'kg', 'L': 'm', 'Q': 'A', 'T': 's'})
                ('CGS', 'Metric CGS', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'g', 'L': 'cm', 'Q': 'A', 'T': 's'})
                ('BFT', 'US ft Consistent', False, {'A': 'slugmol', 'D': 'rad', 'I': 'cd', 'K': 'F', 'M': 'slug', 'L': 'ft', 'Q': 'A', 'T': 's'})
                ('BIN', 'US in Consistent', False, {'A': 'lbmmol', 'D': 'rad', 'I': 'cd', 'K': 'F', 'M': 'slinch', 'L': 'in', 'Q': 'A', 'T': 's'})
                ('MKS', 'Metric MKS', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'kg', 'L': 'm', 'Q': 'A', 'T': 's'})
                ('MPA', 'Metric MPA', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'tonne', 'L': 'mm', 'Q': 'mA', 'T': 's'})
                ('uMKS', 'Metric uMKS', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'kg', 'L': 'um', 'Q': 'pA', 'T': 's'})
                ('CGSK', 'Metric CGSK', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'K', 'M': 'g', 'L': 'cm', 'Q': 'A', 'T': 's'})
                ('NMM', 'Metric NMM', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'kg', 'L': 'mm', 'Q': 'mA', 'T': 's'})
                ('uMKSS', 'Metric uMKSS', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'kg', 'L': 'um', 'Q': 'mA', 'T': 's'})
                ('NMMDAT', 'Metric NMMDAT', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'decatonne', 'L': 'mm', 'Q': 'mA', 'T': 's'})
                ('NMMTON', 'Metric NMMTON', False, {'A': 'mol', 'D': 'rad', 'I': 'cd', 'K': 'C', 'M': 'tonne', 'L': 'mm', 'Q': 'mA', 'T': 's'})
                ('BFTS', 'US ft', False, {'A': 'lbmmol', 'D': 'rad', 'I': 'cd', 'K': 'F', 'M': 'lbm', 'L': 'ft', 'Q': 'A', 'T': 's'})
                ('BINS', 'US in', False, {'A': 'lbmmol', 'D': 'rad', 'I': 'cd', 'K': 'F', 'M': 'lbm', 'L': 'in', 'Q': 'A', 'T': 's'})
                ('USENG', 'US Engineering', False, {'A': 'lbmmol', 'D': 'rad', 'I': 'cd', 'K': 'R', 'M': 'lb', 'L': 'in', 'Q': 'A', 'T': 's'})
                ('Unknown', 'From first loaded case', False, {'A': '', 'D': '', 'I': '', 'K': '', 'M': '', 'L': '', 'Q': '', 'T': ''})
        
        
        See also:
            `EnSight units <https://nexusdemo.ensight.com/docs/python/html/Python.html?ENS_UNITSSchema.html>`_

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(f"name={name.__repr__()}")
        arg_list.append(f"silent={silent.__repr__()}")
        arg_list.append(f"enumerate={enumerate.__repr__()}")
        arg_list.append(f"record={record.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.unit_system({arg_string})"
        return self._session.cmd(cmd)

    def alloc_userdef_attr(self, *args, **kwargs) -> Any:
        """Allocate a user-defined attribute

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.alloc_userdef_attr({arg_string})"
        return self._session.cmd(cmd)

    def find_objs(self, list: Union["ENS_GROUP", list] = [], filter: Optional[dict] = None,            group: int = 0, recurse: int = 0, depth: int = -1,            types: Optional[list] = None) -> Union["ENS_GROUP", list]:
        """Search an object (tree) for objects that match a specific criteria.
        
        
        This method walks an array of objects or an ENS_GROUP rooted object tree, looking for
        objects that meet the specified filters. The object tree to be searched is passed via
        'list', which can be a Python list or a ENS_GROUP subclass. The method will walk all
        of the objects in the list and all the children in the groups.
        
        Once the algorithm finds an object, it will apply filter. The first filter is the
        'types' list. This specifies a list of allowable type objects (e.g. ensight.objs.ENS_PART).
        Only objects of the types in the list are returned. Second, is the 'filter' dictionary.
        This is a dictionary keyed by attribute enums. The algorithm gets the attribute value
        for the specified enum (if the enum does not exist, the object is not selected) and
        compares it to the value of the key in the dictionary. If the value comparisons fail, the
        object is not selected. Note: the algorithm uses the cmp() method on the values in the
        dictionary to make the comparison. Thus, comparisons other than equality can be
        implemented using objects with custom cmp() methods.
        
        By default, the routine returns a Python list of objects, but group=1 can be specified to
        return a user selection group object containing the objects that would be in the list. The
        group option makes it easy to change attributes in bulk on the objects. It also makes it
        possible to access a 'ensobjlist' interface (group.CHILDREN is an 'ensobjlist' instance)
        which includes a useful 'find()' method as well. The depth option controls the depth to
        which the method is allowed to recurse. A value of -1 puts no limits on the recursion.
        
        
        Args:
            list:
                A list of objects or an ENS_GROUP instance.
            filter:
                A dictionary created by ENSOBJ attributes as key and example attribute values as the
                dictionary values.  For example, :samp:`filter=dict(VISIBLE=True)` will select only objects
                that have a VISIBLE attribute with the value True.  If no dictionary is provided, the
                filter check is not applied.
            group:
                By default, return a list of matching objects.  If group is set to 1, return an ENS_GROUP
                instance instead.  This can be useful for chaining operations, but it is not functional
                in the pyensight interface.
            recurse:
                By default, only the objects in 'list' (or the children of an ENS_GROUP) are checked.
                If recurse is set to 1, all objects supporting the CHILDREN attribute will be recursively
                checked as well.
            depth:
                This can be used to limit the depth of recursion (if recurse is set to 1).  The default
                value (-1) will not limit recursion at all.  Otherwise, the maximum depth of the search
                is limited to the value of this keyword.
            types:
                This is set to a list of class objects that the search is limited to.  If unset, all
                classes are allowed.
        
        
        Returns:
            A list or ENS_GROUP object of the matched objects.
        
        
        
        The find_objs() method can be used in a large number of ways. Some common examples are
        illustrated here. Note also that: ensight.objs.core.find_objs(...,group=1).CHILDREN will
        return an ensobjlist containing the objects returned by find_objs().
        
        
        Examples:
            ::
        
                # find all PART objects in the current case
                l = ensight.objs.core.find_objs(ensight.objs.core.CURRENTCASE,
                                                types=[ensight.objs.ENS_PART], recurse=1)
        
        
                # find all non VISIBLE parts as a group object
                g = ensight.objs.core.find_objs(core.PARTS,
                                                filter={ensight.objs.enums.VISIBLE: False}, group=1)
                # and make them all visible
                g.setchildattr(ensight.objs.enums.VISIBLE, True)
        
                # find all the VISIBLE, CLIP parts currently selected
                d = {ensight.objs.enums.VISIBLE: True, ensight.objs.enums.PARTTYPE: ensight.PART_CLIP_PLANE}
                l = ensight.objs.core.find_objs(ensight.objs.core.selection(), filter=d)
        
                # define a class with a custom __cmp__ method
                class strstr():
                    def __init__(self, value):
                        self._v = value
        
                    def __cmp__(self, other):
                        if other.find(self._v) >= 0:
                            return 0
                        return 1
        
                    def __eq__(self, other):
                        return other.find(self._v) >= 0
        
                    def __ne__(self, other):
                        return other.find(self._v) < 0
        
                    def __lt__(self, other):
                        return False
        
                    def __gt__(self, other):
                        return False
        
                    def __le__(self, other):
                        return other.find(self._v) >= 0
        
                    def __ge__(self, other):
                        return other.find(self._v) >= 0
        
                # find all parts in the current case that have "Block" in their DESCRIPTION
                # find_objs() will only use the __eq__() method, the others are there for completeness
                d = {ensight.objs.enums.DESCRIPTION: strstr("Block")}
                l = ensight.objs.core.find_objs(ensight.objs.core.CURRENTCASE, filter=d,
                                                types=[ensight.objs.ENS_PART], recurse=1)
        
                # define a pure comparison case to see if a variable is valid for a case
                class casevar():
                    def __cmp__(self, other):
                        if other[ensight.objs.core.CURRENTCASE[0].CASENUMBER]:
                            return 0
                        return 1
        
                    def __eq__(self, other):
                        return other[ensight.objs.core.CURRENTCASE[0].CASENUMBER]
        
                    def __ne__(self, other):
                        return not other[ensight.objs.core.CURRENTCASE[0].CASENUMBER]
        
                    def __lt__(self, other):
                        return False
        
                    def __gt__(self, other):
                        return False
        
                    def __le__(self, other):
                        return other[ensight.objs.core.CURRENTCASE[0].CASENUMBER]
        
                    def __ge__(self, other):
                        return other[ensight.objs.core.CURRENTCASE[0].CASENUMBER]
        
        
                # find active, scalar variables defined for the current case
                d = {ensight.objs.enums.EXIST_CASE: casevar(), ensight.objs.enums.ACTIVE: 1,
                     ensight.objs.enums.VARTYPE: ensight.objs.enums.ENS_VAR_SCALAR}
                g = ensight.objs.core.find_objs(ensight.objs.core.VARIABLES, filter=d)
        
                # Define a class that defines __cmp__ to be the "find" operation on a list
                class multival():
                    def __init__(self,lst):
                        self._list = lst
        
                    def __cmp__(self,other):
                        if self._list.count(other):
                            return 0
                        return 1
        
                    def __eq__(self, other):
                        return self._list.count(other) > 0
        
                    def __ne__(self, other):
                        return self._list.count(other) <= 0
        
                    def __gt__(self, other):
                        return False
        
                    def __lt__(self, other):
                        return False
        
                    def __ge__(self, other):
                        return self._list.count(other) > 0
        
                    def __le__(self, other):
                        return self._list.count(other) > 0
        
                # use it to find the parts with descriptions that are in a list
                f = {ensight.objs.enums.DESCRIPTION: multival(["engine","windshields"])}
                parts = ensight.objs.core.find_objs(ensight.objs.core.PARTS, filter=f)

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(f"list={list.__repr__()}")
        if filter is not None:
            arg_list.append(f"filter={filter.__repr__()}")
        arg_list.append(f"group={group.__repr__()}")
        arg_list.append(f"recurse={recurse.__repr__()}")
        arg_list.append(f"depth={depth.__repr__()}")
        if (types is not None) and group:
            raise RuntimeError("PyEnSight does not support returning ENS_GROUP objects when the types keyword is specified.")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.find_objs({arg_string})"
        ret = self._session.cmd(cmd)
        if types is not None:
            temp = []
            for obj in ret:
                for target_class in types:
                    if issubclass(type(obj), target_class):
                        temp.append(obj)
            ret = temp
        return ret

    def path_cache(self, *args, **kwargs) -> Any:
        """Cache indexed paths for shared defaults

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.path_cache({arg_string})"
        return self._session.cmd(cmd)

    def add_case(self, *args, **kwargs) -> Any:
        """Add a new case

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_case({arg_string})"
        return self._session.cmd(cmd)

    def create_variable(self, name: str, value: str, sources: Optional[List["ENS_PART"]] = None,            private: int = 0) -> "ENS_VAR":
        """This method creates a new EnSight variable.
        
        
        It creates a variable with the provided name, using the calculator expression
        supplied by the value. If the expression requires a partlist, this
        is supplied using the 'sources' keyword (the default is the current part selection).
        
        Args:
            name:
                The name of the variable to create.
            value:
                The expression to evaluate as the new variable.  See also: :doc:`Calculator Functions <../calc_functions>`.
            sources:
                A list of parts to create the variable with. This can be specified as an ENS_GROUP object, or a list of part names/ids/objects.
            private:
                If the private=1 keyword is set, the variable will be marked as "hidden" and will not show up in some part lists (e.g. in popup dialogs).
        
        
        Returns:
            An :class:`ENS_VAR<pyensight.ens_var.ENS_VAR>` instance.
        
        
        Example:
            ::
        
                var = session.ensight.objs.core.create_variable("EleSize", "EleSize(plist)", sources=session.ensight.objs.core.PARTS)

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(name.__repr__())
        arg_list.append(value.__repr__())
        arg_list.append(f"sources={sources.__repr__()}")
        arg_list.append(f"private={private.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.create_variable({arg_string})"
        return self._session.cmd(cmd)

    def anim_control(self, *args, **kwargs) -> Any:
        """Control animation playback

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.anim_control({arg_string})"
        return self._session.cmd(cmd)

    def idle_anim(self, *args, **kwargs) -> Any:
        """Query or set internal animations

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.idle_anim({arg_string})"
        return self._session.cmd(cmd)

    def default_parent(self, *args, **kwargs) -> Any:
        """Set the default parent for part creation by partype

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.default_parent({arg_string})"
        return self._session.cmd(cmd)

    def region_tool(self, *args, **kwargs) -> Any:
        """Interaction with the region tool

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.region_tool({arg_string})"
        return self._session.cmd(cmd)

    def add_docs_path(self, *args, **kwargs) -> Any:
        """Add a directory to check for i18n docs

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.add_docs_path({arg_string})"
        return self._session.cmd(cmd)

    def ensmodel_updates_suspend(self, *args, **kwargs) -> Any:
        """Suspend EnsModel event processing

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.ensmodel_updates_suspend({arg_string})"
        return self._session.cmd(cmd)

    def ensmodel_updates_resume(self, *args, **kwargs) -> Any:
        """Resume EnsModel event processing

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.ensmodel_updates_resume({arg_string})"
        return self._session.cmd(cmd)

    def generate_uuid(self, ) -> str:
        """Generate a new UUID.
        
        
        This method will generate and return a new GUID.
        
        
        Returns:
            A UUID string.
        
        
        Examples:
            ::
        
                ensight.objs.core.generate_uuid()
                'e8f00942-c733-11ed-a3ec-ebb53f2a5203'

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.generate_uuid({arg_string})"
        return self._session.cmd(cmd)

    def recordselected(self, *args, **kwargs) -> Any:
        """Record selected objects

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.recordselected({arg_string})"
        return self._session.cmd(cmd)

    def mouseactionset(self, *args, **kwargs) -> Any:
        """Set a mouse button combination to a graphics window action for single click or drag.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.mouseactionset({arg_string})"
        return self._session.cmd(cmd)

    def mouseactionget(self, *args, **kwargs) -> Any:
        """Get a mouse button combination's graphics window action for single click or drag.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.mouseactionget({arg_string})"
        return self._session.cmd(cmd)

    def global_datapathhistory(self, *args, **kwargs) -> Any:
        """Get data reader path history cache.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.global_datapathhistory({arg_string})"
        return self._session.cmd(cmd)

    def global_datapathhistory_add(self, *args, **kwargs) -> Any:
        """Add to data reader path history cache.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.global_datapathhistory_add({arg_string})"
        return self._session.cmd(cmd)

    def querydatareadermapinfo(self, *args, **kwargs) -> Any:
        """Get data reader info provided by the mapping file (i.e., ensight_reader_extension.map)

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.querydatareadermapinfo({arg_string})"
        return self._session.cmd(cmd)

    def calculator_function_units_info(self, *args, **kwargs) -> Any:
        """Get information about the unit transformations for calculator functions.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.calculator_function_units_info({arg_string})"
        return self._session.cmd(cmd)

    def post_event(self, *args, **kwargs) -> Any:
        """Post synthetic GUI events.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.post_event({arg_string})"
        return self._session.cmd(cmd)

    def grpc_server(self, *args, **kwargs) -> Any:
        """Control the gRPC server.

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.grpc_server({arg_string})"
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
    def CASES(self) -> ensobjlist['ENS_CASE']:
        """CASES property
        
        cases
        
        Supported operations:
            getattr
        Datatype:
            Object, 32 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CASES)
        _value = cast(ensobjlist['ENS_CASE'], value)
        return _value

    @property
    def cases(self) -> ensobjlist['ENS_CASE']:
        """CASES property
        
        cases
        
        Supported operations:
            getattr
        Datatype:
            Object, 32 element array
        
        Note: both 'cases' and 'CASES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CASES)
        _value = cast(ensobjlist['ENS_CASE'], value)
        return _value

    @property
    def VARIABLES(self) -> ensobjlist['ENS_VAR']:
        """VARIABLES property
        
        variables
        
        Supported operations:
            getattr
        Datatype:
            Object, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLES)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @property
    def variables(self) -> ensobjlist['ENS_VAR']:
        """VARIABLES property
        
        variables
        
        Supported operations:
            getattr
        Datatype:
            Object, 2 element array
        
        Note: both 'variables' and 'VARIABLES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLES)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @property
    def VARIABLETREE(self) -> ensobjlist['ENS_GROUP']:
        """VARIABLETREE property
        
        variable tree root
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLETREE)
        _value = cast(ensobjlist['ENS_GROUP'], value)
        return _value

    @property
    def variabletree(self) -> ensobjlist['ENS_GROUP']:
        """VARIABLETREE property
        
        variable tree root
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'variabletree' and 'VARIABLETREE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VARIABLETREE)
        _value = cast(ensobjlist['ENS_GROUP'], value)
        return _value

    @property
    def GROUPS(self) -> ensobjlist['ENS_GROUP']:
        """GROUPS property
        
        groups
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUPS)
        _value = cast(ensobjlist['ENS_GROUP'], value)
        return _value

    @property
    def groups(self) -> ensobjlist['ENS_GROUP']:
        """GROUPS property
        
        groups
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'groups' and 'GROUPS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GROUPS)
        _value = cast(ensobjlist['ENS_GROUP'], value)
        return _value

    @property
    def SPECIES(self) -> ensobjlist:
        """SPECIES property
        
        species
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SPECIES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def species(self) -> ensobjlist:
        """SPECIES property
        
        species
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'species' and 'SPECIES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SPECIES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def MATERIALS(self) -> ensobjlist:
        """MATERIALS property
        
        materials
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MATERIALS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def materials(self) -> ensobjlist:
        """MATERIALS property
        
        materials
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'materials' and 'MATERIALS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MATERIALS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def PARTS(self) -> ensobjlist['ENS_PART']:
        """PARTS property
        
        parts
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def parts(self) -> ensobjlist['ENS_PART']:
        """PARTS property
        
        parts
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'parts' and 'PARTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def TEXTURES(self) -> ensobjlist['ENS_TEXTURE']:
        """TEXTURES property
        
        textures
        
        Supported operations:
            getattr
        Datatype:
            Object, 32 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURES)
        _value = cast(ensobjlist['ENS_TEXTURE'], value)
        return _value

    @property
    def textures(self) -> ensobjlist['ENS_TEXTURE']:
        """TEXTURES property
        
        textures
        
        Supported operations:
            getattr
        Datatype:
            Object, 32 element array
        
        Note: both 'textures' and 'TEXTURES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TEXTURES)
        _value = cast(ensobjlist['ENS_TEXTURE'], value)
        return _value

    @property
    def TOOLS(self) -> ensobjlist['ENS_TOOL']:
        """TOOLS property
        
        tools
        
        Supported operations:
            getattr
        Datatype:
            Object, 8 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TOOLS)
        _value = cast(ensobjlist['ENS_TOOL'], value)
        return _value

    @property
    def tools(self) -> ensobjlist['ENS_TOOL']:
        """TOOLS property
        
        tools
        
        Supported operations:
            getattr
        Datatype:
            Object, 8 element array
        
        Note: both 'tools' and 'TOOLS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TOOLS)
        _value = cast(ensobjlist['ENS_TOOL'], value)
        return _value

    @property
    def ANNOTS(self) -> ensobjlist['ENS_ANNOT']:
        """ANNOTS property
        
        annots
        
        Supported operations:
            getattr
        Datatype:
            Object, 5 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTS)
        _value = cast(ensobjlist['ENS_ANNOT'], value)
        return _value

    @property
    def annots(self) -> ensobjlist['ENS_ANNOT']:
        """ANNOTS property
        
        annots
        
        Supported operations:
            getattr
        Datatype:
            Object, 5 element array
        
        Note: both 'annots' and 'ANNOTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANNOTS)
        _value = cast(ensobjlist['ENS_ANNOT'], value)
        return _value

    @property
    def VPORTS(self) -> ensobjlist['ENS_VPORT']:
        """VPORTS property
        
        viewports
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VPORTS)
        _value = cast(ensobjlist['ENS_VPORT'], value)
        return _value

    @property
    def vports(self) -> ensobjlist['ENS_VPORT']:
        """VPORTS property
        
        viewports
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'vports' and 'VPORTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VPORTS)
        _value = cast(ensobjlist['ENS_VPORT'], value)
        return _value

    @property
    def GEOMS(self) -> ensobjlist:
        """GEOMS property
        
        geoms
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GEOMS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def geoms(self) -> ensobjlist:
        """GEOMS property
        
        geoms
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'geoms' and 'GEOMS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GEOMS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def CURRENTCASE(self) -> ensobjlist['ENS_CASE']:
        """CURRENTCASE property
        
        current case
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENTCASE)
        _value = cast(ensobjlist['ENS_CASE'], value)
        return _value

    @property
    def currentcase(self) -> ensobjlist['ENS_CASE']:
        """CURRENTCASE property
        
        current case
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'currentcase' and 'CURRENTCASE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENTCASE)
        _value = cast(ensobjlist['ENS_CASE'], value)
        return _value

    @property
    def DEFAULTPARTS(self) -> ensobjlist['ENS_PART']:
        """DEFAULTPARTS property
        
        default parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 28 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTPARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def defaultparts(self) -> ensobjlist['ENS_PART']:
        """DEFAULTPARTS property
        
        default parts
        
        Supported operations:
            getattr
        Datatype:
            Object, 28 element array
        
        Note: both 'defaultparts' and 'DEFAULTPARTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTPARTS)
        _value = cast(ensobjlist['ENS_PART'], value)
        return _value

    @property
    def DEFAULTANNOTS(self) -> ensobjlist['ENS_ANNOT']:
        """DEFAULTANNOTS property
        
        default annotations
        
        Supported operations:
            getattr
        Datatype:
            Object, 9 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTANNOTS)
        _value = cast(ensobjlist['ENS_ANNOT'], value)
        return _value

    @property
    def defaultannots(self) -> ensobjlist['ENS_ANNOT']:
        """DEFAULTANNOTS property
        
        default annotations
        
        Supported operations:
            getattr
        Datatype:
            Object, 9 element array
        
        Note: both 'defaultannots' and 'DEFAULTANNOTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTANNOTS)
        _value = cast(ensobjlist['ENS_ANNOT'], value)
        return _value

    @property
    def DEFAULTPLOT(self) -> ensobjlist['ENS_PLOTTER']:
        """DEFAULTPLOT property
        
        default plotter
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTPLOT)
        _value = cast(ensobjlist['ENS_PLOTTER'], value)
        return _value

    @property
    def defaultplot(self) -> ensobjlist['ENS_PLOTTER']:
        """DEFAULTPLOT property
        
        default plotter
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'defaultplot' and 'DEFAULTPLOT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTPLOT)
        _value = cast(ensobjlist['ENS_PLOTTER'], value)
        return _value

    @property
    def DEFAULTPOLYLINE(self) -> ensobjlist['ENS_POLYLINE']:
        """DEFAULTPOLYLINE property
        
        default polyline
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTPOLYLINE)
        _value = cast(ensobjlist['ENS_POLYLINE'], value)
        return _value

    @property
    def defaultpolyline(self) -> ensobjlist['ENS_POLYLINE']:
        """DEFAULTPOLYLINE property
        
        default polyline
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'defaultpolyline' and 'DEFAULTPOLYLINE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTPOLYLINE)
        _value = cast(ensobjlist['ENS_POLYLINE'], value)
        return _value

    @property
    def DEFAULTQUERY(self) -> ensobjlist['ENS_QUERY']:
        """DEFAULTQUERY property
        
        default query
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTQUERY)
        _value = cast(ensobjlist['ENS_QUERY'], value)
        return _value

    @property
    def defaultquery(self) -> ensobjlist['ENS_QUERY']:
        """DEFAULTQUERY property
        
        default query
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'defaultquery' and 'DEFAULTQUERY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTQUERY)
        _value = cast(ensobjlist['ENS_QUERY'], value)
        return _value

    @property
    def DEFAULTVPORT(self) -> ensobjlist['ENS_VPORT']:
        """DEFAULTVPORT property
        
        default viewport
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTVPORT)
        _value = cast(ensobjlist['ENS_VPORT'], value)
        return _value

    @property
    def defaultvport(self) -> ensobjlist['ENS_VPORT']:
        """DEFAULTVPORT property
        
        default viewport
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'defaultvport' and 'DEFAULTVPORT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTVPORT)
        _value = cast(ensobjlist['ENS_VPORT'], value)
        return _value

    @property
    def DEFAULTVARIABLE(self) -> ensobjlist['ENS_VAR']:
        """DEFAULTVARIABLE property
        
        default variable
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @property
    def defaultvariable(self) -> ensobjlist['ENS_VAR']:
        """DEFAULTVARIABLE property
        
        default variable
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'defaultvariable' and 'DEFAULTVARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULTVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @property
    def PARTHIGHLIGHT(self) -> int:
        """PARTHIGHLIGHT property
        
        part highlights
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTHIGHLIGHT)
        _value = cast(int, value)
        return _value

    @PARTHIGHLIGHT.setter
    def PARTHIGHLIGHT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTHIGHLIGHT, value)

    @property
    def parthighlight(self) -> int:
        """PARTHIGHLIGHT property
        
        part highlights
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'parthighlight' and 'PARTHIGHLIGHT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTHIGHLIGHT)
        _value = cast(int, value)
        return _value

    @parthighlight.setter
    def parthighlight(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTHIGHLIGHT, value)

    @property
    def KEYFRAMEDATA(self) -> List[dict]:
        """KEYFRAMEDATA property
        
        keyframe animation data
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.KEYFRAMEDATA)
        _value = cast(List[dict], value)
        return _value

    @property
    def keyframedata(self) -> List[dict]:
        """KEYFRAMEDATA property
        
        keyframe animation data
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'keyframedata' and 'KEYFRAMEDATA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.KEYFRAMEDATA)
        _value = cast(List[dict], value)
        return _value

    @property
    def MRU(self) -> List[dict]:
        """MRU property
        
        most recently used list
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MRU)
        _value = cast(List[dict], value)
        return _value

    @property
    def mru(self) -> List[dict]:
        """MRU property
        
        most recently used list
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'mru' and 'MRU' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MRU)
        _value = cast(List[dict], value)
        return _value

    @property
    def JLCS(self) -> ensobjlist:
        """JLCS property
        
        job launch configs
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.JLCS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def jlcs(self) -> ensobjlist:
        """JLCS property
        
        job launch configs
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'jlcs' and 'JLCS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.JLCS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def DEFAULT_JLC(self) -> ensobjlist:
        """DEFAULT_JLC property
        
        default job launch config
        
        Supported operations:
            getattr, setattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_JLC)
        _value = cast(ensobjlist, value)
        return _value

    @DEFAULT_JLC.setter
    def DEFAULT_JLC(self, value: ensobjlist) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_JLC, value)

    @property
    def default_jlc(self) -> ensobjlist:
        """DEFAULT_JLC property
        
        default job launch config
        
        Supported operations:
            getattr, setattr
        Datatype:
            Object, scalar
        
        Note: both 'default_jlc' and 'DEFAULT_JLC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_JLC)
        _value = cast(ensobjlist, value)
        return _value

    @default_jlc.setter
    def default_jlc(self, value: ensobjlist) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_JLC, value)

    @property
    def PLOTS(self) -> ensobjlist['ENS_PLOTTER']:
        """PLOTS property
        
        plots
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTS)
        _value = cast(ensobjlist['ENS_PLOTTER'], value)
        return _value

    @property
    def plots(self) -> ensobjlist['ENS_PLOTTER']:
        """PLOTS property
        
        plots
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'plots' and 'PLOTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTS)
        _value = cast(ensobjlist['ENS_PLOTTER'], value)
        return _value

    @property
    def FRAMES(self) -> ensobjlist['ENS_FRAME']:
        """FRAMES property
        
        frames
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FRAMES)
        _value = cast(ensobjlist['ENS_FRAME'], value)
        return _value

    @property
    def frames(self) -> ensobjlist['ENS_FRAME']:
        """FRAMES property
        
        frames
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'frames' and 'FRAMES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FRAMES)
        _value = cast(ensobjlist['ENS_FRAME'], value)
        return _value

    @property
    def QUERIES(self) -> ensobjlist['ENS_QUERY']:
        """QUERIES property
        
        queries
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERIES)
        _value = cast(ensobjlist['ENS_QUERY'], value)
        return _value

    @property
    def queries(self) -> ensobjlist['ENS_QUERY']:
        """QUERIES property
        
        queries
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'queries' and 'QUERIES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERIES)
        _value = cast(ensobjlist['ENS_QUERY'], value)
        return _value

    @property
    def PROBES(self) -> ensobjlist['ENS_PROBE']:
        """PROBES property
        
        probes
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PROBES)
        _value = cast(ensobjlist['ENS_PROBE'], value)
        return _value

    @property
    def probes(self) -> ensobjlist['ENS_PROBE']:
        """PROBES property
        
        probes
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'probes' and 'PROBES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PROBES)
        _value = cast(ensobjlist['ENS_PROBE'], value)
        return _value

    @property
    def FLIPBOOKS(self) -> ensobjlist['ENS_FLIPBOOK']:
        """FLIPBOOKS property
        
        flipbooks
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FLIPBOOKS)
        _value = cast(ensobjlist['ENS_FLIPBOOK'], value)
        return _value

    @property
    def flipbooks(self) -> ensobjlist['ENS_FLIPBOOK']:
        """FLIPBOOKS property
        
        flipbooks
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'flipbooks' and 'FLIPBOOKS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FLIPBOOKS)
        _value = cast(ensobjlist['ENS_FLIPBOOK'], value)
        return _value

    @property
    def POLYLINES(self) -> ensobjlist['ENS_POLYLINE']:
        """POLYLINES property
        
        polylines
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.POLYLINES)
        _value = cast(ensobjlist['ENS_POLYLINE'], value)
        return _value

    @property
    def polylines(self) -> ensobjlist['ENS_POLYLINE']:
        """POLYLINES property
        
        polylines
        
        Supported operations:
            getattr
        Datatype:
            Object, 0 element array
        
        Note: both 'polylines' and 'POLYLINES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.POLYLINES)
        _value = cast(ensobjlist['ENS_POLYLINE'], value)
        return _value

    @property
    def FONTFAMILIES(self) -> List[dict]:
        """FONTFAMILIES property
        
        font families
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FONTFAMILIES)
        _value = cast(List[dict], value)
        return _value

    @property
    def fontfamilies(self) -> List[dict]:
        """FONTFAMILIES property
        
        font families
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'fontfamilies' and 'FONTFAMILIES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FONTFAMILIES)
        _value = cast(List[dict], value)
        return _value

    @property
    def DEFAULT_ANNOT_FONTFAMILY(self) -> str:
        """DEFAULT_ANNOT_FONTFAMILY property
        
        default annotation font family
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTFAMILY)
        _value = cast(str, value)
        return _value

    @DEFAULT_ANNOT_FONTFAMILY.setter
    def DEFAULT_ANNOT_FONTFAMILY(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTFAMILY, value)

    @property
    def default_annot_fontfamily(self) -> str:
        """DEFAULT_ANNOT_FONTFAMILY property
        
        default annotation font family
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'default_annot_fontfamily' and 'DEFAULT_ANNOT_FONTFAMILY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTFAMILY)
        _value = cast(str, value)
        return _value

    @default_annot_fontfamily.setter
    def default_annot_fontfamily(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTFAMILY, value)

    @property
    def DEFAULT_ANNOT_FONTSTYLE(self) -> int:
        """DEFAULT_ANNOT_FONTSTYLE property
        
        default annotation font style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTSTYLE)
        _value = cast(int, value)
        return _value

    @DEFAULT_ANNOT_FONTSTYLE.setter
    def DEFAULT_ANNOT_FONTSTYLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTSTYLE, value)

    @property
    def default_annot_fontstyle(self) -> int:
        """DEFAULT_ANNOT_FONTSTYLE property
        
        default annotation font style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'default_annot_fontstyle' and 'DEFAULT_ANNOT_FONTSTYLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTSTYLE)
        _value = cast(int, value)
        return _value

    @default_annot_fontstyle.setter
    def default_annot_fontstyle(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_ANNOT_FONTSTYLE, value)

    @property
    def DEFAULT_3DANNOT_FONTSIZE(self) -> int:
        """DEFAULT_3DANNOT_FONTSIZE property
        
        default 3d annotation font size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_3DANNOT_FONTSIZE)
        _value = cast(int, value)
        return _value

    @DEFAULT_3DANNOT_FONTSIZE.setter
    def DEFAULT_3DANNOT_FONTSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_3DANNOT_FONTSIZE, value)

    @property
    def default_3dannot_fontsize(self) -> int:
        """DEFAULT_3DANNOT_FONTSIZE property
        
        default 3d annotation font size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'default_3dannot_fontsize' and 'DEFAULT_3DANNOT_FONTSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_3DANNOT_FONTSIZE)
        _value = cast(int, value)
        return _value

    @default_3dannot_fontsize.setter
    def default_3dannot_fontsize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_3DANNOT_FONTSIZE, value)

    @property
    def DEFAULT_SYMBOL_FONTFAMILY(self) -> str:
        """DEFAULT_SYMBOL_FONTFAMILY property
        
        default symbol font family
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTFAMILY)
        _value = cast(str, value)
        return _value

    @DEFAULT_SYMBOL_FONTFAMILY.setter
    def DEFAULT_SYMBOL_FONTFAMILY(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTFAMILY, value)

    @property
    def default_symbol_fontfamily(self) -> str:
        """DEFAULT_SYMBOL_FONTFAMILY property
        
        default symbol font family
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'default_symbol_fontfamily' and 'DEFAULT_SYMBOL_FONTFAMILY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTFAMILY)
        _value = cast(str, value)
        return _value

    @default_symbol_fontfamily.setter
    def default_symbol_fontfamily(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTFAMILY, value)

    @property
    def DEFAULT_SYMBOL_FONTSTYLE(self) -> int:
        """DEFAULT_SYMBOL_FONTSTYLE property
        
        default symbol font style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTSTYLE)
        _value = cast(int, value)
        return _value

    @DEFAULT_SYMBOL_FONTSTYLE.setter
    def DEFAULT_SYMBOL_FONTSTYLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTSTYLE, value)

    @property
    def default_symbol_fontstyle(self) -> int:
        """DEFAULT_SYMBOL_FONTSTYLE property
        
        default symbol font style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'default_symbol_fontstyle' and 'DEFAULT_SYMBOL_FONTSTYLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTSTYLE)
        _value = cast(int, value)
        return _value

    @default_symbol_fontstyle.setter
    def default_symbol_fontstyle(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_SYMBOL_FONTSTYLE, value)

    @property
    def DEFAULT_CORE_FONTFAMILY(self) -> str:
        """DEFAULT_CORE_FONTFAMILY property
        
        default core font family
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTFAMILY)
        _value = cast(str, value)
        return _value

    @DEFAULT_CORE_FONTFAMILY.setter
    def DEFAULT_CORE_FONTFAMILY(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTFAMILY, value)

    @property
    def default_core_fontfamily(self) -> str:
        """DEFAULT_CORE_FONTFAMILY property
        
        default core font family
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 256 characters maximum
        
        Note: both 'default_core_fontfamily' and 'DEFAULT_CORE_FONTFAMILY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTFAMILY)
        _value = cast(str, value)
        return _value

    @default_core_fontfamily.setter
    def default_core_fontfamily(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTFAMILY, value)

    @property
    def DEFAULT_CORE_FONTSTYLE(self) -> int:
        """DEFAULT_CORE_FONTSTYLE property
        
        default core font style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSTYLE)
        _value = cast(int, value)
        return _value

    @DEFAULT_CORE_FONTSTYLE.setter
    def DEFAULT_CORE_FONTSTYLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSTYLE, value)

    @property
    def default_core_fontstyle(self) -> int:
        """DEFAULT_CORE_FONTSTYLE property
        
        default core font style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'default_core_fontstyle' and 'DEFAULT_CORE_FONTSTYLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSTYLE)
        _value = cast(int, value)
        return _value

    @default_core_fontstyle.setter
    def default_core_fontstyle(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSTYLE, value)

    @property
    def DEFAULT_CORE_FONTSCALE(self) -> float:
        """DEFAULT_CORE_FONTSCALE property
        
        default core font scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSCALE)
        _value = cast(float, value)
        return _value

    @DEFAULT_CORE_FONTSCALE.setter
    def DEFAULT_CORE_FONTSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSCALE, value)

    @property
    def default_core_fontscale(self) -> float:
        """DEFAULT_CORE_FONTSCALE property
        
        default core font scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'default_core_fontscale' and 'DEFAULT_CORE_FONTSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSCALE)
        _value = cast(float, value)
        return _value

    @default_core_fontscale.setter
    def default_core_fontscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DEFAULT_CORE_FONTSCALE, value)

    @property
    def LANGUAGE_INFO(self) -> Dict[Any, Any]:
        """LANGUAGE_INFO property
        
        language information
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LANGUAGE_INFO)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def language_info(self) -> Dict[Any, Any]:
        """LANGUAGE_INFO property
        
        language information
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'language_info' and 'LANGUAGE_INFO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LANGUAGE_INFO)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def PREDEFINEDPALETTES(self) -> List[dict]:
        """PREDEFINEDPALETTES property
        
        predefined palettes
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PREDEFINEDPALETTES)
        _value = cast(List[dict], value)
        return _value

    @property
    def predefinedpalettes(self) -> List[dict]:
        """PREDEFINEDPALETTES property
        
        predefined palettes
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'predefinedpalettes' and 'PREDEFINEDPALETTES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PREDEFINEDPALETTES)
        _value = cast(List[dict], value)
        return _value

    @property
    def PALETTES(self) -> ensobjlist:
        """PALETTES property
        
        palettes
        
        Supported operations:
            getattr
        Datatype:
            Object, 5 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PALETTES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def palettes(self) -> ensobjlist:
        """PALETTES property
        
        palettes
        
        Supported operations:
            getattr
        Datatype:
            Object, 5 element array
        
        Note: both 'palettes' and 'PALETTES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PALETTES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def DELAY_REFRESH(self) -> int:
        """DELAY_REFRESH property
        
        delay refresh
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DELAY_REFRESH)
        _value = cast(int, value)
        return _value

    @DELAY_REFRESH.setter
    def DELAY_REFRESH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DELAY_REFRESH, value)

    @property
    def delay_refresh(self) -> int:
        """DELAY_REFRESH property
        
        delay refresh
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'delay_refresh' and 'DELAY_REFRESH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DELAY_REFRESH)
        _value = cast(int, value)
        return _value

    @delay_refresh.setter
    def delay_refresh(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DELAY_REFRESH, value)

    @property
    def SHADING(self) -> int:
        """SHADING property
        
        part shading
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
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
        
        part shading
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
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
        
        hidden line display
        
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
        
        hidden line display
        
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
    def HIDDENLINE_RGB(self) -> List[float]:
        """HIDDENLINE_RGB property
        
        hidden line rgb color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE_RGB)
        _value = cast(List[float], value)
        return _value

    @HIDDENLINE_RGB.setter
    def HIDDENLINE_RGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE_RGB, value)

    @property
    def hiddenline_rgb(self) -> List[float]:
        """HIDDENLINE_RGB property
        
        hidden line rgb color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'hiddenline_rgb' and 'HIDDENLINE_RGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE_RGB)
        _value = cast(List[float], value)
        return _value

    @hiddenline_rgb.setter
    def hiddenline_rgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE_RGB, value)

    @property
    def HIDDENLINE_WEIGHT(self) -> float:
        """HIDDENLINE_WEIGHT property
        
        hidden line weight
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE_WEIGHT)
        _value = cast(float, value)
        return _value

    @HIDDENLINE_WEIGHT.setter
    def HIDDENLINE_WEIGHT(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE_WEIGHT, value)

    @property
    def hiddenline_weight(self) -> float:
        """HIDDENLINE_WEIGHT property
        
        hidden line weight
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'hiddenline_weight' and 'HIDDENLINE_WEIGHT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE_WEIGHT)
        _value = cast(float, value)
        return _value

    @hiddenline_weight.setter
    def hiddenline_weight(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE_WEIGHT, value)

    @property
    def HIDDENLINE_USE_RGB(self) -> int:
        """HIDDENLINE_USE_RGB property
        
        use hidden line rgb color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE_USE_RGB)
        _value = cast(int, value)
        return _value

    @HIDDENLINE_USE_RGB.setter
    def HIDDENLINE_USE_RGB(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE_USE_RGB, value)

    @property
    def hiddenline_use_rgb(self) -> int:
        """HIDDENLINE_USE_RGB property
        
        use hidden line rgb color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'hiddenline_use_rgb' and 'HIDDENLINE_USE_RGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HIDDENLINE_USE_RGB)
        _value = cast(int, value)
        return _value

    @hiddenline_use_rgb.setter
    def hiddenline_use_rgb(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HIDDENLINE_USE_RGB, value)

    @property
    def WATERMARK(self) -> int:
        """WATERMARK property
        
        water mark
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.WATERMARK)
        _value = cast(int, value)
        return _value

    @WATERMARK.setter
    def WATERMARK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.WATERMARK, value)

    @property
    def watermark(self) -> int:
        """WATERMARK property
        
        water mark
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'watermark' and 'WATERMARK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.WATERMARK)
        _value = cast(int, value)
        return _value

    @watermark.setter
    def watermark(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.WATERMARK, value)

    @property
    def CASE_LINKING_LABELS(self) -> int:
        """CASE_LINKING_LABELS property
        
        case linking labels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CASE_LINKING_LABELS)
        _value = cast(int, value)
        return _value

    @CASE_LINKING_LABELS.setter
    def CASE_LINKING_LABELS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CASE_LINKING_LABELS, value)

    @property
    def case_linking_labels(self) -> int:
        """CASE_LINKING_LABELS property
        
        case linking labels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'case_linking_labels' and 'CASE_LINKING_LABELS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CASE_LINKING_LABELS)
        _value = cast(int, value)
        return _value

    @case_linking_labels.setter
    def case_linking_labels(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CASE_LINKING_LABELS, value)

    @property
    def FASTDISPLAY(self) -> int:
        """FASTDISPLAY property
        
        fast part display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FASTDISPLAY)
        _value = cast(int, value)
        return _value

    @FASTDISPLAY.setter
    def FASTDISPLAY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FASTDISPLAY, value)

    @property
    def fastdisplay(self) -> int:
        """FASTDISPLAY property
        
        fast part display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'fastdisplay' and 'FASTDISPLAY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FASTDISPLAY)
        _value = cast(int, value)
        return _value

    @fastdisplay.setter
    def fastdisplay(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FASTDISPLAY, value)

    @property
    def PERSPECTIVE(self) -> int:
        """PERSPECTIVE property
        
        perspective display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PERSPECTIVE)
        _value = cast(int, value)
        return _value

    @PERSPECTIVE.setter
    def PERSPECTIVE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PERSPECTIVE, value)

    @property
    def perspective(self) -> int:
        """PERSPECTIVE property
        
        perspective display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'perspective' and 'PERSPECTIVE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PERSPECTIVE)
        _value = cast(int, value)
        return _value

    @perspective.setter
    def perspective(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PERSPECTIVE, value)

    @property
    def AUXCLIPPING(self) -> int:
        """AUXCLIPPING property
        
        aux clipping planes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AUXCLIPPING)
        _value = cast(int, value)
        return _value

    @AUXCLIPPING.setter
    def AUXCLIPPING(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AUXCLIPPING, value)

    @property
    def auxclipping(self) -> int:
        """AUXCLIPPING property
        
        aux clipping planes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'auxclipping' and 'AUXCLIPPING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AUXCLIPPING)
        _value = cast(int, value)
        return _value

    @auxclipping.setter
    def auxclipping(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AUXCLIPPING, value)

    @property
    def SECURITY_TOKEN(self) -> int:
        """SECURITY_TOKEN property
        
        security token
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SECURITY_TOKEN)
        _value = cast(int, value)
        return _value

    @SECURITY_TOKEN.setter
    def SECURITY_TOKEN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SECURITY_TOKEN, value)

    @property
    def security_token(self) -> int:
        """SECURITY_TOKEN property
        
        security token
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'security_token' and 'SECURITY_TOKEN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SECURITY_TOKEN)
        _value = cast(int, value)
        return _value

    @security_token.setter
    def security_token(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SECURITY_TOKEN, value)

    @property
    def STEREO_SEPARATION(self) -> float:
        """STEREO_SEPARATION property
        
        stereo eye separation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.STEREO_SEPARATION)
        _value = cast(float, value)
        return _value

    @STEREO_SEPARATION.setter
    def STEREO_SEPARATION(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.STEREO_SEPARATION, value)

    @property
    def stereo_separation(self) -> float:
        """STEREO_SEPARATION property
        
        stereo eye separation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'stereo_separation' and 'STEREO_SEPARATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.STEREO_SEPARATION)
        _value = cast(float, value)
        return _value

    @stereo_separation.setter
    def stereo_separation(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.STEREO_SEPARATION, value)

    @property
    def STEREO_CAPABLE(self) -> int:
        """STEREO_CAPABLE property
        
        stereo capable
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.STEREO_CAPABLE)
        _value = cast(int, value)
        return _value

    @STEREO_CAPABLE.setter
    def STEREO_CAPABLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.STEREO_CAPABLE, value)

    @property
    def stereo_capable(self) -> int:
        """STEREO_CAPABLE property
        
        stereo capable
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'stereo_capable' and 'STEREO_CAPABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.STEREO_CAPABLE)
        _value = cast(int, value)
        return _value

    @stereo_capable.setter
    def stereo_capable(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.STEREO_CAPABLE, value)

    @property
    def REALTIME_CLIPS(self) -> Dict[Any, Any]:
        """REALTIME_CLIPS property
        
        realtime clips
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REALTIME_CLIPS)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def realtime_clips(self) -> Dict[Any, Any]:
        """REALTIME_CLIPS property
        
        realtime clips
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'realtime_clips' and 'REALTIME_CLIPS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REALTIME_CLIPS)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def REALTIME_ISOS(self) -> Dict[Any, Any]:
        """REALTIME_ISOS property
        
        realtime isos
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.REALTIME_ISOS)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def realtime_isos(self) -> Dict[Any, Any]:
        """REALTIME_ISOS property
        
        realtime isos
        
        Supported operations:
            getattr
        Datatype:
            Dictionary, scalar
        
        Note: both 'realtime_isos' and 'REALTIME_ISOS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.REALTIME_ISOS)
        _value = cast(Dict[Any, Any], value)
        return _value

    @property
    def QUERY_PROBE_DATA(self) -> List[dict]:
        """QUERY_PROBE_DATA property
        
        query probe data
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERY_PROBE_DATA)
        _value = cast(List[dict], value)
        return _value

    @property
    def query_probe_data(self) -> List[dict]:
        """QUERY_PROBE_DATA property
        
        query probe data
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'query_probe_data' and 'QUERY_PROBE_DATA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.QUERY_PROBE_DATA)
        _value = cast(List[dict], value)
        return _value

    @property
    def STATUS_STRING(self) -> str:
        """STATUS_STRING property
        
        status string
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.STATUS_STRING)
        _value = cast(str, value)
        return _value

    @STATUS_STRING.setter
    def STATUS_STRING(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.STATUS_STRING, value)

    @property
    def status_string(self) -> str:
        """STATUS_STRING property
        
        status string
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'status_string' and 'STATUS_STRING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.STATUS_STRING)
        _value = cast(str, value)
        return _value

    @status_string.setter
    def status_string(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.STATUS_STRING, value)

    @property
    def ANIMATING(self) -> int:
        """ANIMATING property
        
        animation enabled
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANIMATING)
        _value = cast(int, value)
        return _value

    @ANIMATING.setter
    def ANIMATING(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANIMATING, value)

    @property
    def animating(self) -> int:
        """ANIMATING property
        
        animation enabled
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'animating' and 'ANIMATING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANIMATING)
        _value = cast(int, value)
        return _value

    @animating.setter
    def animating(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANIMATING, value)

    @property
    def RECORDING(self) -> int:
        """RECORDING property
        
        recording animation
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RECORDING)
        _value = cast(int, value)
        return _value

    @property
    def recording(self) -> int:
        """RECORDING property
        
        recording animation
        
        Supported operations:
            getattr
        Datatype:
            Integer, scalar
        
        Note: both 'recording' and 'RECORDING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RECORDING)
        _value = cast(int, value)
        return _value

    @property
    def FRAME_DURATION(self) -> float:
        """FRAME_DURATION property
        
        default frame duration
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FRAME_DURATION)
        _value = cast(float, value)
        return _value

    @FRAME_DURATION.setter
    def FRAME_DURATION(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.FRAME_DURATION, value)

    @property
    def frame_duration(self) -> float:
        """FRAME_DURATION property
        
        default frame duration
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'frame_duration' and 'FRAME_DURATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FRAME_DURATION)
        _value = cast(float, value)
        return _value

    @frame_duration.setter
    def frame_duration(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.FRAME_DURATION, value)

    @property
    def ANIMOBJS(self) -> List[dict]:
        """ANIMOBJS property
        
        active animation objects
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANIMOBJS)
        _value = cast(List[dict], value)
        return _value

    @property
    def animobjs(self) -> List[dict]:
        """ANIMOBJS property
        
        active animation objects
        
        Supported operations:
            getattr
        Datatype:
            List of dictionaries, scalar
        
        Note: both 'animobjs' and 'ANIMOBJS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANIMOBJS)
        _value = cast(List[dict], value)
        return _value

    @property
    def OBJECT_API_JOURNAL(self) -> int:
        """OBJECT_API_JOURNAL property
        
        object API journaling state
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OBJECT_API_JOURNAL)
        _value = cast(int, value)
        return _value

    @OBJECT_API_JOURNAL.setter
    def OBJECT_API_JOURNAL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OBJECT_API_JOURNAL, value)

    @property
    def object_api_journal(self) -> int:
        """OBJECT_API_JOURNAL property
        
        object API journaling state
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'object_api_journal' and 'OBJECT_API_JOURNAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OBJECT_API_JOURNAL)
        _value = cast(int, value)
        return _value

    @object_api_journal.setter
    def object_api_journal(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.OBJECT_API_JOURNAL, value)

    @property
    def TIMESTEP_LIMITS(self) -> List[int]:
        """TIMESTEP_LIMITS property
        
        limits on timestep values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMESTEP_LIMITS)
        _value = cast(List[int], value)
        return _value

    @TIMESTEP_LIMITS.setter
    def TIMESTEP_LIMITS(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMESTEP_LIMITS, value)

    @property
    def timestep_limits(self) -> List[int]:
        """TIMESTEP_LIMITS property
        
        limits on timestep values
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        Note: both 'timestep_limits' and 'TIMESTEP_LIMITS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMESTEP_LIMITS)
        _value = cast(List[int], value)
        return _value

    @timestep_limits.setter
    def timestep_limits(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMESTEP_LIMITS, value)

    @property
    def TIMESTEP(self) -> float:
        """TIMESTEP property
        
        current timestep
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMESTEP)
        _value = cast(float, value)
        return _value

    @TIMESTEP.setter
    def TIMESTEP(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMESTEP, value)

    @property
    def timestep(self) -> float:
        """TIMESTEP property
        
        current timestep
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'timestep' and 'TIMESTEP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMESTEP)
        _value = cast(float, value)
        return _value

    @timestep.setter
    def timestep(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMESTEP, value)

    @property
    def SOLUTIONTIME_LIMITS(self) -> List[float]:
        """SOLUTIONTIME_LIMITS property
        
        limits on solution time values
        
        Supported operations:
            getattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SOLUTIONTIME_LIMITS)
        _value = cast(List[float], value)
        return _value

    @property
    def solutiontime_limits(self) -> List[float]:
        """SOLUTIONTIME_LIMITS property
        
        limits on solution time values
        
        Supported operations:
            getattr
        Datatype:
            Float, 2 element array
        
        Note: both 'solutiontime_limits' and 'SOLUTIONTIME_LIMITS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SOLUTIONTIME_LIMITS)
        _value = cast(List[float], value)
        return _value

    @property
    def SOLUTIONTIME(self) -> float:
        """SOLUTIONTIME property
        
        current solution time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SOLUTIONTIME)
        _value = cast(float, value)
        return _value

    @SOLUTIONTIME.setter
    def SOLUTIONTIME(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SOLUTIONTIME, value)

    @property
    def solutiontime(self) -> float:
        """SOLUTIONTIME property
        
        current solution time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'solutiontime' and 'SOLUTIONTIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SOLUTIONTIME)
        _value = cast(float, value)
        return _value

    @solutiontime.setter
    def solutiontime(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SOLUTIONTIME, value)

    @property
    def TIMEVALUES(self) -> object:
        """TIMEVALUES property
        
        timeset values
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEVALUES)
        _value = cast(object, value)
        return _value

    @TIMEVALUES.setter
    def TIMEVALUES(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEVALUES, value)

    @property
    def timevalues(self) -> object:
        """TIMEVALUES property
        
        timeset values
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'timevalues' and 'TIMEVALUES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TIMEVALUES)
        _value = cast(object, value)
        return _value

    @timevalues.setter
    def timevalues(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.TIMEVALUES, value)

    @property
    def DISPLAY_THEME(self) -> int:
        """DISPLAY_THEME property
        
        current display theme
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLAY_THEME)
        _value = cast(int, value)
        return _value

    @DISPLAY_THEME.setter
    def DISPLAY_THEME(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLAY_THEME, value)

    @property
    def display_theme(self) -> int:
        """DISPLAY_THEME property
        
        current display theme
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'display_theme' and 'DISPLAY_THEME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DISPLAY_THEME)
        _value = cast(int, value)
        return _value

    @display_theme.setter
    def display_theme(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DISPLAY_THEME, value)

    @property
    def PICK_SELECTION(self) -> ensobjlist:
        """PICK_SELECTION property
        
        object under cursor
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PICK_SELECTION)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def pick_selection(self) -> ensobjlist:
        """PICK_SELECTION property
        
        object under cursor
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'pick_selection' and 'PICK_SELECTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PICK_SELECTION)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def PATHLINE_SYNC(self) -> int:
        """PATHLINE_SYNC property
        
        sync pathlines to time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PATHLINE_SYNC)
        _value = cast(int, value)
        return _value

    @PATHLINE_SYNC.setter
    def PATHLINE_SYNC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PATHLINE_SYNC, value)

    @property
    def pathline_sync(self) -> int:
        """PATHLINE_SYNC property
        
        sync pathlines to time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'pathline_sync' and 'PATHLINE_SYNC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PATHLINE_SYNC)
        _value = cast(int, value)
        return _value

    @pathline_sync.setter
    def pathline_sync(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PATHLINE_SYNC, value)

    @property
    def CURRENTGUI(self) -> object:
        """CURRENTGUI property
        
        current GUI
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENTGUI)
        _value = cast(object, value)
        return _value

    @property
    def currentgui(self) -> object:
        """CURRENTGUI property
        
        current GUI
        
        Supported operations:
            getattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'currentgui' and 'CURRENTGUI' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CURRENTGUI)
        _value = cast(object, value)
        return _value

    @property
    def FULLSCREEN(self) -> int:
        """FULLSCREEN property
        
        fullscreen mode
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FULLSCREEN)
        _value = cast(int, value)
        return _value

    @FULLSCREEN.setter
    def FULLSCREEN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FULLSCREEN, value)

    @property
    def fullscreen(self) -> int:
        """FULLSCREEN property
        
        fullscreen mode
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'fullscreen' and 'FULLSCREEN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FULLSCREEN)
        _value = cast(int, value)
        return _value

    @fullscreen.setter
    def fullscreen(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FULLSCREEN, value)

    @property
    def WINDOWSIZE(self) -> List[int]:
        """WINDOWSIZE property
        
        window size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.WINDOWSIZE)
        _value = cast(List[int], value)
        return _value

    @WINDOWSIZE.setter
    def WINDOWSIZE(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.WINDOWSIZE, value)

    @property
    def windowsize(self) -> List[int]:
        """WINDOWSIZE property
        
        window size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, 2 element array
        
        Note: both 'windowsize' and 'WINDOWSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.WINDOWSIZE)
        _value = cast(List[int], value)
        return _value

    @windowsize.setter
    def windowsize(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.WINDOWSIZE, value)

    @property
    def HILITE_METHOD(self) -> int:
        """HILITE_METHOD property
        
        selection hiliting method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.CVF_HILITE_METHOD_GEOMETRY - Geometry
            * ensight.objs.enums.CVF_HILITE_METHOD_IMAGE - Image
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_METHOD)
        _value = cast(int, value)
        return _value

    @HILITE_METHOD.setter
    def HILITE_METHOD(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_METHOD, value)

    @property
    def hilite_method(self) -> int:
        """HILITE_METHOD property
        
        selection hiliting method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.CVF_HILITE_METHOD_GEOMETRY - Geometry
            * ensight.objs.enums.CVF_HILITE_METHOD_IMAGE - Image
        
        Note: both 'hilite_method' and 'HILITE_METHOD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_METHOD)
        _value = cast(int, value)
        return _value

    @hilite_method.setter
    def hilite_method(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_METHOD, value)

    @property
    def HILITE_TARGET_COLOR(self) -> List[float]:
        """HILITE_TARGET_COLOR property
        
        target hilite outline color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR)
        _value = cast(List[float], value)
        return _value

    @HILITE_TARGET_COLOR.setter
    def HILITE_TARGET_COLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR, value)

    @property
    def hilite_target_color(self) -> List[float]:
        """HILITE_TARGET_COLOR property
        
        target hilite outline color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        Note: both 'hilite_target_color' and 'HILITE_TARGET_COLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR)
        _value = cast(List[float], value)
        return _value

    @hilite_target_color.setter
    def hilite_target_color(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR, value)

    @property
    def HILITE_TARGET_COLOR_FILL(self) -> List[float]:
        """HILITE_TARGET_COLOR_FILL property
        
        target hilite fill color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR_FILL)
        _value = cast(List[float], value)
        return _value

    @HILITE_TARGET_COLOR_FILL.setter
    def HILITE_TARGET_COLOR_FILL(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR_FILL, value)

    @property
    def hilite_target_color_fill(self) -> List[float]:
        """HILITE_TARGET_COLOR_FILL property
        
        target hilite fill color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        Note: both 'hilite_target_color_fill' and 'HILITE_TARGET_COLOR_FILL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR_FILL)
        _value = cast(List[float], value)
        return _value

    @hilite_target_color_fill.setter
    def hilite_target_color_fill(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_TARGET_COLOR_FILL, value)

    @property
    def HILITE_SELECT_COLOR(self) -> List[float]:
        """HILITE_SELECT_COLOR property
        
        selection hilite outline color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR)
        _value = cast(List[float], value)
        return _value

    @HILITE_SELECT_COLOR.setter
    def HILITE_SELECT_COLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR, value)

    @property
    def hilite_select_color(self) -> List[float]:
        """HILITE_SELECT_COLOR property
        
        selection hilite outline color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        Note: both 'hilite_select_color' and 'HILITE_SELECT_COLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR)
        _value = cast(List[float], value)
        return _value

    @hilite_select_color.setter
    def hilite_select_color(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR, value)

    @property
    def HILITE_SELECT_COLOR_FILL(self) -> List[float]:
        """HILITE_SELECT_COLOR_FILL property
        
        selection hilite fill color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR_FILL)
        _value = cast(List[float], value)
        return _value

    @HILITE_SELECT_COLOR_FILL.setter
    def HILITE_SELECT_COLOR_FILL(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR_FILL, value)

    @property
    def hilite_select_color_fill(self) -> List[float]:
        """HILITE_SELECT_COLOR_FILL property
        
        selection hilite fill color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        Note: both 'hilite_select_color_fill' and 'HILITE_SELECT_COLOR_FILL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR_FILL)
        _value = cast(List[float], value)
        return _value

    @hilite_select_color_fill.setter
    def hilite_select_color_fill(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_SELECT_COLOR_FILL, value)

    @property
    def HILITE_BACK_COLOR_FILL(self) -> List[float]:
        """HILITE_BACK_COLOR_FILL property
        
        unselected object hilite fill color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_BACK_COLOR_FILL)
        _value = cast(List[float], value)
        return _value

    @HILITE_BACK_COLOR_FILL.setter
    def HILITE_BACK_COLOR_FILL(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_BACK_COLOR_FILL, value)

    @property
    def hilite_back_color_fill(self) -> List[float]:
        """HILITE_BACK_COLOR_FILL property
        
        unselected object hilite fill color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGBA, 4 element array
        
        Note: both 'hilite_back_color_fill' and 'HILITE_BACK_COLOR_FILL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HILITE_BACK_COLOR_FILL)
        _value = cast(List[float], value)
        return _value

    @hilite_back_color_fill.setter
    def hilite_back_color_fill(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.HILITE_BACK_COLOR_FILL, value)

    @property
    def FLOATINGZCLIP(self) -> int:
        """FLOATINGZCLIP property
        
        floating z clip planes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FLOATINGZCLIP)
        _value = cast(int, value)
        return _value

    @FLOATINGZCLIP.setter
    def FLOATINGZCLIP(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FLOATINGZCLIP, value)

    @property
    def floatingzclip(self) -> int:
        """FLOATINGZCLIP property
        
        floating z clip planes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'floatingzclip' and 'FLOATINGZCLIP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FLOATINGZCLIP)
        _value = cast(int, value)
        return _value

    @floatingzclip.setter
    def floatingzclip(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FLOATINGZCLIP, value)

    @property
    def ALLOW_MRU_UPDATE(self) -> int:
        """ALLOW_MRU_UPDATE property
        
        allow MRU update
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ALLOW_MRU_UPDATE)
        _value = cast(int, value)
        return _value

    @ALLOW_MRU_UPDATE.setter
    def ALLOW_MRU_UPDATE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ALLOW_MRU_UPDATE, value)

    @property
    def allow_mru_update(self) -> int:
        """ALLOW_MRU_UPDATE property
        
        allow MRU update
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'allow_mru_update' and 'ALLOW_MRU_UPDATE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ALLOW_MRU_UPDATE)
        _value = cast(int, value)
        return _value

    @allow_mru_update.setter
    def allow_mru_update(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ALLOW_MRU_UPDATE, value)

    @property
    def STEREO(self) -> int:
        """STEREO property
        
        stereo enabled
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.STEREO)
        _value = cast(int, value)
        return _value

    @STEREO.setter
    def STEREO(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.STEREO, value)

    @property
    def stereo(self) -> int:
        """STEREO property
        
        stereo enabled
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'stereo' and 'STEREO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.STEREO)
        _value = cast(int, value)
        return _value

    @stereo.setter
    def stereo(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.STEREO, value)

    @property
    def VOLUME_CHUNKING_NUM_TETS(self) -> int:
        """VOLUME_CHUNKING_NUM_TETS property
        
        volume rendering chunking tet count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUME_CHUNKING_NUM_TETS)
        _value = cast(int, value)
        return _value

    @VOLUME_CHUNKING_NUM_TETS.setter
    def VOLUME_CHUNKING_NUM_TETS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VOLUME_CHUNKING_NUM_TETS, value)

    @property
    def volume_chunking_num_tets(self) -> int:
        """VOLUME_CHUNKING_NUM_TETS property
        
        volume rendering chunking tet count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'volume_chunking_num_tets' and 'VOLUME_CHUNKING_NUM_TETS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUME_CHUNKING_NUM_TETS)
        _value = cast(int, value)
        return _value

    @volume_chunking_num_tets.setter
    def volume_chunking_num_tets(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VOLUME_CHUNKING_NUM_TETS, value)

    @property
    def VOLUME_NUM_PASSES(self) -> int:
        """VOLUME_NUM_PASSES property
        
        volume rendering pass count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUME_NUM_PASSES)
        _value = cast(int, value)
        return _value

    @VOLUME_NUM_PASSES.setter
    def VOLUME_NUM_PASSES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VOLUME_NUM_PASSES, value)

    @property
    def volume_num_passes(self) -> int:
        """VOLUME_NUM_PASSES property
        
        volume rendering pass count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'volume_num_passes' and 'VOLUME_NUM_PASSES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VOLUME_NUM_PASSES)
        _value = cast(int, value)
        return _value

    @volume_num_passes.setter
    def volume_num_passes(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VOLUME_NUM_PASSES, value)

    @property
    def TRANSPARENT_METHOD(self) -> int:
        """TRANSPARENT_METHOD property
        
        transparency rendering method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.TRANSP_SORT_INTERACTIVE - Interactive
            * ensight.objs.enums.TRANSP_SORT_DELAYED - Delayed
            * ensight.objs.enums.TRANSP_SORT_DEPTHPEEL - Depthpeel
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSPARENT_METHOD)
        _value = cast(int, value)
        return _value

    @TRANSPARENT_METHOD.setter
    def TRANSPARENT_METHOD(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSPARENT_METHOD, value)

    @property
    def transparent_method(self) -> int:
        """TRANSPARENT_METHOD property
        
        transparency rendering method
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.TRANSP_SORT_INTERACTIVE - Interactive
            * ensight.objs.enums.TRANSP_SORT_DELAYED - Delayed
            * ensight.objs.enums.TRANSP_SORT_DEPTHPEEL - Depthpeel
        
        Note: both 'transparent_method' and 'TRANSPARENT_METHOD' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSPARENT_METHOD)
        _value = cast(int, value)
        return _value

    @transparent_method.setter
    def transparent_method(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSPARENT_METHOD, value)

    @property
    def TRANSPARENT_NUMPEELS(self) -> int:
        """TRANSPARENT_NUMPEELS property
        
        number of depthpeeling peels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [4, 64]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSPARENT_NUMPEELS)
        _value = cast(int, value)
        return _value

    @TRANSPARENT_NUMPEELS.setter
    def TRANSPARENT_NUMPEELS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSPARENT_NUMPEELS, value)

    @property
    def transparent_numpeels(self) -> int:
        """TRANSPARENT_NUMPEELS property
        
        number of depthpeeling peels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [4, 64]
        
        Note: both 'transparent_numpeels' and 'TRANSPARENT_NUMPEELS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSPARENT_NUMPEELS)
        _value = cast(int, value)
        return _value

    @transparent_numpeels.setter
    def transparent_numpeels(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSPARENT_NUMPEELS, value)

    @property
    def PREF_DATADIR(self) -> str:
        """PREF_DATADIR property
        
        data directory preference
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PREF_DATADIR)
        _value = cast(str, value)
        return _value

    @PREF_DATADIR.setter
    def PREF_DATADIR(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PREF_DATADIR, value)

    @property
    def pref_datadir(self) -> str:
        """PREF_DATADIR property
        
        data directory preference
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'pref_datadir' and 'PREF_DATADIR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PREF_DATADIR)
        _value = cast(str, value)
        return _value

    @pref_datadir.setter
    def pref_datadir(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PREF_DATADIR, value)

    @property
    def PREF_DATAFORMAT(self) -> str:
        """PREF_DATAFORMAT property
        
        data format preference
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 20 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PREF_DATAFORMAT)
        _value = cast(str, value)
        return _value

    @PREF_DATAFORMAT.setter
    def PREF_DATAFORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PREF_DATAFORMAT, value)

    @property
    def pref_dataformat(self) -> str:
        """PREF_DATAFORMAT property
        
        data format preference
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 20 characters maximum
        
        Note: both 'pref_dataformat' and 'PREF_DATAFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PREF_DATAFORMAT)
        _value = cast(str, value)
        return _value

    @pref_dataformat.setter
    def pref_dataformat(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PREF_DATAFORMAT, value)

    @property
    def ANTIALIAS_MODE(self) -> int:
        """ANTIALIAS_MODE property
        
        anti-aliasing mode
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.CVF_AAMODE_NONE - None
            * ensight.objs.enums.CVF_AAMODE_MULTIACCUM - Multipass
            * ensight.objs.enums.CVF_AAMODE_IMAGEFILTER - Filtered
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_MODE)
        _value = cast(int, value)
        return _value

    @ANTIALIAS_MODE.setter
    def ANTIALIAS_MODE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_MODE, value)

    @property
    def antialias_mode(self) -> int:
        """ANTIALIAS_MODE property
        
        anti-aliasing mode
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.CVF_AAMODE_NONE - None
            * ensight.objs.enums.CVF_AAMODE_MULTIACCUM - Multipass
            * ensight.objs.enums.CVF_AAMODE_IMAGEFILTER - Filtered
        
        Note: both 'antialias_mode' and 'ANTIALIAS_MODE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_MODE)
        _value = cast(int, value)
        return _value

    @antialias_mode.setter
    def antialias_mode(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_MODE, value)

    @property
    def ANTIALIAS_NUM_SAMPLES(self) -> int:
        """ANTIALIAS_NUM_SAMPLES property
        
        anti-aliasing number of samples
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_NUM_SAMPLES)
        _value = cast(int, value)
        return _value

    @ANTIALIAS_NUM_SAMPLES.setter
    def ANTIALIAS_NUM_SAMPLES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_NUM_SAMPLES, value)

    @property
    def antialias_num_samples(self) -> int:
        """ANTIALIAS_NUM_SAMPLES property
        
        anti-aliasing number of samples
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'antialias_num_samples' and 'ANTIALIAS_NUM_SAMPLES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_NUM_SAMPLES)
        _value = cast(int, value)
        return _value

    @antialias_num_samples.setter
    def antialias_num_samples(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_NUM_SAMPLES, value)

    @property
    def ANTIALIAS_FILTER_ALGORITHM(self) -> int:
        """ANTIALIAS_FILTER_ALGORITHM property
        
        anti-aliasing filter type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.AA_FILTER_ALG_SMALL - Small
            * ensight.objs.enums.AA_FILTER_ALG_LARGE - Large
            * ensight.objs.enums.AA_FILTER_ALG_HYBRID - Hybrid
            * ensight.objs.enums.AA_FILTER_ALG_FXAA - FXAA
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_FILTER_ALGORITHM)
        _value = cast(int, value)
        return _value

    @ANTIALIAS_FILTER_ALGORITHM.setter
    def ANTIALIAS_FILTER_ALGORITHM(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_FILTER_ALGORITHM, value)

    @property
    def antialias_filter_algorithm(self) -> int:
        """ANTIALIAS_FILTER_ALGORITHM property
        
        anti-aliasing filter type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Enums:
            * ensight.objs.enums.AA_FILTER_ALG_SMALL - Small
            * ensight.objs.enums.AA_FILTER_ALG_LARGE - Large
            * ensight.objs.enums.AA_FILTER_ALG_HYBRID - Hybrid
            * ensight.objs.enums.AA_FILTER_ALG_FXAA - FXAA
        
        Note: both 'antialias_filter_algorithm' and 'ANTIALIAS_FILTER_ALGORITHM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_FILTER_ALGORITHM)
        _value = cast(int, value)
        return _value

    @antialias_filter_algorithm.setter
    def antialias_filter_algorithm(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_FILTER_ALGORITHM, value)

    @property
    def ANTIALIAS_PARAM_GAMMA(self) -> float:
        """ANTIALIAS_PARAM_GAMMA property
        
        antiliasing gamma
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_GAMMA)
        _value = cast(float, value)
        return _value

    @ANTIALIAS_PARAM_GAMMA.setter
    def ANTIALIAS_PARAM_GAMMA(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_GAMMA, value)

    @property
    def antialias_param_gamma(self) -> float:
        """ANTIALIAS_PARAM_GAMMA property
        
        antiliasing gamma
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'antialias_param_gamma' and 'ANTIALIAS_PARAM_GAMMA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_GAMMA)
        _value = cast(float, value)
        return _value

    @antialias_param_gamma.setter
    def antialias_param_gamma(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_GAMMA, value)

    @property
    def ANTIALIAS_PARAM_SMOOTH(self) -> float:
        """ANTIALIAS_PARAM_SMOOTH property
        
        antiliasing guassian smoothing
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_SMOOTH)
        _value = cast(float, value)
        return _value

    @ANTIALIAS_PARAM_SMOOTH.setter
    def ANTIALIAS_PARAM_SMOOTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_SMOOTH, value)

    @property
    def antialias_param_smooth(self) -> float:
        """ANTIALIAS_PARAM_SMOOTH property
        
        antiliasing guassian smoothing
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'antialias_param_smooth' and 'ANTIALIAS_PARAM_SMOOTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_SMOOTH)
        _value = cast(float, value)
        return _value

    @antialias_param_smooth.setter
    def antialias_param_smooth(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_SMOOTH, value)

    @property
    def ANTIALIAS_PARAM_COMPRESSION(self) -> float:
        """ANTIALIAS_PARAM_COMPRESSION property
        
        antiliasing gradient compression
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_COMPRESSION)
        _value = cast(float, value)
        return _value

    @ANTIALIAS_PARAM_COMPRESSION.setter
    def ANTIALIAS_PARAM_COMPRESSION(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_COMPRESSION, value)

    @property
    def antialias_param_compression(self) -> float:
        """ANTIALIAS_PARAM_COMPRESSION property
        
        antiliasing gradient compression
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'antialias_param_compression' and 'ANTIALIAS_PARAM_COMPRESSION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_COMPRESSION)
        _value = cast(float, value)
        return _value

    @antialias_param_compression.setter
    def antialias_param_compression(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ANTIALIAS_PARAM_COMPRESSION, value)

    @property
    def CLICKNGO_HANDLE_VISIBILITY(self) -> List[int]:
        """CLICKNGO_HANDLE_VISIBILITY property
        
        click and go handle visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CLICKNGO_HANDLE_VISIBILITY)
        _value = cast(List[int], value)
        return _value

    @CLICKNGO_HANDLE_VISIBILITY.setter
    def CLICKNGO_HANDLE_VISIBILITY(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLICKNGO_HANDLE_VISIBILITY, value)

    @property
    def clickngo_handle_visibility(self) -> List[int]:
        """CLICKNGO_HANDLE_VISIBILITY property
        
        click and go handle visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, 4 element array
        
        Note: both 'clickngo_handle_visibility' and 'CLICKNGO_HANDLE_VISIBILITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CLICKNGO_HANDLE_VISIBILITY)
        _value = cast(List[int], value)
        return _value

    @clickngo_handle_visibility.setter
    def clickngo_handle_visibility(self, value: List[int]) -> None:
        self.setattr(self._session.ensight.objs.enums.CLICKNGO_HANDLE_VISIBILITY, value)

    @property
    def ENSHELL_LOG(self) -> str:
        """ENSHELL_LOG property
        
        EnShell log output
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 32678 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENSHELL_LOG)
        _value = cast(str, value)
        return _value

    @ENSHELL_LOG.setter
    def ENSHELL_LOG(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENSHELL_LOG, value)

    @property
    def enshell_log(self) -> str:
        """ENSHELL_LOG property
        
        EnShell log output
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 32678 characters maximum
        
        Note: both 'enshell_log' and 'ENSHELL_LOG' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENSHELL_LOG)
        _value = cast(str, value)
        return _value

    @enshell_log.setter
    def enshell_log(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENSHELL_LOG, value)

    @property
    def PLOTTER_TIME_CLIPPING(self) -> int:
        """PLOTTER_TIME_CLIPPING property
        
        plotter time clipping
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTTER_TIME_CLIPPING)
        _value = cast(int, value)
        return _value

    @PLOTTER_TIME_CLIPPING.setter
    def PLOTTER_TIME_CLIPPING(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PLOTTER_TIME_CLIPPING, value)

    @property
    def plotter_time_clipping(self) -> int:
        """PLOTTER_TIME_CLIPPING property
        
        plotter time clipping
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'plotter_time_clipping' and 'PLOTTER_TIME_CLIPPING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PLOTTER_TIME_CLIPPING)
        _value = cast(int, value)
        return _value

    @plotter_time_clipping.setter
    def plotter_time_clipping(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PLOTTER_TIME_CLIPPING, value)

    @property
    def PICKANDGO_PARTS(self) -> int:
        """PICKANDGO_PARTS property
        
        pick-and-go part control
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PICKANDGO_PARTS)
        _value = cast(int, value)
        return _value

    @PICKANDGO_PARTS.setter
    def PICKANDGO_PARTS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PICKANDGO_PARTS, value)

    @property
    def pickandgo_parts(self) -> int:
        """PICKANDGO_PARTS property
        
        pick-and-go part control
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'pickandgo_parts' and 'PICKANDGO_PARTS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PICKANDGO_PARTS)
        _value = cast(int, value)
        return _value

    @pickandgo_parts.setter
    def pickandgo_parts(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PICKANDGO_PARTS, value)

    @property
    def OBJECT_DTOR(self) -> ensobjlist:
        """OBJECT_DTOR property
        
        DTOR event interface for callbacks
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OBJECT_DTOR)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def object_dtor(self) -> ensobjlist:
        """OBJECT_DTOR property
        
        DTOR event interface for callbacks
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'object_dtor' and 'OBJECT_DTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OBJECT_DTOR)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def PLAYING_COMMAND_FILE(self) -> int:
        """PLAYING_COMMAND_FILE property
        
        a command is playing
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PLAYING_COMMAND_FILE)
        _value = cast(int, value)
        return _value

    @property
    def playing_command_file(self) -> int:
        """PLAYING_COMMAND_FILE property
        
        a command is playing
        
        Supported operations:
            getattr
        Datatype:
            Boolean, scalar
        
        Note: both 'playing_command_file' and 'PLAYING_COMMAND_FILE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PLAYING_COMMAND_FILE)
        _value = cast(int, value)
        return _value

    @property
    def CONNECT_TIMEOUT(self) -> int:
        """CONNECT_TIMEOUT property
        
        server connection timeout
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONNECT_TIMEOUT)
        _value = cast(int, value)
        return _value

    @CONNECT_TIMEOUT.setter
    def CONNECT_TIMEOUT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CONNECT_TIMEOUT, value)

    @property
    def connect_timeout(self) -> int:
        """CONNECT_TIMEOUT property
        
        server connection timeout
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'connect_timeout' and 'CONNECT_TIMEOUT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONNECT_TIMEOUT)
        _value = cast(int, value)
        return _value

    @connect_timeout.setter
    def connect_timeout(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CONNECT_TIMEOUT, value)

    @property
    def SLIM_TIMEOUT(self) -> int:
        """SLIM_TIMEOUT property
        
        slim idle release
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIM_TIMEOUT)
        _value = cast(int, value)
        return _value

    @SLIM_TIMEOUT.setter
    def SLIM_TIMEOUT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIM_TIMEOUT, value)

    @property
    def slim_timeout(self) -> int:
        """SLIM_TIMEOUT property
        
        slim idle release
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'slim_timeout' and 'SLIM_TIMEOUT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SLIM_TIMEOUT)
        _value = cast(int, value)
        return _value

    @slim_timeout.setter
    def slim_timeout(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SLIM_TIMEOUT, value)

    @property
    def CASELINKING(self) -> int:
        """CASELINKING property
        
        Case linking in use/Allow switch to ON
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CASELINKING)
        _value = cast(int, value)
        return _value

    @CASELINKING.setter
    def CASELINKING(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CASELINKING, value)

    @property
    def caselinking(self) -> int:
        """CASELINKING property
        
        Case linking in use/Allow switch to ON
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'caselinking' and 'CASELINKING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CASELINKING)
        _value = cast(int, value)
        return _value

    @caselinking.setter
    def caselinking(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.CASELINKING, value)

    @property
    def PROJECT_CREATION_MASK(self) -> int:
        """PROJECT_CREATION_MASK property
        
        project mask used for new objects
        
        Supported operations:
            getattr, setattr
        Datatype:
            64bit integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PROJECT_CREATION_MASK)
        _value = cast(int, value)
        return _value

    @PROJECT_CREATION_MASK.setter
    def PROJECT_CREATION_MASK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROJECT_CREATION_MASK, value)

    @property
    def project_creation_mask(self) -> int:
        """PROJECT_CREATION_MASK property
        
        project mask used for new objects
        
        Supported operations:
            getattr, setattr
        Datatype:
            64bit integer, scalar
        
        Note: both 'project_creation_mask' and 'PROJECT_CREATION_MASK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PROJECT_CREATION_MASK)
        _value = cast(int, value)
        return _value

    @project_creation_mask.setter
    def project_creation_mask(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROJECT_CREATION_MASK, value)

    @property
    def PROJECT_VISIBLE_MASK(self) -> int:
        """PROJECT_VISIBLE_MASK property
        
        currently visible project mask
        
        Supported operations:
            getattr, setattr
        Datatype:
            64bit integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PROJECT_VISIBLE_MASK)
        _value = cast(int, value)
        return _value

    @PROJECT_VISIBLE_MASK.setter
    def PROJECT_VISIBLE_MASK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROJECT_VISIBLE_MASK, value)

    @property
    def project_visible_mask(self) -> int:
        """PROJECT_VISIBLE_MASK property
        
        currently visible project mask
        
        Supported operations:
            getattr, setattr
        Datatype:
            64bit integer, scalar
        
        Note: both 'project_visible_mask' and 'PROJECT_VISIBLE_MASK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PROJECT_VISIBLE_MASK)
        _value = cast(int, value)
        return _value

    @project_visible_mask.setter
    def project_visible_mask(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.PROJECT_VISIBLE_MASK, value)

    @property
    def AXISLOCAL(self) -> int:
        """AXISLOCAL property
        
        Frame axis visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISLOCAL)
        _value = cast(int, value)
        return _value

    @AXISLOCAL.setter
    def AXISLOCAL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISLOCAL, value)

    @property
    def axislocal(self) -> int:
        """AXISLOCAL property
        
        Frame axis visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axislocal' and 'AXISLOCAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISLOCAL)
        _value = cast(int, value)
        return _value

    @axislocal.setter
    def axislocal(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISLOCAL, value)

    @property
    def AXISGLOBAL(self) -> int:
        """AXISGLOBAL property
        
        Global transform axis visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISGLOBAL)
        _value = cast(int, value)
        return _value

    @AXISGLOBAL.setter
    def AXISGLOBAL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISGLOBAL, value)

    @property
    def axisglobal(self) -> int:
        """AXISGLOBAL property
        
        Global transform axis visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisglobal' and 'AXISGLOBAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISGLOBAL)
        _value = cast(int, value)
        return _value

    @axisglobal.setter
    def axisglobal(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISGLOBAL, value)

    @property
    def AXISMODEL(self) -> int:
        """AXISMODEL property
        
        Model axis visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISMODEL)
        _value = cast(int, value)
        return _value

    @AXISMODEL.setter
    def AXISMODEL(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISMODEL, value)

    @property
    def axismodel(self) -> int:
        """AXISMODEL property
        
        Model axis visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axismodel' and 'AXISMODEL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISMODEL)
        _value = cast(int, value)
        return _value

    @axismodel.setter
    def axismodel(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISMODEL, value)

    @property
    def AXISMODEL_ANIMATE(self) -> int:
        """AXISMODEL_ANIMATE property
        
        Model axis animation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISMODEL_ANIMATE)
        _value = cast(int, value)
        return _value

    @AXISMODEL_ANIMATE.setter
    def AXISMODEL_ANIMATE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISMODEL_ANIMATE, value)

    @property
    def axismodel_animate(self) -> int:
        """AXISMODEL_ANIMATE property
        
        Model axis animation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axismodel_animate' and 'AXISMODEL_ANIMATE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISMODEL_ANIMATE)
        _value = cast(int, value)
        return _value

    @axismodel_animate.setter
    def axismodel_animate(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISMODEL_ANIMATE, value)

    @property
    def AXISMODEL_LOCATION(self) -> List[float]:
        """AXISMODEL_LOCATION property
        
        Model axis location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISMODEL_LOCATION)
        _value = cast(List[float], value)
        return _value

    @AXISMODEL_LOCATION.setter
    def AXISMODEL_LOCATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISMODEL_LOCATION, value)

    @property
    def axismodel_location(self) -> List[float]:
        """AXISMODEL_LOCATION property
        
        Model axis location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'axismodel_location' and 'AXISMODEL_LOCATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISMODEL_LOCATION)
        _value = cast(List[float], value)
        return _value

    @axismodel_location.setter
    def axismodel_location(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISMODEL_LOCATION, value)

    @property
    def PREF_DATAFILEFILTER(self) -> str:
        """PREF_DATAFILEFILTER property
        
        data file browser filter preference
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PREF_DATAFILEFILTER)
        _value = cast(str, value)
        return _value

    @PREF_DATAFILEFILTER.setter
    def PREF_DATAFILEFILTER(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PREF_DATAFILEFILTER, value)

    @property
    def pref_datafilefilter(self) -> str:
        """PREF_DATAFILEFILTER property
        
        data file browser filter preference
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'pref_datafilefilter' and 'PREF_DATAFILEFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PREF_DATAFILEFILTER)
        _value = cast(str, value)
        return _value

    @pref_datafilefilter.setter
    def pref_datafilefilter(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.PREF_DATAFILEFILTER, value)

    @property
    def VR_ANNOT_CENTER(self) -> List[float]:
        """VR_ANNOT_CENTER property
        
        vr annotation plane center
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_CENTER)
        _value = cast(List[float], value)
        return _value

    @VR_ANNOT_CENTER.setter
    def VR_ANNOT_CENTER(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_CENTER, value)

    @property
    def vr_annot_center(self) -> List[float]:
        """VR_ANNOT_CENTER property
        
        vr annotation plane center
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'vr_annot_center' and 'VR_ANNOT_CENTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_CENTER)
        _value = cast(List[float], value)
        return _value

    @vr_annot_center.setter
    def vr_annot_center(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_CENTER, value)

    @property
    def VR_ANNOT_NORMAL(self) -> List[float]:
        """VR_ANNOT_NORMAL property
        
        vr annotation plane normal
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_NORMAL)
        _value = cast(List[float], value)
        return _value

    @VR_ANNOT_NORMAL.setter
    def VR_ANNOT_NORMAL(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_NORMAL, value)

    @property
    def vr_annot_normal(self) -> List[float]:
        """VR_ANNOT_NORMAL property
        
        vr annotation plane normal
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'vr_annot_normal' and 'VR_ANNOT_NORMAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_NORMAL)
        _value = cast(List[float], value)
        return _value

    @vr_annot_normal.setter
    def vr_annot_normal(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_NORMAL, value)

    @property
    def VR_ANNOT_UP(self) -> List[float]:
        """VR_ANNOT_UP property
        
        vr annotation plane up vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_UP)
        _value = cast(List[float], value)
        return _value

    @VR_ANNOT_UP.setter
    def VR_ANNOT_UP(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_UP, value)

    @property
    def vr_annot_up(self) -> List[float]:
        """VR_ANNOT_UP property
        
        vr annotation plane up vector
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'vr_annot_up' and 'VR_ANNOT_UP' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_UP)
        _value = cast(List[float], value)
        return _value

    @vr_annot_up.setter
    def vr_annot_up(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_UP, value)

    @property
    def VR_ANNOT_SCALE(self) -> List[float]:
        """VR_ANNOT_SCALE property
        
        vr annotation plane width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_SCALE)
        _value = cast(List[float], value)
        return _value

    @VR_ANNOT_SCALE.setter
    def VR_ANNOT_SCALE(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_SCALE, value)

    @property
    def vr_annot_scale(self) -> List[float]:
        """VR_ANNOT_SCALE property
        
        vr annotation plane width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'vr_annot_scale' and 'VR_ANNOT_SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_ANNOT_SCALE)
        _value = cast(List[float], value)
        return _value

    @vr_annot_scale.setter
    def vr_annot_scale(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_ANNOT_SCALE, value)

    @property
    def VR_CAVE_SCALE(self) -> float:
        """VR_CAVE_SCALE property
        
        vr scale factor for model, in model space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_CAVE_SCALE)
        _value = cast(float, value)
        return _value

    @VR_CAVE_SCALE.setter
    def VR_CAVE_SCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_CAVE_SCALE, value)

    @property
    def vr_cave_scale(self) -> float:
        """VR_CAVE_SCALE property
        
        vr scale factor for model, in model space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'vr_cave_scale' and 'VR_CAVE_SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_CAVE_SCALE)
        _value = cast(float, value)
        return _value

    @vr_cave_scale.setter
    def vr_cave_scale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_CAVE_SCALE, value)

    @property
    def VR_CAVE_CENTER(self) -> List[float]:
        """VR_CAVE_CENTER property
        
        center of model in vr space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_CAVE_CENTER)
        _value = cast(List[float], value)
        return _value

    @VR_CAVE_CENTER.setter
    def VR_CAVE_CENTER(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_CAVE_CENTER, value)

    @property
    def vr_cave_center(self) -> List[float]:
        """VR_CAVE_CENTER property
        
        center of model in vr space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'vr_cave_center' and 'VR_CAVE_CENTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_CAVE_CENTER)
        _value = cast(List[float], value)
        return _value

    @vr_cave_center.setter
    def vr_cave_center(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_CAVE_CENTER, value)

    @property
    def VR_CAVE_DIAGONAL(self) -> float:
        """VR_CAVE_DIAGONAL property
        
        vr scale factor for model, in vr space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_CAVE_DIAGONAL)
        _value = cast(float, value)
        return _value

    @VR_CAVE_DIAGONAL.setter
    def VR_CAVE_DIAGONAL(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_CAVE_DIAGONAL, value)

    @property
    def vr_cave_diagonal(self) -> float:
        """VR_CAVE_DIAGONAL property
        
        vr scale factor for model, in vr space
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'vr_cave_diagonal' and 'VR_CAVE_DIAGONAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VR_CAVE_DIAGONAL)
        _value = cast(float, value)
        return _value

    @vr_cave_diagonal.setter
    def vr_cave_diagonal(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.VR_CAVE_DIAGONAL, value)

    @property
    def ANSYS_VERSION(self) -> int:
        """ANSYS_VERSION property
        
        ANSYS distribution version integer
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_VERSION)
        _value = cast(int, value)
        return _value

    @ANSYS_VERSION.setter
    def ANSYS_VERSION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_VERSION, value)

    @property
    def ansys_version(self) -> int:
        """ANSYS_VERSION property
        
        ANSYS distribution version integer
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ansys_version' and 'ANSYS_VERSION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_VERSION)
        _value = cast(int, value)
        return _value

    @ansys_version.setter
    def ansys_version(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_VERSION, value)

    @property
    def ANSYS_VERSION_STRING(self) -> str:
        """ANSYS_VERSION_STRING property
        
        ANSYS distribution version
        
        Supported operations:
            getattr
        Datatype:
            String, 20 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_VERSION_STRING)
        _value = cast(str, value)
        return _value

    @property
    def ansys_version_string(self) -> str:
        """ANSYS_VERSION_STRING property
        
        ANSYS distribution version
        
        Supported operations:
            getattr
        Datatype:
            String, 20 characters maximum
        
        Note: both 'ansys_version_string' and 'ANSYS_VERSION_STRING' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_VERSION_STRING)
        _value = cast(str, value)
        return _value

    @property
    def ANSYS_FLAG_BETA(self) -> int:
        """ANSYS_FLAG_BETA property
        
        ANSYS internal beta flag
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_FLAG_BETA)
        _value = cast(int, value)
        return _value

    @ANSYS_FLAG_BETA.setter
    def ANSYS_FLAG_BETA(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_FLAG_BETA, value)

    @property
    def ansys_flag_beta(self) -> int:
        """ANSYS_FLAG_BETA property
        
        ANSYS internal beta flag
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ansys_flag_beta' and 'ANSYS_FLAG_BETA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_FLAG_BETA)
        _value = cast(int, value)
        return _value

    @ansys_flag_beta.setter
    def ansys_flag_beta(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_FLAG_BETA, value)

    @property
    def ANSYS_FLAG_ALPHA(self) -> int:
        """ANSYS_FLAG_ALPHA property
        
        ANSYS internal alpha flag
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_FLAG_ALPHA)
        _value = cast(int, value)
        return _value

    @ANSYS_FLAG_ALPHA.setter
    def ANSYS_FLAG_ALPHA(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_FLAG_ALPHA, value)

    @property
    def ansys_flag_alpha(self) -> int:
        """ANSYS_FLAG_ALPHA property
        
        ANSYS internal alpha flag
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ansys_flag_alpha' and 'ANSYS_FLAG_ALPHA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_FLAG_ALPHA)
        _value = cast(int, value)
        return _value

    @ansys_flag_alpha.setter
    def ansys_flag_alpha(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_FLAG_ALPHA, value)

    @property
    def ANSYS_DRAW_LOGO(self) -> int:
        """ANSYS_DRAW_LOGO property
        
        ANSYS logo display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_DRAW_LOGO)
        _value = cast(int, value)
        return _value

    @ANSYS_DRAW_LOGO.setter
    def ANSYS_DRAW_LOGO(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_DRAW_LOGO, value)

    @property
    def ansys_draw_logo(self) -> int:
        """ANSYS_DRAW_LOGO property
        
        ANSYS logo display
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'ansys_draw_logo' and 'ANSYS_DRAW_LOGO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ANSYS_DRAW_LOGO)
        _value = cast(int, value)
        return _value

    @ansys_draw_logo.setter
    def ansys_draw_logo(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.ANSYS_DRAW_LOGO, value)

    @property
    def STATES(self) -> ensobjlist['ENS_STATE']:
        """STATES property
        
        attribute states
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.STATES)
        _value = cast(ensobjlist['ENS_STATE'], value)
        return _value

    @property
    def states(self) -> ensobjlist['ENS_STATE']:
        """STATES property
        
        attribute states
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'states' and 'STATES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.STATES)
        _value = cast(ensobjlist['ENS_STATE'], value)
        return _value

    @property
    def SYNTHETIC_MENU(self) -> object:
        """SYNTHETIC_MENU property
        
        synthetic menu event information
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYNTHETIC_MENU)
        _value = cast(object, value)
        return _value

    @SYNTHETIC_MENU.setter
    def SYNTHETIC_MENU(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.SYNTHETIC_MENU, value)

    @property
    def synthetic_menu(self) -> object:
        """SYNTHETIC_MENU property
        
        synthetic menu event information
        
        Supported operations:
            getattr, setattr
        Datatype:
            EnSight Object, scalar
        
        Note: both 'synthetic_menu' and 'SYNTHETIC_MENU' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYNTHETIC_MENU)
        _value = cast(object, value)
        return _value

    @synthetic_menu.setter
    def synthetic_menu(self, value: object) -> None:
        self.setattr(self._session.ensight.objs.enums.SYNTHETIC_MENU, value)

    @property
    def SOLUTIONTIME_MONITOR(self) -> int:
        """SOLUTIONTIME_MONITOR property
        
        Monitor for new timesteps
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MFNTS_OFF - Do not monitor for new timesteps
            * ensight.objs.enums.MFNTS_JUMP_TO_END - Jump to new timestep
            * ensight.objs.enums.MFNTS_STAY_AT_CURRENT - Stay at current timestep
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SOLUTIONTIME_MONITOR)
        _value = cast(int, value)
        return _value

    @SOLUTIONTIME_MONITOR.setter
    def SOLUTIONTIME_MONITOR(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SOLUTIONTIME_MONITOR, value)

    @property
    def solutiontime_monitor(self) -> int:
        """SOLUTIONTIME_MONITOR property
        
        Monitor for new timesteps
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.MFNTS_OFF - Do not monitor for new timesteps
            * ensight.objs.enums.MFNTS_JUMP_TO_END - Jump to new timestep
            * ensight.objs.enums.MFNTS_STAY_AT_CURRENT - Stay at current timestep
        
        Note: both 'solutiontime_monitor' and 'SOLUTIONTIME_MONITOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SOLUTIONTIME_MONITOR)
        _value = cast(int, value)
        return _value

    @solutiontime_monitor.setter
    def solutiontime_monitor(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SOLUTIONTIME_MONITOR, value)

    @property
    def BOUNDS(self) -> int:
        """BOUNDS property
        
        Bounds visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOUNDS)
        _value = cast(int, value)
        return _value

    @BOUNDS.setter
    def BOUNDS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BOUNDS, value)

    @property
    def bounds(self) -> int:
        """BOUNDS property
        
        Bounds visibility
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'bounds' and 'BOUNDS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOUNDS)
        _value = cast(int, value)
        return _value

    @bounds.setter
    def bounds(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BOUNDS, value)

    @property
    def LIGHTSOURCES(self) -> ensobjlist:
        """LIGHTSOURCES property
        
        lightsources
        
        Supported operations:
            getattr
        Datatype:
            Object, 8 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSOURCES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def lightsources(self) -> ensobjlist:
        """LIGHTSOURCES property
        
        lightsources
        
        Supported operations:
            getattr
        Datatype:
            Object, 8 element array
        
        Note: both 'lightsources' and 'LIGHTSOURCES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHTSOURCES)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def SCENE(self) -> ensobjlist['ENS_SCENE']:
        """SCENE property
        
        scene
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCENE)
        _value = cast(ensobjlist['ENS_SCENE'], value)
        return _value

    @property
    def scene(self) -> ensobjlist['ENS_SCENE']:
        """SCENE property
        
        scene
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'scene' and 'SCENE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCENE)
        _value = cast(ensobjlist['ENS_SCENE'], value)
        return _value

    @property
    def CAMERAS(self) -> ensobjlist:
        """CAMERAS property
        
        cameras
        
        Supported operations:
            getattr
        Datatype:
            Object, 8 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CAMERAS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def cameras(self) -> ensobjlist:
        """CAMERAS property
        
        cameras
        
        Supported operations:
            getattr
        Datatype:
            Object, 8 element array
        
        Note: both 'cameras' and 'CAMERAS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CAMERAS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def OBJECTFOCUS(self) -> ensobjlist:
        """OBJECTFOCUS property
        
        global object focus tracker
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.OBJECTFOCUS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def objectfocus(self) -> ensobjlist:
        """OBJECTFOCUS property
        
        global object focus tracker
        
        Supported operations:
            getattr
        Datatype:
            Object, scalar
        
        Note: both 'objectfocus' and 'OBJECTFOCUS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.OBJECTFOCUS)
        _value = cast(ensobjlist, value)
        return _value

    @property
    def LINEWIDTH(self) -> float:
        """LINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(float, value)
        return _value

    @LINEWIDTH.setter
    def LINEWIDTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def linewidth(self) -> float:
        """LINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'linewidth' and 'LINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINEWIDTH)
        _value = cast(float, value)
        return _value

    @linewidth.setter
    def linewidth(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LINEWIDTH, value)

    @property
    def STARTTIME(self) -> float:
        """STARTTIME property
        
        Start time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.STARTTIME)
        _value = cast(float, value)
        return _value

    @STARTTIME.setter
    def STARTTIME(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.STARTTIME, value)

    @property
    def starttime(self) -> float:
        """STARTTIME property
        
        Start time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'starttime' and 'STARTTIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.STARTTIME)
        _value = cast(float, value)
        return _value

    @starttime.setter
    def starttime(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.STARTTIME, value)

    @property
    def DELTATIME(self) -> float:
        """DELTATIME property
        
        Tracer delta(speed)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DELTATIME)
        _value = cast(float, value)
        return _value

    @DELTATIME.setter
    def DELTATIME(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DELTATIME, value)

    @property
    def deltatime(self) -> float:
        """DELTATIME property
        
        Tracer delta(speed)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'deltatime' and 'DELTATIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DELTATIME)
        _value = cast(float, value)
        return _value

    @deltatime.setter
    def deltatime(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.DELTATIME, value)

    @property
    def COLORBY(self) -> int:
        """COLORBY property
        
        Color by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ATRACE_COLBY_CONST - constant_color
            * ensight.objs.enums.ATRACE_COLBY_CALC - calculated_color
        
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORBY)
        _value = cast(int, value)
        return _value

    @COLORBY.setter
    def COLORBY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORBY, value)

    @property
    def colorby(self) -> int:
        """COLORBY property
        
        Color by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ATRACE_COLBY_CONST - constant_color
            * ensight.objs.enums.ATRACE_COLBY_CALC - calculated_color
        
        Note: both 'colorby' and 'COLORBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.COLORBY)
        _value = cast(int, value)
        return _value

    @colorby.setter
    def colorby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.COLORBY, value)

    @property
    def RGB(self) -> List[float]:
        """RGB property
        
        Rgb
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.RGB)
        _value = cast(List[float], value)
        return _value

    @RGB.setter
    def RGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RGB, value)

    @property
    def rgb(self) -> List[float]:
        """RGB property
        
        Rgb
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'rgb' and 'RGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.RGB)
        _value = cast(List[float], value)
        return _value

    @rgb.setter
    def rgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.RGB, value)

    @property
    def SETMAXTIME(self) -> int:
        """SETMAXTIME property
        
        Set max time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SETMAXTIME)
        _value = cast(int, value)
        return _value

    @SETMAXTIME.setter
    def SETMAXTIME(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SETMAXTIME, value)

    @property
    def setmaxtime(self) -> int:
        """SETMAXTIME property
        
        Set max time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'setmaxtime' and 'SETMAXTIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SETMAXTIME)
        _value = cast(int, value)
        return _value

    @setmaxtime.setter
    def setmaxtime(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SETMAXTIME, value)

    @property
    def SYNCTOTRANSIENT(self) -> int:
        """SYNCTOTRANSIENT property
        
        Sync to transient
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SYNCTOTRANSIENT)
        _value = cast(int, value)
        return _value

    @SYNCTOTRANSIENT.setter
    def SYNCTOTRANSIENT(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYNCTOTRANSIENT, value)

    @property
    def synctotransient(self) -> int:
        """SYNCTOTRANSIENT property
        
        Sync to transient
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'synctotransient' and 'SYNCTOTRANSIENT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SYNCTOTRANSIENT)
        _value = cast(int, value)
        return _value

    @synctotransient.setter
    def synctotransient(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SYNCTOTRANSIENT, value)

    @property
    def MAXTIME(self) -> float:
        """MAXTIME property
        
        Max time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MAXTIME)
        _value = cast(float, value)
        return _value

    @MAXTIME.setter
    def MAXTIME(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MAXTIME, value)

    @property
    def maxtime(self) -> float:
        """MAXTIME property
        
        Max time
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'maxtime' and 'MAXTIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MAXTIME)
        _value = cast(float, value)
        return _value

    @maxtime.setter
    def maxtime(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.MAXTIME, value)

    @property
    def MULTIPLEPULSES(self) -> int:
        """MULTIPLEPULSES property
        
        Multiple pulses
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.MULTIPLEPULSES)
        _value = cast(int, value)
        return _value

    @MULTIPLEPULSES.setter
    def MULTIPLEPULSES(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MULTIPLEPULSES, value)

    @property
    def multiplepulses(self) -> int:
        """MULTIPLEPULSES property
        
        Multiple pulses
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'multiplepulses' and 'MULTIPLEPULSES' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.MULTIPLEPULSES)
        _value = cast(int, value)
        return _value

    @multiplepulses.setter
    def multiplepulses(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.MULTIPLEPULSES, value)

    @property
    def PULSEINTERVAL(self) -> float:
        """PULSEINTERVAL property
        
        Pulse interval
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PULSEINTERVAL)
        _value = cast(float, value)
        return _value

    @PULSEINTERVAL.setter
    def PULSEINTERVAL(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PULSEINTERVAL, value)

    @property
    def pulseinterval(self) -> float:
        """PULSEINTERVAL property
        
        Pulse interval
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'pulseinterval' and 'PULSEINTERVAL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PULSEINTERVAL)
        _value = cast(float, value)
        return _value

    @pulseinterval.setter
    def pulseinterval(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PULSEINTERVAL, value)

    @property
    def PARTICLETIME(self) -> float:
        """PARTICLETIME property
        
        Tracer time(length)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTICLETIME)
        _value = cast(float, value)
        return _value

    @PARTICLETIME.setter
    def PARTICLETIME(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTICLETIME, value)

    @property
    def particletime(self) -> float:
        """PARTICLETIME property
        
        Tracer time(length)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'particletime' and 'PARTICLETIME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PARTICLETIME)
        _value = cast(float, value)
        return _value

    @particletime.setter
    def particletime(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PARTICLETIME, value)

    @property
    def HEADTYPE(self) -> int:
        """HEADTYPE property
        
        Head type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ATRACE_HEAD_NONE - none
            * ensight.objs.enums.ATRACE_HEAD_SPHERE - sphere
            * ensight.objs.enums.ATRACE_HEAD_ARROW - arrow
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADTYPE)
        _value = cast(int, value)
        return _value

    @HEADTYPE.setter
    def HEADTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADTYPE, value)

    @property
    def headtype(self) -> int:
        """HEADTYPE property
        
        Head type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ATRACE_HEAD_NONE - none
            * ensight.objs.enums.ATRACE_HEAD_SPHERE - sphere
            * ensight.objs.enums.ATRACE_HEAD_ARROW - arrow
        
        Note: both 'headtype' and 'HEADTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADTYPE)
        _value = cast(int, value)
        return _value

    @headtype.setter
    def headtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADTYPE, value)

    @property
    def HEADDETAIL(self) -> float:
        """HEADDETAIL property
        
        Head detail
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 10.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADDETAIL)
        _value = cast(float, value)
        return _value

    @HEADDETAIL.setter
    def HEADDETAIL(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADDETAIL, value)

    @property
    def headdetail(self) -> float:
        """HEADDETAIL property
        
        Head detail
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 10.0]
        
        Note: both 'headdetail' and 'HEADDETAIL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADDETAIL)
        _value = cast(float, value)
        return _value

    @headdetail.setter
    def headdetail(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADDETAIL, value)

    @property
    def HEADSCALE(self) -> float:
        """HEADSCALE property
        
        Head scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADSCALE)
        _value = cast(float, value)
        return _value

    @HEADSCALE.setter
    def HEADSCALE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADSCALE, value)

    @property
    def headscale(self) -> float:
        """HEADSCALE property
        
        Head scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            (0.0, inf]
        
        Note: both 'headscale' and 'HEADSCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADSCALE)
        _value = cast(float, value)
        return _value

    @headscale.setter
    def headscale(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADSCALE, value)

    @property
    def HEADSIZEBY(self) -> int:
        """HEADSIZEBY property
        
        Head size by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ATRACE_SIZE_CONST - constant
            * ensight.objs.enums.ATRACE_SIZE_SCALAR - scalar
            * ensight.objs.enums.ATRACE_SIZE_VEC_MAG - vector_mag
            * ensight.objs.enums.ATRACE_SIZE_VEC_X - vector_xcomp
            * ensight.objs.enums.ATRACE_SIZE_VEC_Y - vector_ycomp
            * ensight.objs.enums.ATRACE_SIZE_VEC_Z - vector_zcomp
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADSIZEBY)
        _value = cast(int, value)
        return _value

    @HEADSIZEBY.setter
    def HEADSIZEBY(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADSIZEBY, value)

    @property
    def headsizeby(self) -> int:
        """HEADSIZEBY property
        
        Head size by
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.ATRACE_SIZE_CONST - constant
            * ensight.objs.enums.ATRACE_SIZE_SCALAR - scalar
            * ensight.objs.enums.ATRACE_SIZE_VEC_MAG - vector_mag
            * ensight.objs.enums.ATRACE_SIZE_VEC_X - vector_xcomp
            * ensight.objs.enums.ATRACE_SIZE_VEC_Y - vector_ycomp
            * ensight.objs.enums.ATRACE_SIZE_VEC_Z - vector_zcomp
        
        Note: both 'headsizeby' and 'HEADSIZEBY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADSIZEBY)
        _value = cast(int, value)
        return _value

    @headsizeby.setter
    def headsizeby(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADSIZEBY, value)

    @property
    def HEADVARIABLE(self) -> ensobjlist['ENS_VAR']:
        """HEADVARIABLE property
        
        Head variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @HEADVARIABLE.setter
    def HEADVARIABLE(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADVARIABLE, value)

    @property
    def headvariable(self) -> ensobjlist['ENS_VAR']:
        """HEADVARIABLE property
        
        Head variable
        
        Supported operations:
            getattr, setattr
        Datatype:
            ENS_VAR Object, scalar
        Variable type filters:
            * Scalar
            * Nodal
            * Element
        
        Note: both 'headvariable' and 'HEADVARIABLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HEADVARIABLE)
        _value = cast(ensobjlist['ENS_VAR'], value)
        return _value

    @headvariable.setter
    def headvariable(self, value: ensobjlist['ENS_VAR']) -> None:
        self.setattr(self._session.ensight.objs.enums.HEADVARIABLE, value)

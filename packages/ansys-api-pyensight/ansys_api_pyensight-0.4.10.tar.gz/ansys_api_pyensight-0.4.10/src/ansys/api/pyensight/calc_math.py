"""ens_math module"""
"""The ens_math module provides an interface to the EnSight math functions"""

try:
    import ensight
except ImportError:
    pass
from typing import TYPE_CHECKING, Union, List, Optional
from ansys.api.pyensight.ens_var import ENS_VAR
from ansys.pyensight.core.utils.parts import convert_part
if TYPE_CHECKING:
    from ansys.api.pyensight import ensight_api

    from ansys.api.pyensight.ens_part import ENS_PART

class ens_math:
    def __init__(self, ensight: Union["ensight_api.ensight", "ensight"]):
        self._ensight = ensight
        self._func_counter = {}

    def abs(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise absolute value of the parameter.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ABS` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ABS"):
                self._func_counter["ABS"] = 0
            else:
                self._func_counter["ABS"] += 1
            counter = self._func_counter["ABS"]
            output_varname = f"ABS_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ABS({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ABS()')

    def acos(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise arccosine of the parameter in radians.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ACOS` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ACOS"):
                self._func_counter["ACOS"] = 0
            else:
                self._func_counter["ACOS"] += 1
            counter = self._func_counter["ACOS"]
            output_varname = f"ACOS_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ACOS({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ACOS()')

    def asin(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise arcsine of the parameter in radians.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ASIN` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ASIN"):
                self._func_counter["ASIN"] = 0
            else:
                self._func_counter["ASIN"] += 1
            counter = self._func_counter["ASIN"]
            output_varname = f"ASIN_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ASIN({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ASIN()')

    def atan(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise arctangent of the parameter in radians.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ATAN` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ATAN"):
                self._func_counter["ATAN"] = 0
            else:
                self._func_counter["ATAN"] += 1
            counter = self._func_counter["ATAN"]
            output_varname = f"ATAN_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ATAN({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ATAN()')

    def atan2(self, dy: Union['float', 'ENS_VAR', str, int], dx: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise arctangent of the dx/dy parameters in radians.
            dy:
                a constant value, or a scalar, vector or constant variable
            dx:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ATAN2` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['dy', 'dx']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ATAN2"):
                self._func_counter["ATAN2"] = 0
            else:
                self._func_counter["ATAN2"] += 1
            counter = self._func_counter["ATAN2"]
            output_varname = f"ATAN2_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ATAN2({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ATAN2()')

    def cos(self, angle: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise cosine of the angle.  The angle is expressed in radians.
            angle:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`COS` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['angle']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("COS"):
                self._func_counter["COS"] = 0
            else:
                self._func_counter["COS"] += 1
            counter = self._func_counter["COS"]
            output_varname = f"COS_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'COS({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=COS()')

    def cross(self, vector1: Union['ENS_VAR', str, int], vector2: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes the cross product of two vector parameters.
            vector1:
                vector variable
            vector2:
                vector variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CROSS` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector1', 'vector2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CROSS"):
                self._func_counter["CROSS"] = 0
            else:
                self._func_counter["CROSS"] += 1
            counter = self._func_counter["CROSS"]
            output_varname = f"CROSS_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CROSS({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CROSS()')

    def dot(self, vector1: Union['ENS_VAR', str, int], vector2: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes the dot product of two vector parameters.
            vector1:
                vector variable
            vector2:
                vector variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`DOT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector1', 'vector2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("DOT"):
                self._func_counter["DOT"] = 0
            else:
                self._func_counter["DOT"] += 1
            counter = self._func_counter["DOT"]
            output_varname = f"DOT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'DOT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=DOT()')

    def exp(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise raising of e to the specified parameter.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`EXP` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("EXP"):
                self._func_counter["EXP"] = 0
            else:
                self._func_counter["EXP"] += 1
            counter = self._func_counter["EXP"]
            output_varname = f"EXP_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'EXP({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=EXP()')

    def gt(self, value1: Union['float', 'ENS_VAR', str, int], value2: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Selects the greater of two parameter values.
            value1:
                a constant value, or a scalar, vector or constant variable
            value2:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`GT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value1', 'value2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("GT"):
                self._func_counter["GT"] = 0
            else:
                self._func_counter["GT"] += 1
            counter = self._func_counter["GT"]
            output_varname = f"GT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'GT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=GT()')

    def int(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise truncation of the parameter.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`INT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("INT"):
                self._func_counter["INT"] = 0
            else:
                self._func_counter["INT"] += 1
            counter = self._func_counter["INT"]
            output_varname = f"INT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'INT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=INT()')

    def log(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise logarithm (base e) of the parameter.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`LOG` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("LOG"):
                self._func_counter["LOG"] = 0
            else:
                self._func_counter["LOG"] += 1
            counter = self._func_counter["LOG"]
            output_varname = f"LOG_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'LOG({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=LOG()')

    def log10(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise logarithm (base 10) of the parameter.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`LOG10` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("LOG10"):
                self._func_counter["LOG10"] = 0
            else:
                self._func_counter["LOG10"] += 1
            counter = self._func_counter["LOG10"]
            output_varname = f"LOG10_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'LOG10({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=LOG10()')

    def lt(self, value1: Union['float', 'ENS_VAR', str, int], value2: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Selects the lesser of two parameter values.
            value1:
                a constant value, or a scalar, vector or constant variable
            value2:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`LT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value1', 'value2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("LT"):
                self._func_counter["LT"] = 0
            else:
                self._func_counter["LT"] += 1
            counter = self._func_counter["LT"]
            output_varname = f"LT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'LT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=LT()')

    def rnd(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise rounding of the parameter to the nearest integer.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`RND` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("RND"):
                self._func_counter["RND"] = 0
            else:
                self._func_counter["RND"] += 1
            counter = self._func_counter["RND"]
            output_varname = f"RND_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'RND({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=RND()')

    def mod(self, value1: Union['float', 'ENS_VAR', str, int], value2: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the remainder after using of integer division to divide the first value by the second. Both input values are first converted to integers.
            value1:
                a constant value or a scalar or constant variable
            value2:
                a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MOD` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value1', 'value2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("MOD"):
                self._func_counter["MOD"] = 0
            else:
                self._func_counter["MOD"] += 1
            counter = self._func_counter["MOD"]
            output_varname = f"MOD_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MOD({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MOD()')

    def sin(self, angle: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise sine of the angle.  The angle is expressed in radians.
            angle:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`SIN` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['angle']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("SIN"):
                self._func_counter["SIN"] = 0
            else:
                self._func_counter["SIN"] += 1
            counter = self._func_counter["SIN"]
            output_varname = f"SIN_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'SIN({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=SIN()')

    def sqrt(self, value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise square root of the parameter.
            value:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`SQRT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("SQRT"):
                self._func_counter["SQRT"] = 0
            else:
                self._func_counter["SQRT"] += 1
            counter = self._func_counter["SQRT"]
            output_varname = f"SQRT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'SQRT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=SQRT()')

    def tan(self, angle: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the component-wise tangent of the angle.  The angle is expressed in radians.
            angle:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TAN` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['angle']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TAN"):
                self._func_counter["TAN"] = 0
            else:
                self._func_counter["TAN"] += 1
            counter = self._func_counter["TAN"]
            output_varname = f"TAN_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TAN({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TAN()')

    def cdf_norm(self, v: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the cumulative normal distribution function evaluated at v.
            v:
                a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CDF_NORM` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CDF_NORM"):
                self._func_counter["CDF_NORM"] = 0
            else:
                self._func_counter["CDF_NORM"] += 1
            counter = self._func_counter["CDF_NORM"]
            output_varname = f"CDF_NORM_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CDF_NORM({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CDF_NORM()')

    def pdf_norm(self, v: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the normal probability density function evaluated at v.
            v:
                a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PDF_NORM` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PDF_NORM"):
                self._func_counter["PDF_NORM"] = 0
            else:
                self._func_counter["PDF_NORM"] += 1
            counter = self._func_counter["PDF_NORM"]
            output_varname = f"PDF_NORM_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PDF_NORM({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PDF_NORM()')

    def cdf_t(self, v: Union['float', 'ENS_VAR', str, int], k: Union['int', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the cumulative Student's T distribution function for the value v with k degrees of freedom.
            v:
                a constant value or a scalar or constant variable
            k:
                degrees of freedom: a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CDF_T` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v', 'k']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CDF_T"):
                self._func_counter["CDF_T"] = 0
            else:
                self._func_counter["CDF_T"] += 1
            counter = self._func_counter["CDF_T"]
            output_varname = f"CDF_T_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CDF_T({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CDF_T()')

    def pdf_t(self, v: Union['float', 'ENS_VAR', str, int], k: Union['int', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the Student's T probability density function for the value v with k degrees of freedom.
            v:
                a constant value or a scalar or constant variable
            k:
                degrees of freedom: a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PDF_T` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v', 'k']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PDF_T"):
                self._func_counter["PDF_T"] = 0
            else:
                self._func_counter["PDF_T"] += 1
            counter = self._func_counter["PDF_T"]
            output_varname = f"PDF_T_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PDF_T({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PDF_T()')

    def cdf_f(self, v: Union['float', 'ENS_VAR', str, int], j: Union['int', 'ENS_VAR', str, int], k: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the cumulative F distribution function for the value v with j and k degrees of freedom.
            v:
                a constant value or a scalar or constant variable
            j:
                degrees of freedom: a constant value or a scalar or constant variable
            k:
                degrees of freedom: a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CDF_F` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v', 'j', 'k']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CDF_F"):
                self._func_counter["CDF_F"] = 0
            else:
                self._func_counter["CDF_F"] += 1
            counter = self._func_counter["CDF_F"]
            output_varname = f"CDF_F_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CDF_F({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CDF_F()')

    def pdf_f(self, v: Union['float', 'ENS_VAR', str, int], j: Union['int', 'ENS_VAR', str, int], k: Union['int', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the F probability density function for the value v with j and k degrees of freedom.
            v:
                a constant value or a scalar or constant variable
            j:
                degrees of freedom: a constant value or a scalar or constant variable
            k:
                degrees of freedom: a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PDF_F` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v', 'j', 'k']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PDF_F"):
                self._func_counter["PDF_F"] = 0
            else:
                self._func_counter["PDF_F"] += 1
            counter = self._func_counter["PDF_F"]
            output_varname = f"PDF_F_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PDF_F({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PDF_F()')

    def cdf_chisqu(self, v: Union['float', 'ENS_VAR', str, int], k: Union['int', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the cumulative Chi-Squared distribution function for v with k degrees of freedom.
            v:
                a constant value or a scalar or constant variable
            k:
                degrees of freedom: a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CDF_CHISQU` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v', 'k']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CDF_CHISQU"):
                self._func_counter["CDF_CHISQU"] = 0
            else:
                self._func_counter["CDF_CHISQU"] += 1
            counter = self._func_counter["CDF_CHISQU"]
            output_varname = f"CDF_CHISQU_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CDF_CHISQU({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CDF_CHISQU()')

    def pdf_chisqu(self, v: Union['float', 'ENS_VAR', str, int], k: Union['int', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'float':
        """Computes the Chi-Squared probability density function for v with k degrees of freedom.
            v:
                a constant value or a scalar or constant variable
            k:
                degrees of freedom: a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PDF_CHISQU` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['v', 'k']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PDF_CHISQU"):
                self._func_counter["PDF_CHISQU"] = 0
            else:
                self._func_counter["PDF_CHISQU"] += 1
            counter = self._func_counter["PDF_CHISQU"]
            output_varname = f"PDF_CHISQU_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PDF_CHISQU({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PDF_CHISQU()')

    def if_cmp(self, value1: Union['float', 'ENS_VAR', str, int], value2: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compares two parameters and returns -1, 0 or 1 if value1 is less than, equal to or greater than value2 respectively.
            value1:
                a constant value or a scalar or constant variable
            value2:
                a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IF_CMP` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value1', 'value2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("IF_CMP"):
                self._func_counter["IF_CMP"] = 0
            else:
                self._func_counter["IF_CMP"] += 1
            counter = self._func_counter["IF_CMP"]
            output_varname = f"IF_CMP_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IF_CMP({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IF_CMP()')

    def if_lt(self, value1: Union['float', 'ENS_VAR', str, int], value2: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compares two parameters and returns 1 if value1 is less than value2, otherwise it returns 0.
            value1:
                a constant value, or a scalar, vector or constant variable
            value2:
                a constant value, or a scalar, vector or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IF_LT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value1', 'value2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("IF_LT"):
                self._func_counter["IF_LT"] = 0
            else:
                self._func_counter["IF_LT"] += 1
            counter = self._func_counter["IF_LT"]
            output_varname = f"IF_LT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IF_LT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IF_LT()')

    def if_gt(self, value1: Union['float', 'ENS_VAR', str, int], value2: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compares two parameters and returns 1 if value1 is greater than value2, otherwise it returns 0.
            value1:
                a constant value or a scalar or constant variable
            value2:
                a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IF_GT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value1', 'value2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("IF_GT"):
                self._func_counter["IF_GT"] = 0
            else:
                self._func_counter["IF_GT"] += 1
            counter = self._func_counter["IF_GT"]
            output_varname = f"IF_GT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IF_GT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IF_GT()')

    def if_eq(self, value1: Union['float', 'ENS_VAR', str, int], value2: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compares two parameters and returns 1 if value1 is equal to value2, otherwise it returns 0.
            value1:
                a constant value or a scalar or constant variable
            value2:
                a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IF_EQ` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['value1', 'value2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("IF_EQ"):
                self._func_counter["IF_EQ"] = 0
            else:
                self._func_counter["IF_EQ"] += 1
            counter = self._func_counter["IF_EQ"]
            output_varname = f"IF_EQ_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IF_EQ({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IF_EQ()')

    def pi(self, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """The mathematical constant value PI.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PI` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in []:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PI"):
                self._func_counter["PI"] = 0
            else:
                self._func_counter["PI"] += 1
            counter = self._func_counter["PI"]
            output_varname = f"PI_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PI({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PI()')

    def undefined(self, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """The EnSight undefined variable value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`UNDEFINED` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in []:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("UNDEFINED"):
                self._func_counter["UNDEFINED"] = 0
            else:
                self._func_counter["UNDEFINED"] += 1
            counter = self._func_counter["UNDEFINED"]
            output_varname = f"UNDEFINED_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'UNDEFINED({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=UNDEFINED()')

    def lookup(self, table: Union['float', 'ENS_VAR', str, int], value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Interpolates a value in a specific client specified lookup table.
            table:
                a constant value or a scalar or constant variable
            value:
                a constant value or a scalar or constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`LOOKUP` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['table', 'value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("LOOKUP"):
                self._func_counter["LOOKUP"] = 0
            else:
                self._func_counter["LOOKUP"] += 1
            counter = self._func_counter["LOOKUP"]
            output_varname = f"LOOKUP_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'LOOKUP({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=LOOKUP()')



ens_math.abs.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'ABS', 'dimensions': 'a'}
ens_math.acos.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'ACOS', 'dimensions': 'D'}
ens_math.asin.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'ASIN', 'dimensions': 'D'}
ens_math.atan.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'ATAN', 'dimensions': 'D'}
ens_math.atan2.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'ATAN2', 'dimensions': 'D'}
ens_math.cos.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'COS', 'dimensions': '/'}
ens_math.cross.meta = {'class': ['Math'], 'vartype': [], 'name': 'CROSS', 'dimensions': 'ab'}
ens_math.dot.meta = {'class': ['Math'], 'vartype': [], 'name': 'DOT', 'dimensions': 'ab'}
ens_math.exp.meta = {'class': ['Math'], 'vartype': [], 'name': 'EXP', 'dimensions': 'a'}
ens_math.gt.meta = {'class': ['Math', 'Logical'], 'vartype': [], 'name': 'GT', 'dimensions': 'a'}
ens_math.int.meta = {'class': ['Math'], 'vartype': [], 'name': 'INT', 'dimensions': 'a'}
ens_math.log.meta = {'class': ['Math'], 'vartype': [], 'name': 'LOG', 'dimensions': 'a'}
ens_math.log10.meta = {'class': ['Math'], 'vartype': [], 'name': 'LOG10', 'dimensions': 'a'}
ens_math.lt.meta = {'class': ['Math', 'Logical'], 'vartype': [], 'name': 'LT', 'dimensions': 'a'}
ens_math.rnd.meta = {'class': ['Math'], 'vartype': [], 'name': 'RND', 'dimensions': 'a'}
ens_math.mod.meta = {'class': ['Math'], 'vartype': [], 'name': 'MOD', 'dimensions': 'a/b'}
ens_math.sin.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'SIN', 'dimensions': '/'}
ens_math.sqrt.meta = {'class': ['Math'], 'vartype': [], 'name': 'SQRT', 'dimensions': '/'}
ens_math.tan.meta = {'class': ['Math', 'Trigonometry'], 'vartype': [], 'name': 'TAN', 'dimensions': '/'}
ens_math.cdf_norm.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'CDF_NORM', 'dimensions': '/'}
ens_math.pdf_norm.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'PDF_NORM', 'dimensions': '/'}
ens_math.cdf_t.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'CDF_T', 'dimensions': '/'}
ens_math.pdf_t.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'PDF_T', 'dimensions': '/'}
ens_math.cdf_f.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'CDF_F', 'dimensions': '/'}
ens_math.pdf_f.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'PDF_F', 'dimensions': '/'}
ens_math.cdf_chisqu.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'CDF_CHISQU', 'dimensions': '/'}
ens_math.pdf_chisqu.meta = {'class': ['Math', 'Statistics'], 'vartype': [], 'name': 'PDF_CHISQU', 'dimensions': '/'}
ens_math.if_cmp.meta = {'class': ['Math', 'Logical'], 'vartype': [], 'name': 'IF_CMP', 'dimensions': '/'}
ens_math.if_lt.meta = {'class': ['Math', 'Logical'], 'vartype': [], 'name': 'IF_LT', 'dimensions': '/'}
ens_math.if_gt.meta = {'class': ['Math', 'Logical'], 'vartype': [], 'name': 'IF_GT', 'dimensions': '/'}
ens_math.if_eq.meta = {'class': ['Math', 'Logical'], 'vartype': [], 'name': 'IF_EQ', 'dimensions': '/'}
ens_math.pi.meta = {'class': ['Math'], 'vartype': [], 'name': 'PI', 'dimensions': '/'}
ens_math.undefined.meta = {'class': ['Math'], 'vartype': [], 'name': 'UNDEFINED', 'dimensions': '/'}
ens_math.lookup.meta = {'class': ['Math'], 'vartype': [], 'name': 'LOOKUP', 'dimensions': '/'}

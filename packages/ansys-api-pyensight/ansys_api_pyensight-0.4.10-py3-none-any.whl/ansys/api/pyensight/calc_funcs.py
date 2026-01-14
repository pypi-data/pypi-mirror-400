"""ens_calculator module"""
"""The ens_calculator module provides an interface to the EnSight calculator functions"""

try:
    import ensight
except ImportError:
    pass
from typing import TYPE_CHECKING, Union, List, Optional
from ansys.api.pyensight.ens_var import ENS_VAR
from ansys.api.pyensight.calc_math import ens_math
from ansys.pyensight.core.utils.parts import convert_part
if TYPE_CHECKING:
    from ansys.api.pyensight import ensight_api

    from ansys.api.pyensight.ens_part import ENS_PART

class ens_calculator:
    def __init__(self, ensight: Union["ensight_api.ensight", "ensight"]):
        self._ensight = ensight
        self.math = ens_math(self._ensight)
        self._func_counter = {}

    def area(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the sum of the area of the specified parts plus the surface area if any 3D elements exist.

        Args:
            source_parts:
                Any part(s) or a part number.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Area` for function details.
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
            if not self._func_counter.get("Area"):
                self._func_counter["Area"] = 0
            else:
                self._func_counter["Area"] += 1
            counter = self._func_counter["Area"]
            output_varname = f"Area_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Area({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Area()')

    def bl_agradofvelmag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the gradient of the magnitude of the specified velocity variable on the specified boundary part(s)

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_aGradOfVelMag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_aGradOfVelMag"):
                self._func_counter["BL_aGradOfVelMag"] = 0
            else:
                self._func_counter["BL_aGradOfVelMag"] += 1
            counter = self._func_counter["BL_aGradOfVelMag"]
            output_varname = f"BL_aGradOfVelMag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_aGradOfVelMag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_aGradOfVelMag()')

    def bl_cfedge(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], viscosity: Union['float', 'ENS_VAR', str, int], ymax: float, flow_dir_comp: int = 0, opt_for_a_gradient_of_velo_mag: Optional[Union['ENS_VAR', str, int]] = None, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the edge skin-friction coefficient

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            viscosity:
                A viscosity variable or a value.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            flow_dir_comp:
                Enter flow direction: 0=Tangent to surface, or this Tangent flow's 1=Streamwise or 2=Crosswise component.
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_CfEdge` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'density', 'viscosity', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_CfEdge"):
                self._func_counter["BL_CfEdge"] = 0
            else:
                self._func_counter["BL_CfEdge"] += 1
            counter = self._func_counter["BL_CfEdge"]
            output_varname = f"BL_CfEdge_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_CfEdge({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_CfEdge()')

    def bl_cfwall(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], viscosity: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_velocity_mag: Union['float', 'ENS_VAR', str, int], opt_for_a_gradient_of_velo_mag: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the skin-friction coefficient

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            viscosity:
                A viscosity variable or a value.
            free_density:
                A constant 'freestream density' variable or a constant value(>0.).
            free_velocity_mag:
                A constant 'freestream velocity magnitude' variable or a constant value(>0.).
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_CfWall` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'viscosity', 'free_density', 'free_velocity_mag', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_CfWall"):
                self._func_counter["BL_CfWall"] = 0
            else:
                self._func_counter["BL_CfWall"] += 1
            counter = self._func_counter["BL_CfWall"]
            output_varname = f"BL_CfWall_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_CfWall({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_CfWall()')

    def bl_cfwallcmp(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], viscosity: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_velocity_mag: Union['float', 'ENS_VAR', str, int], ymax: float, tangent_flow_comp: int = 1, opt_for_a_gradient_of_velo_mag: Optional[Union['ENS_VAR', str, int]] = None, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the component of the skin-friction coefficient tangent or parallel to the wall in either the steam-wise or cross-flow direction

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            viscosity:
                A viscosity variable or a value.
            free_density:
                A constant 'freestream density' variable or a constant value(>0.).
            free_velocity_mag:
                A constant 'freestream velocity magnitude' variable or a constant value(>0.).
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            tangent_flow_comp:
                Enter tangent flow component 1=Streamwise or 2=Crosswise to surface.
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_CfWallCmp` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'viscosity', 'free_density', 'free_velocity_mag', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_CfWallCmp"):
                self._func_counter["BL_CfWallCmp"] = 0
            else:
                self._func_counter["BL_CfWallCmp"] += 1
            counter = self._func_counter["BL_CfWallCmp"]
            output_varname = f"BL_CfWallCmp_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_CfWallCmp({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_CfWallCmp()')

    def bl_cfwalltau(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], viscosity: Union['float', 'ENS_VAR', str, int], ymax: float, wall_shear_stress_opt: int = 0, opt_for_a_gradient_of_velo_mag: Optional[Union['ENS_VAR', str, int]] = None, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the fluid's shear-stress at the wall or in its stream-wise or cross-flow component direction

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            viscosity:
                A viscosity variable or a value.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            wall_shear_stress_opt:
                Enter surface shear-stress option: 0=RMS(Stream,Cross), or 1=Streamwise:dVs/dn or 2=Crossflow:dVc/dn component.
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_CfWallTau` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'viscosity', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_CfWallTau"):
                self._func_counter["BL_CfWallTau"] = 0
            else:
                self._func_counter["BL_CfWallTau"] += 1
            counter = self._func_counter["BL_CfWallTau"]
            output_varname = f"BL_CfWallTau_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_CfWallTau({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_CfWallTau()')

    def bl_dispthick(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], ymax: float, flow_dir_comp: int, opt_for_a_gradient_of_velo_mag: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the boundary-layer displacement thickness

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            flow_dir_comp:
                Enter flow direction: 0=Tangent to surface, or this Tangent flow's 1=Streamwise or 2=Crosswise component.
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_DispThick` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'density', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_DispThick"):
                self._func_counter["BL_DispThick"] = 0
            else:
                self._func_counter["BL_DispThick"] += 1
            counter = self._func_counter["BL_DispThick"]
            output_varname = f"BL_DispThick_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_DispThick({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_DispThick()')

    def bl_disttovalue(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar: Union['ENS_VAR', str, int], scalar_value: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the distance from the wall to the specified value

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            scalar:
                A scalar variable.
            scalar_value:
                Enter scalar value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_DistToValue` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar', 'scalar_value']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_DistToValue"):
                self._func_counter["BL_DistToValue"] = 0
            else:
                self._func_counter["BL_DistToValue"] += 1
            counter = self._func_counter["BL_DistToValue"]
            output_varname = f"BL_DistToValue_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_DistToValue({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_DistToValue()')

    def bl_momethick(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], ymax: float, flow_dir_i_comp: int, flow_dir_j_comp: int, opt_for_a_gradient_of_velo_mag: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the boundary momentum thickness

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            flow_dir_i_comp:
                Enter flow direction: 0=Tangent to surface, or this Tangent flow's 1=Streamwise or 2=Crosswise component.
            flow_dir_j_comp:
                Enter flow direction: 0=Tangent to surface, or this Tangent flow's 1=Streamwise or 2=Crosswise component.
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_MomeThick` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'density', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_MomeThick"):
                self._func_counter["BL_MomeThick"] = 0
            else:
                self._func_counter["BL_MomeThick"] += 1
            counter = self._func_counter["BL_MomeThick"]
            output_varname = f"BL_MomeThick_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_MomeThick({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_MomeThick()')

    def bl_scalar(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], scalar: Union['ENS_VAR', str, int], ymax: float, opt_for_a_gradient_of_velo_mag: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the scalar value of the corresponding scalar field at the edge of the boundary layer.

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            scalar:
                A scalar variable.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_Scalar` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'scalar', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_Scalar"):
                self._func_counter["BL_Scalar"] = 0
            else:
                self._func_counter["BL_Scalar"] += 1
            counter = self._func_counter["BL_Scalar"]
            output_varname = f"BL_Scalar_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_Scalar({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_Scalar()')

    def bl_recoverythick(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], total_pressure: Union['ENS_VAR', str, int], ymax: float, opt_for_a_gradient_of_velo_mag: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the boundary layer recovery thickness

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            total_pressure:
                A total pressure variable.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_RecoveryThick` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'total_pressure', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_RecoveryThick"):
                self._func_counter["BL_RecoveryThick"] = 0
            else:
                self._func_counter["BL_RecoveryThick"] += 1
            counter = self._func_counter["BL_RecoveryThick"]
            output_varname = f"BL_RecoveryThick_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_RecoveryThick({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_RecoveryThick()')

    def bl_thick(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], ymax: float, opt_for_a_gradient_of_velo_mag: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the boundary layer thickness

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_Thick` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_Thick"):
                self._func_counter["BL_Thick"] = 0
            else:
                self._func_counter["BL_Thick"] += 1
            counter = self._func_counter["BL_Thick"]
            output_varname = f"BL_Thick_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_Thick({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_Thick()')

    def bl_velocityatedge(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], ymax: float, edge_vector_option: int = 0, opt_for_a_gradient_of_velo_mag: Optional[Union['ENS_VAR', str, int]] = None, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as one of Ve, Vn, or Vp where Ve = velocity vector at edge of boundary layer, Vn = decomposed velocity vector normal to the wall at the edge of the boundary layer, or Vp = the decomposed velocity vector parallel to the wall at the edge of the boundary layer.

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            ymax:
                A ymax profiling distance (>0), (enter 0 for convergence alg.).
            edge_vector_option:
                Enter option to extract Velocity at edge of BL: 0=Vedge, or decomposed 1=Vparallel or 2=Vnormal to surface.
            opt_for_a_gradient_of_velo_mag:
                The gradient of the input velocity vector magnitude, or -1 to approximate it.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_VelocityAtEdge` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'opt_for_a_gradient_of_velo_mag']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_VelocityAtEdge"):
                self._func_counter["BL_VelocityAtEdge"] = 0
            else:
                self._func_counter["BL_VelocityAtEdge"] += 1
            counter = self._func_counter["BL_VelocityAtEdge"]
            output_varname = f"BL_VelocityAtEdge_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_VelocityAtEdge({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_VelocityAtEdge()')

    def bl_y1plus(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], viscosity: Union['float', 'ENS_VAR', str, int], gradient_option: int = 0, vector_variable: Optional[Union['ENS_VAR', str, int]] = None, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the coefficient-off-the-wall to the 1st field cell centroid

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            density:
                A density variable or a value.
            viscosity:
                A viscosity variable or a value.
            gradient_option:
                Enter 0 for "Use field velocity (to compute wall gradient)", 1 for "Use gradient at boundary part", or 2 for "Use gradient in field part".
            vector_variable:
                A vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_Y1Plus` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'viscosity', 'vector_variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_Y1Plus"):
                self._func_counter["BL_Y1Plus"] = 0
            else:
                self._func_counter["BL_Y1Plus"] += 1
            counter = self._func_counter["BL_Y1Plus"]
            output_varname = f"BL_Y1Plus_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_Y1Plus({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_Y1Plus()')

    def bl_y1plusdist(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the off-the-wall distance to the 1st field cell centroid. (Note: Velocity only used to determine reference sense (nodal or elemental) of variable to coincide with BL_Y1Plus.)

        Args:
            source_parts:
                Any boundary part(s) or a boundary part number.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`BL_Y1PlusDist` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("BL_Y1PlusDist"):
                self._func_counter["BL_Y1PlusDist"] = 0
            else:
                self._func_counter["BL_Y1PlusDist"] += 1
            counter = self._func_counter["BL_Y1PlusDist"]
            output_varname = f"BL_Y1PlusDist_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'BL_Y1PlusDist({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=BL_Y1PlusDist()')

    def casemap(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], case_number_to_map_from: int, variable: Union['ENS_VAR', str, int], parts_to_map_from: int = 0, search_option: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a field variable (scalar, vector, or tensor) on the selected parts by searching for the node/element location in the case specified.

        Args:
            source_parts:
                Any part(s) to map the variable to  or a part number.
            case_number_to_map_from:
                Enter number of the case to map the variable from.
            variable:
                A scalar or vector variable.
            parts_to_map_from:
                Enter 0 for "Global search", 1 for "Dimension match", 2 for "Part to Part", or 3 for "Selected Parts".
            search_option:
                Enter 0 for "search only" or 1 for "grab closest value if search fails".
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CaseMap` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CaseMap"):
                self._func_counter["CaseMap"] = 0
            else:
                self._func_counter["CaseMap"] += 1
            counter = self._func_counter["CaseMap"]
            output_varname = f"CaseMap_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CaseMap({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CaseMap()')

    def casemapdiff(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], case_number_to_map_from: int, variable: Union['ENS_VAR', str, int], parts_to_map_from: int = 0, search_option: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a field variable (scalar, vector, or tensor) on the selected parts by searching for the node/element location in the case specified.  Results is the field variable minus the case map. 

        Args:
            source_parts:
                Any part(s) to map the variable to  or a part number.
            case_number_to_map_from:
                Enter number of the case to map the variable from.
            variable:
                A scalar or vector variable.
            parts_to_map_from:
                Enter 0 for "Global search", 1 for "Dimension match", 2 for "Part to Part", or 3 for "Selected Parts".
            search_option:
                Enter 0 for "search only" or 1 for "grab closest value if search fails".
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CaseMapDiff` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CaseMapDiff"):
                self._func_counter["CaseMapDiff"] = 0
            else:
                self._func_counter["CaseMapDiff"] += 1
            counter = self._func_counter["CaseMapDiff"]
            output_varname = f"CaseMapDiff_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CaseMapDiff({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CaseMapDiff()')

    def casemapimage(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], part_2: int, variable: Union['ENS_VAR', str, int], vport: int, undefvalue: float, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable by projecting a 2d image to a 3d geometry given the view in a specific viewport

        Args:
            source_parts:
                Enter the part to map the variable from.
            part_2:
                Enter the part to map the variable from.
            variable:
                A scalar variable.
            vport:
                Enter Viewport number for 3D model in correct camera orientation
            undefvalue:
                Enter value limit - value under which the variable will be Undefined
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CaseMapImage` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CaseMapImage"):
                self._func_counter["CaseMapImage"] = 0
            else:
                self._func_counter["CaseMapImage"] += 1
            counter = self._func_counter["CaseMapImage"]
            output_varname = f"CaseMapImage_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CaseMapImage({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CaseMapImage()')

    def coeff(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the surface integral of a scalar variable multiplied by the x, y, or z component of the surface normal

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            scalar:
                A scalar variable.
            component:
                A component [X], [Y], or [Z].
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Coeff` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Coeff"):
                self._func_counter["Coeff"] = 0
            else:
                self._func_counter["Coeff"] += 1
            counter = self._func_counter["Coeff"]
            output_varname = f"Coeff_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Coeff({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Coeff()')

    def cmplx(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector_1: Union['ENS_VAR', str, int], scalar_or_vector_2: Union['ENS_VAR', str, int], frequency: float, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a complex scalar or vector from two scalar or vector variables, Z = A + Bi.  The frequency is optional and is used only for reference.

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_or_vector_1:
                A scalar/vector variable for the imaginary portion.
            scalar_or_vector_2:
                A scalar/vector variable for the imaginary portion.
            frequency:
                A frequency value in degrees or leave blank and UNDEFINED will be used.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Cmplx` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector_1', 'scalar_or_vector_2']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Cmplx"):
                self._func_counter["Cmplx"] = 0
            else:
                self._func_counter["Cmplx"] += 1
            counter = self._func_counter["Cmplx"]
            output_varname = f"Cmplx_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Cmplx({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Cmplx()')

    def cmplxarg(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar in range -180 to 180 degrees defined as the argument of a complex scalar or vector:  Arg = atan(Vi/Vr).

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_or_vector:
                A complex scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CmplxArg` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CmplxArg"):
                self._func_counter["CmplxArg"] = 0
            else:
                self._func_counter["CmplxArg"] += 1
            counter = self._func_counter["CmplxArg"]
            output_varname = f"CmplxArg_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CmplxArg({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CmplxArg()')

    def cmplxconj(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a complex scalar or vector defined as the conjugate of a given complex scalar or vector variable:  Nr = Vr, Ni = -Vi

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_or_vector:
                A complex scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CmplxConj` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CmplxConj"):
                self._func_counter["CmplxConj"] = 0
            else:
                self._func_counter["CmplxConj"] += 1
            counter = self._func_counter["CmplxConj"]
            output_varname = f"CmplxConj_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CmplxConj({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CmplxConj()')

    def cmplximag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar or vector variable defined as the imaginary portion of a complex scalar/vector

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_or_vector:
                A complex scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CmplxImag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CmplxImag"):
                self._func_counter["CmplxImag"] = 0
            else:
                self._func_counter["CmplxImag"] += 1
            counter = self._func_counter["CmplxImag"]
            output_varname = f"CmplxImag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CmplxImag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CmplxImag()')

    def cmplxmodu(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar or vector variable defined as the modulus of a complex scalar/vector

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_or_vector:
                A complex scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CmplxModu` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CmplxModu"):
                self._func_counter["CmplxModu"] = 0
            else:
                self._func_counter["CmplxModu"] += 1
            counter = self._func_counter["CmplxModu"]
            output_varname = f"CmplxModu_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CmplxModu({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CmplxModu()')

    def cmplxreal(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar or vector variable defined as the real portion of a complex scalar/vector

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_or_vector:
                A complex scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CmplxReal` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CmplxReal"):
                self._func_counter["CmplxReal"] = 0
            else:
                self._func_counter["CmplxReal"] += 1
            counter = self._func_counter["CmplxReal"]
            output_varname = f"CmplxReal_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CmplxReal({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CmplxReal()')

    def cmplxtransresp(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], phi: float, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar or vector variable defined as the real transient response of a complex scalar/vector variable given a transient phase angle.  Function is only valid for harmonic variations.

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_or_vector:
                A complex scalar or vector variable.
            phi:
                A value for PHI(Range 0.0 - 360.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`CmplxTransResp` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("CmplxTransResp"):
                self._func_counter["CmplxTransResp"] = 0
            else:
                self._func_counter["CmplxTransResp"] += 1
            counter = self._func_counter["CmplxTransResp"]
            output_varname = f"CmplxTransResp_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'CmplxTransResp({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=CmplxTransResp()')

    def constantperpart(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], constant: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Assigns a constant value as a constant per part variable

        Args:
            source_parts:
                Any part(s) or a part number.
            constant:
                Set value for per part constant variable
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ConstantPerPart` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['constant']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ConstantPerPart"):
                self._func_counter["ConstantPerPart"] = 0
            else:
                self._func_counter["ConstantPerPart"] += 1
            counter = self._func_counter["ConstantPerPart"]
            output_varname = f"ConstantPerPart_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ConstantPerPart({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ConstantPerPart()')

    def curl(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the curl of the vector variable specified

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            vector:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Curl` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Curl"):
                self._func_counter["Curl"] = 0
            else:
                self._func_counter["Curl"] += 1
            counter = self._func_counter["Curl"]
            output_varname = f"Curl_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Curl({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Curl()')

    def defect_bulkvolume(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the bulk volume of defect cells that share a face.

        Args:
            source_parts:
                Any part(s) or a part #.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Defect_BulkVolume` for function details.
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
            if not self._func_counter.get("Defect_BulkVolume"):
                self._func_counter["Defect_BulkVolume"] = 0
            else:
                self._func_counter["Defect_BulkVolume"] += 1
            counter = self._func_counter["Defect_BulkVolume"]
            output_varname = f"Defect_BulkVolume_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Defect_BulkVolume({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Defect_BulkVolume()')

    def defect_count(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], Defect_scalar_per_element: Union['ENS_VAR', str, int], min_constant: Union['float', 'ENS_VAR', str, int], max_constant: Union['float', 'ENS_VAR', str, int], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the count of the defects that exist between a specifed min and max value of any of the computed Defect scalar variables.

        Args:
            source_parts:
                Any part(s) or a part #.
            Defect_scalar_per_element:
                A computed Defect scalar per element variable.
            min_constant:
                A minimum defect constant variable or specify a value.
            max_constant:
                A maximum defect constant variable or specify a value.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Defect_Count` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['Defect_scalar_per_element', 'min_constant', 'max_constant']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Defect_Count"):
                self._func_counter["Defect_Count"] = 0
            else:
                self._func_counter["Defect_Count"] += 1
            counter = self._func_counter["Defect_Count"]
            output_varname = f"Defect_Count_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Defect_Count({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Defect_Count()')

    def defect_largestlinearextent(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the largest linear extent of the defect.

        Args:
            source_parts:
                Any part(s) or a part #.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Defect_LargestLinearExtent` for function details.
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
            if not self._func_counter.get("Defect_LargestLinearExtent"):
                self._func_counter["Defect_LargestLinearExtent"] = 0
            else:
                self._func_counter["Defect_LargestLinearExtent"] += 1
            counter = self._func_counter["Defect_LargestLinearExtent"]
            output_varname = f"Defect_LargestLinearExtent_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Defect_LargestLinearExtent({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Defect_LargestLinearExtent()')

    def defect_netvolume(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_per_element_variable: Union['float', 'ENS_VAR', str, int], scale_factor: float, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the sum of the product of cell volumes with the specified scalar variable of the cells comprising the defect.

        Args:
            source_parts:
                Any part(s) or a part #.
            scalar_per_element_variable:
                A defect scalar per element variable or a value.
            scale_factor:
                Specify a scale factor multiplied to the scalar per element values.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Defect_NetVolume` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_per_element_variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Defect_NetVolume"):
                self._func_counter["Defect_NetVolume"] = 0
            else:
                self._func_counter["Defect_NetVolume"] += 1
            counter = self._func_counter["Defect_NetVolume"]
            output_varname = f"Defect_NetVolume_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Defect_NetVolume({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Defect_NetVolume()')

    def defect_shapefactor(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per node scalar variable defined as the largest linear extent divided by the diameter of the sphere whose volume equals the bulk volume of cells comprising the defect.

        Args:
            source_parts:
                Any part(s) or a part #.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Defect_ShapeFactor` for function details.
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
            if not self._func_counter.get("Defect_ShapeFactor"):
                self._func_counter["Defect_ShapeFactor"] = 0
            else:
                self._func_counter["Defect_ShapeFactor"] += 1
            counter = self._func_counter["Defect_ShapeFactor"]
            output_varname = f"Defect_ShapeFactor_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Defect_ShapeFactor({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Defect_ShapeFactor()')

    def defect_surfacearea(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the surface area of the defect.

        Args:
            source_parts:
                Any part(s) or a part #.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Defect_SurfaceArea` for function details.
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
            if not self._func_counter.get("Defect_SurfaceArea"):
                self._func_counter["Defect_SurfaceArea"] = 0
            else:
                self._func_counter["Defect_SurfaceArea"] += 1
            counter = self._func_counter["Defect_SurfaceArea"]
            output_varname = f"Defect_SurfaceArea_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Defect_SurfaceArea({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Defect_SurfaceArea()')

    def density(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], pressure: Union['ENS_VAR', str, int], temperature: Union['ENS_VAR', str, int], gas_constant: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the density as a function of pressure, temperature, and gas constant

        Args:
            source_parts:
                Any part(s) or a part number.
            pressure:
                A pressure variable.
            temperature:
                A temperature variable.
            gas_constant:
                A specific gas constant variable or a constant value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Density` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['pressure', 'temperature', 'gas_constant']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Density"):
                self._func_counter["Density"] = 0
            else:
                self._func_counter["Density"] += 1
            counter = self._func_counter["Density"]
            output_varname = f"Density_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Density({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Density()')

    def densitylognorm(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the natural log of the normalized density

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`DensityLogNorm` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'free_density']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("DensityLogNorm"):
                self._func_counter["DensityLogNorm"] = 0
            else:
                self._func_counter["DensityLogNorm"] += 1
            counter = self._func_counter["DensityLogNorm"]
            output_varname = f"DensityLogNorm_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'DensityLogNorm({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=DensityLogNorm()')

    def densitynorm(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the normalized density

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`DensityNorm` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'free_density']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("DensityNorm"):
                self._func_counter["DensityNorm"] = 0
            else:
                self._func_counter["DensityNorm"] += 1
            counter = self._func_counter["DensityNorm"]
            output_varname = f"DensityNorm_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'DensityNorm({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=DensityNorm()')

    def densitynormstag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], free_velocity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the normalized stagnation density

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            free_velocity:
                A 'freestream velocity magnitude' variable  or value(>=1.0)
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`DensityNormStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'free_velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("DensityNormStag"):
                self._func_counter["DensityNormStag"] = 0
            else:
                self._func_counter["DensityNormStag"] += 1
            counter = self._func_counter["DensityNormStag"]
            output_varname = f"DensityNormStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'DensityNormStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=DensityNormStag()')

    def densitystag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the stagnation density

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`DensityStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("DensityStag"):
                self._func_counter["DensityStag"] = 0
            else:
                self._func_counter["DensityStag"] += 1
            counter = self._func_counter["DensityStag"]
            output_varname = f"DensityStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'DensityStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=DensityStag()')

    def dist2nodes(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], number_1: int, number_2: int, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the Euclidean distance between the two node IDs specified

        Args:
            source_parts:
                Any part(s) or a part number.
            number_1:
                Enter second node number.
            number_2:
                Enter second node number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Dist2Nodes` for function details.
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
            if not self._func_counter.get("Dist2Nodes"):
                self._func_counter["Dist2Nodes"] = 0
            else:
                self._func_counter["Dist2Nodes"] += 1
            counter = self._func_counter["Dist2Nodes"]
            output_varname = f"Dist2Nodes_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Dist2Nodes({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Dist2Nodes()')

    def dist2part(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], origin_part_number: int, optional_origin_part_normal: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a nodal scalar variable defined as the smallest Euclidean distance from the nodes of the origin part to the nodes of the parts specified.  If a vector is given the result will be signed.  

        Args:
            source_parts:
                Select origin part and field part(s), or enter the origin part number and the field part number(s).
            origin_part_number:
                Enter the origin part number. This part must also be in the previous part list.
            optional_origin_part_normal:
                To select a signed distance, a nodal normal vector for the origin part or choose None to compute an unsigned distance.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Dist2Part` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['optional_origin_part_normal']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Dist2Part"):
                self._func_counter["Dist2Part"] = 0
            else:
                self._func_counter["Dist2Part"] += 1
            counter = self._func_counter["Dist2Part"]
            output_varname = f"Dist2Part_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Dist2Part({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Dist2Part()')

    def dist2partelem(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], origin_part_number: int, optional_origin_part_normal: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a nodal scalar variable defined as the smallest Euclidean distance from the elements of the origin part to the nodes of the parts specified.  If a vector is given the result will be signed.

        Args:
            source_parts:
                Select origin part and field part(s), or enter the origin part number and the field part number(s).
            origin_part_number:
                Enter the origin part number. This part must also be in the previous part list.
            optional_origin_part_normal:
                To select a signed distance, a nodal normal vector for the origin part or choose None to compute an unsigned distance.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Dist2PartElem` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['optional_origin_part_normal']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Dist2PartElem"):
                self._func_counter["Dist2PartElem"] = 0
            else:
                self._func_counter["Dist2PartElem"] += 1
            counter = self._func_counter["Dist2PartElem"]
            output_varname = f"Dist2PartElem_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Dist2PartElem({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Dist2PartElem()')

    def div(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the divergence of the vector specified.

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            vector:
                A vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Div` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Div"):
                self._func_counter["Div"] = 0
            else:
                self._func_counter["Div"] += 1
            counter = self._func_counter["Div"]
            output_varname = f"Div_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Div({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Div()')

    def elemetric(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], metric_function: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per-element scalar variable on any parts, whose value is one of a collection of element quality metric functions.

        Args:
            source_parts:
                Any part(s) or a part number.
            metric_function:
                A Verdict library element quality metric to compute.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`EleMetric` for function details.
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
            if not self._func_counter.get("EleMetric"):
                self._func_counter["EleMetric"] = 0
            else:
                self._func_counter["EleMetric"] += 1
            counter = self._func_counter["EleMetric"]
            output_varname = f"EleMetric_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'EleMetric({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=EleMetric()')

    def elemtonode(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], elemental_scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute a node based variable from a element based scalar or vector by simple nodal averaging.

        Args:
            source_parts:
                Any part(s) or a part number.
            elemental_scalar_or_vector:
                An element based scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ElemToNode` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['elemental_scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ElemToNode"):
                self._func_counter["ElemToNode"] = 0
            else:
                self._func_counter["ElemToNode"] += 1
            counter = self._func_counter["ElemToNode"]
            output_varname = f"ElemToNode_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ElemToNode({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ElemToNode()')

    def elemtonodeweighted(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], elemental_scalar_or_vector: Union['ENS_VAR', str, int], elemental_scalar: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute a node based variable from a element based scalar or vector by weighted nodal averaging.

        Args:
            source_parts:
                Any part(s) or a part number.
            elemental_scalar_or_vector:
                An element based scalar or vector variable.
            elemental_scalar:
                An element based scalar variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ElemToNodeWeighted` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['elemental_scalar_or_vector', 'elemental_scalar']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ElemToNodeWeighted"):
                self._func_counter["ElemToNodeWeighted"] = 0
            else:
                self._func_counter["ElemToNodeWeighted"] += 1
            counter = self._func_counter["ElemToNodeWeighted"]
            output_varname = f"ElemToNodeWeighted_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ElemToNodeWeighted({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ElemToNodeWeighted()')

    def elesize(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute an element based scalar variable defined as the length/Area/Volume of 1d/2d/3d elements in the parts specified.

        Args:
            source_parts:
                Any part(s) or a part number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`EleSize` for function details.
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
            if not self._func_counter.get("EleSize"):
                self._func_counter["EleSize"] = 0
            else:
                self._func_counter["EleSize"] += 1
            counter = self._func_counter["EleSize"]
            output_varname = f"EleSize_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'EleSize({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=EleSize()')

    def energyt(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], pressure: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute a scalar variable defined as the total energy per unit volume given density, pressure, velocity, and ratio of specific heats.

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            pressure:
                A pressure variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`EnergyT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'pressure', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("EnergyT"):
                self._func_counter["EnergyT"] = 0
            else:
                self._func_counter["EnergyT"] += 1
            counter = self._func_counter["EnergyT"]
            output_varname = f"EnergyT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'EnergyT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=EnergyT()')

    def enthalpy(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute a scalar variable defined as the enthalpy given total energy, density, velocity, and ratio of specific heats.

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Enthalpy` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Enthalpy"):
                self._func_counter["Enthalpy"] = 0
            else:
                self._func_counter["Enthalpy"] += 1
            counter = self._func_counter["Enthalpy"]
            output_varname = f"Enthalpy_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Enthalpy({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Enthalpy()')

    def enthalpynorm(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute a scalar variable defined as the normalized enthalpy given total energy, density, velocity, ratio of specific heats, and freestream density and speed of sound

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`EnthalpyNorm` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("EnthalpyNorm"):
                self._func_counter["EnthalpyNorm"] = 0
            else:
                self._func_counter["EnthalpyNorm"] += 1
            counter = self._func_counter["EnthalpyNorm"]
            output_varname = f"EnthalpyNorm_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'EnthalpyNorm({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=EnthalpyNorm()')

    def enthalpynormstag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], free_velocity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute a scalar variable defined as the normalized stagnation enthalpy given total energy, density, velocity, ratio of specific heats, and freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            free_velocity:
                A 'freestream velocity magnitude' variable  or value(>=1.0)
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`EnthalpyNormStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'free_velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("EnthalpyNormStag"):
                self._func_counter["EnthalpyNormStag"] = 0
            else:
                self._func_counter["EnthalpyNormStag"] += 1
            counter = self._func_counter["EnthalpyNormStag"]
            output_varname = f"EnthalpyNormStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'EnthalpyNormStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=EnthalpyNormStag()')

    def enthalpystag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Compute a scalar variable defined as the stagnation enthalpy given total energy, density, velocity, and ratio of specific heats

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`EnthalpyStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("EnthalpyStag"):
                self._func_counter["EnthalpyStag"] = 0
            else:
                self._func_counter["EnthalpyStag"] += 1
            counter = self._func_counter["EnthalpyStag"]
            output_varname = f"EnthalpyStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'EnthalpyStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=EnthalpyStag()')

    def entropy(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], gas: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the entropy given total energy, density, velocity, ratio of specific heats, gas constant, and freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            gas:
                A gas constant variable or value(>0.0).
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Entropy` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'gas', 'free_density', 'free_speed_of_sound']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Entropy"):
                self._func_counter["Entropy"] = 0
            else:
                self._func_counter["Entropy"] += 1
            counter = self._func_counter["Entropy"]
            output_varname = f"Entropy_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Entropy({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Entropy()')

    def flow(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the volume flow rate, i.e., the surface integral of the velocity in the surface normal direction.

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            velocity:
                A velocity variable.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Flow` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Flow"):
                self._func_counter["Flow"] = 0
            else:
                self._func_counter["Flow"] += 1
            counter = self._func_counter["Flow"]
            output_varname = f"Flow_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Flow({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Flow()')

    def flowrate(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the component of velocity in the surface normal direction.

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`FlowRate` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("FlowRate"):
                self._func_counter["FlowRate"] = 0
            else:
                self._func_counter["FlowRate"] += 1
            counter = self._func_counter["FlowRate"]
            output_varname = f"FlowRate_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'FlowRate({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=FlowRate()')

    def fluidshear(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity_magnitude_gradient: Union['ENS_VAR', str, int], viscosity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the shear stress multiplied by the velocity gradient in the surface normal direction

        Args:
            source_parts:
                Any 2D part(s) or a part number.
            velocity_magnitude_gradient:
                A velocity (magnitude) gradient variable.
            viscosity:
                A viscosity variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`FluidShear` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity_magnitude_gradient', 'viscosity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("FluidShear"):
                self._func_counter["FluidShear"] = 0
            else:
                self._func_counter["FluidShear"] += 1
            counter = self._func_counter["FluidShear"]
            output_varname = f"FluidShear_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'FluidShear({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=FluidShear()')

    def fluidshearmax(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], turb_kinetic_energy: Union['ENS_VAR', str, int], turb_dissipation: Union['ENS_VAR', str, int], laminar_viscosity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the turbulent plus laminar viscosity multiplied by the local strain

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            turb_kinetic_energy:
                A turbulent kinetic energy variable.
            turb_dissipation:
                A turbulent dissipation variable.
            laminar_viscosity:
                A 'laminar viscosity' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`FluidShearMax` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'density', 'turb_kinetic_energy', 'turb_dissipation', 'laminar_viscosity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("FluidShearMax"):
                self._func_counter["FluidShearMax"] = 0
            else:
                self._func_counter["FluidShearMax"] += 1
            counter = self._func_counter["FluidShearMax"]
            output_varname = f"FluidShearMax_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'FluidShearMax({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=FluidShearMax()')

    def force(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], pressure: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the pressure*area force acting in the surface normal direction.

        Args:
            source_parts:
                Any 2D part(s) or a part number.
            pressure:
                A pressure variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Force` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['pressure']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Force"):
                self._func_counter["Force"] = 0
            else:
                self._func_counter["Force"] += 1
            counter = self._func_counter["Force"]
            output_varname = f"Force_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Force({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Force()')

    def force1d(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], pressure: Union['ENS_VAR', str, int], surface_normal: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the pressure*length force acting in the normal direction given

        Args:
            source_parts:
                Any 1D part(s) or a part number.
            pressure:
                A pressure variable.
            surface_normal:
                A surface normal variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Force1D` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['pressure', 'surface_normal']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Force1D"):
                self._func_counter["Force1D"] = 0
            else:
                self._func_counter["Force1D"] += 1
            counter = self._func_counter["Force1D"]
            output_varname = f"Force1D_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Force1D({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Force1D()')

    def grad(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the gradient of a scalar or vector magnitude

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            scalar_or_vector:
                A scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Grad` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Grad"):
                self._func_counter["Grad"] = 0
            else:
                self._func_counter["Grad"] += 1
            counter = self._func_counter["Grad"]
            output_varname = f"Grad_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Grad({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Grad()')

    def gradtensor(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a tensor variable defined as the gradient of a vector variable

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            vector:
                A vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`GradTensor` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("GradTensor"):
                self._func_counter["GradTensor"] = 0
            else:
                self._func_counter["GradTensor"] += 1
            counter = self._func_counter["GradTensor"]
            output_varname = f"GradTensor_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'GradTensor({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=GradTensor()')

    def helicitydensity(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the helicity computed by dotting the velocity with vorticity

        Args:
            source_parts:
                Any part(s) or a part number.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`HelicityDensity` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("HelicityDensity"):
                self._func_counter["HelicityDensity"] = 0
            else:
                self._func_counter["HelicityDensity"] += 1
            counter = self._func_counter["HelicityDensity"]
            output_varname = f"HelicityDensity_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'HelicityDensity({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=HelicityDensity()')

    def helicityrelative(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the relative helicity computed by dotting the velocity with vorticity and dividing by the velocity and vorticity magnitudes.

        Args:
            source_parts:
                Any part(s) or a part number.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`HelicityRelative` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("HelicityRelative"):
                self._func_counter["HelicityRelative"] = 0
            else:
                self._func_counter["HelicityRelative"] += 1
            counter = self._func_counter["HelicityRelative"]
            output_varname = f"HelicityRelative_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'HelicityRelative({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=HelicityRelative()')

    def helicityrelfilter(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], free_velocity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the relative filtered helicity = the relative helicity if the helicity density is greater or equal to the filter value and = 0 if the helicity density is less than the filter value.  The filter value is defined to be .1*Vinf^2 where Vinf is the freestream velocity magnitude

        Args:
            source_parts:
                Any part(s) or a part number.
            velocity:
                A velocity variable.
            free_velocity:
                A 'freestream velocity magnitude' variable  or value(>=1.0)
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`HelicityRelFilter` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'free_velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("HelicityRelFilter"):
                self._func_counter["HelicityRelFilter"] = 0
            else:
                self._func_counter["HelicityRelFilter"] += 1
            counter = self._func_counter["HelicityRelFilter"]
            output_varname = f"HelicityRelFilter_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'HelicityRelFilter({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=HelicityRelFilter()')

    def iblankingvalues(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the iblanking value.  Only applies to structured data with iblanking.

        Args:
            source_parts:
                Any iblanked structured part(s) and select Next or a part #.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IblankingValues` for function details.
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
            if not self._func_counter.get("IblankingValues"):
                self._func_counter["IblankingValues"] = 0
            else:
                self._func_counter["IblankingValues"] += 1
            counter = self._func_counter["IblankingValues"]
            output_varname = f"IblankingValues_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IblankingValues({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IblankingValues()')

    def ijkvalues(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the I,J,K values.  Only applies to structured data.

        Args:
            source_parts:
                Any structured part(s) and select Next or a part #.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IJKValues` for function details.
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
            if not self._func_counter.get("IJKValues"):
                self._func_counter["IJKValues"] = 0
            else:
                self._func_counter["IJKValues"] += 1
            counter = self._func_counter["IJKValues"]
            output_varname = f"IJKValues_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IJKValues({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IJKValues()')

    def integralline(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the integral of the variable specified over the length of the part(s)

        Args:
            source_parts:
                Any 1D part(s) or a part number.
            variable:
                A scalar or vector variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IntegralLine` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("IntegralLine"):
                self._func_counter["IntegralLine"] = 0
            else:
                self._func_counter["IntegralLine"] += 1
            counter = self._func_counter["IntegralLine"]
            output_varname = f"IntegralLine_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IntegralLine({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IntegralLine()')

    def integralsurface(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the integral of the variable specified over the surface of the part(s)

        Args:
            source_parts:
                Any 2D part(s) or a part number.
            variable:
                A scalar or vector variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IntegralSurface` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("IntegralSurface"):
                self._func_counter["IntegralSurface"] = 0
            else:
                self._func_counter["IntegralSurface"] += 1
            counter = self._func_counter["IntegralSurface"]
            output_varname = f"IntegralSurface_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IntegralSurface({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IntegralSurface()')

    def integralvolume(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the integral of the variable specified over the volume of the part(s)

        Args:
            source_parts:
                Any 3D part(s) or a part number.
            variable:
                A scalar or vector variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`IntegralVolume` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("IntegralVolume"):
                self._func_counter["IntegralVolume"] = 0
            else:
                self._func_counter["IntegralVolume"] += 1
            counter = self._func_counter["IntegralVolume"]
            output_varname = f"IntegralVolume_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'IntegralVolume({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=IntegralVolume()')

    def kinen(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the kinetic energy 0.5*rho*V^2

        Args:
            source_parts:
                Any part(s) or a part number.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`KinEn` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'density']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("KinEn"):
                self._func_counter["KinEn"] = 0
            else:
                self._func_counter["KinEn"] += 1
            counter = self._func_counter["KinEn"]
            output_varname = f"KinEn_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'KinEn({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=KinEn()')

    def length(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the sum of the length of all 1D elements. Parts composed of 2D or 3D elements need to be in Feature rep to obtain a value

        Args:
            source_parts:
                Any 1D part(s) or a part number.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Length` for function details.
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
            if not self._func_counter.get("Length"):
                self._func_counter["Length"] = 0
            else:
                self._func_counter["Length"] += 1
            counter = self._func_counter["Length"]
            output_varname = f"Length_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Length({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Length()')

    def linevectors(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a nodal vector variable defined as the vector from the first to the last node of each 1d element of the part(s).  Variable is undefined for non 1d elements

        Args:
            source_parts:
                Any 1D part(s) or a part number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`LineVectors` for function details.
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
            if not self._func_counter.get("LineVectors"):
                self._func_counter["LineVectors"] = 0
            else:
                self._func_counter["LineVectors"] += 1
            counter = self._func_counter["LineVectors"]
            output_varname = f"LineVectors_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'LineVectors({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=LineVectors()')

    def mach(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as Speed/Speed_of_sound where Speed_of_sound is computed from the ratio of specific heats, pressure, and density

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Mach` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Mach"):
                self._func_counter["Mach"] = 0
            else:
                self._func_counter["Mach"] += 1
            counter = self._func_counter["Mach"]
            output_varname = f"Mach_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Mach({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Mach()')

    def makescalelem(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], constant: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar per element variable defined as a specified value or constant variable

        Args:
            source_parts:
                Any part(s) or a part number.
            constant:
                A constant variable or a value to assign scalar per element.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MakeScalElem` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['constant']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("MakeScalElem"):
                self._func_counter["MakeScalElem"] = 0
            else:
                self._func_counter["MakeScalElem"] += 1
            counter = self._func_counter["MakeScalElem"]
            output_varname = f"MakeScalElem_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MakeScalElem({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MakeScalElem()')

    def makescalelemid(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar per element variable defined as the element ids for the part

        Args:
            source_parts:
                Any part(s) or a part number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MakeScalElemId` for function details.
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
            if not self._func_counter.get("MakeScalElemId"):
                self._func_counter["MakeScalElemId"] = 0
            else:
                self._func_counter["MakeScalElemId"] += 1
            counter = self._func_counter["MakeScalElemId"]
            output_varname = f"MakeScalElemId_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MakeScalElemId({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MakeScalElemId()')

    def makescalnode(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], constant: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar per node variable defined as a specified value or constant variable

        Args:
            source_parts:
                Any part(s) or a part number.
            constant:
                A constant variable or a value to assign scalar per node.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MakeScalNode` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['constant']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("MakeScalNode"):
                self._func_counter["MakeScalNode"] = 0
            else:
                self._func_counter["MakeScalNode"] += 1
            counter = self._func_counter["MakeScalNode"]
            output_varname = f"MakeScalNode_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MakeScalNode({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MakeScalNode()')

    def makescalnodeid(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar per node variable defined as the node ids for the part

        Args:
            source_parts:
                Any part(s) or a part number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MakeScalNodeId` for function details.
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
            if not self._func_counter.get("MakeScalNodeId"):
                self._func_counter["MakeScalNodeId"] = 0
            else:
                self._func_counter["MakeScalNodeId"] += 1
            counter = self._func_counter["MakeScalNodeId"]
            output_varname = f"MakeScalNodeId_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MakeScalNodeId({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MakeScalNodeId()')

    def makevect(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_1: Union['float', 'ENS_VAR', str, int], scalar_2: Union['float', 'ENS_VAR', str, int], scalar_3: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable using three scalar/constant variables or constant values for the x, y, and z components.

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_1:
                A scalar variable or a 0 to indicate a 2D case.
            scalar_2:
                A scalar variable or a 0 to indicate a 2D case.
            scalar_3:
                A scalar variable or a 0 to indicate a 2D case.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MakeVect` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_1', 'scalar_2', 'scalar_3']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("MakeVect"):
                self._func_counter["MakeVect"] = 0
            else:
                self._func_counter["MakeVect"] += 1
            counter = self._func_counter["MakeVect"]
            output_varname = f"MakeVect_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MakeVect({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MakeVect()')

    def massedparticle(self, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the total mass of massed particles that collide with a surface
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MassedParticle` for function details.
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
            if not self._func_counter.get("MassedParticle"):
                self._func_counter["MassedParticle"] = 0
            else:
                self._func_counter["MassedParticle"] += 1
            counter = self._func_counter["MassedParticle"]
            output_varname = f"MassedParticle_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MassedParticle({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MassedParticle()')

    def massfluxavg(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the mass flux average

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            scalar:
                A scalar variable.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MassFluxAvg` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar', 'velocity', 'density']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("MassFluxAvg"):
                self._func_counter["MassFluxAvg"] = 0
            else:
                self._func_counter["MassFluxAvg"] += 1
            counter = self._func_counter["MassFluxAvg"]
            output_varname = f"MassFluxAvg_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MassFluxAvg({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MassFluxAvg()')

    def matspecies(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_per_elem: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the sum of all specified materials and species combinations multiplied by the specific element variable.

        Args:
            source_parts:
                Any model part(s) or a model part number.
            scalar_per_elem:
                An element-based scalar variable, or a scalar value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MatSpecies` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_per_elem']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("MatSpecies"):
                self._func_counter["MatSpecies"] = 0
            else:
                self._func_counter["MatSpecies"] += 1
            counter = self._func_counter["MatSpecies"]
            output_varname = f"MatSpecies_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MatSpecies({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MatSpecies()')

    def mattoscalar(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the material fraction

        Args:
            source_parts:
                Any model part(s) or a model part number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MatToScalar` for function details.
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
            if not self._func_counter.get("MatToScalar"):
                self._func_counter["MatToScalar"] = 0
            else:
                self._func_counter["MatToScalar"] += 1
            counter = self._func_counter["MatToScalar"]
            output_varname = f"MatToScalar_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MatToScalar({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MatToScalar()')

    def max(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined to be the maximum of the variable specified.

        Args:
            source_parts:
                Any part(s) or a part number.
            variable:
                A scalar, vector or constant variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Max` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Max"):
                self._func_counter["Max"] = 0
            else:
                self._func_counter["Max"] += 1
            counter = self._func_counter["Max"]
            output_varname = f"Max_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Max({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Max()')

    def min(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined to be the minimum of the variable specified.

        Args:
            source_parts:
                Any part(s) or a part number.
            variable:
                A scalar, vector or constant variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Min` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Min"):
                self._func_counter["Min"] = 0
            else:
                self._func_counter["Min"] += 1
            counter = self._func_counter["Min"]
            output_varname = f"Min_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Min({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Min()')

    def moment(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined to be the x, y, or z moment about the cursor tool location given a force vector

        Args:
            source_parts:
                Any part(s) or a part number.
            vector:
                A vector variable.
            component:
                A component [X], [Y], or [Z].
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Moment` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Moment"):
                self._func_counter["Moment"] = 0
            else:
                self._func_counter["Moment"] += 1
            counter = self._func_counter["Moment"]
            output_varname = f"Moment_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Moment({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Moment()')

    def momentum(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as density*Velocity

        Args:
            source_parts:
                Any part(s) or a part number.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Momentum` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'density']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Momentum"):
                self._func_counter["Momentum"] = 0
            else:
                self._func_counter["Momentum"] += 1
            counter = self._func_counter["Momentum"]
            output_varname = f"Momentum_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Momentum({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Momentum()')

    def momentvector(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], force: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a nodal vector variables defined as the x, y, or z moment about each node given a force vector

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            force:
                A force vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`MomentVector` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['force']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("MomentVector"):
                self._func_counter["MomentVector"] = 0
            else:
                self._func_counter["MomentVector"] += 1
            counter = self._func_counter["MomentVector"]
            output_varname = f"MomentVector_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'MomentVector({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=MomentVector()')

    def nodecount(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the number of nodes in the part(s) selected

        Args:
            source_parts:
                Any part(s) or a part number.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`NodeCount` for function details.
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
            if not self._func_counter.get("NodeCount"):
                self._func_counter["NodeCount"] = 0
            else:
                self._func_counter["NodeCount"] += 1
            counter = self._func_counter["NodeCount"]
            output_varname = f"NodeCount_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'NodeCount({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=NodeCount()')

    def nodetoelem(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], nodal_scalar_or_vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes an element based variable from a node based variable

        Args:
            source_parts:
                Any part(s) or a part number.
            nodal_scalar_or_vector:
                A node based scalar or vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`NodeToElem` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['nodal_scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("NodeToElem"):
                self._func_counter["NodeToElem"] = 0
            else:
                self._func_counter["NodeToElem"] += 1
            counter = self._func_counter["NodeToElem"]
            output_varname = f"NodeToElem_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'NodeToElem({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=NodeToElem()')

    def normal(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes an element based vector variable defined as the surface normal for the parts selected

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Normal` for function details.
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
            if not self._func_counter.get("Normal"):
                self._func_counter["Normal"] = 0
            else:
                self._func_counter["Normal"] += 1
            counter = self._func_counter["Normal"]
            output_varname = f"Normal_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Normal({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Normal()')

    def normvect(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the normalized unit vector for the vector specified

        Args:
            source_parts:
                Any part(s) or a part number.
            vector:
                A vector variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`NormVect` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("NormVect"):
                self._func_counter["NormVect"] = 0
            else:
                self._func_counter["NormVect"] += 1
            counter = self._func_counter["NormVect"]
            output_varname = f"NormVect_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'NormVect({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=NormVect()')

    def normc(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], pressure: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], viscosity: Union['float', 'ENS_VAR', str, int], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the normal constraint defined as the surface integral as a function of pressure, velocity, and viscosity

        Args:
            source_parts:
                Any 2D part(s) or a part number.
            pressure:
                A pressure variable.
            velocity:
                A velocity variable.
            viscosity:
                A viscosity variable or a value.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`NormC` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['pressure', 'velocity', 'viscosity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("NormC"):
                self._func_counter["NormC"] = 0
            else:
                self._func_counter["NormC"] += 1
            counter = self._func_counter["NormC"]
            output_varname = f"NormC_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'NormC({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=NormC()')

    def offsetfield(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the offset in the surface normal direction (from the border if 3D)

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`OffsetField` for function details.
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
            if not self._func_counter.get("OffsetField"):
                self._func_counter["OffsetField"] = 0
            else:
                self._func_counter["OffsetField"] += 1
            counter = self._func_counter["OffsetField"]
            output_varname = f"OffsetField_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'OffsetField({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=OffsetField()')

    def offsetvar(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_or_vector: Union['ENS_VAR', str, int], offset: float, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a variable defined as the variable value offset in the surface normal direction into a field.  It provides a way to place near surface values onto the surface.

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            scalar_or_vector:
                A scalar or vector variable.
            offset:
                An offset value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`OffsetVar` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_or_vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("OffsetVar"):
                self._func_counter["OffsetVar"] = 0
            else:
                self._func_counter["OffsetVar"] += 1
            counter = self._func_counter["OffsetVar"]
            output_varname = f"OffsetVar_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'OffsetVar({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=OffsetVar()')

    def partnumber(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a part or case constant variable defined as the part id number.  Sometimes useful for viewing decomposed data.

        Args:
            source_parts:
                Any part(s) or a part #.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PartNumber` for function details.
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
            if not self._func_counter.get("PartNumber"):
                self._func_counter["PartNumber"] = 0
            else:
                self._func_counter["PartNumber"] += 1
            counter = self._func_counter["PartNumber"]
            output_varname = f"PartNumber_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PartNumber({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PartNumber()')

    def pres(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as Pressure where Pressure is computed from the density, total energy, velocity, and ratio of specific heats

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Pres` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Pres"):
                self._func_counter["Pres"] = 0
            else:
                self._func_counter["Pres"] += 1
            counter = self._func_counter["Pres"]
            output_varname = f"Pres_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Pres({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Pres()')

    def prescoef(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], free_velocity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the Pressure-Coefficient as a function of density, total energy, velocity, ratio of specific heats, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            free_velocity:
                A 'freestream velocity magnitude' variable  or value(>=1.0)
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresCoef` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'free_velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresCoef"):
                self._func_counter["PresCoef"] = 0
            else:
                self._func_counter["PresCoef"] += 1
            counter = self._func_counter["PresCoef"]
            output_varname = f"PresCoef_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresCoef({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresCoef()')

    def presdynam(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the dynamic pressure as a function of the density and velocity)

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresDynam` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresDynam"):
                self._func_counter["PresDynam"] = 0
            else:
                self._func_counter["PresDynam"] += 1
            counter = self._func_counter["PresDynam"]
            output_varname = f"PresDynam_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresDynam({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresDynam()')

    def preslognorm(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the log (ln) of the pressure divided by the freestream pressure as a function of density, total energy, velocity, ratio of specific heats, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresLogNorm` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresLogNorm"):
                self._func_counter["PresLogNorm"] = 0
            else:
                self._func_counter["PresLogNorm"] += 1
            counter = self._func_counter["PresLogNorm"]
            output_varname = f"PresLogNorm_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresLogNorm({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresLogNorm()')

    def presnorm(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the normalized pressure = pressure divided by freestream pressure as a function of density, total energy, velocity, ratio of specific heats, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresNorm` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresNorm"):
                self._func_counter["PresNorm"] = 0
            else:
                self._func_counter["PresNorm"] += 1
            counter = self._func_counter["PresNorm"]
            output_varname = f"PresNorm_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresNorm({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresNorm()')

    def presnormstag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], free_velocity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the normalized stagnation pressure = stagnation pressure divided by freestream stagnation pressure as a function of density, total energy, velocity, ratio of specific heats, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            free_velocity:
                A 'freestream velocity magnitude' variable  or value(>=1.0)
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresNormStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'free_velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresNormStag"):
                self._func_counter["PresNormStag"] = 0
            else:
                self._func_counter["PresNormStag"] += 1
            counter = self._func_counter["PresNormStag"]
            output_varname = f"PresNormStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresNormStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresNormStag()')

    def prespitot(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the pitot pressure as a function of density, total energy, velocity, ratio of specific heats

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresPitot` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresPitot"):
                self._func_counter["PresPitot"] = 0
            else:
                self._func_counter["PresPitot"] += 1
            counter = self._func_counter["PresPitot"]
            output_varname = f"PresPitot_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresPitot({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresPitot()')

    def prespitotratio(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the pitot pressure ratio as a function of density, total energy, velocity, ratio of specific heats, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresPitotRatio` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresPitotRatio"):
                self._func_counter["PresPitotRatio"] = 0
            else:
                self._func_counter["PresPitotRatio"] += 1
            counter = self._func_counter["PresPitotRatio"]
            output_varname = f"PresPitotRatio_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresPitotRatio({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresPitotRatio()')

    def presstag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the stagnation pressure as a function of density, total energy, velocity, and ratio of specific heats

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresStag"):
                self._func_counter["PresStag"] = 0
            else:
                self._func_counter["PresStag"] += 1
            counter = self._func_counter["PresStag"]
            output_varname = f"PresStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresStag()')

    def presstagcoef(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], free_velocity: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the stagnation pressure coefficient as a function of density, total energy, velocity, ratio of specific heats, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            free_velocity:
                A 'freestream velocity magnitude' variable  or value(>=1.0)
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresStagCoef` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'free_velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresStagCoef"):
                self._func_counter["PresStagCoef"] = 0
            else:
                self._func_counter["PresStagCoef"] += 1
            counter = self._func_counter["PresStagCoef"]
            output_varname = f"PresStagCoef_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresStagCoef({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresStagCoef()')

    def prest(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], pressure: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the total pressure = pressure + density*velocity^2/2

        Args:
            source_parts:
                Any part(s) or a part number.
            pressure:
                A pressure variable.
            velocity:
                A velocity variable.
            density:
                A density variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`PresT` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['pressure', 'velocity', 'density']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("PresT"):
                self._func_counter["PresT"] = 0
            else:
                self._func_counter["PresT"] += 1
            counter = self._func_counter["PresT"]
            output_varname = f"PresT_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'PresT({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=PresT()')

    def radiograph_grid(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], dir_X: float, dir_Y: float, dir_Z: float, num_points: int, variable: Union['ENS_VAR', str, int], component: str = '[X]', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the integration of a variable in the direction specified through the model given a specified integration step

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            dir_X:
                Enter X direction component value.
            dir_Y:
                Enter Y direction component value.
            dir_Z:
                Enter Z direction component value.
            num_points:
                Enter number of points to use in integration direction.
            variable:
                A scalar or vector variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Radiograph_grid` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Radiograph_grid"):
                self._func_counter["Radiograph_grid"] = 0
            else:
                self._func_counter["Radiograph_grid"] += 1
            counter = self._func_counter["Radiograph_grid"]
            output_varname = f"Radiograph_grid_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Radiograph_grid({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Radiograph_grid()')

    def radiograph_mesh(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], dir_X: float, dir_Y: float, dir_Z: float, variable: Union['ENS_VAR', str, int], component: str = '[X]', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar variable defined as the integration of the variable in the direction specified through the model given

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            dir_X:
                Enter X direction component value.
            dir_Y:
                Enter Y direction component value.
            dir_Z:
                Enter Z direction component value.
            variable:
                A scalar or vector variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Radiograph_mesh` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Radiograph_mesh"):
                self._func_counter["Radiograph_mesh"] = 0
            else:
                self._func_counter["Radiograph_mesh"] += 1
            counter = self._func_counter["Radiograph_mesh"]
            output_varname = f"Radiograph_mesh_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Radiograph_mesh({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Radiograph_mesh()')

    def recttocyl(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector: Union['ENS_VAR', str, int], frame_number: int, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the radial, tangential, and z component according to specified frame.  Intended for calculation purposes

        Args:
            source_parts:
                Any part(s) or a part number.
            vector:
                A vector variable.
            frame_number:
                Specify the frame number to use for the cylindrical coordinate system.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`RectToCyl` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("RectToCyl"):
                self._func_counter["RectToCyl"] = 0
            else:
                self._func_counter["RectToCyl"] += 1
            counter = self._func_counter["RectToCyl"]
            output_varname = f"RectToCyl_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'RectToCyl({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=RectToCyl()')

    def servernumber(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per element scalar defined as the server number that contains the element.  Useful for decomposed data debugging

        Args:
            source_parts:
                Any part(s) or a part #.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ServerNumber` for function details.
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
            if not self._func_counter.get("ServerNumber"):
                self._func_counter["ServerNumber"] = 0
            else:
                self._func_counter["ServerNumber"] += 1
            counter = self._func_counter["ServerNumber"]
            output_varname = f"ServerNumber_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ServerNumber({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ServerNumber()')

    def shockplot3d(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as shock using the plot3d definition.  Function of density, total energy, velocity, and ratio of specific heats

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`ShockPlot3d` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("ShockPlot3d"):
                self._func_counter["ShockPlot3d"] = 0
            else:
                self._func_counter["ShockPlot3d"] += 1
            counter = self._func_counter["ShockPlot3d"]
            output_varname = f"ShockPlot3d_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'ShockPlot3d({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=ShockPlot3d()')

    def smoothmesh(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], number_of_passes: int, smoothing_weight: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a per node vector when applied as a displacement to the part will produce a smoother surface.  Useful for smoothing isosurfaces for example

        Args:
            source_parts:
                Any 1D or 2D part(s) or a part number.
            number_of_passes:
                Enter the number of passes to use
            smoothing_weight:
                A constant or a nodal scalar weighting factor
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`SmoothMesh` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['smoothing_weight']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("SmoothMesh"):
                self._func_counter["SmoothMesh"] = 0
            else:
                self._func_counter["SmoothMesh"] += 1
            counter = self._func_counter["SmoothMesh"]
            output_varname = f"SmoothMesh_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'SmoothMesh({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=SmoothMesh()')

    def sonicspeed(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the sonic speed.  Function of density, total energy, velocity, and ratio of specific heats

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`SonicSpeed` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("SonicSpeed"):
                self._func_counter["SonicSpeed"] = 0
            else:
                self._func_counter["SonicSpeed"] += 1
            counter = self._func_counter["SonicSpeed"]
            output_varname = f"SonicSpeed_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'SonicSpeed({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=SonicSpeed()')

    def spamean(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], component: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the volume (or area) weighted mean of the variable specified

        Args:
            source_parts:
                Any part(s) or a part number.
            variable:
                A scalar or vector variable.
            component:
                A vector component [X], [Y], [Z] or [] for magnitude.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`SpaMean` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("SpaMean"):
                self._func_counter["SpaMean"] = 0
            else:
                self._func_counter["SpaMean"] += 1
            counter = self._func_counter["SpaMean"]
            output_varname = f"SpaMean_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'SpaMean({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=SpaMean()')

    def spameanweighted(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], component_1: str = '[X]', weight: Optional[Union['ENS_VAR', str, int]] = None, component_2: str = '[X]', result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the volume (or area) weighted mean of the variable specified.  Volume or area is weighted by a second variable.

        Args:
            source_parts:
                Any part(s) or a part number.
            variable:
                A scalar or vector variable.
            component_1:
                A vector component [X], [Y], [Z] or [] for magnitude.
            weight:
                A scalar or vector variable.
            component_2:
                A vector component [X], [Y], [Z] or [] for magnitude.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`SpaMeanWeighted` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable', 'weight']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("SpaMeanWeighted"):
                self._func_counter["SpaMeanWeighted"] = 0
            else:
                self._func_counter["SpaMeanWeighted"] += 1
            counter = self._func_counter["SpaMeanWeighted"]
            output_varname = f"SpaMeanWeighted_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'SpaMeanWeighted({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=SpaMeanWeighted()')

    def speed(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as speed = square root of the sum of the velocity components squared

        Args:
            source_parts:
                Any part(s) or a part number.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Speed` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Speed"):
                self._func_counter["Speed"] = 0
            else:
                self._func_counter["Speed"] += 1
            counter = self._func_counter["Speed"]
            output_varname = f"Speed_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Speed({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Speed()')

    def statmoment(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], opt_variable: Union['float', 'ENS_VAR', str, int], which: int = 0, result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant variable defined as the statistics function over all nodes or elements of the parts selected.  The statistical functions available are sum, mean, variance, skew, and kurtosis

        Args:
            source_parts:
                Any part(s) or a part number.
            opt_variable:
                A scalar variable or a value.
            which:
                Select the function to compute. 0=sum, 1=mean, 2=variance, 3=skewness, 4=kurtosis.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`StatMoment` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['opt_variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("StatMoment"):
                self._func_counter["StatMoment"] = 0
            else:
                self._func_counter["StatMoment"] += 1
            counter = self._func_counter["StatMoment"]
            output_varname = f"StatMoment_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'StatMoment({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=StatMoment()')

    def statregspa(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], y: Union['float', 'ENS_VAR', str, int], x0: Union['float', 'ENS_VAR', str, int], x1: Union['float', 'ENS_VAR', str, int], x2: Union['float', 'ENS_VAR', str, int], x3: Union['float', 'ENS_VAR', str, int], x4: Union['float', 'ENS_VAR', str, int], weight: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant value defined as the multi-variate linear regression statistics for the variable selected

        Args:
            source_parts:
                Any part(s) or a part number.
            y:
                A scalar variable or a value.
            x0:
                A scalar variable or a value.
            x1:
                A scalar variable or a value.
            x2:
                A scalar variable or a value.
            x3:
                A scalar variable or a value.
            x4:
                A scalar variable or a value.
            weight:
                A scalar variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`StatRegSpa` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['y', 'x0', 'x1', 'x2', 'x3', 'x4', 'weight']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("StatRegSpa"):
                self._func_counter["StatRegSpa"] = 0
            else:
                self._func_counter["StatRegSpa"] += 1
            counter = self._func_counter["StatRegSpa"]
            output_varname = f"StatRegSpa_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'StatRegSpa({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=StatRegSpa()')

    def statregval1(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], regression_var: Union['float', 'ENS_VAR', str, int], which_stat: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant value defined as the statistics from a StatReg linear regression.  The options are sum of squares error, sum of squares modal, and R-squared

        Args:
            source_parts:
                Any part(s) or a part number.
            regression_var:
                Select the constant output variable from a StatReg*() function.
            which_stat:
                Enter the number of the statistic to output. 0=SS Error 1=SS Total 2=SS Model 3=R squared.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`StatRegVal1` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['regression_var']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("StatRegVal1"):
                self._func_counter["StatRegVal1"] = 0
            else:
                self._func_counter["StatRegVal1"] += 1
            counter = self._func_counter["StatRegVal1"]
            output_varname = f"StatRegVal1_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'StatRegVal1({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=StatRegVal1()')

    def statregval2(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], regression_var: Union['float', 'ENS_VAR', str, int], which_stat: int = 0, var_select: Optional[int] = None, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a constant value defined as the statistics from a StatReg linear regression given a specified coefficient.  The options are the estimated coefficient, sum of squares for the variable, partial sum of squares of the variable, and standard error for the coefficient

        Args:
            source_parts:
                Any part(s) or a part number.
            regression_var:
                Select the constant output variable from a StatReg*() function.
            which_stat:
                Enter the number of the statistic to output. 0=Coefficient 1=SS Variable 2=Partial SS Variable 3=Coeficient stderr.
            var_select:
                Select the variable for which to return the statistic. 0=x0, 1=x1, 2=x2 3=x3, 4=x4.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`StatRegVal2` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['regression_var']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("StatRegVal2"):
                self._func_counter["StatRegVal2"] = 0
            else:
                self._func_counter["StatRegVal2"] += 1
            counter = self._func_counter["StatRegVal2"]
            output_varname = f"StatRegVal2_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'StatRegVal2({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=StatRegVal2()')

    def swirl(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the swirl.  Function of density and velocity

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Swirl` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Swirl"):
                self._func_counter["Swirl"] = 0
            else:
                self._func_counter["Swirl"] += 1
            counter = self._func_counter["Swirl"]
            output_varname = f"Swirl_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Swirl({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Swirl()')

    def temperature(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], gas: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as temperature.  Function of density, total energy, velocity, ratio of specific heats, and the gas constant

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            gas:
                A gas constant variable or value(>0.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Temperature` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'gas']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Temperature"):
                self._func_counter["Temperature"] = 0
            else:
                self._func_counter["Temperature"] += 1
            counter = self._func_counter["Temperature"]
            output_varname = f"Temperature_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Temperature({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Temperature()')

    def temperlognorm(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], gas: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the natural log of the normalized temperature.  Function of density, total energy, velocity, ratio of specific heats, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            gas:
                A gas constant variable or value(>0.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TemperLogNorm` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'gas']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TemperLogNorm"):
                self._func_counter["TemperLogNorm"] = 0
            else:
                self._func_counter["TemperLogNorm"] += 1
            counter = self._func_counter["TemperLogNorm"]
            output_varname = f"TemperLogNorm_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TemperLogNorm({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TemperLogNorm()')

    def tempernorm(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], gas: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the normalized temperature = temperature/freestream temperature.  Function of density, total energy, velocity, ratio of specific heats, gas constant and freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            gas:
                A gas constant variable or value(>0.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TemperNorm` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'gas']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TemperNorm"):
                self._func_counter["TemperNorm"] = 0
            else:
                self._func_counter["TemperNorm"] += 1
            counter = self._func_counter["TemperNorm"]
            output_varname = f"TemperNorm_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TemperNorm({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TemperNorm()')

    def tempernormstag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], free_density: Union['float', 'ENS_VAR', str, int], free_speed_of_sound: Union['float', 'ENS_VAR', str, int], free_velocity: Union['float', 'ENS_VAR', str, int], gas: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the normalized stagnation temperature = stagnation temperature/freestream stagnation temperature.  Function of density, total energy, velocity, ratio of specific heats, gas constant, and the freestream values

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            free_density:
                A 'freestream density' variable or  a value(>=1.0).
            free_speed_of_sound:
                A 'freestream speed of sound' variable or a value(>=1.0).
            free_velocity:
                A 'freestream velocity magnitude' variable  or value(>=1.0)
            gas:
                A gas constant variable or value(>0.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TemperNormStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'free_density', 'free_speed_of_sound', 'free_velocity', 'gas']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TemperNormStag"):
                self._func_counter["TemperNormStag"] = 0
            else:
                self._func_counter["TemperNormStag"] += 1
            counter = self._func_counter["TemperNormStag"]
            output_varname = f"TemperNormStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TemperNormStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TemperNormStag()')

    def temperstag(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], density: Union['float', 'ENS_VAR', str, int], total_energy: Union['ENS_VAR', str, int], velocity: Union['ENS_VAR', str, int], ratio: Union['float', 'ENS_VAR', str, int], gas: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the stagnation temperature.  Function of density, total energy, velocity, ratio of specific heats, and gas constant

        Args:
            source_parts:
                Any part(s) or a part number.
            density:
                A density variable or a value.
            total_energy:
                A total energy variable.
            velocity:
                A velocity variable.
            ratio:
                A 'ratio of specific heats' variable or a value.
            gas:
                A gas constant variable or value(>0.0).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TemperStag` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['density', 'total_energy', 'velocity', 'ratio', 'gas']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TemperStag"):
                self._func_counter["TemperStag"] = 0
            else:
                self._func_counter["TemperStag"] += 1
            counter = self._func_counter["TemperStag"]
            output_varname = f"TemperStag_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TemperStag({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TemperStag()')

    def tempmean(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], t1: int, t2: int, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a variable defined as the temporal mean of the specified variable at the nodes/elements given a range of timesteps

        Args:
            source_parts:
                Any model part(s) or a model part number.
            variable:
                A scalar, vector or constant variable.
            t1:
                A beginning time step.
            t2:
                An ending time step.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TempMean` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TempMean"):
                self._func_counter["TempMean"] = 0
            else:
                self._func_counter["TempMean"] += 1
            counter = self._func_counter["TempMean"]
            output_varname = f"TempMean_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TempMean({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TempMean()')

    def tempminmaxfield(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], variable: Union['ENS_VAR', str, int], t1: int, t2: int, flag: int, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a variable defined as the minimum or maximum (user choice) of the specified variable at the nodes/elements given a range of timesteps

        Args:
            source_parts:
                Any model part(s) or a model part number.
            variable:
                A scalar or vector variable.
            t1:
                A beginning time step.
            t2:
                An ending time step.
            flag:
                Enter 0 for minium or 1 for maximum
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TempMinmaxField` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['variable']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TempMinmaxField"):
                self._func_counter["TempMinmaxField"] = 0
            else:
                self._func_counter["TempMinmaxField"] += 1
            counter = self._func_counter["TempMinmaxField"]
            output_varname = f"TempMinmaxField_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TempMinmaxField({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TempMinmaxField()')

    def tensorcomponent(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], tensor: Union['ENS_VAR', str, int], row1_3: int = 1, col1_3: int = 1, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the specified component of a tensor

        Args:
            source_parts:
                Any part(s) or a part number.
            tensor:
                A tensor variable.
            row1_3:
                A the row(ie. 1-3) of the tensor to extract.
            col1_3:
                A the column(ie. 1-3) of the tensor to extract.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorComponent` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['tensor']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorComponent"):
                self._func_counter["TensorComponent"] = 0
            else:
                self._func_counter["TensorComponent"] += 1
            counter = self._func_counter["TensorComponent"]
            output_varname = f"TensorComponent_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorComponent({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorComponent()')

    def tensordeterminant(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], T11: Union['ENS_VAR', str, int], T22: Union['ENS_VAR', str, int], T33: Union['ENS_VAR', str, int], T12: Union['ENS_VAR', str, int], T13: Union['ENS_VAR', str, int], T23: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the determinant of a tensor.  Tensor can be defined as 3 principal scalars or 6 tensor scalar components

        Args:
            source_parts:
                Any part(s) or a part number.
            T11:
                A tensor, first principal scalar(sigma_1), or tensor scalar component(T11).
            T22:
                Select the second principal scalar(sigma_2) or tensor scalar component(T22).
            T33:
                Select the third principal scalar(sigma_3) or tensor scalar component(T33).
            T12:
                Select tensor scalar component(T12) or a -1 if doing principals.
            T13:
                Select tensor scalar component(T13) or a -1 if doing principals.
            T23:
                Select tensor scalar component(T23) or a -1 if doing principals.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorDeterminant` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['T11', 'T22', 'T33', 'T12', 'T13', 'T23']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorDeterminant"):
                self._func_counter["TensorDeterminant"] = 0
            else:
                self._func_counter["TensorDeterminant"] += 1
            counter = self._func_counter["TensorDeterminant"]
            output_varname = f"TensorDeterminant_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorDeterminant({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorDeterminant()')

    def tensoreigenvalue(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], tensor: Union['ENS_VAR', str, int], num1_3: int = 1, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the eigenvalue (1 to 3) of the specified tensor

        Args:
            source_parts:
                Any part(s) or a part number.
            tensor:
                A tensor variable.
            num1_3:
                Enter which eigenvalue number(ie. 1-3).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorEigenvalue` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['tensor']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorEigenvalue"):
                self._func_counter["TensorEigenvalue"] = 0
            else:
                self._func_counter["TensorEigenvalue"] += 1
            counter = self._func_counter["TensorEigenvalue"]
            output_varname = f"TensorEigenvalue_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorEigenvalue({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorEigenvalue()')

    def tensoreigenvector(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], tensor: Union['ENS_VAR', str, int], num1_3: int = 1, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the first, second, or third eigenvector of the specified tensor

        Args:
            source_parts:
                Any part(s) or a part number.
            tensor:
                A tensor variable.
            num1_3:
                Enter which eigenvector number(ie. 1-3).
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorEigenvector` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['tensor']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorEigenvector"):
                self._func_counter["TensorEigenvector"] = 0
            else:
                self._func_counter["TensorEigenvector"] += 1
            counter = self._func_counter["TensorEigenvector"]
            output_varname = f"TensorEigenvector_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorEigenvector({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorEigenvector()')

    def tensormake(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_1: Union['ENS_VAR', str, int], scalar_2: Union['ENS_VAR', str, int], scalar_3: Union['ENS_VAR', str, int], scalar_4: Union['ENS_VAR', str, int], scalar_5: Union['ENS_VAR', str, int], scalar_6: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a symmetric tensor variable from six scalars. [The 6 tensor components order is TC11, TC22, TC33, TC12, TC13, TC23]

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_1:
                A scalar variable for component T23.
            scalar_2:
                A scalar variable for component T23.
            scalar_3:
                A scalar variable for component T23.
            scalar_4:
                A scalar variable for component T23.
            scalar_5:
                A scalar variable for component T23.
            scalar_6:
                A scalar variable for component T23.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorMake` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_1', 'scalar_2', 'scalar_3', 'scalar_4', 'scalar_5', 'scalar_6']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorMake"):
                self._func_counter["TensorMake"] = 0
            else:
                self._func_counter["TensorMake"] += 1
            counter = self._func_counter["TensorMake"]
            output_varname = f"TensorMake_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorMake({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorMake()')

    def tensormakeasym(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], scalar_1: Union['ENS_VAR', str, int], scalar_2: Union['ENS_VAR', str, int], scalar_3: Union['ENS_VAR', str, int], scalar_4: Union['ENS_VAR', str, int], scalar_5: Union['ENS_VAR', str, int], scalar_6: Union['ENS_VAR', str, int], scalar_7: Union['ENS_VAR', str, int], scalar_8: Union['ENS_VAR', str, int], scalar_9: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes an asymmetric tensor variable from nine scalars. [The 9 tensor components order is TC11,TC12,TC13, TC21,TC22,TC23, TC31,TC32,TC33]

        Args:
            source_parts:
                Any part(s) or a part number.
            scalar_1:
                A scalar variable for component T33.
            scalar_2:
                A scalar variable for component T33.
            scalar_3:
                A scalar variable for component T33.
            scalar_4:
                A scalar variable for component T33.
            scalar_5:
                A scalar variable for component T33.
            scalar_6:
                A scalar variable for component T33.
            scalar_7:
                A scalar variable for component T33.
            scalar_8:
                A scalar variable for component T33.
            scalar_9:
                A scalar variable for component T33.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorMakeAsym` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['scalar_1', 'scalar_2', 'scalar_3', 'scalar_4', 'scalar_5', 'scalar_6', 'scalar_7', 'scalar_8', 'scalar_9']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorMakeAsym"):
                self._func_counter["TensorMakeAsym"] = 0
            else:
                self._func_counter["TensorMakeAsym"] += 1
            counter = self._func_counter["TensorMakeAsym"]
            output_varname = f"TensorMakeAsym_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorMakeAsym({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorMakeAsym()')

    def tensortresca(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], T11: Union['ENS_VAR', str, int], T22: Union['ENS_VAR', str, int], T33: Union['ENS_VAR', str, int], T12: Union['ENS_VAR', str, int], T13: Union['ENS_VAR', str, int], T23: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the tresca of the given tensor, three principals, or six tensor components. [If components specified the order is TC11, TC22, TC33, TC12, TC13, TC23]

        Args:
            source_parts:
                Any part(s) or a part number.
            T11:
                A tensor, first principal scalar(sigma_1), or tensor scalar component(T11).
            T22:
                Select the second principal scalar(sigma_2) or tensor scalar component(T22).
            T33:
                Select the third principal scalar(sigma_3) or tensor scalar component(T33).
            T12:
                Select tensor scalar component(T12) or a -1 if doing principals.
            T13:
                Select tensor scalar component(T13) or a -1 if doing principals.
            T23:
                Select tensor scalar component(T23) or a -1 if doing principals.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorTresca` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['T11', 'T22', 'T33', 'T12', 'T13', 'T23']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorTresca"):
                self._func_counter["TensorTresca"] = 0
            else:
                self._func_counter["TensorTresca"] += 1
            counter = self._func_counter["TensorTresca"]
            output_varname = f"TensorTresca_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorTresca({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorTresca()')

    def tensorvonmises(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], T11: Union['ENS_VAR', str, int], T22: Union['ENS_VAR', str, int], T33: Union['ENS_VAR', str, int], T12: Union['ENS_VAR', str, int], T13: Union['ENS_VAR', str, int], T23: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a scalar variable defined as the von-mises of the  given tensor, three principals, or six tensor components. [If components specified the order is TC11, TC22, TC33, TC12, TC13, TC23]

        Args:
            source_parts:
                Any part(s) or a part number.
            T11:
                A tensor, first principal scalar(sigma_1), or tensor scalar component(T11).
            T22:
                Select the second principal scalar(sigma_2) or tensor scalar component(T22).
            T33:
                Select the third principal scalar(sigma_3) or tensor scalar component(T33).
            T12:
                Select tensor scalar component(T12) or a -1 if doing principals.
            T13:
                Select tensor scalar component(T13) or a -1 if doing principals.
            T23:
                Select tensor scalar component(T23) or a -1 if doing principals.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`TensorVonMises` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['T11', 'T22', 'T33', 'T12', 'T13', 'T23']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("TensorVonMises"):
                self._func_counter["TensorVonMises"] = 0
            else:
                self._func_counter["TensorVonMises"] += 1
            counter = self._func_counter["TensorVonMises"]
            output_varname = f"TensorVonMises_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'TensorVonMises({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=TensorVonMises()')

    def vector1dprojection(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector_to_project: Union['ENS_VAR', str, int], which_direction: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the specified vector variable projected into the 1D part's tangent or normal direction

        Args:
            source_parts:
                Any 1D part(s) or a part number.
            vector_to_project:
                A vector variable.
            which_direction:
                Select the direction to project.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Vector1DProjection` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector_to_project']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Vector1DProjection"):
                self._func_counter["Vector1DProjection"] = 0
            else:
                self._func_counter["Vector1DProjection"] += 1
            counter = self._func_counter["Vector1DProjection"]
            output_varname = f"Vector1DProjection_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Vector1DProjection({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Vector1DProjection()')

    def vectorcylprojection(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector_to_project: Union['ENS_VAR', str, int], frame_number: int, which_axis: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the specified vector variable projected onto a frame's axis, radial, or theta direction

        Args:
            source_parts:
                Any part(s) or a part number.
            vector_to_project:
                A vector variable.
            frame_number:
                A constant variable name or a constant value.
            which_axis:
                Select the cylindrical axis to compute.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`VectorCylProjection` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector_to_project']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("VectorCylProjection"):
                self._func_counter["VectorCylProjection"] = 0
            else:
                self._func_counter["VectorCylProjection"] += 1
            counter = self._func_counter["VectorCylProjection"]
            output_varname = f"VectorCylProjection_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'VectorCylProjection({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=VectorCylProjection()')

    def vectorrectprojection(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], vector_to_project: Union['ENS_VAR', str, int], frame_number: int, which_axis: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the specified vector variable projected onto a frame's x, y, or z direction

        Args:
            source_parts:
                Any part(s) or a part number.
            vector_to_project:
                A vector variable.
            frame_number:
                A constant variable name or a constant value.
            which_axis:
                Select the rectangular axis to compute.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`VectorRectProjection` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['vector_to_project']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("VectorRectProjection"):
                self._func_counter["VectorRectProjection"] = 0
            else:
                self._func_counter["VectorRectProjection"] += 1
            counter = self._func_counter["VectorRectProjection"]
            output_varname = f"VectorRectProjection_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'VectorRectProjection({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=VectorRectProjection()')

    def velo(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], momentum: Union['ENS_VAR', str, int], density: Union['float', 'ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as velocity = momentum/density

        Args:
            source_parts:
                Any part(s) or a part number.
            momentum:
                A momentum variable.
            density:
                A density variable or a value.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Velo` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['momentum', 'density']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Velo"):
                self._func_counter["Velo"] = 0
            else:
                self._func_counter["Velo"] += 1
            counter = self._func_counter["Velo"]
            output_varname = f"Velo_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Velo({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Velo()')

    def vol(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], result_type: str = 'Compute_Per_case', output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes the volume of the parts specified

        Args:
            source_parts:
                Any 3D part(s) or a part number.
            result_type:
                Per/Case or Per/Part Results
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Vol` for function details.
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
            if not self._func_counter.get("Vol"):
                self._func_counter["Vol"] = 0
            else:
                self._func_counter["Vol"] += 1
            counter = self._func_counter["Vol"]
            output_varname = f"Vol_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Vol({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Vol()')

    def vort(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a vector variable defined as the vorticity as a function of velocity

        Args:
            source_parts:
                Any 2D or 3D part(s) or a part number.
            velocity:
                A velocity variable.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`Vort` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("Vort"):
                self._func_counter["Vort"] = 0
            else:
                self._func_counter["Vort"] += 1
            counter = self._func_counter["Vort"]
            output_varname = f"Vort_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'Vort({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=Vort()')

    def vortgamma(self, source_parts: Union[List['ENS_PART'], List[int], List[str], 'ENS_PART', int, str], velocity: Union['ENS_VAR', str, int], gammafunc: int = 1, proximity_radius: Optional[Union['float', 'ENS_VAR', str, int]] = None, proximity_option: int = 0, output_varname: Optional[str] = None) -> 'ENS_VAR':
        """Computes a dimensionless scalar variable on a 2D clip part, whose value is the vorticity-gamma function

        Args:
            source_parts:
                Any 2D clip part(s) or a part number.
            velocity:
                A velocity variable.
            gammafunc:
                Select the vorticity gamma function id.
            proximity_radius:
                Specify a proximity radius (model units) to be used around each base node/cell for its proximity area. A constant value, or select a constant or scalar variable.
            proximity_option:
                Include all cells containing the target node/cell, plus cells where 'all' or 'any' of their nodes are within the target node proximity radius.
            output_varname:
                The name of the newly created variable

        Returns:
            New ENS_VAR instance or None

        Note:
            See :any:`VortGamma` for function details.
        """
        params_dict = {x:y for x,y in locals().items() if x != "self" and x != "output_varname"}
        sources = None
        if params_dict.get("source_parts"):
            params_dict["source_parts"] = "plist"
            part_numbers = [convert_part(self._ensight, p) for p in source_parts]
            sources = self._ensight.objs.core.PARTS.find(part_numbers,attr="PARTNUMBER")
        for var_arg in ['velocity', 'proximity_radius']:
            if isinstance(params_dict.get(var_arg), int):
                if params_dict.get(var_arg) >= 0:
                    params_dict[var_arg] = self._ensight.objs.core.VARIABLES.find([params_dict.get(var_arg)], attr="ID")[0].DESCRIPTION
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, ENS_VAR):
                params_dict[param_name] = param_val.DESCRIPTION
            if param_val is None:
                params_dict[param_name] = -1
        if not output_varname:
            if not self._func_counter.get("VortGamma"):
                self._func_counter["VortGamma"] = 0
            else:
                self._func_counter["VortGamma"] += 1
            counter = self._func_counter["VortGamma"]
            output_varname = f"VortGamma_{counter}"
        if len(params_dict.values()) > 0:
            val = repr(list(params_dict.values()))[1:-1].replace("'", "")
            return self._ensight.objs.core.create_variable(f'{output_varname}', f'VortGamma({val})', sources=sources)
        return self._ensight.variables.evaluate(f'{output_varname}=VortGamma()')



ens_calculator.area.meta = {'class': ['Function', 'Geometry'], 'vartype': ['const', 'const_per_part'], 'name': 'Area', 'dimensions': 'LL'}
ens_calculator.bl_agradofvelmag.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'BL_aGradOfVelMag', 'dimensions': '/T'}
ens_calculator.bl_cfedge.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_CfEdge', 'dimensions': '/'}
ens_calculator.bl_cfwall.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_CfWall', 'dimensions': '/'}
ens_calculator.bl_cfwallcmp.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_CfWallCmp', 'dimensions': '/'}
ens_calculator.bl_cfwalltau.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_CfWallTau', 'dimensions': 'M/LTT'}
ens_calculator.bl_dispthick.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_DispThick', 'dimensions': 'L'}
ens_calculator.bl_disttovalue.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_DistToValue', 'dimensions': 'L'}
ens_calculator.bl_momethick.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_MomeThick', 'dimensions': 'L'}
ens_calculator.bl_scalar.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_Scalar', 'dimensions': 'c'}
ens_calculator.bl_recoverythick.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_RecoveryThick', 'dimensions': 'L'}
ens_calculator.bl_thick.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_Thick', 'dimensions': 'L'}
ens_calculator.bl_velocityatedge.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'BL_VelocityAtEdge', 'dimensions': 'L/T'}
ens_calculator.bl_y1plus.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_Y1Plus', 'dimensions': 'L/T'}
ens_calculator.bl_y1plusdist.meta = {'class': ['Function', 'Boundary Layer'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'BL_Y1PlusDist', 'dimensions': 'L'}
ens_calculator.casemap.meta = {'class': ['Function', 'Variable Manipulation', 'CaseMap'], 'vartype': ['scalar', 'vector', 'tensor', 'nodal', 'element'], 'name': 'CaseMap', 'dimensions': None}
ens_calculator.casemapdiff.meta = {'class': ['Function', 'Variable Manipulation', 'CaseMap'], 'vartype': ['scalar', 'vector', 'tensor', 'nodal', 'element'], 'name': 'CaseMapDiff', 'dimensions': 'c'}
ens_calculator.casemapimage.meta = {'class': ['Function', 'Variable Manipulation', 'CaseMap'], 'vartype': ['scalar', 'nodal'], 'name': 'CaseMapImage', 'dimensions': 'c'}
ens_calculator.coeff.meta = {'class': ['Function', 'Calculus'], 'vartype': ['scalar', 'const', 'const_per_part'], 'name': 'Coeff', 'dimensions': 'ab'}
ens_calculator.cmplx.meta = {'class': ['Function'], 'vartype': ['scalar', 'vector', 'nodal', 'element'], 'name': 'Cmplx', 'dimensions': '/'}
ens_calculator.cmplxarg.meta = {'class': ['Function'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'CmplxArg', 'dimensions': '/'}
ens_calculator.cmplxconj.meta = {'class': ['Function'], 'vartype': ['scalar', 'vector', 'nodal', 'element'], 'name': 'CmplxConj', 'dimensions': 'b'}
ens_calculator.cmplximag.meta = {'class': ['Function'], 'vartype': ['scalar', 'vector', 'nodal', 'element'], 'name': 'CmplxImag', 'dimensions': 'b'}
ens_calculator.cmplxmodu.meta = {'class': ['Function'], 'vartype': ['scalar', 'vector', 'nodal', 'element'], 'name': 'CmplxModu', 'dimensions': 'b'}
ens_calculator.cmplxreal.meta = {'class': ['Function'], 'vartype': ['scalar', 'vector', 'nodal', 'element'], 'name': 'CmplxReal', 'dimensions': 'b'}
ens_calculator.cmplxtransresp.meta = {'class': ['Function'], 'vartype': ['scalar', 'vector', 'nodal', 'element'], 'name': 'CmplxTransResp', 'dimensions': 'b'}
ens_calculator.constantperpart.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['const_per_part'], 'name': 'ConstantPerPart', 'dimensions': 'b'}
ens_calculator.curl.meta = {'class': ['Function', 'Calculus'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Curl', 'dimensions': 'b/L'}
ens_calculator.defect_bulkvolume.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'Defect_BulkVolume', 'dimensions': 'LLL'}
ens_calculator.defect_count.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['const', 'const_per_part'], 'name': 'Defect_Count', 'dimensions': '/'}
ens_calculator.defect_largestlinearextent.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'Defect_LargestLinearExtent', 'dimensions': 'L'}
ens_calculator.defect_netvolume.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'Defect_NetVolume', 'dimensions': 'LLL'}
ens_calculator.defect_shapefactor.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['scalar', 'nodal'], 'name': 'Defect_ShapeFactor', 'dimensions': '/'}
ens_calculator.defect_surfacearea.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'Defect_SurfaceArea', 'dimensions': 'LL'}
ens_calculator.density.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'Density', 'dimensions': 'M/LLL'}
ens_calculator.densitylognorm.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'DensityLogNorm', 'dimensions': 'M/LLL'}
ens_calculator.densitynorm.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'DensityNorm', 'dimensions': 'M/LLL'}
ens_calculator.densitynormstag.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'DensityNormStag', 'dimensions': 'M/LLL'}
ens_calculator.densitystag.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'DensityStag', 'dimensions': 'M/LLL'}
ens_calculator.dist2nodes.meta = {'class': ['Function', 'Geometry'], 'vartype': ['const'], 'name': 'Dist2Nodes', 'dimensions': 'L'}
ens_calculator.dist2part.meta = {'class': ['Function', 'Geometry'], 'vartype': ['scalar', 'nodal'], 'name': 'Dist2Part', 'dimensions': 'L'}
ens_calculator.dist2partelem.meta = {'class': ['Function', 'Geometry'], 'vartype': ['scalar', 'nodal'], 'name': 'Dist2PartElem', 'dimensions': 'L'}
ens_calculator.div.meta = {'class': ['Function', 'Calculus'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'Div', 'dimensions': 'b/L'}
ens_calculator.elemetric.meta = {'class': ['Function', 'Geometry'], 'vartype': ['scalar', 'vector', 'element'], 'name': 'EleMetric', 'dimensions': '[/,/,/,/,/,/,/,/,/,/,/,/,/,/,/,/,/,LLL,LL,/,/,/,/,/,/,/,/,/,L,/,LLL,/,/]@b'}
ens_calculator.elemtonode.meta = {'class': ['Function', 'Variable Manipulation', 'Geometry'], 'vartype': ['scalar', 'vector', 'nodal'], 'name': 'ElemToNode', 'dimensions': 'b'}
ens_calculator.elemtonodeweighted.meta = {'class': ['Function', 'Variable Manipulation', 'Geometry'], 'vartype': ['scalar', 'vector', 'nodal'], 'name': 'ElemToNodeWeighted', 'dimensions': 'b'}
ens_calculator.elesize.meta = {'class': ['Function', 'Geometry'], 'vartype': ['scalar', 'element'], 'name': 'EleSize', 'dimensions': 'a'}
ens_calculator.energyt.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'element', 'nodal'], 'name': 'EnergyT', 'dimensions': 'MLL/TT'}
ens_calculator.enthalpy.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'element', 'nodal'], 'name': 'Enthalpy', 'dimensions': 'MLL/TT'}
ens_calculator.enthalpynorm.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'element', 'nodal'], 'name': 'EnthalpyNorm', 'dimensions': 'MLL/TT'}
ens_calculator.enthalpynormstag.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'element', 'nodal'], 'name': 'EnthalpyNormStag', 'dimensions': 'MLL/TT'}
ens_calculator.enthalpystag.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'element', 'nodal'], 'name': 'EnthalpyStag', 'dimensions': 'MLL/TT'}
ens_calculator.entropy.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'element', 'nodal'], 'name': 'Entropy', 'dimensions': 'MLL/TTK'}
ens_calculator.flow.meta = {'class': ['Function', 'Integrals and Sums'], 'vartype': ['const', 'const_per_part'], 'name': 'Flow', 'dimensions': 'ab'}
ens_calculator.flowrate.meta = {'class': ['Function', 'Integrals and Sums'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'FlowRate', 'dimensions': 'b'}
ens_calculator.fluidshear.meta = {'class': ['Function', 'Stress/Strain'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'FluidShear', 'dimensions': 'M/LTT'}
ens_calculator.fluidshearmax.meta = {'class': ['Function', 'Stress/Strain'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'FluidShearMax', 'dimensions': 'M/LTT'}
ens_calculator.force.meta = {'class': ['Function', 'Stress/Strain', 'Force and Moment'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Force', 'dimensions': 'ML/TT'}
ens_calculator.force1d.meta = {'class': ['Function', 'Stress/Strain', 'Force and Moment'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Force1D', 'dimensions': 'ML/TT'}
ens_calculator.grad.meta = {'class': ['Function', 'Calculus'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Grad', 'dimensions': 'b/L'}
ens_calculator.gradtensor.meta = {'class': ['Function', 'Calculus'], 'vartype': ['tensor', 'nodal', 'element'], 'name': 'GradTensor', 'dimensions': 'b/L'}
ens_calculator.helicitydensity.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'HelicityDensity', 'dimensions': 'L/TT'}
ens_calculator.helicityrelative.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'HelicityRelative', 'dimensions': '/'}
ens_calculator.helicityrelfilter.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'HelicityRelFilter', 'dimensions': '/'}
ens_calculator.iblankingvalues.meta = {'class': ['Function', 'Plot3D', 'Geometry'], 'vartype': ['scalar', 'nodal'], 'name': 'IblankingValues', 'dimensions': '/'}
ens_calculator.ijkvalues.meta = {'class': ['Function', 'Plot3D', 'Geometry'], 'vartype': ['scalar', 'element'], 'name': 'IJKValues', 'dimensions': '/'}
ens_calculator.integralline.meta = {'class': ['Function', 'Integrals and Sums', 'Geometry', 'Calculus'], 'vartype': ['const', 'const_per_part'], 'name': 'IntegralLine', 'dimensions': 'bL'}
ens_calculator.integralsurface.meta = {'class': ['Function', 'Integrals and Sums', 'Geometry', 'Calculus'], 'vartype': ['const', 'const_per_part'], 'name': 'IntegralSurface', 'dimensions': 'bLL'}
ens_calculator.integralvolume.meta = {'class': ['Function', 'Integrals and Sums', 'Geometry', 'Calculus'], 'vartype': ['const', 'const_per_part'], 'name': 'IntegralVolume', 'dimensions': 'bLLL'}
ens_calculator.kinen.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'KinEn', 'dimensions': 'MLL/TT'}
ens_calculator.length.meta = {'class': ['Function', 'Geometry'], 'vartype': ['const', 'const_per_part'], 'name': 'Length', 'dimensions': 'L'}
ens_calculator.linevectors.meta = {'class': ['Function', 'Geometry'], 'vartype': ['vector', 'nodal'], 'name': 'LineVectors', 'dimensions': 'L'}
ens_calculator.mach.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'Mach', 'dimensions': '/'}
ens_calculator.makescalelem.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'MakeScalElem', 'dimensions': 'b'}
ens_calculator.makescalelemid.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'MakeScalElemId', 'dimensions': 'b'}
ens_calculator.makescalnode.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['scalar', 'nodal'], 'name': 'MakeScalNode', 'dimensions': 'b'}
ens_calculator.makescalnodeid.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['scalar', 'nodal'], 'name': 'MakeScalNodeId', 'dimensions': 'b'}
ens_calculator.makevect.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'MakeVect', 'dimensions': 'b'}
ens_calculator.massedparticle.meta = {'class': ['Function', 'Force and Moment'], 'vartype': ['scalar', 'element'], 'name': 'MassedParticle', 'dimensions': 'M'}
ens_calculator.massfluxavg.meta = {'class': ['Function', 'Force and Moment'], 'vartype': ['const', 'const_per_part'], 'name': 'MassFluxAvg', 'dimensions': 'b'}
ens_calculator.matspecies.meta = {'class': ['Function'], 'vartype': ['scalar', 'element'], 'name': 'MatSpecies', 'dimensions': 'd'}
ens_calculator.mattoscalar.meta = {'class': ['Function'], 'vartype': ['scalar', 'element'], 'name': 'MatToScalar', 'dimensions': '/'}
ens_calculator.max.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['const', 'const_per_part'], 'name': 'Max', 'dimensions': 'b'}
ens_calculator.min.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['const', 'const_per_part'], 'name': 'Min', 'dimensions': 'b'}
ens_calculator.moment.meta = {'class': ['Function', 'Force and Moment'], 'vartype': ['const', 'const_per_part'], 'name': 'Moment', 'dimensions': 'bL'}
ens_calculator.momentum.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Momentum', 'dimensions': 'M/LLT'}
ens_calculator.momentvector.meta = {'class': ['Function', 'Force and Moment'], 'vartype': ['vector', 'nodal'], 'name': 'MomentVector', 'dimensions': 'bL'}
ens_calculator.nodecount.meta = {'class': ['Function', 'Geometry'], 'vartype': ['const', 'const_per_part'], 'name': 'NodeCount', 'dimensions': '/'}
ens_calculator.nodetoelem.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['scalar', 'vector', 'element'], 'name': 'NodeToElem', 'dimensions': 'b'}
ens_calculator.normal.meta = {'class': ['Function', 'Geometry'], 'vartype': ['vector', 'element'], 'name': 'Normal', 'dimensions': '/'}
ens_calculator.normvect.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'NormVect', 'dimensions': 'b'}
ens_calculator.normc.meta = {'class': ['Function', 'Integrals and Sums'], 'vartype': ['const', 'const_per_part'], 'name': 'NormC', 'dimensions': 'M/LTT'}
ens_calculator.offsetfield.meta = {'class': ['Function', 'Geometry'], 'vartype': ['scalar', 'nodal'], 'name': 'OffsetField', 'dimensions': 'L'}
ens_calculator.offsetvar.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['scalar', 'vector', 'nodal', 'element'], 'name': 'OffsetVar', 'dimensions': 'b'}
ens_calculator.partnumber.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['const', 'const_per_part'], 'name': 'PartNumber', 'dimensions': '/'}
ens_calculator.pres.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'Pres', 'dimensions': 'M/LTT'}
ens_calculator.prescoef.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresCoef', 'dimensions': '/'}
ens_calculator.presdynam.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresDynam', 'dimensions': 'M/LTT'}
ens_calculator.preslognorm.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresLogNorm', 'dimensions': 'M/LTT'}
ens_calculator.presnorm.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresNorm', 'dimensions': 'M/LTT'}
ens_calculator.presnormstag.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresNormStag', 'dimensions': 'M/LTT'}
ens_calculator.prespitot.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresPitot', 'dimensions': 'M/LTT'}
ens_calculator.prespitotratio.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresPitotRatio', 'dimensions': 'M/LTT'}
ens_calculator.presstag.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresStag', 'dimensions': 'M/LTT'}
ens_calculator.presstagcoef.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresStagCoef', 'dimensions': 'M/LTT'}
ens_calculator.prest.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'PresT', 'dimensions': 'M/LTT'}
ens_calculator.radiograph_grid.meta = {'class': ['Function', 'Integrals and Sums', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'Radiograph_grid', 'dimensions': 'fL'}
ens_calculator.radiograph_mesh.meta = {'class': ['Function', 'Integrals and Sums', 'Variable Manipulation'], 'vartype': ['scalar', 'element'], 'name': 'Radiograph_mesh', 'dimensions': 'eL'}
ens_calculator.recttocyl.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'RectToCyl', 'dimensions': 'b'}
ens_calculator.servernumber.meta = {'class': [], 'vartype': ['scalar', 'element'], 'name': 'ServerNumber', 'dimensions': '/'}
ens_calculator.shockplot3d.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'ShockPlot3d', 'dimensions': '/'}
ens_calculator.smoothmesh.meta = {'class': ['Function', 'Geometry'], 'vartype': ['vector', 'nodal'], 'name': 'SmoothMesh', 'dimensions': 'L'}
ens_calculator.sonicspeed.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'SonicSpeed', 'dimensions': 'L/T'}
ens_calculator.spamean.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['const', 'const_per_part'], 'name': 'SpaMean', 'dimensions': 'b'}
ens_calculator.spameanweighted.meta = {'class': ['Function', 'Geometry', 'Variable Manipulation'], 'vartype': ['const', 'const_per_part'], 'name': 'SpaMeanWeighted', 'dimensions': 'b'}
ens_calculator.speed.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'Speed', 'dimensions': 'L/T'}
ens_calculator.statmoment.meta = {'class': ['Function', 'Statistics'], 'vartype': ['const', 'const_per_part'], 'name': 'StatMoment', 'dimensions': '[b,b,bb,/,/]@c'}
ens_calculator.statregspa.meta = {'class': ['Function', 'Statistics'], 'vartype': ['const'], 'name': 'StatRegSpa', 'dimensions': '/'}
ens_calculator.statregval1.meta = {'class': ['Function', 'Statistics'], 'vartype': ['const'], 'name': 'StatRegVal1', 'dimensions': '/'}
ens_calculator.statregval2.meta = {'class': ['Function', 'Statistics'], 'vartype': ['const'], 'name': 'StatRegVal2', 'dimensions': '/'}
ens_calculator.swirl.meta = {'class': ['Function', 'Calculus', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'Swirl', 'dimensions': 'LLT/M'}
ens_calculator.temperature.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'Temperature', 'dimensions': 'K'}
ens_calculator.temperlognorm.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TemperLogNorm', 'dimensions': 'K'}
ens_calculator.tempernorm.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TemperNorm', 'dimensions': 'K'}
ens_calculator.tempernormstag.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TemperNormStag', 'dimensions': 'K'}
ens_calculator.temperstag.meta = {'class': ['Function', 'Plot3D', 'Density, Energy, Pressure, and Temperature'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TemperStag', 'dimensions': 'K'}
ens_calculator.tempmean.meta = {'class': ['Function', 'Geometry', 'Statistics', 'Variable Manipulation'], 'vartype': ['scalar', 'vector', 'const', 'const_per_part', 'nodal', 'element'], 'name': 'TempMean', 'dimensions': 'b'}
ens_calculator.tempminmaxfield.meta = {'class': ['Function', 'Geometry', 'Statistics', 'Variable Manipulation'], 'vartype': ['scalar', 'vector', 'const', 'const_per_part', 'nodal', 'element'], 'name': 'TempMinmaxField', 'dimensions': 'b'}
ens_calculator.tensorcomponent.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TensorComponent', 'dimensions': 'b'}
ens_calculator.tensordeterminant.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TensorDeterminant', 'dimensions': 'bbb'}
ens_calculator.tensoreigenvalue.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TensorEigenvalue', 'dimensions': 'b'}
ens_calculator.tensoreigenvector.meta = {'class': [], 'vartype': ['vector', 'nodal', 'element'], 'name': 'TensorEigenvector', 'dimensions': '/'}
ens_calculator.tensormake.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['tensor', 'nodal', 'element'], 'name': 'TensorMake', 'dimensions': 'b'}
ens_calculator.tensormakeasym.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['tensor', 'nodal', 'element'], 'name': 'TensorMakeAsym', 'dimensions': 'b'}
ens_calculator.tensortresca.meta = {'class': ['Function', 'Variable Manipulation', 'Stress/Strain'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TensorTresca', 'dimensions': 'b'}
ens_calculator.tensorvonmises.meta = {'class': ['Function', 'Variable Manipulation', 'Stress/Strain'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'TensorVonMises', 'dimensions': 'b'}
ens_calculator.vector1dprojection.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Vector1DProjection', 'dimensions': 'b'}
ens_calculator.vectorcylprojection.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'VectorCylProjection', 'dimensions': 'b'}
ens_calculator.vectorrectprojection.meta = {'class': ['Function', 'Variable Manipulation'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'VectorRectProjection', 'dimensions': 'b'}
ens_calculator.velo.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Velo', 'dimensions': 'L/T'}
ens_calculator.vol.meta = {'class': ['Function', 'Geometry'], 'vartype': ['const', 'const_per_part'], 'name': 'Vol', 'dimensions': 'LLL'}
ens_calculator.vort.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['vector', 'nodal', 'element'], 'name': 'Vort', 'dimensions': '/T'}
ens_calculator.vortgamma.meta = {'class': ['Function', 'Plot3D'], 'vartype': ['scalar', 'nodal', 'element'], 'name': 'VortGamma', 'dimensions': '/'}

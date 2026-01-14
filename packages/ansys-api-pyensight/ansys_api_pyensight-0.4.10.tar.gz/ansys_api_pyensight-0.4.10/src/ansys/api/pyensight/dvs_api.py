"""dvs_base module"""
"""Thed dvs_base module provides an interface to the dynamic_visualization store module"""

from typing import Any, Optional, List, Dict, Tuple, TYPE_CHECKING

import numpy
numpy.set_printoptions(threshold=numpy.inf)
numpy.set_printoptions(linewidth=numpy.inf)

if TYPE_CHECKING:
    from ansys.pyensight.core import Session
class dvs_base:
    def __init__(self, session: Optional["Session"]=None, dvs_module: Optional[Any]=None):
        self._session = session
        self._dvs_module = dvs_module
        self.ELEMTYPE_BAR_2: int = 2
        self.ELEMTYPE_BAR_2_GHOST: int = 3
        self.ELEMTYPE_BAR_3: int = 4
        self.ELEMTYPE_BAR_3_GHOST: int = 5
        self.ELEMTYPE_CONVEX_POLYHEDRON: int = 32
        self.ELEMTYPE_CONVEX_POLYHEDRON_GHOST: int = 33
        self.ELEMTYPE_HEXAHEDRON: int = 24
        self.ELEMTYPE_HEXAHEDRON_20: int = 26
        self.ELEMTYPE_HEXAHEDRON_20_GHOST: int = 27
        self.ELEMTYPE_HEXAHEDRON_GHOST: int = 25
        self.ELEMTYPE_N_SIDED_POLYGON: int = 6
        self.ELEMTYPE_N_SIDED_POLYGON_GHOST: int = 7
        self.ELEMTYPE_PENTAHEDRON: int = 28
        self.ELEMTYPE_PENTAHEDRON_15: int = 30
        self.ELEMTYPE_PENTAHEDRON_15_GHOST: int = 31
        self.ELEMTYPE_PENTAHEDRON_GHOST: int = 29
        self.ELEMTYPE_PNT: int = 0
        self.ELEMTYPE_PNT_GHOST: int = 1
        self.ELEMTYPE_PYRAMID: int = 20
        self.ELEMTYPE_PYRAMID_13: int = 22
        self.ELEMTYPE_PYRAMID_13_GHOST: int = 23
        self.ELEMTYPE_PYRAMID_GHOST: int = 21
        self.ELEMTYPE_QUADRANGLE: int = 12
        self.ELEMTYPE_QUADRANGLE_8: int = 14
        self.ELEMTYPE_QUADRANGLE_8_GHOST: int = 15
        self.ELEMTYPE_QUADRANGLE_GHOST: int = 13
        self.ELEMTYPE_STRUCTURED: int = 34
        self.ELEMTYPE_TETRAHEDRON: int = 16
        self.ELEMTYPE_TETRAHEDRON_10: int = 18
        self.ELEMTYPE_TETRAHEDRON_10_GHOST: int = 19
        self.ELEMTYPE_TETRAHEDRON_GHOST: int = 17
        self.ELEMTYPE_TRIANGLE: int = 8
        self.ELEMTYPE_TRIANGLE_6: int = 10
        self.ELEMTYPE_TRIANGLE_6_GHOST: int = 11
        self.ELEMTYPE_TRIANGLE_GHOST: int = 9
        self.ELEMTYPE_UNDEFINED: int = 35
        self.ELEMTYPE_UNDEFINED_CURVILINEAR: int = 37
        self.ELEMTYPE_UNDEFINED_PARALLELEPIPED: int = 36
        self.ELEM_ID: int = -9999
        self.FLAGS_BLOCK_FOR_SERVER: int = 1
        self.FLAGS_DEDUP: int = 2
        self.FLAGS_NONE: int = 0
        self.LOCATION_CASE: int = 3
        self.LOCATION_ELEMENT: int = 1
        self.LOCATION_NODE: int = 0
        self.LOCATION_PART: int = 2
        self.MESHCHUNK_CURVILINEAR: int = 3
        self.MESHCHUNK_PARALLELEPIPED: int = 2
        self.MESHCHUNK_UNKNOWN: int = 0
        self.MESHCHUNK_UNSTRUCTURED: int = 1
        self.NODE_ID: int = -10000
        self.STRUCTURED_GHOST_ELEMENTS: int = -10001
        self.STRUCTURED_IBLANKED_NODES: int = -10002
        self.VARTYPE_COMPLEX_SCALAR: int = 2
        self.VARTYPE_COMPLEX_TENSOR: int = 4
        self.VARTYPE_COMPLEX_TENSOR9: int = 5
        self.VARTYPE_COMPLEX_VECTOR: int = 3
        self.VARTYPE_SCALAR: int = 0
        self.VARTYPE_VECTOR: int = 1
        self.version: str = '1.4.1'


    class IDatasetObject:
        """Class wrapper for DVS IDatasetObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IDatasetObject
        """
        def __init__(self):
            pass

        def get_chunks_per_rank(self, *args, **kwargs) -> Any:
            """Get an array of the number of chunks for every rank for the query

            """
            if self._dvs_module:
                return self._dvs_module.get_chunks_per_rank(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_chunks_per_rank({arg_string})"
                return self._session.cmd(cmd)

        def get_metadata(self, *args, **kwargs) -> Any:
            """Get the metadata

            """
            if self._dvs_module:
                return self._dvs_module.get_metadata(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_metadata({arg_string})"
                return self._session.cmd(cmd)

        def get_name(self, *args, **kwargs) -> Any:
            """Get the name of the object

            """
            if self._dvs_module:
                return self._dvs_module.get_name(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_name({arg_string})"
                return self._session.cmd(cmd)

        def get_num_chunks_per_rank(self, *args, **kwargs) -> Any:
            """Get the number/size of chunks for each rank of the dataset

            """
            if self._dvs_module:
                return self._dvs_module.get_num_chunks_per_rank(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_num_chunks_per_rank({arg_string})"
                return self._session.cmd(cmd)

        def get_num_parts(self, *args, **kwargs) -> Any:
            """Get number of part for the dataset

            """
            if self._dvs_module:
                return self._dvs_module.get_num_parts(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_num_parts({arg_string})"
                return self._session.cmd(cmd)

        def get_num_plots(self, *args, **kwargs) -> Any:
            """Get the number of plots for the dataset

            """
            if self._dvs_module:
                return self._dvs_module.get_num_plots(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_num_plots({arg_string})"
                return self._session.cmd(cmd)

        def get_num_ranks(self, *args, **kwargs) -> Any:
            """Get number of ranks for the dataset

            """
            if self._dvs_module:
                return self._dvs_module.get_num_ranks(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_num_ranks({arg_string})"
                return self._session.cmd(cmd)

        def get_num_variables(self, *args, **kwargs) -> Any:
            """Get the number of variables for the dataset

            """
            if self._dvs_module:
                return self._dvs_module.get_num_variables(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_num_variables({arg_string})"
                return self._session.cmd(cmd)

        def get_part(self, *args, **kwargs) -> Any:
            """Get the part based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_part(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_part({arg_string})"
                return self._session.cmd(cmd)

        def get_plot(self, *args, **kwargs) -> Any:
            """Get the plot object based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_plot(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_plot({arg_string})"
                return self._session.cmd(cmd)

        def get_ranks(self, *args, **kwargs) -> Any:
            """Get the unique ranks for the dataset query

            """
            if self._dvs_module:
                return self._dvs_module.get_ranks(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_ranks({arg_string})"
                return self._session.cmd(cmd)

        def get_type(self, *args, **kwargs) -> Any:
            """Get the type of the object

            """
            if self._dvs_module:
                return self._dvs_module.get_type(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_type({arg_string})"
                return self._session.cmd(cmd)

        def get_unit_system(self, *args, **kwargs) -> Any:
            """Get the unit system of the dataset

            """
            if self._dvs_module:
                return self._dvs_module.get_unit_system(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_unit_system({arg_string})"
                return self._session.cmd(cmd)

        def get_variable(self, *args, **kwargs) -> Any:
            """Get the variable object based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_variable(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IDatasetObject.get_variable({arg_string})"
                return self._session.cmd(cmd)


    class IElemBlockObject:
        """Class wrapper for DVS IElemBlockObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IElemBlockObject
        """
        def __init__(self):
            pass

        def get_connectivity(self, *args, **kwargs) -> Any:
            """Get the connectivity for the basic unstructured element types for the element block

            """
            if self._dvs_module:
                return self._dvs_module.get_connectivity(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_connectivity({arg_string})"
                return self._session.cmd(cmd)

        def get_connectivity_polygon(self, *args, **kwargs) -> Any:
            """Get the connectivity information for the polygon element blocks

            """
            if self._dvs_module:
                return self._dvs_module.get_connectivity_polygon(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_connectivity_polygon({arg_string})"
                return self._session.cmd(cmd)

        def get_connectivity_polygon_size(self, *args, **kwargs) -> Any:
            """Get the connectivity size information for the polygon element blocks

            """
            if self._dvs_module:
                return self._dvs_module.get_connectivity_polygon_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_connectivity_polygon_size({arg_string})"
                return self._session.cmd(cmd)

        def get_connectivity_polyhedral(self, *args, **kwargs) -> Any:
            """Get the connectivity information for the polyhedral element blocks

            """
            if self._dvs_module:
                return self._dvs_module.get_connectivity_polyhedral(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_connectivity_polyhedral({arg_string})"
                return self._session.cmd(cmd)

        def get_connectivity_polyhedral_size(self, *args, **kwargs) -> Any:
            """Get the connectivity size information for the polyhedral element blocks

            """
            if self._dvs_module:
                return self._dvs_module.get_connectivity_polyhedral_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_connectivity_polyhedral_size({arg_string})"
                return self._session.cmd(cmd)

        def get_connectivity_size(self, *args, **kwargs) -> Any:
            """Get the connectivity size for the basic unstructured element types for the element block

            """
            if self._dvs_module:
                return self._dvs_module.get_connectivity_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_connectivity_size({arg_string})"
                return self._session.cmd(cmd)

        def get_element_type(self, *args, **kwargs) -> Any:
            """Get element type for the element block

            """
            if self._dvs_module:
                return self._dvs_module.get_element_type(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_element_type({arg_string})"
                return self._session.cmd(cmd)

        def get_hash(self, *args, **kwargs) -> Any:
            """Get the hash of the data

            """
            if self._dvs_module:
                return self._dvs_module.get_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_hash({arg_string})"
                return self._session.cmd(cmd)

        def get_is_ghost(self, *args, **kwargs) -> Any:
            """Get if the element block is composed of ghost elements

            """
            if self._dvs_module:
                return self._dvs_module.get_is_ghost(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_is_ghost({arg_string})"
                return self._session.cmd(cmd)

        def get_nodes_per_element(self, *args, **kwargs) -> Any:
            """Get the number of nodes per basic unstructured element

            """
            if self._dvs_module:
                return self._dvs_module.get_nodes_per_element(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_nodes_per_element({arg_string})"
                return self._session.cmd(cmd)

        def get_num_elements(self, *args, **kwargs) -> Any:
            """Get the number of elements for the element block

            """
            if self._dvs_module:
                return self._dvs_module.get_num_elements(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_num_elements({arg_string})"
                return self._session.cmd(cmd)

        def get_num_variables(self, *args, **kwargs) -> Any:
            """Get the number of elemental variables for the element block

            """
            if self._dvs_module:
                return self._dvs_module.get_num_variables(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_num_variables({arg_string})"
                return self._session.cmd(cmd)

        def get_var_hash(self, *args, **kwargs) -> Any:
            """Get hash of the variable data

            """
            if self._dvs_module:
                return self._dvs_module.get_var_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_var_hash({arg_string})"
                return self._session.cmd(cmd)

        def get_variable(self, *args, **kwargs) -> Any:
            """Get the variable definition associated with the elemental variable index

            """
            if self._dvs_module:
                return self._dvs_module.get_variable(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_variable({arg_string})"
                return self._session.cmd(cmd)

        def get_variable_data(self, *args, **kwargs) -> Any:
            """Get the elemental variable data for the variable definition

            """
            if self._dvs_module:
                return self._dvs_module.get_variable_data(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_variable_data({arg_string})"
                return self._session.cmd(cmd)

        def get_variable_data_size(self, *args, **kwargs) -> Any:
            """Get the elemental variable data size for the variable definition

            """
            if self._dvs_module:
                return self._dvs_module.get_variable_data_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IElemBlockObject.get_variable_data_size({arg_string})"
                return self._session.cmd(cmd)


    class IHashObject:
        """Class wrapper for DVS IHashObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IHashObject
        """
        def __init__(self):
            pass

        def get_hash(self, *args, **kwargs) -> Any:
            """Get the hash of the data

            """
            if self._dvs_module:
                return self._dvs_module.get_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IHashObject.get_hash({arg_string})"
                return self._session.cmd(cmd)


    class IMeshChunkObject:
        """Class wrapper for DVS IMeshChunkObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IMeshChunkObject
        """
        def __init__(self):
            pass

        def get_chunk(self, *args, **kwargs) -> Any:
            """Get the chunk for mesh chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_chunk(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_chunk({arg_string})"
                return self._session.cmd(cmd)

        def get_coords(self, *args, **kwargs) -> Any:
            """Get the coordinates for an unstructured mesh

            """
            if self._dvs_module:
                return self._dvs_module.get_coords(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_coords({arg_string})"
                return self._session.cmd(cmd)

        def get_coords_curve(self, *args, **kwargs) -> Any:
            """Get coordinate data for a structured curvilinear mesh

            """
            if self._dvs_module:
                return self._dvs_module.get_coords_curve(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_coords_curve({arg_string})"
                return self._session.cmd(cmd)

        def get_coords_curve_component_size(self, *args, **kwargs) -> Any:
            """Get component size for a structured curvilinear mesh

            """
            if self._dvs_module:
                return self._dvs_module.get_coords_curve_component_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_coords_curve_component_size({arg_string})"
                return self._session.cmd(cmd)

        def get_coords_interleaved(self, *args, **kwargs) -> Any:
            """Get the coords for a unstructured meshes interleaved in a single array

            """
            if self._dvs_module:
                return self._dvs_module.get_coords_interleaved(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_coords_interleaved({arg_string})"
                return self._session.cmd(cmd)

        def get_coords_parallele(self, *args, **kwargs) -> Any:
            """Get the IJK mesh information for structured parallelepiped mesh chunks

            """
            if self._dvs_module:
                return self._dvs_module.get_coords_parallele(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_coords_parallele({arg_string})"
                return self._session.cmd(cmd)

        def get_coords_parallele_ijk_size(self, *args, **kwargs) -> Any:
            """Get the IJK mesh size information for structured parallelepiped mesh chunks

            """
            if self._dvs_module:
                return self._dvs_module.get_coords_parallele_ijk_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_coords_parallele_ijk_size({arg_string})"
                return self._session.cmd(cmd)

        def get_coords_size(self, *args, **kwargs) -> Any:
            """Get the coordinates size for an unstructured mesh

            """
            if self._dvs_module:
                return self._dvs_module.get_coords_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_coords_size({arg_string})"
                return self._session.cmd(cmd)

        def get_element_block(self, *args, **kwargs) -> Any:
            """Get the element block by index

            """
            if self._dvs_module:
                return self._dvs_module.get_element_block(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_element_block({arg_string})"
                return self._session.cmd(cmd)

        def get_element_block_by_type(self, *args, **kwargs) -> Any:
            """Get the element block by element type

            """
            if self._dvs_module:
                return self._dvs_module.get_element_block_by_type(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_element_block_by_type({arg_string})"
                return self._session.cmd(cmd)

        def get_element_block_types(self, *args, **kwargs) -> Any:
            """Get an array of the element block types for the mesh chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_element_block_types(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_element_block_types({arg_string})"
                return self._session.cmd(cmd)

        def get_hash(self, *args, **kwargs) -> Any:
            """Get the hash of the data

            """
            if self._dvs_module:
                return self._dvs_module.get_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_hash({arg_string})"
                return self._session.cmd(cmd)

        def get_num_element_blocks(self, *args, **kwargs) -> Any:
            """Get the number of element blocks for the mesh chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_num_element_blocks(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_num_element_blocks({arg_string})"
                return self._session.cmd(cmd)

        def get_num_variables(self, *args, **kwargs) -> Any:
            """Get the number of nodal variables for the mesh chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_num_variables(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_num_variables({arg_string})"
                return self._session.cmd(cmd)

        def get_object(self, *args, **kwargs) -> Any:
            """Get the mesh chunk object definition

            """
            if self._dvs_module:
                return self._dvs_module.get_object(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_object({arg_string})"
                return self._session.cmd(cmd)

        def get_rank(self, *args, **kwargs) -> Any:
            """Get the rank for the mesh chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_rank(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_rank({arg_string})"
                return self._session.cmd(cmd)

        def get_time(self, *args, **kwargs) -> Any:
            """Get the time for mesh chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_time(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_time({arg_string})"
                return self._session.cmd(cmd)

        def get_type(self, *args, **kwargs) -> Any:
            """Get the type of mesh chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_type(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_type({arg_string})"
                return self._session.cmd(cmd)

        def get_var_hash(self, *args, **kwargs) -> Any:
            """Get hash of the variable data

            """
            if self._dvs_module:
                return self._dvs_module.get_var_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_var_hash({arg_string})"
                return self._session.cmd(cmd)

        def get_variable(self, *args, **kwargs) -> Any:
            """Get the variable definition associates with the nodal variable for given index

            """
            if self._dvs_module:
                return self._dvs_module.get_variable(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_variable({arg_string})"
                return self._session.cmd(cmd)

        def get_variable_data(self, *args, **kwargs) -> Any:
            """Get the variable data

            """
            if self._dvs_module:
                return self._dvs_module.get_variable_data(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_variable_data({arg_string})"
                return self._session.cmd(cmd)

        def get_variable_data_size(self, *args, **kwargs) -> Any:
            """Get the variable data size

            """
            if self._dvs_module:
                return self._dvs_module.get_variable_data_size(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IMeshChunkObject.get_variable_data_size({arg_string})"
                return self._session.cmd(cmd)


    class IObjectO:
        """Class wrapper for DVS IObjectO module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IObjectO
        """
        def __init__(self):
            pass

        def get_dataset(self, *args, **kwargs) -> Any:
            """Get the reference dataset for the object

            """
            if self._dvs_module:
                return self._dvs_module.get_dataset(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IObjectO.get_dataset({arg_string})"
                return self._session.cmd(cmd)

        def get_metadata(self, *args, **kwargs) -> Any:
            """Get the metadata

            """
            if self._dvs_module:
                return self._dvs_module.get_metadata(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IObjectO.get_metadata({arg_string})"
                return self._session.cmd(cmd)

        def get_name(self, *args, **kwargs) -> Any:
            """Get the name of the object

            """
            if self._dvs_module:
                return self._dvs_module.get_name(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IObjectO.get_name({arg_string})"
                return self._session.cmd(cmd)

        def get_type(self, *args, **kwargs) -> Any:
            """Get the type of the object

            """
            if self._dvs_module:
                return self._dvs_module.get_type(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IObjectO.get_type({arg_string})"
                return self._session.cmd(cmd)


    class IPlotChunkObject:
        """Class wrapper for DVS IPlotChunkObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IPlotChunkObject
        """
        def __init__(self):
            pass

        def get_data(self, *args, **kwargs) -> Any:
            """Get the data for plot chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_data(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IPlotChunkObject.get_data({arg_string})"
                return self._session.cmd(cmd)

        def get_hash(self, *args, **kwargs) -> Any:
            """Get the hash of the data

            """
            if self._dvs_module:
                return self._dvs_module.get_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IPlotChunkObject.get_hash({arg_string})"
                return self._session.cmd(cmd)

        def get_metadata(self, *args, **kwargs) -> Any:
            """Get the metadata

            """
            if self._dvs_module:
                return self._dvs_module.get_metadata(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IPlotChunkObject.get_metadata({arg_string})"
                return self._session.cmd(cmd)

        def get_object(self, *args, **kwargs) -> Any:
            """Get the plot definition for the plot chunk

            """
            if self._dvs_module:
                return self._dvs_module.get_object(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IPlotChunkObject.get_object({arg_string})"
                return self._session.cmd(cmd)

        def get_rank(self, *args, **kwargs) -> Any:
            """Get the rank for the plot

            """
            if self._dvs_module:
                return self._dvs_module.get_rank(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IPlotChunkObject.get_rank({arg_string})"
                return self._session.cmd(cmd)

        def get_time(self, *args, **kwargs) -> Any:
            """Get the time for the plot

            """
            if self._dvs_module:
                return self._dvs_module.get_time(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IPlotChunkObject.get_time({arg_string})"
                return self._session.cmd(cmd)


    class IQueryObject:
        """Class wrapper for DVS IQueryObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IQueryObject
        """
        def __init__(self):
            pass

        def add_uri(self, *args, **kwargs) -> Any:
            """Add a URI for the reader API to iterare over

            """
            if self._dvs_module:
                return self._dvs_module.add_uri(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.add_uri({arg_string})"
                return self._session.cmd(cmd)

        def filter(self, *args, **kwargs) -> Any:
            """Method will allocate a new chained query with the passed in filter appended to it

            """
            if self._dvs_module:
                return self._dvs_module.filter(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.filter({arg_string})"
                return self._session.cmd(cmd)

        def get_chunks_per_rank(self, *args, **kwargs) -> Any:
            """Get an array of the number of chunks for every rank for the query

            """
            if self._dvs_module:
                return self._dvs_module.get_chunks_per_rank(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_chunks_per_rank({arg_string})"
                return self._session.cmd(cmd)

        def get_dataset(self, *args, **kwargs) -> Any:
            """Get the dataset object

            """
            if self._dvs_module:
                return self._dvs_module.get_dataset(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_dataset({arg_string})"
                return self._session.cmd(cmd)

        def get_hash_available(self, *args, **kwargs) -> Any:
            """Get if the hash is available in the blobstore

            """
            if self._dvs_module:
                return self._dvs_module.get_hash_available(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_hash_available({arg_string})"
                return self._session.cmd(cmd)

        def get_mesh_chunk(self, *args, **kwargs) -> Any:
            """Get the mesh chunk based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_mesh_chunk(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_mesh_chunk({arg_string})"
                return self._session.cmd(cmd)

        def get_num_chunks_per_rank(self, *args, **kwargs) -> Any:
            """Get the number of chunks for each rank

            """
            if self._dvs_module:
                return self._dvs_module.get_num_chunks_per_rank(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_chunks_per_rank({arg_string})"
                return self._session.cmd(cmd)

        def get_num_datasets(self, *args, **kwargs) -> Any:
            """Get number of datasets objects

            """
            if self._dvs_module:
                return self._dvs_module.get_num_datasets(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_datasets({arg_string})"
                return self._session.cmd(cmd)

        def get_num_mesh_chunks(self, *args, **kwargs) -> Any:
            """Get the number of mesh chunks for the query

            """
            if self._dvs_module:
                return self._dvs_module.get_num_mesh_chunks(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_mesh_chunks({arg_string})"
                return self._session.cmd(cmd)

        def get_num_parts(self, *args, **kwargs) -> Any:
            """Get number of part for the query

            """
            if self._dvs_module:
                return self._dvs_module.get_num_parts(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_parts({arg_string})"
                return self._session.cmd(cmd)

        def get_num_plot_chunks(self, *args, **kwargs) -> Any:
            """Get the number of plot chunks for the query

            """
            if self._dvs_module:
                return self._dvs_module.get_num_plot_chunks(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_plot_chunks({arg_string})"
                return self._session.cmd(cmd)

        def get_num_plots(self, *args, **kwargs) -> Any:
            """Get the number of plots for the query

            """
            if self._dvs_module:
                return self._dvs_module.get_num_plots(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_plots({arg_string})"
                return self._session.cmd(cmd)

        def get_num_ranks(self, *args, **kwargs) -> Any:
            """Get number of ranks for the filtered query

            """
            if self._dvs_module:
                return self._dvs_module.get_num_ranks(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_ranks({arg_string})"
                return self._session.cmd(cmd)

        def get_num_servers(self, *args, **kwargs) -> Any:
            """Get number of servers the cache in the URI was written with

            """
            if self._dvs_module:
                return self._dvs_module.get_num_servers(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_servers({arg_string})"
                return self._session.cmd(cmd)

        def get_num_timesteps(self, *args, **kwargs) -> Any:
            """Get the number of timesteps

            """
            if self._dvs_module:
                return self._dvs_module.get_num_timesteps(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_timesteps({arg_string})"
                return self._session.cmd(cmd)

        def get_num_variables(self, *args, **kwargs) -> Any:
            """Get the number of variables for the query

            """
            if self._dvs_module:
                return self._dvs_module.get_num_variables(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_num_variables({arg_string})"
                return self._session.cmd(cmd)

        def get_part(self, *args, **kwargs) -> Any:
            """Get the part based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_part(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_part({arg_string})"
                return self._session.cmd(cmd)

        def get_plot(self, *args, **kwargs) -> Any:
            """Get the plot object based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_plot(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_plot({arg_string})"
                return self._session.cmd(cmd)

        def get_plot_chunk(self, *args, **kwargs) -> Any:
            """Get the plot chunk based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_plot_chunk(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_plot_chunk({arg_string})"
                return self._session.cmd(cmd)

        def get_ranks(self, *args, **kwargs) -> Any:
            """Get the unique ranks for the filtered query

            """
            if self._dvs_module:
                return self._dvs_module.get_ranks(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_ranks({arg_string})"
                return self._session.cmd(cmd)

        def get_timesteps(self, *args, **kwargs) -> Any:
            """Get the timesteps objects

            """
            if self._dvs_module:
                return self._dvs_module.get_timesteps(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_timesteps({arg_string})"
                return self._session.cmd(cmd)

        def get_variable(self, *args, **kwargs) -> Any:
            """Get the variable object based on the index

            """
            if self._dvs_module:
                return self._dvs_module.get_variable(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_variable({arg_string})"
                return self._session.cmd(cmd)

        def get_variable_data(self, *args, **kwargs) -> Any:
            """Get variable values for dataset and part objects

            """
            if self._dvs_module:
                return self._dvs_module.get_variable_data(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.get_variable_data({arg_string})"
                return self._session.cmd(cmd)

        def set_server_mod(self, *args, **kwargs) -> Any:
            """Set a filter based on the server number and a modulus

            """
            if self._dvs_module:
                return self._dvs_module.set_server_mod(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IQueryObject.set_server_mod({arg_string})"
                return self._session.cmd(cmd)


    class IVarHashObject:
        """Class wrapper for DVS IVarHashObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IVarHashObject
        """
        def __init__(self):
            pass

        def get_var_hash(self, *args, **kwargs) -> Any:
            """Get hash of the variable data

            """
            if self._dvs_module:
                return self._dvs_module.get_var_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarHashObject.get_var_hash({arg_string})"
                return self._session.cmd(cmd)


    class IVarObject:
        """Class wrapper for DVS IVarObject module

        This class acts as a proxy for the DVS Python module dynamic_visualization_store.IVarObject
        """
        def __init__(self):
            pass

        def get_component_count_per_value(self, *args, **kwargs) -> Any:
            """Get the number of floats per value

            """
            if self._dvs_module:
                return self._dvs_module.get_component_count_per_value(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_component_count_per_value({arg_string})"
                return self._session.cmd(cmd)

        def get_dataset(self, *args, **kwargs) -> Any:
            """Get the reference dataset for the variable

            """
            if self._dvs_module:
                return self._dvs_module.get_dataset(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_dataset({arg_string})"
                return self._session.cmd(cmd)

        def get_hash(self, *args, **kwargs) -> Any:
            """Get the hash of the data

            """
            if self._dvs_module:
                return self._dvs_module.get_hash(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_hash({arg_string})"
                return self._session.cmd(cmd)

        def get_metadata(self, *args, **kwargs) -> Any:
            """Get the metadata

            """
            if self._dvs_module:
                return self._dvs_module.get_metadata(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_metadata({arg_string})"
                return self._session.cmd(cmd)

        def get_name(self, *args, **kwargs) -> Any:
            """Get the name of the variable

            """
            if self._dvs_module:
                return self._dvs_module.get_name(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_name({arg_string})"
                return self._session.cmd(cmd)

        def get_unit_dimension(self, *args, **kwargs) -> Any:
            """Get the variable unit dimension as string

            """
            if self._dvs_module:
                return self._dvs_module.get_unit_dimension(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_unit_dimension({arg_string})"
                return self._session.cmd(cmd)

        def get_unit_label(self, *args, **kwargs) -> Any:
            """Get the variable unit label as string

            """
            if self._dvs_module:
                return self._dvs_module.get_unit_label(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_unit_label({arg_string})"
                return self._session.cmd(cmd)

        def get_var_location(self, *args, **kwargs) -> Any:
            """Get the variable location

            """
            if self._dvs_module:
                return self._dvs_module.get_var_location(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_var_location({arg_string})"
                return self._session.cmd(cmd)

        def get_var_type(self, *args, **kwargs) -> Any:
            """Get the type of variable

            """
            if self._dvs_module:
                return self._dvs_module.get_var_type(*args, **kwargs)
            if self._session:
                self._session.cmd('import dynamic_visualization_store', do_eval=False)
                self._session.cmd('import numpy', do_eval=False)
                arg_list = []
                for arg in args:
                    arg_list.append(arg.__repr__())
                for key, value in kwargs.items():
                    data = value.__repr__()
                    if isinstance(value, numpy.ndarray):
                        data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
                    arg_list.append(data)
                arg_string = ",".join(arg_list)
                cmd = f"dynamic_visualization_store.IVarObject.get_var_type({arg_string})"
                return self._session.cmd(cmd)

    def add_metadata(self, session_id: int, metadata: Dict[str, str]) -> None:
        """Add metadata for the current dataset.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        metadata: dict 
            A dictionary containing the metadata keys and values to be added

        """
        if self._dvs_module:
            return self._dvs_module.add_metadata(session_id, metadata)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = metadata.__repr__()
            if isinstance(metadata, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.add_metadata({arg_string})"
            return self._session.cmd(cmd)

    def add_part_info(self, session_id: int, parts: List[dict]) -> None:
        """Add part info for simulation.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        parts: list
            A list of parts definition. Each part is defined via a dictionary defined like this:
              id - The part id
              name - The part name
              structured: True if the part is structured
              chunking: True if using chunking
              tags: a dictionary containing the metadata for the part

        """
        if self._dvs_module:
            return self._dvs_module.add_part_info(session_id, parts)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = parts.__repr__()
            if isinstance(parts, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.add_part_info({arg_string})"
            return self._session.cmd(cmd)

    def add_part_rigid_body_motion(self, session_id: int, part_id: int, update_num: int, quaternion: Optional[List[float]]=None, displacement: Optional[List[float]]=None, cg_offset: Optional[List[float]]=None) -> None:
        """Add rigid body motion data to a specific part for a specific update.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        update_num: int
            update number of this update, must be monotonically increasing
        quaternion: List[float]
            the quaternion defining the rigid body rotation.   
        displacement: List[float]
            a list describing the rigid body translation
        cg_offset: List[float]
            a list describing the center of gravity offset to be applied before applying the rotation and the translation

        """
        if self._dvs_module:
            return self._dvs_module.add_part_rigid_body_motion(session_id, part_id, update_num, quaternion, displacement, cg_offset)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = update_num.__repr__()
            if isinstance(update_num, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = quaternion.__repr__()
            if isinstance(quaternion, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = displacement.__repr__()
            if isinstance(displacement, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = cg_offset.__repr__()
            if isinstance(cg_offset, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.add_part_rigid_body_motion({arg_string})"
            return self._session.cmd(cmd)

    def add_plot_info(self, session_id: int, plots: List[dict]) -> None:
        """Add plot info for simulation.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        plots: list
            A list of plots definition. Each plot is defined via a dictionary defined like this:
              id - The plot id
              name - The plot name
              x_axis_title - The X Axis title
              x_axis_units - The X Axis units
              y_axis_title - The Y Axis title
              y_axis_units - The Y Axis units
              tags: a dictionary containing the metadata for the plot

        """
        if self._dvs_module:
            return self._dvs_module.add_plot_info(session_id, plots)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = plots.__repr__()
            if isinstance(plots, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.add_plot_info({arg_string})"
            return self._session.cmd(cmd)

    def add_var_info(self, session_id: int, variables: List[dict]) -> None:
        """Add var info for simulation.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        variables: list
            A list of variable definitions. Each variable is defined via a dictionary defined like this:
              id - The var id
              name - The variable name
              type - The variable type. Check the VARTYPE enums available with this module
              location - The variable location. Check the LOCATION enums available with this module
              unit - The variable units. See https://nexusdemo.ensight.com/docs/python/html/ENS_UNITSSchema.html
              unit_label - The label for the variable units. See https://nexusdemo.ensight.com/docs/python/html/ENS_UNITSSchema.html
              tags: a dictionary containing the metadata for the variable

        """
        if self._dvs_module:
            return self._dvs_module.add_var_info(session_id, variables)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = variables.__repr__()
            if isinstance(variables, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.add_var_info({arg_string})"
            return self._session.cmd(cmd)

    def begin_init(self, session_id: int, dataset_name: str, rank: int, total_ranks: int, num_chunks: int) -> None:
        """Begin setup of rank.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        dataset_name: str
            name for dataset
        rank: int 
            Rank this solver is processing (zero based)
        total_ranks: int
            Total number of ranks across solver nodes
        num_chunks: int
            Number of chunks for this rank (usually 1)

        """
        if self._dvs_module:
            return self._dvs_module.begin_init(session_id, dataset_name, rank, total_ranks, num_chunks)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = dataset_name.__repr__()
            if isinstance(dataset_name, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = rank.__repr__()
            if isinstance(rank, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = total_ranks.__repr__()
            if isinstance(total_ranks, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = num_chunks.__repr__()
            if isinstance(num_chunks, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.begin_init({arg_string})"
            return self._session.cmd(cmd)

    def begin_update(self, session_id: int, update_num: int, time: float, rank: int, chunk: int) -> None:
        """Method to begin an update.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        update_num: int
            update number of this update, must be monotonically increasing
        time: float
            time in seconds this update is for
        rank: int 
            the rank we are sending an update for (zero based)
        chunk: int
            the chunk number this update is for (zero based)

        """
        if self._dvs_module:
            return self._dvs_module.begin_update(session_id, update_num, time, rank, chunk)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = update_num.__repr__()
            if isinstance(update_num, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = time.__repr__()
            if isinstance(time, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = rank.__repr__()
            if isinstance(rank, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = chunk.__repr__()
            if isinstance(chunk, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.begin_update({arg_string})"
            return self._session.cmd(cmd)

    def connect(self, server_id: int, flags: Optional[int]=0, secret: Optional[str]=None) -> int:
        """Connect to dvs server.
        
        This call will connect to a server that has been created using server_create()
        If server is being created locally server_start() must be called before connecting.
        
        Parameters
        ----------
        server_id: int
            id of server created by server_create()
        flags: int
            flags for client setup. Check the FLAGS enums available with this module
        secret: str
            shared secret to use for client, can be an empty string
        
        Returns
        -------
        session_id: int
            dynamic id created for connection, used for client dvs calls

        """
        if self._dvs_module:
            return self._dvs_module.connect(server_id, flags, secret)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = server_id.__repr__()
            if isinstance(server_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = flags.__repr__()
            if isinstance(flags, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = secret.__repr__()
            if isinstance(secret, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.connect({arg_string})"
            return self._session.cmd(cmd)

    def convert_rotation_to_quaternion(self, session_id: int, axis_start: List[float], axis_end: List[float], relative_rotation_angle: float) -> List[float]:
        """Connect to dvs server.
        
        This call will connect to a server that has been created using server_create()
        If server is being created locally server_start() must be called before connecting.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        axis_start: list
            a list of floats describing the starting point of the line representing the rotation axis
        axis_end: list
            a list of floats describing the end point of the line representing the rotation axis
        relative_rotation_angle: float
            the angle to rotate around the give axis
        
        Returns
        -------
        quaternion: list
            the quaternion representation of the rotation

        """
        if self._dvs_module:
            return self._dvs_module.convert_rotation_to_quaternion(session_id, axis_start, axis_end, relative_rotation_angle)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = axis_start.__repr__()
            if isinstance(axis_start, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = axis_end.__repr__()
            if isinstance(axis_end, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = relative_rotation_angle.__repr__()
            if isinstance(relative_rotation_angle, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.convert_rotation_to_quaternion({arg_string})"
            return self._session.cmd(cmd)

    def create_query_from_server(self, server_id: int, filter: Optional[str]=None) -> IQueryObject:
        """Create a query object from an existing server, to be used against its datasets.
        
        Parameters
        ----------
        server_id: int
            id of server created by server_create()
        filter: str
            an optional filter to select the objects to be found
        
        Returns
        -------
        query: IQueryObject
            the query object requested

        """
        if self._dvs_module:
            return self._dvs_module.create_query_from_server(server_id, filter)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = server_id.__repr__()
            if isinstance(server_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = filter.__repr__()
            if isinstance(filter, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.create_query_from_server({arg_string})"
            return self._session.cmd(cmd)

    def create_query_instance(self) -> IQueryObject:
        """Create instance of a Query
        
        Returns
        -------
        query: IQueryObject
            the query object requested

        """
        if self._dvs_module:
            return self._dvs_module.create_query_instance()
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.create_query_instance({arg_string})"
            return self._session.cmd(cmd)

    def delete_item(self, session_id: int, update_num: int, rank: int, filter: str) -> None:
        """Delete an item.
        
        This call must be called by every rank similarly to how begin_update happens.
        
        Currently this will only allow for timesteps to be deleted. In the future it can
        be expanded to all objects via the filter mechanism. Currently
        this supports the operands of eq, gt, gte, lt, lte. Example: To delete all timesteps
        >= time 1.1 the filter would be "/timestep.time/gte/1.1//" .
        It also currently only supports one statement so
        /timestep.time/gt/1.1//and/timestep.time/lt/2.1// is not valid as of version 1.1.0.
        
        Note: The update number should be monotonically increasing with the begin_update calls
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()
        update_num: int
            update number of this update, must be monotonically increasing
        rank: int 
            rank making this call
        filter: str
            filter for the item(s) to delete. 
            Check https://developer.ansys.com/docs/post-processing - Dynamic Visualization Store API 
            for detailed info.

        """
        if self._dvs_module:
            return self._dvs_module.delete_item(session_id, update_num, rank, filter)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = update_num.__repr__()
            if isinstance(update_num, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = rank.__repr__()
            if isinstance(rank, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = filter.__repr__()
            if isinstance(filter, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.delete_item({arg_string})"
            return self._session.cmd(cmd)

    def end_init(self, session_id: int) -> None:
        """End the initialization of the rank.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()

        """
        if self._dvs_module:
            return self._dvs_module.end_init(session_id)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.end_init({arg_string})"
            return self._session.cmd(cmd)

    def end_update(self, session_id: int) -> None:
        """Call to end the update for this timestep/rank/chunk.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect()

        """
        if self._dvs_module:
            return self._dvs_module.end_update(session_id)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.end_update({arg_string})"
            return self._session.cmd(cmd)

    def server_create(self, uri: str) -> int:
        """Create a Dynamic Visualization Store server instance for the client to connect.
        
        Parameters
        ----------
        uri: str
            URI of server to create of the format protocol://hostname:port, i.e. grpc://localhost:50055 or null:// 
            Check https://developer.ansys.com/docs/post-processing - Dynamic Visualization Store API 
            for detailed info.
        
        Returns
        -------
        server_id: int
            unique id dynamically created for this server

        """
        if self._dvs_module:
            return self._dvs_module.server_create(uri)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = uri.__repr__()
            if isinstance(uri, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.server_create({arg_string})"
            return self._session.cmd(cmd)

    def server_get_uri(self, server_id: int) -> str:
        """Create a Dynamic Visualization Store server instance for the client to connect.
        
        Parameters
        ----------
        server_id: int
            id of server created by server_create()
        
        Returns
        -------
        uri: str
            The uri of the input server

        """
        if self._dvs_module:
            return self._dvs_module.server_get_uri(server_id)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = server_id.__repr__()
            if isinstance(server_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.server_get_uri({arg_string})"
            return self._session.cmd(cmd)

    def server_shutdown(self, server_id: int) -> None:
        """Shutdown this server thread.
        
        Parameters
        ----------
        server_id: int
            id of server created by server_create()

        """
        if self._dvs_module:
            return self._dvs_module.server_shutdown(server_id)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = server_id.__repr__()
            if isinstance(server_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.server_shutdown({arg_string})"
            return self._session.cmd(cmd)

    def server_shutdown_all(self) -> None:
        """Shutdown all DVS servers.

        """
        if self._dvs_module:
            return self._dvs_module.server_shutdown_all()
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.server_shutdown_all({arg_string})"
            return self._session.cmd(cmd)

    def server_start(self, server_id: int, server_num: Optional[int]=0, local_ranks: Optional[int]=1, options: Optional[Dict[str, str]]=None) -> None:
        """Start a Dynamic Visualization Store server in a separate thread to receive data from solver node.
        
        Parameters
        ----------
        server_id: int
            id of server created by server_create()
        server_number: int
            The server number (zero based) for this server, should be unique for each server in this server group.
        local_ranks: int
            Number of local ranks this server will handle.
        options: dict
            A dictionary holding the server options. 
            Check https://developer.ansys.com/docs/post-processing - Dynamic Visualization Store API 
            for detailed info.

        """
        if self._dvs_module:
            return self._dvs_module.server_start(server_id, server_num, local_ranks, options)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = server_id.__repr__()
            if isinstance(server_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = server_num.__repr__()
            if isinstance(server_num, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = local_ranks.__repr__()
            if isinstance(local_ranks, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = options.__repr__()
            if isinstance(options, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.server_start({arg_string})"
            return self._session.cmd(cmd)

    def server_started(self, server_id: int) -> bool:
        """Shutdown this server thread.
        
        Parameters
        ----------
        server_id: int
            id of server created by server_create()
        
        Returns
        -------
        (bool):
            True if the server is running

        """
        if self._dvs_module:
            return self._dvs_module.server_started(server_id)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = server_id.__repr__()
            if isinstance(server_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.server_started({arg_string})"
            return self._session.cmd(cmd)

    def server_timestep_count(self, server_id: int) -> Tuple[int, int]:
        """Query a Dynamic Visualization Store server as to the number of timesteps it contains
        
        Parameters
        ----------
        server_id: int
            id of server created by server_create()
        
        Returns
        -------
        (tuple):
            A tuple containing the number of incomplete timesteps and the number of complete
            timesteps currently in the server

        """
        if self._dvs_module:
            return self._dvs_module.server_timestep_count(server_id)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = server_id.__repr__()
            if isinstance(server_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.server_timestep_count({arg_string})"
            return self._session.cmd(cmd)

    def set_unit_system(self, session_id: int, unit: str) -> None:
        """Set a unit system (optional but recommended)
        
        Note: This cannot be changed once end_init() is called
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        unit: str
            The units to set. See https://nexusdemo.ensight.com/docs/python/html/ENS_UNITSSchema.html

        """
        if self._dvs_module:
            return self._dvs_module.set_unit_system(session_id, unit)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = unit.__repr__()
            if isinstance(unit, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.set_unit_system({arg_string})"
            return self._session.cmd(cmd)

    def shutdown(self) -> None:
        """Shuts down the api, performing any necessary cleanup.
        
        Also calls server_shutdown_all() if any servers are currently running

        """
        if self._dvs_module:
            return self._dvs_module.shutdown()
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.shutdown({arg_string})"
            return self._session.cmd(cmd)

    def update_copy_previous_part(self, session_id: int, part_id: int, options: str) -> None:
        """Copy data from the previous timestep before applying other data.
        
        Currently we only support the options of empty string, mesh or mesh.vars
        empty string and mesh.vars will copy the mesh, connectivity, and nodal/elemental variables.
        mesh only copies the mesh and connectivity.
        
        Note: Currently plots and case/part constant variables will not be copied via this option
        and must always be sent.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        part_id: int
            the id of the part we are copying data for, UINT32_MAX to select all parts
        options: str
            options to copy. An empty string or 'mesh.vars' will copy the mesh, connectivity, and nodal/elemental variables.
            'mesh' only copies the mesh and connectivity.

        """
        if self._dvs_module:
            return self._dvs_module.update_copy_previous_part(session_id, part_id, options)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = options.__repr__()
            if isinstance(options, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_copy_previous_part({arg_string})"
            return self._session.cmd(cmd)

    def update_elements(self, session_id: int, part_id: int, elem_type: int, indices: 'numpy.ndarray') -> None:
        """Update elements for a specific part and element type
        
        This will update the elements for a part. The number of indices needed will vary depending on the
        type and the num_elements. I.E. if updating triangles with 3 elements the indices array should be of
        size 9 (3 triangles with 3 indices)
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        part_id: int
            unique id of part to update elements for (must match parts added with add_part_info)
        elem_type: int
            element type of elements to update (points, triangles, quads, etc.). Check the ELEMTYPE enum available with this module.
        indices: numpy.ndarray
            node indices for each element, for ordering info per element type see EnSight's User Manual, section 9.2.3 Supported EnSight Gold Elements

        """
        if self._dvs_module:
            return self._dvs_module.update_elements(session_id, part_id, elem_type, indices)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = elem_type.__repr__()
            if isinstance(elem_type, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = indices.__repr__()
            if isinstance(indices, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_elements({arg_string})"
            return self._session.cmd(cmd)

    def update_elements_polygon(self, session_id: int, part_id: int, elem_type: int, nodes_per_polygon: 'numpy.ndarray', indices: 'numpy.ndarray') -> None:
        """Update N-SIDED elements
        
        This method will send over a list of arbitrarily sized polygons. The nodes_per_polygon param is an array
        containing the size of each polygon. I.E. if sending a quadrangle, and a 25 sided element the nodes_per_polygon
        array might look like [4, 25]. The size of the indices array would be 4+25=29 in this example where the first
        4 items in the indices array would correspond to the first item in the nodes_per_polygon array, the next 25 items
        in the indices array would correspond to the second item in the nodes_per_polygon array
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        part_id: int
            unique id of part to update elements for (must match parts added with add_part_info)
        elem_type: int
            element type of elements to update (points, triangles, quads, etc.). Check the ELEMTYPE enum available with this module.
        nodes_per_polygon: numpy.ndarray
            Array containing number of nodes in each element/polygon
        indices: numpy.ndarray
            node indices for each element, for ordering info per element type see EnSight's User Manual, section 9.2.3 Supported EnSight Gold Elements

        """
        if self._dvs_module:
            return self._dvs_module.update_elements_polygon(session_id, part_id, elem_type, nodes_per_polygon, indices)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = elem_type.__repr__()
            if isinstance(elem_type, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = nodes_per_polygon.__repr__()
            if isinstance(nodes_per_polygon, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = indices.__repr__()
            if isinstance(indices, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_elements_polygon({arg_string})"
            return self._session.cmd(cmd)

    def update_elements_polyhedral(self, session_id: int, part_id: int, elem_type: int, faces_per_element: 'numpy.ndarray', nodes_per_face: 'numpy.ndarray', indices: 'numpy.ndarray') -> None:
        """Update N-FACED Elements
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        part_id: int
            unique id of part to update elements for (must match parts added with add_part_info)
        elem_type: int
            element type of elements to update (points, triangles, quads, etc.). Check the ELEMTYPE enum available with this module.
        faces_per_element: numpy.ndarray
            Array of how many faces are in each element
        nodes_per_face: numpy.ndarray
            Array of how many nodes each face contains
        indices: numpy.ndarray
            node indices for each element, for ordering info per element type see EnSight's User Manual, section 9.2.3 Supported EnSight Gold Elements

        """
        if self._dvs_module:
            return self._dvs_module.update_elements_polyhedral(session_id, part_id, elem_type, faces_per_element, nodes_per_face)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = elem_type.__repr__()
            if isinstance(elem_type, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = faces_per_element.__repr__()
            if isinstance(faces_per_element, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = nodes_per_face.__repr__()
            if isinstance(nodes_per_face, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_elements_polyhedral({arg_string})"
            return self._session.cmd(cmd)

    def update_nodes(self, session_id: int, part_id: int, x: 'numpy.ndarray', y: 'numpy.ndarray', z: 'numpy.ndarray') -> None:
        """Update nodes for a specific part
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        part_id: int
            unique id of part to update elements for (must match parts added with add_part_info)
        x: numpy.ndarray
            array of x components for nodes
        y: numpy.ndarray
            array of y components for nodes
        z: numpy.ndarray
            array of z components for nodes

        """
        if self._dvs_module:
            return self._dvs_module.update_nodes(session_id, part_id, x, y, z)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = x.__repr__()
            if isinstance(x, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = y.__repr__()
            if isinstance(y, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = z.__repr__()
            if isinstance(z, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_nodes({arg_string})"
            return self._session.cmd(cmd)

    def update_nodes_curvilinear(self, session_id: int, part_id: int, global_ijk_max: 'numpy.ndarray', local_ijk_min: 'numpy.ndarray', local_ijk_max: 'numpy.ndarray', x_vals: 'numpy.ndarray', y_vals: 'numpy.ndarray', z_vals: 'numpy.ndarray') -> None:
        """Update the nodes for a curvilinear structured part.
        
        A curvilinear structured part is represented by the global IJK grid across ranks, the local sub-block's IJK rank,
        and the actual XYZ values for each IJK grid point in the local grid.
        
        Local IJK Dimensions: The min/max represent a local sub-block from the overall global grid. This could be the entire range
        if not splitting the grid into multiple ranks or a specific slice. For example you could have a 2ix3jx4k grid where it was
        split across the I dimension. One rank would specify min/max IJK as min:[0,0,0], max:[0,2,3], the other rank would specify
        min/max IJK as min:[1,0,0], max:[1,2,3]. If sending the data all as one rank it would be the full range of: min:[0,0,0], max:[1,2,3]
        
        IJK Vals: These specify the actual XYZ location for each IJK value in the grid. The order of these should be by the fastest changing dimension
        being I, the next being J, and the next being K. I.E. for a 2x2x2 grid the x_vals array would contain the X component for IJK values:
        [i0 j0 k0][i1 j0 k0][i0 j1 k0][i1 j1 k0][i0 j0 k1][i1 j0 k1][i0 j1 k1][i1 j1 k1].
        
        Note: iblanking information is sent via update_var_node_scalar() using STRUCTURED_IBLANKED_NODES as the variable id
        Note: Ghost element information is sent via update_var_element_scalar() using STRUCTURED_GHOST_ELEMENTS as the variable id
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        part_id: int
            unique id of part to update elements for (must match parts added with add_part_info)
        global_ijk_max: numpy.ndarray 
            The one based global ijk max of the mesh across all ranks
        local_ijk_min: numpy.ndarray 
            the zero based local sub-block ijk min for this rank
        local_ijk_max: numpy.ndarray 
            the zero based local sub-block ijk max for this rank
        x_vals: numpy.ndarray
            The actual X component for each IJK value for the local sub block (size (iMax-iMin+1)*(jMax-jMin+1)*(kMax-kMin+1))
        y_vals: numpy.ndarray
            The actual Y component for each IJK value for the local sub block (size (iMax-iMin+1)*(jMax-jMin+1)*(kMax-kMin+1))
        z_vals: numpy.ndarray
            The actual Z component for each IJK value for the local sub block (size (iMax-iMin+1)*(jMax-jMin+1)*(kMax-kMin+1))

        """
        if self._dvs_module:
            return self._dvs_module.update_nodes_curvilinear(session_id, part_id, global_ijk_max, local_ijk_min, local_ijk_max, x_vals, y_vals, z_vals)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = global_ijk_max.__repr__()
            if isinstance(global_ijk_max, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = local_ijk_min.__repr__()
            if isinstance(local_ijk_min, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = local_ijk_max.__repr__()
            if isinstance(local_ijk_max, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = x_vals.__repr__()
            if isinstance(x_vals, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = y_vals.__repr__()
            if isinstance(y_vals, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = z_vals.__repr__()
            if isinstance(z_vals, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_nodes_curvilinear({arg_string})"
            return self._session.cmd(cmd)

    def update_nodes_parallelepiped(self, session_id: int, part_id: int, global_ijk_max: 'numpy.ndarray', local_ijk_min: 'numpy.ndarray', local_ijk_max: 'numpy.ndarray', origin: 'numpy.ndarray', dir_i: 'numpy.ndarray', dir_j: 'numpy.ndarray', dir_k: 'numpy.ndarray', i_vals: 'numpy.ndarray', j_vals: 'numpy.ndarray', k_vals: 'numpy.ndarray') -> None:
        """Update the nodes for a parallelepiped structured part
        
        A parallelepiped structured part is represented by the global IJK grid across ranks, the local sub-block's IJK range,
        the ogigin of the IJK sub-block, the normalized direction (unit) vectors for each IJK dimension, and the absolute distances
        for each IJK index from the origin of this sub-block.
        
        Global IJK Max: for a 2x3x4 grid would be: [2 3 4]
        Local IJK Dimensions: The min/max represent a local sub-block from the overall global grid. This could be the entire range
        if not splitting the grid into multiple ranks or a specific slice. For example you could have a 2ix3jx4k grid where it was
        split across the I dimension. One rank would specify min/max IJK as min:[0,0,0], max:[0,2,3], the other rank would specify
        min/max IJK as min:[1,0,0], max:[1,2,3]. If sending the data all as one rank it would be the full range of: min:[0,0,0], max:[1,2,3]
        Direction (Unit) Vectors: These represent the XYZ orientation of each IJK axis. I.E. if I==X J==Y K==Z the vectors would be
        dir_i: [1 0 0], dir_j: [0 1 0], dir_k: [0 0 1]
        
        IJK Vals: These specify the absolute distance from the XYZ origin in each IJK direction(specified by the direction vectors).
        So if the distance was 1 between every I index, 2 between every J index, and 3 in between every K index the arrays would look like:
        i_vals: [0 1 2 3 4 5....]
        j_vals: [0 2 4 6 8 10....]
        k_vals: [0 3 6 9 12 15....]
        
        Note: iblanking information is sent via update_var_node_scalar() using STRUCTURED_IBLANKED_NODES as the variable id
        Note: Ghost element information is sent via update_var_element_scalar() using STRUCTURED_GHOST_ELEMENTS as the variable id
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        part_id: int
            unique id of part to update elements for (must match parts added with add_part_info)
        global_ijk_max: numpy.ndarray 
            The one based global ijk max of the mesh across all ranks
        local_ijk_min: numpy.ndarray 
            the zero based local sub-block ijk min for this rank
        local_ijk_max: numpy.ndarray 
            the zero based local sub-block ijk max for this rank
        origin:
            the XYZ origin of this local ijk block
        dir_i:
            The normalized XYZ direction vector for the i dimension
        dir_j:
            The normalized XYZ direction vector for the j dimension
        dir_k:
            The normalized XYZ direction vector for the k dimension
        i_vals: numpy.ndarray
            The absolute distance vector for each i index from the local sub block's origin of size iMax-iMin+1
        j_vals: numpy.ndarray
            The absolute distance vector for each j index from the local sub block's origin of size iMax-iMin+1
        k_vals: numpy.ndarray
            The absolute distance vector for each k index from the local sub block's origin of size iMax-iMin+1

        """
        if self._dvs_module:
            return self._dvs_module.update_nodes_parallelepiped(session_id, part_id, global_ijk_max, local_ijk_min, local_ijk_max, origin, dir_i, dir_j, dir_k, i_vals, j_vals, k_vals)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = global_ijk_max.__repr__()
            if isinstance(global_ijk_max, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = local_ijk_min.__repr__()
            if isinstance(local_ijk_min, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = local_ijk_max.__repr__()
            if isinstance(local_ijk_max, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = origin.__repr__()
            if isinstance(origin, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = dir_i.__repr__()
            if isinstance(dir_i, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = dir_j.__repr__()
            if isinstance(dir_j, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = dir_k.__repr__()
            if isinstance(dir_k, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = i_vals.__repr__()
            if isinstance(i_vals, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = j_vals.__repr__()
            if isinstance(j_vals, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = k_vals.__repr__()
            if isinstance(k_vals, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_nodes_parallelepiped({arg_string})"
            return self._session.cmd(cmd)

    def update_plot(self, session_id: int, plot_id: int, x: 'numpy.ndarray', y: 'numpy.ndarray') -> None:
        """Update the data for a plot.
        
        
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        plot_id: int
            id of plot to update matching plot_infos sent with dvs_add_plot_info
        x: numpy.ndarray
            array of x axis values
        y: numpy.ndarray
            array of y axis values

        """
        if self._dvs_module:
            return self._dvs_module.update_plot(session_id, plot_id, x, y)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = plot_id.__repr__()
            if isinstance(plot_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = x.__repr__()
            if isinstance(x, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = y.__repr__()
            if isinstance(y, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_plot({arg_string})"
            return self._session.cmd(cmd)

    def update_var_case_scalar(self, session_id: int, var_id: int, value: 'float') -> None:
        """Update value of case scalar
        
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        value: float
            value to update

        """
        if self._dvs_module:
            return self._dvs_module.update_var_case_scalar(session_id, var_id, value)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = value.__repr__()
            if isinstance(value, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_case_scalar({arg_string})"
            return self._session.cmd(cmd)

    def update_var_case_vector(self, session_id: int, var_id: int, value: 'numpy.ndarray') -> None:
        """Update value of case vector
        
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        value: numpy.ndarray
            array of x,y,z values (size 3)

        """
        if self._dvs_module:
            return self._dvs_module.update_var_case_vector(session_id, var_id, value)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = value.__repr__()
            if isinstance(value, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_case_vector({arg_string})"
            return self._session.cmd(cmd)

    def update_var_element_scalar(self, session_id: int, var_id: int, part_id: int, elem_type: int, values: 'numpy.ndarray') -> None:
        """Update a field of scalars on elements
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id for part element is associated with (must match parts added with add_part_info)
        elem_type: int
            element type of elements to update (points, triangles, quads, etc.). Check the ELEMTYPE enum available with this module.
        values: numpy.ndarray
            array of scalars

        """
        if self._dvs_module:
            return self._dvs_module.update_var_element_scalar(session_id, var_id, part_id, elem_type, values)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = elem_type.__repr__()
            if isinstance(elem_type, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = values.__repr__()
            if isinstance(values, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_element_scalar({arg_string})"
            return self._session.cmd(cmd)

    def update_var_element_scalar_int64(self, session_id: int, var_id: int, part_id: int, elem_type: int, values: 'numpy.ndarray') -> None:
        """Update a field of int64 scalars on elements
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id for part element is associated with (must match parts added with add_part_info)
        elem_type: int
            element type of elements to update (points, triangles, quads, etc.). Check the ELEMTYPE enum available with this module.
        values: numpy.ndarray
            array of scalars

        """
        if self._dvs_module:
            return self._dvs_module.update_var_element_scalar_int64(session_id, var_id, part_id, elem_type, values)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = elem_type.__repr__()
            if isinstance(elem_type, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = values.__repr__()
            if isinstance(values, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_element_scalar_int64({arg_string})"
            return self._session.cmd(cmd)

    def update_var_element_vector(self, session_id: int, var_id: int, part_id: int, elem_type: int, values: 'numpy.ndarray') -> None:
        """Updates a field of vectors on elements.
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id for part element is associated with (must match parts added with add_part_info)
        elem_type: int
            element type of elements to update (points, triangles, quads, etc.). Check the ELEMTYPE enum available with this module.
        values: numpy.ndarray
            array of values to udpate, should be the size of number of elements * 3, values are XYZ XYZ XYZ.......... XYZ

        """
        if self._dvs_module:
            return self._dvs_module.update_var_element_vector(session_id, var_id, part_id, elem_type, values)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = elem_type.__repr__()
            if isinstance(elem_type, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = values.__repr__()
            if isinstance(values, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_element_vector({arg_string})"
            return self._session.cmd(cmd)

    def update_var_node_scalar(self, session_id: int, var_id: int, part_id: int, values: 'numpy.ndarray') -> None:
        """Update a field of scalars on nodes
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id for part element is associated with (must match parts added with add_part_info)
        values: numpy.ndarray
            array of scalars

        """
        if self._dvs_module:
            return self._dvs_module.update_var_node_scalar(session_id, var_id, part_id, values)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = values.__repr__()
            if isinstance(values, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_node_scalar({arg_string})"
            return self._session.cmd(cmd)

    def update_var_node_scalar_int64(self, session_id: int, var_id: int, part_id: int, values: 'numpy.ndarray') -> None:
        """Update a field of int64 scalars on nodes
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id for part element is associated with (must match parts added with add_part_info)
        values: numpy.ndarray
            array of scalars

        """
        if self._dvs_module:
            return self._dvs_module.update_var_node_scalar_int64(session_id, var_id, part_id, values)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = values.__repr__()
            if isinstance(values, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_node_scalar_int64({arg_string})"
            return self._session.cmd(cmd)

    def update_var_node_vector(self, session_id: int, var_id: int, part_id: int, values: 'numpy.ndarray') -> None:
        """Update a field of vectors on nodes
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id for part element is associated with (must match parts added with add_part_info)
        values: numpy.ndarray
            array of values to udpate, should be the size of number of nodes * 3, values are XYZ XYZ XYZ.......... XYZ

        """
        if self._dvs_module:
            return self._dvs_module.update_var_node_vector(session_id, var_id, part_id, values)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = values.__repr__()
            if isinstance(values, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_node_vector({arg_string})"
            return self._session.cmd(cmd)

    def update_var_part_scalar(self, session_id: int, var_id: int, part_id: int, value: float) -> None:
        """Update value of part scalar
        
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id of part associated with (must match parts added with add_part_info)
        value: float
            value_to_update

        """
        if self._dvs_module:
            return self._dvs_module.update_var_part_scalar(session_id, var_id, part_id, value)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = value.__repr__()
            if isinstance(value, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_part_scalar({arg_string})"
            return self._session.cmd(cmd)

    def update_var_part_vector(self, session_id: int, var_id: int, part_id: int, value: 'numpy.ndarray') -> None:
        """Update value of part scalar
        
        
        Parameters
        ----------
        session_id: int
            id for session created by connect(): int
        var_id: int
            unique id of variable to update (must match var added with add_var_info)
        part_id: int
            unique id of part associated with (must match parts added with add_part_info)
        value: numpy.ndarray
            array of x,y,z values (size 3)

        """
        if self._dvs_module:
            return self._dvs_module.update_var_part_vector(session_id, var_id, part_id, value)
        if self._session:
            self._session.cmd('import dynamic_visualization_store', do_eval=False)
            self._session.cmd('import numpy', do_eval=False)
            arg_list = []
            data = session_id.__repr__()
            if isinstance(session_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = var_id.__repr__()
            if isinstance(var_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = part_id.__repr__()
            if isinstance(part_id, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            data = value.__repr__()
            if isinstance(value, numpy.ndarray):
                data = data.replace("array(", "numpy.array(").replace("float32", "numpy.float32").replace("float64", "numpy.float64").replace("int32", "numpy.int32").replace("int64", "numpy.int64")
            arg_list.append(data)
            arg_string = ",".join(arg_list)
            cmd = f"dynamic_visualization_store.update_var_part_vector({arg_string})"
            return self._session.cmd(cmd)

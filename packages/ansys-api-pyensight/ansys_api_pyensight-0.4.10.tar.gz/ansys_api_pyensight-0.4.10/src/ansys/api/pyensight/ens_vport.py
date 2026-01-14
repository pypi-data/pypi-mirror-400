"""ens_vport module

The ens_vport module provides a proxy interface to EnSight ENS_VPORT instances

"""
from ansys.pyensight.core.session import Session
from ansys.pyensight.core.ensobj import ENSOBJ
from ansys.pyensight.core import ensobjlist
from typing import Any, Dict, List, Type, Union, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ansys.api.pyensight.ensight_api import ENS_VAR, ENS_ANNOT, ENS_PALETTE, ENS_PART, ENS_SOURCE, ENS_CASE, ENS_QUERY, ENS_GROUP, ENS_TOOL, ENS_TEXTURE, ENS_PLOTTER, ENS_POLYLINE, ENS_FRAME, ENS_PROBE, ENS_FLIPBOOK, ENS_SCENE, ENS_LPART, ENS_STATE, ens_emitterobj

class ENS_VPORT(ENSOBJ):
    """This class acts as a proxy for the EnSight Python class ensight.objs.ENS_VPORT

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
        """Get information about GUI groups for this query's attributes

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

    def createviewport(self, *args, **kwargs) -> Any:
        """Create a new viewport

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.createviewport({arg_string})"
        return self._session.cmd(cmd)

    def interpolate(self, *args, **kwargs) -> Any:
        """Interpolate vectors

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        for arg in args:
            arg_list.append(arg.__repr__())
        for key, value in kwargs.items():
            arg_list.append(f"{key}={value.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.interpolate({arg_string})"
        return self._session.cmd(cmd)

    def transform(self, axis_angle: Optional[List[float]] = None, quaternion: Optional[List[float]] = None,    translation: Optional[List[float]] = None, data_translation: Optional[List[float]] = None,    scale: Optional[List[float]] = None, link: int = 0) -> None:
        """This method applies an incremental transformation to the specified viewport view.
        
        For an :class:`pyensight.ens_part_particle_trace.ENS_PART_PARTICLE_TRACE`
        instance, this method will return the data spce coordinates and time of each
        particle trace point.  Optionally, it can return variable values sampled at
        those coordinates.
        
        Args:
            axis_angle:
                For a four value input tuple of the form ``[nx,ny,nz,angle]``, apply a rotation over
                the normal specified by ``[nx,ny,nz]`` in data space by the ``angle`` (in radians).
            quaternion:
                For a four value input tuple of the form ``[a,b,c,d]``, apply the rotation specified
                by the normalized quaternion represented by the tuple.  The rotation is applied in
                data space.  Note: this is equivalent to combining the input with the
                to the :class:`pyensight.ens_vport.ENS_VPORT.ROTATION` attribute.
            translation:
                For a three value input tuple of the form ``[dx,dy,dz]``, apply a translation in
                screen space by the input tuple.  Note: this is equivalent to adding the components
                to the :class:`pyensight.ens_vport.ENS_VPORT.TRANSLATION` attribute.
            data_translation:
                For a three value input tuple of the form ``[dx,dy,dz]``, apply a translation in
                data space by the input tuple.
            scale:
                The value may either be a scalar or a three value tuple.  The former specifies isotropic
                data space scaling and the latter allows for anisotropic scaling.  Note: it is strongly
                recommended that anisotropic scaling not be used if it can at all be avoided as many
                EnSight operations assume isotropic scaling.  This is equivalent to component-wise
                multiplication with the :class:`pyensight.ens_vport.ENS_VPORT.SCALE` attribute.
            link:
                If non-zero and the target viewport is linked to other viewports, the transform will
                be applied to this and all linked viewports.
        
        Example:
            ::
        
                # get the default viewport
                v = session.ensight.objs.core.VPORTS[0]
                # apply a rotation over the data X axis and increase the scale 20%
                v.transform(axis_angle=[1,0,0,0.07], scale=1.2)
                # translate in the data space X axis by one unit
                v.transform(data_translation=(-1,0,0))

        """
        arg_obj = f"{self._remote_obj()}"
        arg_list: List[str] = []
        arg_list.append(f"axis_angle={axis_angle.__repr__()}")
        arg_list.append(f"quaternion={quaternion.__repr__()}")
        arg_list.append(f"translation={translation.__repr__()}")
        arg_list.append(f"data_translation={data_translation.__repr__()}")
        arg_list.append(f"scale={scale.__repr__()}")
        arg_list.append(f"link={link.__repr__()}")
        arg_string = ",".join(arg_list)
        cmd = f"{arg_obj}.transform({arg_string})"
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
    def ENS_TURBO_VPORT(self) -> str:
        """ENS_TURBO_VPORT property
        
        Turbo Vport
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_VPORT)
        _value = cast(str, value)
        return _value

    @ENS_TURBO_VPORT.setter
    def ENS_TURBO_VPORT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_VPORT, value)

    @property
    def ens_turbo_vport(self) -> str:
        """ENS_TURBO_VPORT property
        
        Turbo Vport
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_turbo_vport' and 'ENS_TURBO_VPORT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_VPORT)
        _value = cast(str, value)
        return _value

    @ens_turbo_vport.setter
    def ens_turbo_vport(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_VPORT, value)

    @property
    def ENS_TURBO_ANNO(self) -> str:
        """ENS_TURBO_ANNO property
        
        Turbo Annotation
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_ANNO)
        _value = cast(str, value)
        return _value

    @ENS_TURBO_ANNO.setter
    def ENS_TURBO_ANNO(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_ANNO, value)

    @property
    def ens_turbo_anno(self) -> str:
        """ENS_TURBO_ANNO property
        
        Turbo Annotation
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 4096 characters maximum
        
        Note: both 'ens_turbo_anno' and 'ENS_TURBO_ANNO' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ENS_TURBO_ANNO)
        _value = cast(str, value)
        return _value

    @ens_turbo_anno.setter
    def ens_turbo_anno(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.ENS_TURBO_ANNO, value)

    @property
    def DESCRIPTION(self) -> str:
        """DESCRIPTION property
        
        Description
        
        Supported operations:
            getattr
        Datatype:
            String, 80 characters maximum
        
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
            String, 80 characters maximum
        
        Note: both 'description' and 'DESCRIPTION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DESCRIPTION)
        _value = cast(str, value)
        return _value

    @property
    def SELECTED(self) -> int:
        """SELECTED property
        
        selected
        
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
        
        selected
        
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
    def ID(self) -> int:
        """ID property
        
        ID
        
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
        
        ID
        
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
    def LOOKATPOINT(self) -> List[float]:
        """LOOKATPOINT property
        
        look at point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKATPOINT)
        _value = cast(List[float], value)
        return _value

    @LOOKATPOINT.setter
    def LOOKATPOINT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKATPOINT, value)

    @property
    def lookatpoint(self) -> List[float]:
        """LOOKATPOINT property
        
        look at point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'lookatpoint' and 'LOOKATPOINT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKATPOINT)
        _value = cast(List[float], value)
        return _value

    @lookatpoint.setter
    def lookatpoint(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKATPOINT, value)

    @property
    def LOOKFROMPOINT(self) -> List[float]:
        """LOOKFROMPOINT property
        
        look from point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKFROMPOINT)
        _value = cast(List[float], value)
        return _value

    @LOOKFROMPOINT.setter
    def LOOKFROMPOINT(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKFROMPOINT, value)

    @property
    def lookfrompoint(self) -> List[float]:
        """LOOKFROMPOINT property
        
        look from point
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'lookfrompoint' and 'LOOKFROMPOINT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LOOKFROMPOINT)
        _value = cast(List[float], value)
        return _value

    @lookfrompoint.setter
    def lookfrompoint(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.LOOKFROMPOINT, value)

    @property
    def PERSPECTIVEANGLE(self) -> float:
        """PERSPECTIVEANGLE property
        
        perspective angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.PERSPECTIVEANGLE)
        _value = cast(float, value)
        return _value

    @PERSPECTIVEANGLE.setter
    def PERSPECTIVEANGLE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PERSPECTIVEANGLE, value)

    @property
    def perspectiveangle(self) -> float:
        """PERSPECTIVEANGLE property
        
        perspective angle
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'perspectiveangle' and 'PERSPECTIVEANGLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.PERSPECTIVEANGLE)
        _value = cast(float, value)
        return _value

    @perspectiveangle.setter
    def perspectiveangle(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.PERSPECTIVEANGLE, value)

    @property
    def ROTATION(self) -> List[float]:
        """ROTATION property
        
        rotation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Normalized Quaternion, 4 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ROTATION)
        _value = cast(List[float], value)
        return _value

    @ROTATION.setter
    def ROTATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ROTATION, value)

    @property
    def rotation(self) -> List[float]:
        """ROTATION property
        
        rotation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Normalized Quaternion, 4 element array
        
        Note: both 'rotation' and 'ROTATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ROTATION)
        _value = cast(List[float], value)
        return _value

    @rotation.setter
    def rotation(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ROTATION, value)

    @property
    def TRANSLATION(self) -> List[float]:
        """TRANSLATION property
        
        translation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSLATION)
        _value = cast(List[float], value)
        return _value

    @TRANSLATION.setter
    def TRANSLATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSLATION, value)

    @property
    def translation(self) -> List[float]:
        """TRANSLATION property
        
        translation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'translation' and 'TRANSLATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSLATION)
        _value = cast(List[float], value)
        return _value

    @translation.setter
    def translation(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSLATION, value)

    @property
    def SCALE(self) -> List[float]:
        """SCALE property
        
        scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(List[float], value)
        return _value

    @SCALE.setter
    def SCALE(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def scale(self) -> List[float]:
        """SCALE property
        
        scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'scale' and 'SCALE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SCALE)
        _value = cast(List[float], value)
        return _value

    @scale.setter
    def scale(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SCALE, value)

    @property
    def TRANSFORMCENTER(self) -> List[float]:
        """TRANSFORMCENTER property
        
        center of transformations
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSFORMCENTER)
        _value = cast(List[float], value)
        return _value

    @TRANSFORMCENTER.setter
    def TRANSFORMCENTER(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSFORMCENTER, value)

    @property
    def transformcenter(self) -> List[float]:
        """TRANSFORMCENTER property
        
        center of transformations
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 3 element array
        
        Note: both 'transformcenter' and 'TRANSFORMCENTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSFORMCENTER)
        _value = cast(List[float], value)
        return _value

    @transformcenter.setter
    def transformcenter(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSFORMCENTER, value)

    @property
    def ZCLIPLIMITS(self) -> List[float]:
        """ZCLIPLIMITS property
        
        zclip near and far planes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ZCLIPLIMITS)
        _value = cast(List[float], value)
        return _value

    @ZCLIPLIMITS.setter
    def ZCLIPLIMITS(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ZCLIPLIMITS, value)

    @property
    def zcliplimits(self) -> List[float]:
        """ZCLIPLIMITS property
        
        zclip near and far planes
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        
        Note: both 'zcliplimits' and 'ZCLIPLIMITS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ZCLIPLIMITS)
        _value = cast(List[float], value)
        return _value

    @zcliplimits.setter
    def zcliplimits(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.ZCLIPLIMITS, value)

    @property
    def LINKED(self) -> int:
        """LINKED property
        
        linked transformations
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums (bitfield):
            * ensight.objs.enums.LINK_GROUP1 - link group 1
        
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
        
        linked transformations
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums (bitfield):
            * ensight.objs.enums.LINK_GROUP1 - link group 1
        
        Note: both 'linked' and 'LINKED' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LINKED)
        _value = cast(int, value)
        return _value

    @linked.setter
    def linked(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LINKED, value)

    @property
    def TRANSFORMATION_DELTA(self) -> List[float]:
        """TRANSFORMATION_DELTA property
        
        last transformation change
        
        Supported operations:
            getattr
        Datatype:
            Float, 3 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSFORMATION_DELTA)
        _value = cast(List[float], value)
        return _value

    @property
    def transformation_delta(self) -> List[float]:
        """TRANSFORMATION_DELTA property
        
        last transformation change
        
        Supported operations:
            getattr
        Datatype:
            Float, 3 element array
        
        Note: both 'transformation_delta' and 'TRANSFORMATION_DELTA' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSFORMATION_DELTA)
        _value = cast(List[float], value)
        return _value

    @property
    def STACKING_ORDER(self) -> int:
        """STACKING_ORDER property
        
        viewport stacking order
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.STACKING_ORDER)
        _value = cast(int, value)
        return _value

    @STACKING_ORDER.setter
    def STACKING_ORDER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.STACKING_ORDER, value)

    @property
    def stacking_order(self) -> int:
        """STACKING_ORDER property
        
        viewport stacking order
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'stacking_order' and 'STACKING_ORDER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.STACKING_ORDER)
        _value = cast(int, value)
        return _value

    @stacking_order.setter
    def stacking_order(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.STACKING_ORDER, value)

    @property
    def BOUNDINGBOX(self) -> List[float]:
        """BOUNDINGBOX property
        
        visible geometry bounding box
        
        Supported operations:
            getattr
        Datatype:
            Float, 6 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BOUNDINGBOX)
        _value = cast(List[float], value)
        return _value

    @property
    def boundingbox(self) -> List[float]:
        """BOUNDINGBOX property
        
        visible geometry bounding box
        
        Supported operations:
            getattr
        Datatype:
            Float, 6 element array
        
        Note: both 'boundingbox' and 'BOUNDINGBOX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BOUNDINGBOX)
        _value = cast(List[float], value)
        return _value

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
    def PERSPECTIVE(self) -> int:
        """PERSPECTIVE property
        
        Perspective
        
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
        
        Perspective
        
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
    def GLOBALAXISXLABEL(self) -> str:
        """GLOBALAXISXLABEL property
        
        X Label
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISXLABEL)
        _value = cast(str, value)
        return _value

    @GLOBALAXISXLABEL.setter
    def GLOBALAXISXLABEL(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISXLABEL, value)

    @property
    def globalaxisxlabel(self) -> str:
        """GLOBALAXISXLABEL property
        
        X Label
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'globalaxisxlabel' and 'GLOBALAXISXLABEL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISXLABEL)
        _value = cast(str, value)
        return _value

    @globalaxisxlabel.setter
    def globalaxisxlabel(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISXLABEL, value)

    @property
    def GLOBALAXISYLABEL(self) -> str:
        """GLOBALAXISYLABEL property
        
        Y Label
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISYLABEL)
        _value = cast(str, value)
        return _value

    @GLOBALAXISYLABEL.setter
    def GLOBALAXISYLABEL(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISYLABEL, value)

    @property
    def globalaxisylabel(self) -> str:
        """GLOBALAXISYLABEL property
        
        Y Label
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'globalaxisylabel' and 'GLOBALAXISYLABEL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISYLABEL)
        _value = cast(str, value)
        return _value

    @globalaxisylabel.setter
    def globalaxisylabel(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISYLABEL, value)

    @property
    def GLOBALAXISZLABEL(self) -> str:
        """GLOBALAXISZLABEL property
        
        Z Label
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISZLABEL)
        _value = cast(str, value)
        return _value

    @GLOBALAXISZLABEL.setter
    def GLOBALAXISZLABEL(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISZLABEL, value)

    @property
    def globalaxiszlabel(self) -> str:
        """GLOBALAXISZLABEL property
        
        Z Label
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'globalaxiszlabel' and 'GLOBALAXISZLABEL' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISZLABEL)
        _value = cast(str, value)
        return _value

    @globalaxiszlabel.setter
    def globalaxiszlabel(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISZLABEL, value)

    @property
    def BORDERCOLOR(self) -> List[float]:
        """BORDERCOLOR property
        
        Border color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERCOLOR)
        _value = cast(List[float], value)
        return _value

    @BORDERCOLOR.setter
    def BORDERCOLOR(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERCOLOR, value)

    @property
    def bordercolor(self) -> List[float]:
        """BORDERCOLOR property
        
        Border color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'bordercolor' and 'BORDERCOLOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERCOLOR)
        _value = cast(List[float], value)
        return _value

    @bordercolor.setter
    def bordercolor(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERCOLOR, value)

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
    def LABELSIZE(self) -> float:
        """LABELSIZE property
        
        Label size - DEPRECATED in favor of LABELSIZE3D
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE)
        _value = cast(float, value)
        return _value

    @LABELSIZE.setter
    def LABELSIZE(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE, value)

    @property
    def labelsize(self) -> float:
        """LABELSIZE property
        
        Label size - DEPRECATED in favor of LABELSIZE3D
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'labelsize' and 'LABELSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE)
        _value = cast(float, value)
        return _value

    @labelsize.setter
    def labelsize(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE, value)

    @property
    def WIDTH(self) -> float:
        """WIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.WIDTH)
        _value = cast(float, value)
        return _value

    @WIDTH.setter
    def WIDTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.WIDTH, value)

    @property
    def width(self) -> float:
        """WIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'width' and 'WIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.WIDTH)
        _value = cast(float, value)
        return _value

    @width.setter
    def width(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.WIDTH, value)

    @property
    def HEIGHT(self) -> float:
        """HEIGHT property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.HEIGHT)
        _value = cast(float, value)
        return _value

    @HEIGHT.setter
    def HEIGHT(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEIGHT, value)

    @property
    def height(self) -> float:
        """HEIGHT property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'height' and 'HEIGHT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.HEIGHT)
        _value = cast(float, value)
        return _value

    @height.setter
    def height(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.HEIGHT, value)

    @property
    def LENGTH(self) -> int:
        """LENGTH property
        
        Length
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - as_specified
            * ensight.objs.enums.FALSE - rounded
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LENGTH)
        _value = cast(int, value)
        return _value

    @LENGTH.setter
    def LENGTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LENGTH, value)

    @property
    def length(self) -> int:
        """LENGTH property
        
        Length
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - as_specified
            * ensight.objs.enums.FALSE - rounded
        
        Note: both 'length' and 'LENGTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LENGTH)
        _value = cast(int, value)
        return _value

    @length.setter
    def length(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LENGTH, value)

    @property
    def ORIGINX(self) -> float:
        """ORIGINX property
        
        Origin x
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINX)
        _value = cast(float, value)
        return _value

    @ORIGINX.setter
    def ORIGINX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINX, value)

    @property
    def originx(self) -> float:
        """ORIGINX property
        
        Origin x
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'originx' and 'ORIGINX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINX)
        _value = cast(float, value)
        return _value

    @originx.setter
    def originx(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINX, value)

    @property
    def ORIGINY(self) -> float:
        """ORIGINY property
        
        Origin y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINY)
        _value = cast(float, value)
        return _value

    @ORIGINY.setter
    def ORIGINY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINY, value)

    @property
    def originy(self) -> float:
        """ORIGINY property
        
        Origin y
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'originy' and 'ORIGINY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.ORIGINY)
        _value = cast(float, value)
        return _value

    @originy.setter
    def originy(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.ORIGINY, value)

    @property
    def BACKGROUNDTYPE(self) -> int:
        """BACKGROUNDTYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VPORT_TRANSPARENT - transparent
            * ensight.objs.enums.VPORT_BLEND - blended
            * ensight.objs.enums.VPORT_CONS - constant
            * ensight.objs.enums.VPORT_SET - inherit
            * ensight.objs.enums.VPORT_IMAGE - image
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDTYPE)
        _value = cast(int, value)
        return _value

    @BACKGROUNDTYPE.setter
    def BACKGROUNDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDTYPE, value)

    @property
    def backgroundtype(self) -> int:
        """BACKGROUNDTYPE property
        
        Type
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.VPORT_TRANSPARENT - transparent
            * ensight.objs.enums.VPORT_BLEND - blended
            * ensight.objs.enums.VPORT_CONS - constant
            * ensight.objs.enums.VPORT_SET - inherit
            * ensight.objs.enums.VPORT_IMAGE - image
        
        Note: both 'backgroundtype' and 'BACKGROUNDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDTYPE)
        _value = cast(int, value)
        return _value

    @backgroundtype.setter
    def backgroundtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDTYPE, value)

    @property
    def CONSTANTRGB(self) -> List[float]:
        """CONSTANTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTANTRGB)
        _value = cast(List[float], value)
        return _value

    @CONSTANTRGB.setter
    def CONSTANTRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONSTANTRGB, value)

    @property
    def constantrgb(self) -> List[float]:
        """CONSTANTRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'constantrgb' and 'CONSTANTRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CONSTANTRGB)
        _value = cast(List[float], value)
        return _value

    @constantrgb.setter
    def constantrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CONSTANTRGB, value)

    @property
    def BLENDLEVELS(self) -> int:
        """BLENDLEVELS property
        
        Number of levels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 5]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDLEVELS)
        _value = cast(int, value)
        return _value

    @BLENDLEVELS.setter
    def BLENDLEVELS(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDLEVELS, value)

    @property
    def blendlevels(self) -> int:
        """BLENDLEVELS property
        
        Number of levels
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 5]
        
        Note: both 'blendlevels' and 'BLENDLEVELS' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDLEVELS)
        _value = cast(int, value)
        return _value

    @blendlevels.setter
    def blendlevels(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDLEVELS, value)

    @property
    def BLENDRGB5(self) -> List[float]:
        """BLENDRGB5 property
        
        Color level 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB5)
        _value = cast(List[float], value)
        return _value

    @BLENDRGB5.setter
    def BLENDRGB5(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB5, value)

    @property
    def blendrgb5(self) -> List[float]:
        """BLENDRGB5 property
        
        Color level 5
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'blendrgb5' and 'BLENDRGB5' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB5)
        _value = cast(List[float], value)
        return _value

    @blendrgb5.setter
    def blendrgb5(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB5, value)

    @property
    def BLENDRGB4(self) -> List[float]:
        """BLENDRGB4 property
        
        Color level 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB4)
        _value = cast(List[float], value)
        return _value

    @BLENDRGB4.setter
    def BLENDRGB4(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB4, value)

    @property
    def blendrgb4(self) -> List[float]:
        """BLENDRGB4 property
        
        Color level 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'blendrgb4' and 'BLENDRGB4' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB4)
        _value = cast(List[float], value)
        return _value

    @blendrgb4.setter
    def blendrgb4(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB4, value)

    @property
    def BLENDRGB3(self) -> List[float]:
        """BLENDRGB3 property
        
        Color level 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB3)
        _value = cast(List[float], value)
        return _value

    @BLENDRGB3.setter
    def BLENDRGB3(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB3, value)

    @property
    def blendrgb3(self) -> List[float]:
        """BLENDRGB3 property
        
        Color level 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'blendrgb3' and 'BLENDRGB3' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB3)
        _value = cast(List[float], value)
        return _value

    @blendrgb3.setter
    def blendrgb3(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB3, value)

    @property
    def BLENDRGB2(self) -> List[float]:
        """BLENDRGB2 property
        
        Color level 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB2)
        _value = cast(List[float], value)
        return _value

    @BLENDRGB2.setter
    def BLENDRGB2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB2, value)

    @property
    def blendrgb2(self) -> List[float]:
        """BLENDRGB2 property
        
        Color level 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'blendrgb2' and 'BLENDRGB2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB2)
        _value = cast(List[float], value)
        return _value

    @blendrgb2.setter
    def blendrgb2(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB2, value)

    @property
    def BLENDRGB1(self) -> List[float]:
        """BLENDRGB1 property
        
        Color level 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB1)
        _value = cast(List[float], value)
        return _value

    @BLENDRGB1.setter
    def BLENDRGB1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB1, value)

    @property
    def blendrgb1(self) -> List[float]:
        """BLENDRGB1 property
        
        Color level 1
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'blendrgb1' and 'BLENDRGB1' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDRGB1)
        _value = cast(List[float], value)
        return _value

    @blendrgb1.setter
    def blendrgb1(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDRGB1, value)

    @property
    def BLENDPOSITION4(self) -> float:
        """BLENDPOSITION4 property
        
        Position level 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDPOSITION4)
        _value = cast(float, value)
        return _value

    @BLENDPOSITION4.setter
    def BLENDPOSITION4(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDPOSITION4, value)

    @property
    def blendposition4(self) -> float:
        """BLENDPOSITION4 property
        
        Position level 4
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'blendposition4' and 'BLENDPOSITION4' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDPOSITION4)
        _value = cast(float, value)
        return _value

    @blendposition4.setter
    def blendposition4(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDPOSITION4, value)

    @property
    def BLENDPOSITION3(self) -> float:
        """BLENDPOSITION3 property
        
        Position level 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDPOSITION3)
        _value = cast(float, value)
        return _value

    @BLENDPOSITION3.setter
    def BLENDPOSITION3(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDPOSITION3, value)

    @property
    def blendposition3(self) -> float:
        """BLENDPOSITION3 property
        
        Position level 3
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'blendposition3' and 'BLENDPOSITION3' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDPOSITION3)
        _value = cast(float, value)
        return _value

    @blendposition3.setter
    def blendposition3(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDPOSITION3, value)

    @property
    def BLENDPOSITION2(self) -> float:
        """BLENDPOSITION2 property
        
        Position level 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDPOSITION2)
        _value = cast(float, value)
        return _value

    @BLENDPOSITION2.setter
    def BLENDPOSITION2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDPOSITION2, value)

    @property
    def blendposition2(self) -> float:
        """BLENDPOSITION2 property
        
        Position level 2
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'blendposition2' and 'BLENDPOSITION2' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BLENDPOSITION2)
        _value = cast(float, value)
        return _value

    @blendposition2.setter
    def blendposition2(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.BLENDPOSITION2, value)

    @property
    def BACKGROUNDIMAGENAME(self) -> str:
        """BACKGROUNDIMAGENAME property
        
        Image file
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDIMAGENAME)
        _value = cast(str, value)
        return _value

    @BACKGROUNDIMAGENAME.setter
    def BACKGROUNDIMAGENAME(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDIMAGENAME, value)

    @property
    def backgroundimagename(self) -> str:
        """BACKGROUNDIMAGENAME property
        
        Image file
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'backgroundimagename' and 'BACKGROUNDIMAGENAME' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BACKGROUNDIMAGENAME)
        _value = cast(str, value)
        return _value

    @backgroundimagename.setter
    def backgroundimagename(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.BACKGROUNDIMAGENAME, value)

    @property
    def VIEWDIMENSION(self) -> int:
        """VIEWDIMENSION property
        
        Dimension
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - 3D
            * ensight.objs.enums.FALSE - 2D
        
        """
        value = self.getattr(self._session.ensight.objs.enums.VIEWDIMENSION)
        _value = cast(int, value)
        return _value

    @VIEWDIMENSION.setter
    def VIEWDIMENSION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VIEWDIMENSION, value)

    @property
    def viewdimension(self) -> int:
        """VIEWDIMENSION property
        
        Dimension
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - 3D
            * ensight.objs.enums.FALSE - 2D
        
        Note: both 'viewdimension' and 'VIEWDIMENSION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.VIEWDIMENSION)
        _value = cast(int, value)
        return _value

    @viewdimension.setter
    def viewdimension(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.VIEWDIMENSION, value)

    @property
    def LIGHT1POSITION(self) -> int:
        """LIGHT1POSITION property
        
        Light position
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LIGHT_SOURCE_ABSOLUTE - Absolute
            * ensight.objs.enums.LIGHT_SOURCE_RELATIVE - Relative
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT1POSITION)
        _value = cast(int, value)
        return _value

    @LIGHT1POSITION.setter
    def LIGHT1POSITION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT1POSITION, value)

    @property
    def light1position(self) -> int:
        """LIGHT1POSITION property
        
        Light position
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LIGHT_SOURCE_ABSOLUTE - Absolute
            * ensight.objs.enums.LIGHT_SOURCE_RELATIVE - Relative
        
        Note: both 'light1position' and 'LIGHT1POSITION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT1POSITION)
        _value = cast(int, value)
        return _value

    @light1position.setter
    def light1position(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT1POSITION, value)

    @property
    def LIGHT1AZIMUTH(self) -> float:
        """LIGHT1AZIMUTH property
        
        Light azimuth
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [-180.0, 180.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT1AZIMUTH)
        _value = cast(float, value)
        return _value

    @LIGHT1AZIMUTH.setter
    def LIGHT1AZIMUTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT1AZIMUTH, value)

    @property
    def light1azimuth(self) -> float:
        """LIGHT1AZIMUTH property
        
        Light azimuth
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [-180.0, 180.0]
        
        Note: both 'light1azimuth' and 'LIGHT1AZIMUTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT1AZIMUTH)
        _value = cast(float, value)
        return _value

    @light1azimuth.setter
    def light1azimuth(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT1AZIMUTH, value)

    @property
    def LIGHT1ELEVATION(self) -> float:
        """LIGHT1ELEVATION property
        
        Light elevation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [-90.0, 90.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT1ELEVATION)
        _value = cast(float, value)
        return _value

    @LIGHT1ELEVATION.setter
    def LIGHT1ELEVATION(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT1ELEVATION, value)

    @property
    def light1elevation(self) -> float:
        """LIGHT1ELEVATION property
        
        Light elevation
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [-90.0, 90.0]
        
        Note: both 'light1elevation' and 'LIGHT1ELEVATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT1ELEVATION)
        _value = cast(float, value)
        return _value

    @light1elevation.setter
    def light1elevation(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT1ELEVATION, value)

    @property
    def LIGHT2INTENSITY(self) -> float:
        """LIGHT2INTENSITY property
        
        Headlight intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT2INTENSITY)
        _value = cast(float, value)
        return _value

    @LIGHT2INTENSITY.setter
    def LIGHT2INTENSITY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT2INTENSITY, value)

    @property
    def light2intensity(self) -> float:
        """LIGHT2INTENSITY property
        
        Headlight intensity
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'light2intensity' and 'LIGHT2INTENSITY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LIGHT2INTENSITY)
        _value = cast(float, value)
        return _value

    @light2intensity.setter
    def light2intensity(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.LIGHT2INTENSITY, value)

    @property
    def TRACK(self) -> int:
        """TRACK property
        
        Track
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.NO_TRACKING - Off
            * ensight.objs.enums.TRACK_PART_CENTROID - part_centroid
            * ensight.objs.enums.TRACK_PART_XMIN - part_xmin
            * ensight.objs.enums.TRACK_PART_XMAX - part_xmax
            * ensight.objs.enums.TRACK_PART_YMIN - part_ymin
            * ensight.objs.enums.TRACK_PART_YMAX - part_ymax
            * ensight.objs.enums.TRACK_PART_ZMIN - part_zmin
            * ensight.objs.enums.TRACK_PART_ZMAX - part_zmax
            * ensight.objs.enums.TRACK_NODE_NUMBER - node_number
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRACK)
        _value = cast(int, value)
        return _value

    @TRACK.setter
    def TRACK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRACK, value)

    @property
    def track(self) -> int:
        """TRACK property
        
        Track
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.NO_TRACKING - Off
            * ensight.objs.enums.TRACK_PART_CENTROID - part_centroid
            * ensight.objs.enums.TRACK_PART_XMIN - part_xmin
            * ensight.objs.enums.TRACK_PART_XMAX - part_xmax
            * ensight.objs.enums.TRACK_PART_YMIN - part_ymin
            * ensight.objs.enums.TRACK_PART_YMAX - part_ymax
            * ensight.objs.enums.TRACK_PART_ZMIN - part_zmin
            * ensight.objs.enums.TRACK_PART_ZMAX - part_zmax
            * ensight.objs.enums.TRACK_NODE_NUMBER - node_number
        
        Note: both 'track' and 'TRACK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRACK)
        _value = cast(int, value)
        return _value

    @track.setter
    def track(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRACK, value)

    @property
    def TRACKINGPARTID(self) -> int:
        """TRACKINGPARTID property
        
        Part ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRACKINGPARTID)
        _value = cast(int, value)
        return _value

    @TRACKINGPARTID.setter
    def TRACKINGPARTID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRACKINGPARTID, value)

    @property
    def trackingpartid(self) -> int:
        """TRACKINGPARTID property
        
        Part ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        
        Note: both 'trackingpartid' and 'TRACKINGPARTID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRACKINGPARTID)
        _value = cast(int, value)
        return _value

    @trackingpartid.setter
    def trackingpartid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRACKINGPARTID, value)

    @property
    def TRACKINGNODEID(self) -> int:
        """TRACKINGNODEID property
        
        Node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, inf]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRACKINGNODEID)
        _value = cast(int, value)
        return _value

    @TRACKINGNODEID.setter
    def TRACKINGNODEID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRACKINGNODEID, value)

    @property
    def trackingnodeid(self) -> int:
        """TRACKINGNODEID property
        
        Node ID
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, inf]
        
        Note: both 'trackingnodeid' and 'TRACKINGNODEID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRACKINGNODEID)
        _value = cast(int, value)
        return _value

    @trackingnodeid.setter
    def trackingnodeid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.TRACKINGNODEID, value)

    @property
    def GLOBALAXISVISIBLE(self) -> int:
        """GLOBALAXISVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISVISIBLE)
        _value = cast(int, value)
        return _value

    @GLOBALAXISVISIBLE.setter
    def GLOBALAXISVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISVISIBLE, value)

    @property
    def globalaxisvisible(self) -> int:
        """GLOBALAXISVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'globalaxisvisible' and 'GLOBALAXISVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISVISIBLE)
        _value = cast(int, value)
        return _value

    @globalaxisvisible.setter
    def globalaxisvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISVISIBLE, value)

    @property
    def GLOBALAXISLOCATION(self) -> List[float]:
        """GLOBALAXISLOCATION property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISLOCATION)
        _value = cast(List[float], value)
        return _value

    @GLOBALAXISLOCATION.setter
    def GLOBALAXISLOCATION(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISLOCATION, value)

    @property
    def globalaxislocation(self) -> List[float]:
        """GLOBALAXISLOCATION property
        
        Location
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 2 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'globalaxislocation' and 'GLOBALAXISLOCATION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GLOBALAXISLOCATION)
        _value = cast(List[float], value)
        return _value

    @globalaxislocation.setter
    def globalaxislocation(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GLOBALAXISLOCATION, value)

    @property
    def BORDERVISIBLE(self) -> int:
        """BORDERVISIBLE property
        
        Border visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERVISIBLE)
        _value = cast(int, value)
        return _value

    @BORDERVISIBLE.setter
    def BORDERVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERVISIBLE, value)

    @property
    def bordervisible(self) -> int:
        """BORDERVISIBLE property
        
        Border visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'bordervisible' and 'BORDERVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.BORDERVISIBLE)
        _value = cast(int, value)
        return _value

    @bordervisible.setter
    def bordervisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.BORDERVISIBLE, value)

    @property
    def AXESVISIBLE(self) -> int:
        """AXESVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXESVISIBLE)
        _value = cast(int, value)
        return _value

    @AXESVISIBLE.setter
    def AXESVISIBLE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXESVISIBLE, value)

    @property
    def axesvisible(self) -> int:
        """AXESVISIBLE property
        
        Visible
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axesvisible' and 'AXESVISIBLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXESVISIBLE)
        _value = cast(int, value)
        return _value

    @axesvisible.setter
    def axesvisible(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXESVISIBLE, value)

    @property
    def AUTOSIZE(self) -> int:
        """AUTOSIZE property
        
        Auto size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AUTOSIZE)
        _value = cast(int, value)
        return _value

    @AUTOSIZE.setter
    def AUTOSIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AUTOSIZE, value)

    @property
    def autosize(self) -> int:
        """AUTOSIZE property
        
        Auto size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'autosize' and 'AUTOSIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AUTOSIZE)
        _value = cast(int, value)
        return _value

    @autosize.setter
    def autosize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AUTOSIZE, value)

    @property
    def AXISLINEWIDTH(self) -> int:
        """AXISLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISLINEWIDTH)
        _value = cast(int, value)
        return _value

    @AXISLINEWIDTH.setter
    def AXISLINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISLINEWIDTH, value)

    @property
    def axislinewidth(self) -> int:
        """AXISLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'axislinewidth' and 'AXISLINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISLINEWIDTH)
        _value = cast(int, value)
        return _value

    @axislinewidth.setter
    def axislinewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISLINEWIDTH, value)

    @property
    def AXISRGB(self) -> List[float]:
        """AXISRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISRGB)
        _value = cast(List[float], value)
        return _value

    @AXISRGB.setter
    def AXISRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISRGB, value)

    @property
    def axisrgb(self) -> List[float]:
        """AXISRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisrgb' and 'AXISRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISRGB)
        _value = cast(List[float], value)
        return _value

    @axisrgb.setter
    def axisrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISRGB, value)

    @property
    def TRANSPARENCY(self) -> float:
        """TRANSPARENCY property
        
        Opaqueness
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSPARENCY)
        _value = cast(float, value)
        return _value

    @TRANSPARENCY.setter
    def TRANSPARENCY(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSPARENCY, value)

    @property
    def transparency(self) -> float:
        """TRANSPARENCY property
        
        Opaqueness
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [0.0, 1.0]
        
        Note: both 'transparency' and 'TRANSPARENCY' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TRANSPARENCY)
        _value = cast(float, value)
        return _value

    @transparency.setter
    def transparency(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TRANSPARENCY, value)

    @property
    def DIMENSION(self) -> int:
        """DIMENSION property
        
        Dimension
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - 3D
            * ensight.objs.enums.FALSE - 2D
        
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION)
        _value = cast(int, value)
        return _value

    @DIMENSION.setter
    def DIMENSION(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION, value)

    @property
    def dimension(self) -> int:
        """DIMENSION property
        
        Dimension
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.TRUE - 3D
            * ensight.objs.enums.FALSE - 2D
        
        Note: both 'dimension' and 'DIMENSION' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.DIMENSION)
        _value = cast(int, value)
        return _value

    @dimension.setter
    def dimension(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.DIMENSION, value)

    @property
    def LABELSIZE2D(self) -> int:
        """LABELSIZE2D property
        
        Label size 2D
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE2D)
        _value = cast(int, value)
        return _value

    @LABELSIZE2D.setter
    def LABELSIZE2D(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE2D, value)

    @property
    def labelsize2d(self) -> int:
        """LABELSIZE2D property
        
        Label size 2D
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'labelsize2d' and 'LABELSIZE2D' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE2D)
        _value = cast(int, value)
        return _value

    @labelsize2d.setter
    def labelsize2d(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE2D, value)

    @property
    def LABELSIZE3D(self) -> int:
        """LABELSIZE3D property
        
        Label size 3D
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE3D)
        _value = cast(int, value)
        return _value

    @LABELSIZE3D.setter
    def LABELSIZE3D(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE3D, value)

    @property
    def labelsize3d(self) -> int:
        """LABELSIZE3D property
        
        Label size 3D
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'labelsize3d' and 'LABELSIZE3D' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.LABELSIZE3D)
        _value = cast(int, value)
        return _value

    @labelsize3d.setter
    def labelsize3d(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.LABELSIZE3D, value)

    @property
    def GRIDLINEWIDTH(self) -> int:
        """GRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @GRIDLINEWIDTH.setter
    def GRIDLINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINEWIDTH, value)

    @property
    def gridlinewidth(self) -> int:
        """GRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'gridlinewidth' and 'GRIDLINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @gridlinewidth.setter
    def gridlinewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINEWIDTH, value)

    @property
    def GRIDLINETYPE(self) -> int:
        """GRIDLINETYPE property
        
        Line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @GRIDLINETYPE.setter
    def GRIDLINETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINETYPE, value)

    @property
    def gridlinetype(self) -> int:
        """GRIDLINETYPE property
        
        Line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        Note: both 'gridlinetype' and 'GRIDLINETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @gridlinetype.setter
    def gridlinetype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDLINETYPE, value)

    @property
    def GRIDRGB(self) -> List[float]:
        """GRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDRGB)
        _value = cast(List[float], value)
        return _value

    @GRIDRGB.setter
    def GRIDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDRGB, value)

    @property
    def gridrgb(self) -> List[float]:
        """GRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'gridrgb' and 'GRIDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.GRIDRGB)
        _value = cast(List[float], value)
        return _value

    @gridrgb.setter
    def gridrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.GRIDRGB, value)

    @property
    def TICKSCALEFACTOR(self) -> float:
        """TICKSCALEFACTOR property
        
        Tick scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.TICKSCALEFACTOR)
        _value = cast(float, value)
        return _value

    @TICKSCALEFACTOR.setter
    def TICKSCALEFACTOR(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TICKSCALEFACTOR, value)

    @property
    def tickscalefactor(self) -> float:
        """TICKSCALEFACTOR property
        
        Tick scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'tickscalefactor' and 'TICKSCALEFACTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.TICKSCALEFACTOR)
        _value = cast(float, value)
        return _value

    @tickscalefactor.setter
    def tickscalefactor(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.TICKSCALEFACTOR, value)

    @property
    def SUBGRIDLINEWIDTH(self) -> int:
        """SUBGRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @SUBGRIDLINEWIDTH.setter
    def SUBGRIDLINEWIDTH(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH, value)

    @property
    def subgridlinewidth(self) -> int:
        """SUBGRIDLINEWIDTH property
        
        Line width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 4]
        
        Note: both 'subgridlinewidth' and 'SUBGRIDLINEWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH)
        _value = cast(int, value)
        return _value

    @subgridlinewidth.setter
    def subgridlinewidth(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINEWIDTH, value)

    @property
    def SUBGRIDLINETYPE(self) -> int:
        """SUBGRIDLINETYPE property
        
        Line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @SUBGRIDLINETYPE.setter
    def SUBGRIDLINETYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE, value)

    @property
    def subgridlinetype(self) -> int:
        """SUBGRIDLINETYPE property
        
        Line style
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.LINE_SOLID - solid
            * ensight.objs.enums.LINE_DOTTED - dotted
            * ensight.objs.enums.LINE_DOTDSH - dash
        
        Note: both 'subgridlinetype' and 'SUBGRIDLINETYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE)
        _value = cast(int, value)
        return _value

    @subgridlinetype.setter
    def subgridlinetype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDLINETYPE, value)

    @property
    def SUBGRIDRGB(self) -> List[float]:
        """SUBGRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDRGB)
        _value = cast(List[float], value)
        return _value

    @SUBGRIDRGB.setter
    def SUBGRIDRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDRGB, value)

    @property
    def subgridrgb(self) -> List[float]:
        """SUBGRIDRGB property
        
        Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'subgridrgb' and 'SUBGRIDRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBGRIDRGB)
        _value = cast(List[float], value)
        return _value

    @subgridrgb.setter
    def subgridrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBGRIDRGB, value)

    @property
    def SUBTICKSCALEFACTOR(self) -> float:
        """SUBTICKSCALEFACTOR property
        
        Sub tick scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBTICKSCALEFACTOR)
        _value = cast(float, value)
        return _value

    @SUBTICKSCALEFACTOR.setter
    def SUBTICKSCALEFACTOR(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBTICKSCALEFACTOR, value)

    @property
    def subtickscalefactor(self) -> float:
        """SUBTICKSCALEFACTOR property
        
        Sub tick scale
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'subtickscalefactor' and 'SUBTICKSCALEFACTOR' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.SUBTICKSCALEFACTOR)
        _value = cast(float, value)
        return _value

    @subtickscalefactor.setter
    def subtickscalefactor(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.SUBTICKSCALEFACTOR, value)

    @property
    def AXISXTITLE(self) -> str:
        """AXISXTITLE property
        
        Title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLE)
        _value = cast(str, value)
        return _value

    @AXISXTITLE.setter
    def AXISXTITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLE, value)

    @property
    def axisxtitle(self) -> str:
        """AXISXTITLE property
        
        Title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisxtitle' and 'AXISXTITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLE)
        _value = cast(str, value)
        return _value

    @axisxtitle.setter
    def axisxtitle(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLE, value)

    @property
    def AXISYTITLE(self) -> str:
        """AXISYTITLE property
        
        Title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLE)
        _value = cast(str, value)
        return _value

    @AXISYTITLE.setter
    def AXISYTITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLE, value)

    @property
    def axisytitle(self) -> str:
        """AXISYTITLE property
        
        Title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisytitle' and 'AXISYTITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLE)
        _value = cast(str, value)
        return _value

    @axisytitle.setter
    def axisytitle(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLE, value)

    @property
    def AXISXTITLESIZE(self) -> int:
        """AXISXTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLESIZE)
        _value = cast(int, value)
        return _value

    @AXISXTITLESIZE.setter
    def AXISXTITLESIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLESIZE, value)

    @property
    def axisxtitlesize(self) -> int:
        """AXISXTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axisxtitlesize' and 'AXISXTITLESIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTITLESIZE)
        _value = cast(int, value)
        return _value

    @axisxtitlesize.setter
    def axisxtitlesize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTITLESIZE, value)

    @property
    def AXISXMIN(self) -> float:
        """AXISXMIN property
        
        Min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMIN)
        _value = cast(float, value)
        return _value

    @AXISXMIN.setter
    def AXISXMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMIN, value)

    @property
    def axisxmin(self) -> float:
        """AXISXMIN property
        
        Min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisxmin' and 'AXISXMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMIN)
        _value = cast(float, value)
        return _value

    @axisxmin.setter
    def axisxmin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMIN, value)

    @property
    def AXISXMAX(self) -> float:
        """AXISXMAX property
        
        Max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMAX)
        _value = cast(float, value)
        return _value

    @AXISXMAX.setter
    def AXISXMAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMAX, value)

    @property
    def axisxmax(self) -> float:
        """AXISXMAX property
        
        Max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisxmax' and 'AXISXMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXMAX)
        _value = cast(float, value)
        return _value

    @axisxmax.setter
    def axisxmax(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXMAX, value)

    @property
    def AXISXORIG(self) -> float:
        """AXISXORIG property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXORIG)
        _value = cast(float, value)
        return _value

    @AXISXORIG.setter
    def AXISXORIG(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXORIG, value)

    @property
    def axisxorig(self) -> float:
        """AXISXORIG property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisxorig' and 'AXISXORIG' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXORIG)
        _value = cast(float, value)
        return _value

    @axisxorig.setter
    def axisxorig(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXORIG, value)

    @property
    def AXISWIDTH(self) -> float:
        """AXISWIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISWIDTH)
        _value = cast(float, value)
        return _value

    @AXISWIDTH.setter
    def AXISWIDTH(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISWIDTH, value)

    @property
    def axiswidth(self) -> float:
        """AXISWIDTH property
        
        Width
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axiswidth' and 'AXISWIDTH' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISWIDTH)
        _value = cast(float, value)
        return _value

    @axiswidth.setter
    def axiswidth(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISWIDTH, value)

    @property
    def AXISXLABELAXISLOC(self) -> int:
        """AXISXLABELAXISLOC property
        
        Value axis loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELAXISLOC)
        _value = cast(int, value)
        return _value

    @AXISXLABELAXISLOC.setter
    def AXISXLABELAXISLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELAXISLOC, value)

    @property
    def axisxlabelaxisloc(self) -> int:
        """AXISXLABELAXISLOC property
        
        Value axis loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        Note: both 'axisxlabelaxisloc' and 'AXISXLABELAXISLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELAXISLOC)
        _value = cast(int, value)
        return _value

    @axisxlabelaxisloc.setter
    def axisxlabelaxisloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELAXISLOC, value)

    @property
    def AXISXLABELEXTENTLOC(self) -> int:
        """AXISXLABELEXTENTLOC property
        
        Value extent location (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELEXTENTLOC)
        _value = cast(int, value)
        return _value

    @AXISXLABELEXTENTLOC.setter
    def AXISXLABELEXTENTLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELEXTENTLOC, value)

    @property
    def axisxlabelextentloc(self) -> int:
        """AXISXLABELEXTENTLOC property
        
        Value extent location (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        Note: both 'axisxlabelextentloc' and 'AXISXLABELEXTENTLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELEXTENTLOC)
        _value = cast(int, value)
        return _value

    @axisxlabelextentloc.setter
    def axisxlabelextentloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELEXTENTLOC, value)

    @property
    def AXISXLABELFILTER(self) -> int:
        """AXISXLABELFILTER property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELFILTER)
        _value = cast(int, value)
        return _value

    @AXISXLABELFILTER.setter
    def AXISXLABELFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELFILTER, value)

    @property
    def axisxlabelfilter(self) -> int:
        """AXISXLABELFILTER property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'axisxlabelfilter' and 'AXISXLABELFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELFILTER)
        _value = cast(int, value)
        return _value

    @axisxlabelfilter.setter
    def axisxlabelfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELFILTER, value)

    @property
    def AXISXFORMAT(self) -> str:
        """AXISXFORMAT property
        
        Value format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXFORMAT)
        _value = cast(str, value)
        return _value

    @AXISXFORMAT.setter
    def AXISXFORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXFORMAT, value)

    @property
    def axisxformat(self) -> str:
        """AXISXFORMAT property
        
        Value format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisxformat' and 'AXISXFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXFORMAT)
        _value = cast(str, value)
        return _value

    @axisxformat.setter
    def axisxformat(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXFORMAT, value)

    @property
    def AXISXLABELRGB(self) -> List[float]:
        """AXISXLABELRGB property
        
        Value Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELRGB)
        _value = cast(List[float], value)
        return _value

    @AXISXLABELRGB.setter
    def AXISXLABELRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELRGB, value)

    @property
    def axisxlabelrgb(self) -> List[float]:
        """AXISXLABELRGB property
        
        Value Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisxlabelrgb' and 'AXISXLABELRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXLABELRGB)
        _value = cast(List[float], value)
        return _value

    @axisxlabelrgb.setter
    def axisxlabelrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXLABELRGB, value)

    @property
    def AXISXDISPLAYONEDGE(self) -> int:
        """AXISXDISPLAYONEDGE property
        
        Value display on silhouette edge
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXDISPLAYONEDGE)
        _value = cast(int, value)
        return _value

    @AXISXDISPLAYONEDGE.setter
    def AXISXDISPLAYONEDGE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXDISPLAYONEDGE, value)

    @property
    def axisxdisplayonedge(self) -> int:
        """AXISXDISPLAYONEDGE property
        
        Value display on silhouette edge
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxdisplayonedge' and 'AXISXDISPLAYONEDGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXDISPLAYONEDGE)
        _value = cast(int, value)
        return _value

    @axisxdisplayonedge.setter
    def axisxdisplayonedge(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXDISPLAYONEDGE, value)

    @property
    def AXISXYMINZMIN(self) -> int:
        """AXISXYMINZMIN property
        
        Value location Y min/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMINZMIN)
        _value = cast(int, value)
        return _value

    @AXISXYMINZMIN.setter
    def AXISXYMINZMIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMINZMIN, value)

    @property
    def axisxyminzmin(self) -> int:
        """AXISXYMINZMIN property
        
        Value location Y min/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxyminzmin' and 'AXISXYMINZMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMINZMIN)
        _value = cast(int, value)
        return _value

    @axisxyminzmin.setter
    def axisxyminzmin(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMINZMIN, value)

    @property
    def AXISXYMINZMAX(self) -> int:
        """AXISXYMINZMAX property
        
        Value location Y min/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMINZMAX)
        _value = cast(int, value)
        return _value

    @AXISXYMINZMAX.setter
    def AXISXYMINZMAX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMINZMAX, value)

    @property
    def axisxyminzmax(self) -> int:
        """AXISXYMINZMAX property
        
        Value location Y min/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxyminzmax' and 'AXISXYMINZMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMINZMAX)
        _value = cast(int, value)
        return _value

    @axisxyminzmax.setter
    def axisxyminzmax(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMINZMAX, value)

    @property
    def AXISXYMAXZMIN(self) -> int:
        """AXISXYMAXZMIN property
        
        Value location Y max/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMAXZMIN)
        _value = cast(int, value)
        return _value

    @AXISXYMAXZMIN.setter
    def AXISXYMAXZMIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMAXZMIN, value)

    @property
    def axisxymaxzmin(self) -> int:
        """AXISXYMAXZMIN property
        
        Value location Y max/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxymaxzmin' and 'AXISXYMAXZMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMAXZMIN)
        _value = cast(int, value)
        return _value

    @axisxymaxzmin.setter
    def axisxymaxzmin(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMAXZMIN, value)

    @property
    def AXISXYMAXZMAX(self) -> int:
        """AXISXYMAXZMAX property
        
        Value location Y max/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMAXZMAX)
        _value = cast(int, value)
        return _value

    @AXISXYMAXZMAX.setter
    def AXISXYMAXZMAX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMAXZMAX, value)

    @property
    def axisxymaxzmax(self) -> int:
        """AXISXYMAXZMAX property
        
        Value location Y max/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxymaxzmax' and 'AXISXYMAXZMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXYMAXZMAX)
        _value = cast(int, value)
        return _value

    @axisxymaxzmax.setter
    def axisxymaxzmax(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXYMAXZMAX, value)

    @property
    def AXISXGRIDTYPE(self) -> int:
        """AXISXGRIDTYPE property
        
        Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISXGRIDTYPE.setter
    def AXISXGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXGRIDTYPE, value)

    @property
    def axisxgridtype(self) -> int:
        """AXISXGRIDTYPE property
        
        Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisxgridtype' and 'AXISXGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisxgridtype.setter
    def axisxgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXGRIDTYPE, value)

    @property
    def AXISXTICK(self) -> int:
        """AXISXTICK property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTICK)
        _value = cast(int, value)
        return _value

    @AXISXTICK.setter
    def AXISXTICK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTICK, value)

    @property
    def axisxtick(self) -> int:
        """AXISXTICK property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxtick' and 'AXISXTICK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXTICK)
        _value = cast(int, value)
        return _value

    @axisxtick.setter
    def axisxtick(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXTICK, value)

    @property
    def AXISXNUMGRID(self) -> float:
        """AXISXNUMGRID property
        
        Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMGRID)
        _value = cast(float, value)
        return _value

    @AXISXNUMGRID.setter
    def AXISXNUMGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMGRID, value)

    @property
    def axisxnumgrid(self) -> float:
        """AXISXNUMGRID property
        
        Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 100.0]
        
        Note: both 'axisxnumgrid' and 'AXISXNUMGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMGRID)
        _value = cast(float, value)
        return _value

    @axisxnumgrid.setter
    def axisxnumgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMGRID, value)

    @property
    def AXISXSGRIDTYPE(self) -> int:
        """AXISXSGRIDTYPE property
        
        Sub Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISXSGRIDTYPE.setter
    def AXISXSGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE, value)

    @property
    def axisxsgridtype(self) -> int:
        """AXISXSGRIDTYPE property
        
        Sub Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisxsgridtype' and 'AXISXSGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisxsgridtype.setter
    def axisxsgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSGRIDTYPE, value)

    @property
    def AXISXSUBTICK(self) -> int:
        """AXISXSUBTICK property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSUBTICK)
        _value = cast(int, value)
        return _value

    @AXISXSUBTICK.setter
    def AXISXSUBTICK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSUBTICK, value)

    @property
    def axisxsubtick(self) -> int:
        """AXISXSUBTICK property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisxsubtick' and 'AXISXSUBTICK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXSUBTICK)
        _value = cast(int, value)
        return _value

    @axisxsubtick.setter
    def axisxsubtick(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXSUBTICK, value)

    @property
    def AXISXNUMSUBGRID(self) -> float:
        """AXISXNUMSUBGRID property
        
        Sub Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @AXISXNUMSUBGRID.setter
    def AXISXNUMSUBGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID, value)

    @property
    def axisxnumsubgrid(self) -> float:
        """AXISXNUMSUBGRID property
        
        Sub Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisxnumsubgrid' and 'AXISXNUMSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @axisxnumsubgrid.setter
    def axisxnumsubgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXNUMSUBGRID, value)

    @property
    def AXISXGRIDEXTENTLOC(self) -> int:
        """AXISXGRIDEXTENTLOC property
        
        Grid/SubGrid extent loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXGRIDEXTENTLOC)
        _value = cast(int, value)
        return _value

    @AXISXGRIDEXTENTLOC.setter
    def AXISXGRIDEXTENTLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXGRIDEXTENTLOC, value)

    @property
    def axisxgridextentloc(self) -> int:
        """AXISXGRIDEXTENTLOC property
        
        Grid/SubGrid extent loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        Note: both 'axisxgridextentloc' and 'AXISXGRIDEXTENTLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISXGRIDEXTENTLOC)
        _value = cast(int, value)
        return _value

    @axisxgridextentloc.setter
    def axisxgridextentloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISXGRIDEXTENTLOC, value)

    @property
    def AXISYTITLESIZE(self) -> int:
        """AXISYTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLESIZE)
        _value = cast(int, value)
        return _value

    @AXISYTITLESIZE.setter
    def AXISYTITLESIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLESIZE, value)

    @property
    def axisytitlesize(self) -> int:
        """AXISYTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axisytitlesize' and 'AXISYTITLESIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTITLESIZE)
        _value = cast(int, value)
        return _value

    @axisytitlesize.setter
    def axisytitlesize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTITLESIZE, value)

    @property
    def AXISYMIN(self) -> float:
        """AXISYMIN property
        
        Min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMIN)
        _value = cast(float, value)
        return _value

    @AXISYMIN.setter
    def AXISYMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMIN, value)

    @property
    def axisymin(self) -> float:
        """AXISYMIN property
        
        Min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisymin' and 'AXISYMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMIN)
        _value = cast(float, value)
        return _value

    @axisymin.setter
    def axisymin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMIN, value)

    @property
    def AXISYMAX(self) -> float:
        """AXISYMAX property
        
        Max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMAX)
        _value = cast(float, value)
        return _value

    @AXISYMAX.setter
    def AXISYMAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMAX, value)

    @property
    def axisymax(self) -> float:
        """AXISYMAX property
        
        Max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisymax' and 'AXISYMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYMAX)
        _value = cast(float, value)
        return _value

    @axisymax.setter
    def axisymax(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYMAX, value)

    @property
    def AXISYORIG(self) -> float:
        """AXISYORIG property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYORIG)
        _value = cast(float, value)
        return _value

    @AXISYORIG.setter
    def AXISYORIG(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYORIG, value)

    @property
    def axisyorig(self) -> float:
        """AXISYORIG property
        
        Origin
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisyorig' and 'AXISYORIG' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYORIG)
        _value = cast(float, value)
        return _value

    @axisyorig.setter
    def axisyorig(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYORIG, value)

    @property
    def AXISHEIGHT(self) -> float:
        """AXISHEIGHT property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISHEIGHT)
        _value = cast(float, value)
        return _value

    @AXISHEIGHT.setter
    def AXISHEIGHT(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISHEIGHT, value)

    @property
    def axisheight(self) -> float:
        """AXISHEIGHT property
        
        Height
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axisheight' and 'AXISHEIGHT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISHEIGHT)
        _value = cast(float, value)
        return _value

    @axisheight.setter
    def axisheight(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISHEIGHT, value)

    @property
    def AXISYLABELAXISLOC(self) -> int:
        """AXISYLABELAXISLOC property
        
        Value axis loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELAXISLOC)
        _value = cast(int, value)
        return _value

    @AXISYLABELAXISLOC.setter
    def AXISYLABELAXISLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELAXISLOC, value)

    @property
    def axisylabelaxisloc(self) -> int:
        """AXISYLABELAXISLOC property
        
        Value axis loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        Note: both 'axisylabelaxisloc' and 'AXISYLABELAXISLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELAXISLOC)
        _value = cast(int, value)
        return _value

    @axisylabelaxisloc.setter
    def axisylabelaxisloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELAXISLOC, value)

    @property
    def AXISYLABELFILTER(self) -> int:
        """AXISYLABELFILTER property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELFILTER)
        _value = cast(int, value)
        return _value

    @AXISYLABELFILTER.setter
    def AXISYLABELFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELFILTER, value)

    @property
    def axisylabelfilter(self) -> int:
        """AXISYLABELFILTER property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'axisylabelfilter' and 'AXISYLABELFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELFILTER)
        _value = cast(int, value)
        return _value

    @axisylabelfilter.setter
    def axisylabelfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELFILTER, value)

    @property
    def AXISYLABELEXTENTLOC(self) -> int:
        """AXISYLABELEXTENTLOC property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELEXTENTLOC)
        _value = cast(int, value)
        return _value

    @AXISYLABELEXTENTLOC.setter
    def AXISYLABELEXTENTLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELEXTENTLOC, value)

    @property
    def axisylabelextentloc(self) -> int:
        """AXISYLABELEXTENTLOC property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        Note: both 'axisylabelextentloc' and 'AXISYLABELEXTENTLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELEXTENTLOC)
        _value = cast(int, value)
        return _value

    @axisylabelextentloc.setter
    def axisylabelextentloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELEXTENTLOC, value)

    @property
    def AXISYFORMAT(self) -> str:
        """AXISYFORMAT property
        
        Value format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYFORMAT)
        _value = cast(str, value)
        return _value

    @AXISYFORMAT.setter
    def AXISYFORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYFORMAT, value)

    @property
    def axisyformat(self) -> str:
        """AXISYFORMAT property
        
        Value format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisyformat' and 'AXISYFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYFORMAT)
        _value = cast(str, value)
        return _value

    @axisyformat.setter
    def axisyformat(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYFORMAT, value)

    @property
    def AXISYLABELRGB(self) -> List[float]:
        """AXISYLABELRGB property
        
        Value Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELRGB)
        _value = cast(List[float], value)
        return _value

    @AXISYLABELRGB.setter
    def AXISYLABELRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELRGB, value)

    @property
    def axisylabelrgb(self) -> List[float]:
        """AXISYLABELRGB property
        
        Value Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axisylabelrgb' and 'AXISYLABELRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYLABELRGB)
        _value = cast(List[float], value)
        return _value

    @axisylabelrgb.setter
    def axisylabelrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYLABELRGB, value)

    @property
    def AXISYDISPLAYONEDGE(self) -> int:
        """AXISYDISPLAYONEDGE property
        
        Value display on silhouette edge
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYDISPLAYONEDGE)
        _value = cast(int, value)
        return _value

    @AXISYDISPLAYONEDGE.setter
    def AXISYDISPLAYONEDGE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYDISPLAYONEDGE, value)

    @property
    def axisydisplayonedge(self) -> int:
        """AXISYDISPLAYONEDGE property
        
        Value display on silhouette edge
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisydisplayonedge' and 'AXISYDISPLAYONEDGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYDISPLAYONEDGE)
        _value = cast(int, value)
        return _value

    @axisydisplayonedge.setter
    def axisydisplayonedge(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYDISPLAYONEDGE, value)

    @property
    def AXISZDISPLAYONEDGE(self) -> int:
        """AXISZDISPLAYONEDGE property
        
        Value display on silhouette edge
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZDISPLAYONEDGE)
        _value = cast(int, value)
        return _value

    @AXISZDISPLAYONEDGE.setter
    def AXISZDISPLAYONEDGE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZDISPLAYONEDGE, value)

    @property
    def axiszdisplayonedge(self) -> int:
        """AXISZDISPLAYONEDGE property
        
        Value display on silhouette edge
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axiszdisplayonedge' and 'AXISZDISPLAYONEDGE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZDISPLAYONEDGE)
        _value = cast(int, value)
        return _value

    @axiszdisplayonedge.setter
    def axiszdisplayonedge(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZDISPLAYONEDGE, value)

    @property
    def AXISYYMINZMIN(self) -> int:
        """AXISYYMINZMIN property
        
        Value location X min/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMINZMIN)
        _value = cast(int, value)
        return _value

    @AXISYYMINZMIN.setter
    def AXISYYMINZMIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMINZMIN, value)

    @property
    def axisyyminzmin(self) -> int:
        """AXISYYMINZMIN property
        
        Value location X min/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisyyminzmin' and 'AXISYYMINZMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMINZMIN)
        _value = cast(int, value)
        return _value

    @axisyyminzmin.setter
    def axisyyminzmin(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMINZMIN, value)

    @property
    def AXISYYMINZMAX(self) -> int:
        """AXISYYMINZMAX property
        
        Value location X min/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMINZMAX)
        _value = cast(int, value)
        return _value

    @AXISYYMINZMAX.setter
    def AXISYYMINZMAX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMINZMAX, value)

    @property
    def axisyyminzmax(self) -> int:
        """AXISYYMINZMAX property
        
        Value location X min/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisyyminzmax' and 'AXISYYMINZMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMINZMAX)
        _value = cast(int, value)
        return _value

    @axisyyminzmax.setter
    def axisyyminzmax(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMINZMAX, value)

    @property
    def AXISYYMAXZMIN(self) -> int:
        """AXISYYMAXZMIN property
        
        Value location X max/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMAXZMIN)
        _value = cast(int, value)
        return _value

    @AXISYYMAXZMIN.setter
    def AXISYYMAXZMIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMAXZMIN, value)

    @property
    def axisyymaxzmin(self) -> int:
        """AXISYYMAXZMIN property
        
        Value location X max/Z min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisyymaxzmin' and 'AXISYYMAXZMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMAXZMIN)
        _value = cast(int, value)
        return _value

    @axisyymaxzmin.setter
    def axisyymaxzmin(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMAXZMIN, value)

    @property
    def AXISYYMAXZMAX(self) -> int:
        """AXISYYMAXZMAX property
        
        Value location X max/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMAXZMAX)
        _value = cast(int, value)
        return _value

    @AXISYYMAXZMAX.setter
    def AXISYYMAXZMAX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMAXZMAX, value)

    @property
    def axisyymaxzmax(self) -> int:
        """AXISYYMAXZMAX property
        
        Value location X max/Z max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisyymaxzmax' and 'AXISYYMAXZMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYYMAXZMAX)
        _value = cast(int, value)
        return _value

    @axisyymaxzmax.setter
    def axisyymaxzmax(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYYMAXZMAX, value)

    @property
    def AXISYGRIDTYPE(self) -> int:
        """AXISYGRIDTYPE property
        
        Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISYGRIDTYPE.setter
    def AXISYGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYGRIDTYPE, value)

    @property
    def axisygridtype(self) -> int:
        """AXISYGRIDTYPE property
        
        Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisygridtype' and 'AXISYGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisygridtype.setter
    def axisygridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYGRIDTYPE, value)

    @property
    def AXISYTICK(self) -> int:
        """AXISYTICK property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTICK)
        _value = cast(int, value)
        return _value

    @AXISYTICK.setter
    def AXISYTICK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTICK, value)

    @property
    def axisytick(self) -> int:
        """AXISYTICK property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisytick' and 'AXISYTICK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYTICK)
        _value = cast(int, value)
        return _value

    @axisytick.setter
    def axisytick(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYTICK, value)

    @property
    def AXISYNUMGRID(self) -> float:
        """AXISYNUMGRID property
        
        Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMGRID)
        _value = cast(float, value)
        return _value

    @AXISYNUMGRID.setter
    def AXISYNUMGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMGRID, value)

    @property
    def axisynumgrid(self) -> float:
        """AXISYNUMGRID property
        
        Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 100.0]
        
        Note: both 'axisynumgrid' and 'AXISYNUMGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMGRID)
        _value = cast(float, value)
        return _value

    @axisynumgrid.setter
    def axisynumgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMGRID, value)

    @property
    def AXISYSGRIDTYPE(self) -> int:
        """AXISYSGRIDTYPE property
        
        Sub Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISYSGRIDTYPE.setter
    def AXISYSGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE, value)

    @property
    def axisysgridtype(self) -> int:
        """AXISYSGRIDTYPE property
        
        Sub Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axisysgridtype' and 'AXISYSGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axisysgridtype.setter
    def axisysgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSGRIDTYPE, value)

    @property
    def AXISYSUBTICK(self) -> int:
        """AXISYSUBTICK property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSUBTICK)
        _value = cast(int, value)
        return _value

    @AXISYSUBTICK.setter
    def AXISYSUBTICK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSUBTICK, value)

    @property
    def axisysubtick(self) -> int:
        """AXISYSUBTICK property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisysubtick' and 'AXISYSUBTICK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYSUBTICK)
        _value = cast(int, value)
        return _value

    @axisysubtick.setter
    def axisysubtick(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYSUBTICK, value)

    @property
    def AXISYNUMSUBGRID(self) -> float:
        """AXISYNUMSUBGRID property
        
        Sub Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @AXISYNUMSUBGRID.setter
    def AXISYNUMSUBGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID, value)

    @property
    def axisynumsubgrid(self) -> float:
        """AXISYNUMSUBGRID property
        
        Sub Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisynumsubgrid' and 'AXISYNUMSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @axisynumsubgrid.setter
    def axisynumsubgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYNUMSUBGRID, value)

    @property
    def AXISYGRIDEXTENTLOC(self) -> int:
        """AXISYGRIDEXTENTLOC property
        
        Grid/SubGrid extent loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYGRIDEXTENTLOC)
        _value = cast(int, value)
        return _value

    @AXISYGRIDEXTENTLOC.setter
    def AXISYGRIDEXTENTLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYGRIDEXTENTLOC, value)

    @property
    def axisygridextentloc(self) -> int:
        """AXISYGRIDEXTENTLOC property
        
        Grid/SubGrid extent loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        Note: both 'axisygridextentloc' and 'AXISYGRIDEXTENTLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISYGRIDEXTENTLOC)
        _value = cast(int, value)
        return _value

    @axisygridextentloc.setter
    def axisygridextentloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISYGRIDEXTENTLOC, value)

    @property
    def AXISZTITLE(self) -> str:
        """AXISZTITLE property
        
        Title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZTITLE)
        _value = cast(str, value)
        return _value

    @AXISZTITLE.setter
    def AXISZTITLE(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZTITLE, value)

    @property
    def axisztitle(self) -> str:
        """AXISZTITLE property
        
        Title
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axisztitle' and 'AXISZTITLE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZTITLE)
        _value = cast(str, value)
        return _value

    @axisztitle.setter
    def axisztitle(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZTITLE, value)

    @property
    def AXISZTITLESIZE(self) -> int:
        """AXISZTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZTITLESIZE)
        _value = cast(int, value)
        return _value

    @AXISZTITLESIZE.setter
    def AXISZTITLESIZE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZTITLESIZE, value)

    @property
    def axisztitlesize(self) -> int:
        """AXISZTITLESIZE property
        
        Title size
        
        Supported operations:
            getattr, setattr
        Datatype:
            Integer, scalar
        Range:
            [1, 100]
        
        Note: both 'axisztitlesize' and 'AXISZTITLESIZE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZTITLESIZE)
        _value = cast(int, value)
        return _value

    @axisztitlesize.setter
    def axisztitlesize(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZTITLESIZE, value)

    @property
    def AXISZMIN(self) -> float:
        """AXISZMIN property
        
        Min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZMIN)
        _value = cast(float, value)
        return _value

    @AXISZMIN.setter
    def AXISZMIN(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZMIN, value)

    @property
    def axiszmin(self) -> float:
        """AXISZMIN property
        
        Min value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axiszmin' and 'AXISZMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZMIN)
        _value = cast(float, value)
        return _value

    @axiszmin.setter
    def axiszmin(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZMIN, value)

    @property
    def AXISZMAX(self) -> float:
        """AXISZMAX property
        
        Max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZMAX)
        _value = cast(float, value)
        return _value

    @AXISZMAX.setter
    def AXISZMAX(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZMAX, value)

    @property
    def axiszmax(self) -> float:
        """AXISZMAX property
        
        Max value
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        
        Note: both 'axiszmax' and 'AXISZMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZMAX)
        _value = cast(float, value)
        return _value

    @axiszmax.setter
    def axiszmax(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZMAX, value)

    @property
    def AXISZLABELAXISLOC(self) -> int:
        """AXISZLABELAXISLOC property
        
        Value axis loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELAXISLOC)
        _value = cast(int, value)
        return _value

    @AXISZLABELAXISLOC.setter
    def AXISZLABELAXISLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELAXISLOC, value)

    @property
    def axiszlabelaxisloc(self) -> int:
        """AXISZLABELAXISLOC property
        
        Value axis loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_LABEL_NONE - none
            * ensight.objs.enums.XY_LABEL_ALL - all
            * ensight.objs.enums.XY_LABEL_BEG_END - beg_end
        
        Note: both 'axiszlabelaxisloc' and 'AXISZLABELAXISLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELAXISLOC)
        _value = cast(int, value)
        return _value

    @axiszlabelaxisloc.setter
    def axiszlabelaxisloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELAXISLOC, value)

    @property
    def AXISZLABELFILTER(self) -> int:
        """AXISZLABELFILTER property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELFILTER)
        _value = cast(int, value)
        return _value

    @AXISZLABELFILTER.setter
    def AXISZLABELFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELFILTER, value)

    @property
    def axiszlabelfilter(self) -> int:
        """AXISZLABELFILTER property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'axiszlabelfilter' and 'AXISZLABELFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELFILTER)
        _value = cast(int, value)
        return _value

    @axiszlabelfilter.setter
    def axiszlabelfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELFILTER, value)

    @property
    def AXISZLABELEXTENTLOC(self) -> int:
        """AXISZLABELEXTENTLOC property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELEXTENTLOC)
        _value = cast(int, value)
        return _value

    @AXISZLABELEXTENTLOC.setter
    def AXISZLABELEXTENTLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELEXTENTLOC, value)

    @property
    def axiszlabelextentloc(self) -> int:
        """AXISZLABELEXTENTLOC property
        
        Value filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        Note: both 'axiszlabelextentloc' and 'AXISZLABELEXTENTLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELEXTENTLOC)
        _value = cast(int, value)
        return _value

    @axiszlabelextentloc.setter
    def axiszlabelextentloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELEXTENTLOC, value)

    @property
    def AXISZFORMAT(self) -> str:
        """AXISZFORMAT property
        
        Value format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZFORMAT)
        _value = cast(str, value)
        return _value

    @AXISZFORMAT.setter
    def AXISZFORMAT(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZFORMAT, value)

    @property
    def axiszformat(self) -> str:
        """AXISZFORMAT property
        
        Value format
        
        Supported operations:
            getattr, setattr
        Datatype:
            String, 1024 characters maximum
        
        Note: both 'axiszformat' and 'AXISZFORMAT' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZFORMAT)
        _value = cast(str, value)
        return _value

    @axiszformat.setter
    def axiszformat(self, value: str) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZFORMAT, value)

    @property
    def AXISZLABELRGB(self) -> List[float]:
        """AXISZLABELRGB property
        
        Value Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELRGB)
        _value = cast(List[float], value)
        return _value

    @AXISZLABELRGB.setter
    def AXISZLABELRGB(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELRGB, value)

    @property
    def axiszlabelrgb(self) -> List[float]:
        """AXISZLABELRGB property
        
        Value Color
        
        Supported operations:
            getattr, setattr
        Datatype:
            Color RGB, 3 element array
        Range:
            [0.0, 1.0]
        
        Note: both 'axiszlabelrgb' and 'AXISZLABELRGB' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZLABELRGB)
        _value = cast(List[float], value)
        return _value

    @axiszlabelrgb.setter
    def axiszlabelrgb(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZLABELRGB, value)

    @property
    def AXISZYMINZMIN(self) -> int:
        """AXISZYMINZMIN property
        
        Value location X min/Y min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMINZMIN)
        _value = cast(int, value)
        return _value

    @AXISZYMINZMIN.setter
    def AXISZYMINZMIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMINZMIN, value)

    @property
    def axiszyminzmin(self) -> int:
        """AXISZYMINZMIN property
        
        Value location X min/Y min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axiszyminzmin' and 'AXISZYMINZMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMINZMIN)
        _value = cast(int, value)
        return _value

    @axiszyminzmin.setter
    def axiszyminzmin(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMINZMIN, value)

    @property
    def AXISZYMINZMAX(self) -> int:
        """AXISZYMINZMAX property
        
        Value location X min/Y max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMINZMAX)
        _value = cast(int, value)
        return _value

    @AXISZYMINZMAX.setter
    def AXISZYMINZMAX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMINZMAX, value)

    @property
    def axiszyminzmax(self) -> int:
        """AXISZYMINZMAX property
        
        Value location X min/Y max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axiszyminzmax' and 'AXISZYMINZMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMINZMAX)
        _value = cast(int, value)
        return _value

    @axiszyminzmax.setter
    def axiszyminzmax(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMINZMAX, value)

    @property
    def AXISZYMAXZMIN(self) -> int:
        """AXISZYMAXZMIN property
        
        Value location X max/Y min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMAXZMIN)
        _value = cast(int, value)
        return _value

    @AXISZYMAXZMIN.setter
    def AXISZYMAXZMIN(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMAXZMIN, value)

    @property
    def axiszymaxzmin(self) -> int:
        """AXISZYMAXZMIN property
        
        Value location X max/Y min
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axiszymaxzmin' and 'AXISZYMAXZMIN' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMAXZMIN)
        _value = cast(int, value)
        return _value

    @axiszymaxzmin.setter
    def axiszymaxzmin(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMAXZMIN, value)

    @property
    def AXISZYMAXZMAX(self) -> int:
        """AXISZYMAXZMAX property
        
        Value location X max/Y max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMAXZMAX)
        _value = cast(int, value)
        return _value

    @AXISZYMAXZMAX.setter
    def AXISZYMAXZMAX(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMAXZMAX, value)

    @property
    def axiszymaxzmax(self) -> int:
        """AXISZYMAXZMAX property
        
        Value location X max/Y max
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axiszymaxzmax' and 'AXISZYMAXZMAX' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZYMAXZMAX)
        _value = cast(int, value)
        return _value

    @axiszymaxzmax.setter
    def axiszymaxzmax(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZYMAXZMAX, value)

    @property
    def AXISZGRIDTYPE(self) -> int:
        """AXISZGRIDTYPE property
        
        Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISZGRIDTYPE.setter
    def AXISZGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZGRIDTYPE, value)

    @property
    def axiszgridtype(self) -> int:
        """AXISZGRIDTYPE property
        
        Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axiszgridtype' and 'AXISZGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axiszgridtype.setter
    def axiszgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZGRIDTYPE, value)

    @property
    def AXISZTICK(self) -> int:
        """AXISZTICK property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZTICK)
        _value = cast(int, value)
        return _value

    @AXISZTICK.setter
    def AXISZTICK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZTICK, value)

    @property
    def axisztick(self) -> int:
        """AXISZTICK property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axisztick' and 'AXISZTICK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZTICK)
        _value = cast(int, value)
        return _value

    @axisztick.setter
    def axisztick(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZTICK, value)

    @property
    def AXISZNUMGRID(self) -> float:
        """AXISZNUMGRID property
        
        Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZNUMGRID)
        _value = cast(float, value)
        return _value

    @AXISZNUMGRID.setter
    def AXISZNUMGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZNUMGRID, value)

    @property
    def axisznumgrid(self) -> float:
        """AXISZNUMGRID property
        
        Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [2.0, 100.0]
        
        Note: both 'axisznumgrid' and 'AXISZNUMGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZNUMGRID)
        _value = cast(float, value)
        return _value

    @axisznumgrid.setter
    def axisznumgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZNUMGRID, value)

    @property
    def AXISZSGRIDTYPE(self) -> int:
        """AXISZSGRIDTYPE property
        
        Sub Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @AXISZSGRIDTYPE.setter
    def AXISZSGRIDTYPE(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZSGRIDTYPE, value)

    @property
    def axiszsgridtype(self) -> int:
        """AXISZSGRIDTYPE property
        
        Sub Grid type (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.XY_GRID_NONE - none
            * ensight.objs.enums.XY_GRID_GRID - grid
            * ensight.objs.enums.XY_GRID_TICK - tick
        
        Note: both 'axiszsgridtype' and 'AXISZSGRIDTYPE' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZSGRIDTYPE)
        _value = cast(int, value)
        return _value

    @axiszsgridtype.setter
    def axiszsgridtype(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZSGRIDTYPE, value)

    @property
    def AXISZSUBTICK(self) -> int:
        """AXISZSUBTICK property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZSUBTICK)
        _value = cast(int, value)
        return _value

    @AXISZSUBTICK.setter
    def AXISZSUBTICK(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZSUBTICK, value)

    @property
    def axiszsubtick(self) -> int:
        """AXISZSUBTICK property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'axiszsubtick' and 'AXISZSUBTICK' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZSUBTICK)
        _value = cast(int, value)
        return _value

    @axiszsubtick.setter
    def axiszsubtick(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZSUBTICK, value)

    @property
    def AXISZNUMSUBGRID(self) -> float:
        """AXISZNUMSUBGRID property
        
        Sub Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @AXISZNUMSUBGRID.setter
    def AXISZNUMSUBGRID(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZNUMSUBGRID, value)

    @property
    def axisznumsubgrid(self) -> float:
        """AXISZNUMSUBGRID property
        
        Sub Grid count
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, scalar
        Range:
            [1.0, 100.0]
        
        Note: both 'axisznumsubgrid' and 'AXISZNUMSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZNUMSUBGRID)
        _value = cast(float, value)
        return _value

    @axisznumsubgrid.setter
    def axisznumsubgrid(self, value: float) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZNUMSUBGRID, value)

    @property
    def AXISZGRIDEXTENTLOC(self) -> int:
        """AXISZGRIDEXTENTLOC property
        
        Grid/SubGrid extent loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZGRIDEXTENTLOC)
        _value = cast(int, value)
        return _value

    @AXISZGRIDEXTENTLOC.setter
    def AXISZGRIDEXTENTLOC(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZGRIDEXTENTLOC, value)

    @property
    def axiszgridextentloc(self) -> int:
        """AXISZGRIDEXTENTLOC property
        
        Grid/SubGrid extent loc (DEPRECATED, not used)
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINIMUM - min
            * ensight.objs.enums.STAGE_SHOW_STUFF_MAXIMUM - max
            * ensight.objs.enums.STAGE_SHOW_STUFF_MINANDMAX - both
        
        Note: both 'axiszgridextentloc' and 'AXISZGRIDEXTENTLOC' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.AXISZGRIDEXTENTLOC)
        _value = cast(int, value)
        return _value

    @axiszgridextentloc.setter
    def axiszgridextentloc(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.AXISZGRIDEXTENTLOC, value)

    @property
    def FACEXMINGRID(self) -> int:
        """FACEXMINGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMINGRID)
        _value = cast(int, value)
        return _value

    @FACEXMINGRID.setter
    def FACEXMINGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMINGRID, value)

    @property
    def facexmingrid(self) -> int:
        """FACEXMINGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facexmingrid' and 'FACEXMINGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMINGRID)
        _value = cast(int, value)
        return _value

    @facexmingrid.setter
    def facexmingrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMINGRID, value)

    @property
    def FACEXMINSUBGRID(self) -> int:
        """FACEXMINSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMINSUBGRID)
        _value = cast(int, value)
        return _value

    @FACEXMINSUBGRID.setter
    def FACEXMINSUBGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMINSUBGRID, value)

    @property
    def facexminsubgrid(self) -> int:
        """FACEXMINSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facexminsubgrid' and 'FACEXMINSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMINSUBGRID)
        _value = cast(int, value)
        return _value

    @facexminsubgrid.setter
    def facexminsubgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMINSUBGRID, value)

    @property
    def FACEYMINGRID(self) -> int:
        """FACEYMINGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMINGRID)
        _value = cast(int, value)
        return _value

    @FACEYMINGRID.setter
    def FACEYMINGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMINGRID, value)

    @property
    def faceymingrid(self) -> int:
        """FACEYMINGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'faceymingrid' and 'FACEYMINGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMINGRID)
        _value = cast(int, value)
        return _value

    @faceymingrid.setter
    def faceymingrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMINGRID, value)

    @property
    def FACEYMINSUBGRID(self) -> int:
        """FACEYMINSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMINSUBGRID)
        _value = cast(int, value)
        return _value

    @FACEYMINSUBGRID.setter
    def FACEYMINSUBGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMINSUBGRID, value)

    @property
    def faceyminsubgrid(self) -> int:
        """FACEYMINSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'faceyminsubgrid' and 'FACEYMINSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMINSUBGRID)
        _value = cast(int, value)
        return _value

    @faceyminsubgrid.setter
    def faceyminsubgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMINSUBGRID, value)

    @property
    def FACEYMINGRIDFILTER(self) -> int:
        """FACEYMINGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMINGRIDFILTER)
        _value = cast(int, value)
        return _value

    @FACEYMINGRIDFILTER.setter
    def FACEYMINGRIDFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMINGRIDFILTER, value)

    @property
    def faceymingridfilter(self) -> int:
        """FACEYMINGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'faceymingridfilter' and 'FACEYMINGRIDFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMINGRIDFILTER)
        _value = cast(int, value)
        return _value

    @faceymingridfilter.setter
    def faceymingridfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMINGRIDFILTER, value)

    @property
    def FACEZMINGRID(self) -> int:
        """FACEZMINGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMINGRID)
        _value = cast(int, value)
        return _value

    @FACEZMINGRID.setter
    def FACEZMINGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMINGRID, value)

    @property
    def facezmingrid(self) -> int:
        """FACEZMINGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facezmingrid' and 'FACEZMINGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMINGRID)
        _value = cast(int, value)
        return _value

    @facezmingrid.setter
    def facezmingrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMINGRID, value)

    @property
    def FACEZMINSUBGRID(self) -> int:
        """FACEZMINSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMINSUBGRID)
        _value = cast(int, value)
        return _value

    @FACEZMINSUBGRID.setter
    def FACEZMINSUBGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMINSUBGRID, value)

    @property
    def facezminsubgrid(self) -> int:
        """FACEZMINSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facezminsubgrid' and 'FACEZMINSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMINSUBGRID)
        _value = cast(int, value)
        return _value

    @facezminsubgrid.setter
    def facezminsubgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMINSUBGRID, value)

    @property
    def FACEZMINGRIDFILTER(self) -> int:
        """FACEZMINGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMINGRIDFILTER)
        _value = cast(int, value)
        return _value

    @FACEZMINGRIDFILTER.setter
    def FACEZMINGRIDFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMINGRIDFILTER, value)

    @property
    def facezmingridfilter(self) -> int:
        """FACEZMINGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'facezmingridfilter' and 'FACEZMINGRIDFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMINGRIDFILTER)
        _value = cast(int, value)
        return _value

    @facezmingridfilter.setter
    def facezmingridfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMINGRIDFILTER, value)

    @property
    def FACEXMINGRIDFILTER(self) -> int:
        """FACEXMINGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMINGRIDFILTER)
        _value = cast(int, value)
        return _value

    @FACEXMINGRIDFILTER.setter
    def FACEXMINGRIDFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMINGRIDFILTER, value)

    @property
    def facexmingridfilter(self) -> int:
        """FACEXMINGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'facexmingridfilter' and 'FACEXMINGRIDFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMINGRIDFILTER)
        _value = cast(int, value)
        return _value

    @facexmingridfilter.setter
    def facexmingridfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMINGRIDFILTER, value)

    @property
    def FACEZMAXGRID(self) -> int:
        """FACEZMAXGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMAXGRID)
        _value = cast(int, value)
        return _value

    @FACEZMAXGRID.setter
    def FACEZMAXGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMAXGRID, value)

    @property
    def facezmaxgrid(self) -> int:
        """FACEZMAXGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facezmaxgrid' and 'FACEZMAXGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMAXGRID)
        _value = cast(int, value)
        return _value

    @facezmaxgrid.setter
    def facezmaxgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMAXGRID, value)

    @property
    def FACEZMAXGRIDFILTER(self) -> int:
        """FACEZMAXGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMAXGRIDFILTER)
        _value = cast(int, value)
        return _value

    @FACEZMAXGRIDFILTER.setter
    def FACEZMAXGRIDFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMAXGRIDFILTER, value)

    @property
    def facezmaxgridfilter(self) -> int:
        """FACEZMAXGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'facezmaxgridfilter' and 'FACEZMAXGRIDFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMAXGRIDFILTER)
        _value = cast(int, value)
        return _value

    @facezmaxgridfilter.setter
    def facezmaxgridfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMAXGRIDFILTER, value)

    @property
    def FACEYMAXGRID(self) -> int:
        """FACEYMAXGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMAXGRID)
        _value = cast(int, value)
        return _value

    @FACEYMAXGRID.setter
    def FACEYMAXGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMAXGRID, value)

    @property
    def faceymaxgrid(self) -> int:
        """FACEYMAXGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'faceymaxgrid' and 'FACEYMAXGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMAXGRID)
        _value = cast(int, value)
        return _value

    @faceymaxgrid.setter
    def faceymaxgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMAXGRID, value)

    @property
    def FACEYMAXSUBGRID(self) -> int:
        """FACEYMAXSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMAXSUBGRID)
        _value = cast(int, value)
        return _value

    @FACEYMAXSUBGRID.setter
    def FACEYMAXSUBGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMAXSUBGRID, value)

    @property
    def faceymaxsubgrid(self) -> int:
        """FACEYMAXSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'faceymaxsubgrid' and 'FACEYMAXSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMAXSUBGRID)
        _value = cast(int, value)
        return _value

    @faceymaxsubgrid.setter
    def faceymaxsubgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMAXSUBGRID, value)

    @property
    def FACEXMAXGRID(self) -> int:
        """FACEXMAXGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMAXGRID)
        _value = cast(int, value)
        return _value

    @FACEXMAXGRID.setter
    def FACEXMAXGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMAXGRID, value)

    @property
    def facexmaxgrid(self) -> int:
        """FACEXMAXGRID property
        
        Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facexmaxgrid' and 'FACEXMAXGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMAXGRID)
        _value = cast(int, value)
        return _value

    @facexmaxgrid.setter
    def facexmaxgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMAXGRID, value)

    @property
    def FACEYMAXGRIDFILTER(self) -> int:
        """FACEYMAXGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMAXGRIDFILTER)
        _value = cast(int, value)
        return _value

    @FACEYMAXGRIDFILTER.setter
    def FACEYMAXGRIDFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMAXGRIDFILTER, value)

    @property
    def faceymaxgridfilter(self) -> int:
        """FACEYMAXGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'faceymaxgridfilter' and 'FACEYMAXGRIDFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEYMAXGRIDFILTER)
        _value = cast(int, value)
        return _value

    @faceymaxgridfilter.setter
    def faceymaxgridfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEYMAXGRIDFILTER, value)

    @property
    def FACEZMAXSUBGRID(self) -> int:
        """FACEZMAXSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMAXSUBGRID)
        _value = cast(int, value)
        return _value

    @FACEZMAXSUBGRID.setter
    def FACEZMAXSUBGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMAXSUBGRID, value)

    @property
    def facezmaxsubgrid(self) -> int:
        """FACEZMAXSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facezmaxsubgrid' and 'FACEZMAXSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEZMAXSUBGRID)
        _value = cast(int, value)
        return _value

    @facezmaxsubgrid.setter
    def facezmaxsubgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEZMAXSUBGRID, value)

    @property
    def FACEXMAXSUBGRID(self) -> int:
        """FACEXMAXSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMAXSUBGRID)
        _value = cast(int, value)
        return _value

    @FACEXMAXSUBGRID.setter
    def FACEXMAXSUBGRID(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMAXSUBGRID, value)

    @property
    def facexmaxsubgrid(self) -> int:
        """FACEXMAXSUBGRID property
        
        Sub Grid/Tick show
        
        Supported operations:
            getattr, setattr
        Datatype:
            Boolean, scalar
        
        Note: both 'facexmaxsubgrid' and 'FACEXMAXSUBGRID' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMAXSUBGRID)
        _value = cast(int, value)
        return _value

    @facexmaxsubgrid.setter
    def facexmaxsubgrid(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMAXSUBGRID, value)

    @property
    def FACEXMAXGRIDFILTER(self) -> int:
        """FACEXMAXGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMAXGRIDFILTER)
        _value = cast(int, value)
        return _value

    @FACEXMAXGRIDFILTER.setter
    def FACEXMAXGRIDFILTER(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMAXGRIDFILTER, value)

    @property
    def facexmaxgridfilter(self) -> int:
        """FACEXMAXGRIDFILTER property
        
        Face filter
        
        Supported operations:
            getattr, setattr
        Datatype:
            Enum, scalar
        Enums:
            * ensight.objs.enums.STAGE_LABEL_BACK_FACES - facing_back
            * ensight.objs.enums.STAGE_LABEL_FRONT_FACES - facing_front
            * ensight.objs.enums.STAGE_LABEL_FRONT_AND_BACK_FACES - off
        
        Note: both 'facexmaxgridfilter' and 'FACEXMAXGRIDFILTER' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.FACEXMAXGRIDFILTER)
        _value = cast(int, value)
        return _value

    @facexmaxgridfilter.setter
    def facexmaxgridfilter(self, value: int) -> None:
        self.setattr(self._session.ensight.objs.enums.FACEXMAXGRIDFILTER, value)

    @property
    def CORETRANSFORM(self) -> List[float]:
        """CORETRANSFORM property
        
        core transform details
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 54 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CORETRANSFORM)
        _value = cast(List[float], value)
        return _value

    @CORETRANSFORM.setter
    def CORETRANSFORM(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CORETRANSFORM, value)

    @property
    def coretransform(self) -> List[float]:
        """CORETRANSFORM property
        
        core transform details
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 54 element array
        
        Note: both 'coretransform' and 'CORETRANSFORM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CORETRANSFORM)
        _value = cast(List[float], value)
        return _value

    @coretransform.setter
    def coretransform(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CORETRANSFORM, value)

    @property
    def CORE2DTRANSFORM(self) -> List[float]:
        """CORE2DTRANSFORM property
        
        core 2D viewport transform details
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 26 element array
        
        """
        value = self.getattr(self._session.ensight.objs.enums.CORE2DTRANSFORM)
        _value = cast(List[float], value)
        return _value

    @CORE2DTRANSFORM.setter
    def CORE2DTRANSFORM(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CORE2DTRANSFORM, value)

    @property
    def core2dtransform(self) -> List[float]:
        """CORE2DTRANSFORM property
        
        core 2D viewport transform details
        
        Supported operations:
            getattr, setattr
        Datatype:
            Float, 26 element array
        
        Note: both 'core2dtransform' and 'CORE2DTRANSFORM' property names are supported.
        """
        value = self.getattr(self._session.ensight.objs.enums.CORE2DTRANSFORM)
        _value = cast(List[float], value)
        return _value

    @core2dtransform.setter
    def core2dtransform(self, value: List[float]) -> None:
        self.setattr(self._session.ensight.objs.enums.CORE2DTRANSFORM, value)

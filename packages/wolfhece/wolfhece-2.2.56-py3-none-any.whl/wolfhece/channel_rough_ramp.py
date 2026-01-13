"""
Author: HECE - University of Liege, Pierre Archambeau
Date: 2024

Copyright (c) 2024 University of Liege. All rights reserved.

This script and its content are protected by copyright law. Unauthorized
copying or distribution of this file, via any medium, is strictly prohibited.
"""

import logging

import numpy as np
from shapely.geometry import Point, LineString
from dataclasses import dataclass

from.drawing_obj import Element_To_Draw
from .PyVertexvectors import Triangulation, vector,Zones, zone, wolfvertex as wv
from .wolf_array import WolfArray, header_wolf
from .synthetic_dike import SyntheticDike

@dataclass
class BreachElement:
    """ Class representing a breach element with its properties.
    """
    curvilinear_position:float
    width:float
    depth:float

class Channel(SyntheticDike):
    """ Channel class based on a trace vector, width of the sides (left and right) and lateral slopes.
    """

    def __init__(self, idx:str = '', plotted:bool = True, mapviewer = None, need_for_wx:bool = False):

        super().__init__(idx, plotted, mapviewer, need_for_wx)

        self._triangulation = None
        self._zones = Zones()
        newzone = zone(name='channel')

        self._zones.add_zone(newzone, forceparent=True)

        self._ds = 1.0

    def create_from_slopes(self, trace:vector,
                             slope_left:float, slope_right:float,
                             width_left:float, width_right:float,
                             zmin:float, zmax:float, ds:float):

        """ Create the rough ramp triangulation based on the trace vector and the width of the dike.

        :param trace: Trace vector of the dike
        :param slope_left: Slope of the dike on the left side [slope = dz/dx]
        :param slope_right: Slope of the dike on the right side [slope = dz/dx]
        :param width_left: Width of the dike on the left side [m]
        :param width_right: Width of the dike on the right side [m]
        :param zmin: Minimum elevation of the dike [m]
        :param zmax: Maximum elevation of the dike [m]
        :param ds: Distance for rebinning [m]
        """

        assert ds > 0.0, "Distance for rebinning must be positive"
        assert slope_left > 0.0, "Slope must be positive"
        assert slope_right > 0.0, "Slope must be positive"
        assert width_left >= 0.0, "Width must be positive"
        assert width_right >= 0.0, "Width must be positive"
        assert zmin < zmax, "zmin must be less than zmax"

        self._ds = ds
        myzone = self._zones.myzones[0]
        myzone.myvectors = []

        # Impose altimetry of the crest
        trace.z = zmin

        # add the trace vector to the zone
        myzone.add_vector(trace, forceparent=True)

        # LATERAL SIDES
        # create parallel vectors to the trace vector - right and left

        if width_left > 0.0:
            distances_left = list(np.linspace(0, width_left, int(width_left/ds)+1, endpoint=True))[1:]
            for curds in distances_left:
                # create a new vector parallel to the trace vector
                parleft = trace.parallel_offset(curds, 'left')
                myzone.add_vector(parleft, 0, forceparent=True)
                # impose altimetry of the dike
                parleft.z = zmin
        else:
            # no width on the upstream side -> use the trace vector
            parleft = trace

        if width_right > 0.0:
            distances_right = list(np.linspace(0, width_right, int(width_right/ds)+1, endpoint=True))[1:]
            for curds in distances_right:
                parright = trace.parallel_offset(curds, 'right')
                myzone.add_vector(parright, forceparent=True)
                # impose altimetry of the dike
                parright.z = zmin
        else:
            # no width on the downstream side -> use the trace vector
            parright = trace

        # distances to the crest
        distances_left   = (zmax-zmin) / slope_left
        distances_left = list(np.linspace(0, distances_left, int(distances_left/ds)+1, endpoint=True))[1:]
        # distances_left.reverse()
        # iterate over the distleft basd on ds
        for curds in distances_left:
            # create a new vector parallel to the trace vector
            parup_new = parleft.parallel_offset(curds, 'left')
            myzone.add_vector(parup_new, 0, forceparent=True)
            # impose altimetry of the dike
            parup_new.z = zmin + slope_left * curds

        distances_right = (zmax-zmin) / slope_right
        distances_right = list(np.linspace(0, distances_right, int(distances_right/ds)+1, endpoint=True))[1:]
        for curds in distances_right:
            pardown_new  = parright.parallel_offset(curds, 'right')
            myzone.add_vector(pardown_new, forceparent=True) # append
            # impose altimetry of the dike
            pardown_new.z = zmin + slope_right * curds

        # on dispose de multiples vecteurs dans la zone, orientés de l'amont vers l'aval
        trace.update_lengths()

        nb_along_trace  = int(trace.length3D / ds) # nombre de points sur la trace

        self._triangulation = myzone.create_multibin(nb_along_trace)

    def create_from_shape(self, trace:vector, shape:vector, ds:float):
        """ create the rough ramp triangulation based on the trace vector and the shape vector

        :param trace: Trace vector of the dike
        :param shape: Transversal shape of the dike in (s,z) coordinates, s=0.0 is on the trace vector, elevations are relative to the trace vector
        :param ds: Distance for rebinning [m]
        """

        self._ds = ds
        super().create_from_shape(trace, shape, ds)


class RoughRamp(Channel):
    """ Rough ramp class based on a trace vector, width of the sides (left and right) and lateral slopes.
    """
    _rough_elements:list[SyntheticDike]
    _breach_elements:list["RoughRamp"]

    def __init__(self, idx:str = '', plotted:bool = True, mapviewer = None, need_for_wx:bool = False):

        super().__init__(idx, plotted, mapviewer, need_for_wx)

        self._triangulation = None
        self._zones = Zones()
        newzone = zone(name='roughramp')

        self._zones.add_zone(newzone, forceparent=True)

        self._rough_elements= []
        self._breach_elements = []

        self._ds = 1.0

    def _add_rough_element(self, shape_horiz:vector, shape_cs:vector,
                           ds:float | None = None,
                           rotation_angle:float = 0.0, translation_vertex:vector = None):
        """ Add rough element

        :param shape_horiz: Horizontal shape of rough elements (optional)
        :param shape_cs: Cross-sectional shape of rough elements (optional)
        :param ds: Distance for rebinning (optional)
        """

        if ds is None:
            ds = self._ds

        elem = SyntheticDike()
        elem.create_from_shape(shape_horiz, shape_cs, ds)

        z_shape_trace = shape_cs.y[shape_cs.x == 0.0][0]
        translation_vertex.z += z_shape_trace

        elem.rotation_angle = rotation_angle
        if translation_vertex is not None:
            elem.translation_vertex = translation_vertex

        self._rough_elements.append(elem)

    def _add_breach_element(self, breach: BreachElement, middle:wv, orientation:wv, length: float):
        """ Create a "dike" representing a breach element and add it to the list.

        :param breach: BreachElement object containing breach properties
        :param middle: Middle point of the breach element
        :param orientation: Orientation vector of the breach element
        :param length: Length of the breach element along the orientation [m]
        """

        trace = vector(name= 'breach_trace')
        trace.add_vertex(wv(- orientation.x * length / 2,
                         - orientation.y * length / 2,
                         -breach.depth))
        trace.add_vertex(wv(orientation.x * length / 2,
                         orientation.y * length / 2,
                         -breach.depth))

        new_breach = RoughRamp()
        new_breach.create_from_slopes(trace,
                                      slope_left=10.0,
                                      slope_right=10.0,
                                      width_left=breach.width / 2,
                                      width_right=breach.width / 2,
                                      zmin=-breach.depth,
                                      zmax=0.0,
                                      ds=self._ds)

        new_breach.translation_vertex = middle

        self._breach_elements.append(new_breach)

    def add_rough_elements_along_trace(self,
                                     shape_horiz:vector = None,
                                     shape_cs:vector = None,
                                     spacing:float = 10.0,
                                     reset:bool = True,
                                     ds:float | None = None,
                                     breach: BreachElement = None,
                                     decal_each:float = 1.0
                                     ):
        """ Add rough elements along the dike trace

        :param shape_horiz: Horizontal shape of rough elements (optional)
        :param shape_cs: Cross-sectional shape of rough elements (optional)
        :param spacing: Spacing between rough elements along the trace [m]
        :param reset: If True, reset existing rough elements before adding new ones
        :param ds: Distance for rebinning (optional)
        :param breach: BreachElement object containing breach properties (optional)
        :param decal_each: Lateral offset for breach elements to alternate sides [m]
        """

        assert spacing > 0.0, "Spacing must be positive"

        if ds is None:
            ds = self._ds

        if reset:
            self._rough_elements = []
            self._breach_elements = []

        if self.trace.length3D is None:
            self.trace.update_lengths()

        nb_elems = int(self.trace.length3D / spacing) + 1
        spacings = list(np.linspace(0, self.trace.length3D, nb_elems, endpoint=True))

        if breach is not None:
            ref_s = breach.curvilinear_position

        for idx, curds in enumerate(spacings):
            point_on_trace = self.trace.interpolate(curds, adim=False)
            normal = self.trace.normal_at_s(curds, adim=False, counterclockwise=False)
            angle = np.arctan2(normal.y, normal.x)

            # make a copy of the horizontal shape
            shape_horiz_copy = shape_horiz.deepcopy()
            # Set altimetry of the horizontal shape to zero
            shape_horiz_copy.z = 0.0

            # create a new rough element
            self._add_rough_element(shape_horiz_copy,
                                    shape_cs.deepcopy(),
                                    ds=ds,
                                    rotation_angle= np.rad2deg(angle),
                                    translation_vertex=point_on_trace)

            if breach is not None:
                delta = (shape_horiz.y.max() - shape_horiz.y.min()) * 1.5

                # insert a breach in the horizontal shape
                decal_loc = -decal_each/2. + decal_each * (idx % 2)  # alternate left and right
                breach.curvilinear_position = ref_s + decal_loc + breach.width / 2
                point_on_rough = shape_horiz_copy.interpolate(breach.curvilinear_position, adim=False)

                tangent = self.trace.tangent_at_s(curds, adim=False)
                self._add_breach_element(breach,
                                         middle=point_on_rough + point_on_trace,
                                         orientation=tangent,
                                         length=max(spacing / 1.5, delta))

    @property
    def triangulations_above(self) -> list[Triangulation]:
        """ List of triangulations of the rough elements

        :return: List of triangulations
        """

        return [self._triangulation] + [elem.triangulation for elem in self._rough_elements]

    @property
    def triangulations_rough(self) -> list[Triangulation]:
        """ List of triangulations of the rough elements

        :return: List of triangulations
        """

        return [elem.triangulation for elem in self._rough_elements]

    @property
    def triangulations_below(self) -> list[Triangulation]:
        """ List of triangulations of the breach elements

        :return: List of triangulations
        """

        return [elem.triangulation for elem in self._breach_elements]

    @property
    def triangulations(self) -> tuple[list[Triangulation], list[str]]:
        """ List of all triangulations

        :return: List of triangulations
        """

        return self.triangulations_above + self.triangulations_below, ['above'] * (1 + len(self._rough_elements)) + ['below'] * len(self._breach_elements)

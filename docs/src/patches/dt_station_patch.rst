DTStationPatch
===============

The ``DTStationPatch`` class provides visualization capabilities for DT Station. It can draw station and super layer
boundary boxes, and DT cells based on geometrical information taken from :doc:`Station <../geometry/station>` instances.

The class itself is not a matplotlib artist, but it creates a couple of matplotlib patch collections 
to draw the station bounds and cells and that can be accessed as attributes of the ``DTStationPatch`` instance. 
It adds to the provided matplotlib axes the following artists:

- ``bounds_collections``: A collection of patches representing the bounds of the station and its superlayers.
- ``cells_collection``: A collection of patches representing each DT cell, with optional colormap based on time information.

Since station and super layers bounds are a patch collection independent of the cells collection, any supported matplotlib
rc parameters can be passed to customize the appearance of the bounds. The same applies to the cells collection, specially
the patch array that allows to define the color map to represent any drift cell properties passed through
the ``dt_info`` argument of the ``Station`` class.

The class supports plotting in both **local** and **global** DT CMS coordinate views. And it is possible 
to draw the chamber in either the :math:`\phi` or :math:`\eta` orientation, displaying
the cells of ``SL1`` and ``SL3`` or the cells of ``SL2``, respectively.

.. tip::

    ``bounds_collections`` has the matplotlib property ``set_picker`` enabled, and the ``Station`` 
    instance stored as the ``station`` attribute. This allows for the creation of interactive plots
    with the matplotlib ``pick_event``. 

.. autoclass:: mpldts.patches.dt_station_patch.DTStationPatch
    :show-inheritance:
    :members:
    :special-members: __init__
    :private-members: _draw_bounds, _draw_cells, _create_frame
    :inherited-members:

Examples
--------

The following example shows how to create ``DTStationPatch`` objects and plot the cells of a DT chamber in the local view.

.. literalinclude:: ../../../test/cms_dt_local_wb.py
    :language: python
    :lines: 1-57
    :linenos:


.. image:: ../../_static/img/cms_dt_local_wb.svg
    :alt: Alternative text
    :class: image-class
    :width: 800px
    :align: center
    :name: cms_dt_local_wb


Setting the ``bounds_kwargs`` and ``cells_kwargs`` arguments allows for customization of the
appearance of the bounds and cells, respectively. And as mentioned before, the ``dt_info`` argument
passed to the ``Station`` instance can be used to define a colormap based on any drift cell property as 
shown in the following example.

.. literalinclude:: ../../../test/cms_dt_local_c.py
    :language: python
    :lines: 1-74
    :emphasize-lines: 4, 9-11, 17-18, 21-44, 51, 56, 60, 64 
    :linenos:


.. image:: ../../_static/img/cms_dt_local_c.svg
    :alt: Alternative text
    :class: image-class
    :width: 800px
    :align: center

Since each ``DTStationPatch`` object is an isolated instance, it is possible to plot multiple chambers in 
the same axes and use the global mode to utilize the exact CMS coordinate system to visualize part 
or the whole DT system.

.. literalinclude:: ../../../test/cms_dts_phi_zoomed.py
    :language: python
    :lines: 1-73
    :linenos:

.. image:: ../../_static/img/cms_dts_phi_zoomed.svg
    :alt: Alternative text
    :class: image-class
    :width: 1200px
    :align: center

And also in :math:`\eta` orientation, that means the longitudinal CMS view:

.. literalinclude:: ../../../test/cms_dts_eta_zoomed.py
    :language: python
    :lines: 1-71
    :linenos:
    

.. image:: ../../_static/img/cms_dts_eta_zoomed.svg
    :alt: Alternative text
    :class: image-class
    :width: 800px
    :align: center


As you can notice from the first :ref:`example <cms_dt_local_wb>`, the chamber appears in the local reference frame
resulting in an unnaturally rotated view. But, by using the ``invert_view`` method inherited from :doc:`DTRelatedPatch <dt_patch_base>` class,
(or setting the ``invert`` argument ``True`` when instantiating the ``DTStationPatch`` class) you can easily
invert the view by applying reflections to the chamber view according to wheel, station and faceview (:math:`\phi` or :math:`\eta`)
and the result is a more natural view of the chamber as illustrated in the follow illustration.

.. image:: ../../_static/img/mpldts_view_frames.png 
    :alt: Alternative text
    :class: image-class
    :width: 800px
    :align: center

inversion (1) or (2) will depend on DT chamber's orientation, that means, 
if detector face is in :math:`+z` or :math:`-z` direction, detailed information can be found `here. <https://dt-sx5.web.cern.ch/dt-sx5/run/docs/050912DT_type_naming.pdf>`_

The following example shows how to do this:

.. literalinclude:: ../../../test/cms_dt_local_inversion.py
    :language: python
    :lines: 1-118
    :linenos:

.. image:: ../../_static/img/cms_dt_local_inversion.svg
    :alt: Alternative text
    :class: image-class
    :width: 800px
    :align: center
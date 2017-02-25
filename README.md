# LabRAD-sweeper-2
LabRAD sweeper rework. This version is to separate the functionality and the user interface; these modules are separated here.

Sweeper code: standalone functionality for performing sweeps through LabRAD
* sweeper.py - the main functionality of the sweeper
* components - some of the other sweep functionality is stored here.
  * logger.py
  * settings.py
  * sweep_mesh.py

User interface: raw PyQt4 layout, widgets, components
* qtdesigner
  * make_ui.bat - compiles the .ui files into their .py counterparts.
  * setup.py, setup.ui - the main user interface file for setup mode
  * other setup components (setup_axis_bar,setup_rec_bar,setup_swp_bar)

Connecting code: Connects the components of the user interface to the functionality of the sweeper
* run_ui.py - connects UI to sweeper

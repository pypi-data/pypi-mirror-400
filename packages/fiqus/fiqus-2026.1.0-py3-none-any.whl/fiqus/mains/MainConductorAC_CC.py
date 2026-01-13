
"""MainConductorAC_CC.py:"""

import os
import sys

from fiqus.geom_generators.GeometryConductorAC_CC import Generate_geometry
from fiqus.mesh_generators.MeshConductorAC_CC import Mesh
from fiqus.getdp_runners.RunGetdpConductorAC_CC import Solve
from fiqus.post_processors.PostProcessAC_CC import Post_Process

if len(sys.argv) == 3:
    sys.path.insert(0, os.path.join(os.getcwd(), 'steam-fiqus-dev'))
from fiqus.data.DataFiQuS import FDM

class MainConductorAC_CC:
    def __init__(self, fdm, inputs_folder_path='', verbose=True):
        """
        Main class for working with simulations for CAC_CC type magnets
        :param fdm: FiQuS data model
        :type fdm: FDM
        :param inputs_folder_path: full path to folder with input files, i.e. conductor and STEP files
        :type inputs_folder_path: str
        :param verbose: if True, more info is printed in the console
        :type verbose: bool
        :return: nothing, only saves files on disk
        :rtype: none
        """
        self.verbose = verbose
        self.fdm = fdm
        self.inputs_folder_path = inputs_folder_path
        self.GetDP_path = None
        self.geom_folder = None
        self.mesh_folder = None
        self.solution_folder = None
        self.model_file = None
        self.model_folder = None

    def generate_geometry(self, gui=False):
        """
        Main method for loading the geometry of CAC_CC models
        :param gui: if true, graphical user interface (gui) of Gmsh is opened at the end
        :type gui: bool
        :return: nothing, only saves files on disk
        :rtype: none
        """
        os.chdir(self.geom_folder)
        gg = Generate_geometry(fdm=self.fdm, inputs_folder_path=self.inputs_folder_path, verbose=self.verbose)
        gg.generate_HTS_layer()        
        gg.generate_silver_top_layer()              
        gg.generate_substrate_layer()        
        gg.generate_copper_top_layer()
        gg.generate_silver_bottom_layer()        
        gg.generate_copper_bottom_layer()
        gg.generate_copper_left_layer()
        gg.generate_copper_right_layer()        
        gg.generate_air_region()
        gg.finalize_and_write()

    def load_geometry(self, gui=False):
        """
        Main method for loading the geometry of CAC_CC models
        """
        os.chdir(self.geom_folder)
        gg = Generate_geometry(fdm=self.fdm, inputs_folder_path=self.inputs_folder_path, verbose=self.verbose)
        self.geometry = gg
        gg.load_geometry(gui=gui)

    def pre_process(self, gui=False):
        """
        Main method for preprocessing of CAC_CC models
        :param gui: if true, graphical user interface (gui) of Gmsh is opened at the end
        :type gui: bool
        :return: nothing, only saves files on disk
        :rtype: none
        """
        os.chdir(self.geom_folder)


    def mesh(self, gui=False):
        """
        Main method for building the mesh of CAC_CC models
        :param gui: if true, graphical user interface (gui) of Gmsh is opened at the end
        :type gui: bool
        :return: dictionary with mesh quality stats
        :rtype: dict
        """
        os.chdir(self.mesh_folder)
        m = Mesh(self.fdm)
        m.generate_mesh(self.geom_folder)
        return {"gamma": 0}


    def load_mesh(self, gui=False):
        """
        Main method for loading the mesh of CAC_CC models
        :param gui: if true, graphical user interface (gui) of Gmsh is opened at the end
        :type gui: bool
        :return: Nothing, only saves files on disk
        :rtype: none
        """
        os.chdir(self.mesh_folder)

    def solve_and_postprocess_getdp(self, gui: bool = False):
        """
        Assembles the .pro-file from the template, then runs the simulation and the post-processing steps using GetDP.
        """
        os.chdir(self.solution_folder)

        s = Solve(self.fdm, self.GetDP_path, self.geom_folder, self.mesh_folder, self.verbose)
        s.read_excitation(inputs_folder_path=self.inputs_folder_path)
        s.assemble_pro()
        s.run_getdp(solve = True, postOperation = True, gui = gui)
    
    def post_process_getdp(self, gui: bool = False):
        """ 
        Runs the post-processing steps trough GetDP.
        """
        os.chdir(self.solution_folder)

        s = Solve(self.fdm, self.GetDP_path, self.geom_folder, self.mesh_folder, self.verbose)
        s.read_excitation(inputs_folder_path=self.inputs_folder_path)
        s.assemble_pro()
        s.run_getdp(solve = False, postOperation = True, gui = gui)

    def post_process_python(self, gui=False):
        """
        Main method for postprocessing using python (without solving) of CAC_CC models
        :param gui: if true, graphical user interface (gui) of Gmsh is opened at the end
        :type gui: bool
        :return: Nothing, only saves files on disk
        :rtype: none
        """
        os.chdir(self.solution_folder)
        p=Post_Process(self.fdm, verbose=self.verbose)
        p.cleanup()
        return {'overall_error': 0}

    def plot_python(self, gui=False):
        """
        Main method for making python plots related to CAC_CC models
        :param gui: if true, graphical user interface (gui) of Gmsh is opened at the end
        :type gui: bool
        :return: Nothing, only saves files on disk
        :rtype: none
        """
        os.chdir(self.solution_folder)


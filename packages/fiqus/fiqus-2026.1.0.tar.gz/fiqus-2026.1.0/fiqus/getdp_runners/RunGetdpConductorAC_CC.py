import timeit
import logging
from enum import Enum
import os
import subprocess
import re
import pandas as pd

import gmsh
import numpy as np

#from fiqus.data import RegionsModelFiQuS
from fiqus.utils.Utils import GmshUtils, FilesAndFolders
from fiqus.data.RegionsModelFiQuS import RegionsModel
# import fiqus.data.DataConductorACGeom as geom

from fiqus.pro_assemblers.ProAssembler import ASS_PRO

logger = logging.getLogger('FiQuS')

class Solve:
    def __init__(self, fdm, GetDP_path, geometry_folder, mesh_folder, verbose=True):
        self.fdm = fdm
        self.cacdm = fdm.magnet
        self.GetDP_path = GetDP_path
        self.solution_folder = os.path.join(os.getcwd())
        self.magnet_name = fdm.general.magnet_name
        self.geometry_folder = geometry_folder
        self.mesh_folder = mesh_folder
        self.mesh_file = os.path.join(self.mesh_folder, f"{self.magnet_name}.msh")
        self.pro_file = os.path.join(self.solution_folder, f"{self.magnet_name}.pro")
        self.regions_file = os.path.join(mesh_folder, f"{self.magnet_name}.regions")
        
        self.verbose = verbose
        self.gu = GmshUtils(self.solution_folder, self.verbose)
        self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

        self.ass_pro = ASS_PRO(os.path.join(self.solution_folder, self.magnet_name))
        self.regions_model = FilesAndFolders.read_data_from_yaml(self.regions_file, RegionsModel)
        self.material_properties_model = None

        self.ed = {} # excitation dictionary

        gmsh.option.setNumber("General.Terminal", verbose)

    def assemble_pro(self):
        logger.info("Assembling .pro file")
        self.ass_pro.assemble_combined_pro(template = self.cacdm.solve.pro_template, rm = self.regions_model, dm = self.fdm, ed=self.ed, mp=self.material_properties_model)

    def read_excitation(self, inputs_folder_path):
        """
        Function for reading a CSV file for the 'piecewise' excitation case.

        :param inputs_folder_path: The full path to the folder with input files.
        :type inputs_folder_path: str
        """
        if self.cacdm.solve.source_parameters.source_type == 'piecewise' and self.cacdm.solve.source_parameters.piecewise.source_csv_file:
            input_file = os.path.join(inputs_folder_path, self.cacdm.solve.source_parameters.piecewise.source_csv_file)
            logger.info(f'Using excitation from file: {input_file}')
            df = pd.read_csv(input_file, delimiter=',', engine='python')
            excitation_time = df['time'].to_numpy(dtype='float').tolist()
            self.ed['time'] = excitation_time
            excitation_b = df['b'].to_numpy(dtype='float').tolist()
            self.ed['b'] = excitation_b
            excitation_I = df['I'].to_numpy(dtype='float').tolist()
            self.ed['I'] = excitation_I

    def run_getdp(self, solve = True, postOperation = True, gui = False):
        command = ["-v2", "-verbose", "3"]
        if solve: 
            command += ["-solve", "MagDyn", "-mat_mumps_icntl_14","100"] # icntl for mumps just by precaution
        command += ["-pos", "MagDyn"]

        logger.info(f"Running GetDP with command: {command}")
        startTime = timeit.default_timer()

        if self.cacdm.solve.general_parameters.noOfMPITasks:
            mpi_prefix = ["mpiexec", "-np", str(self.cacdm.solve.general_parameters.noOfMPITasks)]
        else:
            mpi_prefix = []

        getdpProcess = subprocess.Popen(mpi_prefix + [self.GetDP_path] + [self.pro_file] + command + ["-msh"] + [self.mesh_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        with getdpProcess.stdout:
            for line in iter(getdpProcess.stdout.readline, b""):
                line = line.decode("utf-8").rstrip()
                line = line.split("\r")[-1]
                if not "Test" in line:
                    if line.startswith("Info"):
                        parsedLine = re.sub(r"Info\s+:\s+", "", line)
                        logger.info(parsedLine)
                    elif line.startswith("Warning"):
                        parsedLine = re.sub(r"Warning\s+:\s+", "", line)
                        logger.warning(parsedLine)
                    elif line.startswith("Error"):
                        parsedLine = re.sub(r"Error\s+:\s+", "", line)
                        logger.error(parsedLine)
                        logger.error("Solving CAC failed.")
                        # raise Exception(parsedLine)
                    elif re.match("##", line):
                        logger.critical(line)
                    else:
                        logger.info(line)
        
        simulation_time = timeit.default_timer()-startTime
        
        if gui and ((postOperation and not solve) or (solve and postOperation)): # and self.cacdm.postproc.generate_pos_files
            # gmsh.option.setNumber("Geometry.Volumes", 1)
            # gmsh.option.setNumber("Geometry.Surfaces", 1)
            # gmsh.option.setNumber("Geometry.Curves", 1)
            # gmsh.option.setNumber("Geometry.Points", 0)
            posFiles = [
                fileName
                for fileName in os.listdir(self.solution_folder)
                if fileName.endswith(".pos")
            ]
            for posFile in posFiles:
                gmsh.open(os.path.join(self.solution_folder, posFile))
            self.gu.launch_interactive_GUI()
        else:
            if gmsh.isInitialized():
                gmsh.clear()
                gmsh.finalize()

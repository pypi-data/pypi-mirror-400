import os
import math
import csv
import re
import logging

import gmsh
import json
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from fiqus.utils.Utils import GmshUtils
from fiqus.parsers.ParserCOND import ParserCOND
from fiqus.utils.Utils import FilesAndFolders as uff
from fiqus.data.RegionsModelFiQuS import RegionsModel

logger = logging.getLogger('FiQuS')

class Post_Process:
    """
    Postprocessing class for CWS
    """
    def __init__(self, fdm, verbose=True):
        """
        Class to cct models postprocessing
        :param fdm: FiQuS data model
        :param verbose: If True more information is printed in python console.
        """
        self.current_FiQuS = {}
        self.fdm = fdm
        self.model_folder = os.path.join(os.getcwd())

        self.mesh_folder = Path(self.model_folder).parent
        self.geom_folder = Path(self.mesh_folder).parent
        self.magnet_name = fdm.general.magnet_name
        self.verbose = verbose

    def cleanup(self):
        """
            This function is used to remove .msh, .pre and .res files from the solution folder, as they may be large and not needed.
        """
        magnet_name = self.fdm.general.magnet_name
        cleanup = self.fdm.magnet.postproc.cleanup

        if cleanup.remove_res_file:
            res_file_path = os.path.join(self.model_folder, f"{magnet_name}.res")
            if os.path.exists(res_file_path):
                os.remove(res_file_path)
                logger.info(f"Removed {magnet_name}.res")

        if cleanup.remove_pre_file:
            pre_file_path = os.path.join(self.model_folder, f"{magnet_name}.pre")
            if os.path.exists(pre_file_path):
                os.remove(pre_file_path)
                logger.info(f"Removed {magnet_name}.pre")

        if cleanup.remove_msh_file:
            msh_file_path = os.path.join(self.mesh_folder, f"{magnet_name}.msh")
            if os.path.exists(msh_file_path):
                os.remove(msh_file_path)
                logger.info(f"Removed {magnet_name}.msh")

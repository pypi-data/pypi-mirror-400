import os

from steam_sdk.parsers.ParserYAML import dict_to_yaml, dump_concrete
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class ParserFiQuS:
    """
        Class with methods to write FiQuS input files from steam sdk
    """

    def __init__(self, builder_FiQuS, verbose=True):
        """
        Initialization using a BuilderFiQuS object containing FiQuS parameter structure
        :param builder_FiQuS: BuilderFiQuS object
        :param verbose: boolean if set to true more information is printed to the screen
        """

        self.builder_FiQuS = builder_FiQuS
        self.verbose = verbose
        self.file_exts = ['yaml']

    def writeFiQuS2yaml(self, output_path: str, simulation_name=None, append_str_to_magnet_name: str = '_FiQuS'):
        """
        ** Writes FiQuS input files **

        :param output_path: full path to output folder.
        :param simulation_name: This is used in analysis steam to change yaml name from magnet name to simulation name
        :param append_str_to_magnet_name: additional string to add to magnet name, e.g. '_FiQuS'.
        :return:   Nothing, writes files to output folder.
        """
        make_folder_if_not_existing(output_path)  # If the output folder is not an empty string, and it does not exist, make it

        if simulation_name:
            file_name = f'{simulation_name}{append_str_to_magnet_name}'
        else:
            file_name = f'{self.builder_FiQuS.data_FiQuS.general.magnet_name}{append_str_to_magnet_name}'
        dict_to_yaml(dump_concrete(self.builder_FiQuS.data_FiQuS), os.path.join(output_path, f'{file_name}.yaml'), list_exceptions=[])

        if self.builder_FiQuS.data_FiQuS.magnet.type in ['multipole', 'solenoid']:
            if self.builder_FiQuS.data_FiQuS.magnet.geometry.geom_file_path:
                pass #self.attributes, self.file_exts = ['data_FiQuS', 'data_FiQuS_set'], ['yaml']
            else:
                pass
                dict_to_yaml(self.builder_FiQuS.data_FiQuS_geo.model_dump(), os.path.join(output_path, f'{file_name}.geom'), list_exceptions=[])
                self.file_exts = ['yaml', 'geom']


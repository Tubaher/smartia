import pandas as pd
import json
import os
import utils.config as config
import logging
from os.path import join
from glob import glob
import utils.utils as utils
from datetime import datetime
import shutil

def load_data(**kwargs):
    """
    This function uses a metainfo.json configuration to load
    files and store in temporal .csv according to each table information
    """

    # Loading metainfo
    metainfo = utils.load_metainfo(kwargs)

    if metainfo is not None:

        # Validation of metainfo
        utils.validate_metainfo(metainfo)

        # Define a parser to the current files format
        fileParser = utils.WrapperFileParser(metainfo)
        
        # Loading file with a especific format
        file_path = join(metainfo["ruta_archivos"],"processed")
        

        #Create the processed file if not exists
        if not os.path.exists(file_path):
            os.mkdir(file_path)

        # get the files according to what we expect: lastest file, a list of files in a folder, etc.
        files = utils.load_files_names(metainfo)

        logging.info("FILES: {}".format(files))
        
        for f in files:
            filename, filename_ext = os.path.splitext(f)

            #check the extension file
            if filename_ext == "."+metainfo["file_extension"].translate({".":""}):
                path_file = join(metainfo["ruta_archivos"], f)
                
                # Parser to df frame
                logging.info("PATH FILE: {} ".format(path_file))

                dataframes = fileParser.generate_dfs(path_file)

                error = False
                #Saving the data frames in temporals .csv
                for table_name, df in dataframes.items():
                    folder_name = metainfo["cliente"]
                    tmp_folder_dir = join(config.TMP_FILES_DIR, folder_name)
                    if not os.path.exists(tmp_folder_dir):
                        os.mkdir(tmp_folder_dir)

                    # Name of the temporal file .csv
                    output_file_name = table_name + "_"+ datetime.now().strftime('%d-%m-%Y-%H-%M') + ".csv"
                    
                    # Try to cast the columns according to each corresponding data type
                    try:
                        df.astype(config.TABLES_FIELDS[table_name]).dtypes
                    except:
                        logging.warning("The temporal df {} could not be casted to the correct datatype".format(output_file_name))
                    

                    tmp_file_dir = join(tmp_folder_dir, output_file_name)
                    
                    try:
                        df.to_csv( tmp_file_dir , index = False)
                    except:
                        error = True
                        logging.warning("The program could not save the temporal file {}".format(tmp_file_dir))
                
                # If the temporal file csv is stored the moved the already processed file
                if error == False:
                    dst = join( join(metainfo["ruta_archivos"], "processed"), f)
                    # shutil.move(src = path_file, dst = dst)
                else:
                    logging.warning("Problems saving temporal files. Then, the file {} was not moved to processed".format(f))

            else:
                logging.warning("The file {} extension does not match with metadata used extension".format(f))
import pandas as pd
import logging
import config

class FileParser:
    def __init__(self, metainfo):
        self.metainfo = metainfo

    def generate_dfs(self, path_file):        
        # Process the file according its extension
        full_df = self.file_processing(path_file)

        # Process each table from the columns of the original file
        # return a dataframe per each table
        tables_dataframes = self.__processing_tables(full_df)

        return tables_dataframes

    # def file_processing(self, path_file):
    #     #TODO: require a function to load the file into a data frame
    #     df = pd.DataFrame(path_file)

    #     return df

    def __processing_tables(self, full_df):
        """
        This function takes the full dataframe and creates sub dataframes
        per each table define in metainfo

        return: List of dataframes. On data frame per table.
        """
        
        tables_dataframes = {}

        for table_name in self.metainfo["tablas_salida"]:

            same_columns = []
            operations_columns = []
            default_columns = []
            
            for meta_column in self.metainfo[table_name]:
                # filter the columns with default values
                if meta_column.get("default") is not None:
                    default_columns.append(meta_column)

                # filter the meta columns with operations
                elif meta_column.get("operaciones") is not None:
                    operations_columns.append(meta_column)

                # filter some columns from the original
                else:
                    same_columns.append(meta_column)

            # generate a df with some filter same columns of the full_df
            table_df = self.__generate_same_columns(full_df, same_columns)

            # generate columns with default values
            self.__generate_default_columns(table_df, default_columns)

            logging.info("TABLE DF AFTER OPERATIONS : \n {} \n {}".format(table_df, table_df.dtypes))

            # generate columns from operation between columns, 
            # adding new columns to the right of the table_df
            self.__generate_operations_columns(table_df, full_df, operations_columns)

            logging.info("TABLE DF BEFORE OPERATIONS: \n {}".format(table_df))

            tables_dataframes[table_name] = table_df
            
        return tables_dataframes

    def __generate_same_columns(self, full_df, same_columns):

        #extract the names in and out from meta columns
        columns_in = [m_c["nombre_entradas"][0] for m_c in same_columns ]
        columns_out = [m_c["nombre_salida"] for m_c in same_columns ]

        #filter some colums from the full_df
        table_df = full_df[columns_in]

        # rename column names according to the output names
        dict_names = { past_name: new_name for past_name, new_name in zip(columns_in,columns_out)}
        table_df = table_df.rename(columns = dict_names)

        return table_df

    
    def __generate_default_columns(self, table_df, default_columns):
        for m_column in default_columns:
            column_name = m_column["nombre_salida"]
            default_value = m_column["default"]

            table_df[column_name] = default_value

    def __generate_operations_columns(self, table_df, full_df, operations_columns):
        """
        This function performs the operations between columns, and stores the results
        in a new column.
        """
        
        for m_column in operations_columns:

            auxiliar_operator = full_df[ m_column["nombre_entradas"][0] ]

            for idx, op in enumerate(m_column["operaciones"]):
                column1 = auxiliar_operator
                column2 = full_df[ m_column["nombre_entradas"][idx + 1] ]
                auxiliar_operator = config.OPERATIONS[op](column1, column2)
            
            table_df[m_column["nombre_salida"]] = auxiliar_operator

            # ANOTHER way to process the operations between columns            
            # str_exec = "table_df[\"{}\"] = ".format(m_column["nombre_salida"])

            # inter_layer = m_column["nombre_entradas"] + m_column["operaciones"]
            # inter_layer[::2] = m_column["nombre_entradas"]
            # inter_layer[1::2] = m_column["operaciones"]

            # for idx, value in enumerate(inter_layer):
            #     if idx % 2 == 0:
            #         str_exec += "full_df[{}]".format(value) + " "
            #     else:
            #         str_exec += str(value) + " "
                    
            
            # logging.info("STR EXEC: {}".format(str_exec))
            # exec(str_exec)
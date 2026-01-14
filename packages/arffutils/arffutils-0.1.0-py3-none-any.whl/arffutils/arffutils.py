import pandas as pd

def pandas_dataframe_to_arff(df, outputfile, relation_name="test"):
    """
    Converts a pandas DataFrame to ARFF format.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        outputfile (str): The path where the ARFF file will be written.
        relation_name (str, optional): The name of the relation. Defaults to "test".

    Returns:
        None
    """

    # Generate the header for the ARFF file
    arff_str = "@RELATION " + relation_name + "\n\n" 

    # Iterate over each column in the DataFrame
    for columnname, columntype in zip(df.columns, df.dtypes):
        # Add the attribute name
        arff_str += "@ATTRIBUTE " + columnname + " "

        # Add the data type of the attribute
        if pd.api.types.is_numeric_dtype(columntype):
            # The column contains numeric data
            arff_str += "NUMERIC\n"
        elif pd.api.types.is_categorical_dtype(columntype):
            # The column contains categorical data
            cat_types = df[columnname].cat.categories
            arff_str += "{" + ','.join(cat_types) + "}\n"
        elif pd.api.types.is_datetime64_any_dtype(columntype):
            # The column contains date data
            # arff_str += "DATE \"yyyy-mm-dd\"\n"
            # Dates stored as strings for now
            arff_str += "STRING\n"
        else:
            # The column is a string
            arff_str += "STRING\n"

    # Define the data section of the ARFF file
    arff_str += "\n@DATA\n"

    # Write the ARFF file
    with open(outputfile, 'w') as outfile:
        outfile.write(arff_str)
        df.to_csv(outfile, index=False, header=False, lineterminator='\n')

def arff_to_pandas_dataframe(arfffile, dtype={}):
    """
    Converts an ARFF file to a pandas DataFrame.
    
    Args:
        arfffile (str): The path to the ARFF file.
        dtype (dict): A dictionary mapping column names to their respective data types.

    Returns:
        pd.DataFrame: The converted DataFrame.
    """

    # Open the ARFF file for reading
    with open(arfffile, 'r') as infile:
        # Initialize an empty list to store attribute names and types
        attributes = []

        # Iterate over each line in the ARFF file
        for line in infile:
            if line.startswith("@ATTRIBUTE"):
                # Split the line into attribute name and type
                line = line.strip().split()
                attrname, attrtype = line[1], line[2]
                # Determine the data type of the attribute based on its value
                if attrtype == "NUMERIC": # numeric values are floats or integers
                    if attrname in dtype:
                        attributes.append((attrname, dtype[attrname]))
                    else:
                        attributes.append((attrname, "float"))
                elif attrtype == "STRING":
                    attributes.append((attrname, "str"))  # string values are strings
                elif attrtype.startswith("{"):
                    attributes.append((attrname, "category"))  # categorical values are stored in a category data type
            elif line.startswith("@DATA"):
                # Read the rest of the file into a pandas DataFrame once all attribute information has been gathered
                break

        # Create a pandas DataFrame with the specified attributes and data type
        df = pd.read_csv(infile, sep=',', header=None,
                     names=[attr[0] for attr in attributes], dtype={attrname: attrtype for attrname, attrtype in attributes})

    return df  

def csv_to_arff(csvfile, arfffile, dtype, relation_name="test"):
    """
    Converts a CSV file to an ARFF file.
    
    Args:
        csvfile (str): The path to the CSV file.
        arfffile (str): The path where the ARFF file will be written.
        dtype (dict): A dictionary mapping column names to their respective data types.
        relation_name (str, optional): The name of the relationship in the ARFF file. Defaults to "test".
    
    Returns:
        None
    """

    # Generate the header for the ARFF file
    arff_str = "@RELATION " + relation_name + "\n\n" 

    with open(csvfile, 'r') as infile:
        columns = next(infile).strip().split(',')

        for columnname in columns:
            columntype = dtype[columnname]
            # Add the attribute name
            arff_str += "@ATTRIBUTE " + columnname + " "

    
            # Add the data type of the attribute
            if pd.api.types.is_numeric_dtype(columntype[:len("category")]):
                # The column contains numeric data
                arff_str += "NUMERIC\n"
            elif pd.api.types.is_categorical_dtype(columntype[:len("category")]):
                # The column contains categorical data
                cat_types = columntype[columntype.find("{")+1:columntype.find("}")].split(',')
                arff_str += "{" + ','.join(cat_types) + "}\n"
            elif pd.api.types.is_datetime64_any_dtype(columntype[:len("category")]):
                # The column contains date data
                # arff_str += "DATE \"yyyy-mm-dd\"\n"
                # Dates stored as strings for now
                arff_str += "STRING\n"
            else:
                # The column is a string
                arff_str += "STRING\n"
    
        # Define the data section of the ARFF file
        arff_str += "\n@DATA\n"

        # Write the generated ARFF header to the corresponding ARFF file and write the data
        with open(arfffile, 'w') as outfile:
            outfile.write(arff_str)
            for line in infile:
                outfile.write(line)

def arff_to_csv(arfffile, csvfile):
    """
    Converts an ARFF file to a CSV file.

    Args:
        arfffile (str): The path to the ARFF file.
        csvfile (str): The path where the CSV file will be written.

    Returns:
        None
    """

    # Open the ARFF file for reading
    with open(arfffile, 'r') as infile:
        # Initialize an empty list to store attribute names and types
        attributes = []

        # Iterate over each line in the ARFF file
        for line in infile:
            if line.startswith("@ATTRIBUTE"):
                # Get the attribute name
                line = line.strip().split()
                attrname = line[1]
                # Add the attribute name to the list of attributes
                attributes.append(attrname)
            elif line.startswith("@DATA"):
                # Read the rest of the file
                break

        # Write the generated CSV header to the corresponding CSV file and write the data
        with open(csvfile, 'w') as outfile:
            outfile.write(",".join(attributes) + "\n")
            for line in infile:
                outfile.write(line)

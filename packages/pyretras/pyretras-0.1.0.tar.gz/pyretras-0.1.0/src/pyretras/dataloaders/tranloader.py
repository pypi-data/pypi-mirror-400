import pandas as pd


def read_tra(fname):
    """
    Reads and parses a transport input file for a groundwater transport simulation.
    This function processes a structured input file, extracting various configuration
    sections and parameters required for transport modeling. It identifies key sections
    by their header keywords, parses the relevant data, and organizes the results into
    a dictionary for further use in the simulation workflow.
    Parameters
    ----------
    fname : str
        Path to the transport input file to be read.
    Returns
    -------
    project_tran : dict
        A dictionary containing parsed data for each recognized section of the input file.
        The keys correspond to section names, and the values are the extracted data,
        which may be strings, dictionaries, or pandas DataFrames depending on the section.
    Notes
    -----
    - The function expects the input file to follow a specific format with known section headers.
    - Several helper functions (e.g., get_FlowTransportControlVaraible, get_DimensionVariables, etc.)
      are used to parse individual sections.
    - The function assumes that all required sections and data are present and correctly formatted.
    - The function prints progress and warnings to the console during parsing.
    """

    print("Start to read the Transport file=>", fname)
    ## initial value with -1 for easy checking if the key word is found in the input file
    keyword_tran = {
        "title card": -1,
        "flow and transport and general controls": -1,
        "chemical calculation controls": -1,
        "input and output file names": -1,
        "dimension variables": -1,
        "time steps": -1,
        "piecewise functions": -1,
        "aquifer parameters": -1,
        "default values for data to elements": -1,
        "data to elements": -1,
        "default values for data to nodes": -1,
        "data to nodes": -1,
        "data to convergence criteria": -1,
        "data to jacobian matrix": -1,
        "writing control variables": -1,
        "nodes for writing in time": -1,
        "components for writing": -1,
        "aquous species for writing": -1,
        "minerals for writing": -1,
    }

    project_tran = {}
    with open(fname, encoding="latin1") as f:
        lines = f.readlines()
    f.close()
    # find the line numbers for each of keyword_tran
    for idx, line in enumerate(lines):
        line = line.strip("\n")
        for key in keyword_tran:
            if key in line.lower():
                keyword_tran[key] = idx
                break

    for key, idx in keyword_tran.items():

        if key == "title card":
            if idx >= 0:
                title = lines[idx + 1]
                print(title)
                project_tran[key] = title
        if key == "flow and transport and general controls":
            if idx >= 0:
                line = lines[idx + 1].strip("\n")
                columnNames = [
                    "iotpa",
                    "ioflu",
                    "iodim",
                    "xita1",
                    "xita2",
                    "iheat",
                    "irestart",
                ]
                flowTranControlVariables = get_FlowTransportControlVaraible(
                    line, columnNames
                )
                project_tran[key] = flowTranControlVariables
        if key == "chemical calculation controls":
            if idx >= 0:
                line = lines[idx + 1].strip("\n")
                columnNames = ["ispia", "inibound"]
                chemControlVariables = get_ChemicalCalculationControl(line, columnNames)
                project_tran[key] = chemControlVariables

        if key == "input and output file names":
            if idx >= 0:
                newlines = lines[idx + 1 : idx + 33]
                fileControls = get_InputOutputFilenames(newlines)
                project_tran[key] = fileControls

        # dimension varaibles should be provided earlier than time steps
        if key == "dimension variables":
            if idx >= 0:
                line = lines[idx + 1]
                columnName = ["nnod", "nele", "nma", "ntimeint"]
                dimensionVariables = get_DimensionVariables(line, columnName)
                project_tran[key] = dimensionVariables

        if key == "time steps":
            if idx >= 0:
                ntimeint = dimensionVariables["ntimeint"].values[0]
                newlines = lines[idx + 1 : idx + 1 + ntimeint]
                columnName = ["timeint", "nstep"]
                timeSteps = get_TimeSteps(newlines, columnName)
                project_tran[key] = timeSteps

        if key == "piecewise functions":
            if idx >= 0:
                piecewiseFunctions = {}
                line = lines[idx + 1].strip("\n")
                columnName = ["nboundfh", "nboundfc"]
                numbBoundFuns = get_BoundNumberFunc(line, columnName)
                piecewiseFunctions["numberBoundFunction"] = numbBoundFuns
                ntimeint = dimensionVariables["ntimeint"].values[0]
                nboundfh = numbBoundFuns["nboundfh"].values[0]
                nboundfc = numbBoundFuns["nboundfc"].values[0]
                if nboundfh > 0:
                    boundFunH = pd.DataFrame()
                    for jh in range(nboundfh):
                        l1 = idx + 3 + jh * (ntimeint + 1)
                        l2 = l1 + (ntimeint + 1)
                        newlines = lines[l1:l2]
                        funh = get_boundfunc(newlines)
                        if len(funh) != ntimeint:
                            print("The ", jh + 1, "th BOUNDFH has a probelm!")
                        funhdf = pd.DataFrame({"fh" + str(jh): funh})
                        if len(boundFunH) != 0:
                            boundFunH = pd.concat([boundFunH, funhdf], axis=1)
                        else:
                            boundFunH = funhdf.copy()
                    piecewiseFunctions["BoundFunH"] = boundFunH
                if nboundfc > 0:
                    if nboundfh == 0:
                        jc_idx = idx + 2
                    else:
                        jc_idx = idx + 3 + nboundfh * (ntimeint + 1)

                    boundFunC = pd.DataFrame()
                    for jc in range(nboundfc):
                        l1 = jc_idx + 1 + jc * (ntimeint + 1)
                        l2 = l1 + ntimeint + 1
                        newlines = lines[l1:l2]
                        func = []
                        func = get_boundfunc(newlines)
                        if len(func) != ntimeint:
                            print("The ", jc + 1, "th BOUNDFH has a probelm!")
                        funcdf = pd.DataFrame({"fc" + str(jc): func})
                        if len(boundFunC) == 0:
                            boundFunC = funcdf.copy()
                        else:
                            boundFunC = pd.concat([boundFunC, funcdf], axis=1)
                    piecewiseFunctions["BoundFunC"] = boundFunC
                project_tran[key] = piecewiseFunctions

        if key == "aquifer parameters":
            if idx >= 0:
                nma = dimensionVariables["nma"].values[0]
                newlines = lines[idx + 1 : idx + 1 + nma]
                columnNames = [
                    "pk1",
                    "pk2",
                    "angle",
                    "ss",
                    "por",
                    "dfm",
                    "dsl",
                    "dst",
                    "densec",
                    "porcin",
                ]
                aquiferParameters = get_AquiferZoneParameters(newlines, columnNames)
                iotpa = flowTranControlVariables["iotpa"].values[0]
                if iotpa == 2:  ## Read the unsaturated parameters
                    newlines = lines[idx + 1 + nma + 1 : idx + 1 + nma + 1 + nma]
                    columnNames = ["ia", "itprl", "sr", "sas", "cm", "alpha"]
                    unsaturatedParameters = get_UnsaturatedParameters(
                        newlines, columnNames
                    )
                    aquiferParameters = pd.concat(
                        [aquiferParameters, unsaturatedParameters], axis=1
                    )

                aquiferParameters.index.name = "zone"
                project_tran[key] = aquiferParameters

        if key == "default values for data to elements":
            if idx >= 0:
                line = lines[idx + 1].strip("\n")
                columnNames = ["matdf", "thickdf", "rechdf", "irechdf"]
                defaultElementValues = get_DefaultData4elements(line, columnNames)
                project_tran[key] = defaultElementValues
        if key == "data to elements":
            ## For current version, all elements should be provided
            nele = dimensionVariables["nele"].values[0]
            if idx >= 0:
                newlines = lines[idx + 1 : idx + 1 + nele]
                columnNames = [
                    "ie",
                    "node1",
                    "node2",
                    "node3",
                    "mat",
                    "thick",
                    "rech",
                    "irech",
                ]
                elementData = get_ElementData(
                    newlines, defaultElementValues, columnNames
                )

                # Note that the node for element starts with 1, needs to subtract - 1
                # Probably in the future, we need to numbering the nodes from 0.
                elementData[["node1", "node2", "node3"]] = (
                    elementData[["node1", "node2", "node3"]] - 1
                )

                project_tran[key] = elementData
        if key == "default values for data to nodes":
            ## For current version, all elements should be provided
            if idx >= 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                defaultDataNode = get_DefaultDataNodes(line)
                project_tran[key] = defaultDataNode
        if key == "data to nodes":
            ## For current version, all nodes should be provided
            nnod = dimensionVariables["nnod"].values[0]
            if idx >= 0:
                newlines = lines[idx + 1 : idx + 1 + nnod]
                columnNames = [
                    "ip",
                    "xx",
                    "y",
                    "idbh",
                    "hp",
                    "q1",
                    "alfa",
                    "iq",
                    "h0",
                    "idboc",
                    "izoneiw",
                    "izonebw",
                    "izonerw",
                    "izonem",
                    "izoneg",
                    "izoned",
                    "izonex",
                ]
                nodeData = get_NodeData(newlines, defaultDataNode, columnNames)

                project_tran[key] = nodeData
        if key == "data to convergence criteria":
            if idx >= 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                columnNames = [
                    "maxitpfl",
                    "tolfl",
                    "maxitptr",
                    "toltr",
                    "maxitpch",
                    "tolch",
                    "maxitpad",
                    "tolad",
                ]
                dataConverCriteria = get_ConvergenceCriteria(line, columnNames)
                project_tran[key] = dataConverCriteria
        if key == "data to jacobian matrix":
            #
            if idx >= 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                columnNames = ["iswitch", "itemp", "njacob"]
                dataJacobianMatrix = get_DataJacobianMatrix(line, columnNames)
                project_tran[key] = dataJacobianMatrix

        if key == "writing control variables":
            if idx >= 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                columnNames = [
                    "nwxy",
                    "nwdim",
                    "nwti",
                    "nwnod",
                    "nwcom",
                    "nacom",
                    "nwmin",
                    "indmat",
                    "nvol",
                    "nwtv",
                ]
                writingControlVariables = get_WritingControlVariables(line, columnNames)
                project_tran[key] = writingControlVariables

        if key == "nodes for writing in time":
            nwnod = writingControlVariables["nwnod"].values[0]
            if idx >= 0 and nwnod > 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                nodesWritinginTime = get_WritinginTime(line, nwnod)
                project_tran[key] = nodesWritinginTime

        if key == "components for writing":
            nwcom = writingControlVariables["nwcom"].values[0]
            if idx >= 0 and nwcom > 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                componentsWritinginTime = get_WritinginTime(line, nwcom)
                project_tran[key] = componentsWritinginTime

        if key == "aquous species for writing":
            nacom = writingControlVariables["nacom"].values[0]
            if idx >= 0 and nwcom > 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                aquSpecWritinginTime = get_WritinginTime(line, nacom)
                project_tran[key] = aquSpecWritinginTime

        if key == "minerals for writing":
            nwmin = writingControlVariables["nwmin"].values[0]
            if idx >= 0 and nwmin > 0:
                line = lines[idx + 1]
                line = line.strip("\n")
                mineralsWritinginTime = get_WritinginTime(line, nwmin)
                project_tran[key] = mineralsWritinginTime

    return project_tran


def get_FlowTransportControlVaraible(line, columnNames):
    """
    Parses a line of flow transport control variables, either in free (comma-separated) or fixed-width format,
    and returns a pandas DataFrame with the variables as columns.
    Args:
        line (str): The input string containing the flow transport control variables.
        columnNames (list of str): List of column names for the variables.
    Returns:
        pandas.DataFrame: A single-row DataFrame with variable names as columns and their corresponding values.
    Notes:
        - If the input line contains commas, it is treated as free format and split accordingly.
        - Otherwise, the line is parsed as fixed-width fields with predefined widths.
        - The function expects exactly 7 variables; if not, a warning is printed.
        - The resulting DataFrame columns are cast to int or float types as appropriate.
    """

    if len(line) > 45:
        line = line[:45]
    if "," in line:  # Freee format
        flowTranControlVariables = line.split(",")[:7]
    else:  # The traditional fixed format
        length = len(line)
        if length < 45:
            line = line + " " * (45 - length)
        width = [5, 5, 5, 10, 10, 5, 5]
        flowTranControlVariables = []
        l1 = 0
        for wth in width:
            l2 = l1 + wth
            pa = line[l1:l2].strip()
            if len(pa) == 0:
                pa = 0
            if wth == 10:
                pa = float(pa)
            else:
                pa = int(pa)
            flowTranControlVariables.append(pa)
            l1 = l2
            ## Check the number of the variables in the list

    if len(flowTranControlVariables) != 7:
        print("there are something wrong!")

    flowTranControlVariables = pd.DataFrame(
        {"var": columnNames, "val": flowTranControlVariables}
    )
    flowTranControlVariables = flowTranControlVariables.set_index("var")
    flowTranControlVariables = flowTranControlVariables.T
    cols = flowTranControlVariables.columns
    for i in range(len(cols)):
        col = cols[i]
        if 3 <= i < 5:
            flowTranControlVariables[col] = flowTranControlVariables[col].astype(float)
        else:
            flowTranControlVariables[col] = flowTranControlVariables[col].astype(int)

    return flowTranControlVariables


def get_ChemicalCalculationControl(line, columnName):
    """
    Parses a line of chemical calculation control variables and returns them as a pandas DataFrame.
    The function supports both free format (comma-separated values) and traditional fixed-width format.
    - In free format, the line is split by commas.
    - In fixed format, the line is split into two variables of width 5 each (up to 10 characters).
    Parameters:
        line (str): The input string containing chemical calculation control variables.
        columnName (list or array-like): The names to assign to the variables in the resulting DataFrame.
    Returns:
        pandas.DataFrame: A DataFrame with the control variables as values and columnName as the index.
    Notes:
        - If the number of parsed variables is not 2, a warning message is printed.
        - If a variable is missing in fixed format, it is set to 0.
    """

    chemControlVariables = []
    if len(line) > 10:
        line = line[:10]
    if "," in line:  # Freee format
        chemControlVariables = line.split(",")
    else:  # The traditional fixed format
        length = len(line)
        if length < 10:
            line = line + " " * (10 - length)
        else:
            line = line[:10]
            width = [5, 5]
            # controlVariables=[]
            l = 0
            for wdth in width:
                l1 = l + wdth
                var = line[l:l1].strip()
                if len(var) == 0:
                    var = 0
                chemControlVariables.append(var)
    ## Check the number of the variables in the list
    if len(chemControlVariables) != 2:
        print("there are something wrong")
    chemControlVariables = pd.DataFrame(
        {"var": columnName, "val": chemControlVariables}
    )
    chemControlVariables = chemControlVariables.set_index("var")

    return chemControlVariables.T


def get_InputOutputFilenames(lines):
    """
    Parses a list of lines to extract input and output file names, write indicators, and additional indicators.
    Each line in the input corresponds to a specific file or output, and the function uses the `get_Filenames`
    helper to extract relevant information from each line. The results are aggregated into lists and returned
    as a pandas DataFrame with columns for write indicators, file names, and any additional indicators.
    Args:
        lines (list of str): List of lines, each containing information about a file or output.
    Returns:
        pandas.DataFrame: A DataFrame with columns:
            - 'IOwrite': List of integer write indicators for each file/output.
            - 'fileName': List of extracted file names.
            - 'additionalIndicator': List of additional indicators (may be empty strings or lists).
    """

    IOWrite = []
    fileNameLst = []
    additionalIndicators = []
    iow, inputhet = get_Filenames(lines[0], 30, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(inputhet)
    additionalIndicators.append("")

    iow, inputche = get_Filenames(lines[1], 30, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(inputche)
    additionalIndicators.append("")

    iow, outche = get_Filenames(lines[2], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outche)
    additionalIndicators.append("")

    iow, outthx = get_Filenames(lines[3], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outthx)
    additionalIndicators.append("")

    iow, outht = get_Filenames(lines[4], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outht)
    additionalIndicators.append("")

    iow, outvt = get_Filenames(lines[5], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outvt)
    additionalIndicators.append("")

    iow, outft = get_Filenames(lines[6], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outft)
    additionalIndicators.append("")

    iow, outwt = get_Filenames(lines[7], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outwt)
    additionalIndicators.append("")

    iow, outtex = get_Filenames(lines[8], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outtex)
    additionalIndicators.append("")

    iow, outtet = get_Filenames(lines[9], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outtet)
    additionalIndicators.append("")

    iow, outspx = get_Filenames(lines[10], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outspx)
    additionalIndicators.append("")

    iow, outspt = get_Filenames(lines[11], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outspt)
    additionalIndicators.append("")

    iow, outphx = get_Filenames(lines[12], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outphx)
    additionalIndicators.append("")

    iow, outpht = get_Filenames(lines[13], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outpht)
    additionalIndicators.append("")

    iow, outmix, kliter = get_Filenames(lines[14], 20, 2)
    IOWrite.append(int(iow))
    fileNameLst.append(outmix)
    additionalIndicators.append("")

    iow, outmit = get_Filenames(lines[15], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outmit)
    additionalIndicators.append("")

    iow, outpex = get_Filenames(lines[16], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outpex)
    additionalIndicators.append("")

    iow, outpet = get_Filenames(lines[17], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outpet)
    additionalIndicators.append("")

    iow, outadx = get_Filenames(lines[18], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outadx)
    additionalIndicators.append("")

    iow, outadt = get_Filenames(lines[19], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outadt)
    additionalIndicators.append("")

    iow, outiter = get_Filenames(lines[20], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outiter)
    additionalIndicators.append("")

    iow, outcesc = get_Filenames(lines[21], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outcesc)
    additionalIndicators.append("")

    iow, outexx = get_Filenames(lines[22], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outexx)
    additionalIndicators.append("")

    iow, outsix = get_Filenames(lines[23], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outsix)
    additionalIndicators.append("")

    iow, outsit = get_Filenames(lines[24], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outsit)
    additionalIndicators.append("")

    iow, outmasol, ichkMs = get_Filenames(lines[25], 20, 2)
    IOWrite.append(int(iow))
    fileNameLst.append(outmasol)
    additionalIndicators.append(ichkMs)

    iow, outmprec = get_Filenames(lines[26], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outmprec)
    additionalIndicators.append("")

    iow, nodbal, inodbal = get_Filenames(lines[27], 20, 2)
    IOWrite.append(int(iow))
    fileNameLst.append(nodbal)
    additionalIndicators.append(inodbal)

    iow, outpeclet = get_Filenames(lines[28], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(outpeclet)
    additionalIndicators.append("")

    iow, log1, iterat, iterstop = get_Filenames(lines[29], 20, 3)
    IOWrite.append(int(iow))
    fileNameLst.append(log1)
    additionalIndicators.append([iterat, iterstop])

    iow, log2 = get_Filenames(lines[30], 20, 1)
    IOWrite.append(int(iow))
    fileNameLst.append(log2)
    additionalIndicators.append("")

    iow, log3, selectr = get_Filenames(lines[31], 20, 4)
    IOWrite.append(int(iow))
    fileNameLst.append(log3)
    additionalIndicators.append("")
    fileControls = pd.DataFrame(
        {
            "IOwrite": IOWrite,
            "fileName": fileNameLst,
            "additionalIndicator": additionalIndicators,
        }
    )

    return fileControls


def get_Filenames(line, width=30, itype=1):
    """
    Parses a line of text to extract file-related information based on the specified input type.
    Parameters:
        line (str): The input line containing file information.
        width (int, optional): The width used to extract the filename substring. Default is 30.
        itype (int, optional): The type of parsing to perform. Determines the expected format and return values.
            - 1: Extracts an integer and a filename.
            - 2: Extracts an integer, a filename, and an integer 'kliter'.
            - 3: Extracts an integer, a filename, and two integers 'iterat' and 'iterstop'.
            - 4: Extracts an integer, a filename, and a string 'selectr'.
    Returns:
        tuple: A tuple containing the extracted values, which varies depending on 'itype':
            - itype == 1: (int iow, str filename)
            - itype == 2: (int iow, str filename, int kliter)
            - itype == 3: (int iow, str filename, int iterat, int iterstop)
            - itype == 4: (int iow, str filename, str selectr)
    Notes:
        - The function supports both space-separated and fixed-width formats.
        - If the line contains a comma, it is assumed to be space-separated; otherwise, fixed-width parsing is used.
        - For missing or empty fields in fixed-width parsing, default values (0 or empty string) are used.
    """

    if itype == 1:
        line = line.strip("\n")
        if len(line) > 35:
            line = line[:35]
        if "," in line:
            iow, filename = line.split()
        else:
            iow = line[:5]
            l2 = 5 + width
            filename = line[5:l2]
        return int(iow), filename

    if itype == 2:
        line = line.strip("\n")
        if len(line) > 25:
            line = line[:25]

        if "," in line:
            iow, filename, kliter = line.split()
        else:
            iow = line[:5]
            l2 = 5 + width
            filename = line[5:l2]
            l3 = l2 + 5
            kliter = line[l2:l3].strip()
            if len(kliter) == 0:
                kliter = 0
        return int(iow), filename, int(kliter)

    if itype == 3:
        line = line.strip("\n")
        if len(line) > 35:
            line = line[:35]

        if "," in line:
            iow, filename, iterat, iterstop = line.split()
        else:
            iow = line[:5]
            l2 = 5 + width
            filename = line[5:l2]
            l3 = l2 + 5
            iterat = line[l2:l3].strip()
            if len(iterat) == 0:
                iterat = 0
            l4 = l3 + 5
            iterstop = line[l3:l4].strip()
            if len(iterstop) == 0:
                iterstop = 0
        return int(iow), filename, int(iterat), int(iterstop)

    if itype == 4:
        line = line.strip("\n")
        if len(line) > 30:
            line = line[:30]

        if "," in line:
            iow, filename, selectr = line.split()
        else:
            iow = line[:5]
            l2 = 5 + width
            filename = line[5:l2]
            l3 = l2 + 5
            selectr = line[l2:l3].strip()
        return int(iow), filename, selectr


def get_DimensionVariables(line, columnName):
    """
    Parses a string representing dimension variables and returns them as a pandas DataFrame.
    The function processes the input `line` in two ways:
    - If the line contains commas, it splits the line by commas to extract up to 4 dimension variables.
    - If the line does not contain commas, it splits the line into four fixed-width (5 characters each) segments.
    Each extracted variable is stripped of whitespace and converted to an integer (empty segments are treated as 0).
    The resulting variables are returned as a single-row DataFrame with `columnName` as the index and the variables as values.
    Args:
        line (str): The input string containing dimension variables, either comma-separated or fixed-width.
        columnName (str): The name to use as the index for the resulting DataFrame.
    Returns:
        pandas.DataFrame: A single-row DataFrame with the parsed dimension variables, indexed by `columnName`.
    """

    if len(line) > 20:
        line = line[:20]
    if "," in line:
        dimensionVariables = line.strip("\n").split(",")
    else:
        length = len(line)
        if length < 20:
            line = line + " " * (20 - length)
        width = [5, 5, 5, 5]
        dimensionVariables = []
        l1 = 0
        for wth in width:
            l2 = l1 + wth
            dimensionVariables.append(line[l1:l2])
            l1 = l2

    for idx, pa in enumerate(dimensionVariables):
        pa = pa.strip()
        if len(pa) == 0:
            pa = 0
        dimensionVariables[idx] = int(pa)

    dimensionVariables = pd.DataFrame({"var": columnName, "val": dimensionVariables})
    dimensionVariables = dimensionVariables.set_index("var")

    return dimensionVariables.T


def get_TimeSteps(lines, columnNames):
    """
    Parses a list of lines to extract time step and step number information, returning a DataFrame.
    The function supports two formats for each line:
    1. CSV format: If a line contains a comma, it is split into three parts, and the second and third parts are parsed as time and step number.
    2. Fixed-width format: If a line does not contain a comma, it is parsed by extracting two fields from specific character positions.
    Empty or missing values for time or step number are replaced with 0.
    Args:
        lines (list of str): List of lines containing time step data in either CSV or fixed-width format.
        columnNames (list of str): List of column names for the resulting DataFrame.
    Returns:
        pandas.DataFrame: DataFrame with columns specified by `columnNames`, containing parsed time and step number values.
    """

    timeSteps = []
    for line in lines:
        line = line.strip("\n")
        if len(line) > 20:
            line = line[:20]

        if "," in line:
            _, time, nstp = line.split(",")
            time = time.strip()
            nstp = nstp.strip()
            if len(time) == 0:
                time = 0.0
            if len(nstp) == 0:
                nstp = 0
            timeSteps.append([float(time), int(nstp)])
        else:
            length = len(line)
            if length < 20:
                line = line + " " * (20 - length)
            step = []
            for i in range(2):
                l1 = 5 + i * 10
                l2 = 5 + (i + 1) * 10
                pa = line[l1:l2].strip()
                if len(pa) == 0:
                    pa = 0
                if i % 2 == 0:
                    pa = float(pa)
                else:
                    pa = int(pa)
                step.append(pa)
            timeSteps.append(step)

    timeSteps = pd.DataFrame(timeSteps, columns=columnNames)
    return timeSteps


def get_BoundNumberFunc(line, columnNames):
    """
    Parses a line containing two numeric values (either comma-separated or fixed-width)
    and returns a pandas DataFrame with these values mapped to the provided column names.
    Args:
        line (str): A string containing two numbers, either separated by a comma or as a fixed-width string.
        columnNames (list or array-like): A list of two column names to assign to the parsed values.
    Returns:
        pandas.DataFrame: A DataFrame with one row, indexed by the provided column names,
        containing the parsed integer values.
    Notes:
        - If the input line is longer than 10 characters, it is truncated to 10 characters.
        - If the line contains a comma, it is split into two values.
        - If not, the first 5 characters are taken as the first value, and the next 5 as the second.
        - If a value is missing or empty, it defaults to 0.
    """

    if len(line) > 10:
        line = line[:10]
    if "," in line:
        nboundfh, nboundfc = line.split(",")
    else:
        length = len(line)
        if length < 10:
            line = line + " " * (10 - length)
        else:
            line = line[:10]
        nboundfh = line[:5]
        nboundfc = line[5:]

    nboundfh = nboundfh.strip()
    nboundfc = nboundfc.strip()
    if len(nboundfh) == 0:
        nboundfh = 0
    if len(nboundfc) == 0:
        nboundfc = 0
    numbBoundFuncs = pd.DataFrame(
        {"var": columnNames, "val": [int(nboundfh), int(nboundfc)]}
    )
    numbBoundFuncs = numbBoundFuncs.set_index("var")

    return numbBoundFuncs.T


def get_boundfunc(newlines):
    """
    Extracts and converts numerical boundary values from a list of strings.
    Args:
        newlines (list of str): A list of strings, where each string represents a line. The first line is ignored; subsequent lines are expected to contain numerical values.
    Returns:
        list of float: A list of floating-point numbers parsed from the input lines (excluding the first line).
    Raises:
        ValueError: If any of the lines (excluding the first) cannot be converted to a float.
    """

    bound = []
    for line in newlines[1:]:
        line = line.strip("\n").strip()
        bound.append(float(line))
    return bound


def get_AquiferZoneParameters(newlines, columnNames):
    """
    Parses a list of strings representing aquifer zone parameters and returns a pandas DataFrame.
    Each line in `newlines` is processed to extract up to 10 parameters per aquifer zone, either by splitting
    comma-separated values or by fixed-width slicing. The extracted parameters are converted to floats and
    organized into a DataFrame with columns specified by `columnNames`.
    Args:
        newlines (list of str): List of strings, each representing a line of aquifer zone data.
        columnNames (list of str): List of column names for the resulting DataFrame.
    Returns:
        pandas.DataFrame: DataFrame containing the parsed aquifer zone parameters.
    """

    aquiferParameters = []
    for line in newlines:
        line = line.strip("\n")
        if len(line) > 95:
            line = line[:95]
        aqzone = []
        if "," in line:
            aqzone = line[5:].split(",")
        else:
            length = len(line)
            if length < 95:
                line = line + " " * (95 - length)
            for i in range(10):
                l1 = 5 + i * 9
                l2 = l1 + 9
                pa = line[l1:l2]
                aqzone.append(pa)

        aqzone = [pa.strip() for pa in aqzone]
        aqzone = [float(pa) if len(pa) > 0 else 0 for pa in aqzone]
        aquiferParameters.append(aqzone)

        aquiferParameters = pd.DataFrame(aquiferParameters, columns=columnNames)

        return aquiferParameters


def get_UnsaturatedParameters(newlines, columnNames):
    """
    Parses a list of strings representing unsaturated parameter data and returns a pandas DataFrame.
    Each line in `newlines` is expected to contain values for the following parameters:
    - IA (neglected)
    - ITPRL
    - Sr
    - Ss
    - m
    - alpha
    The function supports both comma-separated and fixed-width formatted lines. For fixed-width lines,
    the expected format is:
        - Characters 0-4: ITPRL
        - Characters 5-9: Sr
        - Characters 10-18: Ss
        - Characters 19-27: m
        - Characters 28-36: alpha
    Parameters:
        newlines (list of str): List of strings, each representing a line of parameter data.
        columnNames (list of str): List of column names for the resulting DataFrame.
    Returns:
        pandas.DataFrame: DataFrame containing the parsed unsaturated parameters, with columns as specified by `columnNames`.
    """

    # IA,ITPRL,Sr, Ss, m and alpha
    ## The IA is neglected
    unsaturatedParameters = []
    for line in newlines:
        line = line.strip("\n")
        if len(line) > 55:
            line = line[:55]
        aqzone = []
        if "," in line:
            aqzone = line.split(",")
        else:
            length = len(line)
            if length < 55:
                line = line + " " * (55 - length)
            pa = line[0:5]
            aqzone.append(pa)
            pa = line[5:10]
            aqzone.append(pa)
            for i in range(4):  # Sr, Ss, m and alpha
                l1 = 10 + i * 9
                l2 = l1 + 9
                pa = line[l1:l2]
                aqzone.append(pa)

        for idx, pa in enumerate(aqzone):
            pa = pa.strip()
            if len(pa) == 0:
                pa = 0
            if idx <= 1:
                pa = int(pa)
            else:
                pa = float(pa)
            aqzone[idx] = pa
        unsaturatedParameters.append(aqzone)
        unsaturatedParameters = pd.DataFrame(unsaturatedParameters, columns=columnNames)

        return unsaturatedParameters


def get_DefaultData4elements(line, columnNames):
    """
    Parses a line of data and extracts four default element values, converting them to appropriate types.
    The function supports two formats:
    1. Free format: If the line contains commas, it is split by commas.
    2. Fixed format: Otherwise, the line is padded/truncated to 30 characters and split into four fields
       of widths [5, 10, 10, 5].
    The extracted values are converted as follows:
    - The first and fourth values are converted to integers.
    - The second and third values are converted to floats.
    If the number of extracted values is not four, a warning message is printed.
    Args:
        line (str): The input line containing element data, either comma-separated or fixed-width.
        columnNames (list): List of column names (not used in the function logic).
    Returns:
        list: A list of four values [int, float, float, int] representing the parsed element data.
    """

    defaultElementValues = []
    if len(line) > 30:
        line = line[:30]
    if "," in line:  # Freee format
        defaultElementValues = line.split(",")
    else:  # The traditional fixed format
        length = len(line)
        if length <= 30:
            line = line + " " * (30 - length)
            width = [5, 10, 10, 5]
            l1 = 0
            for wth in width:
                l2 = l1 + wth
                var = line[l1:l2].strip()
                if len(var) == 0:
                    var = 0
                defaultElementValues.append(var)
                l1 = l2
    ## Check the number of the variables in the list
    if len(defaultElementValues) != 4:
        print("there are something wrong in the default values for element")

    for idx, val in enumerate(defaultElementValues):
        if idx == 0 or idx == 3:
            defaultElementValues[idx] = int(val)
        else:
            defaultElementValues[idx] = float(val)

    # defaultElementValues=pd.DataFrame({'var':columnNames,'val':defaultElementValues})
    # defaultElementValues=defaultElementValues.set_index('var')

    return defaultElementValues


def get_ElementData(newlines, defaultElementValues, columnNames):
    """
    Parses element data from a list of strings and returns a pandas DataFrame.
    Each line in `newlines` represents an element, either as a comma-separated string or a fixed-width string.
    The function extracts element properties, applies default values where necessary, and constructs a DataFrame.
    Args:
        newlines (list of str): List of strings, each representing an element's data.
        defaultElementValues (list): List of default values to use for missing or zero fields.
            - [0]: Default material value (MAT)
            - [1]: Default thickness value (THICK)
            - [2]: Default recharge value (Rech)
            - [3]: Default iRech value (iRech)
        columnNames (list of str): List of column names for the resulting DataFrame.
    Returns:
        pandas.DataFrame: DataFrame containing parsed element data, indexed by the 'ie' column.
    Notes:
        - If a line is shorter than 50 characters, it is padded with spaces.
        - If a line is longer than 50 characters, it is truncated.
        - If a field is missing or zero, the corresponding default value is used.
        - The DataFrame is indexed by the 'ie' column.
    """

    elementDataLst = []
    for line in newlines:
        eData = []
        line = line.strip("\n")
        if len(line) > 50:
            line = line[:50]

        if "," in line:
            eData = line.split(",")
        else:
            length = len(line)
            if length < 50:
                line = line + " " * (50 - length)
            width = [5, 5, 5, 5, 5, 10, 10, 5]
            l1 = 0
            for wth in width:
                l2 = l1 + wth
                eData.append(line[l1:l2])
                l1 = l2

        # IE,NODE(IE,1),NODE(IE,2),NODE(IE,3)
        eleData = [int(data.strip()) for data in eData[:4]]
        # MAT
        if len(eData[4].strip()) == 0:
            matl = 0
        else:
            matl = int(eData[4].strip())
        if matl == 0:
            matl = defaultElementValues[0]
        eleData.append(matl)

        # THICK
        if len(eData[5].strip()) == 0:
            thick = 0.0
        else:
            thick = float(eData[5].strip())
        if thick == 0.0:
            thick = defaultElementValues[1]
        eleData.append(thick)

        # Rech
        if len(eData[6].strip()) == 0:
            rech = 0.0
        else:
            rech = float(eData[6].strip())
        if rech == 0.0:
            rech = defaultElementValues[2]
        eleData.append(rech)

        # iRech
        if len(eData[7].strip()) == 0:
            rech = 0.0
        else:
            rech = int(eData[7].strip())

        rech = defaultElementValues[3]
        eleData.append(rech)

        elementDataLst.append(eleData)
        elementData = pd.DataFrame(elementDataLst, columns=columnNames)
        elementData = elementData.set_index("ie")
    return elementData


def get_DefaultDataNodes(line):
    """
    Parses a line of data representing default data nodes, either as a comma-separated string
    or as a fixed-width formatted string, and returns a list of parsed values with appropriate types.
    The function supports two input formats:
    1. Comma-separated values: The line is split by commas.
    2. Fixed-width format: The line is split into fields of predefined widths.
    The parsed values are converted to either int or float based on their position:
    - Indices 0, 4, and 6 to 13 are converted to int.
    - All other indices are converted to float.
    - Empty fields are replaced with 0.
    Parameters:
        line (str): The input string containing data node values.
    Returns:
        list: A list of parsed values with appropriate types (int or float).
    """

    # defaultDataNode:
    # idbhdf,hpdf,q1df,alfadf,iqdf,h0df,idbocdf,
    # iiwdf,ibwdf,irwdf,imidf,igsdf,iaddf,iexdf
    if len(line) > 61:
        line = line[:61]

    if "," in line:
        defaultDataNode = line.split(",")
    else:
        length = len(line)
        if length < 61:
            line = line + " " * (61 - length)

        width = [3, 7, 7, 7, 3, 10, 3, 3, 3, 3, 3, 3, 3, 3]
        defaultDataNode = []
        l1 = 0
        for wth in width:
            l2 = l1 + wth
            defaultDataNode.append(line[l1:l2])
            l1 = l2

    for idx, data in enumerate(defaultDataNode):
        pa = defaultDataNode[idx].strip()
        if len(pa) == 0:
            pa = 0
        if idx == 0 or idx == 4 or idx >= 6:
            defaultDataNode[idx] = int(pa)
        else:
            defaultDataNode[idx] = float(pa)

    return defaultDataNode


def get_NodeData(newlines, defaultDataNode, columnNames):
    """
    Parses node data from a list of strings, handling both comma-separated and fixed-width formats,
    applies default values for missing or zero fields, and returns a pandas DataFrame indexed by 'ip'.
    Args:
        newlines (list of str): List of strings, each representing a line of node data.
        defaultDataNode (list): List of default values to use for missing or zero fields.
        columnNames (list of str): List of column names for the resulting DataFrame.
    Returns:
        pandas.DataFrame: DataFrame containing parsed node data, indexed by the 'ip' column.
    Notes:
        - Each line can be either comma-separated or fixed-width.
        - For fixed-width lines, specific field widths are used to extract values.
        - If a field is missing or zero, the corresponding value from defaultDataNode is used.
        - The resulting DataFrame columns correspond to columnNames, and the index is set to 'ip'.
    """

    nodeDataLst = []
    for line in newlines:
        nodeData = []
        line = line.strip("\n")
        if len(line) > 83:
            line = line[:83]

        if "," in line:
            nodeData = line.split(",")
        else:
            length = len(line)
            if length < 83:
                line = line + " " * (83 - length)
            width = [5, 10, 10, 3, 7, 7, 7, 3, 7, 3, 3, 3, 3, 3, 3, 3, 3]
            l1 = 0
            for wth in width:
                l2 = l1 + wth
                nodeData.append(line[l1:l2])
                l1 = l2
        newNodeData = []
        # IP
        newNodeData.append(int(nodeData[0].strip()))
        # XX
        newNodeData.append(float(nodeData[1].strip()))
        # Y
        newNodeData.append(float(nodeData[2].strip()))
        # IDBH
        idbh = nodeData[3].strip()
        if len(idbh) == 0:
            idbh = 0
        else:
            idbh = int(idbh)
        if idbh == 0:
            idbh = defaultDataNode[0]
        newNodeData.append(idbh)

        # HP
        hp = nodeData[4].strip()
        if len(hp) == 0:
            hp = 0
        else:
            hp = float(hp)
        if hp == 0.0:
            hp = defaultDataNode[1]
        newNodeData.append(hp)

        # Q1
        q1 = nodeData[5].strip()
        if len(q1) == 0:
            q1 = 0.0
        else:
            q1 = float(q1)
        if q1 == 0.0:
            q1 = defaultDataNode[2]
        newNodeData.append(q1)

        # alfa
        alfa = nodeData[6].strip()
        if len(alfa) == 0:
            alfa = 0.0
        else:
            alfa = float(alfa)
        if alfa == 0.0:
            alfa = defaultDataNode[3]

        newNodeData.append(alfa)

        # iq
        iq = nodeData[7].strip()
        if len(iq) == 0:
            iq = 0
        else:
            iq = int(iq)
        if iq == 0:
            iq = defaultDataNode[4]
        newNodeData.append(iq)

        # h0
        h0 = nodeData[8].strip()
        if len(h0) == 0:
            h0 = 0.0
        else:
            h0 = float(h0)
        if h0 == 0.0:
            h0 = defaultDataNode[5]
        newNodeData.append(h0)

        # idboc
        idboc = nodeData[9].strip()
        if len(idboc) == 0:
            idboc = 0
        else:
            idboc = int(idboc)
        if idboc == 0:
            idboc = defaultDataNode[6]
        newNodeData.append(idboc)

        # izoneiw
        izoneiw = nodeData[10].strip()
        if len(izoneiw) == 0:
            izoneiw = 0
        else:
            izoneiw = int(izoneiw)
        if izoneiw == 0:
            izoneiw = defaultDataNode[7]
        newNodeData.append(izoneiw)

        # izonebw
        izonebw = nodeData[11].strip()
        if len(izonebw) == 0:
            izonebw = 0
        else:
            izonebw = int(izonebw)
        if izonebw == 0:
            izonebw = defaultDataNode[8]
        newNodeData.append(izonebw)

        # izonerw
        izonerw = nodeData[12].strip()
        if len(izonerw) == 0:
            izonerw = 0
        else:
            izonerw = int(izonerw)
        if izonerw == 0:
            izonerw = defaultDataNode[9]
        newNodeData.append(izonerw)

        # izonem
        izonem = nodeData[13].strip()
        if len(izonem) == 0:
            izonem = 0
        else:
            izonem = int(izonem)
        if izonem == 0:
            izonem = defaultDataNode[10]
        newNodeData.append(izonem)

        # izoneg
        izoneg = nodeData[14].strip()
        if len(izoneg) == 0:
            izoneg = 0
        else:
            izoneg = int(izoneg)
        if izoneg == 0:
            izoneg = defaultDataNode[11]
        newNodeData.append(izoneg)

        # izoned
        izoned = nodeData[15].strip()
        if len(izoned) == 0:
            izoned = 0
        else:
            izoned = int(izoned)
        if izoned == 0:
            izoned = defaultDataNode[12]
        newNodeData.append(izoned)

        # izonex
        izonex = nodeData[16].strip()
        if len(izonex) == 0:
            izonex = 0
        else:
            izonex = int(izonex)
        if izonex == 0:
            izonex = defaultDataNode[13]
        newNodeData.append(izonex)
        nodeDataLst.append(newNodeData)

    dataNode = pd.DataFrame(nodeDataLst, columns=columnNames)
    dataNode = dataNode.set_index("ip")
    return dataNode


def get_ConvergenceCriteria(line, columnNames):
    """
    Parses a line containing convergence criteria parameters and returns them as a pandas DataFrame.
    The function supports two input formats for the `line` parameter:
    1. Comma-separated values.
    2. Fixed-width fields (total 60 characters, with alternating int/float values).
    Parameters:
        line (str): A string containing the convergence criteria values, either comma-separated or fixed-width.
        columnNames (list of str): List of column names corresponding to the convergence criteria parameters.
    Returns:
        pandas.DataFrame: A DataFrame with one row, indexed by the provided column names, containing the parsed
        convergence criteria values as integers and floats in the correct order.
    Notes:
        - The expected order of parameters is: maxitpfl, tolfl, maxitptr, toltr, maxitpch, tolch, maxitpad, tolad.
        - Integer and float types alternate in the parsed output.
        - If a value is missing or empty, it is replaced with 0.
    """

    # maxitpfl, tolfl, maxitptr, toltr, maxitpch, tolch,maxitpad, tolad
    if len(line) > 60:
        line = line[:60]

    if "," in line:
        dataConverCriteria = line.split(",")
    else:
        length = len(line)
        if length < 60:
            line = line + " " * (60 - length)
        width = [5, 10, 5, 10, 5, 10, 5, 10]
        dataConverCriteria = []
        l1 = 0
        for wth in width:
            l2 = l1 + wth
            dataConverCriteria.append(line[l1:l2])
            l1 = l2

    for idx, pa in enumerate(dataConverCriteria):
        pa = pa.strip()
        if len(pa) == 0:
            pa = 0
        if idx % 2 == 0:
            dataConverCriteria[idx] = int(pa)
        else:
            dataConverCriteria[idx] = float(pa)

    dataConverCriteria = pd.DataFrame({"var": columnNames, "val": dataConverCriteria})
    dataConverCriteria = dataConverCriteria.set_index("var")
    dataConverCriteria = dataConverCriteria.T
    cols = dataConverCriteria.columns
    for i in range(len(cols)):
        col = cols[i]
        if i % 2 == 0:
            dataConverCriteria[col] = dataConverCriteria[col].astype(int)
        else:
            dataConverCriteria[col] = dataConverCriteria[col].astype(float)

    return dataConverCriteria


def get_DataJacobianMatrix(line, columnNames):
    """
    Parses a line of data to extract Jacobian matrix values and returns them as a pandas DataFrame.
    The function supports two formats for the input line:
    1. Comma-separated values.
    2. Fixed-width values (each value is 5 characters wide, up to 3 values).
    If the line contains more than 15 characters, it is truncated to 15 characters.
    If the line contains fewer than 15 characters, it is padded with spaces.
    Parameters:
        line (str): The input string containing the Jacobian matrix data, either comma-separated or fixed-width.
        columnNames (list of str): The names of the columns (variables) for the Jacobian matrix.
    Returns:
        pandas.DataFrame: A DataFrame with one row, indexed by the provided column names, containing the parsed integer values.
    """

    # iswitch, itemp, njacob
    if len(line) > 15:
        line = line[:15]

    if "," in line:
        dataJacobianMatrix = line.split(",")
    else:
        length = len(line)
        if length < 15:
            line = line + " " * (15 - length)
        width = [5, 5, 5]
        dataJacobianMatrix = []
        l1 = 0
        for wth in width:
            l2 = l1 + wth
            dataJacobianMatrix.append(line[l1:l2])
            l1 = l2

    for idx, pa in enumerate(dataJacobianMatrix):
        pa = pa.strip()
        if len(pa) == 0:
            pa = 0
        dataJacobianMatrix[idx] = int(pa)
    dataJacobianMatrix = pd.DataFrame({"var": columnNames, "val": dataJacobianMatrix})
    dataJacobianMatrix = dataJacobianMatrix.set_index("var")

    return dataJacobianMatrix.T


def get_WritingControlVariables(line, columnNames):
    """
    Parses a line containing writing control variables and returns them as a pandas DataFrame.
    The function supports two formats for the input line:
    1. Comma-separated values.
    2. Fixed-width values (10 fields, each 5 characters wide, padded to 50 characters).
    Parameters:
        line (str): The input string containing the writing control variables, either comma-separated or fixed-width.
        columnNames (list of str): The list of column names corresponding to the variables.
    Returns:
        pandas.DataFrame: A DataFrame with a single row, indexed by the provided column names, containing the parsed integer values.
    Notes:
        - If a value is missing or empty, it is replaced with 0.
        - The DataFrame is transposed so that the variables are columns.
    """

    # nwxy,nwdim,nwti,nwnod,nwcom,nacom,nwmin,indmat,nvol,nwtv
    if len(line) > 50:
        line = line[:50]

    if "," in line:
        writingControlVariables = line.split(",")
    else:
        length = len(line)
        if length < 50:
            line = line + " " * (50 - length)
        width = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
        writingControlVariables = []
        l1 = 0
        for wth in width:
            l2 = l1 + wth
            writingControlVariables.append(line[l1:l2])
            l1 = l2

    for idx, pa in enumerate(writingControlVariables):
        pa = pa.strip()
        if len(pa) == 0:
            pa = 0
        writingControlVariables[idx] = int(pa)
    writingControlVariables = pd.DataFrame(
        {"var": columnNames, "val": writingControlVariables}
    )
    writingControlVariables = writingControlVariables.set_index("var")

    return writingControlVariables.T


def get_WritinginTime(line, nwnod):
    """
    Parses a string representing writing times for nodes and returns a list of integers.
    The function supports two input formats:
    1. Comma-separated values: If the input string contains commas, it is split into substrings using ',' as the delimiter.
    2. Fixed-width values: If the input string does not contain commas, it is assumed to be a concatenation of fixed-width (5-character) fields.
       The string is padded with spaces if its length is less than `nwnod * 5`, and then split into `nwnod` substrings of 5 characters each.
    Each substring is stripped of whitespace and converted to an integer. Empty substrings are treated as 0.
    Args:
        line (str): The input string containing writing times for nodes.
        nwnod (int): The number of nodes (used for fixed-width parsing).
    Returns:
        List[int]: A list of integers representing the writing times for each node.
    """

    if "," in line:
        nodesWritinginTime = line.split(",")
    else:
        length = len(line)
        if length < nwnod * 5:
            line = line + " " * (nwnod * 5 - length)
        nodesWritinginTime = []
        for i in range(nwnod):
            l1 = 5 * i
            l2 = 5 * (i + 1)
            nodesWritinginTime.append(line[l1:l2])

    for idx, pa in enumerate(nodesWritinginTime):
        pa = pa.strip()
        if len(pa) == 0:
            pa = 0
        nodesWritinginTime[idx] = int(pa)

    return nodesWritinginTime


## End of module

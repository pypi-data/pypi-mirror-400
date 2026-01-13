import sys, os

import numpy as np
import pandas as pd
# from utilities import ludcmp, lubksb
from scipy.optimize import curve_fit


def get_database(name_spieces,numbs, tc2,databasePath, jtemp=0):
    """
    Load and parse the chemical database file, extracting species, minerals, gases, and surface complexes.
    
    Parameters:
        name_spieces (list): List of all species names.
        numbs (list): Number of each species type (primary, complexes, minerals, etc.).
        tc2 (float): Temperature in Celsius.
        databasePath (str): Path to the database directory.
        jtemp (int, optional): Temperature flag (default: 0).
    Returns:
        tuple: Parsed database information (various DataFrames and lists).
    """

    
    namePrimarySpecies = name_spieces[:numbs[0]]
    nameAquComplexes = []
    nameMinerals = []
    nameGases = []
    nameSurfaceComplexes = []
    
    if numbs[1]>=1:
        isp = numbs[0]
        jsp = isp + numbs[1]
        nameAquComplexes = name_spieces[isp:jsp]
    if numbs[2]>=1:
        isp = numbs[0] + numbs[1]
        jsp = isp + numbs[2]
        nameMinerals = name_spieces[isp:jsp]
    if numbs[3]>=1:    
        isp = numbs[0] + numbs[1] + numbs[2]
        jsp = isp + numbs[3]
        nameGases = name_spieces[isp:jsp]

    if numbs[4]>=1:    
        isp = numbs[0] + numbs[1] + numbs[2] + numbs[3]
        jsp = isp + numbs[4]
        nameSurfaceComplexes = name_spieces[isp:jsp]




    temp = tc2
    if temp == 25.0 and jtemp == 0:
        databaseName = os.path.join(databasePath,'master25.dat')
    else:
        databaseName = os.path.join(databasePath,'masterte.dat')

    with open(databaseName) as f:
        lines = f.readlines()

    line = lines[0].strip('\n')
    try:
        ntemp = int(line.split()[2])
    except ValueError:
        raise ValueError('Something is wrong in the first line of the database')
    tempc = line.split()[3: 3 + ntemp]

    tempc = [float(pa.replace('D', 'e').replace('d', 'e')) for pa in tempc]

    nullIndxLines = []
    for idx, line in enumerate(lines):
        if 'null' in line:
            nullIndxLines.append(idx)
    assert len(nullIndxLines) == 5, "There are something wrong in the blocks of the database!!"

    ## Read Block one for primary components
    l1 = 1
    l2 = nullIndxLines[0]
    componentBlocklines = lines[l1:l2]
    primarySpecies = pd.DataFrame()
    charges = []
    ion_sizes = []
    names = []
    for line in componentBlocklines:
        line = line.strip('\n')
        dummy = line.split()
        if dummy[0] in namePrimarySpecies:
            if len(dummy) >= 3:
                names.append(dummy[0])
                charges.append(float(dummy[2]))
                ion_sizes.append(float(dummy[1]))
            else:
                raise ValueError('Something is wrong in the Chemical database!')
    primarySpeciesNDatabase = [key for key in namePrimarySpecies if key not in names]
    for key in primarySpeciesNDatabase:
        names.append(key)
        charges.append(0.0)
        ion_sizes.append(1.0)

    primarySpecies = pd.DataFrame({'primarySpecies': names, 'charge': charges, 'ionSize': ion_sizes})

    chemicalReactions = pd.DataFrame()

    # Read auqoues complexes if len(nameAquComplexes)>0
    aquComplexes = pd.DataFrame()

    if len(nameAquComplexes) > 0:
        l1 = nullIndxLines[0] + 1
        l2 = nullIndxLines[1]
        aquComplexesLines = lines[l1:l2]
        aquComplexes = get_chemicalreactions(aquComplexesLines,
                                             nameAquComplexes, namePrimarySpecies, tc2, tempc,
                                             iBlock=1)
        aquComplexes['reaction'] = ['aquComplexes'] * len(aquComplexes)

        if len(chemicalReactions) == 0:
            chemicalReactions = aquComplexes.copy()
        else:
            chemicalReactions = pd.concat([chemicalReactions, aquComplexes], axis=0)

    # Read mineral block if len(nameMinerals)>0
    #mineralStoiCoeff = pd.DataFrame()
    # mineralsDict = {}

    if len(nameMinerals) > 0:
        l1 = nullIndxLines[1] + 1
        l2 = nullIndxLines[2]
        mineralLines = lines[l1:l2]
        # mineralStoiCoeff = pd.DataFrame()
        # mineralsDict = {}
        minerals = get_chemicalreactions(mineralLines,
                                         nameMinerals, namePrimarySpecies, tc2,
                                         tempc, iBlock=2)
        minerals['reaction'] = ['mineral'] * len(minerals)
        if len(chemicalReactions) == 0:
            chemicalReactions = minerals.copy()
        else:
            chemicalReactions = pd.concat([chemicalReactions, minerals], axis=0)

    # Read gas block if len(nameGases)>0
    #gasStoiCoeff = pd.DataFrame()
    #gasesDict = {}
    if len(nameGases) > 0:
        l1 = nullIndxLines[2] + 1
        l2 = nullIndxLines[3]
        gasLines = lines[l1:l2]

        gases = get_chemicalreactions(gasLines,
                                      nameGases, namePrimarySpecies, tc2,
                                      tempc, iBlock=3)
        gases['reaction'] = ['gas'] * len(gases)

        if len(chemicalReactions) == 0:
            chemicalReactions = gases.copy()
        else:
            chemicalReactions = pd.concat([chemicalReactions, gases], axis=0)

    # Read surface adsorbed species block if len(nameSurfaceComplexes)>0

    if len(nameSurfaceComplexes) > 0:
        l1 = nullIndxLines[3] + 1
        l2 = nullIndxLines[4]
        surfaceComplexLines = lines[l1:l2]
        surfaceComplexes = get_chemicalreactions(surfaceComplexLines,
                                                 nameSurfaceComplexes, namePrimarySpecies, tc2,
                                                 tempc, iBlock=4)
        surfaceComplexes['reaction'] = ['surfaceComplexes'] * len(surfaceComplexes)

        if len(chemicalReactions) == 0:
            chemicalReactions = surfaceComplexes.copy()
        else:
            chemicalReactions = pd.concat([chemicalReactions, surfaceComplexes], axis=0)

    
    primarySpecies = primarySpecies.set_index('primarySpecies').loc[namePrimarySpecies].reset_index()
    ordered_chem_reactions = nameAquComplexes + nameMinerals + nameGases + nameSurfaceComplexes
    chemicalReactions.index.name = 'species'
    chemicalReactions = chemicalReactions.reindex(ordered_chem_reactions)

    return primarySpecies, chemicalReactions



def get_chemicalreactions(newlines, nameReactions, namePrimarySpecies, Tc, tempc, iBlock=1):
    """
    Parse chemical reaction data from database lines.

    Parameters:
        newlines (list): Lines from the database file.
        nameReactions (list): List of reaction names.
        namePrimarySpecies (list): List of primary species names.
        Tc (float): Temperature in Celsius.
        tempc (list): List of temperature points.
        iBlock (int, optional): Block type (default: 1).
    Returns:
        tuple: DataFrames for reactions, stoichiometry, logK, and parameters.
    """

    ntemp = len(tempc)
    reactions = pd.DataFrame()
    reactionStoiCoeff = pd.DataFrame()  # index=namePrimarySpecies)
    #    reactionStoiCoeff.index.name = 'primarySpecies'

    alogK0 = pd.DataFrame()  # index=[tempc])
    #    alogK0.index.name = 'temperaturePoint'
    df_b = pd.DataFrame(columns =['b1', 'b2', 'b3', 'b4', 'b5'])


    names = []
    charges = []
    ion_sizes = []
    logK = []
    molarVolum = []

    for line in newlines:
        line = line.strip('\n')
        dummy = line.split()

        if dummy[0] in nameReactions:

            stoiCoeff = dict(zip(namePrimarySpecies, [0] * len(namePrimarySpecies)))

            if iBlock == 1 or iBlock == 4:
                numberComponents = int(dummy[1])
                position = 1
            else:
                numberComponents = int(dummy[2])
                molarVolum.append(float(dummy[1]))
                position = 2

            for i in range(numberComponents):
                l1 = position + 1 + i * 2
                l2 = l1 + 1
                stoiCoeff[dummy[l2]] = float(dummy[l1])

            df = pd.DataFrame({'primarySpecies': list(stoiCoeff.keys()),
                               dummy[0]: stoiCoeff.values()})
            df = df.set_index('primarySpecies')
            if len(reactionStoiCoeff) == 0:
                reactionStoiCoeff = df.copy()
            else:
                reactionStoiCoeff = pd.concat([reactionStoiCoeff, df], axis=1)

            l = position + 1 + numberComponents * 2
            alogks = dummy[l: l + ntemp]
            alogks = [float(pa) for pa in alogks]
            df = pd.DataFrame({'temperaturePoint': tempc, dummy[0]: alogks})
            df = df.set_index('temperaturePoint')
            if len(alogK0) == 0:
                alogK0 = df.copy()
            else:
                alogK0 = pd.concat([alogK0, df], axis=1)
            if len(tempc) > 1:
                popt, _ = curve_fit(flogk, tempc, alogks)
                df_b = pd.concat([df_b, pd.DataFrame([popt], columns=['b1', 'b2', 'b3', 'b4', 'b5'])], ignore_index=True)
                alogk = flogk(Tc, popt[0], popt[1], popt[2], popt[3], popt[4])
                logK.append(alogk)
            else:
                logK.append(alogks[0])
            if iBlock == 1:
                # save the charge and ion size for aqueous complexes and charge
                l = 1 + numberComponents * 2 + ntemp + 1
                ion_sizes.append(float(dummy[l]))
                charges.append(float(dummy[l + 1]))

            if iBlock == 4:
                l = 1 + numberComponents * 2 + ntemp + 1
                charges.append(float(dummy[l]))
            names.append(dummy[0])

    if len(charges) == 0:
        charges = [0] * len(names)
    if len(molarVolum) == 0:
        molarVolum = [0] * len(names)
    if len(ion_sizes) == 0:
        ion_sizes = [0] * len(names)

    df = pd.DataFrame({'species': names, 'logK': logK, 'charge': charges,
                       'molarVolum': molarVolum, 'ionSize': ion_sizes})
    df['molarVolum'] = df['molarVolum'].astype(float)
    df['molarVolum'] = df['molarVolum']*1.0e-3 # convert from cm3/mol to dm3/mol
    df = df.set_index('species')
    reactionStoiCoeff = reactionStoiCoeff.T
    reactions = pd.concat([df, reactionStoiCoeff], axis=1)
    alogK0 = alogK0.T
    
    reactions = pd.concat([reactions, alogK0], axis=1)
    reactions = pd.concat([reactions, df_b], axis=1) 
    reactions.index.name = 'species'
    return reactions


def flogk(t, b0, b1, b2, b3, b4):
    """
    Calculate the decimal logarithm of the equilibrium constant at a given temperature.

    Parameters:
        t (float): Temperature in Celsius.
        b0, b1, b2, b3, b4 (float): Fitting parameters.
    Returns:
        float: Logarithm of the equilibrium constant.
    """
    # calculate the decimal logarithm of the equilibrium constant
    # at given temperature
    temp = t + 273.15
    return b0 * np.log(temp) + b1 + b2 * temp + b3 / temp + b4 / (temp * temp)


def get_logKSpecialElements(tc):
    """
    Get log equilibrium constants for special redox and gas reactions at a given temperature.

    Parameters:
        tc (float): Temperature in Celsius.
    Returns:
        tuple: LogK values for Eh, O2(aq), CH4, CO2, and H2.
    """
    tempc = [+0., +25., +60., +100., +150., +200., +250., +300]
    # Log equilibrium constant for the reaction 2H2O = O2(g) + 4H+ + 4e-
    alogkEh = [-91.0448, -83.1049, -74.0534, -65.8641,
               -57.8929, -51.6848, -46.7256, -42.6828]
    # Log equilibrium constant for the reaction O2(g) = O2(aq). It is used
    # to calculate logfO2, Eh, and pe from the dissolved concentration
    # of O2(aq), which is the primary species when dealing with redox.
    alogkfO2 = [-2.6567, -2.8983, -3.0633, -3.1076, -3.0354, -2.8742, -2.6488, -2.3537]
    # Log equilibrium constants for CH4, CO2, and H2 (dissociation reactions). They are used
    #  to calculate gas partial pressures according to solute concentrations.
    alogkCH4 = [155.2357, 141.2909, 125.0219,
                109.9249, 94.7907, 82.5281, 72.4209, 63.6475]
    alogkCO2 = [-7.6765, -7.8136, -8.0527, -8.3574,
                -8.7692, -9.2165, -9.7202, -10.3393]
    alogkH2 = [47.4693, 43.0017, 37.8322, 33.0786,
               28.3653, 24.6161, 21.5520, 18.9809]
    if tc != 25.0:
        popt, _ = curve_fit(flogk, tempc, alogkEh)
        logkEh = flogk(tc, popt[0], popt[1], popt[2], popt[3], popt[4])
        popt, _ = curve_fit(flogk, tempc, alogkfO2)
        logkfO2 = flogk(tc, popt[0], popt[1], popt[2], popt[3], popt[4])
        popt, _ = curve_fit(flogk, tempc, alogkCH4)
        logkCH4 = flogk(tc, popt[0], popt[1], popt[2], popt[3], popt[4])
        popt, _ = curve_fit(flogk, tempc, alogkCO2)
        logkCO2 = flogk(tc, popt[0], popt[1], popt[2], popt[3], popt[4])
        popt, _ = curve_fit(flogk, tempc, alogkH2)
        logkH2 = flogk(tc, popt[0], popt[1], popt[2], popt[3], popt[4])
    else:
        logkEh = alogkEh[1]
        logkfO2 = alogkfO2[1]
        logkCH4 = alogkCH4[1]
        logkCO2 = alogkCO2[1]
        logkH2 = alogkH2[1]
    return logkEh, logkfO2, logkCH4, logkCO2, logkH2

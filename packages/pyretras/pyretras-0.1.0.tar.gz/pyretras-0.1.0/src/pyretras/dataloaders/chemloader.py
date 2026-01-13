import sys
import os
import numpy as np
import pandas as pd

#sys.path.insert(1, os.path.abspath("."))
# from iodatabase import preprocessing_chemicalsystem
# sys.path.insert(0, os.path.abspath('../src/chemicals'))
# from src.ios.iotran import read_tra
# from chemical import initializingwaterchemistry_test


def read_chem(fname):
    """
    Reads and parses a chemical transport input file, extracting chemical species, zones, and parameters.

    Parameters:
        fname (str): Path to the chemical transport input file.

    Returns:
        dict: Dictionary with keys for all chemical categories, species, and zone data.

    Notes:
        Expects a specific file format with labeled blocks for each chemical category.
        Uses helper functions for parsing each block.
    """
    print(f"Start to read the Transport file => {fname}")
    keyword_chem = {
        "primary aqueous species": -1,
        "aqueous complexes": -1,
        "minerals": -1,
        "gases": -1,
        "surface complexes": -1,
        "exchangeable cations": -1,
        "initial and boundary water types": -1,
        "initial mineral zones": -1,
        "value of kd": -1,
        "initial gas zones": -1,
        "initial adsorption zones": -1,
        "initial cation exchange zones": -1,
    }
    # initializing the variables
    title_label = []
    tc2 = 25.0
    name_pri_species = []
    name_aqu_complexes = []
    name_minerals = []
    name_gases = []
    name_surf_complexes = []
    exchange_reactions = pd.DataFrame()
    water_zones = pd.DataFrame()
    mineral_zones = pd.DataFrame()
    xkd = 0.0
    gas_zones = pd.DataFrame()
    adsorption_zones = pd.DataFrame()
    cation_exchange_zones = pd.DataFrame()

    with open(fname, encoding="latin1") as f:
        lines = f.readlines()
    f.close()
    # Note: The first 4 lines are fixed
    title_label = lines[0:3]
    # temperature  oC
    tc2 = float(lines[3].split()[0])
    # From the 4th line, we will look into the key words
    lines = lines[4:]

    for idx, line in enumerate(lines):
        line = line.strip("\n")
        for key in keyword_chem:
            if key in line.lower():
                keyword_chem[key] = idx
                break

    for key, idx in keyword_chem.items():
        if key == "primary aqueous species":
            if idx >= 0:
                num_pri_species = int(lines[idx + 2].split()[0])
                l1 = idx + 4
                l2 = l1 + num_pri_species
                newlines = lines[l1:l2]
                # Check errors in the primary aqueous species block
                if "*" in lines[l2]:
                    name_pri_species = get_name_species(newlines)
                else:
                    raise ValueError(f"There is something wrong in the {key} block!")
        if key == "aqueous complexes":
            # Reading name of the aqueous complexes:
            if idx >= 0:
                newlines = []
                for line in lines[idx + 1 :]:
                    if "*" in line:
                        break
                    else:
                        newlines.append(line)
                name_aqu_complexes = []
                if len(newlines) > 0:
                    name_aqu_complexes = get_name_species(newlines)

        if key == "minerals":
            # Reading name of the minerals:
            if idx >= 0:
                newlines = []
                for line in lines[idx + 1 :]:
                    if "*" in line:
                        break
                    else:
                        newlines.append(line)
                name_minerals = []
                if len(newlines) > 0:
                    name_minerals = get_name_species(newlines)

        if key == "gases":
            # Reading name of the gases:
            if idx >= 0:
                newlines = []
                for line in lines[idx + 1 :]:
                    if "*" in line:
                        break
                    else:
                        newlines.append(line)
                name_gases = []
                if len(newlines) > 0:
                    name_gases = get_name_species(newlines)

        if key == "surface complexes":
            # Reading name of the surface complexes:
            if idx >= 0:
                newlines = []
                for line in lines[idx + 1 :]:
                    if "*" in line:
                        break
                    else:
                        newlines.append(line)
                name_surf_complexes = []
                if len(newlines) > 0:
                    name_surf_complexes = get_name_species(newlines)

        if key == "exchangeable cations":
            # Reading exchange reactions
            if idx >= 0:
                newlines = []
                for line in lines[idx + 2 :]:
                    if "*" in line:
                        break
                    else:
                        newlines.append(line)
                exchange_reactions = []
                if len(newlines) > 0:
                    column_names = [
                        "exchanger",
                        "ims",
                        "iex",
                        "aekx1",
                        "aekx2",
                        "aekx3",
                        "aekx4",
                    ]
                    exchange_reactions = get_exchange_reactions(newlines, column_names)

        if key == "initial and boundary water types":
            # initial and boundary water types
            if idx >= 0:
                number_waters = lines[idx + 1].strip("\n").split()[:3]
                number_waters = [int(wtype.strip()) for wtype in number_waters]
                # numberWaters for initial waters, boundary waters adn recharge waters
                l1 = idx + 2
                water_zones = pd.DataFrame()
                water_cat = ["initial", "boundary", "recharge"]
                for wc, itypes in zip(water_cat, number_waters):
                    for jtype in range(itypes):
                        newlines = []
                        nline = 0
                        for line in lines[l1:]:
                            if "*" in line:
                                l1 = l1 + nline + 1
                                break
                            else:
                                newlines.append(line)
                                nline += 1
                        water_zone = get_water_zone(newlines, name_pri_species)
                        water_zone["waterType"] = [wc] * len(water_zone)
                        water_zone["zone"] = [jtype + 1] * len(water_zone)
                        if len(water_zones) == 0:
                            water_zones = water_zone
                        else:
                            water_zones = pd.concat([water_zones, water_zone], axis=0)

        if key == "initial mineral zones":
            # initial mineral zones
            if idx >= 0 and len(name_minerals) > 0:
                line = lines[idx + 1].strip("\n")
                number_mineral_zones = line.split()[0]
                number_mineral_zones = int(number_mineral_zones)
                mineral_zones = pd.DataFrame()
                l1 = idx + 2
                newlines = []
                for j in range(number_mineral_zones):
                    nline = 0
                    for line in lines[l1:]:
                        if "*" in line:
                            l1 = l1 + nline + 1
                            break
                        else:
                            newlines.append(line)
                            nline += 1

                    zone = get_mineral_zones(newlines, name_minerals)
                    # zone['zone'] = [j+1] * len(zone)
                    if len(mineral_zones) == 0:
                        mineral_zones = zone
                    else:
                        mineral_zones = pd.concat([mineral_zones, zone], axis=0)

        if key == "value of kd":
            # initial mineral zones
            if idx >= 0:
                line = lines[idx + 1].strip("\n")
                xkd = line.split()[0]
                if xkd.isnumeric():
                    xkd = float(xkd)
                else:
                    xkd = 0.0

        if key == "initial gas zones":
            # initial gas zones
            if idx >= 0 and len(name_gases) > 0:
                line = lines[idx + 1].strip("\n")
                number_gas_zones = line.split()[0]
                number_gas_zones = int(number_gas_zones)
                gas_zones = pd.DataFrame()
                l1 = idx + 2
                newlines = []
                for j in range(number_gas_zones):
                    nline = 0
                    for line in lines[l1:]:
                        if "*" in line:
                            l1 = l1 + nline + 1
                            break
                        else:
                            newlines.append(line)
                            nline += 1

                    zone = get_gas_zones(newlines, name_gases)
                    # zone['zone'] = [j + 1] * len(zone)
                    if len(gas_zones) == 0:
                        gas_zones = zone
                    else:
                        gas_zones = pd.concat([gas_zones, zone], axis=0)

        if key == "initial adsorption zones":
            # initial adsorption zones
            if idx >= 0 and len(name_surf_complexes) > 0:
                line = lines[idx + 1].strip("\n")
                number_adsorption_zones = line.split()[0]
                number_adsorption_zones = int(number_adsorption_zones)
                adsorption_zones = pd.DataFrame()
                l1 = idx + 3
                l2 = l1 + number_adsorption_zones
                newlines = lines[l1:l2]
                adsorption_zones = get_adsorption_zones(newlines)

        if key == "initial cation exchange zones":
            # initial cation exchange zones
            if idx >= 0 and len(exchange_reactions) > 0:
                line = lines[idx + 1].strip("\n")
                number_cation_exchange_zones = line.split()[0]
                number_cation_exchange_zones = int(number_cation_exchange_zones)
                cation_exchange_zones = pd.DataFrame()
                l1 = idx + 3
                newlines = []
                number_exchangers = len(exchange_reactions)
                name_exchangers = list(exchange_reactions["exchanger"].values)
                for j in range(number_cation_exchange_zones):
                    l2 = l1 + number_exchangers + 1
                    newlines = lines[l1:l2]
                    zone = get_cation_exchange_zones(newlines, name_exchangers)
                    if len(cation_exchange_zones) == 0:
                        cation_exchange_zones = zone
                    else:
                        cation_exchange_zones = pd.concat(
                            [cation_exchange_zones, zone], axis=0
                        )

    project_chem = {
        "title": title_label,
        "temperature": tc2,
        "primary aqueous species": name_pri_species,
        "aqueous complexes": name_aqu_complexes,
        "minerals": name_minerals,
        "gases": name_gases,
        "surface complexes": name_surf_complexes,
        "exchangeable cations": exchange_reactions,
        "initial and boundary water types": water_zones,
        "initial mineral zones": mineral_zones,
        "value of kd": xkd,
        "initial gas zones": gas_zones,
        "initial adsorption zones": adsorption_zones,
        "initial cation exchange zones": cation_exchange_zones,
    }

    return project_chem


def get_name_species(newlines):
    """
    Extract the first word (species name) from each line in a list of strings.
    Parameters:
        newlines (list of str): Lines containing species information.
    Returns:
        list of str: List of species names.
    """

    name_species = []
    for line in newlines:
        line = line.strip("\n")
        name = line.split()[0]
        name_species.append(name)
    return name_species


def get_exchange_reactions(newlines, column_names):
    """
    Parse exchange reaction lines into a pandas DataFrame.
    Parameters:
        newlines (list of str): Lines representing exchange reactions.
        column_names (list of str): Column names for the DataFrame.
    Returns:
        pd.DataFrame: DataFrame of exchange reactions.
    """

    exchange_reactions = []
    for line in newlines:
        line = line.strip("\n")
        exchange_r = line.split()
        exchange_reactions.append(exchange_r)
    exchange_reactions = pd.DataFrame(exchange_reactions, columns=column_names)
    return exchange_reactions


def get_water_zone(newlines, name_primary_species):
    """
    Parse water zone composition data and return a DataFrame for all primary species.
    Parameters:
        newlines (list of str): Lines with water zone and species composition data.
        name_primary_species (list of str): List of primary species names.
    Returns:
        pd.DataFrame: DataFrame with water zone composition for each primary species.
    Raises:
        ValueError: If any species has a 'guess' value less than 0.0.
    """

    line = newlines[0].strip("\n")
    [iz, tc, itc] = line.split()[0:3]
    componentData = [1, -1.0, -1.0, " ", 0]
    water_zone_primary = dict(
        zip(name_primary_species, [componentData] * len(name_primary_species))
    )
    # from the thrid line to read the water compositions
    for line in newlines[2:]:
        line = line.strip("\n")
        composition = line.split()
        primary_species_composition = []
        if composition[0] in name_primary_species:

            numb = composition.count("'")
            if numb == 2:
                primary_species_composition = [compos for compos in composition[1:4]]
                primary_species_composition.append(" ")
                primary_species_composition.append(composition[6])
            elif composition.count("''") == 1:
                primary_species_composition = [compos for compos in composition[1:4]]
                primary_species_composition.append(" ")
                primary_species_composition.append(composition[5])
            else:
                primary_species_composition = [compos for compos in composition[1:6]]

            primary_species_composition[0] = int(primary_species_composition[0])
            primary_species_composition[4] = int(primary_species_composition[4])
            guess = primary_species_composition[1].lower()
            if "d" in guess:
                guess = guess.replace("d", "e")
            primary_species_composition[1] = float(guess)

            ctot = primary_species_composition[2].lower()
            if "d" in ctot:
                ctot = ctot.replace("d", "e")
            primary_species_composition[2] = float(ctot)

            water_zone_primary[composition[0]] = primary_species_composition

    column_names = ["icon", "guess", "ctot", "constrain", "ictot2"]
    water_zone = pd.DataFrame(water_zone_primary).T
    water_zone.columns = column_names
    water_zone.index.name = "namePrimarySpecies"
    water_zone["tc2"] = [float(tc)] * len(water_zone)
    water_zone["itc2"] = [int(itc)] * len(water_zone)
    water_zone["zone"] = [int(iz)] * len(water_zone)
    if (water_zone["guess"] < 0.0).any():
        raise ValueError(f"There are some issues in the water zone {iz}!\n{water_zone[water_zone['guess'] < 0.0]}")

    return water_zone


def get_mineral_zones(newlines, name_minerals):
    """
    Parse mineral zone data and return a DataFrame with mineral information for each zone.
    Parameters:
        newlines (list of str): Lines with mineral zone data.
        name_minerals (list of str): List of mineral names.
    Returns:
        pd.DataFrame: DataFrame with mineral zone data.
    Raises:
        ValueError: If any mineral has an initial volume less than 0.0.
    """

    # from third line to look for the minerals

    component_data = [-1.0, 0]
    mineral_zone = dict(zip(name_minerals, [component_data] * len(name_minerals)))
    iz = newlines[0].strip("\n").split()[0]
    iz = int(iz)
    for line in newlines[2:]:
        line = line.strip("\n")
        dummy = line.split()
        mineral = []
        if dummy[0] in name_minerals:
            if len(dummy) <= 2:
                mineral = [dum for dum in dummy[1:2]]
                mineral.append(0)
            else:
                mineral = [dum for dum in dummy[1:3]]

            mineral = [float(m) for m in mineral]
            mineral_zone[dummy[0]] = mineral
    column_name = ["initial vol", "surface area"]
    mineral_zone = pd.DataFrame(mineral_zone).T  # , columns=columnName)
    mineral_zone.columns = column_name
    mineral_zone.index.name = "mineral"
    mineral_zone["zone"] = [iz] * len(mineral_zone)
    if (mineral_zone["initial vol"] < 0.0).any():
        raise ValueError(f"There are some issues in the mineral zone {iz}!\n{mineral_zone[mineral_zone['initial vol'] < 0.0]}")

    return mineral_zone


def get_gas_zones(newlines, name_gases):
    """
    Parse gas zone data and return a DataFrame with partial pressures for each gas.
    Parameters:
        newlines (list of str): Lines with gas zone data.
        name_gases (list of str): List of gas names.
    Returns:
        pd.DataFrame: DataFrame with gas zone data.
    Raises:
        ValueError: If any gas has a negative partial pressure.
    """

    # from third line to look for the minerals
    gas_zone = dict(zip(name_gases, [-1] * len(name_gases)))
    iz = int(newlines[0].strip()[0])
    # gasZone = []
    for line in newlines[2:]:
        line = line.strip("\n")
        dummy = line.split()
        gas = []
        if dummy[0] in name_gases:
            gas = [dum for dum in dummy[:2]]

        gasPressure = [float(gas[1])]
        gas_zone[dummy[0]] = gasPressure
    column_name = ["partial pressure"]
    gas_zone = pd.DataFrame(gas_zone).T  # , columns=columnName)
    gas_zone.columns = column_name
    gas_zone["zone"] = [iz] * len(gas_zone)

    gas_zone.index.name = "gas"
    if (gas_zone["partial pressure"] < 0.0).any():
        raise ValueError(f"There are some issues in the gas zone {iz}!\n{gas_zone[gas_zone['partial pressure'] < 0.0]}")
    return gas_zone


def get_adsorption_zones(newlines):
    """
    Parse adsorption zone data and return a DataFrame with zone and adsorption parameters.
    Parameters:
        newlines (list of str): Lines with adsorption zone data.
    Returns:
        pd.DataFrame: DataFrame with adsorption zone data.
    """
    adsorption_zone = []
    for line in newlines:
        line = line.strip("\n")
        temp = line.split()
        for jdx, pa in enumerate(temp[:3]):
            if jdx == 0:
                temp[jdx] = int(pa)
            else:
                pa = pa.lower()
                if "d" in pa:
                    pa = pa.replace("d", "e")
                temp[jdx] = float(pa)

        adsorption_zone.append(temp[:3])
    column_names = ["zone", "sadsdum", "tads2"]
    adsorption_zone = pd.DataFrame(adsorption_zone, columns=column_names)

    return adsorption_zone


def get_cation_exchange_zones(newlines, name_exchangers):
    """
    Parse cation exchanger zone data and return a DataFrame with exchanger capacities and zone info.
    Parameters:
        newlines (list of str): Lines with cation exchanger data.
        name_exchangers (list of str): List of exchanger names.
    Returns:
        pd.DataFrame: DataFrame with cation exchanger zone data.
    Raises:
        ValueError: If any exchanger has a negative exchange capacity.
    """

    exchanger_zone = dict(zip(name_exchangers, [-1] * len(name_exchangers)))
    iz = int(newlines[0].strip()[0])

    for line in newlines[1:]:
        line = line.strip("\n")
        dummy = line.split()
        if dummy[0] in name_exchangers:

            ceca = [float(dummy[1])]
            exchanger_zone[dummy[0]] = ceca
    column_name = ["ex capacity"]
    exchanger_zone = pd.DataFrame(exchanger_zone).T  # , columns=columnName)
    exchanger_zone.columns = column_name
    exchanger_zone["zone"] = [iz] * len(exchanger_zone)

    exchanger_zone.index.name = "exchanger"
    if (exchanger_zone["ex capacity"] < 0.0).any():
        raise ValueError(f"There are some issues in the exchanger capacity zone {iz}!\n{exchanger_zone[exchanger_zone['ex capacity'] < 0.0]}")

    return exchanger_zone

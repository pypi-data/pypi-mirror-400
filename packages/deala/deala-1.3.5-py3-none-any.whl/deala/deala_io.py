import pandas as pd
import numpy as np
from scipy.stats import linregress
import os
from os import walk
import json
import brightway2 as bw
from tqdm import tqdm
import math
from deala import *
import uuid
from premise import *
from constructive_geometries import *
import bw2analyzer as bwa
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import sqlite3
import pickle
from tqdm import tqdm
import toml
import time
import gc
import pycountry
from bw2data import mapping
import re
import hashlib




# ============================================================
# Main class for DEALA I/O logic
# ============================================================




class deala_io:
    def __init__(self):
        self.bw2 = bw
        self.pd = pd
        self.os = os
        self.json = json
        self.tqdm = tqdm
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Creation of a new database in the Python project
    def create_DB(self, name):
        """Create a new Brightway2 database.
        Parameters:
        - name: The name of the database to create.
        """

        if name in bw.databases:
            print(name + ' ' + 'is already included')
        else:
            db = bw.Database(name)
            db.register()
            return bw.Database(name)
    
    # Setup function to import marketsphere database and DEALA methods
    def deala_setup(self, overwrite=False):
        """
        Imports the 'marketsphere' database and DEALA impact assessment categories database.

        - If 'marketsphere' is already imported and overwrite is False, it prints a message and returns.
        - If 'marketsphere' is already imported and overwrite is True, it deletes the existing database and imports the new one.
        - Loads data from 'marketsphere.json' and allocates it to the 'marketsphere' database.
        - Imports DEALA impact assessment methods from 'DEALA.json'.
        - Sets the unit for the methods to "USD2023".
        """
        if "marketsphere" in bw.databases:
            if overwrite:
                del bw.databases["marketsphere"]
                print("The existing marketsphere database has been deleted.")
            else:
                print("The marketsphere database is already imported.")
                return

        # Define the 'marketsphere' database
        mdb = bw.Database('marketsphere')

        # Load data from 'marketsphere.json'
        # Construct the file path
        base_path = os.path.dirname(os.path.abspath(__file__))
        fp = os.path.join(base_path, "files", "characterization_models", "marketsphere.json")
        with open(fp) as f:
            data = json.load(f)

        # Allocate data and store it in the 'marketsphere' database
        mdb_data = {
            (dataset["database"], dataset["code"]): {
                "categories": (dataset["compartment"], dataset["subcompartment"]),
                "name": dataset["name"],
                "database": dataset["database"],
                "exchanges": [],
                "unit": dataset["unit"],
                "type": "biosphere"
            }
            for dataset in data
        }

        mdb.write(mdb_data)

         # Import DEALA Impact Assessment methods
        fp = os.path.join(base_path, "files", "characterization_models","DEALA.json")
        with open(fp) as f:
            data = json.load(f)

        methods = list(set(dataset['category'] + " " + dataset['method'] for dataset in data))

        for method in tqdm(methods):
            cfs=[]
            for datasets in data:
                if datasets["category"] in method and datasets["method"] in method:
                    m=bw.Method((datasets["method"],datasets["category"],datasets["indicator"]))
                    if m.name not in bw.methods: m.register()
                    bw.methods[m.name]['unit']="USD2023"
                    bw.methods.flush()
                    cf = ((datasets["database"], datasets["code"]),datasets["CF"])
                    cfs.append(cf)
            m.write(cfs)

        print('The marketsphere database and DEALA impact assessment methods are successfully imported.')

    # Defintion to create new activities in the database (DEALA acitivities)
    def new_DEALA_activity(self, database_name, name, reference_product, unit, category, location, comment, code1):
        """
        Create a new deala activity in a specified Brightway2 database.

        This function generates a new deala activity with the provided attributes and saves it to the specified database.
        It also creates a production exchange for the activity, ensuring it is properly linked within the database.

        Args:
            database_name (str): The name of the Brightway2 database where the activity will be created.
            name (str): The name of the activity.
            reference_product (str): The reference product associated with the activity.
            unit (str): The unit of measurement for the activity.
            category (list): A list of categories describing the activity.
            location (str): The geographical location of the activity.
            comment (str): A comment or description for the activity.
            code1 (str): A unique hexadecimal code to identify the activity.

        Returns:
            bw.Activity: The newly created activity object.

        Note:
            - The function assumes that the Brightway2 library (`bw`) is properly initialized and the database exists.
            - The `code1` parameter must be unique within the database to avoid conflicts.
        """
        data = {
            "name": name, "reference product": reference_product, "unit": unit, "categories": category, "location": location,
            "type": "process", "comment": comment
        }
        new_act = bw.Database(database_name).new_activity(
            code=code1, #gives each activity a hexa code
            **data
            )
        new_act.save()
        production_exchange = new_act.new_exchange(
            input=new_act, amount=1, type="production"
        )
        production_exchange.save()
        return new_act
    
    # Defintion to create new activities in the database (main acitivities)
    def new_activity(self, database_name, name, reference_product, unit, category, location):
        """
        Create a new activity in the specified Brightway2 database.

        This function generates a new activity with the provided attributes and saves it to the specified database.
        It also creates and saves a production exchange for the activity.

        Args:
            database_name (str): The name of the Brightway2 database where the activity will be created.
            name (str): The name of the activity.
            reference_product (str): The reference product associated with the activity.
            unit (str): The unit of measurement for the activity.
            category (str): The category or categories associated with the activity.
            location (str): The geographical location of the activity.

        Returns:
            bw.Activity: The newly created activity object.

        Notes:
            - Each activity is assigned a unique hexadecimal code using `uuid.uuid4().hex`.
            - A production exchange with an amount of 1 is automatically created and linked to the activity.
        """
        data = {
            "name": name, "reference product": reference_product, "unit": unit, "categories": category, "location": location,
            "type": "process"
        }
        new_act = bw.Database(database_name).new_activity(
            code=uuid.uuid4().hex, #gives each activity a hexa code
            **data
            )
        new_act.save()
        production_exchange = new_act.new_exchange(
            input=new_act, amount=1, type="production"
        )
        production_exchange.save()
        return new_act



    def compute_growth_rate(self, years, values, method="geo"):
        """
        Compute annual growth rate r from historical deflator data.
        
        Parameters:
        - years: list of int (years)
        - values: list of float (deflator values corresponding to years)
        - method: 'geo' for geometric mean, 'reg' for regression
        
        Returns:
        - r: annual growth rate (decimal, e.g., 0.03 for 3%)
        """
        if len(years) < 2:
            raise ValueError("Need at least two data points to compute growth rate.")

        if method == "geo":
            growth_rates = []
            for i in range(1, len(values)):
                yr_diff = years[i] - years[i-1]
                rate = (values[i] / values[i-1]) ** (1 / yr_diff) - 1
                growth_rates.append(rate)
            r = np.mean(growth_rates)
        elif method == "reg":
            # Linear regression on log(values) ~ years
            log_vals = np.log(values)
            slope, intercept, _, _, _ = linregress(years, log_vals)
            r = np.exp(slope) - 1
        else:
            raise ValueError("Method must be 'geo' or 'reg'")
        return r

    def normalize_and_extend_deflators(self, json_data, base_year=2023, extend_to_year=2030, method="geo"):
        """
        Normalize deflator series to base_year and extend to extend_to_year using growth rate from method.
        
        Parameters:
        - json_data: list of dicts, each with years as keys and deflator values
        - base_year: int, year to normalize deflators to (default 2023)
        - extend_to_year: int, last year to extrapolate deflator values to
        - method: "geo" or "reg" for growth rate calculation
        
        Returns:
        - extended_normalized_data: list of dicts with normalized and extended deflators
        """
        extended_data = []

        for entry in json_data:
            # Separate metadata and year data
            meta_keys = {k: v for k, v in entry.items() if not k.isdigit()}
            year_values = {}
            for k, v in entry.items():
                if k.isdigit() and v is not None:
                    try:
                        val = float(v)
                        if not np.isnan(val):
                            year_values[int(k)] = val
                    except:
                        pass
            
            # Check base_year presence
            base_val = year_values.get(base_year)
            if base_val is None or base_val == 0:
                print(f"Warning: Base year {base_year} missing or zero for country {entry.get('ISO-3166-1 ALPHA-2', 'Unknown')}. Skipping normalization and extension.")
                extended_data.append(entry)
                continue

            # Normalize existing years by base_val
            normalized_year_values = {year: val / base_val for year, val in year_values.items()}

            # Prepare data for growth calculation (only years <= base_year)
            # Or you might want all available years before base_year; adapt as needed
            historical_years = sorted([y for y in normalized_year_values if y <= base_year])
            historical_values = [normalized_year_values[y] for y in historical_years]

            # If not enough data to compute growth rate, skip extrapolation
            if len(historical_years) < 2:
                # Just keep normalized years, no extension
                extended_year_values = normalized_year_values.copy()
            else:
                # Compute growth rate r
                r = self.compute_growth_rate(historical_years, historical_values, method=method)

                # Extend series to extend_to_year
                extended_year_values = normalized_year_values.copy()
                last_known_year = max(normalized_year_values.keys())
                
                for year in range(last_known_year + 1, extend_to_year + 1):
                    years_ahead = year - base_year
                    # Extrapolate using (1 + r)^years_ahead, base_year normalized to 1
                    extended_year_values[year] = (1 + r) ** years_ahead
            
            # Convert keys back to str for consistency
            extended_year_values_str = {str(k): v for k, v in extended_year_values.items()}
            extended_entry = {**meta_keys, **extended_year_values_str}
            extended_data.append(extended_entry)

        return extended_data


    # --- Example usage ---

    # Suppose you have your JSON data loaded in variable `json_data`

    # extended_normalized = normalize_and_extend_deflators(
    #     json_data,
    #     base_year=2023,
    #     extend_to_year=2030,
    #     method="geo"  # or "reg"
    # )

    # print(extended_normalized)

    


    def import_DEALA_activities_fast(
        self,
        base_year,
        dict_scenarios,
        repository_main_path,
        method_calc_r="geo",
        price_calculation="nominal",
        modus=None,
        Overwrite=True
    ):
        """
        Fast import of DEALA activities into Brightway2 databases with GDP deflator adjustment.
        Parameters:
        - base_year: int, the base year for deflator normalization
        - dict_scenarios: dict, mapping scenario names to their last year (e.g., {'SSP2': 2050})
        - repository_main_path: str, path to the main repository containing data files
        - method_calc_r: str, method for growth rate calculation ('geo' or 'reg')
        - price_calculation: str, type of price calculation ('nominal' or 'real')
        - modus: str or None, if specified, only load activities for this modus
        - Overwrite: bool, if True, overwrite existing DEALA databases
        """

        # === Load GDP data ===
        fp_gdp = os.path.join(repository_main_path, "files", "GDP")
        lst_filepath = [
            os.path.join(dirpath, f)
            for (dirpath, _, filenames) in os.walk(fp_gdp)
            for f in filenames
        ]
        dict_gdp = {}
        for file in lst_filepath:
            filename = os.path.basename(file)
            for key in dict_scenarios.keys():
                if os.path.splitext(filename)[0] in key:
                    df = pd.read_excel(file)
                    dict_gdp[key] = df

        # === Load activity files ===
        if modus is None:
            fp = os.path.join(repository_main_path, "files", "DEALA_activities")
            lst_file_names = next(os.walk(fp), (None, None, []))[2]
            if '.DS_Store' in lst_file_names:
                lst_file_names.remove('.DS_Store')
        else:
            fp = os.path.join(repository_main_path, "files", "DEALA_activities")
            lst_file_names = [modus + '.json']

        # === Load deflator & elasticity data ===
        deflator_path = os.path.join(repository_main_path, "Files", "GDP", "gdp_deflator.json")
        elasticity_path = os.path.join(repository_main_path, "Files", "GDP", "elasticity.json")

        data_deflator = json.load(open(deflator_path))
        data_elasticity = json.load(open(elasticity_path))

        # === Normalize deflator data ===
        for scenario in dict_scenarios:
            last_year = dict_scenarios[scenario]
        extended_normalized = self.normalize_and_extend_deflators(
            data_deflator,
            base_year=base_year,
            extend_to_year=last_year,
            method=method_calc_r
        )

        # === Delete existing DEALA DBs if Overwrite ===
        if Overwrite:
            for database in list(bw.databases):
                if 'DEALA' in database:
                    del bw.databases[database]

        countries_deflator = {entry['ISO-3166-1 ALPHA-2'] for entry in data_deflator}
        countries_elasticity = {entry['ISO-3166-1 ALPHA-2'] for entry in data_elasticity}

        # === Process each scenario ===
        for scenario in dict_scenarios:
            print(f"[INFO] Processing scenario: {scenario}")
            db_name = f"DEALA_activities_{scenario}"
            db = bw.Database(db_name)
            db.register()

            data_to_write = {}
            total_datasets = 0
            skipped_elasticity = skipped_deflator = skipped_gdp = skipped_marketsphere = written = 0

            # === Iterate over each activity file ===
            for file in tqdm(lst_file_names, desc=f"Files for {scenario}"):
                data = json.load(open(os.path.join(fp, file)))

                for dataset in tqdm(data, desc=f"Datasets in {file}", leave=False):
                    total_datasets += 1

                    # --- Elasticity matching ---
                    elasticity_value = None
                    location = dataset.get('ISO-3166-1 ALPHA-2', 'GLO')
                    sector_ds = dataset['Sector'].strip().lower()
                    type_ds = dataset['Type'].strip().lower()

                    matches = [
                        e for e in data_elasticity
                        if e['Sector'].strip().lower() == sector_ds
                        and any(
                            token.strip(' ,').lower() in type_ds
                            for token in e['Type'].replace(',', ' ').split()
                            if token.strip()
                        )
                        and e['ISO-3166-1 ALPHA-2'] == location
                    ]
                    if not matches:
                        matches = [
                            e for e in data_elasticity
                            if e['Sector'].strip().lower() == sector_ds
                            and any(
                                token.strip(' ,').lower() in type_ds
                                for token in e['Type'].replace(',', ' ').split()
                                if token.strip()
                            )
                            and e['ISO-3166-1 ALPHA-2'] == 'GLO'
                        ]

                    if matches:
                        elasticity_value = matches[0]['Elasticity (long run)']
                    else:
                        skipped_elasticity += 1
                        continue

                    # --- Price calculation ---
                    base_price_nominal = dataset['Costs per unit [USD/unit]']
                    location = dataset['ISO-3166-1 ALPHA-2'] if dataset['ISO-3166-1 ALPHA-2'] in countries_deflator else "GLO"
                    amount = None
                    for deflator in extended_normalized:
                        if (
                            str(dict_scenarios[scenario]) in deflator
                            and location == deflator['ISO-3166-1 ALPHA-2']
                            and elasticity_value is not None
                        ):
                            try:
                                deflator_factor = deflator[str(base_year)] / deflator[str(dataset['Base Year'])]
                                base_price_real = base_price_nominal * deflator_factor

                                df_gdp = dict_gdp[scenario].set_index('ISO Code')
                                gdp_tgt = df_gdp.at[dataset['REMIND Region'], int(dict_scenarios[scenario])]
                                gdp_base = df_gdp.at[dataset['REMIND Region'], int(dataset['Base Year'])]

                                projected_price_real = base_price_real * (gdp_tgt / gdp_base) ** elasticity_value

                                if price_calculation == "real":
                                    amount = projected_price_real
                                elif price_calculation == "nominal":
                                    inflation_factor = deflator[str(dict_scenarios[scenario])] / deflator[str(base_year)]
                                    amount = projected_price_real * inflation_factor
                            except KeyError:
                                skipped_gdp += 1
                                amount = None
                                break
                            except Exception:
                                skipped_deflator += 1
                                amount = None
                                break

                    if amount is None:
                        continue

                    dataset.update({scenario: amount})

                    # --- Build activity definitions for batch write ---
                    found_market = False
                    if dataset['Years'] > 0:
                        list_years = [f"{i} years" for i in range(1, dataset['Years'] + 1)]
                        for act in bw.Database('marketsphere'):
                            if act['categories'][0] == dataset['Identifier'] and act['categories'][1] in list_years:
                                found_market = True
                                act_name = f"{dataset['Identifier']} - {dataset['Type']} - {act['categories'][1]}"
                                act_code_clean = f"{dataset['Code']}_{act['categories'][1]}".replace(" ", "_")
                                key = (db_name, act_code_clean)
                                data_to_write[key] = {
                                    'name': act_name,
                                    'unit': dataset['Unit'],
                                    'location': dataset['ISO-3166-1 ALPHA-2'],
                                    'reference product': dataset['Type'],
                                    'code': act_code_clean,
                                    'database': db_name,
                                    'type': 'process',
                                    'exchanges': [
                                        {'input': act.key, 'amount': dataset[scenario], 'type': 'biosphere'},
                                        {'input': (db_name, act_code_clean), 'amount': 1.0, 'type': 'production'}
                                    ]
                                }
                                written += 1
                    else:
                        for act in bw.Database('marketsphere'):
                            if act['categories'][0] == dataset['Identifier']:
                                found_market = True
                                act_name = f"{dataset['Identifier']} - {dataset['Type']}"
                                act_code_clean = str(dataset["Code"]).replace(" ", "_")
                                key = (db_name, act_code_clean)
                                data_to_write[key] = {
                                    'name': act_name,
                                    'unit': dataset['Unit'],
                                    'location': dataset['ISO-3166-1 ALPHA-2'],
                                    'reference product': dataset['Type'],
                                    'code': act_code_clean,
                                    'database': db_name,
                                    'type': 'process',
                                    'exchanges': [
                                        {'input': act.key, 'amount': dataset[scenario], 'type': 'biosphere'},
                                        {'input': (db_name, act_code_clean), 'amount': 1.0, 'type': 'production'}
                                    ]
                                }
                                written += 1

                    if not found_market:
                        skipped_marketsphere += 1

            # === Batch write once per scenario ===
            print(f"[INFO] Writing {len(data_to_write)} activities to database {db_name} ...")
            db.write(data_to_write)
            print(f"[INFO] Finished writing {db_name}")

            # === Debug summary ===
            print(f"\n[DEBUG] Scenario {scenario}:")
            print(f"  Total datasets read:        {total_datasets}")
            print(f"  Skipped (elasticity):       {skipped_elasticity}")
            print(f"  Skipped (deflator):         {skipped_deflator}")
            print(f"  Skipped (GDP missing):      {skipped_gdp}")
            print(f"  Skipped (marketsphere):     {skipped_marketsphere}")
            print(f"  Successfully prepared:      {written}")
            print(f"  --> Written to DB:          {len(data_to_write)}\n")


    def import_DEALA_activities(self, base_year, dict_scenarios, repository_main_path,
                            method_calc_r="geo", price_calculation="nominal",
                            modus=None, Overwrite=True):
        """
        Imports DEALA activities from data files, calculates adjusted costs based on scenarios, 
        and creates or updates activities in the Brightway2 database.

        This function processes data files containing DEALA activities, calculates adjusted costs 
        for each scenario using GDP deflator and elasticity data, and creates or updates activities 
        in the respective Brightway2 databases. It also handles multi-year activities and ensures 
        proper linking with the 'marketsphere' database.

        Args:
            base_year (int): The base year for normalization of costs.
            dict_scenarios (dict): Dictionary mapping scenario names to their corresponding years.
            repository_main_path (str): Path to the main repository containing required files.
            method_calc_r (str): Method to calculate growth rate, either "geo" for geometric mean or "reg" for regression.
            price_calculation (str): Method for price calculation, either "nominal" for nominal prices or "real" for real prices.
            modus (str, optional): Specific mode (e.g., transport) or subdirectory to load files from. Defaults to None.
            Overwrite (bool): If True, existing databases with the same name will be overwritten. Defaults to True.

        Returns:
            None
        """

        # === Load all GDP data for the defined scenarios ===
        fp = os.path.join(repository_main_path, "files", "GDP")
        lst_file_names = next(os.walk(fp), (None, None, []))[2]  # [] if no file
        lst_filepath = [os.path.join(dirpath, f)
                        for (dirpath, dirnames, filenames) in os.walk(fp)
                        for f in filenames]

        dict_gdp = {}
        for file in lst_filepath:
            filename = os.path.basename(file)
            for key in dict_scenarios.keys():
                if os.path.splitext(filename)[0] in key:
                    df = pd.read_excel(file)
                    dict_gdp[key] = df

        list_databases = []

        # === Store all files in list including data to create DEALA activities ===
        if modus is None:
            fp = os.path.join(repository_main_path, "files", "DEALA_activities")
            lst_file_names = next(walk(fp), (None, None, []))[2]
            if '.DS_Store' in lst_file_names:
                lst_file_names.remove('.DS_Store')
        else:
            # add online file (module) to list. It is one json file
            fp = os.path.join(repository_main_path, "files", "DEALA_activities")
            lst_file_names = [modus + '.json']

        # === Load the deflator and elasticity data ===
        deflator_path = os.path.join(repository_main_path, "Files", "GDP", "gdp_deflator.json")
        elasticity_path = os.path.join(repository_main_path, "Files", "GDP", "elasticity.json")

        data_deflator = json.load(open(deflator_path))
        data_elasticity = json.load(open(elasticity_path))

        # === Normalize and extend the deflator and elasticity data ===
        for scenario in dict_scenarios:
            last_year = dict_scenarios[scenario]
        extended_normalized = self.normalize_and_extend_deflators(
            data_deflator,
            base_year=base_year,
            extend_to_year=last_year,
            method=method_calc_r  # "geo" or "reg"
        )

        # === Step 1: Retrieve a list of existing databases ===
        for database in bw.databases:
            list_databases.append(database)

        # === Step 2: Delete databases containing 'DEALA' if Overwrite ===
        for database in list_databases:
            if 'DEALA' in database and Overwrite:
                del bw.databases[database]

        # === Get a set of countries from the data_deflator list ===
        countries_deflator = {entry['ISO-3166-1 ALPHA-2'] for entry in data_deflator}
        countries_elasticity = {entry['ISO-3166-1 ALPHA-2'] for entry in data_elasticity}

        # === Loop over each scenario ===
        for scenario in dict_scenarios:
            # Register a new database for the given scenario
            db = bw.Database('DEALA_activities_' + scenario)
            db.register()

            # Loop over each file in the list of file names
            elasticity_value = None
            for file in tqdm(lst_file_names):
                # Load the data from the current file
                data = json.load(open(fp + "/" + file))

                # Loop over each dataset in the loaded data
                for dataset in tqdm(data):
                    if dataset['ISO-3166-1 ALPHA-2'] in countries_elasticity:
                        location = dataset['ISO-3166-1 ALPHA-2']
                    else:
                        location = "GLO"

                    for elasticity in data_elasticity:
                        if (
                            dataset['Sector'] == elasticity['Sector']
                            and elasticity['Type'] in dataset['Type']
                            and dataset['ISO-3166-1 ALPHA-2'] == location
                        ):
                            elasticity_value = elasticity['Elasticity (long run)']

                    # check if real or nominal price calculation is used
                    if elasticity_value is None:
                        continue
                    elif price_calculation in ["real", "nominal"]:
                        # Apply real price adjustments
                        base_price_nominal = dataset['Costs per unit [USD/unit]']
                        if dataset['ISO-3166-1 ALPHA-2'] in countries_deflator:
                            location = dataset['ISO-3166-1 ALPHA-2']
                        else:
                            location = "GLO"
                        for deflator in extended_normalized:
                            if (str(dict_scenarios[scenario]) in deflator
                                and location == deflator['ISO-3166-1 ALPHA-2']
                                and elasticity_value is not None):
                                deflator_factor = deflator[str(base_year)] / deflator[str(dataset['Base Year'])]
                                base_price_real = base_price_nominal * deflator_factor
                                # project prices
                                projected_price_real = base_price_real * (
                                    dict_gdp[scenario].set_index('ISO Code').at[
                                        dataset['REMIND Region'], int(dict_scenarios[scenario])
                                    ] / dict_gdp[scenario].set_index('ISO Code').at[
                                        dataset['REMIND Region'], int(dataset['Base Year'])
                                    ]
                                ) ** elasticity_value

                                if price_calculation == "real":
                                    amount = projected_price_real
                                elif price_calculation == "nominal":
                                    inflation_factor = deflator[str(dict_scenarios[scenario])] / deflator[str(base_year)]
                                    amount = projected_price_real * inflation_factor
                    elif price_calculation not in ["real", "nominal"]:
                        raise ValueError(f"Unexpected price calculation type: {price_calculation}")

                    # Update the dataset with the calculated amount for the scenario
                    dataset.update({scenario: amount})

                    # If the dataset includes years, create respective activities for each year
                    if dataset['Years'] > 0:
                        list_years = []
                        for i in range(1, dataset['Years'] + 1):
                            list_years.append(str(i) + " years")

                        # Loop over the "marketsphere" database to create or update activities
                        for act in bw.Database('marketsphere'):
                            if act['categories'][0] == dataset['Identifier'] and act['categories'][1] in list_years:
                                act_new = self.new_DEALA_activity(
                                    db.name,
                                    dataset['Identifier'] + ' - ' + dataset['Type'] + ' - ' + act['categories'][1],
                                    dataset['Type'],
                                    dataset['Unit'],
                                    dataset['Identifier'],
                                    dataset['ISO-3166-1 ALPHA-2'],
                                    dataset['Description'],
                                    dataset['Code'] + act['categories'][1]
                                )
                                act_new.new_exchange(input=act.key, amount=dataset[scenario], type='biosphere').save()
                    else:
                        # If no years are considered, create or update a single activity
                        for act in bw.Database('marketsphere'):
                            if act['categories'][0] == dataset['Identifier']:
                                act_new = self.new_DEALA_activity(
                                    db.name,
                                    dataset['Identifier'] + ' - ' + dataset['Type'],
                                    dataset['Type'],
                                    dataset['Unit'],
                                    dataset['Identifier'],
                                    dataset['ISO-3166-1 ALPHA-2'],
                                    dataset['Description'],
                                    dataset['Code']
                                )
                                act_new.new_exchange(input=act.key, amount=dataset[scenario], type='biosphere').save()


            # Create DEALA activities in the respective databases for the defined scenarios
    def create_default_DEALA_activities(self, name_DB, dict_scenarios):
        """
        Creates DEALA activities in separate databases based on defined scenarios.

        Args:
            name_DB (str): The base name for the databases.
            dict_scenarios (dict): A dictionary containing scenario names as keys.
            dict_activities (dict): A dictionary containing activity names as keys and associated information.

        Returns:
            None
        """
        # definition of remaining deala activities to represent remaining impact categories as dict. The value represents the years to be considered. The value is 0 if no values have to be considered
        dict_activities={
            'administration':['administration', 0],
            'insurance':['insurance', 0],
            'depreciation (linear) - machinery and equipment':['machinery and equipment', 50],
            'maintenance and repair':['maintenance and repair', 0],
            'interest (internal)':['interest', 0],
            'interest (external)':['interest', 0],
            'taxes':['taxes', 0],
            'research and development':['research and development', 0],
            'warranty':['warranty', 0],
            'subsidies (linear)':['subsidies', 50],
            'capital expenditures':['capital expenditures', 0],
            'capital-dependent subsidies':['subsidies', 0]

            }

        # For each scenario, a separate database is created
        for scenario in dict_scenarios:
            self.create_DB(name_DB + scenario)
            DB = bw.Database(name_DB + scenario)
            for activity in tqdm(dict_activities):
                if dict_activities[activity][1] > 0:
                    list_years = []
                    for i in range(0, dict_activities[activity][1] + 1, 1):
                        list_years.append(str(i) + " years")
                    for act in bw.Database('marketsphere'):
                        if act['categories'][0] in activity and act['categories'][1] in list_years:
                            act_new = self.new_activity(DB.name, activity + ' - ' + act['categories'][1], act['name'], 'USD', dict_activities[activity][0], 'GLO')
                            act_new.new_exchange(input=act.key, amount=1, type='biosphere').save()
                else:
                    for act in bw.Database('marketsphere'):
                        if act['categories'][0] in activity:
                            act_new = self.new_activity(DB.name, activity + ' - ' + act['categories'][1], act['name'], 'USD', dict_activities[activity][0], 'GLO')
                            act_new.new_exchange(input=act.key, amount=1, type='biosphere').save()

  
    def create_default_DEALA_activities_fast(
            self,
            name_DB: str,
            dict_scenarios: dict,
            overwrite: bool = False,
        ):
        """
        Fast creation of default DEALA activities directly into Brightway SQLite backend.
        Args:
            name_DB (str): Base name for the DEALA databases, e.g. 'DEALA_activities_'
            dict_scenarios (dict): Scenario names and corresponding metadata
            overwrite (bool): If True, deletes existing databases first
        """

        # --- Local Brightway-safe exchange fixer (no external dependency) ---
        def fix_exchanges_for_index(exchanges, output_db, output_code):
            """
            Ensure all exchanges have 'output', 'type', and numeric 'amount',
            so Brightway's index (and bw.copy) will see them correctly.
            """
            fixed = []
            for ex in exchanges:
                ex_new = ex.copy()
                ex_new["output"] = (output_db, output_code)
                ex_new["type"] = ex_new.get("type", "technosphere")
                ex_new["amount"] = float(ex_new.get("amount", 0.0))
                fixed.append(ex_new)
            return fixed

        # === 1️⃣ Check Brightway path ===
        project_path = bw.projects.dir
        db_path_main = os.path.join(project_path, "lci", "databases.db")
        if not os.path.exists(db_path_main):
            raise FileNotFoundError(f"databases.db not found: {db_path_main}")

        # === 2️⃣ Load Marketsphere ===
        market_db = bw.Database("marketsphere")

        # === 3️⃣ Define default DEALA activities ===
        dict_activities = {
            'administration': ['administration', 0],
            'insurance': ['insurance', 0],
            'depreciation (linear) - machinery and equipment': ['depreciation (linear)', 50],
            'maintenance and repair': ['maintenance and repair', 0],
            'interest (internal)': ['interest', 0],
            'interest (external)': ['interest', 0],
            'taxes': ['taxes', 0],
            'research and development': ['research and development', 0],
            'warranty': ['warranty', 0],
            'subsidies (linear)': ['subsidies', 50],
            'capital expenditures': ['capital expenditures', 0],
            'capital-dependent subsidies': ['subsidies', 0],
        }

        # === 4️⃣ Helper: create stable codes ===
        def generate_code(db_name, act_name, flow_name):
            base = f"{db_name}_{act_name}_{flow_name}_GLO"
            return hashlib.md5(base.encode("utf-8")).hexdigest()

        # === 5️⃣ Overwrite optional ===
        if overwrite:
            for db in list(bw.databases):
                if db.startswith(name_DB):
                    print(f"[INFO] Deleting old DB: {db}")
                    del bw.databases[db]
        
        new_keys = set()

        # === 6️⃣ Main loop over scenarios ===
        for scenario in dict_scenarios:
            db_name = f"{name_DB}{scenario}"
            print(f"\n[INFO] Creating GLO DEALA activities for {db_name} …")

            if db_name not in bw.databases:
                bw.Database(db_name).register()
                print(f"[INFO] Registered new Brightway DB: {db_name}")

            # === SQLite Connection ===
            conn = sqlite3.connect(db_path_main, timeout=120)
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute("PRAGMA busy_timeout = 300000;")
            cur.execute("PRAGMA synchronous=OFF;")
            cur.execute("PRAGMA temp_store=MEMORY;")
            cur.execute("BEGIN;")
            conn.commit()

            # Retrieve existing codes
            cur.execute("SELECT code FROM activitydataset WHERE database=?", (db_name,))
            existing_codes = {r[0] for r in cur.fetchall()}

            batch = []
            total_added = 0
            t0 = time.time()

            flows = [flow for flow in market_db]

            # === Generate activities ===
            for act_name, (category, years) in tqdm(dict_activities.items(), desc=f"{scenario}"):

                for flow in flows:
                    if category not in flow["categories"][0]:
                        continue

                    name = f"{act_name} - {flow['categories'][1]}"
                    code = generate_code(db_name, name, flow['name'])
                    if code in existing_codes:
                        continue

                    # Input = marketsphere flow
                    bio_exc = {
                        "input": flow.key,
                        "amount": 1.0,
                        "type": "biosphere",
                    }
                    # Output = Production
                    prod_exc = {
                        "input": (db_name, code),
                        "amount": 1.0,
                        "type": "production",
                    }

                    # --- Brightway-safe exchanges (add output, type, amount) ---
                    exchanges = fix_exchanges_for_index([bio_exc, prod_exc], db_name, code)

                    act_data = {
                        "name": name,
                        "unit": "USD",
                        "location": "GLO",
                        "reference product": flow["name"],
                        "code": code,
                        "type": "process",
                        "database": db_name,
                        "production amount": 1.0,
                        "categories": ("DEALA default", "GLO"),
                        "exchanges": exchanges,
                    }

                    pickled_act = pickle.dumps(act_data, protocol=pickle.HIGHEST_PROTOCOL)

                    # Build exchange rows from fixed exchanges
                    exc_rows = []
                    for ex in exchanges:
                        in_db, in_code = ex["input"]
                        pickled_ex = pickle.dumps(ex, protocol=pickle.HIGHEST_PROTOCOL)
                        exc_rows.append(
                            (
                                in_db,
                                in_code,
                                db_name,
                                code,
                                ex.get("type", "technosphere"),
                                pickled_ex,
                            )
                        )

                    batch.append((db_name, code, pickled_act, exc_rows))
                    existing_codes.add(code)
                    new_keys.add((db_name, code))
                    total_added += 1

                    # === Write batch ===
                    if len(batch) >= 1000:
                        cur.execute("BEGIN;")
                        for dbn, code, pact, exr in batch:
                            cur.execute(
                                "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                                (dbn, code, pact),
                            )
                            cur.executemany(
                                "INSERT INTO exchangedataset (input_database, input_code, output_database, output_code, type, data) VALUES (?, ?, ?, ?, ?, ?)",
                                exr,
                            )
                        conn.commit()
                        batch.clear()

            # Flush remaining batch
            if batch:
                cur.execute("BEGIN;")
                for dbn, code, pact, exr in batch:
                    cur.execute(
                        "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                        (dbn, code, pact),
                    )
                    cur.executemany(
                        "INSERT INTO exchangedataset (input_database, input_code, output_database, output_code, type, data) VALUES (?, ?, ?, ?, ?, ?)",
                        exr,
                    )
                conn.commit()

            conn.close()
            gc.collect()
            print(f"✅ Added {total_added} GLO activities to {db_name} in {time.time()-t0:.1f}s")

        # -----------------------------
        # 5️⃣ Mapping repair
        # -----------------------------
        print("\n🧩 Updating Brightway mapping for new DEALA default activities …")

        missing = {k for k in new_keys if k not in mapping.data}
        if missing:
            mapping.add(missing)
            print(f"✅ Added {len(missing)} mappings.")
        else:
            print("✅ No missing mappings.")

        # -----------------------------
        # 6️⃣ Process rebuild matrices
        # -----------------------------
        print("\n⚙️ Running db.process() for each DEALA database …")
        for db_name in [d for d in bw.databases if d.startswith("DEALA_activities_")]:
            db = bw.Database(db_name)
            try:
                db.process()
            except Exception as e:
                print(f"  ❌ {db_name}: {e}")



    def create_premise_databases(dict_scenarios, key_premise, source_type, filepath_ecoinvent, source_version, overwrite=False):
        """
        Creates premise databases based on given scenarios and other parameters.

        Args:
            dict_scenarios (dict): A dictionary containing scenario keys and corresponding years.
            key_premise (str): The decryption key for the premise database.
            source_type (str): Type of the source data (e.g., 'ecoinvent', 'custom', etc.).
            filepath_ecoinvent (str): File path to the ecoinvent data.
            source_version (str): Version of the source data.
            overwrite (bool): If True, overwrite existing databases. Default is False.

        Returns:
            None: The function does not return any value directly but creates premise databases.
        """
        list_scenarios = []

        # Split the keys and store the resulting strings as variables
        for key, values in dict_scenarios.items():
            db_name = f"{'ecoinvent'}_{source_version}{'-cutoff'}_{key}"
            if db_name in bw.databases:
                if overwrite:
                    del bw.databases[db_name]
                    print(f"Existing database '{db_name}' deleted due to overwrite=True.")
                    parts = key.split('_')
                    if len(parts) == 3:
                        model, pathway, year = parts
                        list_scenarios.append({"model": model, "pathway": pathway, "year": values})
                else:
                    print(f"Database '{db_name}' already exists. Skipping creation.")
                    continue
            else:
                parts = key.split('_')
                if len(parts) == 3:
                    model, pathway, year = parts
                    list_scenarios.append({"model": model, "pathway": pathway, "year": values})

        if not list_scenarios:
            print("No new scenarios to create databases for.")
            return

        clear_cache()

        for scenario in list_scenarios:

            # Initialize a NewDatabase object
            ndb = NewDatabase(
                scenarios=[scenario],
                source_type=source_type,
                source_file_path=filepath_ecoinvent,
                source_version=source_version,
                key=key_premise,
                # use_multiprocessing=True,  # Set to False if multiprocessing causes issues
                # keep_uncertainty_data=False,  # Set to True if you want to keep ecoinvent's uncertainty data
                # use_absolute_efficiency=True  # Set to True if you want to use IAM's absolute efficiency for power plants
            )

            ndb.update()
            ndb.write_db_to_brightway(f"{'ecoinvent'}_{source_version}-{'cutoff'}_{scenario['model']}_{scenario['pathway']}_{scenario['year']}")


    def create_target_databases(self, filepath: str, target: str):
        """
        Creates and populates target databases based on the specified Excel file.

        Args:
            filepath (str): Path to the Excel file containing data of target (e.g. transport or energy).
            target (str): name of target (e.g. transport or energy)

        Returns:
            dict: A dictionary mapping activity tuples (name, location, database) to their keys.
        """
        list_databases = []
        dict_activities = {}

        # Step 1: Retrieve a list of existing databases
        for database in bw.databases:
            list_databases.append(database)

        # Step 2: Delete databases containing both 'ecoinvent' and target
        for database in list_databases:
            if 'ecoinvent' in database and target in database:
                del bw.databases[database]

        # Step 3: Import data from the specified Excel file
        for database in list_databases:
            index_ecoinvent = database.find('ecoinvent')
            if 'ecoinvent' in database and index_ecoinvent == 0:
                imp = bw.ExcelImporter(filepath)
                imp.apply_strategies()
                imp.match_database(database, fields=('name', 'unit', 'location'))
                imp.match_database(fields=('name', 'unit', 'location'))
                imp.match_database('biosphere3', fields=('name', 'unit', 'categories'))
                imp.write_database()

                # Step 4: Rename the newly created target database
                bw.Database(target).rename(target + '_' + database)

                # Step 5: Populate the dictionary with activity keys
                for act in bw.Database(target + '_' + database):
                    dict_activities[(act['name'], act['location'], act['database'])] = act.key

        return dict_activities
    
    def identify_dependent_activities(name_database):
        """
        Identifies dependent activities in target databases to DEALA database and creates a dictionary of matches.

        This function performs the following steps:
        1. Retrieves lists of target and DEALA databases.
        2. Creates a dictionary mapping target databases to corresponding DEALA databases.
        3. Iterates through target databases and identifies dependent activities.
        4. Populates a dictionary of matches for each activity.

        Args:
            target_db (str): Name of target database (e.g. 'Energy' or 'Transport').

        Returns:
            dict: A dictionary mapping input keys to lists of dependent activities.
            dict: A dictionary containing the matches of the databases.
            list: A list containing the DEALA databases stored in the project.
            list: A list containing the Target databases stored in the project.
        """
        lst_DB_DEALA = []
        lst_DB = []

        # Step 1: Retrieve lists of target and DEALA databases
        for database in bw.databases:
            if 'Energy' in database and 'ecoinvent' in database:
                lst_DB.append(database)
            elif 'DEALA' in database:
                lst_DB_DEALA.append(database)

        # Step 2: Create a dictionary mapping target databases to DEALA databases
        # dict_databases = {key: value for key, value in zip(lst_DB, lst_DB_DEALA)}
        dict_databases={}
        for string in lst_DB:
            for match in lst_DB_DEALA:
                last_part=match.rsplit('_', 1)[-1]
                print(match, last_part)
                if last_part in string:
                    dict_databases[string]=match


        # Step 3: Identify dependent activities in target databases
        dict_matches = {}
        for database in tqdm(lst_DB):
            for activity in bw.Database(database):
                list_countries = []
                for exchange in activity.technosphere():
                    if 'ecoinvent' in exchange.input['database']:
                        key = exchange.input
                        dict_matches[key] = [exchange.input]
                        act = exchange.input
                        list_inputs = [act]
                        list_countries.append(act['location'])
                        for exchange in act.technosphere():
                            if (
                                exchange.input['location'] != act['location']
                                and exchange.input['reference product'] == act['reference product']
                                and exchange.input['location'] not in list_countries
                            ):
                                list_inputs.append(exchange.input)
                                list_countries.append(exchange.input['location'])
                                dict_matches[key].append(exchange.input)
                        while list_inputs:
                            list_check = []
                            for exchange in list_inputs[0].technosphere():
                                if exchange.input['location'] not in list_check:
                                    list_check.append(exchange.input['location'])
                                else:
                                    list_countries.append(exchange.input['location'])
                            for exchange in list_inputs[0].technosphere():
                                if (
                                    exchange.input['location'] != act['location']
                                    and exchange.input['reference product'] == act['reference product']
                                    and exchange.input['location'] not in list_countries
                                ):
                                    list_inputs.append(exchange.input)
                                    list_countries.append(exchange.input['location'])
                                    dict_matches[key].append(exchange.input)
                            list_inputs.pop(0)

        return dict_databases, dict_matches, lst_DB_DEALA, lst_DB
    
   
   
    def copy_and_add_DEALA_activity(dict_databases, dict_target, dict_activities):
        """
        Copies activities of target database and adds DEALA activity to specified databases.

        Args:
            dict_databases (dict): A dictionary mapping database names to their values.
            dict_target (dict): A dictionary containing information related to target database.
            dict_activities (dict): A dictionary containing activity information.

        Returns:
            None
        """

        for key, value in tqdm(dict_databases.items(), desc='Copy target activities and add DEALA activity to database'):
            for act_DEALA in bw.Database(value):
                if act_DEALA['name'] in dict_target.keys():
                    # Get activity from energy database
                    act=bw.get_activity(dict_activities[(dict_target[act_DEALA['name']], 'GLO', bw.Database(key).name)])
                    # Copy activity with name from DEALA activity and respective country
                    act_copy=act.copy(name=act_DEALA['name'], location=act_DEALA['location'])
                    act_copy.new_exchange(input=act_DEALA.key, amount = 1, type='technosphere').save()

        # Example usage:
        # copy_and_add_DEALA_activity(my_dict_databases, my_dict_energy)

    def find_location(self, Loc, df):
        """
        Finds the appropriate location for a given activity based on geographical matching.

        Args:
            Loc (str): The location to match.
            df (pandas.DataFrame): A DataFrame containing relevant data.

        Returns:
            str: The matched location.
            
        Raises:
            ValueError: If the location is not found or if both GLO and ROW are unavailable.
        """
        geomatcher = Geomatcher()  # Initialize the Geomatcher
        locations = geomatcher.within(Loc, biggest_first=False)  # Get matching locations
        
        for location in locations:
            if "ecoinvent" in location:
                location = location[1]  # Extract the actual location name from ecoinvent
            if location in df.columns and not df[location].isnull().values.any():
                return location  # Return the location if it exists in the DataFrame
            elif location == "GLO" and location in df.columns and df[location].isnull().values.any():
                if "RoW" in df.columns and not df["RoW"].isnull().values.any():
                    location = "RoW"  # Use RoW if available
                    return location
                elif "RER" in df.columns and not df["RER"].isnull().values.any():
                    location = "RER"  # Use RER if available
                    return location
                else:
                    raise ValueError(f"{location} of activity not found, GLO and ROW also not available")
            elif location == "GLO" and location not in df.columns:
                if "RoW" in df.columns and not df["RoW"].isnull().values.any():
                    location = "RoW"  # Use RoW if available
                return location

    def calculate_price_based_on_margin(self, db, deala_db, list_names, percentage_margin=0.2, overwrite=True):
        """
        Calculates the price of end products based on a margin and adds them to the DEALA database.
        Args:
            db (str): The name of the database containing the end products.
            deala_db (str): The name of the DEALA database where the prices will be added.
            list_names (list): A list of names of end products to calculate prices for.
            percentage_margin (float): The percentage margin to apply to the cost. Default is 0.2 (20%).
            overwrite (bool): If True, existing activities in the DEALA database will be overwritten. Default is True.

        """
        db_marketsphere = bw.Database('marketsphere')
        exchange = db_marketsphere.search('end product', limit=1)


        methods = [m for m in bw.methods if 'DEALA-Cost (BEIC 1)' in str(m)]
        activities = [act for act in db if act['reference product'] in list_names]
        prod_sys=[]
        for act in activities:
            prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
        bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
        myMultiLCA = bw.MultiLCA('multiLCA')
        scores = myMultiLCA.results

        dict_RD={}
        total_cost={}

        for index, element in enumerate(prod_sys):
            for key in element.items():
                dict_RD[f"{key[0]['name']}_{key[0]['location']}"] = scores[index][0]

        for act in activities:
            amount=dict_RD[f"{act['name']}_{act['location']}"]
            for exc in act.technosphere():
                if f"{exc.input['name']}_{exc.input['location']}" in dict_RD:
                    amount=amount-dict_RD[f"{exc.input['name']}_{exc.input['location']}"]*exc.amount
            total_cost[(act['name'], act['location'])] = amount

        for act in activities:
            # calculate the price based on the margin
            price = total_cost[(act['name'], act['location'])] * (1 + percentage_margin)
            # add DEALA activity representing the price of the pan to DEALA database
            if overwrite:
                # delete the existing activity if overwrite is True
                for existing_act in deala_db.search('end products - ' + db.name + act['location'], limit=1):
                    existing_act.delete()
            # create a new activity in the DEALA database with the price
            act_new = self.new_activity(deala_db.name, 'end products - ' + db.name, db.name, 'item', 'end products', location=act['location'])
            #add the exchange with the price
            act_new.new_exchange(input=exchange[0].key, amount=price, type='biosphere').save()

            # add act_new to act
            act.new_exchange(input=act_new.key, amount=1, type='technosphere').save()


    def update_exchanges(self, dict_matches, lst_DB1, lst_DB2):
        """
        Updates technosphere exchanges in the given databases based on geographical matching.

        Args:
            dict_matches (dict): A dictionary containing matched locations for input exchanges.
                                 The keys are tuples of (name, reference product, location) and the values are lists of tuples
                                 with the same information for matched activities.
            lst_DB1 (list): A list of target-related database names where the exchanges will be updated.
            lst_DB2 (list): A list of ecoinvent database names to search for matching activities.

        Returns:
            None
        """
        
        for db1, db2 in zip(lst_DB1, lst_DB2):  
            for act in tqdm(bw.Database(db1)):
                for exc in act.technosphere():
                    if (exc.input['name'], exc.input['reference product'], exc.input['location']) in dict_matches:
                        list_locations = []
                        list_names = []
                        for entry in dict_matches[(exc.input['name'], exc.input['reference product'], exc.input['location'])]:
                            list_names.append((entry[0], entry[1]))
                            list_locations.append(entry[2])
                        df = pd.DataFrame([list_names], columns=list_locations)
                        location = self.find_location(act['location'], df)
                        results = bw.Database(db2).search(df[location][0][0] + " " + location, limit=1000)
                        for result in results:
                            if (
                                result['name'] == df[location].values[0][0]
                                and result['reference product'] == df[location].values[0][1]
                                and result['location'] == location
                            ):
                                exc.delete()
                                act.new_exchange(input=result, amount=exc.amount, type='technosphere').save()

    # Example usage:
    # update_exchanges(dict_matches, lst_DB_Energy)


    def identify_matches(database_name):
        """
        Identify dependent activities in the specified ecoinvent database.

        Parameters:
        database_name (str): The name of the ecoinvent database to search.

        Returns:
        dict: A dictionary where the keys are tuples containing the name, reference product, and location of the input,
            and the values are lists of tuples with the same information for dependent activities.
        """
        dict_matches = {}

        # Iterate over each activity in the specified database
        for activity in tqdm(bw.Database(database_name)):
            list_countries = []

            # Iterate over each technosphere exchange of the activity
            for exchange in activity.technosphere():
                if 'ecoinvent' in exchange.input['database']:
                    key = (exchange.input['name'], exchange.input['reference product'], exchange.input['location'])
                    dict_matches[key] = [(exchange.input['name'], exchange.input['reference product'], exchange.input['location'])]
                    act = exchange.input
                    list_inputs = [act]
                    list_countries.append(act['location'])

                    # Iterate over each technosphere exchange of the current activity
                    for exchange in act.technosphere():
                        if (
                            exchange.input['location'] != act['location']
                            and exchange.input['reference product'] == act['reference product']
                            and exchange.input['location'] not in list_countries
                        ):
                            list_inputs.append(exchange.input)
                            list_countries.append(exchange.input['location'])
                            dict_matches[key].append((exchange.input['name'], exchange.input['reference product'], exchange.input['location']))

                    # Process the list of inputs
                    while list_inputs:
                        list_check = []

                        # Iterate over each technosphere exchange of the first input in the list
                        for exchange in list_inputs[0].technosphere():
                            if exchange.input['location'] not in list_check:
                                list_check.append(exchange.input['location'])
                            else:
                                list_countries.append(exchange.input['location'])

                        for exchange in list_inputs[0].technosphere():
                            if (
                                exchange.input['location'] != act['location']
                                and exchange.input['reference product'] == act['reference product']
                                and exchange.input['location'] not in list_countries
                            ):
                                list_inputs.append(exchange.input)
                                list_countries.append(exchange.input['location'])
                                dict_matches[key].append((exchange.input['name'], exchange.input['reference product'], exchange.input['location']))

                        list_inputs.pop(0)

        return dict_matches

    # Example usage
    # database_name = "Energy_ecoinvent 3.9.1-cutoff_ecoSpold02"
    # dependent_activities = identify_dependent_activities(database_name)
    # print(dependent_activities)


    def regionalize_process(self, database_name, dict_countries):
        """
        Regionalizes processes and their exchanges in a specified database.
        This function creates regionalized copies of processes in the foreground system 
        based on the provided dictionary of countries. It then updates the exchanges 
        of the copied activities to match the location-specific processes.
        Args:
            database_name (str): The name of the database containing the processes to be regionalized.
            dict_countries (dict): A dictionary where keys are country identifiers and values are country names.
        Returns:
            None: The function modifies the database in place by creating regionalized copies 
            of processes and updating their exchanges.
        Notes:
            - The function assumes that the database contains processes with a 'location' attribute.
            - Exchanges are updated to match the location-specific processes based on their name, 
              reference product, and location.
            - The function uses the Brightway2 framework for database and activity manipulation.
        """
        
        # create regionalized copies of processes in the foreground system
        activities = [act for act in bw.Database(database_name)]
        for country in dict_countries.values():
            for act in activities:
                act.copy(name=act['name'], location=country)

        # regionalize exchanges of copied activities
        activities = [act for act in bw.Database(database_name)]
        for act in tqdm(activities, "change activity location"):
            exchanges = [exc for exc in act.technosphere()]
            for exc in exchanges:
                list_possibilities = []
                for alt in bw.Database(exc.input['database']):  
                    if exc.input['name'] == alt['name'] and exc.input['reference product'] == alt['reference product']:
                        list_possibilities.append(alt)
                geomatcher = Geomatcher()  # Initialize the Geomatcher
                locations = geomatcher.within(act['location'], biggest_first=False)
                matched_item = None  # To store the result

                for location in locations:
                    # Extract location from ecoinvent tuple if needed
                    if isinstance(location, tuple) and "ecoinvent" in location:
                        location = location[1]

                    # Check if this location is part of any item['location']
                    for item in list_possibilities:
                        if location in item['location']:
                            matched_item = item
                            break
                    if matched_item:
                        break  # Exit the outer loop if a match is found

                    # Special case: location is "GLO" but not present in list_possibilities
                    if location == "GLO" and not any("GLO" in item['location'] for item in list_possibilities):
                        if any("RoW" in item['location'] for item in list_possibilities):
                            matched_item = next(item for item in list_possibilities if "RoW" in item['location'])
                            break
                        elif any("RER" in item['location'] for item in list_possibilities):
                            matched_item = next(item for item in list_possibilities if "RER" in item['location'])
                            break

                # If no match is found at all
                if not matched_item:
                    print(f"No matching item found for {act}")



                act.new_exchange(
                    input=matched_item.key, amount=exc.amount, type="technosphere"
                ).save()
                exc.delete()
                act.save()


    def add_social_exchanges(self, lst_DB, df_social, fp, dict_project, target):
        """
        Adds social exchange data to specified databases.

        This method reads a JSON file containing cost data, filters the social exchanges
        DataFrame for the specified target activity, and iterates through the provided databases.
        For each activity in the databases, it identifies technosphere exchanges related to 'DEALA',
        retrieves the corresponding biosphere exchange amount, finds the location in the filtered
        DataFrame, and creates a new technosphere exchange using the project dictionary.

        Parameters:
            lst_DB (list): List of database names to process.
            df_social (pd.DataFrame): DataFrame containing social exchange information.
            fp (str): File path to the JSON file with cost data.
            dict_project (dict): Dictionary mapping project data for exchange creation.
            target (str): Target activity name to filter social exchanges.

        Returns:
            None

        Notes:
            - Uses tqdm for progress visualization.
            - Modifies the databases by adding new technosphere exchanges.
        """
        # Read json file including data for electricity cost
        with open(fp) as f:
            data = json.load(f)

        # Definition of df_result (row showing the social exchanges for electricity)
        mask = (df_social["Activity"] == target)
        df_result = df_social[mask]

        for database in lst_DB:
            for act in tqdm(bw.Database(database)):
                for exchange in act.technosphere():
                    if "DEALA" in exchange.input['database']:
                        for bio in exchange.input.biosphere():
                            amount = bio.amount
                        loc = self.find_location(act['location'], df_result)
                        act.new_exchange(
                            input=dict_project[(df_result[loc].values[0], df_result[loc].values[0], loc, 'shdb')],
                            amount=amount,
                            type='technosphere'
                        ).save()


    def calculate_investments_buildings_machine(self, db_act, machinery_keyword, building_keyword):
        """
        # Calculate the total investments for machinery and buildings

        Parameters:
            db_act (bw.Database): The foreground database containing activities.
            machinery_keyword (str): Keyword to identify machinery-related investments.
            building_keyword (str): Keyword to identify building-related investments.

        Returns:
            tuple: Two dictionaries containing investments for machinery and buildings as well as the sum of both.
                Format: (dict_machine, dict_buildings, total_investments)
        """
        # Dictionary for investment of machinery and equipment
        dict_machine = {}
        # Dictionary for investment of buildings
        dict_buildings = {}

        # Calculate investments for machinery
        for act in db_act:
            for exc in act.technosphere():
                if machinery_keyword in exc.input['name']:
                    dict_machine[(act['name'], act['location'])] = exc['amount']

        # Calculate investments for buildings
        for act in db_act:
            for exc in act.technosphere():
                if building_keyword in exc.input['name']:
                    for bio in exc.input.biosphere():
                        dict_buildings[(act['name'], act['location'])] = exc['amount'] * bio['amount']

        # Calculate the total investments for machinery and buildings
        total_investments = {}

        for key in dict_machine.keys():
            total_investments[key] = dict_machine[key]

        for key in dict_buildings.keys():
            if key in total_investments:
                total_investments[key] += dict_buildings[key]
            else:
                total_investments[key] = dict_buildings[key]

        return dict_machine, dict_buildings, total_investments
    
    def dependent_DEALA_activity_percentage_rate(self, db_act, db_deala, dict_investment, percentage_rate, keyword=None, amount=1, location=None):
        """
        Adds dependent DEALA activities with a percentage rate to the specified database.

        Parameters:
            db_act (bw.Database): The foreground database containing activities.
            db_deala (bw.Database): The DEALA database containing percentage rate activities.
            dict_investment (dict): A dictionary mapping activity names and locations to investment amounts.
            percentage_rate (str): Keyword to identify percentage rate activities in the DEALA database.
            amount (float, optional): Multiplier for the investment amount. Defaults to 1.
            location (str, optional): Location to filter activities. If None, location is ignored.

        Returns:
            None: The function modifies the database in place by adding new exchanges.
        """
        for exc in db_deala:
            if percentage_rate in exc['name'] and (keyword is None or keyword in exc['reference product']):
                # Add new exchange to activity
                for key in dict_investment.keys():
                    for act in db_act:
                        if key[0] in act['name'] and key[1] == act['location'] and (location is None or act['location'] == location):
                            act.new_exchange(input=exc.key, amount=dict_investment[key] * amount, type='technosphere').save()


    def calculate_personnel_cost_processes(self, db_act):
        """
        Calculate the personnel costs associated with processes in a given database.

        This function iterates through the activities in the provided database and calculates
        the personnel costs for each activity based on the technosphere exchanges and their
        corresponding biosphere flows.


            dict: A dictionary containing personnel costs for each activity, with keys as tuples
              of activity name and location, and values as the calculated personnel cost.
        """
        # Dictionary for personnel cost of processes
        dict_personnel = {}


        #calculate personnel cost of each activity of database
        for act in db_act:
            for exc in act.technosphere():
                if "personnel" in exc.input['name']:
                    for bio in exc.input.biosphere():
                        personnel_cost=exc.amount*bio.amount
                    dict_personnel[(act['name'], act['location'])] = personnel_cost

        return dict_personnel
    

    def calculate_total_cost_processes(self, db_act):
        """
        Calculate the total cost of processes in a given database.

        This function computes the total cost of each activity in the provided database, including all associated costs
        and subtracting the costs of dependent activities. It uses Brightway2's MultiLCA functionality to perform the 
        calculations based on predefined impact assessment methods.

        Args:
            db_act (bw.Database): The foreground database containing activities.

        Returns:
            dict: A dictionary containing the total cost for each activity, with keys as tuples of activity name and location,
                  and values as the calculated total cost.
        """
 
        #Definition of all methods to calculate the cost before taxes
        methods = [m for m in bw.methods if 'DEALA-Cost (BEIC 1)' in str(m)]

        #calculate the total cost of acitvities
        prod_sys=[]
        for act in db_act:
            prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
        bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
        myMultiLCA = bw.MultiLCA('multiLCA')
        scores = myMultiLCA.results

        dict_RD={}
        total_cost={}

        for index, element in enumerate(prod_sys):
            for key in element.items():
                dict_RD[f"{key[0]['name']}_{key[0]['location']}"] = scores[index][0]

        for act in db_act:
            amount=dict_RD[f"{act['name']}_{act['location']}"]
            for exc in act.technosphere():
                if f"{exc.input['name']}_{exc.input['location']}" in dict_RD:
                    amount=amount-dict_RD[f"{exc.input['name']}_{exc.input['location']}"]*exc.amount
            total_cost[(act['name'], act['location'])] = amount

        return total_cost
    
    def calculate_total_cost_processes_wo_co_products(self, db_act):
            """
            Calculate the total cost of processes in a given database.

            This function computes the total cost of each activity in the provided database, including all associated costs
            and subtracting the costs of dependent activities. It uses Brightway2's MultiLCA functionality to perform the 
            calculations based on predefined impact assessment methods.

            Args:
                db_act (bw.Database): The foreground database containing activities.

            Returns:
                dict: A dictionary containing the total cost for each activity, with keys as tuples of activity name and location,
                    and values as the calculated total cost.
            """
    
            #Definition of all methods to calculate the cost before taxes
            methods = [m for m in bw.methods if 'DEALA-Cost (BEIC 3)' in str(m) and 'cost' in str(m) and 'co-product' not in str(m)]

            #calculate the total cost of acitvities
            prod_sys=[]
            for act in db_act:
                prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
            bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
            myMultiLCA = bw.MultiLCA('multiLCA')
            scores = myMultiLCA.results

            dict_RD={}
            total_cost={}

            for index, element in enumerate(prod_sys):
                for key in element.items():
                    dict_RD[f"{key[0]['name']}_{key[0]['location']}"] = sum(scores[index])

            for act in db_act:
                amount=dict_RD[f"{act['name']}_{act['location']}"]
                for exc in act.technosphere():
                    if f"{exc.input['name']}_{exc.input['location']}" in dict_RD:
                        amount=amount-dict_RD[f"{exc.input['name']}_{exc.input['location']}"]*exc.amount
                total_cost[(act['name'], act['location'])] = amount

            return total_cost



    def calculate_profit_processes(self, db_act, final_product):
        """
        Calculate the profit associated with processes in a given database before taxes.

        This function iterates through the activities in the provided database and calculates
        the profit for each activity that matches the specified final product. The profit is 
        computed using Brightway2's MultiLCA functionality based on predefined impact assessment 
        methods for DEALA profit.

        Args:
            db_act (bw.Database): The foreground database containing activities.
            final_product (str): The name of the final product to filter activities.

        Returns:
            float: The total profit sum for the specified final product before taxes.
        """

        #Definition of all methods to calculate the cost before taxes
        methods = [m for m in bw.methods if 'DEALA-Profit (BEIC 1)' in str(m)]

        total_profit={}

        #calculate the profit of acitvities before taxes
        for act in db_act:
            profit_sum = 0
            if final_product in act['name']:
                prod_sys=[]
                prod_sys.append({act:1}) #Definition for 1 kg to represent the right amount in the end
                profit_sum = 0
                bw.calculation_setups['multiLCA'] = {'inv': prod_sys, 'ia': methods}
                myMultiLCA = bw.MultiLCA('multiLCA')
                profits = myMultiLCA.results
                for profit in profits[0]:
                    profit_sum = profit_sum + profit

                total_profit[(act['name'], act['location'])] = profit_sum

        return total_profit

    def calculate_impacts_per_activity(self, process_system, methods_list, file_paths, method_mapping):
        """
        Calculate environmental and economic impacts for each activity in the foreground system.

        Parameters:
        - process_system (list): List of reference flows representing the production system.
        - methods_list (list): List of impact assessment methods to be applied.
        - file_paths (dict): Dictionary mapping reference flows to file paths for saving results.
        - method_mapping (dict): Dictionary mapping method tuples to readable method names.

        Returns:
        - results (list): List of calculated results for each reference flow.
        """
        from openpyxl import load_workbook
        from tqdm import tqdm

        results = []
        for reference_flow in process_system:
            impact_results = {}
            lca_instance = bw.LCA(reference_flow)
            lca_instance.lci()

            # Determine file path for the reference flow
            try:
                file_path = file_paths[reference_flow['database']]
            except KeyError:
                file_path = file_paths[str(reference_flow)]

            # Iterate over all methods and calculate impacts
            for method in tqdm(methods_list):
                lca_instance.switch_method(method)
                impact_data = bwa.traverse_tagged_databases(reference_flow, method, label='name')
                impact_values = impact_data[0].values()
                impact_labels = list(impact_data[0].keys())

                # Filter out zero values
                filtered_labels = [label for label, value in zip(impact_labels, impact_values) if value != 0]
                filtered_values = [value for value in impact_values if value != 0]

                # Create a DataFrame for the results
                impact_df = pd.DataFrame({'Process': filtered_labels, 'Value': filtered_values})
                impact_results[method_mapping[method][0]] = impact_df

            # Save results to an Excel file
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in impact_results.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            results.append(impact_results)

        return results
    
    def generate_stacked_bar_chart_process_view(self, file_name, file_path, dict_method, methods, custom_colors=None, title_diagram=None):
        """
        Generate an interactive stacked bar chart for a given file and method dictionary.

        Parameters:
        - file_name (str): The name of the file (e.g., 'batch').
        - file_path (str): The path to the directory containing the file.
        - dict_method (dict): A dictionary mapping method tuples to readable method names.
        - methods (list): A list of methods to be visualized.
        - custom_colors (list): List of custom colors for the bars. If None, default Plotly colors are used.

        Returns:
        - None: Displays the interactive stacked bar chart.
        """

        # Default Plotly colors if no custom colors are provided
        if custom_colors is None:
            custom_colors = px.colors.qualitative.Plotly

        # Initialize an empty dictionary to store dataframes
        dict_df = {}

        # Iterate through files in the specified directory
        for file in os.listdir(file_path):
            if file_name in file:  # Check if the file name matches the input
                parts = file.split('_')
                if len(parts) >= 2:
                    last_part = parts[-1].replace('.xlsx', '')  # Extract country code
                    country_code = last_part
                # Read each sheet in the Excel file and store it in the dictionary
                for sheet in pd.ExcelFile(os.path.join(file_path, file)).sheet_names:
                    dict_df[(country_code, sheet)] = pd.read_excel(
                        os.path.join(file_path, file), sheet_name=sheet
                    )

        # Iterate through methods in the dictionary
        for method in methods:
            # Filter dataframes based on the method
            if method not in dict_method:
                print(f"Method {method} not found in dict_method.")
                continue
            filtered = {k: v for k, v in dict_df.items() if k[1] == dict_method[method][0]}
            if filtered == {}:
                print(f"No data found for method {method}.")
                continue
            for (country, _), df in filtered.items():
                df["Countries"] = country  # Add a column for country
            # Combine all filtered dataframes
            df_combined = pd.concat(filtered.values(), keys=filtered.keys(), ignore_index=True)

            # Calculate totals for each country
            totals = df_combined.groupby("Countries")["Value"].sum().to_dict()

            # Create an interactive stacked bar chart
            fig = px.bar(
                df_combined,
                x="Value",
                y="Countries",
                color="Process",
                orientation="h",
                color_discrete_sequence=custom_colors,  # Use user-defined colors
                labels={"Value": dict_method[method][1]},
                title=f"Impact Category: {method[1]} - {title_diagram}"
            )

            # Add diamonds to represent total values
            for country, total in totals.items():
                fig.add_scatter(
                    x=[total],
                    y=[country],
                    mode="markers",
                    marker=dict(symbol="diamond", size=10, color="black"),
                    name="Total",
                    showlegend=False
                )

            # Update layout and display the chart
            fig.update_layout(barmode='relative')
            fig.show()

    def create_horizontal_bar_plot_DEALA(self, df, title="Horizontal Bar Plot", custom_colors=None):
        """
        Creates a horizontal bar plot for the given DataFrame, visualizing the impact categories 
        across different BEIC levels. The plot is interactive and uses Plotly for visualization.

        Parameters:
        - df (pd.DataFrame): Input DataFrame containing the data to be visualized.
        - title (str): Title of the plot. Default is "Horizontal Bar Plot".
        - custom_colors (list): List of custom colors for the bars. If None, default Plotly colors are used.

        Returns:
        - None: Displays the plot in the notebook.
        """


        # Default Plotly colors if no custom colors are provided
        if custom_colors is None:
            custom_colors = px.colors.qualitative.Plotly

        # Define BEIC levels
        beic_levels = ['BEIC 3', 'BEIC 2', 'BEIC 1']

        for index in df.index:
            df_index = df.loc[index]
            country = index.split("item,")[1].split(",")[0].strip()
            scenario = index.split("item,")[1].strip()

            # Extract and sort impact categories
            categories = df_index.index
            sorted_categories = sorted(categories, key=lambda x: (x.split(' - ')[0], x.split(' - ')[-1]))
            impact_categories = list({cat.split(' - ')[-1] for cat in sorted_categories})
            impact_categories.sort()

            # Map impact categories to BEIC levels
            data_per_category = {impact: [0, 0, 0] for impact in impact_categories}

            for category in sorted_categories:
                impact_name = category.split(' - ')[-1]
                beic_name = next(b for b in beic_levels if b in category)
                beic_index = beic_levels.index(beic_name)
                value = df_index[category]
                data_per_category[impact_name][beic_index] = value

            # Create bar traces for each impact category
            traces = []
            for i, impact in enumerate(impact_categories):
                values = data_per_category[impact]
                traces.append(go.Bar(
                    y=beic_levels,
                    x=values,
                    name=impact,
                    orientation='h',
                    marker_color=custom_colors[i % len(custom_colors)],
                    customdata=np.array(beic_levels).reshape(-1, 1),
                    hovertemplate='%{customdata[0]}<br>Kategorie: ' + impact + '<br>Wert: %{x:.2f}<extra></extra>',
                ))

            # Calculate total value for the title (only BEIC 1)
            total_value = sum(data_per_category[impact][2] for impact in impact_categories)
            total_str = f"{total_value:,.2f}" if total_value <= 10 else f"{total_value:,.0f}"
            total_str = total_str.replace(',', 'X').replace('.', ',').replace('X', '.')

            # Create the plot
            fig = go.Figure(data=traces)

            fig.update_layout(
                barmode='relative',
                title=f'{title} = {total_str} USD ({scenario})',
                xaxis_title='USD',
                yaxis=dict(
                    categoryorder='array',
                    categoryarray=beic_levels,
                    title=None
                ),
                legend=dict(title='Impact Categories'),
            )

            # Display the plot
            fig.show()



    def regionalize_process_input_fast(self, database_name, dict_countries, commit_every=2000):
        """
        Fast regionalization of processes in input databases (internal variant).
        """

        print(f"[INFO] Starting fast regionalization for: {database_name}")

        # === SQLite setup ===
        project_path = bw.projects.dir
        db_path = os.path.join(project_path, "lci", "databases.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Brightway SQLite DB not found: {db_path}")

        conn = sqlite3.connect(db_path, timeout=120)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA busy_timeout = 300000;")
        cur.execute("PRAGMA synchronous=OFF;")
        cur.execute("PRAGMA temp_store=MEMORY;")

        geomatcher = Geomatcher()

        # === Determine reference DB ===
        use_regioinvent = "regionalized" in database_name
        print(f"[INFO] → Using {'regioinvent' if use_regioinvent else 'ecoinvent'} references")

        # === Find matching DEALA DB ===
        deala_db_candidates = [d for d in bw.databases if d.startswith("DEALA_activities_")]

        def best_deala_match(fg_db_name, candidates):
            best = None
            best_len = -1
            for c in candidates:
                tail = c.replace("DEALA_activities_", "")
                if tail in fg_db_name and len(tail) > best_len:
                    best = c
                    best_len = len(tail)
            return best

        deala_db = best_deala_match(database_name, deala_db_candidates)
        if deala_db:
            print(f"[INFO] Using DEALA DB: {deala_db}")
        else:
            print(f"[WARN] No matching DEALA DB found for {database_name}.")

        # === Build DEALA cache ===
        deala_fwd, deala_rev = {}, {}
        if deala_db:
            for a in bw.Database(deala_db):
                nm = a.get("name", "").lower()
                rp = a.get("reference product", "").lower()
                loc = a.get("location", "GLO")
                if isinstance(loc, (tuple, list)):
                    loc = loc[-1]
                key = a.key

                deala_fwd[(nm, rp, loc)] = key
                deala_rev[key] = (nm, rp, loc)

            print(f"[INFO] Cached {len(deala_fwd)} DEALA activities.")

        # === Internal helper: FIX exchanges for bw.copy() ===
        def fix_exchanges_for_index(exchanges, output_db, output_code):
            """
            INTERNAL version:
            Ensures each exchange includes: input, output, type, amount.
            Does NOT override DEALA system method.
            """
            fixed = []
            for ex in exchanges:
                ex_new = ex.copy()

                # Mandatory fields for Brightway index
                ex_new["output"] = (output_db, output_code)
                ex_new["type"] = ex_new.get("type", "technosphere")
                ex_new["amount"] = float(ex_new.get("amount", 0.0))

                fixed.append(ex_new)
            return fixed

        # === Other helpers ===
        def normalize_location(loc):
            if isinstance(loc, (tuple, list)):
                return loc[-1]
            return loc or "GLO"

        def exchange_dict_from_exc(exc):
            try:
                in_key = exc.input.key
            except Exception:
                in_key = exc.get("input", None)
            if not in_key:
                return None
            return {
                "input": in_key,
                "amount": float(exc.amount),
                "type": exc.get("type", "technosphere"),
                "_bw_name": exc.input.get("name", ""),
                "_bw_db": exc.input.get("database", ""),
                "_bw_ref": exc.input.get("reference product", "")
            }

        def replace_deala_input_if_possible(exc_dict, target_country):
            if not deala_fwd:
                return exc_dict
            inp = exc_dict.get("input")
            if not isinstance(inp, tuple) or "DEALA" not in inp[0]:
                return exc_dict
            if inp not in deala_rev:
                return exc_dict

            nm, rp, _loc_old = deala_rev[inp]
            for loc in geomatcher.within(target_country, biggest_first=False):
                key = (nm, rp, loc)
                if key in deala_fwd:
                    exc_dict["input"] = deala_fwd[key]
                    return exc_dict

            glo_key = (nm, rp, "GLO")
            if glo_key in deala_fwd:
                exc_dict["input"] = deala_fwd[glo_key]
            return exc_dict

        # === Load activities ===
        fg_db = bw.Database(database_name)
        base_acts = list(fg_db)
        print(f"[INFO] Loaded {len(base_acts)} base activities.")

        new_rows = []
        written = 0
        all_new_keys = set()

        # ==============================
        # === MAIN LOOP ===============
        # ==============================
        for act in tqdm(base_acts, desc=f"Regionalizing {database_name}"):

            act_name = act.get("name", "")
            act_ref = act.get("reference product", act_name)
            act_unit = act.get("unit", "unit")
            act_code = act.get("code")
            act_database = act.get("database", database_name)

            orig_exchanges = [
                exchange_dict_from_exc(exc)
                for exc in act.exchanges()
                if exchange_dict_from_exc(exc)
            ]

            # CASE A: Production market
            countries_prod = {}
            has_production_market = False

            for exc in act.technosphere():
                if "production market" in exc.input.get("name", ""):
                    has_production_market = True
                    for exc1 in exc.input.technosphere():
                        loc = normalize_location(exc1.input.get("location", "GLO"))
                        if loc != "GLO" and "transport" not in exc1.input.get("name", "").lower():
                            countries_prod.setdefault(loc, []).append(exc1)

            if has_production_market and countries_prod:
                for country, exc_list in countries_prod.items():

                    total_amt = sum(e["amount"] for e in exc_list) or 0.0
                    if total_amt <= 0:
                        continue

                    new_exchanges = []

                    # Copy exchanges except production market
                    for d in orig_exchanges:
                        if d["type"] == "technosphere" and "production market" in d["_bw_name"]:
                            continue
                        ex_mod = replace_deala_input_if_possible(d.copy(), country)
                        new_exchanges.append(ex_mod)

                    # Add the new market-specific technosphere inputs
                    for e in exc_list:
                        new_exchanges.append({
                            "input": e.input.key,
                            "amount": float(e["amount"]) / total_amt,
                            "type": "technosphere"
                        })

                    # Construct new activity
                    new_code = f"{act_code}_{country}"
                    clean_exchanges = [
                        {k: v for k, v in ex.items() if not k.startswith("_bw_")}
                        for ex in new_exchanges
                    ]

                    # Add production exchange
                    clean_exchanges.append({
                        "input": (database_name, new_code),
                        "amount": 1.0,
                        "type": "production",
                    })

                    # FIX for Brightway index (internal only)
                    clean_exchanges = fix_exchanges_for_index(
                        clean_exchanges, database_name, new_code
                    )

                    act_data = {
                        "name": act_name,
                        "unit": act_unit,
                        "location": country,
                        "reference product": act_ref,
                        "code": new_code,
                        "type": "process",
                        "database": act_database,
                        "exchanges": clean_exchanges,
                    }

                    # Prepare SQL
                    exc_rows = []
                    for ex in clean_exchanges:
                        in_db, in_code = ex["input"]
                        pex = pickle.dumps(ex, protocol=pickle.HIGHEST_PROTOCOL)
                        exc_rows.append((in_db, in_code, database_name, new_code,
                                        ex.get("type", "technosphere"), pex))

                    new_rows.append((database_name, new_code,
                                    pickle.dumps(act_data, protocol=pickle.HIGHEST_PROTOCOL),
                                    exc_rows))

                    all_new_keys.add((database_name, new_code))

            # CASE B: Technology mix
            has_tech_mix = any("technology mix" in exc.input.get("name", "")
                            for exc in act.technosphere())

            if has_tech_mix:

                techmix_exchanges = [
                    exc for exc in act.technosphere()
                    if "technology mix" in exc.input.get("name", "")
                ]

                for country in dict_countries.values():

                    new_exchanges = []

                    mix_keys = {
                        (exc.input["name"],
                        exc.input.get("reference product", ""),
                        exc.input["database"])
                        for exc in techmix_exchanges
                    }

                    # Copy all except techmix items
                    for d in orig_exchanges:
                        if d["type"] == "technosphere" and (d["_bw_name"], d["_bw_ref"], d["_bw_db"]) in mix_keys:
                            continue
                        new_exchanges.append(
                            replace_deala_input_if_possible(d.copy(), country)
                        )

                    # Resolve technology mix replacements
                    ref_db_prefix = "regioinvent_" if use_regioinvent else "ecoinvent_"
                    target_dbs = [db for db in bw.databases if db.startswith(ref_db_prefix)]

                    for exc in techmix_exchanges:
                        matched_item = None
                        for dbname in target_dbs:
                            for alt in bw.Database(dbname):
                                if (
                                    alt["name"] == exc.input["name"]
                                    and alt.get("reference product", "") == exc.input.get("reference product", "")
                                ):

                                    alt_loc = normalize_location(alt.get("location", ""))

                                    for loc in geomatcher.within(country, biggest_first=False):
                                        if isinstance(loc, tuple):
                                            loc = loc[-1]
                                        if isinstance(alt_loc, str) and loc == alt_loc:
                                            matched_item = alt
                                            break
                                    if matched_item:
                                        break
                            if matched_item:
                                break

                        if matched_item:
                            new_exchanges.append({
                                "input": matched_item.key,
                                "amount": float(exc.amount),
                                "type": "technosphere"
                            })

                    new_code = f"{act_code}_{country}"

                    clean_exchanges = [
                        {k: v for k, v in ex.items() if not k.startswith("_bw_")}
                        for ex in new_exchanges
                    ]

                    clean_exchanges.append({
                        "input": (database_name, new_code),
                        "amount": 1.0,
                        "type": "production"
                    })

                    clean_exchanges = fix_exchanges_for_index(
                        clean_exchanges, database_name, new_code
                    )

                    act_data = {
                        "name": act_name,
                        "unit": act_unit,
                        "location": country,
                        "reference product": act_ref,
                        "code": new_code,
                        "type": "process",
                        "database": act_database,
                        "exchanges": clean_exchanges,
                    }

                    exc_rows = []
                    for ex in clean_exchanges:
                        in_db, in_code = ex["input"]
                        pex = pickle.dumps(ex, protocol=pickle.HIGHEST_PROTOCOL)
                        exc_rows.append((in_db, in_code, database_name, new_code,
                                        ex.get("type", "technosphere"), pex))

                    new_rows.append(
                        (database_name, new_code,
                        pickle.dumps(act_data, protocol=pickle.HIGHEST_PROTOCOL),
                        exc_rows)
                    )
                    all_new_keys.add((database_name, new_code))

            # Commit batch
            if len(new_rows) >= commit_every:
                cur.execute("BEGIN;")
                for dbn, code, pact, exc_rows in new_rows:
                    cur.execute(
                        "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                        (dbn, code, pact)
                    )
                    cur.executemany(
                        """INSERT INTO exchangedataset 
                        (input_database, input_code, output_database, output_code, type, data)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        exc_rows
                    )
                conn.commit()
                written += len(new_rows)
                print(f"[INFO] Committed {written} new region activities.")
                new_rows.clear()

        # Remaining commits
        if new_rows:
            cur.execute("BEGIN;")
            for dbn, code, pact, exc_rows in new_rows:
                cur.execute(
                    "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                    (dbn, code, pact)
                )
                cur.executemany(
                    """INSERT INTO exchangedataset 
                    (input_database, input_code, output_database, output_code, type, data)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    exc_rows
                )
            conn.commit()
            written += len(new_rows)
            new_rows.clear()

        conn.close()

        # Update mapping
        missing = {k for k in all_new_keys if k not in mapping.data}
        if missing:
            mapping.add(missing)
            print(f"[INFO] Added {len(missing)} new mappings.")

        # Re-process brightway DB
        try:
            bw.Database(database_name).process()
            print(f"[PROCESS] {database_name} processed successfully.")
        except Exception as e:
            print(f"[WARN] {database_name} process failed: {e}")

        print(f"\n✅ Finished regionalizing {database_name}. Total new activities: {written}")
        return written



   #### Transport functions

    DEFAULT_LORRY_KM = 208.8
    DEFAULT_SEA_KM = 599.0
    DEFAULT_LORRY_DIST_GLO = 300.0

    # ------------------------------------------------------------------
    # DATABASE UTILITIES
    # ------------------------------------------------------------------

    @staticmethod
    def _open_bw_sqlite():
        project_path = bw.projects.dir
        db_path = os.path.join(project_path, "lci", "databases.db")
        conn = sqlite3.connect(db_path, timeout=60)
        cur = conn.cursor()
        return conn, cur, db_path

    @staticmethod
    def _find_market_keys(ecoinvent_db_name):
        """Locate relevant ecoinvent market processes for lorry and sea freight."""
        db = bw.Database(ecoinvent_db_name)
        key_lorry = key_sea = None
        for act in db:
            if (
                act["name"] == "market for transport, freight, lorry, unspecified"
                and act["location"] == "RoW"
            ):
                key_lorry = act.key
            elif (
                act["name"] == "market for transport, freight, sea, container ship"
                and act["location"] == "GLO"
            ):
                key_sea = act.key
        if not key_lorry or not key_sea:
            raise RuntimeError(f"Missing transport markets in {ecoinvent_db_name}")
        return key_lorry, key_sea

    @staticmethod
    def _cache_deala_keys(deala_db_name):
        """Cache all DEALA activity keys from a single database."""
        db = bw.Database(deala_db_name)
        return {act["name"]: act.key for act in db}

    @staticmethod
    def _ensure_empty_database(db_name, overwrite=True):
        """Safely remove or create a new Brightway database."""
        if db_name in bw.databases and overwrite:
            del bw.databases[db_name]
        if db_name not in bw.databases:
            bw.Database(db_name).register()

    @staticmethod
    def _load_transport_inputs(FP_land, FP_sea, FP_harbor):
        """Load Excel-based transport matrices."""
        df_land = pd.read_excel(FP_land)
        countries = sorted(set([c[2:4] for c in df_land["country"]]))
        dist_land = pd.DataFrame(index=countries, columns=countries, data=-1.0)
        for _, row in df_land.iterrows():
            c1, c2 = row["country"][2:4], row["country"][8:10]
            if not pd.isna(row["distance"]):
                dist_land.at[c1, c2] = float(row["distance"])
                dist_land.at[c2, c1] = float(row["distance"])

        dist_sea = pd.read_excel(FP_sea, keep_default_na=False).set_index("Unnamed: 0")
        dist_sea.index = dist_sea.index.astype(str)
        dist_sea.columns = dist_sea.columns.astype(str)

        df_h = pd.read_excel(FP_harbor, keep_default_na=False)
        land2harbor = {str(r["country"]): float(r["distance"]) for _, r in df_h.iterrows()}

        return dist_land, dist_sea, land2harbor

    # ======================================================
    # === Transport Database Builder (fully Brightway-safe)
    # ======================================================

    def _open_bw_sqlite(self):
        db_path = os.path.join(bw.projects.dir, "lci", "databases.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Brightway SQLite not found: {db_path}")

        conn = sqlite3.connect(db_path, timeout=120)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA busy_timeout = 300000;")
        cur.execute("PRAGMA synchronous=OFF;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        return conn, cur, db_path


    # ------------------------------------------------------
    def _write_entries_sqlite(self, all_entries):
        """
        Writes activities and exchanges directly to Brightway SQLite DB.
        Ensures each activity has a production exchange and mapping entry.
        Returns set of new activity keys.
        """

        # --- LOCAL BRIGHTWAY-SAFE FIXER ---
        def fix_exchanges_for_index(exchanges, output_db, output_code):
            fixed = []
            for ex in exchanges:
                ex_new = ex.copy()
                ex_new["output"] = (output_db, output_code)
                ex_new["type"] = ex_new.get("type", "technosphere")
                ex_new["amount"] = float(ex_new.get("amount", 0.0))
                fixed.append(ex_new)
            return fixed

        conn, cur, _ = self._open_bw_sqlite()
        new_keys = set()

        for i, entry in enumerate(tqdm(all_entries, desc="Writing transport activities")):
            db_t = entry["db_target"]
            act = entry["data"]

            act.setdefault("type", "process")
            act.setdefault("database", db_t)
            act.setdefault("production amount", 1.0)

            # Production exchange enforced
            prod_exc = {"input": (db_t, act["code"]), "amount": 1.0, "type": "production"}
            act["exchanges"] = [e for e in act.get("exchanges", []) if e.get("type") != "production"]
            act["exchanges"].append(prod_exc)

            # --- CRITICAL FIX: Make exchanges Brightway-safe ---
            act["exchanges"] = fix_exchanges_for_index(act["exchanges"], db_t, act["code"])

            # --- Write activity ---
            pickled_act = pickle.dumps(act, protocol=pickle.HIGHEST_PROTOCOL)
            cur.execute(
                "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                (db_t, act["code"], pickled_act),
            )

            # --- Write exchanges ---
            for exc in act["exchanges"]:
                input_db, input_code = exc["input"]
                pickled_exc = pickle.dumps(exc, protocol=pickle.HIGHEST_PROTOCOL)
                cur.execute(
                    """INSERT INTO exchangedataset
                    (input_database, input_code, output_database, output_code, type, data)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        input_db,
                        input_code,
                        db_t,
                        act["code"],
                        exc.get("type", "technosphere"),
                        pickled_exc,
                    ),
                )

            new_keys.add((db_t, act["code"]))

            if (i + 1) % 500 == 0:
                conn.commit()

        conn.commit()
        conn.close()
        return new_keys


    # ------------------------------------------------------
    def _prepare_transport_entries(
        self,
        db_transport,
        dist_land,
        dist_sea,
        land2harbor,
        key_lorry,
        key_sea,
        deala_cache,
    ):
        """
        Prepare transport activities based on distance matrices and DEALA cache.
        Generates activities for all country pairs and handles various transport scenarios.
        Returns a list of activity entries ready for database insertion.
        """

        all_entries = []
        countries = sorted(set(dist_land.index) | {"GLO"})

        def find_deala_key(base_name):
            if base_name in deala_cache:
                return deala_cache[base_name]
            alt = f"transport - {base_name}"
            return deala_cache.get(alt, None)

        for c1 in tqdm(countries, desc=f"{db_transport}", leave=False):
            for c2 in countries:

                code = f"trans_{c1}_{c2}"
                act = {
                    "name": f"Transport from {c1} to {c2}",
                    "unit": "tkm",
                    "location": c1,
                    "reference product": "transport",
                    "code": code,
                    "type": "process",
                    "database": db_transport,
                    "exchanges": [],
                }

                def add_deala(name, amount):
                    key = find_deala_key(name)
                    if key:
                        act["exchanges"].append(
                            {"input": key, "amount": float(amount), "type": "technosphere"}
                        )

                # GLO → GLO
                if c1 == "GLO" and c2 == "GLO":
                    lorry_amt, sea_amt = 1000, 10000
                    act["exchanges"] += [
                        {"input": key_lorry, "amount": lorry_amt, "type": "technosphere"},
                        {"input": key_sea, "amount": sea_amt, "type": "technosphere"},
                    ]
                    add_deala(f"Transport, Road, from {c1} to {c2}", lorry_amt)
                    add_deala(f"Transport, Sea, from {c1} to {c2}", sea_amt)
                    all_entries.append({"db_target": db_transport, "data": act})
                    continue

                # One side GLO
                elif "GLO" in [c1, c2]:
                    lorry_amt, sea_amt = 1000, 10000
                    act["exchanges"] += [
                        {"input": key_lorry, "amount": lorry_amt, "type": "technosphere"},
                        {"input": key_sea, "amount": sea_amt, "type": "technosphere"},
                    ]
                    add_deala(f"Transport, Road, from {c1} to {c2}", lorry_amt)
                    add_deala(f"Transport, Sea, from {c1} to {c2}", sea_amt)
                    all_entries.append({"db_target": db_transport, "data": act})
                    continue

                # Domestic
                elif c1 == c2 and c1 != "GLO":
                    lorry_amt, sea_amt = 208.0, 599.0
                    act["exchanges"] += [
                        {"input": key_lorry, "amount": lorry_amt, "type": "technosphere"},
                        {"input": key_sea, "amount": sea_amt, "type": "technosphere"},
                    ]
                    add_deala(f"Transport, Road, from {c1} to {c2}", lorry_amt)
                    add_deala(f"Transport, Sea, from {c1} to {c2}", sea_amt)
                    all_entries.append({"db_target": db_transport, "data": act})
                    continue

                # Country → Country
                d_land = (
                    dist_land.at[c1, c2]
                    if (c1 in dist_land.index and c2 in dist_land.columns)
                    else -1
                )

                d_sea = None
                if c1 in dist_sea.index and c2 in dist_sea.columns:
                    val = dist_sea.at[c1, c2]
                    if not pd.isna(val) and str(val).strip() not in ["", "-"]:
                        d_sea = float(val)

                if (d_land <= 0) and (not d_sea or d_sea <= 0):
                    continue

                if 0 < d_land < 2000:
                    act["exchanges"].append(
                        {"input": key_lorry, "amount": float(d_land), "type": "technosphere"}
                    )
                    add_deala(f"Transport, Road, from {c1} to {c2}", d_land)
                else:
                    d1 = land2harbor.get(c1, 300.0)
                    d2 = land2harbor.get(c2, 300.0)
                    d_sea = d_sea or 10000.0
                    act["exchanges"] += [
                        {"input": key_lorry, "amount": float(d1), "type": "technosphere"},
                        {"input": key_sea, "amount": float(d_sea), "type": "technosphere"},
                        {"input": key_lorry, "amount": float(d2), "type": "technosphere"},
                    ]
                    add_deala(f"Transport, Road, from {c1} to {c1}", d1)
                    add_deala(f"Transport, Sea, from {c1} to {c2}", d_sea)
                    add_deala(f"Transport, Road, from {c2} to {c2}", d2)

                all_entries.append({"db_target": db_transport, "data": act})

        return all_entries


    # ------------------------------------------------------
    def build_transport_databases_fast(
        self,
        dict_scenarios,
        FP_transport_matrices_land,
        FP_transport_matrices_sea,
        FP_transport_matrices_land_harbor,
        name_ecoinvent_prefix="ecoinvent_3.9.1-cutoff_",
        overwrite=True,
    ):

        dist_land, dist_sea, land2harbor = self._load_transport_inputs(
            FP_transport_matrices_land,
            FP_transport_matrices_sea,
            FP_transport_matrices_land_harbor,
        )

        all_dbs = list(bw.databases)
        ecoinvent_dbs = [db for db in all_dbs if db.startswith(name_ecoinvent_prefix)]
        deala_dbs = [db for db in all_dbs if db.startswith("DEALA_activities_")]

        matches = []
        for scen_name in dict_scenarios.keys():
            eco_matches = [db for db in ecoinvent_dbs if scen_name in db]
            deala_matches = [db for db in deala_dbs if scen_name in db]
            if eco_matches and deala_matches:
                for eco_db in eco_matches:
                    matches.append((eco_db, deala_matches[0]))

        if not matches:
            print("[WARN] No ecoinvent↔DEALA matches found.")
            return

        summary = []
        for ecoinvent_db, deala_db in matches:
            db_transport = "Transport_" + ecoinvent_db

            key_lorry, key_sea = self._find_market_keys(ecoinvent_db)
            deala_cache = self._cache_deala_keys(deala_db)

            self._ensure_empty_database(db_transport, overwrite=overwrite)

            entries = self._prepare_transport_entries(
                db_transport,
                dist_land,
                dist_sea,
                land2harbor,
                key_lorry,
                key_sea,
                deala_cache,
            )

            new_keys = self._write_entries_sqlite(entries)

            missing = {k for k in new_keys if k not in mapping.data}
            if missing:
                mapping.add(missing)

            try:
                bw.Database(db_transport).process()
                print(f"[PROCESS] {db_transport} processed successfully.")
            except Exception as e:
                print(f"[WARN] {db_transport} process failed: {e}")

            summary.append((db_transport, len(entries)))

        print("\n=== Build Summary ===")
        for db_name, n_entries in summary:
            print(f"[UPDATE] {db_name} → {n_entries:,} activities created.")
        print(f"[INFO] ✅ {len(summary)} transport databases successfully built.")

    # ------------------------------------------------------
    def _commit_new_rows_to_sqlite(self, db_path, rows):
        conn = sqlite3.connect(db_path, timeout=120)
        cur = conn.cursor()
        cur.execute("PRAGMA synchronous = OFF;")
        cur.execute("PRAGMA journal_mode = MEMORY;")
        cur.execute("PRAGMA temp_store = MEMORY;")
        cur.execute("BEGIN;")
        for dbn, code, pact, exc_rows in rows:
            cur.execute(
                "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                (dbn, code, pact)
            )
            if exc_rows:
                cur.executemany(
                    "INSERT INTO exchangedataset (input_database, input_code, output_database, output_code, type, data) VALUES (?, ?, ?, ?, ?, ?)",
                    exc_rows
                )
        conn.commit()
        conn.close()


    def regionalize_process_outputmaterials_fast(self, database_name, commit_every=10000, debug=True):
        """
        Fast regionalization of output materials (class-based version).
        """

        import os, sqlite3, pickle, time
        import brightway2 as bw
        from tqdm import tqdm
        from constructive_geometries import Geomatcher
        import pandas as pd
        from bw2data import mapping

        # === LOCAL FIX: Brightway-safe exchange correction ===
        def fix_exchanges_for_index(exchanges, output_db, output_code):
            fixed = []
            for ex in exchanges:
                ex_new = ex.copy()
                ex_new["output"] = (output_db, output_code)
                ex_new["type"] = ex_new.get("type", "technosphere")
                ex_new["amount"] = float(ex_new.get("amount", 0.0))
                fixed.append(ex_new)
            return fixed
        # =====================================================

        t0 = time.time()
        print(f"[INFO] Starting optimized regionalization for {database_name}")

        # === Brightway SQLite path ===
        db_path = os.path.join(bw.projects.dir, "lci", "databases.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"[ERROR] Brightway SQLite DB not found: {db_path}")

        conn = sqlite3.connect(db_path, timeout=300)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA busy_timeout = 300000;")
        cur.execute("PRAGMA synchronous=OFF;")
        cur.execute("PRAGMA temp_store=MEMORY;")

        geomatcher = Geomatcher()

        # === Match DEALA DB ===
        deala_db = next(
            (d for d in bw.databases 
            if d.startswith("DEALA_activities_") 
            and d.replace("DEALA_activities_", "") in database_name),
            None
        )
        if not deala_db:
            raise ValueError(f"[ERROR] No matching DEALA DB found for {database_name}")

        # === Match background DB ===
        scenario_part = database_name.replace("output_materials_", "", 1)
        eco_db_target = f"ecoinvent_3.9.1-cutoff_{scenario_part}"
        regio_db_target = f"regioinvent_{scenario_part}"

        if regio_db_target in bw.databases:
            eco_db_target = regio_db_target
        elif eco_db_target not in bw.databases:
            raise ValueError(
                f"[ERROR] No matching background DB found for '{scenario_part}'."
            )

        # === Build DEALA caches ===
        deala_fwd, deala_rev = {}, {}
        for a in bw.Database(deala_db):
            nm = str(a.get("name", "")).lower().strip()
            rp = str(a.get("reference product", "")).lower().strip()
            loc = a.get("location", "GLO")
            deala_fwd[(nm, rp, loc)] = a.key
            deala_rev[a.key] = (nm, rp, loc)

        # === Build ecoinvent/regioinvent cache ===
        eco_map = {}
        for a in bw.Database(eco_db_target):
            nm = str(a.get("name", "")).lower().strip()
            rp = str(a.get("reference product", "")).lower().strip()
            loc = a.get("location", "GLO")
            eco_map.setdefault((nm, rp), {})[loc] = a.key

        all_countries = sorted({loc for (_, _, loc) in deala_fwd.keys() if loc != "GLO"})
        geo_within = {c: geomatcher.within(c, biggest_first=False) for c in all_countries}

        cache_deala, cache_eco, cache_findloc = {}, {}, {}

        # === Helper functions remain unchanged ===
        # ===================================================================
        def replace_deala_input_if_possible(exc_dict, target_country):
            key_cache = (exc_dict["input"], target_country)
            if key_cache in cache_deala:
                exc_dict["input"] = cache_deala[key_cache]
                return exc_dict

            inp = exc_dict["input"]
            if not isinstance(inp, tuple) or "DEALA" not in inp[0]:
                return exc_dict
            if inp not in deala_rev:
                return exc_dict

            nm, rp, _ = deala_rev[inp]
            for loc in geo_within.get(target_country, []):
                if (nm, rp, loc) in deala_fwd:
                    new_key = deala_fwd[(nm, rp, loc)]
                    exc_dict["input"] = new_key
                    cache_deala[key_cache] = new_key
                    return exc_dict

            if (nm, rp, "GLO") in deala_fwd:
                exc_dict["input"] = deala_fwd[(nm, rp, "GLO")]
            return exc_dict


        def replace_ecoinvent_input_if_possible(exc_dict, target_country, ex_name, ex_ref):
            key_cache = (ex_name, ex_ref, target_country)
            if key_cache in cache_eco:
                exc_dict["input"] = cache_eco[key_cache]
                return exc_dict

            inp = exc_dict["input"]
            if not isinstance(inp, tuple) or ("ecoinvent" not in inp[0] and "regioinvent" not in inp[0]):
                return exc_dict

            variants = eco_map.get((ex_name, ex_ref), {})
            if not variants:
                return exc_dict

            cols = list(variants.keys())
            df = pd.DataFrame([[1] * len(cols)], columns=cols)

            fl_key = (target_country, tuple(cols))
            if fl_key in cache_findloc:
                chosen_loc = cache_findloc[fl_key]
            else:
                try:
                    chosen_loc = self.find_location(target_country, df)
                except Exception:
                    chosen_loc = "GLO"
                cache_findloc[fl_key] = chosen_loc

            if chosen_loc in variants:
                exc_dict["input"] = variants[chosen_loc]
                cache_eco[key_cache] = variants[chosen_loc]
            else:
                for fb in ("RoW", "RER", "GLO"):
                    if fb in variants:
                        exc_dict["input"] = variants[fb]
                        cache_eco[key_cache] = variants[fb]
                        break
            return exc_dict
        # ===================================================================

        fg_db = bw.Database(database_name)
        base_acts = list(fg_db)
        relevant = [a for a in base_acts if any("DEALA" in exc.input["database"] for exc in a.technosphere())]

        new_keys = set()
        written = 0

        # === MAIN LOOP ===
        for act in tqdm(relevant, desc=f"Regionalizing {database_name}"):
            act_name = act["name"]
            act_ref = act.get("reference product", act_name)
            act_unit = act.get("unit", "unit")
            act_code = act["code"]

            dealas_in_act = [exc for exc in act.technosphere() if "DEALA" in exc.input["database"]]
            if not dealas_in_act:
                continue

            for exc in dealas_in_act:
                nm = str(exc.input["name"]).lower().strip()
                rp = str(exc.input["reference product"]).lower().strip()
                variants = {loc: k for (n, r, loc), k in deala_fwd.items() if (n, r) == (nm, rp)}
                if len(variants) <= 1:
                    continue

                for loc, d_key in variants.items():
                    if loc == "GLO":
                        continue

                    new_exchanges = []
                    for ex in act.exchanges():
                        ex_dict = {
                            "input": ex.input.key,
                            "amount": float(ex.amount),
                            "type": ex.get("type", "technosphere"),
                        }
                        ex_name = str(ex.input.get("name", "")).lower().strip()
                        ex_ref = str(ex.input.get("reference product", "")).lower().strip()
                        ex_dict = replace_deala_input_if_possible(ex_dict, loc)
                        ex_dict = replace_ecoinvent_input_if_possible(ex_dict, loc, ex_name, ex_ref)
                        new_exchanges.append(ex_dict)

                    new_code = f"{act_code}_{loc}"
                    act_data = {
                        "name": act_name,
                        "unit": act_unit,
                        "location": loc,
                        "reference product": act_ref,
                        "code": new_code,
                        "type": "process",
                        "database": database_name,
                        "production amount": 1.0,
                        "exchanges": new_exchanges + [
                            {"input": (database_name, new_code), "amount": 1.0, "type": "production"}
                        ],
                    }

                    # === CRITICAL FIX: Make exchanges Brightway-safe ===
                    act_data["exchanges"] = fix_exchanges_for_index(
                        act_data["exchanges"], database_name, new_code
                    )
                    # ==================================================

                    pickled_act = pickle.dumps(act_data, protocol=pickle.HIGHEST_PROTOCOL)
                    cur.execute(
                        "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                        (database_name, new_code, pickled_act),
                    )

                    for ex in act_data["exchanges"]:
                        in_db, in_code = ex["input"]
                        pickled_ex = pickle.dumps(ex, protocol=pickle.HIGHEST_PROTOCOL)
                        cur.execute(
                            "INSERT INTO exchangedataset (input_database, input_code, output_database, output_code, type, data) VALUES (?, ?, ?, ?, ?, ?)",
                            (in_db, in_code, database_name, new_code, ex.get("type", "technosphere"), pickled_ex),
                        )

                    new_keys.add((database_name, new_code))
                    written += 1
                    if written % commit_every == 0:
                        conn.commit()
                        print(f"[INFO] Committed {written} new activities...")

        # === Final ===
        conn.commit()
        conn.close()

        if new_keys:
            mapping.add(new_keys)

        try:
            bw.Database(database_name).process()
            print(f"[PROCESS] {database_name} processed successfully.")
        except Exception as e:
            print(f"[WARN] {database_name} process failed: {e}")

        print(f"\n✅ Finished regionalizing {database_name}")
        print(f"[INFO] Total new activities: {written}")
        print(f"[INFO] Duration: {round(time.time() - t0, 2)}s")

        return written



    def copy_and_add_DEALA_activity_fast(self, dict_databases, dict_target, dict_activities,
                                        overwrite=False, debug=True):
        """
        Ultra-fast direct-SQL version to copy Energy activities and link DEALA activities.
        Immediately usable for LCI/LCIA after creation.
        """

        # --- Local internal Brightway-safe exchange fixer ---
        def fix_exchanges_for_index(exchanges, output_db, output_code):
            """
            Ensure all exchanges have required fields so Brightway indexing and bw.copy()
            can detect them.
            """
            fixed = []
            for ex in exchanges:
                ex_new = ex.copy()
                ex_new["output"] = (output_db, output_code)
                ex_new["type"] = ex_new.get("type", "technosphere")
                ex_new["amount"] = float(ex_new.get("amount", 0.0))
                fixed.append(ex_new)
            return fixed

        # === Locate Brightway SQLite ===
        project_path = bw.projects.dir
        db_path = os.path.join(project_path, "lci", "databases.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"[ERROR] Brightway SQLite DB not found:\n{db_path}")

        # === Helper: find matching DEALA DB ===
        def find_matching_deala_db(energy_db_name, available_deala_dbs):
            cleaned = energy_db_name.replace("Energy_", "").replace(" regionalized", "")
            m = re.search(r"remind_[^ ]+", cleaned)
            if not m:
                return None
            scen = m.group(0)
            for db in available_deala_dbs:
                if scen in db:
                    return db
            return None

        available_deala_dbs = [db for db in bw.databases if db.startswith("DEALA_")]
        print(f"[INFO] Found {len(available_deala_dbs)} DEALA databases.")

        conn = sqlite3.connect(db_path, timeout=120)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA busy_timeout = 300000;")
        cur.execute("PRAGMA synchronous=OFF;")
        cur.execute("PRAGMA temp_store=MEMORY;")

        new_keys = set()
        total_added = 0

        for db_target, db_source in tqdm(dict_databases.items(), desc="Building Energy DBs"):
            matching_deala_db = find_matching_deala_db(db_target, available_deala_dbs)
            if not matching_deala_db:
                print(f"[⚠️] No matching DEALA DB for {db_target}, skipping.")
                continue

            db_deala = bw.Database(matching_deala_db)

            if overwrite:
                cur.execute("DELETE FROM activitydataset WHERE database=?", (db_target,))
                cur.execute("DELETE FROM exchangedataset WHERE output_database=?", (db_target,))
                conn.commit()

            batch = []
            for act_DEALA in db_deala:
                act_name = act_DEALA["name"]
                if act_name not in dict_target:
                    continue

                energy_key = (dict_target[act_name], "GLO", db_target)
                if energy_key not in dict_activities:
                    continue

                act_energy = bw.get_activity(dict_activities[energy_key])

                # === Build exchanges ===
                orig_exchanges = []
                for exc in act_energy.exchanges():
                    orig_exchanges.append({
                        "input": exc.input.key,
                        "amount": float(exc.amount),
                        "type": exc.get("type", "technosphere")
                    })

                # Add DEALA link
                orig_exchanges.append({
                    "input": act_DEALA.key,
                    "amount": 1.0,
                    "type": "technosphere"
                })

                code_new = f"{act_DEALA['code']}_energycopy"

                # --- NEW: Fix exchanges BEFORE writing ---
                fixed_exchanges = fix_exchanges_for_index(
                    orig_exchanges + [{
                        "input": (db_target, code_new),
                        "amount": 1.0,
                        "type": "production"
                    }],
                    db_target,
                    code_new
                )

                act_data = {
                    "name": act_DEALA["name"],
                    "unit": act_energy.get("unit", "USD"),
                    "location": act_DEALA.get("location", "GLO"),
                    "reference product": act_energy.get("reference product", act_energy["name"]),
                    "code": code_new,
                    "type": "process",
                    "database": db_target,
                    "production amount": 1.0,
                    "exchanges": fixed_exchanges
                }

                batch.append(act_data)
                new_keys.add((db_target, code_new))

            # === Write batch directly (unchanged except for fixed exchanges) ===
            for act_data in batch:
                p_act = pickle.dumps(act_data, protocol=pickle.HIGHEST_PROTOCOL)
                cur.execute(
                    "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                    (act_data["database"], act_data["code"], p_act)
                )
                for exc in act_data["exchanges"]:
                    in_db, in_code = exc["input"]
                    p_exc = pickle.dumps(exc, protocol=pickle.HIGHEST_PROTOCOL)
                    cur.execute("""
                        INSERT INTO exchangedataset
                        (input_database, input_code, output_database, output_code, type, data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (in_db, in_code, act_data["database"], act_data["code"], exc["type"], p_exc))

            conn.commit()
            total_added += len(batch)

        conn.close()

        # === Mapping repair ===
        missing = {k for k in new_keys if k not in mapping.data}
        if missing:
            mapping.add(missing)
            print(f"🧩 Added {len(missing)} new mappings.")

        # === Process all Energy DBs ===
        for db_name in [d for d in bw.databases if d.startswith("Energy_")]:
            try:
                bw.Database(db_name).process()
            except Exception as e:
                print(f"⚠️ {db_name}: {e}")

        print(f"\n🎉 Finished adding DEALA links to {len(dict_databases)} Energy DBs ({total_added} total activities).")


    def update_exchanges_replace_consistent_fast(
        self, dict_matches, lst_DB_energy, lst_DB_ecoinvent,
        debug=True
    ):
        """
        Fast & consistent regionalization of technosphere exchanges in Energy DBs.
        Direct SQLite updates, including mapping repair & db.process().
        """

        # -------------------------------------------------------------
        # LOCAL HELPER – EXACTLY LIKE YOUR WORKING VERSION
        # -------------------------------------------------------------
        def fix_exchanges_for_index(exchanges, output_db, output_code):
            """Ensure exchanges have output, type, numeric amount so Brightway index works."""
            fixed = []
            for ex in exchanges:
                ex_new = ex.copy()
                ex_new["output"] = (output_db, output_code)
                ex_new["type"] = ex_new.get("type", "technosphere")
                ex_new["amount"] = float(ex_new.get("amount", 0.0))
                fixed.append(ex_new)
            return fixed

        # -------------------------------------------------------------
        # SQLite + ecoinvent lookup identical to your code
        # -------------------------------------------------------------
        geomatcher = Geomatcher()
        db_path = os.path.join(bw.projects.dir, "lci", "databases.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"SQLite database not found: {db_path}")

        conn = sqlite3.connect(db_path, timeout=120)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA busy_timeout = 300000;")
        cur.execute("PRAGMA synchronous=OFF;")
        cur.execute("PRAGMA temp_store=MEMORY;")

        eco_cache = {}
        for db_name in tqdm(lst_DB_ecoinvent, desc="Indexing ecoinvent DBs"):
            fwd, rev = {}, {}
            for act in bw.Database(db_name):
                nm = act.get("name", "")
                rp = act.get("reference product", "")
                loc = act.get("location", "GLO")
                fwd[(nm, rp, loc)] = act.key
                rev[act.key] = (nm, rp, loc)
            eco_cache[db_name] = (fwd, rev)

        def find_eco_db(db_energy):
            db_suffix = db_energy.replace("Energy_", "")
            matches = [eco for eco in lst_DB_ecoinvent if eco == db_suffix]
            if matches:
                return matches[0]
            for eco in lst_DB_ecoinvent:
                if eco in db_suffix or db_suffix in eco:
                    return eco
            return None

        cache_find_loc = {}
        def find_location(act_loc, df):
            locs = list(df.columns)
            if act_loc in locs:
                return act_loc
            try:
                return geomatcher.closest(act_loc, locs)
            except:
                for fb in ("RER", "RoW", "GLO"):
                    if fb in locs: return fb
                return locs[0]

        def cached_find_location(act_loc, df):
            key = (act_loc, tuple(df.columns))
            if key in cache_find_loc:
                return cache_find_loc[key]
            try:
                r = find_location(act_loc, df)
            except:
                r = act_loc
            cache_find_loc[key] = r
            return r

        stats = {}
        new_keys = set()

        # -------------------------------------------------------------
        # MAIN LOOP – ONLY THE EXCHANGE FIX IS CHANGED
        # -------------------------------------------------------------
        for db_energy in tqdm(lst_DB_energy, desc="Updating Energy DBs"):
            eco_db = find_eco_db(db_energy)
            if not eco_db:
                print(f"[WARN] No ecoinvent DB for {db_energy}")
                continue

            fwd, rev = eco_cache[eco_db]
            updated = attempted = failed = 0

            cur.execute("SELECT rowid, code, data FROM activitydataset WHERE database=?",
                        (db_energy,))
            for rowid, out_code, blob in cur.fetchall():

                try:
                    act = pickle.loads(blob)
                except:
                    continue

                exchs = act.get("exchanges", [])
                if not exchs:
                    continue

                act_loc = act.get("location", "GLO")

                for i, exc in enumerate(exchs):

                    if exc.get("type") != "technosphere":
                        continue
                    if not isinstance(exc.get("input"), tuple):
                        continue

                    inp = exc["input"]
                    if inp not in rev:
                        continue

                    in_name, in_rp, in_loc = rev[inp]
                    if in_loc != "GLO":
                        continue

                    key_gl = (in_name, in_rp, "GLO")
                    if key_gl not in dict_matches:
                        continue

                    entries = dict_matches[key_gl]
                    df = pd.DataFrame(
                        [[(e[0], e[1]) for e in entries]],
                        columns=[e[2] for e in entries]
                    )

                    target_loc = cached_find_location(act_loc, df)
                    if target_loc not in df.columns:
                        continue

                    tgt_name, tgt_rp = df[target_loc].values[0]
                    tgt_key = (tgt_name, tgt_rp, target_loc)
                    if tgt_key not in fwd:
                        continue

                    new_key = fwd[tgt_key]

                    # -------------------------------------------------------------
                    # THE IMPORTANT FIX:
                    # Build a CORRECT technosphere exchange by copying the original
                    # -------------------------------------------------------------
                    new_exc = exc.copy()
                    new_exc["input"] = new_key

                    # Replace exchange in the list
                    exchs[i] = new_exc

                    # -------------------------------------------------------------
                    # FIX ALL EXCHANGES IN THE ACTIVITY
                    # -------------------------------------------------------------
                    fixed = fix_exchanges_for_index(exchs, db_energy, out_code)
                    act["exchanges"] = fixed

                    # Find the fixed exchange that matches new_key
                    fixed_exc = next(
                        (x for x in fixed if x.get("type") == "technosphere"
                            and x.get("input") == new_key),
                        new_exc
                    )

                    # -------------------------------------------------------------
                    # Write to SQLite
                    # -------------------------------------------------------------
                    p_act = pickle.dumps(act, protocol=pickle.HIGHEST_PROTOCOL)
                    p_exc = pickle.dumps(fixed_exc, protocol=pickle.HIGHEST_PROTOCOL)

                    old_in_db, old_in_code = inp
                    new_in_db, new_in_code = new_key

                    try:
                        cur.execute("BEGIN;")

                        cur.execute(
                            "UPDATE activitydataset SET data=? WHERE rowid=?",
                            (p_act, rowid)
                        )

                        cur.execute("""
                            DELETE FROM exchangedataset
                            WHERE input_database=? AND input_code=?
                            AND output_database=? AND output_code=?
                            AND type='technosphere'
                        """, (old_in_db, old_in_code, db_energy, out_code))

                        cur.execute("""
                            INSERT INTO exchangedataset
                            (input_database, input_code, output_database, output_code, type, data)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (new_in_db, new_in_code, db_energy, out_code, "technosphere", p_exc))

                        conn.commit()
                        updated += 1
                        new_keys.add(new_key)

                    except Exception as e:
                        conn.rollback()
                        failed += 1
                        if debug: print(f"[WARN] {db_energy}/{out_code}: {e}")

                attempted += 1

            stats[db_energy] = dict(attempted=attempted, updated=updated, failed=failed)

        conn.close()
        gc.collect()

        # Mapping repair
        missing = {k for k in new_keys if k not in mapping.data}
        if missing: mapping.add(missing)

        # Rebuild
        for db in lst_DB_energy:
            try:
                bw.Database(db).process()
            except Exception as e:
                print(f"[WARN] {db}: {e}")

        return stats



    def regionalize_processes_foreground(self, database_name, dict_countries, commit_every=4000):
        """
        Fast and reliable regionalization of all processes in a Brightway database.
        """

        import os, sqlite3, pickle
        import brightway2 as bw
        from tqdm import tqdm
        from bw2data import mapping
        from constructive_geometries import Geomatcher

        # ============================================================
        # LOCAL FIX: Brightway-safe exchange correction
        # ============================================================
        def fix_exchanges_for_index(exchanges, output_db, output_code):
            fixed = []
            for ex in exchanges:
                ex_new = ex.copy()
                ex_new["output"] = (output_db, output_code)
                ex_new["type"] = ex_new.get("type", "technosphere")
                ex_new["amount"] = float(ex_new.get("amount", 0.0))
                fixed.append(ex_new)
            return fixed
        # ============================================================

        # ----------------- Helpers -----------------
        def norm_loc(loc):
            if isinstance(loc, (tuple, list)):
                return loc[-1]
            return loc or "GLO"

        def extract_exchange_dict(exc):
            try:
                in_key = exc.input.key
                in_name = exc.input.get("name", "")
                in_db = exc.input.get("database", "")
                in_ref = exc.input.get("reference product", "")
                amount = float(getattr(exc, "amount", None) or exc.get("amount", 0.0))
                typ = getattr(exc, "type", None) or exc.get("type", "technosphere")
            except Exception:
                in_key = exc.get("input")
                if not in_key:
                    return None
                in_name = exc.get("_bw_name", "")
                in_db = exc.get("_bw_db", in_key[0] if isinstance(in_key, tuple) else "")
                in_ref = exc.get("_bw_ref", "")
                amount = float(exc.get("amount", 0.0))
                typ = exc.get("type", "technosphere")

            return {
                "input": in_key,
                "amount": amount,
                "type": typ,
                "_bw_name": in_name,
                "_bw_ref": in_ref,
                "_bw_db": in_db,
            }

        # ----------------- Setup -----------------
        geomatcher = Geomatcher()
        fg_db = bw.Database(database_name)
        activities = list(fg_db)

        db_path = os.path.join(bw.projects.dir, "lci", "databases.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Brightway SQLite not found: {db_path}")

        conn = sqlite3.connect(db_path, timeout=300)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA busy_timeout = 300000;")
        cur.execute("PRAGMA synchronous=OFF;")
        cur.execute("PRAGMA temp_store=MEMORY;")

        # ----------------- Phase 1 -----------------
        print(f"[PHASE 1] Preparing copies for {len(activities)} activities …")
        new_acts = []
        self_index = {}
        referenced_dbs = set()

        for act in tqdm(activities, desc="Create in-memory copies"):
            act_name = act.get("name", "")
            act_ref = act.get("reference product", act_name)
            act_unit = act.get("unit", "unit")
            act_code = act.get("code")
            act_type = act.get("type", "process")

            orig_tech = []
            for exc in act.technosphere():
                ed = extract_exchange_dict(exc)
                if ed:
                    orig_tech.append(ed)
                    if isinstance(ed["input"], tuple):
                        referenced_dbs.add(ed["_bw_db"])

            for country in dict_countries.values():
                new_code = f"{act_code}_{country}"
                new_act = {
                    "name": act_name,
                    "reference product": act_ref,
                    "unit": act_unit,
                    "code": new_code,
                    "type": act_type,
                    "location": country,
                    "database": database_name,
                    "exchanges": [],
                }
                new_acts.append(new_act)
                self_index[(act_name, act_ref, country)] = (database_name, new_code)

        referenced_dbs.add(database_name)

        # ----------------- Phase 2 -----------------
        print(f"[PHASE 2] Building indices for {len(referenced_dbs)} referenced DBs …")

        fwd_index = {}
        rev_index = {}

        for dbn in tqdm(sorted(referenced_dbs), desc="Index DBs"):
            cur.execute("SELECT data FROM activitydataset WHERE database=?", (dbn,))
            rows = cur.fetchall()
            fwd = {}
            for (blob,) in rows:
                a = pickle.loads(blob)
                nm = a.get("name", "")
                rp = a.get("reference product", "")
                loc = norm_loc(a.get("location", "GLO"))
                code = a.get("code")
                if not nm or not code:
                    continue
                fwd[(nm, rp, loc)] = (dbn, code)
                rev_index[(dbn, code)] = (nm, rp, loc)
            fwd_index[dbn] = fwd

        # ----------------- Phase 3 -----------------
        print(f"[PHASE 3] Rewiring exchanges in memory …")

        orig_tech_by_key = {}
        for act in activities:
            nm = act.get("name", "")
            rp = act.get("reference product", nm)
            orig_tech_by_key[(nm, rp)] = [extract_exchange_dict(exc) for exc in act.technosphere()]

        updates = 0

        for new_act in tqdm(new_acts, desc="Apply rewiring"):
            nm = new_act["name"]
            rp = new_act["reference product"]
            loc_target = norm_loc(new_act["location"])
            orig_list = orig_tech_by_key.get((nm, rp), [])
            new_exchs = []

            for exc in orig_list:
                if exc.get("type") != "technosphere":
                    continue
                inp = exc.get("input")
                if not isinstance(inp, tuple):
                    continue

                in_db, in_code = inp
                in_name = exc.get("_bw_name", "")
                in_ref = exc.get("_bw_ref", "")

                # ---- Self-links ----
                if in_db == database_name:
                    candidate_key = (in_name, in_ref, loc_target)
                    if candidate_key in self_index:
                        new_exchs.append({"input": self_index[candidate_key], "amount": exc["amount"], "type": "technosphere"})
                        updates += 1
                        continue
                    for fb in ("RoW", "RER", "GLO"):
                        ck = (in_name, in_ref, fb)
                        if ck in self_index:
                            new_exchs.append({"input": self_index[ck], "amount": exc["amount"], "type": "technosphere"})
                            updates += 1
                            break
                    else:
                        new_exchs.append({"input": inp, "amount": exc["amount"], "type": "technosphere"})
                    continue

                # ---- External links ----
                fwd = fwd_index.get(in_db, {})
                picked = None
                for g_loc in geomatcher.within(loc_target, biggest_first=False):
                    g_loc = norm_loc(g_loc)
                    key = (in_name, in_ref, g_loc)
                    if key in fwd:
                        picked = fwd[key]
                        break
                if not picked:
                    for fb in ("GLO", "RoW", "RER"):
                        key = (in_name, in_ref, fb)
                        if key in fwd:
                            picked = fwd[key]
                            break

                if picked:
                    new_exchs.append({"input": picked, "amount": exc["amount"], "type": "technosphere"})
                    updates += 1
                else:
                    new_exchs.append({"input": inp, "amount": exc["amount"], "type": "technosphere"})

            # ---- Add production ----
            new_exchs.append({"input": (database_name, new_act["code"]), "amount": 1.0, "type": "production"})

            # =====================================================
            # LOCAL FIX APPLIED HERE:
            # Make exchanges Brightway-index-safe
            # =====================================================
            new_act["exchanges"] = fix_exchanges_for_index(
                new_exchs,
                database_name,
                new_act["code"]
            )
            # =====================================================

        print(f"[PHASE 3] Rewired {updates:,} inputs.")

        # ----------------- Phase 4 -----------------
        print(f"[PHASE 4] Writing {len(new_acts)} activities to SQLite …")
        new_keys = set()
        batch = 0

        for act in tqdm(new_acts, desc="Insert into DB"):
            p_act = pickle.dumps(act, protocol=pickle.HIGHEST_PROTOCOL)
            cur.execute(
                "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                (database_name, act["code"], p_act),
            )

            for ex in act["exchanges"]:
                in_db, in_code = ex["input"]
                p_exc = pickle.dumps(ex, protocol=pickle.HIGHEST_PROTOCOL)
                cur.execute(
                    """INSERT INTO exchangedataset
                    (input_database, input_code, output_database, output_code, type, data)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (in_db, in_code, database_name, act["code"],
                    ex.get("type", "technosphere"), p_exc),
                )

            new_keys.add((database_name, act["code"]))
            batch += 1
            if batch >= commit_every:
                conn.commit()
                batch = 0

        if batch:
            conn.commit()
        conn.close()

        # ----------------- Phase 5 -----------------
        missing = {k for k in new_keys if k not in mapping.data}
        if missing:
            mapping.add(missing)
            print(f"[INFO] Added {len(missing)} new mappings.")

        try:
            bw.Database(database_name).process()
            print(f"[PROCESS] {database_name} processed successfully.")
        except Exception as e:
            print(f"[WARN] {database_name} process failed: {e}")

        print(f"\n✅ Regionalization complete: {len(new_keys)} activities created; {updates} inputs rewired.")
        return {"created": len(new_keys), "rewired_inputs": updates}



    # === DEALA-IO function: PPP regionalization of DEALA activities ===
    def import_PPP_DEALA_activities(
        self,
        FP_ppp_excel: str,
        base_year: int = 2023,
        ppp_category_label: str = "PPP regionalized",
        batch_size: int = 1000,
        name_tokens=("consumables and supplies", "co-product", "end product"),
    ):
        """
        Internal version using Brightway-safe exchange construction.
        All exchanges are repaired using internal _fix_exchanges_for_index().
        """

        # --------------------------------------------------------
        # Internal exchange fixer (Brightway-safe)
        # --------------------------------------------------------
        def _fix(exchanges, out_db, out_code):
            fixed = []
            for ex in exchanges:
                e = ex.copy()
                e["output"] = (out_db, out_code)
                e["type"] = e.get("type", "technosphere")
                e["amount"] = float(e.get("amount", 0.0))
                fixed.append(e)
            return fixed

        # --------------------------------------------------------
        # 1. Load PPP Excel
        # --------------------------------------------------------
        df_ppp_raw = pd.read_excel(FP_ppp_excel)
        if base_year not in df_ppp_raw.columns:
            raise ValueError(f"PPP Excel must contain column '{base_year}'.")

        def iso3_to_iso2(iso3):
            try:
                return pycountry.countries.get(alpha_3=str(iso3)).alpha_2
            except Exception:
                return None

        df_ppp_raw["ISO2"] = df_ppp_raw["Country Code"].apply(iso3_to_iso2)
        df_ppp = df_ppp_raw.loc[df_ppp_raw["ISO2"].notna(), ["ISO2", base_year]]
        df_ppp = df_ppp.rename(columns={base_year: "PPP_value"}).dropna()
        ppp_list = list(df_ppp.itertuples(index=False, name=None))
        print(f"[INFO] Loaded PPP data for {len(ppp_list)} countries (year {base_year}).")

        # --------------------------------------------------------
        # 2. Brightway SQLite path
        # --------------------------------------------------------
        project_path = bw.projects.dir
        db_path_main = os.path.join(project_path, "lci", "databases.db")
        if not os.path.exists(db_path_main):
            raise FileNotFoundError(f"databases.db not found: {db_path_main}")

        # --------------------------------------------------------
        # 3. Safe multiply
        # --------------------------------------------------------
        def safe_amount(x, factor):
            try:
                base = 0.0 if x is None or np.isnan(x) else float(x)
                v = float(factor) * base
                return 0.0 if np.isnan(v) or np.isinf(v) else v
            except Exception:
                return 0.0

        # --------------------------------------------------------
        # 4. Process all DEALA DBs
        # --------------------------------------------------------
        new_keys = set()

        for db_name in [d for d in bw.databases if d.startswith("DEALA_activities_")]:
            print(f"\n[INFO] PPP regionalizing {db_name} …")

            conn = sqlite3.connect(db_path_main, timeout=120)
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute("PRAGMA synchronous=OFF;")
            cur.execute("BEGIN;")
            conn.commit()

            # ---- load base acts
            cur.execute("SELECT code, data FROM activitydataset WHERE database=?", (db_name,))
            rows = cur.fetchall()

            base_acts = []

            for code, pdata in rows:
                act = pickle.loads(pdata)
                nm = act.get("name", "").lower()
                if not any(tok in nm for tok in name_tokens):
                    continue

                # Find marketsphere exchange
                cur.execute(
                    """
                    SELECT data FROM exchangedataset
                    WHERE output_database=? AND output_code=? AND input_database='marketsphere'
                    """,
                    (db_name, code)
                )
                ms_rows = cur.fetchall()
                if not ms_rows:
                    continue

                exc = pickle.loads(ms_rows[0][0])

                base_acts.append({
                    "name": act["name"],
                    "unit": act.get("unit", "unit"),
                    "ref_prod": act.get("reference product", act["name"]),
                    "code": code,
                    "type": act.get("type", "process"),
                    "base_amount": exc.get("amount", 0.0),
                    "ms_input_key": exc.get("input", ("marketsphere", None)),
                })

            print(f"  → Found {len(base_acts)} PPP base activities")

            # Already existing codes (avoid duplicates)
            cur.execute("SELECT code FROM activitydataset WHERE database=?", (db_name,))
            existing_codes = {r[0] for r in cur.fetchall()}

            batch = []

            for ba in tqdm(base_acts, desc=db_name):
                for iso2, factor in ppp_list:

                    new_code = f"{ba['code']}_{iso2}"
                    if new_code in existing_codes:
                        continue

                    # --- build exchanges ---
                    bio_exc = {
                        "input": ba["ms_input_key"],
                        "amount": safe_amount(ba["base_amount"], factor),
                        "type": "biosphere",
                    }
                    prod_exc = {
                        "input": (db_name, new_code),
                        "amount": 1.0,
                        "type": "production",
                    }

                    # --- fix exchanges (IMPORTANT) ---
                    fixed_exchanges = _fix([bio_exc, prod_exc], db_name, new_code)

                    # --- assemble activity ---
                    act_data = {
                        "name": ba["name"],
                        "unit": ba["unit"],
                        "location": iso2,
                        "reference product": ba["ref_prod"],
                        "code": new_code,
                        "type": ba["type"],
                        "database": db_name,
                        "production amount": 1.0,
                        "categories": (ppp_category_label, iso2),
                        "exchanges": fixed_exchanges,
                    }

                    pickled_act = pickle.dumps(act_data, protocol=pickle.HIGHEST_PROTOCOL)

                    # --- exchange inserts ---
                    exc_rows = []
                    for ex in fixed_exchanges:
                        in_db, in_code = ex["input"]
                        exc_rows.append(
                            (
                                in_db, in_code,
                                db_name, new_code,
                                ex["type"],
                                pickle.dumps(ex, protocol=pickle.HIGHEST_PROTOCOL),
                            )
                        )

                    batch.append((db_name, new_code, pickled_act, exc_rows))
                    new_keys.add((db_name, new_code))
                    existing_codes.add(new_code)

                    if len(batch) >= batch_size:
                        cur.execute("BEGIN;")
                        for dbn, code, pact, exr in batch:
                            cur.execute(
                                "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                                (dbn, code, pact),
                            )
                            cur.executemany(
                                "INSERT INTO exchangedataset (input_database, input_code, output_database, output_code, type, data) VALUES (?, ?, ?, ?, ?, ?)",
                                exr,
                            )
                        conn.commit()
                        batch.clear()

            # Remaining batch
            if batch:
                cur.execute("BEGIN;")
                for dbn, code, pact, exr in batch:
                    cur.execute(
                        "INSERT OR REPLACE INTO activitydataset (database, code, data) VALUES (?, ?, ?)",
                        (dbn, code, pact),
                    )
                    cur.executemany(
                        "INSERT INTO exchangedataset (input_database, input_code, output_database, output_code, type, data) VALUES (?, ?, ?, ?, ?, ?)",
                        exr,
                    )
                conn.commit()

            conn.close()

        # --------------------------------------------------------
        # 5. Mapping update
        # --------------------------------------------------------
        missing = {k for k in new_keys if k not in mapping.data}
        if missing:
            mapping.add(missing)
            print(f"[INFO] Added {len(missing)} new mappings.")

        # --------------------------------------------------------
        # 6. Rebuild BW matrices
        # --------------------------------------------------------
        for db_name in [d for d in bw.databases if d.startswith("DEALA_activities_")]:
            try:
                bw.Database(db_name).process()
            except Exception as e:
                print(f"[WARN] process() failed for {db_name}: {e}")

import os
import pandas as pd
from datetime import datetime, timedelta
import logging
import re
import string
from copy import deepcopy
import configparser
from importlib.resources import files
import subprocess

logger = logging.getLogger(__name__)

class ProjectData:
    def __init__(self, project_directory=None):
        self.project_directory = project_directory
        self.data = {}
        self.project_metadata = {
            "project_name": os.path.basename(project_directory) if project_directory else "UnnamedProject",
            "created_at": datetime.now()
        }
        self.metadata = _MetadataAccessor(self)
        self.time_index = _time_index(self)

        if project_directory:
            self.load(project_directory)

    def load(self, project_directory):
        self.project_directory = project_directory

        #Prüfen ob config.ini vorhanden ist
        config_path = os.path.join(project_directory, "config.ini")
        if not os.path.isfile(config_path):
            logger.error(f"Not a valid BiVital-Project: '{config_path}' is missing.")
            return
        config = configparser.ConfigParser()
        config.read(config_path)

        if not config.has_section("General") or not config.getboolean("General", "bivital_data", fallback=False):
            logger.error(f"Not a valid BiVital-Project: 'bivital_data' is not True in {config_path}\n Wrong project folder or no Data in it.")
            return
        
        skip_dirs = {
            "__pycache__",
            ".git", ".idea", ".vscode",
            ".mypy_cache", ".pytest_cache", ".tox",
            "env", "venv", ".venv",
            "build", "dist", "__MACOSX"
        }
        
        # Sicherstellen, dass die Projektstruktur gültig ist
        found_series = 0
        found_csv = 0

        for series_name in sorted(os.listdir(project_directory)):
            if series_name.startswith(".") or series_name in skip_dirs:
                continue
            series_path = os.path.join(project_directory, series_name)
            if not os.path.isdir(series_path):
                continue

            # Check for unexpected CSVs directly in the series folder
            unexpected_csvs = [
                f for f in os.listdir(series_path)
                if os.path.isfile(os.path.join(series_path, f)) and f.endswith(".csv")
            ]
            if unexpected_csvs:
                logger.warning(
                    f"Unexpected CSV file(s) found directly in '{series_path}' \nwithout a subfolder: {unexpected_csvs}. "
                    "They will be ignored. Each CSV must be placed inside its own data folder."
                )

            has_csv = False
            for dataset_folder in os.listdir(series_path):
                dataset_path = os.path.join(series_path, dataset_folder)
                if not os.path.isdir(dataset_path):
                    continue
                for filename in os.listdir(dataset_path):
                    if filename.endswith(".csv"):
                        has_csv = True
                        break
                if has_csv:
                    break

            if has_csv:
                found_series += 1
                found_csv += 1

        if found_series == 0 or found_csv == 0:
            raise RuntimeError("Invalid project structure: At least one series with at least one .csv file is required.")
        
        for series_name in sorted(os.listdir(project_directory)):
            if series_name.startswith(".") or series_name in skip_dirs:
                continue
            if series_name in skip_dirs:
                continue
            series_path = os.path.join(project_directory, series_name)
            if not os.path.isdir(series_path):
                continue

            self.data[series_name] = {
                "datasets": {},
                "summary": {},
                "series_metadata": {},
                "labels": None
            }

            self._load_labels(series_name)

            for dataset_folder in sorted(os.listdir(series_path)):
                if dataset_folder.lower() == "label":
                    continue

                dataset_path = os.path.join(series_path, dataset_folder)
                if not os.path.isdir(dataset_path):
                    continue

                for filename in sorted(os.listdir(dataset_path)):
                    if not filename.endswith(".csv"):
                        continue

                    file_path = os.path.join(dataset_path, filename)
                    dataset_key = f"{dataset_folder}_{filename.replace('.csv', '')}"

                    dataset_result = self.__read_in__(file_path, series_name, dataset_key)
                    if dataset_result is None:
                        continue

                    df, metadata = dataset_result
                    self.data[series_name]["datasets"][dataset_key] = {
                        "df": df,
                        "metadata": metadata
                    }

            all_metadata = [ds["metadata"] for ds in self.data[series_name]["datasets"].values()]
            num_datasets = len(all_metadata)
            unique_configs = sorted(set(m.get("config") for m in all_metadata if m.get("config") is not None))
            config_map = {cfg: string.ascii_uppercase[i] for i, cfg in enumerate(unique_configs)}

            for meta in all_metadata:
                cfg = meta.get("config")
                meta["config_label"] = config_map.get(cfg, "?")

            self.data[series_name]["summary"] = {
                "num_datasets": num_datasets,
                "num_configs": len(unique_configs)
            }
            self.data[series_name]["series_metadata"] = {
                "mac_addresses": list({m.get("mac") for m in all_metadata if m.get("mac")}),
                "feature_union": sorted(set(f for m in all_metadata for f in m.get("features", [])))
            }

            self._add_labels_to_series(series_name)

    @classmethod
    def from_csv(cls, csv_path):

        if not os.path.isfile(csv_path):
            raise FileNotFoundError(f"File not found: {csv_path}")
        if not csv_path.endswith(".csv"):
            raise ValueError("Only .csv files are supported.")

        instance = cls(project_directory=None)
        series_name = "Series1"
        dataset_name = os.path.splitext(os.path.basename(csv_path))[0]

        # Read data using the class’s method
        dataset_result = instance.__read_in__(csv_path, series_name, dataset_name)
        if dataset_result is None:
            raise ValueError(f"Failed to read CSV: {csv_path}")

        df, metadata = dataset_result
        if "config" in metadata and metadata["config"] is not None:
            metadata["config_label"] = "A"

        instance.project_metadata["project_name"] = "SingleFileProject"
        instance.data = {
            series_name: {
                "datasets": {
                    dataset_name: {
                        "df": df,
                        "metadata": metadata
                    }
                },
                "summary": {
                    "num_datasets": 1,
                    "num_configs": 1 if metadata.get("config") else 0
                },
                "series_metadata": {
                    "mac_addresses": [metadata.get("mac")] if metadata.get("mac") else [],
                    "feature_union": metadata.get("features", [])
                },
                "labels": None
            }
        }
        instance.metadata = _MetadataAccessor(instance)
        instance.time_index = _time_index(instance)

        return instance

    def __read_in__(self, csv_path, series_name, id_name):
        logger.info(f"Processing {series_name} - Log File {id_name}")

        with open(csv_path, 'r') as file:
            metadata_line_1 = file.readline().strip().split(',')
            metadata_line_2 = file.readline().strip().split(',')

        data = pd.read_csv(csv_path, skiprows=2)
        data.columns = [col.strip() for col in data.columns]

        raw_feature_names = data.columns[1:]
        features, units = [], []
        for col in raw_feature_names:
            if "[" in col and "]" in col:
                name_part = col.split("[")[0].strip()
                unit_part = col.split("[")[-1].strip("]")
                features.append(name_part)
                units.append(unit_part)
            else:
                features.append(col)
                units.append(None)

        metadata = self._parse_metadata(metadata_line_1, metadata_line_2, features, units)

        if metadata.get("mac") is None:
            logger.warning(f"Skipping {id_name} in {series_name} (No MAC Address)")
            return None

        data.columns = [data.columns[0]] + features

        if metadata["start_time"]:
            metadata["date"] = metadata["start_time"].date()
            metadata["start_time"] = metadata["start_time"].time()

        if "Time [s]" in data.columns and metadata.get("date") and metadata.get("start_time"):
            base_time = datetime.combine(metadata["date"], metadata["start_time"])
            data["Time [s]"] = [base_time + timedelta(seconds=t) for t in data["Time [s]"]]

        raw_times = pd.to_datetime(data['Time [s]'], errors='coerce').dt.time
        data.index = raw_times

        for col in data.columns[1:]:
            series = data[col].astype(str).str.strip().replace(["", "nan", "NaN", "None"], None)
            non_null = series.dropna()

            is_float_like = non_null.str.contains(r'^\s*-?\d*\.\d+(?:[eE][-+]?\d+)?\s*$', regex=True)
            is_int_like = non_null.str.contains(r'^\s*-?\d+\s*$', regex=True)

            has_other = ~(is_float_like | is_int_like)
            
            if has_other.any():
                data[col] = series.astype(str)
            elif is_float_like.any():
                data[col] = pd.to_numeric(series, errors="coerce").astype(float)
            else:
                data[col] = pd.to_numeric(series, errors="coerce").astype("Int64")

        data.drop(columns=["Time [s]"], inplace=True)

        return data, metadata

    def _parse_metadata(self, line1, line2, features, units):
        return {
            "mac": self._extract_value(line1, r"BI-Vital (\S+)", str),
            "config_label": self._extract_value(line1, r"Config #(\d+)", str),
            "date": None,
            "start_time": self._extract_value(line1, r"Start Time ([^,]+)", self._parse_time),
            "features": features,
            "STM_FW": self._extract_value(line1, r"STM_FW ([^,]+)", str),
            "NRF_FW": self._extract_value(line1, r"NRF_FW ([^,]+)", str),
            "config": self._extract_value(line1, r"Config #(\d+)", int),
            "uptime": self._extract_value(line1, r"Uptime ([^,]+)", self._parse_duration),
            "units": units,
            "update_rates": [int(x.strip()) if x.strip().isdigit() else None for x in line2[1:]]
        }

    def _extract_value(self, line, pattern, caster):
        match = re.search(pattern, ", ".join(line))
        if match:
            return caster(match.group(1))
        return None

    def _parse_time(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    def _parse_duration(self, value):
        try:
            h, m, s = map(int, value.strip().split(":"))
            return timedelta(hours=h, minutes=m, seconds=s)
        except Exception:
            return None

    def _load_labels(self, series_name):
        label_path = os.path.join(self.project_directory, series_name, "Label", "label.csv")
        if not os.path.isfile(label_path):
            return

        raw_label_df = pd.read_csv(label_path, header=None)
        clean_label_df = raw_label_df.iloc[2:].copy()
        clean_label_df.columns = ['BaseTime', 'Rest']
        clean_label_df = clean_label_df.dropna()

        clean_label_df[['Milliseconds', 'Label']] = clean_label_df['Rest'].str.split(';', expand=True)
        clean_label_df['FullTimeStr'] = (clean_label_df['BaseTime'] + ',' + clean_label_df['Milliseconds']).str.replace(',', '.', regex=False)
        clean_label_df['Time'] = clean_label_df['FullTimeStr'].apply(
            lambda t: datetime.strptime(t, "%H:%M:%S.%f").time()
        )
        final_labels = clean_label_df[['Time', 'Label']].reset_index(drop=True)

        self.data[series_name]["labels"] = final_labels

    def _add_labels_to_series(self, series_name):
        if "labels" not in self.data[series_name] or self.data[series_name]["labels"] is None:
            return

        final_labels = self.data[series_name]["labels"]
        label_lookup = dict(zip(final_labels['Time'], final_labels['Label']))

        for dataset_key, dataset in self.data[series_name]["datasets"].items():
            logger.info(f"Adding 'Label' column to DataFrame {series_name}[{dataset_key}]")
            df = dataset["df"].copy()
            missing_times = [t for t in label_lookup if t not in df.index]
            if missing_times:
                empty_rows = pd.DataFrame(index=missing_times, columns=df.columns)
                empty_rows = empty_rows.dropna(axis=1, how='all')
                df = pd.concat([df, empty_rows])
                df = df.sort_index()
            df['Label'] = [label_lookup.get(t, None) for t in df.index]
            self.data[series_name]["datasets"][dataset_key]["df"] = df

    def __getitem__(self, indices):
        if not isinstance(indices, tuple):
            indices = (indices,)

        series_key = indices[0]
        dataset_key = indices[1] if len(indices) > 1 else None
        feature_key = indices[2] if len(indices) > 2 else None
        row_key = indices[3] if len(indices) > 3 else None

        def _filtered_instance(filtered_data):
            new_instance = ProjectData()
            new_instance.project_directory = self.project_directory
            new_instance.project_metadata = deepcopy(self.project_metadata)
            new_instance.data = filtered_data
            new_instance.metadata = _MetadataAccessor(new_instance)
            return new_instance

        def resolve(keys, available):
            if keys is None:
                return available
            elif isinstance(keys, slice):
                return available[keys]
            elif isinstance(keys, list):
                return [k if isinstance(k, str) else available[k] for k in keys]
            elif isinstance(keys, int):
                return [available[keys]]
            elif isinstance(keys, str):
                return [keys]
            else:
                raise TypeError(f"Unsupported key type: {type(keys)}")

        selected_series = resolve(series_key, list(self.data.keys()))
        multi_series = len(selected_series) > 1

        filtered_data = {}
        for s in selected_series:
            if s not in self.data:
                raise KeyError(f"Series '{s}' not found")

            series_data = self.data[s]
            selected_datasets = resolve(dataset_key, list(series_data["datasets"].keys()))
            multi_dataset = len(selected_datasets) > 1

            new_series = deepcopy(series_data)
            new_series["datasets"] = {}

            for d in selected_datasets:
                if d not in series_data["datasets"]:
                    raise KeyError(f"Dataset '{d}' not found in series '{s}'")
                df = series_data["datasets"][d]["df"]

                # Filter Features
                if feature_key is None:
                    selected_df = df
                elif isinstance(feature_key, slice):
                    selected_df = df.iloc[:, feature_key]
                elif isinstance(feature_key, int):
                    selected_df = df.iloc[:, [feature_key]]
                elif isinstance(feature_key, list):
                    selected_df = df[feature_key]
                elif isinstance(feature_key, str):
                    selected_df = df[[feature_key]]
                else:
                    raise TypeError("Invalid feature key")

                # Filter Rows
                if row_key is None:
                    final_df = selected_df
                elif isinstance(row_key, int):
                    final_df = selected_df.iloc[[row_key]]
                elif isinstance(row_key, slice):
                    final_df = selected_df.iloc[row_key]
                elif isinstance(row_key, list):
                    final_df = selected_df.iloc[row_key]
                else:
                    final_df = selected_df.loc[[row_key]]

                new_series["datasets"][d] = {
                    "df": final_df,
                    "metadata": deepcopy(series_data["datasets"][d]["metadata"])
                }

            filtered_data[s] = new_series

            # Falls Labels existieren, übernehmen
            if "labels" in series_data:
                filtered_data[s]["labels"] = deepcopy(series_data["labels"])

        if len(selected_series) == 1 and not multi_dataset:
            # Einzel-DataFrame zurückgeben
            s = selected_series[0]
            d = resolve(dataset_key, list(self.data[s]["datasets"].keys()))[0]
            return filtered_data[s]["datasets"][d]["df"]

        return _filtered_instance(filtered_data)
    
    def time_range(self, series=None):
        """
        Compute time ranges for the project or for specific series.

        Returns a dictionary where keys are series names and values are time range dictionaries.
        """
        
        def resolve(keys, available):
            if keys is None:
                return available
            elif isinstance(keys, slice):
                return available[keys]
            elif isinstance(keys, list):
                return [k if isinstance(k, str) else available[k] for k in keys]
            elif isinstance(keys, int):
                return [available[keys]]
            elif isinstance(keys, str):
                return [keys]
            else:
                raise TypeError(f"Unsupported key type: {type(keys)}")

        available_series = list(self.data.keys())
        selected_series = resolve(series, available_series)

        if not selected_series:
            raise ValueError("No valid series selected.")

        result = {}
        for s in selected_series:
            if s not in self.data:
                raise KeyError(f"Series '{s}' not found")

            logger.info(f"Calculating time range of series '{s}'")

            datasets = self.data[s]["datasets"]
            if not datasets:
                result[s] = None
                continue

            # --- OVERALL START/END ---
            overall_start_dataset = min(
                ((name, ds["df"].index[0]) for name, ds in datasets.items()), key=lambda x: x[1]
            )
            overall_end_dataset = max(
                ((name, ds["df"].index[-1]) for name, ds in datasets.items()), key=lambda x: x[1]
            )

            # --- VALID RANGE (DROP rows with all-NaN) ---
            valid_indices = {
                name: ds["df"].dropna(how="all").index
                for name, ds in datasets.items()
                if not ds["df"].dropna(how="all").empty
            }

            if not valid_indices:
                result[s] = None
                continue

            valid_start_dataset = max(
                ((name, idx[0]) for name, idx in valid_indices.items()), key=lambda x: x[1]
            )
            valid_end_dataset = min(
                ((name, idx[-1]) for name, idx in valid_indices.items()), key=lambda x: x[1]
            )

            result[s] = {
                "overall_start_time": overall_start_dataset[1],
                "overall_end_time": overall_end_dataset[1],
                "valid_start_time": valid_start_dataset[1],
                "valid_end_time": valid_end_dataset[1],
                "overall_start_dataset": overall_start_dataset[0],
                "overall_end_dataset": overall_end_dataset[0],
                "valid_start_dataset": valid_start_dataset[0],
                "valid_end_dataset": valid_end_dataset[0],
            }

        return result

    def smallest_update_rates(self, series=None):
        """
        Returns the smallest update rate per config label.

        - If `series` is None: returns a dict for all series
        { 'Series1': {'config_A': 25, 'config_B': 50}, ... }
        - If `series` is specified (name, index, slice, or list): returns matching subset
        e.g. { 'Series2': {'config_A': 20} }
        """

        def resolve(keys, available):
            if keys is None:
                return available
            elif isinstance(keys, slice):
                return available[keys]
            elif isinstance(keys, list):
                return [k if isinstance(k, str) else available[k] for k in keys]
            elif isinstance(keys, int):
                return [available[keys]]
            elif isinstance(keys, str):
                return [keys]
            else:
                raise TypeError(f"Unsupported key type: {type(keys)}")

        available_series = list(self.data.keys())
        selected_series = resolve(series, available_series)

        result = {}
        for s in selected_series:
            if s not in self.data:
                raise KeyError(f"Series '{s}' not found")

            datasets = self.data[s]["datasets"]
            seen_labels = {}

            for dataset_key, dataset in datasets.items():
                metadata = dataset["metadata"]
                label = metadata.get("config_label")
                if label is not None:
                    config_key = f"config_{label}"
                    rates = metadata.get("update_rates", [])
                    rates = [r for r in rates if r is not None]
                    min_rate = min(rates) if rates else None

                    if config_key not in seen_labels:
                        seen_labels[config_key] = min_rate
                    else:
                        if min_rate is not None and (seen_labels[config_key] is None or min_rate < seen_labels[config_key]):
                            seen_labels[config_key] = min_rate

            result[s] = seen_labels

        return result

    def interpolate(self, method="linear", inplace=False, region=None):
            def resolve(keys, available):
                if keys is None:
                    return available
                elif isinstance(keys, slice):
                    return available[keys]
                elif isinstance(keys, list):
                    return [k if isinstance(k, str) else available[k] for k in keys]
                elif isinstance(keys, int):
                    return [available[keys]]
                elif isinstance(keys, str):
                    return [keys]
                else:
                    raise TypeError(f"Unsupported key type: {type(keys)}")

            # Copy or work in place
            if inplace:
                new_data = self.data
            else:
                new_data = deepcopy(self.data)

            all_series = list(new_data.keys())
            series_keys = resolve(region[0] if region and len(region) > 0 else None, all_series)

            for s in series_keys:
                if s not in new_data:
                    raise KeyError(f"Series '{s}' not found")
                datasets = new_data[s]["datasets"]
                all_datasets = list(datasets.keys())
                dataset_keys = resolve(region[1] if region and len(region) > 1 else None, all_datasets)

                for d in dataset_keys:
                    if d not in datasets:
                        raise KeyError(f"Dataset '{d}' not found in series '{s}'")
                    df = datasets[d]["df"]
                    all_features = list(df.columns)
                    feature_keys = resolve(region[2] if region and len(region) > 2 else None, all_features)

                    for f in feature_keys:
                        if f not in df.columns:
                            raise KeyError(f"Feature '{f}' not found in dataset '{d}' of series '{s}'")
                        # Only interpolate numeric columns
                        if pd.api.types.is_numeric_dtype(df[f]):
                            df[f] = df[f].interpolate(method=method)
                        else:
                            logger.warning(f"Skipping interpolation for non-numeric feature '{f}' in dataset '{d}' of series '{s}'")

            if inplace:
                return None

            # Return new ProjectData instance
            new_instance = type(self)()
            new_instance.project_directory = self.project_directory
            new_instance.project_metadata = deepcopy(self.project_metadata)
            new_instance.data = new_data
            new_instance.metadata = _MetadataAccessor(new_instance)
            new_instance.time_index = _time_index(new_instance)

            return new_instance

    def label_fill(self, inplace=False, region=None, start=None, end=None, label=None, method="ffill"):
        
        """
        Fill missing labels in the project data.
        Parameters:
        - inplace: If True, fill missing labels in place. Otherwise, return a new ProjectData instance with filled labels.
        - region: A list specifying the series and dataset to operate on. If None, fill all labels.
        - start: The start Label. If None, fill all labels
        - end: The end Label. If None, fill all labels
        - label: The label to fill missing values with. If None, use the last valid label.
        - method: The method to use for filling missing values. Can be 'ffill' or 'bfill'. Default is 'ffill'.
        """
 
        def resolve(keys, available):
            if keys is None:
                return available
            elif isinstance(keys, slice):
                return available[keys]
            elif isinstance(keys, list):
                return [k if isinstance(k, str) else available[k] for k in keys]
            elif isinstance(keys, int):
                return [available[keys]]
            elif isinstance(keys, str):
                return [keys]
            else:
                raise TypeError(f"Unsupported key type: {type(keys)}")

        if inplace:
            new_data = self.data
        else:
            new_data = deepcopy(self.data)

        all_series = list(new_data.keys())
        series_keys = resolve(region[0] if region and len(region) > 0 else None, all_series)

        for s in series_keys:
            if s not in new_data:
                raise KeyError(f"Series '{s}' not found")
            datasets = new_data[s]["datasets"]
            all_datasets = list(datasets.keys())
            dataset_keys = resolve(region[1] if region and len(region) > 1 else None, all_datasets)

            for d in dataset_keys:
                if d not in datasets:
                    raise KeyError(f"Dataset '{d}' not found in series '{s}'")
                df = datasets[d]["df"]
                if "Label" not in df.columns:
                    continue

                label_series = df["Label"]
                label_mask = pd.Series([True] * len(df), index=df.index)

                # Handle label-based start/end
                if isinstance(start, str):
                    start_idx = label_series[label_series == start].first_valid_index()
                    if start_idx:
                        label_mask &= df.index > start_idx

                if isinstance(end, str):
                    end_idx = label_series[label_series == end].first_valid_index()
                    if end_idx:
                        label_mask &= df.index < end_idx

                # Handle time-based start/end
                if isinstance(start, pd.Timestamp) or isinstance(start, str) and ":" in start:
                    try:
                        ts = pd.to_datetime(start).time()
                        label_mask &= df.index > ts
                    except Exception:
                        pass

                if isinstance(end, pd.Timestamp) or isinstance(end, str) and ":" in end:
                    try:
                        ts = pd.to_datetime(end).time()
                        label_mask &= df.index < ts
                    except Exception:
                        pass

                if label is not None:
                    df.loc[label_mask & df["Label"].isna(), "Label"] = label
                else:
                    if method == "ffill":
                        df["Label"] = df["Label"].ffill()
                    elif method == "bfill":
                        df["Label"] = df["Label"].bfill()
                    else:
                        raise ValueError(f"Unsupported method '{method}'. Use 'ffill' or 'bfill'.")

        if inplace:
            return None

        new_instance = type(self)()
        new_instance.project_directory = self.project_directory
        new_instance.project_metadata = deepcopy(self.project_metadata)
        new_instance.data = new_data
        new_instance.metadata = _MetadataAccessor(new_instance)
        new_instance.time_index = _time_index(new_instance)

        return new_instance

    
    def print(self, region=None):
        """
        Pretty-print information about the project or a subregion.

        Examples:
            project_data.print(region=[0])              # series overview
            project_data.print(region=[0, 0])           # dataset overview
            project_data.print(region=[0, 0, 0])        # column overview
            project_data.print(region=[0, 0, 0, 0])     # single row value
            project_data.print(region=[slice(0,2)])     # multiple series
            project_data.print(region=[0, slice(0,2)])  # multiple datasets
        """
        import pandas as pd

        def resolve(keys, available):
            """Expand slices, ints, strings, or lists into a list of valid keys."""
            if keys is None:
                return available
            elif isinstance(keys, slice):
                return available[keys]
            elif isinstance(keys, int):
                return [available[keys]]
            elif isinstance(keys, str):
                return [keys]
            elif isinstance(keys, list):
                result = []
                for k in keys:
                    result.extend(resolve(k, available))
                return result
            else:
                raise TypeError(f"Unsupported key type: {type(keys)}")

        # Parse region input
        series = datasets = column = row = None
        if region is None or region == []:
            pass
        elif isinstance(region, list) and len(region) == 1:
            series = region[0]
        elif isinstance(region, list) and len(region) == 2:
            series, datasets = region[0], region[1]
        elif isinstance(region, list) and len(region) == 3:
            series, datasets, column = region[0], region[1], region[2]
        elif isinstance(region, list) and len(region) == 4:
            series, datasets, column, row = region[0], region[1], region[2], region[3]
        else:
            raise ValueError(
                "region must be None, [], [series], [series, dataset], [series, dataset, column], or [series, dataset, column, row]"
            )

        proj_name = self.project_metadata.get("project_name", "UnnamedProject")

        # ---- PROJECT OVERVIEW
        if series is None:
            print("Metadata:")
            print(f"  Project Name: {proj_name}")
            print(f"  Series in Project ({len(self.data)}):")
            for s in self.data.keys():
                num_ds = len(self.data[s]['datasets'])
                print(f"    - {s}: {num_ds} dataset(s)")
            return

        # ---- SERIES LOOP
        all_series = list(self.data.keys())
        series_keys = resolve(series, all_series)

        for s in series_keys:
            if s not in self.data:
                print(f"[Warning] Series '{s}' not found. Skipping.")
                continue

            # ---- SERIES OVERVIEW
            if datasets is None:
                ds_names = list(self.data[s]["datasets"].keys())
                num_ds = len(ds_names)
                sum_info = self.data[s].get("summary", {})
                labels = self.data[s].get("labels")

                print("Metadata:")
                print(f"  Series Name: {s}")
                print(f"  Datasets ({num_ds}): {', '.join(ds_names)}")
                print(f"  Number of Configs: {sum_info.get('num_configs', 0)}")

                if labels is not None:
                    print("  Label File: present")
                    print("  Labels:")
                    for _, row_ in labels.iterrows():
                        print(f"    {row_['Time']} -> {row_['Label']}")
                else:
                    print("  Label File: not found")
                print("-" * 80)
                continue

            # ---- DATASET LOOP
            ds_keys = resolve(datasets, list(self.data[s]["datasets"].keys()))

            for d in ds_keys:
                if d not in self.data[s]["datasets"]:
                    print(f"[Warning] Dataset '{d}' not found in series '{s}'. Skipping.")
                    continue

                ds = self.data[s]["datasets"][d]
                df = ds["df"]
                meta = ds["metadata"]

                # ---- DATASET OVERVIEW
                if column is None:
                    print("Metadata:")
                    print(f"  Series: {s}")
                    print(f"  Dataset: {d}")
                    print(f"  BiVital MAC: {meta.get('mac', 'N/A')}")
                    print(f"  Config Label: {meta.get('config_label', 'N/A')}")
                    date = meta.get("date")
                    if date and getattr(date, "year", 1970) != 1970:
                        print(f"  Date: {date}")
                    else:
                        print("  Date: N/A")
                    print(f"  Start Time: {meta.get('start_time', 'N/A')}")
                    print(f"  Features ({len(df.columns)}): {', '.join(df.columns)}")

                    print("\nHead:")
                    print(df.head())
                    print("\nTail:")
                    print(df.tail())
                    print("-" * 80)
                    continue

                # ---- COLUMN / FEATURE OVERVIEW
                features = list(df.columns)
                if isinstance(column, int):
                    if column < 0 or column >= len(features):
                        raise IndexError(f"Feature index {column} out of range (0..{len(features)-1}).")
                    feat_name = features[column]
                else:
                    feat_name = column
                    if feat_name not in df.columns:
                        raise KeyError(f"Feature '{feat_name}' not found in dataset '{d}'.")

                units = meta.get("units", []) or []
                update_rates = meta.get("update_rates", []) or []
                idx = features.index(feat_name)
                unit = units[idx] if idx < len(units) else None
                upd = update_rates[idx] if idx < len(update_rates) else None

                if row is None:
                    print("Metadata:")
                    print(f"  Feature: {feat_name}")
                    print(f"  Unit: {unit}")
                    print(f"  Update rate: {upd}")
                    print("\nData:")
                    print(df[feat_name])
                    print("-" * 80)
                    continue

                # ---- SINGLE CELL / ROW
                if isinstance(row, int):
                    if row < -len(df) or row >= len(df):
                        raise IndexError(f"Row index {row} out of range for {len(df)} rows.")
                    idx_label = df.index[row]
                    value = df.iloc[row][feat_name]
                else:
                    label = row
                    if label not in df.index:
                        try:
                            ts = pd.to_datetime(label).time()
                            label = ts
                        except Exception:
                            pass
                    if label not in df.index:
                        raise KeyError(f"Row label '{row}' not found in index.")
                    idx_label = label
                    value = df.at[label, feat_name]

                print("Metadata:")
                print(f"  {'Feature':15} {feat_name}")
                print(f"  {'Unit':15} {unit}")
                print(f"  {'Update rate':15} {upd}")
                print("\nData:")
                print(f"  {idx_label}    {value}")
                print("-" * 80)




class _MetadataAccessor:
    def __init__(self, project_data):
        self._project_data = project_data

    def __getitem__(self, indices):
        if indices is None:
            return self._project_data.project_metadata

        if not isinstance(indices, tuple):
            indices = (indices,)

        if len(indices) > 3:
            raise IndexError(
                f"Metadata access only supports up to 3 indices "
                f"(series, dataset, feature). Got {len(indices)}."
            )

        keys = list(self._project_data.data.keys())
        series = keys[indices[0]] if isinstance(indices[0], int) else indices[0]
        if isinstance(indices[0], int) and (indices[0] < 0 or indices[0] >= len(keys)):
            raise IndexError(f"Series index {indices[0]} out of range. Max index is {len(keys) - 1}.")
        if isinstance(series, str) and series not in self._project_data.data:
            raise KeyError(f"Series '{series}' not found. Available: {keys}")

        data = self._project_data.data[series]

        if len(indices) == 1:
            return {
                "series_name": series,
                "datasets": list(data["datasets"].keys()),
                "num_configs": data["summary"].get("num_configs")
            }

        dataset_keys = list(data["datasets"].keys())
        dataset = dataset_keys[indices[1]] if isinstance(indices[1], int) else indices[1]
        if isinstance(indices[1], int) and (indices[1] < 0 or indices[1] >= len(dataset_keys)):
            raise IndexError(f"Dataset index {indices[1]} out of range. Max index is {len(dataset_keys) - 1}.")
        if isinstance(dataset, str) and dataset not in data["datasets"]:
            raise KeyError(f"Dataset '{dataset}' not found. Available: {dataset_keys}")

        metadata = data["datasets"][dataset]["metadata"].copy()
        metadata.pop("units", None)
        metadata.pop("update_rate_global", None)
        metadata.pop("update_rates", None)
        metadata["features"] = data["datasets"][dataset]["df"].columns.tolist()

        if len(indices) == 3:
            feature_index = indices[2]
            features = data["datasets"][dataset]["df"].columns.tolist()
            units = data["datasets"][dataset]["metadata"].get("units", [])
            update_rates = data["datasets"][dataset]["metadata"].get("update_rates", [])
            feature = features[feature_index] if isinstance(feature_index, int) else feature_index

            return {
                "name": feature,
                "unit": units[features.index(feature)] if feature in features else None,
                "update_rate": update_rates[features.index(feature)] if feature in features else None
            }

        return metadata

    def __str__(self):
        keys = list(self._project_data.data.keys())
        return f"Project '{self._project_data.project_metadata['project_name']}' with series: {keys}"
    
class _time_index:
    def __init__(self, project_data):
        self._project_data = project_data

    def generate_uniform(self, start_time, end_time, interval_ms):
        from datetime import datetime, timedelta, time

        def to_time(t):
            if isinstance(t, time):
                return t
            for fmt in ("%H:%M:%S.%f", "%H:%M:%S"):
                try:
                    return datetime.strptime(t, fmt).time()
                except ValueError:
                    continue
            raise ValueError(f"Invalid time format: {t}")
        
        start_time = to_time(start_time)
        end_time = to_time(end_time)

        base_date = datetime(2000, 1, 1)
        start_dt = datetime.combine(base_date, start_time)
        end_dt = datetime.combine(base_date, end_time)

        current = start_dt
        delta = timedelta(milliseconds=interval_ms)
        times = []
        while current <= end_dt:
            times.append(current.time())
            current += delta

        return times
    
    def apply(self, new_time_index, inplace=False, region=None):

        def resolve(keys, available):
            if keys is None:
                return available
            elif isinstance(keys, slice):
                return available[keys]
            elif isinstance(keys, list):
                return [k if isinstance(k, str) else available[k] for k in keys]
            elif isinstance(keys, int):
                return [available[keys]]
            elif isinstance(keys, str):
                return [keys]
            else:
                raise TypeError(f"Unsupported key type: {type(keys)}")

        # Interpret region argument
        if region is None or region == []:
            series, datasets = None, None
        elif isinstance(region, list) and len(region) == 1:
            series, datasets = region[0], None
        elif isinstance(region, list) and len(region) == 2:
            series, datasets = region[0], region[1]
        else:
            raise ValueError("`region` must be None, [], [series], or [series, dataset]")

        # Work on a copy unless inplace
        if inplace:
            new_data = self._project_data.data
        else:
            new_data = deepcopy(self._project_data.data)

        selected_series = resolve(series, list(new_data.keys()))

        for s in selected_series:
            if s not in new_data:
                raise KeyError(f"Series '{s}' not found")

            series_data = new_data[s]
            selected_datasets = resolve(datasets, list(series_data["datasets"].keys()))

            for d in selected_datasets:
                if d not in series_data["datasets"]:
                    raise KeyError(f"Dataset '{d}' not found in series '{s}'")

                df = series_data["datasets"][d]["df"]
                empty_df = pd.DataFrame(index=new_time_index, columns=df.columns)
                merged_df = df.combine_first(empty_df).sort_index()

                series_data["datasets"][d]["df"] = merged_df

        if inplace:
            return None

        new_instance = ProjectData()
        new_instance.project_directory = self._project_data.project_directory
        new_instance.project_metadata = deepcopy(self._project_data.project_metadata)
        new_instance.data = new_data
        new_instance.metadata = _MetadataAccessor(new_instance)
        new_instance.time_index = _time_index(new_instance)

        return new_instance
    
    def filter(self, time_index, inplace=False, region=None):

        def resolve(keys, available):
            if keys is None:
                return available
            elif isinstance(keys, slice):
                return available[keys]
            elif isinstance(keys, list):
                return [k if isinstance(k, str) else available[k] for k in keys]
            elif isinstance(keys, int):
                return [available[keys]]
            elif isinstance(keys, str):
                return [keys]
            else:
                raise TypeError(f"Unsupported key type: {type(keys)}")

        if inplace:
            new_data = self._project_data.data
        else:
            new_data = deepcopy(self._project_data.data)

        all_series = list(new_data.keys())
        series_keys = resolve(region[0] if region and len(region) > 0 else None, all_series)

        for s in series_keys:
            if s not in new_data:
                raise KeyError(f"Series '{s}' not found")
            datasets = new_data[s]["datasets"]
            all_datasets = list(datasets.keys())
            dataset_keys = resolve(region[1] if region and len(region) > 1 else None, all_datasets)

            for d in dataset_keys:
                if d not in datasets:
                    raise KeyError(f"Dataset '{d}' not found in series '{s}'")
                df = datasets[d]["df"]
                datasets[d]["df"] = df[df.index.isin(time_index)]

        if inplace:
            return None

        new_instance = type(self._project_data)()
        new_instance.project_directory = self._project_data.project_directory
        new_instance.project_metadata = deepcopy(self._project_data.project_metadata)
        new_instance.data = new_data
        new_instance.metadata = _MetadataAccessor(new_instance)
        new_instance.time_index = _time_index(new_instance)

        return new_instance

### Functions for Example Data Loading and Opening
def path_to_example_data():
    
    path = files("bivital.example.example_project")

    return path


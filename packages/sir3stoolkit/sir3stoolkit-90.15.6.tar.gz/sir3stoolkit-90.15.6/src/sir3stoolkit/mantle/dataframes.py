# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:22:31 2025

This module implements interactions between SIR 3S and pandas dataframes. You can obtain pandas dfs with meta- or resultdata, insert nodes and pipes via a df, etc.

@author: Jablonski
"""
from __future__ import annotations
from attrs import field
from pytoolconfig import dataclass

import pandas as pd
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum
import io
from typing import List, Tuple, Any
from enum import Enum
from collections import defaultdict
import geopandas as gpd
from shapely import wkt

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from sir3stoolkit.core.wrapper import SIR3S_Model

class SIR3S_Model_Dataframes(SIR3S_Model):
    """
    This class is supposed to extend the general SIR3S_Model class with the possibility of using pandas dataframes when working with SIR 3S. Getting dataframes, inserting elements via dataframes, running algorithms on dataframes should be made possible.
    """

    # Dataframe Creation

    ## Dataframe Creation: Basic Functions

    def generate_element_metadata_dataframe(
        self,
        element_type: Enum,
        tks: Optional[List[str]] = None,
        properties: Optional[List[str]] = None,
        geometry: Optional[bool] = False,
        end_nodes: Optional[bool] = False,
        element_type_col: Optional[bool] = False
    ) -> pd.DataFrame | gpd.GeoDataFrame:

        """
        Generate a dataframe with metadata (static) properties for all devices of a given element type.

        :param element_type: The element type (e.g., self.ObjectTypes.Node).
        :type element_type: Enum
        :param tks: List of tks of instances of the element type to include. All other tks will be excluded. Use for filtering.
                    Default: None (no filtering)
        :type tks: list[str], optional
        :param properties: List of metadata property names to include.  
                        If properties=None ⇒ all available properties are used.  
                        If properties=[] ⇒ no properties are used.
                        Default: None.
        :type properties: list[str], optional
        :param geometry: If True, includes geometric information for each element in the dataframe.  
                        Adds a 'geometry' column containing spatial data (WKT representation, e.g. POINT (x y)).  
                        An attempt will be made to transform the Dataframe into a GeoDataFrame. The success depends on whether an SRID is defined in the SIR 3S model.
                        Default: False.
        :type geometry: bool, optional
        :param end_nodes: If True and supported by the element type, includes tks of end nodes as columns  
                        (fkKI, fkKK, fkKI2, fkKK2).
                        Default: False.
        :type end_nodes: bool, optional
        :param element_type_col: If True, adds a column indicating the element type.  
                                Useful when merging dataframes later.
                                Default: False.
        :type element_type_col: bool, optional

        :return: DataFrame (or GeoDataFrame) with one row per device (tk) and columns for the requested metadata properties,  
                geometry and end nodes.  
                Columns: ["tk", <metadata_props>]
        :rtype: pd.DataFrame | gpd.GeoDataFrame

        :description:  
        Generates a DataFrame (or GeoDataFrame) containing static metadata for all elements of a given type.
        """

        logger.info(f"[metadata] Generating metadata dataframe for element type: {element_type}")

        # --- Collect device keys (tks) ---
        try:
            available_tks = self.GetTksofElementType(ElementType=element_type)
        except Exception as e:
            logger.error(f"[metadata] Error retrieving element tks: {e}")
            return pd.DataFrame()
        
        if len(available_tks) < 1:
            logger.warning(f"[metadata] No elements exist of this element type {element_type}: {e}")
            return pd.DataFrame()
        
        # --- Resolve tks ---
        if tks:
            tks=self.__resolve_given_tks(element_type=element_type, tks=tks, filter_container_tks=None)
            if len(tks) < 1:
                return pd.DataFrame
        else:
            tks=available_tks
            logger.info(f"[metadata] Retrieved {len(available_tks)} element(s) of element type {element_type}.")
          
        # --- Resolve given metadata properties ---
        metadata_props = self.__resolve_given_metadata_properties(element_type=element_type, properties=properties)

        # --- Retrieve values ---
        to_retrieve = []
        if metadata_props != []:
            to_retrieve.append(f"metadata properties {metadata_props}")
        if geometry:
            to_retrieve.append("geometry")
        if end_nodes:
            to_retrieve.append("end nodes")
            
        logger.info(f"[metadata] Retrieving {', '.join(to_retrieve)}...")
        
        rows = []

        end_nodes_available = False
        if end_nodes:
            if self.__is_get_endnodes_applicable(element_type=element_type):
                end_nodes_available = True
            else:
                logger.warning(f"[metadata] End nodes are not defined for element type {element_type}. Dataframe is created without end nodes.")
            
        for tk in tks:
            
            row = {"tk": tk}
            
            # Add metadata properties
            for prop in metadata_props:
                try:
                    row[prop] = self.GetValue(Tk=tk, propertyName=prop)[0]
                except Exception as e:
                    logger.warning(f"[metadata] Failed to get property '{prop}' for tk '{tk}': {e}")
            
            # Add geometry if requested
            if geometry:
                try:
                    row["geometry"] = self.GetGeometryInformation(Tk=tk)
                except Exception as e:
                    logger.warning(f"[metadata] Failed to get geometry information for tk '{tk}': {e}")
            
            # Add end nodes if requested
            if end_nodes_available:
                try:
                    endnode_tuple = self.GetEndNodes(Tk=tk) 
                    row["fkKI"], row["fkKK"], row["fkKI2"], row["fkKK2"] = endnode_tuple
                except Exception as e:
                    logger.warning(f"[metadata] Failed to get end nodes for tk '{tk}': {e}")
            
             # Add element type col if requested
            if element_type_col:
                row["element type"] = str(element_type).split(".")[-1]

            rows.append(row)

        # --- Endnodes Post Processing ---
        if end_nodes_available:
            endnode_cols = ["fkKI", "fkKK", "fkKI2", "fkKK2"]
            used_cols = []

            for col in endnode_cols:
                if any(row.get(col, "-1") != "-1" for row in rows):
                    used_cols.append(col)
                else:
                    for row in rows:
                        row.pop(col, None)

            logger.info(f"[metadata] {len(used_cols)} non-empty end node columns were created.")

        # --- Dataframe creation ---
        df = pd.DataFrame(rows)

        if geometry:
            try:
                df["geometry"] = df["geometry"].apply(wkt.loads)
                srid, srid2, srid_string = self.get_EPSG()
                if srid and (srid != '0'):
                    df = gpd.GeoDataFrame(df, geometry="geometry", crs=f"EPSG: {srid}")
                    logger.info(f"[metadata] Transforming DataFrame to GeoDataFrame successful with EPSG: {srid}")
                else:
                    logger.warning(f"[metadata] Spatial Reference Identifier (SRID) not defined in model. DataFrame cannot be transformed to GeoDataFrame but geometry column can be created independently of SRID. Returning regular DataFrame with a geometry column.")
            except Exception as e:
                    logger.error(f"[metadata] Error transforming DataFrame to GeoDataFrame. {e}")

        logger.info(f"[metadata] Done. Shape: {df.shape}")
        return df

    def generate_element_results_dataframe(
        self,
        element_type: Enum,
        tks: Optional[List[str]] = None,
        properties: Optional[List[str]] = None,
        timestamps: Optional[List[str]] = None,
        place_holder_value: Optional[float] = 99999.0
    ) -> pd.DataFrame:

        """
        Generate a dataframe with RESULT (time-dependent) properties for all devices and timestamps.

        :param element_type: The element type (e.g., self.ObjectTypes.Node). 
        :type element_type: Enum
        :param properties: List of RESULT property names to include.  
                        If properties=None ⇒ includes all available result properties (per element, only if values exist).  
                        If properties=[] ⇒ no properties are used.
                        Default: None.
        :type properties: list[str], optional
        :param timestamps: List of timestamps to include. Can be:  
                        - List of timestamp strings  
                            (e.g., ["2025-09-25 00:00:00.000 +02:00", "2025-09-25 00:05:00.000 +02:00"])  
                        - List of integer indices  
                            (e.g., [0, 7, -1]) 
                            where 0 = first timestamp, 7 = eighth timestamp, -1 = last timestamp.  
                        Default: None (includes all available timestamps).
        :type timestamps: list[Union[str, int]], optional

        :return: DataFrame with one row per timestamp and MultiIndex columns:  
                - Level 0: tk (device ID)  
                - Level 1: name (device name)  
                - Level 2: end_nodes (tuple of connected node tks as string)  
                - Level 3: property (result name)  
                Data types: float for scalars, str for vectorized data.
        :rtype: pd.DataFrame

        :description:
        Generates a DataFrame containing time-dependent result vectors for all selected devices and timestamps.  
        Supports both timestamp strings and index-based selection. Produces a MultiIndex-column DataFrame grouped by device, name, end-nodes, and property.
        """

        # --- Validate time stamps ---
        logger.info(f"[results] Generating results dataframe for element type: {element_type}")

        valid_timestamps = self._resolve_given_timestamps(timestamps)
        if not valid_timestamps:
            logger.warning("[results] No valid timestamps. Returning empty dataframe.")
            return pd.DataFrame()
            
        # --- Resolve tks ---
        tks=self.__resolve_given_tks(element_type=element_type, tks=tks, filter_container_tks=None)
        if len(tks) < 1:
            return pd.DataFrame
        
        # --- Resolve given properties ---
        try:
            available_metadata_props = self.GetPropertiesofElementType(ElementType=element_type)
            available_result_props = self.GetResultProperties_from_elementType(
                elementType=element_type,
                onlySelectedVectors=False
            )
            available_result_vector_props=[available_result_props for available_result_props in available_result_props if "VEC" in available_result_props]
            available_result_non_vector_props = [available_result_props for available_result_props in available_result_props if "VEC" not in available_result_props]

            result_props: List[str] = []

            if properties is None:
                logger.info(f"[results] No properties given → using ALL result properties for {element_type}.")
                result_props = available_result_props
            else:
                for prop in properties:
                    if prop in available_result_props:
                        result_props.append(prop)
                    elif prop in available_metadata_props:
                        logger.warning(f"[results] Property '{prop}' is a METADATA property; excluded from results.")
                    else:
                        logger.warning(
                            f"[results] Property '{prop}' not found in metadata or result properties of type {element_type}. Excluding."
                        ) 
            logger.info(f"[results] Using {len(result_props)} result properties.")
        except Exception as e:
            logger.error(f"[results] Error determining result properties: {e}")
            return pd.DataFrame()

        end_nodes_available = False
        if self.__is_get_endnodes_applicable(element_type=element_type):
            end_nodes_available = True

        # --- Retrieve values ---
        logger.info("[results] Retrieving result values...")

        data_dict = defaultdict(dict)

        for ts in map(str, valid_timestamps):
            for tk in tks:
                for prop in result_props:
                    try:
                        value = self.GetResultfortimestamp(timestamp=ts, Tk=tk, property=prop)[0]
                        if value == "":
                            data_dict[(tk, prop)][ts] = place_holder_value
                        elif prop in available_result_vector_props:
                            value = str(value)
                            data_dict[(tk, prop)][ts] = value
                        else:
                            try:
                                value = float(value)
                            except ValueError:
                                logger.warning(f"[results] Non-numeric value for '{prop}' at '{ts}': {value}")
                                value = float("nan")
                            data_dict[(tk, prop)][ts] = value

                    except Exception as e:
                        logger.warning(f"[results] Failed to get result '{prop}' for tk '{tk}' at '{ts}': {e}")

        df = pd.DataFrame(data_dict)
        df.index.name = "timestamp"

        # --- Add Name, End Nodes and Interior points to column MultiIndex ---
        col_tuples = []

        for col in df.columns:
            tk, prop = col
            try:
                name = self.GetValue(tk, "Name")[0]
            except Exception as e:
                logger.warning(f"[results] Failed to get name for tk '{tk}': {e}")
                name = "UNKNOWN"

            if end_nodes_available:
                try:
                    end_nodes = self.GetEndNodes(tk)
                    end_nodes_str = str(end_nodes)
                except Exception as e:
                    logger.warning(f"[results] Failed to get end nodes for tk '{tk}': {e}")
                    end_nodes_str = "UNKNOWN"
            else:
                end_nodes_str = "No end nodes on element type"

            
            col_tuples.append((tk, name, end_nodes_str, prop))

        df.columns = pd.MultiIndex.from_tuples(
            col_tuples,
            names=["tk", "name", "end_nodes", "property"]
        )

        logger.info(f"[results] Done. Shape: {df.shape}")
        return df

    ## Dataframe Creation: Explicit Dataframe Creation

    def generate_element_dataframe(
        self,
        element_type: str,
        tks: Optional[list[str]] = None
    ) -> pd.DataFrame | gpd.GeoDataFrame:

        """
        Generates a dataframe containing all instances for a given element type in the open
        SIR 3S model. All metadata and most result values
        (self.GetResultProperties_from_elementType(onlySelectedVectors=True))
        for the static timestamp are included.

        Result values are returned as floats unless they are vectorized (relevant only for
        pipes), in which case they are returned as strings. The tks of end nodes are included
        (fkKI, fkKK). Geometry information is also included.

        :param element_type: The element type (e.g., self.ObjectTypes.Node, self.ObjectTypes.Pipe).
        :type element_type: Enum
        :param tks: List of tks to include in the dataframe.
                    Default: None.
        :type tks: list[str], optional

        :return: DataFrame containing one row per element instance, including metadata, end
                nodes, geometry, and available static result values.
        :rtype: pd.DataFrame

        :description:
        Builds a comprehensive DataFrame containing metadata and static result values for
        all requested elements of the given type. Vectorized pipe results are included
        as strings, and scalar results as floats. Geometry and end-node tks are always included.
        """

        logger.info(f"[generate_element_dataframe] Generating df for element type: {element_type} ...")
        
        try:
            logger.debug(f"[generate_element_dataframe] Generating df_metadata for element type: {element_type} ...")
            df_metadata = self.generate_element_metadata_dataframe(element_type=element_type
                                                                ,tks=tks
                                                                ,properties=None
                                                                ,geometry=True
                                                                ,end_nodes=True
                                                                ,element_type_col=False
            )
            
            logger.debug(f"[generate_element_dataframe] Generating df_results for element type: {element_type} ...")
            result_values_to_obtain = self.GetResultProperties_from_elementType(element_type, True)
            static_timestamp = self.GetTimeStamps()[1]
            df_results = self.generate_element_results_dataframe(element_type=element_type
                                                                        ,tks=tks
                                                                        ,properties=result_values_to_obtain
                                                                        ,timestamps=[static_timestamp]
            )

            logger.debug(f"[generate_element_dataframe] Merging df_metadata with df_results for element type: {element_type} ...")
            df_results.columns = df_results.columns.droplevel([1, 2])
            df_results = df_results.T.unstack(level=0).T
            df_results = df_results.droplevel(0, axis=0)
            df = df_metadata.merge(on="tk",
                                how="outer",
                                right=df_results)
            
            return df
        
        except Exception as e:
            logger.error(f"[generate_element_dataframe] Error Generating df for element type: {element_type}: {e}")
            

    def add_interior_points_to_results_dataframe(self, df_results):
        """
        Expand vector properties from tab-separated strings into multiple interior-point
        segments along a new MultiIndex column level.

        Vector properties are identified by having 'VEC' in the last column-level name.
        Their tab-separated string values are split into float segments representing
        interior points along the device. Non-vector properties have their interior
        point index set to -1 and retain their scalar values.

        :param df_results: Results DataFrame containing scalar and vector properties.
        :type df_results: pd.DataFrame

        :return: A DataFrame in which vector properties are expanded along a new
                MultiIndex level named 'interior points', with float values for each
                interior segment. Non-vector properties are assigned interior point -1.
        :rtype: pd.DataFrame

        :description:
            This method processes the result DataFrame by expanding tab-separated
            vector-valued properties (typically from pipes) into properly structured
            numerical segments. Each vector entry becomes a sequence of interior point
            values along a new index level. Scalar properties remain unchanged and are
            placed under interior point -1 to maintain consistent indexing.
        """

        last_level = df_results.columns.get_level_values(-1)
        vec_props = {p for p in last_level.unique() if "VEC" in str(p)}

        new_level_name = "interior points"
        new_names = list(df_results.columns.names) + [new_level_name]

        pieces = []

        for col_key in df_results.columns:

            key = col_key if isinstance(col_key, tuple) else (col_key,)
            prop = key[-1]
            col = df_results[col_key]

            if prop in vec_props:

                s = col.where(col.notna())
                
                split_lists = s.apply(lambda x: x.split("\t") if isinstance(x, str) else [])

                # Determine max number of segments for THIS column
                max_len = split_lists.apply(len).max()

                if max_len == 0:
                    continue

                
                segs = pd.DataFrame(
                    split_lists.apply(lambda lst: lst + [None] * (max_len - len(lst))).tolist(),
                    index=col.index
                )

                # Convert to numeric
                segs = segs.apply(pd.to_numeric, errors="coerce")

                # Assign MultiIndex columns
                segs.columns = pd.MultiIndex.from_tuples(
                    [key + (i,) for i in range(max_len)],
                    names=new_names
                )

                pieces.append(segs)

            else:
                # Non-vector property → interior point = -1
                df1 = col.to_frame()
                df1.columns = pd.MultiIndex.from_tuples(
                    [key + (-1,)],
                    names=new_names
                )
                pieces.append(df1)

        out = pd.concat(pieces, axis=1)
        out = out.dropna(axis=1, how="all")
        return out

    
    def generate_longitudinal_section_dataframes(
        self
    ) -> List[pd.DataFrame]:
        """
        Generates dataframes for longitudinal sections.
        
        :param self: Instance of SIR_Model_Dataframes class
        :return: List of dataframes of the form [section_1_VL, section_1_RL, section_2_VL, section_2_RL, ..., section_lfdnr_VL, section_lfdnr_RL, ...]
        :rtype: List[DataFrame|GeoDataFrame]
        """

        df_agsn_metadata = self.generate_element_metadata_dataframe(self.ObjectTypes.AGSN_HydraulicProfile)
        df_agsn_metadata = df_agsn_metadata.sort_values('Lfdnr')

        """
        # Only include active 
        df_agsn_metadata["Aktiv"] = df_agsn_metadata["Aktiv"].astype(str)
        df_agsn_metadata = df_agsn_metadata[df_agsn_metadata["Aktiv"] == "101"]
        """

        dfs = []

        for tk, lfdnr, name in df_agsn_metadata[['tk', 'Lfdnr', 'Name']].itertuples(index=False):

            # --- Retrieve Hydraulic Profile
            logger.info(f"Retrieving Hydraulic Profile with Lfdnr: {lfdnr}.")
            try:
                hydraulicProfile = self.GetCourseOfHydraulicProfile(tkAgsn=tk, uid="0")
                if hydraulicProfile.nrOfBranches != 0:
                    logger.info(f"Method does not work for longitudinal sections with branches. Not including hydraulic profile: {lfdnr}.")
                    continue
                # VL
                nodes_VL = list(hydraulicProfile.nodesVL)
                links_VL = list(hydraulicProfile.linksVL)
                x_VL = list(hydraulicProfile.xVL)
                x_VL = x_VL[1:]
                links_VL_tk_to_x_sum = dict(zip(links_VL, x_VL))
                df_pipes_VL = self.generate_element_dataframe(element_type=self.ObjectTypes.Pipe
                                                            ,tks=links_VL)
                df_pipes_VL["l_sum"] = df_pipes_VL["tk"].map(links_VL_tk_to_x_sum)
                df_pipes_VL["AGSN_Lfdnr"] = lfdnr
                df_pipes_VL["AGSN_Name"] = name
                df_pipes_VL.sort_values(by='l_sum', ascending=True, inplace=True)
                df_pipes_VL = df_pipes_VL.reset_index(drop=True)
                dfs.append(df_pipes_VL)
                    
                # RL
                nodes_RL = list(hydraulicProfile.nodesRL)
                links_RL = list(hydraulicProfile.linksRL)
                x_RL = list(hydraulicProfile.xRL)
                x_RL = x_RL[1:]
                links_RL_tk_to_x_sum = dict(zip(links_RL, x_RL))
                df_pipes_RL = self.generate_element_dataframe(element_type=self.ObjectTypes.Pipe
                                                            ,tks=links_RL)
                df_pipes_RL["l_sum"] = df_pipes_RL["tk"].map(links_RL_tk_to_x_sum)
                df_pipes_RL["AGSN_Lfdnr"] = lfdnr
                df_pipes_RL["AGSN_Name"] = name
                df_pipes_RL.sort_values(by='l_sum', ascending=True, inplace=True)
                df_pipes_RL = df_pipes_RL.reset_index(drop=True)
                dfs.append(df_pipes_RL)
            except Exception as e:
                logging.error(f"Error retrieving Hydraulic Profile with Lfdnr: {lfdnr}.")
                return []

        return dfs
    
    def generate_hydraulic_edge_dataframe(
        self      
    ) -> pd.DataFrame:

        """
        Generates dataframes for longitudinal sections.

        Each section produces two dataframes: VL (supply/flow) and RL (return).
        The returned list follows the structure:
        [section_1_VL, section_1_RL, section_2_VL, section_2_RL, ..., section_n_VL, section_n_RL].

        :return: List of dataframes representing longitudinal sections in the order
                [section_1_VL, section_1_RL, ..., section_n_VL, section_n_RL].
        :rtype: list[DataFrame | GeoDataFrame]

        :description:
            Creates a collection of longitudinal-section dataframes for the open SIR 3S model.
            For each section, both supply (VL) and return (RL) lines are extracted.
            Depending on whether geometric information is present, each dataframe may be
            a regular pandas DataFrame or a GeoDataFrame.
        """

        edge_types = [
            'Pipe', 'Valve', 'SafetyValve', 'PressureRegulator', 'DifferentialRegulator',
            'FlapValve', 'PhaseSeparation', 'FlowControlUnit', 'ControlValve', 'Pump',
            'DistrictHeatingConsumer', 'DistrictHeatingFeeder', 'Compressor', 'HeaterCooler',
            'HeatExchanger', 'HeatFeederConsumerStation', 'RART_ControlMode'
        ]

        try:
            enum_members = self.__get_object_type_enums(edge_types, self.ObjectTypes)
            dfs = []
            for em in enum_members:
                tks = self.GetTksofElementType(ElementType=em)
                if tks:
                    df = self.generate_element_metadata_dataframe(
                        element_type=em,
                        properties=["Fkcont"],
                        geometry=True,
                        end_nodes=True,
                        element_type_col=True
                    )
                    dfs.append(df)
            df_edges = pd.concat(dfs, ignore_index=True)
            logger.info(f"[hydraulic edges dataframe] Retrieved {len(df_edges)} edges from {len(enum_members)} element types.")
        except Exception as e:
            logger.error(f"[hydraulic edges dataframe] Failed to retrieve edges: {e}")

        return df_edges
        
    def __get_object_type_enums(self, names, enum_class):
        return [getattr(enum_class, name) for name in names if hasattr(enum_class, name)]

    ## Dataframe Creation: Helpers

    def __sort_properties_into_metadata_and_results(
        self, 
        element_type: Enum,
        properties: List[str],
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Sorts the given properties into three categories:
        - Metadata properties
        - Result properties
        - Uncategorized properties (not found in either metadata or result properties)
        
        Args:
            element_type (Enum): The type of element to query properties for.
            properties (List[str]): The list of properties to sort.
        
        Returns:
            Tuple[List[str], List[str], List[str]]: A tuple containing three lists:
                - metadata_matches
                - result_matches
                - uncategorized
        """
        metadata_properties = self.GetPropertiesofElementType(element_type=element_type)
        result_properties = self.GetResultProperties_from_elementType(elementType=element_type)

        metadata_matches = [prop for prop in properties if prop in metadata_properties]
        result_matches = [prop for prop in properties if prop in result_properties]
        uncategorized = [prop for prop in properties if prop not in metadata_properties and prop not in result_properties]

        return metadata_matches, result_matches, uncategorized

    def __decapitalize(s: str) -> str:
        return s[:1].lower() + s[1:] if s else s

    def get_EPSG(self
    ) -> Tuple[str]:
        """
        Returns SRID, SRID and combined String. For example: ('25832', '1571', '25832-1571')
        """
        
        tk_SIRGRAF = self.GetTksofElementType(self.ObjectTypes.SIRGRAF)[0]
        srid = str(self.GetValue(tk_SIRGRAF, "Srid")[0])
        srid2 = str(self.GetValue(tk_SIRGRAF, "Srid2")[0])
        srid_string = self.GetValue(tk_SIRGRAF, "SridString")[0]

        return srid, srid2, srid_string
    
    def __resolve_given_tks(
        self,
        element_type: Enum,
        tks: Optional[List[str]] = None,
        filter_container_tks: Optional[List[str]] = None
    ) -> List:

        # --- Collect device keys (tks) ---
        try:
            available_tks = self.GetTksofElementType(ElementType=element_type)
            logger.info(f"[Resolving tks] Retrieved {len(available_tks)} element(s) of element type {element_type}.")
        except Exception as e:
            logger.error(f"[metadata] Error retrieving element tks: {e}")
            return pd.DataFrame()
        
        if len(available_tks) < 1:
            logger.warning(f"[Resolving tks] No elements exist of this element type {element_type}: {e}")
            return pd.DataFrame()
        
        # --- Filter for given tks ---
        given_tks = tks
        if tks:
            try:
                for tk in tks:
                    if tk not in available_tks:
                        logger.warning(f"[Resolving tks] {tk} does not exist or is not of element type {element_type}. Excluding.")
                        tks.remove(tk)
                if len(tks) < 1:
                    logger.error(f"[Resolving tks] No elements remain after filtering for given tks: {given_tks}")
                    return pd.DataFrame()
                else:
                    logger.info(f"[Resolving tks] {len(tks)} tks remain after filtering for given tks.")

            except Exception as e:
                logger.error(f"[Resolving tks] Error validating given tks: {e}")
                return pd.DataFrame()
            
        else:
            tks = available_tks
            
        
        # --- Filer for container tk list ---
        if filter_container_tks:
            try:
                all_container_tks = self.GetTksofElementType(self.ObjectTypes.ObjectContainerSymbol)
                for tk in filter_container_tks[:]:
                    if tk not in all_container_tks:
                        logger.warning(f"[Resolving tks] Removed invalid container tk: {tk}. Proceeding without it.")
                        filter_container_tks.remove(tk)

                if filter_container_tks:
                    tks = [tk for tk in tks if self.GetValue(tk, "FkCont")[0] in filter_container_tks]
                if len(tks) < 1:
                    logger.error(f"[Resolving tks] No elements remain after container filtering.")
                    return []
                logger.info(f"[Resolving tks] {len(tks)} tks remain after container filtering.")
            except Exception as e:
                logger.error(f"[Resolving tks] Error occured while filtering with filter_container_tks: {e}")

        return tks
    
    def _resolve_given_timestamps(self, timestamps: Optional[List[Union[str, int]]]) -> List[str]:
        """
        Resolve the list of timestamps to use:
        - If `timestamps` is None: use all simulation timestamps (if available) else STAT.
        - If list contains integers: treat them as indices into the available timestamps.
        - If list contains strings: treat them as actual timestamp strings.
        - Validate against available timestamps and filter out invalid ones.

        Returns
        -------
        List[str]
            A list of valid timestamp strings (possibly empty).
        """
        # --- Default timestamp resolution ---
        if timestamps is None:
            logger.info("[Resolving Timestamps] No timestamps were given. Checking available simulation timestamps (SIR3S_Model.GetTimeStamps()[0]).")
            try:
                simulation_timestamps, tsStat, tsMin, tsMax = self.GetTimeStamps()
                if simulation_timestamps:
                    timestamps = simulation_timestamps
                    logger.info(f"[Resolving Timestamps] {len(timestamps)} simulation timestamp(s) are available.")
                else:
                    logger.warning("[Resolving Timestamps] No valid simulation timestamps exist in result data.")
                    return []
            except Exception as e:
                logger.error(f"[Resolving Timestamps] Error retrieving timestamps: {e}")
                return []

        # --- Validate given timestamps ---
        try:
            simulation_timestamps, tsStat, tsMin, tsMax = self.GetTimeStamps()
            available_timestamps = list(simulation_timestamps) if simulation_timestamps else []

            valid_timestamps = []

            # Check if input is list of integers (indices)
            if isinstance(timestamps[0], int):
                for idx in timestamps:
                    try:
                        resolved_ts = available_timestamps[idx]
                        valid_timestamps.append(resolved_ts)
                    except IndexError:
                        logger.warning(f"[Resolving Timestamps] Index {idx} out of bounds for available timestamps. It will be excluded.")
            else:
                # Assume list of timestamp strings
                for ts in timestamps:
                    if ts in available_timestamps:
                        valid_timestamps.append(ts)
                    else:
                        logger.warning(
                            f"[Resolving Timestamps] Timestamp {ts} is not valid (SIR3S_Model.GetTimeStamps()). It will be excluded."
                        )

            if len(valid_timestamps) == 1 and tsStat == valid_timestamps[0]:
                logger.info(f"[Resolving Timestamps] Only static timestamp {tsStat} is used")
            logger.info(f"[Resolving Timestamps] {len(valid_timestamps)} valid timestamp(s) will be used.")
            return valid_timestamps
        except Exception as e:
            logger.error(f"Error validating timestamps: {e}")
            return []

    def __resolve_given_metadata_properties(
        self,
        element_type: Enum,
        properties: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Checks the validity of given list of metadata properties. 
        If properties=None => All available properties will be used
        If properties=[] => No properties will be used
        """

        try:
            available_metadata_props = self.GetPropertiesofElementType(ElementType=element_type)
            available_result_props = self.GetResultProperties_from_elementType(
                elementType=element_type,
                onlySelectedVectors=False
            )

            metadata_props: List[str] = []

            if properties is None:
                logger.info(f"[Resolving Metadata Properties] No properties given → using ALL metadata properties for {element_type}.")
                metadata_props = available_metadata_props
            else:
                for prop in properties:
                    if prop in available_metadata_props:
                        metadata_props.append(prop)
                    elif prop in available_result_props:
                        logger.warning(f"[Resolving Metadata Properties] Property '{prop}' is a RESULT property; excluded from metadata.")
                    else:
                        logger.warning(
                            f"[Resolving Metadata Properties] Property '{prop}' not found in metadata or result properties of type {element_type}. Excluding."
                        )

            logger.info(f"[Resolving Metadata Properties] Using {len(metadata_props)} metadata properties.")
       
        except Exception as e:
            logger.error(f"[Resolving Metadata Properties] Error resolving metadata properties: {e}")
        
        return metadata_props

    def __is_get_endnodes_applicable(self, element_type):
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer  # Redirect stdout

        dummy = self.InsertElement(element_type, "to be deleted")

        try:
            
            _ = self.GetEndNodes(dummy)
        except Exception:
            sys.stdout = sys_stdout  # Restore stdout

        self.DeleteElement(dummy)

        sys.stdout = sys_stdout  # Restore stdout
        output = buffer.getvalue()
        buffer.close()

        if "doesnt apply to such Type of Elements" in output:
            return False
        
        return True

    # Dataframe Operations

    def __apply_metadata_property_updates(
        self,
        element_type: Enum,
        updates_df: pd.DataFrame,
        properties_new: Optional[List[str]] = None,
        tag: Optional[str] = "_new",
    ) -> pd.DataFrame:
        """
        WORK IN PROGRESS
        Apply metadata updates for a single property using a DataFrame with keys and new values.

        Expects:
        - One key column (default: 'tk'), and
        - Exactly one column named '<metadata_property>_new' (or pass `property_name` to target one explicitly).

        Parameters
        ----------
        element_type : Enum
            The element type to update (e.g., self.ObjectTypes.Pipe).
        updates_df : pd.DataFrame
            Input with at least:
            - key column (default 'tk'), and
            - one '<property>_new' column (e.g., 'diameter_mm_new').
        property_name : Optional[str], default None
            If given, we will look for the column f"{property_name}_new".
            If None, we auto-detect a single '*_new' column.
        on : str, default 'tk'
            Name of the key column in `updates_df`. If it's the index, it will be reset.
        create_missing : bool, default False
            If True, allow creating metadata rows that don't exist yet (your set-logic decides how).
        dry_run : bool, default False
            If True, do NOT apply; just return a normalized summary of what would be changed.
        allow_na : bool, default True
            If False, rows with NaN in the '<property>_new' column will be dropped (skipped).

        Returns
        -------
        pd.DataFrame
            A summary dataframe with columns:
            ['tk', 'property', 'new_value'] (+ 'status' when dry_run)
            representing the intended updates.
        """
        logger.info(f"[update] Applying metadata updates for element type: {element_type}")

        if updates_df is None or updates_df.empty:
            logger.warning("[update] Empty updates_df provided. Nothing to do.")
            return pd.DataFrame(columns=["tk", "property", "new_value"])

        df = updates_df.copy()

        # --- Ensure key ('tk') column is present ---
        if tk not in df.columns:
            if df.index.name == tk:
                df = df.reset_index()
                logger.info(f"[update] Using index as column.")
            else:
                msg = f"[update] tk not found in updates_df (nor as index)."
                logger.error(msg)
                raise KeyError(msg)

        # --- Resolve & Validate given properties_new ---
        logger.info("[update] Resolving & validating given properties_new...")
        properties_new_in_index=df.columns.intersection(properties_new).tolist()
        logger.info(f"[update] In updates_df found: {properties_new_in_index}")
        properties_new_stripped = [p.removesuffix(tag) for p in properties_new]
        metadata_props_new=self.__resolve_given_metadata_properties(element_type=element_type, properties=properties_new_stripped)
        metadata_props_new_with_suffix = [p + tag for p in metadata_props_new]
        logger.info("[update] Resolved & validated given properties_new")

        # TODO
        # --- Set metadata values in model ---
        for tk in self.GetTksofElementType(ElementType=element_type):
            for prop in metadata_props_new:
                msg=self.SetValue(prop, updates_df.iloc[tk, metadata_props_new_with_suffix])
                logger.debug

    def __AddNodesAndPipes(self, dfXL):
        """
        Takes a dataframe with each row representing one pipe and adds it to the model. Only dfXL
        This function should be moved to Dataframes.py to create a general module for working with Dataframes in SIR 3S.
        """
        for i, row in dfXL.iterrows():
            kvr = int(row['KVR'])

            # Create KI node
            x_ki, y_ki = row['geometry'].coords[0]
            tk_ki = self.AddNewNode(
                "-1", f"Node{i}KI {self.__VL_or_RL(kvr)}", f"Node{i}", x_ki, y_ki,
                1.0, 0.1, 2.0, f"Node{i}KI", f'ID{row.nodeKI_id}', kvr
            )
            dfXL.at[i, 'nodeKI'] = tk_ki

            # Create KK node
            x_kk, y_kk = row['geometry'].coords[-1]
            tk_kk = self.AddNewNode(
                "-1", f"Node{i}KK {self.__VL_or_RL(kvr)}", f"Node{i}", x_kk, y_kk,
                1.0, 0.1, 2.0, f"Node{i}KK", f'ID{row.nodeKK_id}', kvr
            )
            dfXL.at[i, 'nodeKK'] = tk_kk

            # Create pipe
            tk_pipe = self.AddNewPipe(
                "-1", tk_ki, tk_kk, row['geometry'].length,
                str(row['geometry']), str(row['MATERIAL']), str(row['DN']),
                1.5, f'ID{i}', f'Pipe {i}', kvr
            )
            dfXL.at[i, 'tk'] = tk_pipe

            try:
                baujahr = dfXL.at[i, 'BAUJAHR']
                if pd.notna(baujahr):
                    self.SetValue(tk_pipe, "Baujahr", str(baujahr))
            except Exception as e:
                logger.debug(f"BAUJAHR of Pipe {tk_pipe} not assigned: {e}")

            try:
                hal = dfXL.at[i, 'HAL']
                if pd.notna(hal):
                    self.SetValue(tk_pipe, "Hal", str(hal))
            except Exception as e:
                logger.debug(f"HAL of Pipe {tk_pipe} not assigned: {e}")

            # 2LROHR does not work
            try:
                partner_id = dfXL.at[i, '2LROHR_id']
                if pd.notna(partner_id):
                    match = dfXL[dfXL['tk_id'] == partner_id]
                    if not match.empty:
                        partner_pipe_tk = match.iloc[0]['tk']
                        self.SetValue(tk_pipe, "Fk2lrohr", partner_pipe_tk)
            except Exception as e:
                logger.debug(f"2LROHR of Pipe {tk_pipe} not assigned: {e}")

        return dfXL

    def __insert_dfPipes(self, dfPipes):
        """
        Takes a dataframe with each row representing one pipe and adds it to the model.
        The dataframe needs minimum of cols: geometry (LINESTRING), MATERIAL (str), DN (int), KVR (int)
        """
        func_name = sys._getframe().f_code.co_name
        logger.debug(f"{func_name}: Start.")

        climbing_index = 0
        for idx in range(len(dfPipes)):
            dfPipes.at[idx, 'nodeKI_id'] = climbing_index
            dfPipes.at[idx, 'nodeKK_id'] = climbing_index + 1
            climbing_index += 2

        self.StartEditSession(SessionName="AddNodesAndPipes")

        dfPipes['KVR'] = dfPipes['KVR'].astype(str).str.strip()
        dfVL = dfPipes[dfPipes['KVR'] == '1'].reset_index(drop=True)
        dfRL = dfPipes[dfPipes['KVR'] == '2'].reset_index(drop=True)

        dfVL = self.AddNodesAndPipes(dfVL)
        dfRL = self.AddNodesAndPipes(dfRL)

        dfPipes = pd.concat([dfVL, dfRL], ignore_index=True)

        self.EndEditSession()
        self.SaveChanges()
        self.RefreshViews()

        return dfPipes


    # Miscellaneous
    def __Get_Node_Tks_From_Pipe(self, pipe_tk):
        func_name = sys._getframe().f_code.co_name
        logger.debug(f"{func_name}: Start.")

        from_node_name = self.GetValue(pipe_tk, 'FromNode.Name')[0]
        to_node_name = self.GetValue(pipe_tk, 'ToNode.Name')[0]

        from_node_tk = None
        to_node_tk = None

        for node_tk in self.GetTksofElementType(ElementType=self.ObjectTypes.Node):
            node_name = self.GetValue(node_tk, 'Name')[0]
            if node_name == from_node_name:
                from_node_tk = node_tk
            if node_name == to_node_name:
                to_node_tk = node_tk

        return from_node_tk, to_node_tk

    def __Get_Pipe_Tk_From_Nodes(self, fkKI, fkKK, Order=True):
        func_name = sys._getframe().f_code.co_name
        logger.debug(f"{func_name}: Start.")

        from_node_name = self.GetValue(fkKI, 'Name')[0]
        to_node_name = self.GetValue(fkKK, 'Name')[0]

        pipe_tk_ret = None

        if Order:
            for pipe_tk in self.GetTksofElementType(ElementType=self.ObjectTypes.Pipe):
                if (self.GetValue(pipe_tk, 'FromNode.Name')[0] == from_node_name and
                   self.GetValue(pipe_tk, 'ToNode.Name')[0] == to_node_name):
                    pipe_tk_ret = pipe_tk
                    break
        else:
            for pipe_tk in self.GetTksofElementType(ElementType=self.ObjectTypes.Pipe):
                from_name = self.GetValue(pipe_tk, 'FromNode.Name')[0]
                to_name = self.GetValue(pipe_tk, 'ToNode.Name')[0]
                if ((from_name == from_node_name and to_name == to_node_name) or
                   (from_name == to_node_name and to_name == from_node_name)):
                    pipe_tk_ret = pipe_tk
                    break

        return pipe_tk_ret

    def __VL_or_RL(self, KVR):
        func_name = sys._getframe().f_code.co_name
        logger.debug(f"{func_name}: Start.")
        if KVR == 1:
            return 'VL'
        elif KVR == 2:
            return 'RL'
        else:
            return 'Unknown'

    def __Check_Node_Name_Duplicates(self, name):
        func_name = sys._getframe().f_code.co_name
        logger.debug(f"{func_name}: Start.")

        tks = []
        for node_tk in self.GetTksofElementType(ElementType=self.ObjectTypes.Node):
            current_name = self.GetValue(node_tk, 'Name')[0]
            if current_name == name:
                tks.append(node_tk)

        if len(tks) == 1:
            print(f'Only the node with tk {tks[0]} has the name {name}')
        else:
            print(f'The nodes of the following tks have the same name ({name}):')
            for tk in tks:
                print(f'{tk}')

        return tks

    def __is_a_model_open(self):
        """
        Returns true if a model is open, false if no model is open or the NetworkType is undefined.
        """
        is_a_model_open = True
        if(self.GetNetworkType=="NetworkType.Undefined"):
            is_a_model_open = False
        return is_a_model_open
    

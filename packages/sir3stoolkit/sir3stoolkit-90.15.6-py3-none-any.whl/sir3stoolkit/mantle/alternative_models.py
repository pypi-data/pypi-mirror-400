# -*- coding: utf-8 -*-
"""
Created on Weg Sep 01 14:04:43 2025

This module implements the generation of SIR 3S models in alternative model formats such as pandapipes or nx-Graphs.

@author: Jablonski
"""

import pandapipes as pp
import pandas as pd
from shapely import wkt
from shapely.geometry.base import BaseGeometry

import networkx as nx
from typing import List, Optional, Union

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

from sir3stoolkit.mantle.dataframes import SIR3S_Model_Dataframes

class SIR3S_Model_Alternative_Models(SIR3S_Model_Dataframes):
    """
    This class is supposed to extend the Dataframes class that extends the general SIR3S_Model class with the possibility of using alternative District Heating models such as pandapipes.
    """
    def SIR_3S_to_pandapipes(self):
        """
        Converts the currently open SIR 3S network into a pandapipes network.

        This function creates a pandapipes network that mirrors the structure of the SIR 3S network,
        including junctions (nodes), pipes, and external sources/sinks. Only elements of type Node and Pipe
        are included; FWVB (district heating consumers) are excluded.

        Returns
        -------
        pandapipes.pandapipesNet
            A pandapipes network object containing:
            - Junctions with metadata and result values (pressure, temperature, flow).
            - Pipes with geometry and physical parameters.
            - External grids (sources) and sinks based on node type and flow direction.
        """
        net = pp.create_empty_network(fluid="water")

        # --- Nodes/Junctions ---
        df_nodes_metadata = self.generate_element_metadata_dataframe(element_type=self.ObjectTypes.Node, properties=['Name', 'Zkor', 'QmEin', 'bz.PhEin', 'Ktyp'], geometry=True)
        df_nodes_results = self.generate_element_results_dataframe(element_type=self.ObjectTypes.Node, properties=['PH', 'T', 'QM'], timestamps=self.GetTimeStamps()[0])
        df_nodes_results.columns = df_nodes_results.columns.droplevel([1, 2])
        df_nodes_results = df_nodes_results.T.unstack(level=0).T
        df_nodes_results = df_nodes_results.droplevel(0, axis=0)
        df_nodes = df_nodes_metadata.merge(on="tk",
                            how="outer",
                            right=df_nodes_results)

        js = {}

        for idx, row in df_nodes.iterrows():
            geom = row["geometry"]
            x, y = geom.x, geom.y

            j = pp.create_junction(
                net,
                pn_bar=float(row['PH']),
                tfluid_k=273.15 + float(row['T']),
                height_m=float(row['Zkor']),
                name=f"{row['Name']}~{row['tk']}"
            )

            # Assign geodata to junction_geodata table
            net.junction_geodata.at[j, "x"] = x
            net.junction_geodata.at[j, "y"] = y

            js[row['tk']] = j

        # --- Pipes ---
        df_pipes_metadata = self.generate_element_metadata_dataframe(element_type=self.ObjectTypes.Pipe, properties=['L', 'Di', 'Rau', 'Name'], end_nodes=True, geometry=True)
        
        df_pipes_metadata['Rau'] = df_pipes_metadata['Rau'].str.replace(',', '.', regex=False)
        df_pipes_metadata['L'] = df_pipes_metadata['L'].str.replace(',', '.', regex=False)
        df_pipes_metadata['L'] = df_pipes_metadata['L'].astype(float)

        ps = {}

        for idx, row in df_pipes_metadata.iterrows():
            geom = row["geometry"]
            coords = list(geom.coords)        

            # Create pipe
            p = pp.create_pipe_from_parameters(
                net,
                from_junction=js[row['fkKI']],
                to_junction=js[row['fkKK']],
                length_km=float(row['L']) / 1000.,
                diameter_m=float(row['Di']) / 1000.,
                k_mm=float(row['Rau']),
                name=f"{row['Name']}~{row['tk']}"
            )
            ps[row['tk']] = p

            net.pipe_geodata.at[p, "coords"] = coords

        # --- Source/Sinks ---
        for idx, row in df_nodes.iterrows():
            ktyp = (row.get("Ktyp"))
            tk = row.get("tk")

            # Create source if Ktyp is PKON and PH > 0
            if ktyp == "PKON" and float(row.get("PH", 0)) > 0:
                pp.create_ext_grid(
                    net,
                    junction=js[tk],
                    p_bar=float(row["PH"]),
                    t_k=273.15 + float(row["T"]),
                    name=f"Src: {row['Name']}~{tk}"
                )

            # Create sink if Ktyp is QKON and QM < 0
            elif ktyp == "QKON" and float(row.get("QM", 0)) < 0:
                pp.create_sink(
                    net,
                    junction=js[tk],
                    mdot_kg_per_s=abs(float(row["QM"])),
                    name=f"Snk: {row['Name']}~{tk}"
                )

        return net
    
    def SIR_3S_to_nx_graph(self):
        """
        Build a directed NetworkX graph from SIR 3S model.

        Parameters
        ----------

        Returns
        -------
        nx.DiGraph
            Directed graph with nodes and edges populated from SIR 3S model.
        """
        logger.info("[graph] Building nx graph...")

        # --- Nodes ---
        try:
            df_nodes = self.generate_element_metadata_dataframe(
                element_type=self.ObjectTypes.Node,
                properties=["Fkcont"],
                geometry=True
            )
            logger.info(f"[graph] Retrieved {len(df_nodes)} nodes.")
        except Exception as e:
            logger.error(f"[graph] Failed to retrieve node metadata: {e}")
            return nx.DiGraph()

        # --- Edges ---
        try:
            df_edges=self.generate_hydraulic_edge_dataframe()
        except Exception as e:
            logger.error(f"[graph] Failed to retrieve edges: {e}")
            return nx.DiGraph()

        # --- Build graph ---
        G = nx.DiGraph()

        # Add nodes with attributes
        logger.info("[graph] Adding nodes to graph...")
        for _, row in df_nodes.iterrows():
            try:
                attr = row.to_dict()

                geom = row['geometry']
                if isinstance(geom, str):
                    geom = wkt.loads(geom)
                elif isinstance(geom, BaseGeometry):
                    pass
                else:
                    raise ValueError(f"[graph] Unsupported geometry type: {type(geom)}")

                G.add_node(row['tk'], **attr)
            except Exception as e:
                logger.warning(f"[graph] Failed to add node '{row['tk']}': {e}")

        # Add edges with attributes
        logger.info("[graph] Adding edges to graph...")
        for _, row in df_edges.iterrows():
            try:
                attr = row.to_dict()

                geom = row['geometry']
                if isinstance(geom, str):
                    geom = wkt.loads(geom)
                elif isinstance(geom, BaseGeometry):
                    pass
                else:
                    raise ValueError(f"Unsupported geometry type: {type(geom)}")

                attr['geometry'] = geom

                G.add_edge(row['fkKI'], row['fkKK'], **attr)

            except Exception as e:
                logger.warning(f"[graph] Failed to add edge from '{row['fkKI']}' to '{row['fkKK']}': {e}")
                
        logger.info(f"[graph] Graph construction complete. Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
        return G
  
    def add_properties_to_graph(
        self,
        G: nx.DiGraph,
        element_type: str,        
        properties: List[str],
        timestamp: Optional[str] = None,
    ) -> nx.DiGraph:
        """
        Enrich nodes and edges in `G` with additional attributes by joining on 'tk'.

        Parameters
        ----------
        G : nx.DiGraph
            The already-built graph where nodes/edges have at least a 'tk' attribute.
        element_type : str
            The element type to filter by (must match df[element_type_col] and edge attr "element type").
        properties : list of str
            Column names from the dataframe to add as attributes
        timestamp: str
            Timestamp used for adding result properties. If None, STAT will be used.

        Returns
        -------
        nx.DiGraph
            The same graph instance with enriched attributes.
        """
        logger.info(f"[graph] Enriching graph with properties for element_type='{element_type}'")

        # --- Validate property availability (optional, keep if you want the checks) ---
        try:
            available_metadata_props = self.GetPropertiesofElementType(ElementType=self.get_object_type_enum(element_type))
            available_result_props = self.GetResultProperties_from_elementType(
                elementType=self.get_object_type_enum(element_type),
                onlySelectedVectors=False
            )
            metadata_props: List[str] = []
            result_props: List[str] = []
            if properties is None:
                logger.warning(
                    f"[graph] No properties given → using ALL metadata and STAT result properties for {element_type}. "
                    "This can lead to long runtimes."
                )
                metadata_props = available_metadata_props or []
                result_props = available_result_props or []
            else:
                for prop in properties:
                    if prop in (available_result_props or []):
                        result_props.append(prop)
                    elif prop in (available_metadata_props or []):
                        metadata_props.append(prop)
                    else:
                        logger.warning(
                            f"[graph] Property '{prop}' not found in metadata or result properties of type {element_type}. Excluding."
                        )
                all_props_to_use = metadata_props + result_props
            logger.info(f"[graph] Using {len(metadata_props)} metadata props and {len(result_props)} result props.")
        except Exception as e:
            logger.error(f"[graph] Error validating metadata/result properties: {e}. Aborting.")
            return G

        # --- Build dataframe with at least ['tk', *requested_columns] ---
        try:
            tks = self.GetTksofElementType(ElementType=self.get_object_type_enum(element_type))
            if not tks:
                logger.error(f"[graph] No elements exist for element type: {element_type}: {e}")
                return G

            df_metadata = self.generate_element_metadata_dataframe(
                element_type=self.get_object_type_enum(element_type),
                properties=metadata_props,
                element_type_col=False,
                geometry=False,
                end_nodes=False
            )

            simulation_timestamps, tsStat, tsMin, tsMax = self.GetTimeStamps()
            available_timestamps = list(simulation_timestamps) if simulation_timestamps else []

            if timestamp and (timestamp in available_timestamps):
                timestamp_for_values = timestamp
            else:
                timestamp_for_values = tsStat

            df_results = self.generate_element_results_dataframe(
                element_type=self.get_object_type_enum(element_type),
                properties=result_props,
                timestamps=[timestamp_for_values]
            )
            
            df_results.columns = df_results.columns.droplevel([1, 2])
            df_results = df_results.T.unstack(level=0).T
            df_results = df_results.droplevel(0, axis=0)
            df = df_metadata.merge(on="tk",
                             how="outer",
                             right=df_results)
            
            logger.debug(f"{df.columns}")

            if df is None or df.empty:
                logger.info(f"[graph] Empty metadata DataFrame for element_type='{element_type}'. Nothing to add.")
                return G

        except Exception as e:
            logger.error(f"[graph] Failed to retrieve metadata for enrichment: {e}")
            return G

        # --- Decide which columns to add; never add these ---
        never_add = {"geometry", "fkKI", "fkKK", "tk", "element_type"}
        add_cols = [c for c in (all_props_to_use or []) if c in df.columns and c not in never_add]
        if not add_cols:
            logger.info(f"[graph] No permissible columns to add for element_type='{element_type}'.")
            return G

        # --- Build tk -> {prop: value, ...} mapping ---
        try:
            df_updates = (
                df[["tk"] + add_cols]
                .drop_duplicates(subset=["tk"], keep="last")
                .set_index("tk")
            )
        except KeyError as e:
            logger.error(f"[graph] Required columns missing in df: {e}")
            return G

        tk_to_attrs = df_updates.to_dict(orient="index")

        nodes_updated = 0
        edges_updated = 0

        try:
            if element_type == "Node":
                for _, data in G.nodes(data=True):
                    tk = data.get("tk")
                    if tk is None:
                        continue
                    row = tk_to_attrs.get(tk)
                    if row is None:
                        continue
                    updates = {k: v for k, v in row.items() if k not in never_add}
                    if updates:
                        data.update(updates)
                        nodes_updated += 1
        except Exception as e:
            logger.error(f"[graph] Error while updating nodes: {e}")

        # --- Update edges (filter by 'element type' attr in the graph) ---
        try:
            if element_type != "Node":
                for _, _, data in G.edges(data=True):
                    if data.get("element type") != element_type:
                        continue
                    tk = data.get("tk")
                    if tk is None:
                        continue
                    row = tk_to_attrs.get(tk)
                    if row is None:
                        continue
                    updates = {k: v for k, v in row.items() if k not in never_add}
                    if updates:
                        data.update(updates)
                        edges_updated += 1
        except Exception as e:
            logger.error(f"[graph] Error while updating edges: {e}")

        logger.info(
            "[graph] Enrichment summary for element_type='%s': nodes_updated=%d; edges_updated=%d; cols_added=%s",
            str(element_type), nodes_updated, edges_updated, add_cols
        )
        return G
    
    def get_object_type_enum(self, element_type: str):
        """
        Return the enum member from self.ObjectTypes corresponding to the given element_type string.

        Parameters
        ----------
        element_type : str
            Name of the element type (e.g., 'Node', 'Pipe').

        Returns
        -------
        Enum member from self.ObjectTypes if found, else None.
        """
        try:
            # Normalize input to match attribute names
            normalized = element_type.strip()
            return getattr(self.ObjectTypes, normalized)
        except AttributeError:
            logger.error(f"[graph] Invalid element_type '{element_type}' — not found in ObjectTypes.")
            return None
def main():
    #!/usr/bin/env python
    # coding: utf-8
    
    # In[1]:
    
    
    import sys # for automation and parallelization
    manual, scenario = (True, 'base') if 'ipykernel' in sys.argv[0] else (False, sys.argv[1])
    
    
    # # OSMNX
    
    # In[2]:
    
    
    import sys
    sys.path.insert(0, r'../../../quetzal')
    
    import geopandas as gpd
    from shapely import geometry
    import osmnx as ox
    import geopandas as gpd
    import os
    
    from syspy.spatial.graph.graphbuilder import GraphBuilder, OsmnxCleaner
    from syspy.spatial.graph import graphbuilder
    
    training_folder = '../../'
    input_folder = training_folder + r'inputs/'
    
    
    # In[3]:
    
    
    if manual:
        get_ipython().run_line_magic('matplotlib', 'inline')
        
    import matplotlib.pyplot as plt
    plt.rcParams['figure.figsize'] = [16, 9]
    
    
    # In[4]:
    
    
    zones = gpd.read_file(r'../../inputs/zones/zones.geojson')
    hull = geometry.MultiPolygon(zones['geometry'].values).buffer(1e-3)
    hull
    
    
    # # OSMNX API
    
    # In[5]:
    
    
    drive = ox.graph_from_polygon(hull, network_type='drive')
    
    
    # In[6]:
    
    
    plot = ox.plot_graph(drive)
    
    
    # In[7]:
    
    
    road_nodes, road_links = ox.graph_to_gdfs(drive)
    
    
    # In[8]:
    
    
    road_links.rename(columns={'u': 'from', 'v': 'to'}, inplace=True)
    road_nodes['osmid'] = road_nodes['osmid'].astype(str)
    road_nodes = road_nodes.set_index('osmid')[['geometry']]
    road_links[['from', 'to']] = road_links[['from', 'to']].astype(str)
    
    
    # # cleaning
    
    # In[9]:
    
    
    from shapely import geometry
    def simplify_link(g):
        l = list(g.coords)
        return geometry.LineString([l[0], l[-1]])
    
    
    # In[10]:
    
    
    road_links['geometry'] = road_links['geometry'].apply(simplify_link)
    oc = OsmnxCleaner(
        road_links, 
        road_nodes, 
        a='from', 
        b='to'
    )
    
    
    # In[11]:
    
    
    oc.add_reversed_links(
        direction_column='oneway', 
        reverse_value=False # the boolean has been stored as a string    
    )
    oc.clean_geometries()
    oc.fix_nodeset_consistency()
    
    
    # # export 
    
    # In[12]:
    
    
    from quetzal.model.stepmodel import StepModel
    
    sm = StepModel(epsg=4326, coordinates_unit='degree')
    sm.road_links = oc.links[['a', 'b', 'length', 'geometry', 'highway']].copy()
    sm.road_nodes = oc.nodes[['geometry']].copy()
    
    
    # In[13]:
    
    
    sm.integrity_fix_road_network(cutoff=10, recursive_depth=5)
    
    
    # In[14]:
    
    
    sm.road_links['highway'] = sm.road_links['highway'].astype(str)
    irrelevant = ['pedestrian', 'footway', 'service', 'cycleway', 'residential']
    sm.road_links = sm.road_links.loc[~sm.road_links['highway'].isin(irrelevant)]
    
    
    # In[15]:
    
    
    sm.to_json(input_folder + 'road', only_attributes=['road_links', 'road_nodes'])
    
from multiprocessing import freeze_support
if __name__ == '__main__':
    freeze_support()
    main()

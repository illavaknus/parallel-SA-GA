import xml.etree.ElementTree as ET
import numpy as np

xml_data = ET.parse('data/eil101.xml')

graph = xml_data.find('graph')

vertices = graph.findall('vertex')

count = 0
dist_matrix = {}

for vertex in vertices:
	edges = vertex.findall('edge')
	vertex_edges_cost = [99999]*(len(edges)+1)
	for edge in edges:
		vertex_edges_cost[int(edge.text)] = float(edge.get('cost'))
	dist_matrix[count] = vertex_edges_cost
	count += 1
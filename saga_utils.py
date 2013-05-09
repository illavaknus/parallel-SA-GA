import xml.etree.ElementTree as ET
import numpy as np

def energy_distance(route, dist_matrix):
	total_distance = 0
	for i in range(len(route)):
		total_distance += dist_matrix[route[i]][route[(i+1)%len(route)]]
	return total_distance

def shuffle_list(element_list, shuffle_count = None):
	if(shuffle_count == None):
		return np.random.shuffle(element_list)
	else:
		indices = np.random.randint(0,len(element_list), shuffle_count+1)
		# print indices
		for i in range(len(indices)):
			# print indices[i], indices[(i+1)%shuffle_count]
			# print element_list[indices[i]], element_list[indices[(i+1)%shuffle_count]]
			element_list[indices[i]], element_list[indices[(i+1)%shuffle_count]] = element_list[indices[(i+1)%shuffle_count]], element_list[indices[i]]
		return element_list


def parse_xml_data(filename):
	xml_data = ET.parse(filename)

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

	return dist_matrix
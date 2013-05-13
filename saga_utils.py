import xml.etree.ElementTree as ET
import numpy as np

def accumulate(list_):
	sum_ = 0
	for x in list_:
		yield sum_
		sum_ += x
	yield sum_

def energy_distance(route, dist_matrix):
	total_distance = 0
	for i in range(len(route)):
		# print dist_matrix[route[i]][route[(i+1)%len(route)]]
		if i == len(route) - 1:
			total_distance += dist_matrix[route[i]][route[0]]
		else:
			total_distance += dist_matrix[route[i]][route[(i+1)]]
	return total_distance

def shuffle_list(element_list, shuffle_count = None):
	if(shuffle_count == None):
		return np.random.shuffle(element_list)
	else:
		assert(shuffle_count <= len(element_list))
		i = 0
		while i < shuffle_count:
			index_one = np.random.randint(0,len(element_list))
			index_two = np.random.randint(0,len(element_list))
			if index_two == index_one:
				i -= 1
			else:
				element_list[index_one], element_list[index_two] = element_list[index_two], element_list[index_one]
				i += 1
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
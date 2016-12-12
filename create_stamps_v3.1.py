import ansa
import os
from ansa import base
from ansa import connections
from ansa import mesh
from ansa import morph
import math
import distribute_points as disPoint

def createCircStamp():
	## default values for Stamp
	#param_D = 15
	#param_H = 8
	#param_A = 75
	#param_R1 = 3 
	#param_R2 = 2
	#param_WD = 6 # a_param for weld diameter
	##
	## model parameters
	## pid_inner = inner hood
	## pid_outer = outer hood
	## pid_glue = glue pid
	#pid_inner = 20020110
	#pid_outer = 20020100
	#pid_glue = 960330
	#num_hexas = 4
	#search_dist = 25
	##
	## reconstruct parameters
	doReconstruct = True
	num_neighb = '2'
	expand_level = 2
	max_reconstruct = 5
	##
	## Read mesh param and quality files
	##
	ansa_home_dir = "S:/backup/cae_modelling/ansa/"
	if not os.path.exists(ansa_home_dir):
		ansa_home_dir = '/share/backup/cae_modelling/ansa/'
	quality_file = ansa_home_dir + "batch_mesh_sessions/3.5mm.ansa_qual"
	param_file = ansa_home_dir + "batch_mesh_sessions/shell_3.5mm.ansa_mpar"
	if os.path.isfile(quality_file):
		mesh.ReadQualityCriteria(quality_file)
	if os.path.isfile(param_file):
		mesh.ReadMeshParams(param_file)
	##
	base.All()
	a_params = base.CollectEntities(0, None, "A_PARAMETER")
	
	# type 
	#	0 str, 1 int, 2 float
	parList = [['D', 'param_D', 2], ['H', 'param_H', 2], ['A', 'param_A', 2], ['R1', 'param_R1', 2], 
				['R2', 'param_R2', 2], ['weldD', 'param_WD', 2], ['searchDist', 'search_dist', 2],
				['innerPID', 'pid_inner', 1],	['outerPID', 'pid_outer', 1], ['gluePID', 'pid_glue', 1],
				['glueMeshLen', 'glueMeshLen', 2], ['tGlue', 'tGlue', 2]]
				
	
	for item in parList:
		for a_param in a_params:
			ret = base.GetEntityCardValues(0, a_param, ('Value', ))
			type = item[2]
			if ret:
				if a_param._name == item[0]:
					if type == 2:
						globals()[item[1]] = float(ret['Value'])
					if type == 1:
						globals()[item[1]] = int(ret['Value'])
					if type == 0:
						globals()[item[1]] = str(ret['Value'])
					print(item[1], globals()[item[1]])				
					break
		
	# adjust number of hexa
	numHexOpt = [1, 4, 8, 16]
	reqNumHex = math.pow(param_WD/glueMeshLen, 2)		
	for i, opt in enumerate(numHexOpt):
		if i == len(numHexOpt)-1:
			num_hexas = opt
		elif opt <= reqNumHex < numHexOpt[i+1]:
			num_hexas = opt
			break
			
	params = [param_D, param_H, param_A, param_R1, param_R2]
	points = base.CollectEntities(0, None, "POINT")
	cnctns = []
	for point in points:
		if point._name == 'cone':
			shells = morph.CreateStamp("Circular", [point], params)
			# morph.MorphOrtho(loaded_elements=shells)
			if doReconstruct:
				# recontruct up to max_reconstruct times
				base.Or(shells)
				base.Neighb(num_neighb)
				n = 0
				off_elements = base.CalculateOffElements()
				while off_elements['TOTAL OFF'] and n < max_reconstruct:
					mesh.ReshapeViolatingShells(expand_level)
					mesh.ReconstructViolatingShells(expand_level)
					off_elements = base.CalculateOffElements()
					n += 1
			base.All()
			# create spotweld
			ret = base.GetEntityCardValues(0, point, ('X', 'Y', 'Z'))
			position = (ret['X'], ret['Y'], ret['Z'])
			cnctn = connections.CreateConnectionPoint("SpotweldPoint_Type", position)
			if cnctn:
				cnctns.append(cnctn)
				fields = {"D":param_WD, "P1":"#"+str(pid_inner), "P2":"#"+str(pid_outer), "FE Rep Type":"DYNA SPOT WELD", "Search Dist":search_dist, "Property":"PSOLID", "PSOLID ID":pid_glue}
				fields["Use LS DYNA Mat100"] = "no"
				fields["Number of hexas"] = num_hexas
				fields["Contact"] = "no"
				ret = base.SetEntityCardValues(0, cnctn, fields)
				if ret:
					print('Failed to set params to spot')
					print(fields)
					print(position)
					continue
				cnctn_projs = connections.GetConnectionProjections(cnctn, search_distance=search_dist)
				if cnctn_projs[0]:
					outer_skin_pos = cnctn_projs[0][1][0]
					fields = {'X':outer_skin_pos[0], 'Y':outer_skin_pos[1], 'Z':outer_skin_pos[2]}
					ret = base.SetEntityCardValues(0, cnctn, fields)
					if ret:
						print('Failed to set new position to spot')
						print(fields)
						print(position)
						continue
				else:
					print('Failed to find projection to spot')
					print(fields)
					print(position)
					continue
			else:
				print('Failed to create spot')
				print((position, point._id))
		#break
	connections.ReApplyConnections(cnctns)

#if __name__ == '__main__':
#	createCircStamp()

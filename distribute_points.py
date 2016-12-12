import ansa
from ansa import *

def _check_dist(pos1, pos2, tol):
	c1 = pos1[0] - pos2[0]
	if abs(c1) > tol:
		return(False)
	c2 = pos1[1] - pos2[1]
	if abs(c2) > tol:
		return(False)
	dist = ((c1)**2 + (c2)**2)**0.5
	if dist > tol:
		return(False)
	else:
		return(dist)

def _distribute_points(pid, n_width, n_height, dist_from_feature, point_name):
	##
	## Isolate main perimeter and exlude regions
	##
	pshell = base.GetEntity(constants.NASTRAN, "PSHELL", pid)
	prt_node_chains = base.CollectBoundaryNodes(pshell)
	i = 0
	all_chains = []
	for chain in prt_node_chains.perimeters:
		if i == 0:
			first_chain = chain
		all_chains += chain
		i += 1
	##
	exclude_pos = []
	for node in all_chains:
		ret = base.GetEntityCardValues(constants.NASTRAN, node, ('X1', 'X2', 'X3'))
		pos = (ret['X1'], ret['X2'], ret['X3'])
		exclude_pos.append(pos)
	##
	## use first_chain to isolate envelope
	##
	ymin = 0
	ymax = 0
	for node in first_chain:
		ret = base.GetEntityCardValues(constants.NASTRAN, node, ('X1', 'X2', 'X3'))
		if ymin == 0 and ymax == 0:
			ymin = ret['X2']
			ymax = ret['X2']
		elif ret['X2'] < ymin:
			ymin = ret['X2']
		elif ret['X2'] > ymax:
			ymax = ret['X2']
	delta_y = (ymax - ymin)/n_width
	#print((ymin, ymax))
	##
	## store nodal positions, split into 1mm bins
	##
	grids = base.CollectEntities(constants.NASTRAN, pshell, "GRID", recursive = True)
	grid_poses = dict()
	for grid in grids:
		ret = base.GetEntityCardValues(constants.NASTRAN, grid, ('X1', 'X2', 'X3'))
		pos = (ret['X1'], ret['X2'], ret['X3'])
		##
		toExclude = False
		for in_pos in exclude_pos:
			if _check_dist((in_pos[0], in_pos[1]), (pos[0], pos[1]), dist_from_feature):
				toExclude = True
				break
		if toExclude:
			continue
		##
		y_index = int(pos[1])
		if y_index in grid_poses:
			grid_poses[y_index] = grid_poses[y_index] + [pos]
		else:
			grid_poses[y_index] = [pos]
	##
	## use stored positions to find desired positions
	##
	for x in range(0, n_width):
		y_from = int(round(ymin + (x)*delta_y, 0))
		y_to = int(round(ymin + (x+1)*delta_y, 0))
		#print('From: ' + str(y_from) + ', To: ' + str(y_to))
		##
		## divide current area into 15mm slices, use xmin and xmax from smallest slize
		##
		n_div = int(round((y_to - y_from)/20, 0))
		delta_yy = (y_to - y_from)/n_div
		xxmin = 0
		xxmax = 0
		for y in range(0, n_div):
			yy_from = int(round(y_from + (y)*delta_yy, 0))
			yy_to = int(round(y_from + (y+1)*delta_yy, 0))
			yy_list = list(range(yy_from, yy_to+1))
			tmp_grid_poses = []
			for tmp_key in yy_list:
				if tmp_key in grid_poses:
					tmp_grid_poses += grid_poses[tmp_key]
			xmax = -999999
			xmin = 999999
			for pos in tmp_grid_poses:
				if pos[0] < xmin:
					xmin = pos[0]
				elif pos[0] > xmax:
					xmax = pos[0]
			if xxmax == 0 and xxmin == 0:
				xxmax = xmax
				xxmin = xmin
			#elif (xmax - xmin) < (xxmax - xxmin):
			elif (xmax - xmin) > (xxmax - xxmin):
				xxmin = xmin
				xxmax = xmax
			#print('From: ' + str(yy_from) + ', To: ' + str(yy_to) + ', Range: ' + str(xmax - xmin))
		##
		## Defining Y-coords
		##
		y_coord = int(round((ymin + x*delta_y) + delta_y/2, 0))
		y_list = [x + y for x in [y_coord] for y in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]]
		tmp_grid_poses = []
		for tmp_key in y_list:
			if tmp_key in grid_poses:
				tmp_grid_poses += grid_poses[tmp_key]
		#print('Y-coord: ' + str(y_coord))
		##
		## Defining X-coords
		##
		delta_x = (xxmax - xxmin)/n_height
		x_coords = [int(round((xxmin + y*delta_x) + delta_x/2, 0)) for y in range(0, n_height)]
		if (x % 2 == 0):
			# special treatment for even row
			x_coords = [(x_coords[z] + x_coords[z+1])/2 for z in range(0,n_height - 1) ]
		##
		## find closest point
		##
		pnts = []
		for x_coord in x_coords:
			min_dist = 999
			search_pos = (x_coord, y_coord)
			for pos in tmp_grid_poses:
				xy_pos = (pos[0], pos[1])
				dist = _check_dist(search_pos, xy_pos, min_dist)
				if dist:
					if dist < min_dist:
						min_dist = dist
						point_pos = pos
			toClose = False
			for pos in pnts:
				xy_pos = (pos[0], pos[1])
				dist = _check_dist((point_pos[0], point_pos[1]), xy_pos, dist_from_feature) 
				if dist:
					toClose = True
			if toClose:
				continue
			pnts.append(point_pos)
			pnt = base.Newpoint(point_pos[0], point_pos[1], point_pos[2])
			base.SetEntityCardValues(constants.NASTRAN, pnt, {'Name' : point_name})


pid = 20020111
pid = 1
n_width = 15
n_height = 12
dist_from_feature = 30
point_name = 'cone'

_distribute_points(pid, n_width, n_height, dist_from_feature, point_name)

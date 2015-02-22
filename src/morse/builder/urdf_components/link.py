import bpy, math
from mathutils import Vector, Matrix, Euler
#from io_scene_urdf.urdf_parser.urdf import *

from morse.builder.urdf_parser.urdf import *
from morse.builder.urdf_components.pathretriever import *
import rospkg
class URDFLink:

	def __init__(self, urdf_link):
		self.urdf_link = urdf_link
		self.name = urdf_link.name
		self.inertial = urdf_link.inertial

		# Copy visual or collision mesh if only one of them exists:
		if urdf_link.visual and not urdf_link.collision:
			urdf_link.collision = urdf_link.visual
		elif urdf_link.collision and not urdf_link.visual:
			urdf_link.visual = urdf_link.collision

		self.visual = urdf_link.visual
		self.collision = urdf_link.collision

		#self._get_origin()
		# Add empty at 0 with link name

		bpy.ops.object.add(type = "EMPTY")
		self.frame = bpy.context.selected_objects[0]
		self.frame.name = self.name
		self.frame.empty_draw_type = 'ARROWS'
		self.frame.empty_draw_size = 0.05


		if self.urdf_link.origin:
			print('WARNING: Link origin will be overwritten by joint origin')
			self.frame.location = self.urdf_link.origin.xyz
			self.frame.rotation_quaternion = Euler(self.urdf_link.origin.rpy, 'XYZ').to_quaternion()

		self.mesh_visual = None
		self.mesh_collision = None
		self.mesh_visual_type = None
		self.mesh_collision_type = None
		print('got here.......................')
		

		print('and THEN got here.......................')

		if self.visual:
			self.build_visual()
		if self.collision:
			self.build_collision()
		# # Add bones
		# self.bone = armature.data.edit_bones.new(self.name + '_bone')

		#print("Link %s at %s" % (self.name, self.xyz))

	def _get_origin(self):
		""" Links do not define proper origin. We still try to extract one
		to correctly place the bones' tails when necessary (like, when a bone
		is not connected to any other child bone).
		"""
		xyz = (0,0,0)
		rpy = None

		if self.inertial:
			xyz = self.inertial.origin.xyz
			rpy = self.inertial.origin.rpy
		elif self.collision:
			xyz = self.collision.origin.xyz
			rpy = self.collision.origin.rpy
		elif self.visual:
			xyz = self.visual.origin.xyz
			rpy = self.visual.origin.rpy

		self.xyz = Vector(xyz)
		if rpy:
			self.rot = Euler(rpy, 'XYZ').to_quaternion()
		else:
			self.rot = Euler((0,0,0)).to_quaternion()


	def build_visual(self):

		geometry = self.urdf_link.visual.geometry
		print(geometry)
		if isinstance(geometry, Box):

			# Require size as Vector () geometry.size
			bpy.ops.mesh.primitive_cube_add()
			self.mesh_visual = bpy.context.selected_objects[0]
			self.mesh_visual.dimensions = geometry.size
			self.mesh_visual_type = 'BOX'
			
		elif isinstance(geometry, Cylinder):
			# Requires geometry.radius and geometry.length
			bpy.ops.mesh.primitive_cylinder_add(radius = geometry.radius, depth = geometry.length)
			self.mesh_visual = bpy.context.selected_objects[0]
			self.mesh_visual_type = 'CYLINDER'	
		elif isinstance(geometry, Sphere):
			# Require geometry.radius
			bpy.ops.mesh.primitive_uv_sphere_add(size = geometry.radius)
			self.mesh_visual = bpy.context.selected_objects[0]
			self.mesh_visual_type = 'SPHERE'
		elif isinstance(geometry, Mesh): 
			print('Mesh type')
		 	# Get absolute path
			rel_filepath = geometry.filename
			retriever = PathRetriever(rel_filepath)
			filepath = retriever.path
			print(filepath + '.......................')

			# Import mesh
			bpy.ops.import_mesh.stl(filepath= filepath)
			self.mesh_visual = bpy.context.selected_objects[0]
			self.mesh_visual.select = True
			bpy.context.scene.objects.active = self.mesh_visual
			if geometry.scale:
				scale = Vector(geometry.scale)
				bpy.ops.transform.resize(value = scale)
			self.mesh_visual_type = 'MESH'

		if self.mesh_visual:	
			self.mesh_visual.name = self.frame.name + '_visual' 
			# Make frame parent of mesh
			self.mesh_visual.parent = self.frame
			# Put mesh at the right location, but this will be overwritten by joint location
			if self.urdf_link.visual.origin:
				self.mesh_visual.location = self.urdf_link.visual.origin.xyz
				self.mesh_visual.rotation_quaternion = Euler(self.urdf_link.visual.origin.rpy, 'XYZ').to_quaternion()
		print('finish building visual mesh.......')
	def build_collision(self):
		geometry = self.urdf_link.collision.geometry
		print(geometry)
		if isinstance(geometry, Box):

			# Require size as Vector () geometry.size
			bpy.ops.mesh.primitive_cube_add()
			self.mesh_collision= bpy.context.selected_objects[0]
			self.mesh_collision.dimensions = geometry.size
			self.mesh_collision_type = 'BOX'
		elif isinstance(geometry, Cylinder):
			# Requires geometry.radius and geometry.length
			bpy.ops.mesh.primitive_cylinder_add(radius = geometry.radius, depth = geometry.length)
			self.mesh_collision = bpy.context.selected_objects[0]
			self.mesh_collision_type = 'CYLINDER'
		elif isinstance(geometry, Sphere):
			# Require geometry.radius
			bpy.ops.mesh.primitive_uv_sphere_add(size = geometry.radius)
			self.mesh_collision = bpy.context.selected_objects[0]
			self.mesh_collision_type = 'SPHERE'
		elif isinstance(geometry, Mesh): 
			print('Mesh type')
		 	# Get absolute path			
			rel_filepath = geometry.filename
			retriever = PathRetriever(rel_filepath)
			filepath = retriever.path

			# Import mesh 
			bpy.ops.import_mesh.stl(filepath= filepath)
			self.mesh_collision = bpy.context.selected_objects[0]
			self.mesh_collision.select = True
			bpy.context.scene.objects.active = self.mesh_collision
			if geometry.scale:
				scale = Vector(geometry.scale)
				bpy.ops.transform.resize(value = scale)
			self.mesh_collision_type = 'MESH'	
		print('No problem here...............')
		if self.mesh_collision:	
			self.mesh_collision.name = self.frame.name + '_collision' 
			# Make frame parent of mesh
			self.mesh_collision.parent = self.frame
			# Put mesh at the right location, but this will be overwritten by joint location
			if self.urdf_link.collision.origin:
				self.mesh_collision.location = self.urdf_link.collision.origin.xyz
				self.mesh_collision.rotation_quaternion = Euler(self.urdf_link.collision.origin.rpy, 'XYZ').to_quaternion()
	
	def set_physics(self, physics_type = 'STATIC'):
		print('Setting physics of ' + self.name)
		if physics_type == 'STATIC':
			self.frame.game.physics_type = 'STATIC'
			self.frame.game.use_collision_compound = True
			self.frame.game.radius = 0.01
			if self.mesh_visual:
				self.mesh_visual.game.physics_type = 'STATIC'
				self.mesh_visual.game.use_ghost = True
			if self.mesh_collision:
				self.mesh_collision.game.physics_type = 'STATIC'
		else:
			# Set frame to be rigid body and compound
			print('Set frame to be rigid body and compound')
			self.frame.game.physics_type = 'RIGID_BODY'
			self.frame.game.use_collision_compound = True
			self.frame.game.radius = 0.01

			print('Set visual mesh to be static and ghost')
			# Set visual mesh to be static and ghost
			if self.mesh_visual:
				self.mesh_visual.game.physics_type = 'RIGID_BODY'
				self.mesh_visual.game.use_ghost = True
			print('Set collision mesh to be rigid body')
			# Set collision mesh to be rigid body
			if self.mesh_collision:
				self.mesh_collision.game.physics_type = 'RIGID_BODY'
		if self.mesh_collision:
			self.mesh_collision.game.use_collision_compound = True
			self.mesh_collision.game.radius = 0.01
			print('Set collision bounds for collision mesh')
			# Set collision bounds for collision mesh
			print('use collision bounds')
			self.mesh_collision.game.use_collision_bounds = True
			print('set collision margin')
			# self.mesh_collision.game.collision_margin = 0.06
			if self.mesh_collision_type == 'BOX':
				print('if type box')
				self.mesh_collision.game.collision_bounds_type = 'BOX'
			elif self.mesh_collision_type == 'CYLINDER':
				print('if type cylinder')
				self.mesh_collision.game.collision_bounds_type = 'CYLINDER'
			elif self.mesh_collision_type == 'SPHERE':
				print('if type sphere')
				self.mesh_collision.game.collision_bounds_type = 'SPHERE'
			else: 
				print('if type mesh')
				self.mesh_collision.game.collision_bounds_type = 'CONVEX_HULL'
	
	def set_motion(self, motion_type = 'fixed'):
		if motion_type == 'fixed':
			self.frame.game.lock_location_x = True
			self.frame.game.lock_location_y = True
			self.frame.game.lock_location_z = True
			self.frame.game.lock_rotation_x = True
			self.frame.game.lock_rotation_y = True
			self.frame.game.lock_rotation_z = True

			




	# NOT BEING USED				
	def get_path(self, rel_filepath):
		if  rel_filepath.find('package://') != -1:
			print('Retrieving path.....')
			# Extract package name
			ind = rel_filepath.find('//')
			temp = rel_filepath[ind+2:]
			ind2 = temp.find('/')
			package_name = temp[:ind2]
			remain = temp[ind2:]

			# Find package path

			rospack = rospkg.RosPack()
			package_path = rospack.get_path(package_name)
			# Return absolute path
			return package_path + remain
		else:
			print('The path ' + rel_filepath + ' can\'t be handled')
			return rel_filepath

	# def build_visual(self):

	# 	geometry = self.urdf_link.visual.geometry
	# 	# Add mesh
	# 	mesh = self._add_mesh(geometry)	
	# 	if mesh:

	# 		self.mesh_visual = mesh
	# 		# Create mesh name
	# 		self.mesh_visual.name = self.frame.name + '_visual' 
	# 		# Make frame parent of mesh
	# 		self.mesh_visual.parent = self.frame
	# 		# Put mesh at the right location, but this will be overwritten by joint location
	# 		if self.urdf_link.visual.origin:
	# 			self.mesh_visual.location = self.urdf_link.visual.origin.xyz
	# 			self.mesh_visual.rotation_quaternion = Euler(self.urdf_link.visual.origin.rpy, 'XYZ').to_quaternion()
	# def build_collision(self):
	# 	# TODO: Load mesh from file
	# 	geometry = self.urdf_link.collision.geometry

	# 	# Add mesh
	# 	mesh = self._add_mesh(geometry)	
	# 	if mesh:
	# 		self.mesh_collision = mesh
	# 		# Create mesh name
	# 		self.mesh_collision.name = self.frame.name + '_collision' 
	# 		# Make frame parent of mesh
	# 		self.mesh_collision.parent = self.frame
	# 		# Put mesh at the right location, but this will be overwritten by joint location
	# 		if self.urdf_link.collision.origin:
	# 			self.mesh_collision.location = self.urdf_link.collision.origin.xyz
	# 			self.mesh_collision.rotation_quaternion = Euler(self.urdf_link.collision.origin.rpy, 'XYZ').to_quaternion()	
	# def _add_mesh(self, geometry):
	# 	# If it is a box
	# 	# try: 
	# 	# 	isinstance(geometry, Mesh)
	# 	# except Exception, e:
	# 	# 	print('Problem checking mesh type..........................')
	# 	print(geometry)
	# 	if isinstance(geometry, Box):

	# 		# Require size as Vector () geometry.size
	# 		bpy.ops.mesh.primitive_cube_add()
	# 		mesh = bpy.context.selected_objects[0]
	# 		mesh.dimensions = geometry.size
			
	# 	elif isinstance(geometry, Cylinder):
	# 		# Requires geometry.radius and geometry.length
	# 		bpy.ops.mesh.primitive_cylinder_add(radius = geometry.radius, depth = geometry.length)
	# 		mesh = bpy.context.selected_objects[0]

	# 	elif isinstance(geometry, Sphere):
	# 		# Require geometry.radius
	# 		bpy.ops.mesh.primitive_uv_sphere_add(size = geometry.radius)
	# 		mesh = bpy.context.selected_objects[0]

	# 	elif isinstance(geometry, Mesh): 
	# 		print('Mesh type')
	# 	 	Requires file path geometry.filename
	#  		filepath = geometry.filename
	# 		bpy.ops.import_mesh.stl(filepath= filepath)
	# 		mesh = bpy.context.selected_objects[0]

	# 	else: 
	# 		return None
	# 	return mesh

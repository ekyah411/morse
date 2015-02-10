import bpy, math
from mathutils import Vector, Matrix, Euler
from io_scene_urdf.urdf_parser.urdf import *
class URDFLink:

	def __init__(self, urdf_link):
		self.urdf_link = urdf_link
		self.name = urdf_link.name
		self.inertial = urdf_link.inertial
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
		# Add mesh
		self.mesh_visual = self._add_mesh(geometry)	
		# Create mesh name
		self.mesh_visual.name = self.frame.name + '_visual' 
		# Make frame parent of mesh
		self.mesh_visual.parent = self.frame
		# Put mesh at the right location, but this will be overwritten by joint location
		if self.urdf_link.visual.origin:
			self.mesh_visual.location = self.urdf_link.visual.origin.xyz
			self.mesh_visual.rotation_quaternion = Euler(self.urdf_link.visual.origin.rpy, 'XYZ').to_quaternion()
	def build_collision(self):
		# TODO: Load mesh from file
		geometry = self.urdf_link.collision.geometry
		# Add mesh
		self.mesh_collision = self._add_mesh(geometry)	
		# Create mesh name
		self.mesh_collision.name = self.frame.name + '_collision' 
		# Make frame parent of mesh
		self.mesh_collision.parent = self.frame
		# Put mesh at the right location, but this will be overwritten by joint location
		if self.urdf_link.collision.origin:
			self.mesh_collision.location = self.urdf_link.collision.origin.xyz
			self.mesh_collision.rotation_quaternion = Euler(self.urdf_link.collision.origin.rpy, 'XYZ').to_quaternion()


	def _add_mesh(self, geometry):
		# If it is a box
		if isinstance(geometry, Box):
			# Require size as Vector () geometry.size
			bpy.ops.mesh.primitive_cube_add()
			mesh = bpy.context.selected_objects[0]
			mesh.dimensions = geometry.size


		elif isinstance(geometry, Mesh): 
			# Requires file path geometry.filename
			filepath = geometry.filename
			bpy.ops.import_mesh.stl(filepath= filepath)
			mesh = bpy.context.selected_objects[0]

		elif isinstance(geometry, Cylinder):
			# Requires geometry.radius and geometry.length
			bpy.ops.mesh.primitive_cylinder_add(radius = geometry.radius, depth = geometry.length)
			mesh = bpy.context.selected_objects[0]

		elif isinstance(geometry, Sphere):
			# Require geometry.radius
			bpy.ops.mesh.primitive_uv_sphere_add(size = geometry.radius)
			mesh = bpy.context.selected_objects[0]
		return mesh

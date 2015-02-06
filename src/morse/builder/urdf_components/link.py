import bpy, math
from mathutils import Vector, Matrix, Euler
import copy
class URDFLink:

	def __init__(self, urdf_link):

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
			   
		bpy.ops.object.add(type="MESH")
		self.mesh_visual = bpy.context.selected_objects[0]
		self.mesh_visual.name = self.frame.name + '_visual' 
		self.mesh_visual.parent = self.frame
		# TODO: Load mesh from file

	def build_collision(self):
		bpy.ops.object.add(type="MESH")
		self.mesh_collision = bpy.context.selected_objects[0]
		self.mesh_collision.name = self.frame.name + '_collision' 
		self.mesh_collision.parent = self.frame
		# TODO: Load mesh from file


	# Make empty parent of mesh



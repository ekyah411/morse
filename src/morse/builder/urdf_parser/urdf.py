from morse.builder.urdf_parser.xml_reflection.basics import * 
from morse.builder.urdf_parser.xml_reflection.core import *

# Add a 'namespace' for names so that things don't conflict between URDF and SDF?
# A type registry? How to scope that? Just make a 'global' type pointer?
# Or just qualify names? urdf.geometric, sdf.geometric

start_namespace('urdf')

add_type('element_link', SimpleElementType('link', str))
add_type('element_xyz', SimpleElementType('xyz', 'vector3'))

verbose = True

class Pose(Object):
	def __init__(self, xyz=None, rpy=None):
		self.xyz = xyz
		self.rpy = rpy
	
	def check_valid(self):
		assert self.xyz is not None or self.rpy is not None
	
	# Aliases for backwards compatibility
	@property
	def rotation(self): return self.rpy
	@rotation.setter
	def rotation(self, value): self.rpy = value
	@property
	def position(self): return self.xyz
	@position.setter
	def position(self, value): self.xyz = value

reflect(Pose, params = [
	Attribute('xyz', 'vector3', False),
	Attribute('rpy', 'vector3', False)
	])


# Common stuff
name_attribute = Attribute('name', str)
origin_element = Element('origin', Pose, False)

class Color(Object):
	def __init__(self, *args):
		# What about named colors?
		count = len(args)
		if count == 4 or count == 3:
			self.rgba = args
		elif count == 1:
			self.rgba = args[0]
		elif count == 0:
			self.rgba = None
		if self.rgba is not None:
			if len(self.rgba) == 3:
				self.rgba += [1.]
			if len(self.rgba) != 4:
				raise Exception('Invalid color argument count')

reflect(Color, params = [
	Attribute('rgba', 'vector4')
	])


class JointDynamics(Object):
	def __init__(self, damping=None, friction=None):
		self.damping = damping
		self.friction = friction

reflect(JointDynamics, params = [
	Attribute('damping', float, False),
	Attribute('friction', float, False)
	])


class Box(Object):
	def __init__(self, size = None):
		self.size = size

reflect(Box, params = [
	Attribute('size', 'vector3')
	])


class Cylinder(Object):
	def __init__(self, radius = 0.0, length = 0.0):
		self.radius = radius
		self.length = length

reflect(Cylinder, params = [
	Attribute('radius', float),
	Attribute('length', float)
	])


class Sphere(Object):
	def __init__(self, radius=0.0):
		self.radius = radius

reflect(Sphere, params = [
	Attribute('radius', float)
	])


class Mesh(Object):
	def __init__(self, filename = None, scale = None):
		self.filename = filename
		self.scale = scale

reflect(Mesh, params = [
	Attribute('filename', str),
	Attribute('scale', 'vector3', required=False)
	])


class GeometricType(ValueType):
	def __init__(self):
		self.factory = FactoryType('geometric', {
			'box': Box,
			'cylinder': Cylinder,
			'sphere': Sphere,
			'mesh': Mesh
			})
	
	def from_xml(self, node):
		children = xml_children(node)
		assert len(children) == 1, 'One element only for geometric'
		return self.factory.from_xml(children[0])
	
	def write_xml(self, node, obj):
		name = self.factory.get_name(obj)
		child = node_add(node, name)
		obj.write_xml(child)

add_type('geometric', GeometricType())

class Collision(Object):
	def __init__(self, geometry = None, origin = None):
		self.geometry = geometry
		self.origin = origin

reflect(Collision, params = [
	origin_element,
	Element('geometry', 'geometric')
	])


class Texture(Object):
	def __init__(self, filename = None):
		self.filename = filename

reflect(Texture, params = [
	Attribute('filename', str)
	])


class Material(Object):
	def __init__(self, name=None, color=None, texture=None):
		self.name = name
		self.color = color
		self.texture = texture
	
	def check_valid(self):
		if self.color is None and self.texture is None:
			on_error("Material has neither a color nor texture")

reflect(Material, params = [
	name_attribute,
	Element('color', Color, False),
	Element('texture', Texture, False)
	])


class Visual(Object):
	def __init__(self, geometry = None, material = None, origin = None):
		self.geometry = geometry
		self.material = material
		self.origin = origin

reflect(Visual, params = [
	origin_element,
	Element('geometry', 'geometric'),
	Element('material', Material, False)
	])


class Inertia(Object):
	KEYS = ['ixx', 'ixy', 'ixz', 'iyy', 'iyz', 'izz']
	
	def __init__(self, ixx=0.0, ixy=0.0, ixz=0.0, iyy=0.0, iyz=0.0, izz=0.0):
		self.ixx = ixx
		self.ixy = ixy
		self.ixz = ixz
		self.iyy = iyy
		self.iyz = iyz
		self.izz = izz
	
	def to_matrix(self):
		return [
			[self.ixx, self.ixy, self.ixz],
			[self.ixy, self.iyy, self.iyz],
			[self.ixz, self.iyz, self.izz]]

reflect(Inertia, params = [Attribute(key, float) for key in Inertia.KEYS])


class Inertial(Object):
	def __init__(self, mass = 0.0, inertia = None, origin=None):
		self.mass = mass
		self.inertia = inertia
		self.origin = origin

reflect(Inertial, params = [
	origin_element,
	Element('mass', 'element_value'),
	Element('inertia', Inertia, False)
	])



#FIXME: we are missing the reference position here.
class JointCalibration(Object):
	def __init__(self, rising=None, falling=None):
		self.rising = rising
		self.falling = falling

reflect(JointCalibration, params = [
	Attribute('rising', float),
	Attribute('falling', float)
	])

class JointLimit(Object):
	def __init__(self, effort=None, velocity=None, lower=None, upper=None):
		self.effort = effort
		self.velocity = velocity
		self.lower = lower
		self.upper = upper

reflect(JointLimit, params = [
	Attribute('effort', float),
	Attribute('lower', float, False, 0),
	Attribute('upper', float, False, 0),
	Attribute('velocity', float)
	])

#FIXME: we are missing __str__ here.
class JointMimic(Object):
	def __init__(self, joint_name=None, multiplier=None, offset=None):
		self.joint = joint_name
		self.multiplier = multiplier
		self.offset = offset	

reflect(JointMimic, params = [
	Attribute('joint', str),
	Attribute('multiplier', float, False),
	Attribute('offset', float, False)
	])

class SafetyController(Object):
	def __init__(self, velocity=None, position=None, lower=None, upper=None):
		self.k_velocity = velocity
		self.k_position = position
		self.soft_lower_limit = lower
		self.soft_upper_limit = upper

reflect(SafetyController, params = [
	Attribute('k_velocity', float),
	Attribute('k_position', float, False, 0),
	Attribute('soft_lower_limit', float, False, 0),
	Attribute('soft_upper_limit', float, False, 0)
	])

class Joint(Object):
	TYPES = ['unknown', 'revolute', 'continuous', 'prismatic', 'floating', 'planar', 'fixed']

	def __init__(self, name=None, parent=None, child=None, joint_type=None,
			axis=None, origin=None,
			limit=None, dynamics=None, safety_controller=None, calibration=None,
			mimic=None):
		self.name = name
		self.parent = parent
		self.child = child
		self.type = joint_type
		self.axis = axis
		self.origin = origin
		self.limit = limit
		self.dynamics = dynamics
		self.safety_controller = safety_controller
		self.calibration = calibration
		self.mimic = mimic
	
	def check_valid(self):
		assert self.type in self.TYPES, "Invalid joint type: {}".format(self.type)
	
	# Aliases
	@property
	def joint_type(self): return self.type
	@joint_type.setter
	def joint_type(self, value): self.type = value

reflect(Joint, params = [
	name_attribute,
	Attribute('type', str),
	origin_element,
	Element('axis', 'element_xyz', False),
	Element('parent', 'element_link'),
	Element('child', 'element_link'),
	Element('limit', JointLimit, False),
	Element('dynamics', JointDynamics, False),
	Element('safety_controller', SafetyController, False),
	Element('calibration', JointCalibration, False),
	Element('mimic', JointMimic, False)
	])


class Link(Object):
	def __init__(self, name=None, visual=None, inertial=None, collision=None, origin = None):
		self.name = name
		self.visual = visual
		self.inertial = inertial
		self.collision = collision
		self.origin = origin

reflect(Link, params = [
	name_attribute,
	origin_element,
	Element('inertial', Inertial, False),
	Element('visual', Visual, False),
	Element('collision', Collision, False)
	])


class PR2Transmission(Object):
	def __init__(self, name = None, joint = None, actuator = None, type = None, mechanicalReduction = 1):
		self.name = name
		self.type = type
		self.joint = joint
		self.actuator = actuator
		self.mechanicalReduction = mechanicalReduction

reflect(PR2Transmission, tag = 'pr2_transmission', params = [
	name_attribute,
	Attribute('type', str),
	Element('joint', 'element_name'),
	Element('actuator', 'element_name'),
	Element('mechanicalReduction', float)
	])


class Actuator(Object):
	def __init__(self, name = None, hardwareInterface = None, mechanicalReduction = 1):
		self.name = name
		self.hardwareInterface = None
		self.mechanicalReduction = None

reflect(Actuator, tag = 'actuator', params = [
		name_attribute,
		Element('hardwareInterface', str),
		Element('mechanicalReduction', float, required = False)
		])

class Transmission(Object):
	""" New format: http://wiki.ros.org/urdf/XML/Transmission """
	def __init__(self, name = None, joint = None, actuator = None):
		self.name = name
		self.joint = joint
		self.actuator = actuator

reflect(Transmission, tag = 'new_transmission', params = [
		name_attribute,
		Element('type', str),
		Element('joint', 'element_name'),
		Element('actuator', Actuator)
		])

add_type('transmission', DuckTypedFactory('transmission', [Transmission, PR2Transmission]))

class Robot(Object):
	def __init__(self, name = None):
		self.aggregate_init()
		
		self.name = name
		self.joints = []
		self.links = []
		self.materials = []
		self.gazebos = []
		self.transmissions = []
		
		self.joint_map = {}
		self.link_map = {}

		self.parent_map = {}
		self.child_map = {}
	
	def add_aggregate(self, typeName, elem):
		Object.add_aggregate(self, typeName, elem)
		
		if typeName == 'joint':
			joint = elem
			self.joint_map[joint.name] = joint
			self.parent_map[ joint.child ] = (joint.name, joint.parent)
			if joint.parent in self.child_map:
				self.child_map[joint.parent].append( (joint.name, joint.child) )
			else:
				self.child_map[joint.parent] = [ (joint.name, joint.child) ]
		elif typeName == 'link':
			link = elem
			self.link_map[link.name] = link

	def add_link(self, link):
		self.add_aggregate('link', link)

	def add_joint(self, joint):
		self.add_aggregate('joint', joint)

	def get_chain(self, root, tip, joints=True, links=True, fixed=True):
		chain = []
		if links:
			chain.append(tip)
		link = tip
		while link != root:
			(joint, parent) = self.parent_map[link]
			if joints:
				if fixed or self.joint_map[joint].joint_type != 'fixed':
					chain.append(joint)
			if links:
				chain.append(parent)
			link = parent
		chain.reverse()
		return chain

	def get_root(self):
		root = None
		for link in self.link_map:
			if link not in self.parent_map:
				assert root is None, "Multiple roots detected, invalid URDF."
				root = link
		assert root is not None, "No roots detected, invalid URDF."
		return root

	@classmethod
	def load_from_parameter_server(cls, key = 'robot_description'):
		"""
		Retrieve the robot model on the parameter server
		and parse it to create a URDF robot structure.

		Warning: this requires roscore to be running.
		"""
		# Could move this into xml_reflection
		import rospy
		return cls.from_xml_string(rospy.get_param(key))
	@classmethod
	def load_from_string(cls, xstring):
		return cls.from_xml_string(xstring)
	@classmethod
	def load_from_file(cls, filename):
		return cls.load_from_string(open(filename).read())
	
reflect(Robot, tag = 'robot', params = [
# 	name_attribute,
	Attribute('name', str, False), # Is 'name' a required attribute?
	AggregateElement('link', Link),
	AggregateElement('joint', Joint),
	AggregateElement('gazebo', RawType()),
 	AggregateElement('transmission', 'transmission'),
	AggregateElement('material', Material)
	])

# Make an alias
URDF = Robot

end_namespace()

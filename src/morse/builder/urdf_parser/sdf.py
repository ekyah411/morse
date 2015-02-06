#from morse.builder.urdf_parser.xml_reflection.basics import *
#from morse.builder.urdf_parser.xml_reflection.core import *

## What is the scope of plugins? Model, World, Sensor?

#start_namespace('sdf')

#class Pose(Object):
	#def __init__(self, vec=None, extra=None):
		#self.xyz = None
		#self.rpy = None
		#if vec is not None:
			#assert isinstance(vec, list)
			#count = len(vec)
			#if len == 3:
				#xyz = vec
			#else:
				#self.from_vec(vec)
		#elif extra is not None:
			#assert xyz is None, "Cannot specify 6-length vector and 3-length vector"
			#assert len(extra) == 3, "Invalid length"
			#self.rpy = extra
	
	#def from_vec(self, vec):
		#assert len(vec) == 6, "Invalid length"
		#self.xyz = vec[:3]
		#self.rpy = vec[3:6]
	
	#def as_vec(self):
		#xyz = self.xyz if self.xyz else [0, 0, 0]
		#rpy = self.rpy if self.rpy else [0, 0, 0]
		#return xyz + rpy
	
	#def read_xml(self, node):
		## Better way to do this? Define type?
		#vec = get_type('vector6').read_xml(node)
		#self.load_vec(vec)
	
	#def write_xml(self, node):
		#vec = self.as_vec()
		#get_type('vector6').write_xml(node, vec)
	
	#def check_valid(self):
		#assert self.xyz is not None or self.rpy is not None

#name_attribute = Attribute('name', str)
#pose_element = Element('pose', Pose, False)

#class Entity(Object):
	#def __init__(self, name = None, pose = None):
		#self.name = name
		#self.pose = pose

#reflect(Entity, params = [
	#name_attribute,
	#pose_element
	#])


#class Inertia(Object):
	#KEYS = ['ixx', 'ixy', 'ixz', 'iyy', 'iyz', 'izz']
	
	#def __init__(self, ixx=0.0, ixy=0.0, ixz=0.0, iyy=0.0, iyz=0.0, izz=0.0):
		#self.ixx = ixx
		#self.ixy = ixy
		#self.ixz = ixz
		#self.iyy = iyy
		#self.iyz = iyz
		#self.izz = izz
	
	#def to_matrix(self):
		#return [
			#[self.ixx, self.ixy, self.ixz],
			#[self.ixy, self.iyy, self.iyz],
			#[self.ixz, self.iyz, self.izz]]

#reflect(Inertia, params = [Element(key, float) for key in Inertia.KEYS])

## Pretty much copy-paste... Better method?
## Use multiple inheritance to separate the objects out so they are unique?
#class Inertial(Object):
	#def __init__(self, mass = 0.0, inertia = None, pose=None):
		#self.mass = mass
		#self.inertia = inertia
		#self.pose = pose

#reflect(Inertial, params = [
	#Element('mass', float),
	#Element('inertia', Inertia),
	#pose_element
	#])


#class Link(Entity):
	#def __init__(self, name = None, pose = None, inertial = None, kinematic = False):
		#Entity.__init__(self, name, pose)
		#self.inertial = inertial
		#self.kinematic = kinematic

#reflect(Link, parent_cls = Entity, params = [
	#Element('inertial', Inertial),
	#Attribute('kinematic', bool, False),
	#AggregateElement('visual', Visual, var = 'visuals'),
	#AggregateElement('collision', Collision, var = 'collisions')
	#])


#class Model(Entity):
	#def __init__(self, name = None, pose=None):
		#Entity.__init__(self, name, pose)
		#self.links = []
		#self.joints = []
		#self.plugins = []

#reflect(Model, parent_cls = Entity, params = [
	#AggregateElement('link', Link, var = 'links'),
	#AggregateElement('joint', Joint, var = 'joints'),
	#AggregateElement('plugin', Plugin, var = 'plugins')
	#])

#end_namespace('sdf')

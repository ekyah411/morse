import rospkg

class PathRetriever:
	def __init__(self, rel_filepath):
		self.path = None
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
			self.path = package_path + remain

		else:
			print('The path ' + rel_filepath + ' can\'t be handled')
			self.path = rel_filepath

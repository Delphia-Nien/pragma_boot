import os
import pragma.commands
import pragma.drivers


class Command(pragma.commands.Command):
	"""
	Shuts down a virtual cluster but does not unallocate resources.

	<arg type='string' name='vc-name'>
	The name of the cluster which should be shutdown.
	</arg>

	<example cmd='shutdown myPragmaCluster'>
	Will shutdown the virtual cluster named myPragmaCluster.
	</example>
	"""

	def run(self, params, args):

		(args, vcname) = self.fillPositionalArgs(('vc-name'))

		if not vcname:
			self.abort('must supply a name for the virtual cluster')

		# Read in site configuration file and imports values:
		#   site_ve_driver, temp_directory,
		#   repository_class, repository_dir, repository_settings
		execfile(self.siteconf, {}, globals())

		# load driver
		driver = pragma.drivers.Driver.factory(site_ve_driver, self.basepath)
		if not driver:
			self.abort("Uknown driver %s" % site_ve_driver)

		#print "Shutting down virtual cluster %s" % vcname
		if driver.shutdown(vcname):
			print "\nCluster %s successfully shutdown" % vcname


RollName = "pragma_boot"

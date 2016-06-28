from datetime import datetime
import logging
import pragma.commands
import pragma.drivers
import os

class Command(pragma.commands.Command):
	"""
	Boot a virtual cluster using configured VM provisioning tool (see
	examples).

	<arg type='string' name='vc-name'>
	The name of the cluster which should be started.
	</arg>

	<arg type='string' name='num-cpus'>
	The nuber of CPUs requested to start up (default is 0 only frontend will
	be started)
	</arg>

	<param type='boolean' name='enable-ent'>
	Configure virtual cluster nodes on PRAGMA-ENT.
	</param>

	<param type='string' name='enable-ipop-client'>
	Start up the IPOP-enabled virtual cluster as an IPOP
	client (to another virtual cluster) using the provided
	IPOP server info file
	</param>

	<param type='string' name='enable-ipop-server'>
	Start up the IPOP-enabled virtual cluster with the
	frontend serving as an IPOP server; once
	initialization is complete, store the IPOP server info
	into the provided URL.  If begins with file://, will
	be stored locally, otherwise will be a REST call if
	begins with http://
	</param>

	<param type='string' name='logfile'>
	Print log commands to file at path instead of stdout.
	</param>

	<param type='string' name='loglevel'>
	Specify level of log messages (default: ERROR)
	</param>

	<param type='string' name='key'>
	The ssh key that will be authorized on the frontend of the cluster 
	(default is /root/.ssh/id_rsa.pub).
	</param>

	<example cmd='boot myPragmaCluster 8'>
	Will create a virtual cluster named myPragmaCluster with one or more
	compute nodes adding up to 8 CPUs.
	</example>
	"""

	def makeLog(self, logdir, name):
		if not os.path.isdir(logdir):
			os.makedirs(logdir)
		
		# default logfile name = logdir + name + timestamp
		timestamp = datetime.today().strftime("%Y%m%d-%H:%M")
		return "%s/%s-%s.log" % (logdir, name, timestamp)

	def run(self, params, args):

		(args, vcname, num_cpus) = self.fillPositionalArgs(
			('vc-name', 'num-cpus'))

		if not vcname:
			self.abort('must supply a name for the virtual cluster')
		if not num_cpus:
			self.abort('must supply the number of CPUs')

		try:
			num_cpus = int(num_cpus)
		except:
			self.abort('num-cpus must be an integer')

		# fillParams with the above default values
		(ent, ipop_clientinfo_file, ipop_serverinfo_url,
			key, logfile, loglevel, memory) = self.fillParams(
			[
			 ('enable-ent', "false"),
			 ('enable-ipop-client', ""),
			 ('enable-ipop-server', ""),
			 ('key', os.path.expanduser('~/.ssh/id_rsa.pub')),
			 ('logfile', None),
			 ('loglevel', 'ERROR'),
			 ('memory', None)
			])

		if ipop_serverinfo_url != "" or ipop_clientinfo_file != "":
			self.abort("IPOP features not yet supported")
		enable_ent = ent.lower() in ("yes", "true", "t", "1")

		# Read site configuration file, imports values:
		#   site_ve_driver, temp_directory, log_directory
		# chekc if the values exists.
		execfile(self.siteconf, {}, globals())
		try:
			log_directory
		except NameError:
			self.abort('Missing setting log_directory in configuration file %s ' % self.siteconf)
		try:
			temp_directory
		except NameError:
			self.abort('Missing setting temp_directory in configuration file %s ' % self.siteconf)
		try:
			site_ve_driver
		except NameError:
			self.abort('Missing setting site_ve_driver in configuration file %s ' % self.siteconf)

		# create logger
		if logfile == None:
			logfile = self.makeLog(log_directory, vcname)
		logging.basicConfig(filename=logfile,
			format='%(asctime)s %(levelname)s %(message)s',
			level=getattr(logging,loglevel.upper()))
		logger = logging.getLogger('pragma_boot')

		# check if temp directory exists 
		if not os.path.isdir(temp_directory):
			self.abort('VM images staging directory %s does not exist' % temp_directory)

		# load driver
		driver = self.importDriver(site_ve_driver)
		if driver == None:
			self.abort( "Unknown driver %s. Check configuration file setting for site_ve_driver." % site_ve_driver )

		# initialize repostiroy 
		repository = self.getRepository()

		# initialize output xml object
		repository.createXmlOutputObject(temp_directory)

		# parse virtual image xml file to get all the info
                repository.createXmlInputObject(vcname)

		# Download virtual image to cache
		repository.processImage(vcname)

		#FIXME rm this line
		# and update allocate and deploy calls with new vc_in and vc_out  changes
		self.abort("Exiting DEBUG") 

		# We call allocate 
		#if not( driver.allocate(
		#	num_cpus, memory, key, enable_ent, vc_in, vc_out, repository)):
		#	self.abort("Unable to allocate virtual cluster")

		driver.deploy(vc_in, vc_out, our_temp_dir)

		# cleanup
		#vc_out.clean()
		#os.rmdir(our_temp_dir)


RollName = "pragma_boot"


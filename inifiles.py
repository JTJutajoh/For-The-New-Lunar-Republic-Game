import ConfigParser
import os

def generateini(cfg, inifilename, values):
	f = file(inifilename, 'w')
	f.write("") # Clear the file just in case
	f.close()
	# Create the sections first
	for section in values.iterkeys():
		cfg.add_section(section)
	# Now create the actual values
	for section in values.iterkeys():
		for value in values[section].iterkeys():
			cfg.set(str(section), str(value), str(values[section][value]))
	
	cfg.write(file(inifilename, 'w'))

def main(values={}, defaults={}, inifilename='default.ini'):
	cfg = ConfigParser.SafeConfigParser(defaults)
	if not os.path.exists(inifilename):
		generateini(cfg, inifilename, values)
	try:
		cfg.read(inifilename) # Try to read the ini file
	except ConfigParser.MissingSectionHeaderError, IOError:
		# No ini file exists, make a new one.
		generateini(cfg, inifilename, values)
	else:
		# An ini file exists, now check if it has anything in it.
		# First, check if the file is void of all data:
		inifiler = file(inifilename, 'r')
		if inifiler.read() == "":
			generateini(cfg, inifilename, values)
	
	# Ini file is verified. Now read it to make sure the data within is correct
	cfg = read(inifilename, defaults)
	
	modified = False
	
	# First, check the sections. Make sure that all of the proper sections are in place
	for section in values.iterkeys():
		if not section in cfg.sections():
			cfg.add_section(section)
			# Now write the values defined at the top of this file
			for s in values.iterkeys():
				for value in values[s].iterkeys():
					cfg.set(str(s), str(value), str(values[s][value]))
			modified = True
					
	for section in values.iterkeys():
		for option in values[section].iterkeys():
			if not option in cfg.options(section):
				cfg.set(str(section), str(option), str(values[section][option]))
				modified = True
			
	# If something was changed or fixed, re-write it to the file to permanently fix it.
	# Otherwise, don't bother and just continue on and conserve memory.
	if modified:
		cfg.write(file(inifilename, 'w'))
	# Ini file is approved and ready to go, reading the file and returning it.
	return cfg
			
def read(inifilename, defaults):
	cfg = ConfigParser.SafeConfigParser(defaults)
	cfg.read(inifilename)
	return cfg
	
if __name__ == '__main__': main()
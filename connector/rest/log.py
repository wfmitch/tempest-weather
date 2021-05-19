class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def warning(s):
	print(bcolors.WARNING + "Warning: " + str(s) + bcolors.ENDC)

def error(s):
	print(bcolors.FAIL + "Error: " + str(s) + bcolors.ENDC)

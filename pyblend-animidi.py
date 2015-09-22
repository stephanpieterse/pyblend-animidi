from main import *
import sys, getopt
import os.path

__author__ = "Stephan Pieterse"
# TODO can i just be consistent in naming anything please


def main(argv):
    program_version = "0.2"
    help_message = """
    pyblend-animidi.py
    Stephan Pieterse

    This is a python script that creates a script to be used in Blender, to map predefined data to object animations.

    -h Shows this help message.
    -V Shows current script version.
    -c Specify a config file to be used. Default is config.yml in the same directory as this script.

    Multiple config files can be parsed, each specified by -c.
    Example:
    pyblend-animidi.py -c config1.yml -c config2.yml

    This script is still in test phase. Thanks for using!
"""

    try:
        opts,args = getopt.getopt(argv,"hVc:")
    except getopt.GetoptError:
        print "Use -h to get help"
        sys.exit(2)

    configfile = []

    for opt, arg in opts:
        if opt == '-h':
            print(help_message)
            sys.exit()
        if opt == '-V':
            print("pyblend-animidi Version {}".format(program_version))
            sys.exit()
        if opt == '-c':
            configfile.append(arg)

    if len(configfile) == 0:
        configfile.append("config.yml")

    for config in configfile:
        is_file = os.path.isfile(config)

        if is_file:
            print("Currently running for {} ...".format(config))
            genScript = animidi(config)
            genScript.main()
        else:
            print("Specified config file {} could not be found, or is not a file. Please check your spelling and try again!".format(config))


if __name__ == "__main__":
    main(sys.argv[1:])
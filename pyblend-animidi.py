from main import *
import sys
import getopt
import os.path

"""
 Copyright (C) 2015 Stephan Pieterse

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Stephan Pieterse"
# TODO can i just be consistent in naming anything please


def main(argv):
    program_version = "1"
    help_message = """
    pyblend-animidi.py
    Copyright (C) 2015 Stephan Pieterse

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    This is a python script that creates a script to be used in Blender, to map predefined data to object animations.

    -h Shows this help message and exits.
    -V Shows current script version and exits.
    -c Specify a config file to be used. Default is config.yml in the same directory as this script.

    Multiple config files can be parsed, each specified by -c.
    Example:
    pyblend-animidi.py -c config1.yml -c config2.yml
"""

    try:
        opts,args = getopt.getopt(argv,"hVc:")
    except getopt.GetoptError:
        print("Use -h to get help")
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
            gen_script = animidi(config)
            gen_script.main()
        else:
            print("Specified config file {} could not be found, or is not a file."
                  " Please check your spelling and try again!".format(config))


if __name__ == "__main__":
    main(sys.argv[1:])

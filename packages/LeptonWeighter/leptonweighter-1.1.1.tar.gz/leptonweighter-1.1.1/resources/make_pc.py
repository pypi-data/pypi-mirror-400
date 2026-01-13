import os 
import pkgconfig
import argparse
import warnings

parser=argparse.ArgumentParser(description="Create .pc file")
parser.add_argument("module",metavar="module",type=str, nargs=1, help="module for which to create a pc file")
parser.add_argument("libraryname", metavar="libraryname", type=str, nargs=1,
                    default=None, help="What's the equivalent c library, eg 'hdf5'?")
args    = parser.parse_args()
module  = args.module
library = args.libraryname

print("Preparing to create pkgconfig file for {}".format(module))


import importlib
if isinstance(module,list):
    module = module[0]
if isinstance(library,list):
    library= library[0]

module_obj = importlib.import_module(module)

try:
    name    = module_obj.__name__
except AttributeError:
    name    = module
    warnings.warn("WARNING: Name not found, setting it to {}".format(module))

try:
    desc    = " ".join(list(filter(lambda x: x!="", module_obj.__doc__.split("\n") )) )
except AttributeError:
    warnings.warn("WARNING: Description not found, leaving blank.")
    desc    = ""

try:
    pathto  = module_obj.__file__
    pathto  = pathto.split("lib")[0]
except AttributeError:
    warnings.warn("WARNING: Path not found, setting to /usr/")
    pathto  = "/usr"

try:
    version = module_obj.__version__
except AttributeError:
    warnings.warn("WARNING: Version number not found, setting to 1.0")
    version = "1.0.0"

if library is None:
    warnings.warn("WARNING: Guessing the library linking name!")

file_dir = "./"
found = False
try: 
    env_var = os.environ['PKG_CONFIG_LIBDIR']
    found = True
except KeyError:
    print("Couldn't find 'PKG_CONFIG_LIBDIR', let's try 'PKG_CONFIG_PATH'")
    try: 
        env_var = os.environ['PKG_CONFIG_PATH']
        found=True
    except KeyError:
        warnings.warn("WARNING: Couldn't identify any pkgconfig repository. Writing .pc right here './'")
if found:
    for path in env_var.split(":"):
        if os.path.isdir( path ):
            try:
                file_object = open(path+"/{}.pc".format(library), 'wt')
                print("Writing pc file to {}/{}.pc".format(path,library))
                break
            except OSError:
                continue
else:
    file_object = open("./{}.pc".format(library), 'wt')


# get the path to the environmental variables


file_object.write("prefix={}\r\n".format(pathto))
file_object.write("\r\n")
file_object.write("libdir=${prefix}/lib\r\n")
file_object.write("includedir=${prefix}/include\r\n")
file_object.write("\r\n")
file_object.write("Name: {}\r\n".format(name))
file_object.write("Description: {}\r\n".format(desc))
file_object.write("URL: http:www.google.com\r\n")
file_object.write("Version: {}\r\n".format(version))
file_object.write("Requres: \r\n")
if library is not None:
    file_object.write("Libs: -L${{libdir}} -l{}\r\n".format(library))
else:
    file_object.write("Libs: -L${{libdir}} -l{}\r\n".format(name))
file_object.write("Cflags: -I${includedir}\r\n")
file_object.close()

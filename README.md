# Imgtool JPEG Photo tool#

Renames, reorients, resizes and/or timestamps jpg files with a unique
name based on camera model and taken date stored in the exif header. By
default imgtool updates the atime/mtime timestamps on a file to match
the exif header data.

## Usage

`imgtool [-h] [-R] [-c] [-d] [-f FORMAT] [-p Pattern] [-r] [-z GEOMETRY] [--help-geometry] [-v] [-V] [PATH [PATH ...]]`

## Program Options  ##

**-h|--help** - *Show help text*

**--help-geometry** - *Show help on resize geometry*

**-R|--recurse** - *Recurse into subdirectories*

**-c|--camera-names** - *Use embedded EXIF camera name to rename files.*

**-d|--dry-run** - *Show all actions to be performed without doing them. Also sets* **-v|--verbose**

**-f|--format** - *Time format string for filenaming in Python strftime format. Default is `’%Y%m%d%H%M%S'`*

**-p|--patern** - *Glob format pattern to search for files, e.g., *.jpg, default is *.[Jj][Pp][Gg] (see glob(3) and fnmatch(3))*

**-r|--auto-rotate** - *Automatically rotate image(s) based on EXIF Orientation tag. If not present, or set to 1 no rotation is performed*

**-z|--resize** - *Resize image(s) based on geometry. (See below)*

**-v|--verbose** - *Set verbose mode: Show operations as they are performed. If -d|--dry-run is also set, operations are shown without actually doing them.*

**-V|--version** - *Show program version and exit.*

## GEOMETRY

When using the -z or --resize option, a geometry must be specified. Geometry can be specified as a percentage of the overall image or as a pair of width:height.  Width and height are specified in pixels. If width is specified but no height, e.g., 1000: the image will be reized to a width of 1000px with a height calculated in relation to width to maintain the image aspect ratio. Conversely, height is specified without a width, e.g., :1000 will resize the image to 1000px high with a width calculated to maintain the aspect ratio.  When the width and height are spcecified no attempt to maintain the aspect ratio is made.


## WARNING

This tool is ALPHA. I have tested it in a limited environment and was
written to work with my photographs. It may even be destructive.
Backing up data is always a good idea before employing automatic tools
that can recurse directories. If you break something, you own the
remaining pieces.

## Author

Nicole Stevens (https://github.com/nicciniamh)

## Copyright

Copyright 2018 Nicole Stevens

## License

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

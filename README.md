# imgtool  Imgtool - JPEG Photo tool

## Descrtiption 

imgtool is a tool for dating, renaming, organizing, resizing, rotating
and thumbnailing images based on the information stored in their EXIF
header. This is to aid in the processing and organizing of digital
photography images.

## Background

With a fairly large collection of digital photos I have taken with my
phone and three different Nikon cameras.

In an effort to have unqique file names, I wrote this tool. I also added
the functionality of a couple other operations I frequently do in post-
processing.

A number of graphics tools will honor the Orientation tag in an image,
however, on occasion, I find I need to manually rotate an image. More
commonly, images get resized and renamed. Sometimes other tools are
employed which modify the timestamp of the file, on the files system,
which can disrupt sorting. (I use a date descending order in my file
manager to show me the most recent photos) The default operation of
imgtool is to set the timestamp of the files it finds with the date
stamp in the photo's EXIF header.

Files can be moved (or copied if to a different device) to another
directory. The naming can have embedded exif data just like the format
option. This would allow creation of a directory structure based on
image data. E.g., `~/Photos/#Y-#m-#d .` will create a tree of
directories based on the EXIF (or file) Date/Time. Any subdirectory
trees are maintained.

*If an output directory is specified, and, no other renaming is done,
for operations such as dating or resizing, the file is **copied** to
the output directory instead of renaming.*

## Digital Photography Images

Files created by digital photography have a header built-in called
*Exhangeabe Image Format* or EXIF (https://en.wikipedia.org/wiki/Exif)
header. There is a lot of information that can be in this header that
relates to the photograph, when it was taken, sometimes where it was
taken, camera settings, camera model, etc. This tool extracts this
information and uses it to create unique names for photography files,
rotate them, etc.

- [Usage](#usage)
    - [Program Options](#program-options)
- [Geometry](#geometry)
- [Thumbnails](#thumbnails)
    - [Creating thumbnails from image](#creating-thumbnails-from-image)
    - [Creating thumbnails from EXIF data](#creating-thumbnails-from-exif-data)
- [Order of operations](#order-of-operations)
- [Setting Options](#setting-options)
    - [ignore-processed](#ignore-processed)
    - [set-processed](#set-processed)
    - [ignore-no-exif](#ignore-no-exif)
- [Automatic Image Naming](#automatic-image-naming)
    - [Splitting strings in tags](#splitting-strings-in-tags)
- [Some tips](#some-tips)
- [Installation](#installation)
- [Pre-requisites](#pre-requisites)
    - [Running the installer script:](#running-the-installer-script:)
- [Issues](#issues)
- [WARNING](#warning)
- [Author](#author)
- [Copyright](#copyright)
- [License](#license)
- [About this Document](#about-this-document)

## Usage

```
usage: imgtool [-h] [-a ROTANGLE] [-R] [-c] [-D] [-d directory] [-e]
               [--exif-rotate-thumb] [-f format-string] [-n] [-p Pattern]
               [-q REQUIRED_TAG] [-r] [-t] [-s SET] [--thumb-dir directory]
               [--thumb-geometry geometry] [-v] [-V] [-z geometry] [--debug]
               [--dumpkeys] [--help-geometry] [--help-format] [--help-options]
               [---dumpargs]
               [PATH [PATH ...]]
```
### Program Options

#### rotation-angle
-a ROTANGLE, --rotation-angle ROTANGLE


#### camera-names
-c, --camera-names Rename pictures that have an embedded camera name to


#### output-directory
-d directory, --output-directory directory


#### dry_run
-D, --dry_run Dry run: show what will be done without actually doing


#### debug
--debug Enable debugging messages


#### -dumpargs
---dumpargs Pyton Pickle formatted dump of program arguments


#### dumpkeys
--dumpkeys Dump all exif tag keys for first file and exit.


#### exif-extract-thumb
-e, --exif-extract-thumb


#### exif-rotate-thumb
--exif-rotate-thumb Rotate EXIF thumnail(s) by EXIF orientation or by


#### format
-f format-string, --format format-string


#### no-clobber
-n, --no-clobber Do not overwrite existing files. Files will be named


#### pattern
-p Pattern, --pattern Pattern


#### required-tag
-q REQUIRED_TAG, --required-tag REQUIRED_TAG


#### auto-rotate
-r, --auto-rotate Automatically rotate images.


#### recurse
-R, --recurse Recurse into sub-directories


#### thumb-dir
--thumb-dir directory


#### thumb-dir
--thumb-dir to override output directory.


#### thumb-geometry
--thumb-geometry geometry


#### thumb-geometry
--thumb-geometry to override default of 96x96, use


#### thumbnail
-t, --thumbnail Generate thumbnails in the same output path. Use


#### verbose
-v, --verbose Describe what is being done.


#### version
-V, --version Show version information and exit.


#### resize
-z geometry, --resize geometry


## Geometry

Geometry can be specified as a percentage of the overall image or as a
pair of width:height.  Width and height are specified in pixels. If
width is specified but no height, e.g., 1000: the image will be reized
to a width of 1000px with a height calculated in relation to width to
maintain the image aspect ratio. Conversely, height is specified without
a width, e.g., :1000 will resize the image to 1000px high with a width
calculated to maintain the aspect ratio.  When the width and height are
spcecified no attempt to maintain the aspect ratio is made.

## Thumbnails
Thumbnails may be created or extracted from the EXIF data, when present. 

### Creating thumbnails from image
When generating thumbnails from image data, they are written to the 
diretory specified with the --thumb-dir option or to the same path
where the file is ultimately written using the pattern 
filename-thumb.png.

### Creating thumbnails from EXIF data
Thumbnails are often stored in the images EXIF header. These files are 
written with the same rule for paths of thumbnails above, but, they are
written as JPEG images. Unless --exif-rotate-thumb is set, the thubnail
is not rotated. If -a or --rotation-angle is set then that angle is used
to rotate images otherwise the Exif.Image.Orientation data is used and 
if appropriate the thumbnail will be rotated.

## Order of operations
Each image processed, if the operations are specified, has their operations
peformed in this order:
1. Image resize
2. Auto-rotation
3. Dating and/or Renaming
4. Thumbnail generation

## Setting Options
Setting options with -s or --set changes some program operations.
Each option can be toggled. The format of these options are:
>option-key[:option-key...]

Current options are:

### ignore-processed
    Ignore files already processed by imgtool. Default is to ignore.

### set-processed
    Set the processed flag in the image header. Default is to set the flag.

### ignore-no-exif
    Ignore files without an EXIF header. Default is to process.

## Automatic Image Naming

Formatting filenames for automatic renaming is as follows:
    [@+]type.Tag#timefmt

Tags starting with @ have their spaces replaced with periods (.), Tags
starting with + do not have spaces replaced. There are two types of tags, File
and Exif. File Tags are:

    File.Name:  Filename of the image without extension
    File.Ext:   Extension of filename, e.g., .JPG 
    File.ext:   Extension of filename converted to lower-case, e.g., .jpg
    File.Fullname: Full name of file with directories.
    File.mtime: String representation YYYYMMDDhhmmss of the file's timestamp in
    the filesystem.


EXIF Tags vary by image and camera. The program exiftool may be useful in
finding appropriate tags. When specifying EXIF Tags, they are formatted as
Exif.Image.Model which results in a string, for one of my cameras, as 
'NIKON D3400',by default the resultant string will have spaced replaced with
periods (.), to suppress this behavior, precede them with a plus (+). E.g.:

    @Exif.Image.Make returns 'NIKON.D3400' where +Exif.Image.Make 
    returns 'NIKON D3400' 

This conversion is done just before substituting the tag with its value. 

### Splitting strings in tags
Splitting the tag values can be done as an index of space separated words 
or as asubstring. 

#### Indexing
To use an index, 
place the index number in brackets, e.g, @Exif.Image.Make[1] returns 'D3400'
instead of 'NIKON D3400'. Index values start with 0. 

#### Substrings
To use a substring, place the start and, optionally the length in parentheses.
E.g,: @Exif.Image.Make(7,5) will return 'D3400' instead of 'NIKON D3400'. If
the second value is omitted the length of the value, starting at the first 
number is presumed, so @Exif.Image.Make(7) will also result with 'D3400'

Any EXIF Tag present in the image EXIF header can be used to create all or part
of a file name. For example, `@Image.Make[1]_@File.name@File.ext will create,
from DSC_328.JPG a name of 'D3400_DSC_328.jpg'.`


Note that the @File tags are never evaluated with a plus instead of an at-sign,
and no indexing or substring operations are performed.

Time formatting, using the EIXF header's image time, is formatted using
strftime(3) format, or with the following formatting keys:

       #a     The abbreviated name of the day of the week according to the
              current locale.  (Calculated from tm_wday.)

       #A     The full name of the day of the week according to the current
              locale.  (Calculated from tm_wday.)

       #b     The abbreviated month name according to the current locale.
              (Calculated from tm_mon.)

       #B     The full month name according to the current locale.
              (Calculated from tm_mon.)

       #c     The preferred date and time representation for the current
              locale.

       #C     The century number (year/100) as a 2-digit integer. (SU)
              (Calculated from tm_year.)

       #d     The day of the month as a decimal number (range 01 to 31).
              (Calculated from tm_mday.)

       #D     Equivalent to #m/#d/#y.  (Yecch—for Americans only.  Americans
              should note that in other countries #d/#m/#y is rather common.
              This means that in international context this format is
              ambiguous and should not be used.) (SU)

       #e     Like #d, the day of the month as a decimal number, but a
              leading zero is replaced by a space. (SU) (Calculated from
              tm_mday.)

       #E     Modifier: use alternative format, see below. (SU)

       #F     Equivalent to #Y-#m-#d (the ISO 8601 date format). (C99)

       #G     The ISO 8601 week-based year (see NOTES) with century as a
              decimal number.  The 4-digit year corresponding to the ISO
              week number (see #V).  This has the same format and value as
              #Y, except that if the ISO week number belongs to the previous
              or next year, that year is used instead. (TZ) (Calculated from
              tm_year, tm_yday, and tm_wday.)

       #g     Like #G, but without century, that is, with a 2-digit year
              (00–99). (TZ) (Calculated from tm_year, tm_yday, and tm_wday.)

       #h     Equivalent to #b.  (SU)

       #H     The hour as a decimal number using a 24-hour clock (range 00
              to 23).  (Calculated from tm_hour.)

       #I     The hour as a decimal number using a 12-hour clock (range 01
              to 12).  (Calculated from tm_hour.)

       #j     The day of the year as a decimal number (range 001 to 366).
              (Calculated from tm_yday.)

       #k     The hour (24-hour clock) as a decimal number (range 0 to 23);
              single digits are preceded by a blank.  (See also #H.)
              (Calculated from tm_hour.)  (TZ)

       #l     The hour (12-hour clock) as a decimal number (range 1 to 12);
              single digits are preceded by a blank.  (See also #I.)
              (Calculated from tm_hour.)  (TZ)

       #m     The month as a decimal number (range 01 to 12).  (Calculated
              from tm_mon.)

       #M     The minute as a decimal number (range 00 to 59).  (Calculated
              from tm_min.)

       #n     A newline character. (SU)

       #O     Modifier: use alternative format, see below. (SU)

       #p     Either "AM" or "PM" according to the given time value, or the
              corresponding strings for the current locale.  Noon is treated
              as "PM" and midnight as "AM".  (Calculated from tm_hour.)

       #P     Like #p but in lowercase: "am" or "pm" or a corresponding
              string for the current locale.  (Calculated from tm_hour.)
              (GNU)

       #r     The time in a.m. or p.m. notation.  In the POSIX locale this
              is equivalent to #I:#M:#S #p.  (SU)

       #R     The time in 24-hour notation (#H:#M).  (SU) For a version
              including the seconds, see #T below.

       #s     The number of seconds since the Epoch, 1970-01-01 00:00:00
              +0000 (UTC). (TZ) (Calculated from mktime(tm).)

       #S     The second as a decimal number (range 00 to 60).  (The range
              is up to 60 to allow for occasional leap seconds.)
              (Calculated from tm_sec.)

       #t     A tab character. (SU)

       #T     The time in 24-hour notation (#H:#M:#S).  (SU)

       #u     The day of the week as a decimal, range 1 to 7, Monday being
              1.  See also #w.  (Calculated from tm_wday.)  (SU)

       #U     The week number of the current year as a decimal number, range
              00 to 53, starting with the first Sunday as the first day of
              week 01.  See also #V and #W.  (Calculated from tm_yday and
              tm_wday.)

       #V     The ISO 8601 week number (see NOTES) of the current year as a
              decimal number, range 01 to 53, where week 1 is the first week
              that has at least 4 days in the new year.  See also #U and #W.
              (Calculated from tm_year, tm_yday, and tm_wday.)  (SU)

       #w     The day of the week as a decimal, range 0 to 6, Sunday being
              0.  See also #u.  (Calculated from tm_wday.)

       #W     The week number of the current year as a decimal number, range
              00 to 53, starting with the first Monday as the first day of
              week 01.  (Calculated from tm_yday and tm_wday.)

       #x     The preferred date representation for the current locale
              without the time.

       #X     The preferred time representation for the current locale
              without the date.

       #y     The year as a decimal number without a century (range 00 to
              99).  (Calculated from tm_year)

       #Y     The year as a decimal number including the century.
              (Calculated from tm_year)

       #z     The +hhmm or -hhmm numeric timezone (that is, the hour and
              minute offset from UTC). (SU)

       #Z     The timezone name or abbreviation.

       #+     The date and time in date format. (TZ) (Not supported in
              glibc2.)

       ##     A literal '#' character.

       Some conversion specifications can be modified by preceding the
       conversion specifier character by the E or O modifier to indicate
       that an alternative format should be used.  If the alternative format
       or specification does not exist for the current locale, the behavior
       will be as if the unmodified conversion specification were used. (SU)
       The Single UNIX Specification mentions #Ec, #EC, #Ex, #EX, #Ey, #EY,
       #Od, #Oe, #OH, #OI, #Om, #OM, #OS, #Ou, #OU, #OV, #Ow, #OW, #Oy,
       where the effect of the O modifier is to use alternative numeric
       symbols (say, roman numerals), and that of the E modifier is to use a
       locale-dependent alternative representation.

(Taken from Linux strftime(3) manual page, from the Linux Man Pages Project,
http://www.kernel.org/doc/man-pages)
## Some tips
1. Always backup data!
2. Before emplyoing this tool on a
number of photos, be sure it will do what  you want it to do using the
-D or --dry-run option. This will tell you most  of what operations are
being done without actually doing them.
3. When using EXIF tags for renaming files from multiple camera 
make/models, do not use vendor specific tags, e.g. Exif.NikonFi.FileNumber
as these may not be consistent across those cameras even for the same
manufacturer.
## Installation

## Pre-requisites
imgtool requires the following python packages in order to work
- pyexiv2 -   https://github.com/escaped/pyexiv2
- Pillow -    (pip install pillow)

The standard modules used are:
- os  -               OS Dependent interfaces
- sys -               System interfaces
- datetime, time -    Date and time manipulation and conversions
- re -                Regular expression library
- fnmatch, glob2, shutil - File globbing, matching and copying.

This tool was developed on Linux. While untested it may work on 
OSX and Windows provided these libraries are installed.

The installer script will install the files, based on what is
in installer.json, to appropriate directories with the specified
mode. 

### Running the installer script:
```
usage: installer [-h] [--bindir program-dir] [--docdir doccument-dir]
                 [--mandir man-dir] [--libdir library-dir]
                 [--sources source-list]

optional arguments:
  -h, --help              show this help message and exit
  --bindir program-dir    Directory to store executable(s)
  --docdir doccument-dir  Directory to store document(s)
  --mandir man-dir        Directory to store manual page(s)
  --libdir library-dir    Directory to store library files(s) (Not used for this tool)
```

Running installer without arguments will install the program to 
/usr/bin, the manual page to /usr/man/man1, and this file to
/usr/share/doc/imgtool. You must have appropriate access rights, 
e.g.:, sudo, to perform this install. The installer can write to
other directories. Specifying 'none' as the deestination will prevent 
that part from being copied.

## Issues
- The documentation has some missing parts from the auto-generated 
stuff from reading the help output from imgtool. 
- Not fuly tested, but working on it. 

## WARNING

This tool is ALPHA. I have tested it in a limited environment and was
written to work with my photographs. It may even be destructive. Backing
up data is always a good idea before employing automatic tools that can
recurse directories. If you break something, you own the remaining
pieces.

## Author

Nicole Stevens [@github](https://github.com/nicciniamh)

## Copyright

Copyright 2018 Nicole Stevens

## License

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

## About this Document
This document was automatically generated using tools in the doc/ directory. Please see the [README.md](doc/README.md) 
in that directory for information and build procedures. 

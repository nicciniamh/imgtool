# Imgtool JPEG Photo tool

I have a fairly large collection of digital photos I have taken with my phone and three different Nikon cameras. 

In an effort to have unqique file names, I wrote this tool. I also added the functionality of a couple other operations I frequently do in post-processing.

A number of graphics tools will honor the Orientation tag in an image, however, on occasion, I find I need to manually rotate an image. More commonly, images get resized and renamed. Sometimes other tools are employed which modify the timestamp of the file, on the files system, which can disrupt sorting. (I use a date descending order in my file manager to show me the most recent photos) The default operation of imgtool is to set the timestamp of the files it finds with the date stamp in the photo's EXIF header. 

Files can be moved (or copied if to a different device) to another directory. The naming can have embedded exif data just like
the format option. This would allow creation of a directory structure based on image data. E.g.,
  `~/Photos/%Y-%m-%d .` will create a tree of directories based on the EXIF (or file) Date/Time. Any subdirectory trees are maintaine. 

## Table of Contents
- [Usage](#usage)
    - [-a|--rot-angle](#-a\|--rot-angle)
    - [-h|--help](#-h\|--help)
    - [--help-geometry](#--help-geometry)
    - [-R|--recurse](#-r\|--recurse)
    - [-c|--camera-names](#-c\|--camera-names)
    - [-d|--directory](#-d\|--directory)
    - [-D|--dry-run](#-d\|--dry-run)
    - [-f|--format](#-f\|--format)
    - [-i|--ignore-no-exif](#-i\|--ignore-no-exif)
    - [-n|--no-clobber](#-n\|--no-clobber)
    - [-q|--required-tag](#-q|--required-tag)
    - [-p|--patern](#-p\|--patern)
    - [-r|--auto-rotate](#-r\|--auto-rotate)
    - [-t|--thumnbail](#-t\|--thumnbail)
    - [--thumb-dir](#--thumb-dir)
    - [--thumb-geometry](#--thumb-geometry)
    - [-z|--resize](#-z\|--resize)
    - [-v|--verbose](#-v\|--verbose)
    - [-V|--version](#-v\|--version)
    - [--dumpkeys](#--dumpkeys)- [Automatic Image Naming](#automatic-image-naming)
    - [Splitting strings in tags](#splitting-strings-in-tags)
        - [Indexing](#indexing)
        - [Substrings](#substrings)
- [Geometry](#geometry)
- [Order of operations](#order-of-operations)
- [Some tips](#some-tips)
- [A Strong Warning](#warning)
- [Author](#author)
- [Copyright](#copyright)
- [License](#license)
- [Installation](#installation)

## Usage

`imgtool [-h] [-a ROTANGLE] [-R] [-c] [-D] [-d directory]
                  [-f format-string] [-i] [-n] [-p Pattern] [-q REQUIRED_TAG]
                  [-r] [-t] [--thumb-dir directory]
                  [--thumb-geometry geometry] [-v] [-V] [-z geometry]
                  [--debug] [--dumpkeys] [--help-geometry] [--help-format]
                  [PATH [PATH ...]]
`
### -a|--rot-angle
Specify angle for rotation and override EXIF data.
### -h|--help
Show help text
### --help-geometry
Show help on resize geometry
### -R|--recurse
Recurse into subdirectories
### -c|--camera-names
Use embedded EXIF camera name to rename files.
### -d|--directory
Specify output directory. Formatting with exif tags is allowed. See formatting below.
### -D|--dry-run
Show all actions to be performed without doing them. Also sets -v|--verbose
### -f|--format
Time format string for filenaming in Python strftime format. Default is `@Exif.Image.Model[1]_%Y%m%d%H%M%S@File.ext`
### -i|--ignore-no-exif
Ignore that a file has no EXIF data. Default is to skip files without EXIF data.
### -n|--no-clobber
Do not overwrite files. Files will be named as "newname (n).ext" where n is a number indicating the number of files with the new name. Similar to other file renaming operations
### -q|--required-tag
Require specific EXIF tag to be in the header for processing.
### -p|--patern
Glob format pattern to search for files, e.g., .jpg, default is .[Jj][Pp][Gg] (see glob(3) and fnmatch(3))
### -r|--auto-rotate
Automatically rotate image(s) based on EXIF Orientation tag. If not present, or set to 1 no rotation is performed
### -t|--thumnbail
Automaticall generate image thumbnails
### --thumb-dir
Specify thumbmail output directory
### --thumb-geometry
Specify thumbnail geometry as XXxYY or x%, the latter is not recommended.
### -z|--resize
Resize image(s) based on geometry. (See below)
### -v|--verbose
Set verbose mode: Show operations as they are performed. If -d|--dry-run is also set, operations are shown without actually doing them.
### -V|--version
Show program version and exit.
### --dumpkeys
Dump EXIF tag keys for first found file and exit. May be used to help with formatting.


## Program Options  ##
## Geometry

Geometry can be specified as a percentage of the overall image or as a pair of width:height.  Width and height are specified in pixels. If width is specified but no height, e.g., 1000: the image will be reized to a width of 1000px with a height calculated in relation to width to maintain the image aspect ratio. Conversely, height is specified without a width, e.g., :1000 will resize the image to 1000px high with a width calculated to maintain the aspect ratio.  When the width and height are spcecified no attempt to maintain the aspect ratio is made.

## Automatic Image Naming

Formatting filenames for automatic renaming is as follows:
    [@|+]type.Tag%timefmt

Tags starting with @ have their spaces replaced with periods (.), Tags starting with + 
do not have spaces replaced. There are two types of tags, File and Exif. File Tags are:

    File.Name:  Filename of the image without extension
    File.Ext:   Extension of filename, e.g., .JPG 
    File.ext:   Extension of filename converted to lower-case, e.g., .jpg
    File.Fullname: Full name of file with directories.
    File.mtime: String representation YYYYMMDDhhmmss of the file's timestamp in the filesystem.


EXIF Tags vary by image and camera. The program exiftool may be useful in finding appropriate tags. 
When specifying EXIF Tags, they are formatted as Exif.Image.Model which results in a string, for one 
of my cameras, as 'NIKON D3400', by default the resultant string will have spaced replaced with 
periods (.), to suppress this behavior, precede them with a plus (+). E.g.:

    @Exif.Image.Make returns 'NIKON.D3400' where +Exif.Image.Make returns 'NIKON D3400' 

This conversion is done just before substituting the tag with its value. 

### Splitting strings in tags
Splitting the tag values can be done as an index of space separated words or as a substring. 

#### Indexing
To use an index, 
place the index number in brackets, e.g, @Exif.Image.Make[1] returns 'D3400' instead of 'NIKON D3400'. 
Index values start with 0. 

#### Substrings
To use a substring, place the start and, optionally the length in parentheses. E.g,
@Exif.Image.Make(7,5) will return 'D3400' instead of 'NIKON D3400'. If the second value is omitted the 
length of the value, starting at the first number is presumed, so @Exif.Image.Make(7) will also result 
with 'D3400'

Any EXIF Tag present in the image EXIF header can be used to create all or part of a file name. For example, 
`@Image.Make[1]_@File.name@File.ext will create, from DSC_328.JPG a name of 'D3400_DSC_328.jpg'.`


Note that the @File tags are never evaluated with a plus instead of an at-sign, and no indexing or substring
operations are performed.

Time formatting, using the EIXF header's image time, is formatted with the following formatting:
       %a     The abbreviated name of the day of the week according to the
              current locale.  (Calculated from tm_wday.)

       %A     The full name of the day of the week according to the current
              locale.  (Calculated from tm_wday.)

       %b     The abbreviated month name according to the current locale.
              (Calculated from tm_mon.)

       %B     The full month name according to the current locale.
              (Calculated from tm_mon.)

       %c     The preferred date and time representation for the current
              locale.

       %C     The century number (year/100) as a 2-digit integer. (SU)
              (Calculated from tm_year.)

       %d     The day of the month as a decimal number (range 01 to 31).
              (Calculated from tm_mday.)

       %D     Equivalent to %m/%d/%y.  (Yecch—for Americans only.  Americans
              should note that in other countries %d/%m/%y is rather common.
              This means that in international context this format is
              ambiguous and should not be used.) (SU)

       %e     Like %d, the day of the month as a decimal number, but a
              leading zero is replaced by a space. (SU) (Calculated from
              tm_mday.)

       %E     Modifier: use alternative format, see below. (SU)

       %F     Equivalent to %Y-%m-%d (the ISO 8601 date format). (C99)

       %G     The ISO 8601 week-based year (see NOTES) with century as a
              decimal number.  The 4-digit year corresponding to the ISO
              week number (see %V).  This has the same format and value as
              %Y, except that if the ISO week number belongs to the previous
              or next year, that year is used instead. (TZ) (Calculated from
              tm_year, tm_yday, and tm_wday.)

       %g     Like %G, but without century, that is, with a 2-digit year
              (00–99). (TZ) (Calculated from tm_year, tm_yday, and tm_wday.)

       %h     Equivalent to %b.  (SU)

       %H     The hour as a decimal number using a 24-hour clock (range 00
              to 23).  (Calculated from tm_hour.)

       %I     The hour as a decimal number using a 12-hour clock (range 01
              to 12).  (Calculated from tm_hour.)

       %j     The day of the year as a decimal number (range 001 to 366).
              (Calculated from tm_yday.)

       %k     The hour (24-hour clock) as a decimal number (range 0 to 23);
              single digits are preceded by a blank.  (See also %H.)
              (Calculated from tm_hour.)  (TZ)

       %l     The hour (12-hour clock) as a decimal number (range 1 to 12);
              single digits are preceded by a blank.  (See also %I.)
              (Calculated from tm_hour.)  (TZ)

       %m     The month as a decimal number (range 01 to 12).  (Calculated
              from tm_mon.)

       %M     The minute as a decimal number (range 00 to 59).  (Calculated
              from tm_min.)

       %n     A newline character. (SU)

       %O     Modifier: use alternative format, see below. (SU)

       %p     Either "AM" or "PM" according to the given time value, or the
              corresponding strings for the current locale.  Noon is treated
              as "PM" and midnight as "AM".  (Calculated from tm_hour.)

       %P     Like %p but in lowercase: "am" or "pm" or a corresponding
              string for the current locale.  (Calculated from tm_hour.)
              (GNU)

       %r     The time in a.m. or p.m. notation.  In the POSIX locale this
              is equivalent to %I:%M:%S %p.  (SU)

       %R     The time in 24-hour notation (%H:%M).  (SU) For a version
              including the seconds, see %T below.

       %s     The number of seconds since the Epoch, 1970-01-01 00:00:00
              +0000 (UTC). (TZ) (Calculated from mktime(tm).)

       %S     The second as a decimal number (range 00 to 60).  (The range
              is up to 60 to allow for occasional leap seconds.)
              (Calculated from tm_sec.)

       %t     A tab character. (SU)

       %T     The time in 24-hour notation (%H:%M:%S).  (SU)

       %u     The day of the week as a decimal, range 1 to 7, Monday being
              1.  See also %w.  (Calculated from tm_wday.)  (SU)

       %U     The week number of the current year as a decimal number, range
              00 to 53, starting with the first Sunday as the first day of
              week 01.  See also %V and %W.  (Calculated from tm_yday and
              tm_wday.)

       %V     The ISO 8601 week number (see NOTES) of the current year as a
              decimal number, range 01 to 53, where week 1 is the first week
              that has at least 4 days in the new year.  See also %U and %W.
              (Calculated from tm_year, tm_yday, and tm_wday.)  (SU)

       %w     The day of the week as a decimal, range 0 to 6, Sunday being
              0.  See also %u.  (Calculated from tm_wday.)

       %W     The week number of the current year as a decimal number, range
              00 to 53, starting with the first Monday as the first day of
              week 01.  (Calculated from tm_yday and tm_wday.)

       %x     The preferred date representation for the current locale
              without the time.

       %X     The preferred time representation for the current locale
              without the date.

       %y     The year as a decimal number without a century (range 00 to
              99).  (Calculated from tm_year)

       %Y     The year as a decimal number including the century.
              (Calculated from tm_year)

       %z     The +hhmm or -hhmm numeric timezone (that is, the hour and
              minute offset from UTC). (SU)

       %Z     The timezone name or abbreviation.

       %+     The date and time in date(1) format. (TZ) (Not supported in
              glibc2.)

       %%     A literal '%' character.

       Some conversion specifications can be modified by preceding the
       conversion specifier character by the E or O modifier to indicate
       that an alternative format should be used.  If the alternative format
       or specification does not exist for the current locale, the behavior
       will be as if the unmodified conversion specification were used. (SU)
       The Single UNIX Specification mentions %Ec, %EC, %Ex, %EX, %Ey, %EY,
       %Od, %Oe, %OH, %OI, %Om, %OM, %OS, %Ou, %OU, %OV, %Ow, %OW, %Oy,
       where the effect of the O modifier is to use alternative numeric
       symbols (say, roman numerals), and that of the E modifier is to use a
       locale-dependent alternative representation.


## Order of operations
Each image processed, if the operations are specified, has their operations peformed in this order:
1. Image resize
2. Auto-rotation
3. Dating and/or Renaming
4. Thumbnail generation


## Some tips
1. Always backup data!
2. Before emplyoing this tool on a number of photos, be sure it will do what you want it to do using the -D or --dry-run option. This will tell you most of what operations are being done without actually doing them.
3. When using EXIF tags for renaming files from multiple camera make/models, do not use vendor specific tags, e.g. Exif.NikonFi.FileNumber as these may not be consistent across those cameras even for the same manufacturer. 


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

## Installation

To run the installer script, run bash install.sh 

The installer script looks for PATH and MANPATH to present installation directories. Proper permisions (e.g, sudo) must be obtained first. Alternatively the script can be copied anywhere and execute be set (chmod 755). The man page, imgtool.1, can be put in man1 on manpath. 
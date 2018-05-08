#!/usr/bin/env python2
import os, sys, datetime, time, exifread, fnmatch, glob2, re, pyexiv2
from PIL import Image
from PIL import ExifTags
from argparse import ArgumentParser
toolversion = '0.1'

description = """
Imgtool version {} - Copyright 2018 Nicole Stevens - Image manipulation tool
\n
Rename, reorient, resize and or timestamp jpg files with a unique name based on
camera model and taken date stored in the exif header. By default imgtool updates
the atime/mtime timestamps on a file to match the exif header data. 
""".format(toolversion)

versinfo = """
{}

Copyright 2018 Nicole Stevens

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""".format(description)

geometry_help = """
    GEOMETRY is used with the -z or --resize options are used.

    Geometry can be specified as a percentage of the overall image or as a pair of width:height. 
    Width and height are specified in pixels. If width is specified but no height, e.g., 1000:
    the image will be reized to a width of 1000px with a height calculated in relation to width to
    maintain the image aspect ratio. Conversely, height is specified without a width, e.g., :1000
    will resize the image to 1000px high with a width calculated to maintain the aspect ratio. 
    When the width and height are spcecified no attempt to maintain the aspect ratio is made.
"""

progwarning = """
WARNING: This tool was written to work with my photographs. It may even be destructive. Backing up 
data is always a good idea before employing automatic tools that can recurse directories. If you 
break something, you own the remaining pieces."""

defaultTimeFormat='%Y%m%d%H%M%S'
timeformatHelp='Set the time format used for naming files, in python strftime format, default is "{}"'.format(defaultTimeFormat.replace('%','%%'))

recurse = False
rename = False
dry = True

class fileExif:
    """ Read file exif data and process tags """
    def __init__(self,file,timeformat = '%Y%m%d%H%M%S'):
        self.timeformat = timeformat
        try:
            self.mtime = os.stat(file).st_mtime
        except Exception as e:
            print >> sys.stderr, "Cannot stat {}: {}".format(file,e)
            
        self.file = file
        with open(file,'rb') as f:
            e = exifread.process_file(f,details=False)
        self.exif = e

    def adjustOrientation(self):
        degrees = {3: 180, 6: 270, 8: 90}
        try:
            m = pyexiv2.ImageMetadata(self.file)
            m.read()
            if m['Exif.Image.Orientation'].value in degrees:
                image = Image.open(self.file)
                rot = degrees[m['Exif.Image.Orientation'].value]
                if verbose:
                    print 'Rotate image {} by {} degrees'.format(self.file,rot)
                if not dry:
                    image=image.rotate(rot, expand=True)
                    image.save(self.file)
                    m['Exif.Image.Orientation'].value = 1
                    m.write()
            else:
                if verbose:
                    print 'Not rotating image, {}, either {} is not in list or does not need rotation.'.format(self.file,m['Exif.Image.Orientation'].value)
        except Exception as e:
            m = 'Cannot rotate image {}: {}'.format(self.file,e)
            raise IOError(m)

    def __coord(self,s):
        if s == '':
            return None
        else:
            return int(s)

    def resize(self,gspec,geometry):
        try:
            image = Image.open(self.file)
            [imw,imh] = map(float,image.size)

            if gspec == 'P':
                p = float(geometry.split('%')[0])/100.0
                [rw,rh] = map(lambda x: x*p, [imw,imh])
            else:
                [rw,rh] = map(self.__coord,geometry.split(':'))
                if rh and not rw:
                    hpercent = rh/imh
                    rw = imw*hpercent
                elif rw and not rh:
                    wpercent = rw/imw
                    rh = imh * wpercent

            rw,rh = map(int,[rw,rh])
            if verbose:
                print 'Resize {} to {}x{}'.format(self.file,rw,rh)
            i = image.resize((rw,rh), Image.ANTIALIAS)
            imexif = image.info['exif']
            if not dry:
                i.save(self.file, exif=imexif)
        except Exception as e:
            m='Cannot resize {}: {}'.format(self.file,e)
            raise IOError(m)


    def tag(self,tag,_type = str):
        try:
            tdata = self.exif[tag]
        except KeyError:
            return None
        return _type(tdata)

    def fileDate(self):
        """ get a EPOCH time value from exif data """
        try:
            dt = self.tag('Image DateTime')
            e = time.mktime(datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S").timetuple())
            return int(e)
        except:
            return self.mtime

    def cameraNameForFile(self):
        """ get a new file name for loaded image based on the camera make and model. 
            of those cannot be determined return the original name. """
        ext = os.path.splitext(self.file)[1]
        path =  os.path.dirname(self.file)
        epoch = self.fileDate()
        timestr = time.strftime(self.timeformat,time.localtime(epoch))

        try:
            mk = self.tag('Image Make')
            md = self.tag('Image Model').split(' ')[1]
        except:
            if verbose:
                print >> sys.stderr, '{}: Cannot get Image.Make or Image.Model'.format(self.file)
            if epoch and epoch > 0:   # Only rename if there is an emedded date
                return '{}{}'.format(timestr,ext),epoch
            return self.file,self.mtime


        if mk is not '' and md is not '':
            n = os.path.join(path,'{}_{}{}'.format(md,timestr,ext.lower()))
            return n,epoch
        return src

def setFileInfo(path,fname,exif,rename):
    info = ''
    fname = os.path.join(path,fname)
    tstamp = exif.fileDate()
    newname = False
    if rename:
        newname,tstamp = exif.cameraNameForFile()
        if not newname == fname:
            if rename:
                info = info + 'new name: {} '.format(newname)
                if not dry:
                    try:
                        os.rename(fname,newname)
                    except Exception as e:
                        print >> sys.stderr, "Error renaming file {} to {}: {}".format(fname,newname,e)
    if tstamp:
        if not newname:
            newname = fname 
        info = info + 'set time to {} '.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tstamp)))
        if not dry:
            try:
                os.utime(newname,(tstamp,tstamp))
            except Exception as e:
                print >> sys.stderr, "Error setting date on {}: {}".format(fname,e)
    if dry or verbose:
        if info == '':
            info = 'No Action'
        print 'File {}: {}'.format(fname,info)

def getFileList(dir,recurse,pat):
    flist = []
    if not recurse:
        for fname in glob.glob(os.path.join(dir,pat)):
            flist.append(fname)
    else:
        for root, dirs, files in os.walk(dir):
            for fname in files:
                if fnmatch.fnmatch(fname,pat):
                    flist.append(os.path.join(root,fname))
    return flist

def geometryHelp():
    parser.print_help()
    print geometry_help

def checkGeometrySpec(geometry):
    rPerc = r"^[0-9]{1,2}\%$"               # regex to match percentage
    rCart = r"^[0-9]{0,10}\:[0-9]{0,10}$"   # regex to match cartesians
    if re.match(rPerc,geometry):
        return 'P'
    if re.match(rCart,geometry):
        return 'C'
    return False

def getparser(alist=None):
    
    if alist:
        parser = ArgumentParser(alist,
            description=description, epilog=progwarning)
    else:
        parser = ArgumentParser(description=description, epilog=progwarning)

    parser.add_argument("-R", "--recurse", dest="recurse", default = False, action='store_true',
                        help="Recurse into sub-directories")
    parser.add_argument("-c", "--camera-names",action="store_true", dest="rename", default=False,
                        help="Rename pictures that have an embedded camera name to unique and meaningful names.")
    parser.add_argument("-d", "--dry_run",action="store_true", dest="dry", default=False,
                        help="Dry run: show what will be done without actually doing it. (sets verbose too.)")
    parser.add_argument('-f', '--format', action='store', dest='timeformat', default=defaultTimeFormat,
                        metavar='FORMAT',help=timeformatHelp)
    parser.add_argument('-p', '--pattern', action='store', dest='pat', default=None,
                        metavar='Pattern',help='Pattern, e.g, *.jpg, to match files against.')
    parser.add_argument('-r', '--auto-rotate', action="store_true", dest="rotate", default=False,
                        help="Automatically rotate images.")
    parser.add_argument('-z', '--resize', action='store', dest='resize', default=None, metavar='GEOMETRY',
                        help='Resize Images by: x%% or (width:height) if width or heigh is blank, Automatically calcualte based on the present value.')
    parser.add_argument('--help-geometry', action="store_true", dest="geohelp", default=False,
                        help='Show additional help on GEOMETRY and exit.')
    parser.add_argument('list', metavar='PATH', type=str, nargs='*',
                        help='File(s) or sub-directories to process')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                        help='Be chatty about what is being done.')
    parser.add_argument('-V','--version', action='store_true', dest='dispversion', default=False,
                        help='Show version information and exit.')
    return parser


if __name__ == '__main__':
    globPat = '*.[Jj][Pp][Gg]'

    parser = getparser()
    args = parser.parse_args()

    if args.dispversion:
        print versinfo.format(toolversion)
        parser.print_help() 
        sys.exit(0)
    if args.geohelp:
        geometryHelp()
        sys.exit(0)

    if args.resize:
        try:
            geoSpec = checkGeometrySpec(args.resize)
            if not geoSpec:
                raise ValueError()
        except Exception as e:
            print >>sys.stderr,"{} is an invalid geometry\n".format(args.resize)
            print >>sys.stderr,"Use --help-geometry for information on size geometry."

        if not geoSpec:
            sys.exit(1)
    recurse = args.recurse
    rename = args.rename
    verbose = args.verbose 
    dry = args.dry
    if dry:
        verbose = True

    if args.pat:
        globPat = args.pat
        globCwd = True
    else:
        globCwd = False

    flist = []

    if globCwd:
        flist = glob2.glob(globPat,recursive=recurse)

    if args.list:
        for f in args.list:
            if os.path.isdir(f):
                if args.recurse:
                    flist.extend(getFileList(f,recurse,globPat))
                else:
                    if verbose:
                        print >>sys.stderr, "--recurse not set. {} is a directory. Cannot process.".format(f)
            else:
                if fnmatch.fnmatch(f,globPat):
                    flist.append(f)
    
    if len(flist) < 1:
        print >>sys.stderr,'Nothing to do.'

    for file in flist:
        if not os.path.isdir(file):
            dir = os.path.dirname(file)
            fname = os.path.basename(file) 
            exif = fileExif(file,args.timeformat)
            if args.rotate:
                if dry:
                    print 'Would rotate'
                else:
                    exif.adjustOrientation()
            if args.resize:
                if dry:
                    print 'Would resize '
                else:
                    exif.resize(geoSpec,args.resize)
            setFileInfo(dir,fname,exif,rename)

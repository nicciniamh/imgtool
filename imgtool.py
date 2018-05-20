#!/usr/bin/env python2
import os, sys, datetime, time, fnmatch, glob2, re, pyexiv2, shutil
from PIL import Image
from PIL import ExifTags
from argparse import ArgumentParser
toolversion = '0.1.5'

description = """
Imgtool version {} - Copyright 2018 Nicole Stevens - Image manipulation tool:  
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
Geometry can be specified as a percentage of the overall image or as
a pair of [width]x[height]. Width and height are specified in pixels.
If width is specified but no height, e.g., 1000x the image will be
resized to a width of 1000px with a height calculated in relation to
width to maintain the image aspect ratio. Conversely, height is specified
without a width, e.g., x1000 will resize the image to 1000px high with a
width calculated to maintain the aspect ratio. When the width and height are
spcecified no attempt to maintain the aspect ratio is made.
"""

format_help = """
Formatting filenames for automatic renaming is as follows:
    [@|+]type.Tag%timefmt

Tags starting with @ have their spaces replaced with periods (.), Tags 
starting with + do not have spaces replaced. There are two types of tags, 
File and Exif. File Tags are:

    File.Name:  Filename of the image without extension
    File.Ext:   Extension of filename, e.g., .JPG 
    File.ext:   Extension of filename converted to lower-case, e.g., .jpg
    File.Fullname: Full name of file with directories.
    File.mtime: String representation YYYYMMDDhhmmss of the file's 
                timestamp in the filesystem.


EXIF Tags vary by image and camera. Running imgtool --dumpexif <image> may
be useful in finding appropriate tags. When specifying EXIF Tags, they are
formatted as Exif.Image.Model which results in a string, for one of my cameras,
as 'NIKON D3400', by default the resultant string will have spaced replaced 
with periods (.), to suppress this behavior, precede them with a plus (+).
E.g.:

    @Exif.Image.Make returns 'NIKON.D3400'
    and
    +Exif.Image.Make returns 'NIKON D3400' 

This conversion is done just before substituting the tag with its value. 

Splitting strings in tags:
Splitting the tag values can be done as an index of space separated words 
or as a substring. 

To use an index, 
place the index number in brackets, e.g, @Exif.Image.Make[1] returns 
'D3400' instead of 'NIKON D3400'. Index values start with 0. 

To use a substring, place the start and, optionally the length in 
parentheses. E.g, @Exif.Image.Make(7,5) will return 'D3400' instead of 
'NIKON D3400'. If the second value is omitted the length of the value,
starting at the first number is presumed, so @Exif.Image.Make(7) will 
also result with 'D3400'

Any EXIF Tag present in the image EXIF header can be used to create all
or part of a file name. For example, @Image.Make[1]_@File.name@File.ext
will create, from DSC_328.JPG a name of 'D3400_DSC_328.jpg'

Note that the @File tags are never evaluated with a plus instead of 
an at-sign (@), and no indexing or substring operations are performed.

Time formatting, using the EIXF header's image time, is formatted with
strftime formatting. See strftime(3).

"""

progwarning = """
WARNING: This tool was written to work with my photographs. It may even
be destructive. Backing up data is always a good idea before employing
 automatic tools that can recurse directories. If you break something, 
 you own the remaining pieces."""

defaultTimeFormat='@Exif.Image.Model[1]_%Y%m%d%H%M%S@File.ext'
timeformatHelp='Set the time format used for naming files, in python strftime format, default is "{}"'.format(defaultTimeFormat.replace('%','%%'))

recurse = False
rename = False
dry = True

class log:
    def __init__(self,out=sys.stdout,err=sys.stderr):
        self.out=out
        self.err=err

    def logout(self,tag,s):
        print >>self.out,'{}: {}'.format(tag,s)

    def errout(self,msg):
        print >>self.err,'ERROR',msg

    def debugout(self,msg):
        global args
        if args.debug:
            print >>self.err,'DEBUG',msg

    def __call__(self,tag,msg):
        self.logout(tag,msg)

logger = log()
error = logger.errout
debug = logger.debugout

class fileExif:
    """ Read file exif data and process tags """
    def __init__(self,file,timeformat = defaultTimeFormat):
        self._renospc = '(\@[A-Za-z\.0-9]*[\(\)\[\]\,0-9]*)'
        self._renoxlt = self._renospc.replace('@','+')

        self.timeformat = timeformat
        try:
            self.mtime = os.stat(file).st_mtime
        except Exception as e:
            error("Cannot stat {}: {}".format(file,e))
            raise e
            
        self.file = file
        try:
            e = pyexiv2.ImageMetadata(self.file)
            e.read()
            self.exif = e
        except Exception as e:
            debug('{} Cannot get exif data {}'.format(self.file,e))
            e = None
        self.exif = e
        self.fileInfo = {'File.Name': os.path.splitext(os.path.basename(self.file))[0],
                         'File.Ext': os.path.splitext(os.path.basename(self.file))[1],
                         'File.ext': os.path.splitext(os.path.basename(self.file))[1].lower(),
                         'File.FullName': self.file,
                         'File.mtime': time.strftime('%Y%m%d%H%M%S',time.localtime(self.mtime))
                    }
    def dumpkeys(self):
        for k in self.exif.exif_keys:
            logger('KEYDUMP',k)

    def fileTag(self,tag):
        if tag in self.fileInfo:
            return self.fileInfo[tag]
        return ''

    def adjustOrientation(self):
        degrees = {3: 180, 6: 270, 8: 90}
        if self.exif is None:
            if verbose:
                logger('INFO','Not rotating image {}: No EXIF data.'.format(self.file))
            return
        try:
            if self.exif['Exif.Image.Orientation'].value in degrees:
                image = Image.open(self.file)
                rot = degrees[self.exif['Exif.Image.Orientation'].value]
                if verbose:
                    logger('INFO','Rotate image {} by {} degrees'.format(self.file,rot))
                if not dry:
                    image=image.rotate(rot, expand=True)
                    image.save(self.file)
                    self.exif['Exif.Image.Orientation'].value = 1
                    self.exif.write()
            else:
                if verbose:
                    logger('INFO','Not rotating image, {}, either {} is not in list or does not need rotation.'.format(self.file,self.exif['Exif.Image.Orientation'].value))
        except Exception as e:
            raise IOError('Cannot rotate image {}: {}'.format(self.file,e))

    def __coord(self,s):
        if s == '':
            return None
        else:
            return int(s)

    def resize(self,geometry):
        try:
            image = Image.open(self.file)
            [imw,imh] = map(float,image.size)

            if type(geometry) is float:
                p = geometry
                [rw,rh] = map(lambda x: x*p, [imw,imh])
            else:
                [rw,rh] = geometry
                if rh and not rw:
                    hpercent = rh/imh
                    rw = imw*hpercent
                elif rw and not rh:
                    wpercent = rw/imw
                    rh = imh * wpercent

            rw,rh = map(int,[rw,rh])
            if verbose:
                logger('INFO','Resize {} to {}x{}'.format(self.file,rw,rh))
            i = image.resize((rw,rh), Image.ANTIALIAS)
            imexif = image.info['exif']
            if not dry:
                i.save(self.file, exif=imexif)
        except Exception as e:
            raise IOError('Cannot resize {}: {}'.format(self.file,e))

    def thumbnail(self,image,size = (96,96),color=None):
        ''' Create a thumbnail image from the source image and return the newly created image.
        '''
        i = Image.new('RGBA',image.size,color)
        if type(size) is float:
            size = map(lambda x: int(x*p), size)

        i.paste(image)
        i.thumbnail(size)
        b = Image.new('RGBA',size,color)
        left,top = [0,0]
        if i.size[0] < size[0]:
            left = (b.size[0] /2 ) - (i.size[0]/2)

        if i.size[1] < size[1]:
            top = (b.size[1] /2 ) - (i.size[1]/2)

        box = (left,top)

        b.paste(i,box)
        return b

    def genThumbFile(self, fname, size, thumbdir=False):
        [dir,name] = os.path.split(fname)
        if thumbdir:
            dir = thumbdir
        if verbose:
            logger('INFO','Generate thumbnail for {} {} in {}'.format(fname,size,dir))
        i = Image.open(fname)
        name = '{}-thumb{}'.format(os.path.splitext(name)[0],'.png')
        fname = os.path.join(dir,name)
        t = self.thumbnail(i,size)
        if verbose:
            logger('INFO','Writing {} thumbnail to {}'.format(t.size,fname))
        if not dry:
            t.save(fname)


    def tag(self,tag,_type = str):
        tag = tag.replace(' ','.')
        if tag.startswith('Exif.'):
            try:
                tdata = self.exif[tag].value
            except KeyError:
                tdata = None
        if tag.startswith('File.'):
            try:
                tdata = self.fileInfo[tag]
            except KeyError:
                tdata = None
        return _type(tdata)

    def _extractExif2(self,match):
        def ispunct(s):
            return s is not None and ord(s[0]) > 32 and not s[0].isalnum()
        tregex = r'(\([0-9]*\,?[0-9]*?\))|(\[[0-9]*\])'
        tokens = []
        groups = []
        tag  = ''
        base = match.group()
        tlist = re.split(tregex,base)

        for token in tlist:
            if token and ispunct(token):
                tokens.append(token)
        
        if not len(tokens):
            return ''

        srch = {
                'tag': r'[\@\+]{1}[A-Za-z\.]*',
                'sub': r'\(([0-9]*)\,?([0-9]*)?\)*',
                'idx': r'\[([0-9]*)\]*',
        }

        for item in tokens:
            if item:
                for typ,rx in srch.items():
                    m = re.match(rx,item)
                    if m:
                        if typ == 'tag':
                            tag = item[1:]
                        if typ == 'sub':
                            pstart = int(m.groups()[0])
                            if m.groups()[1]:
                                pend = pstart + int(m.groups()[1])
                            else:
                                pend = -1
                            groups.append((typ, (pstart,pend)))
                        if typ == 'idx':
                            if not m.groups()[0]:
                                idx = -1
                            else:
                                idx = int(m.groups()[0])
                            groups.append((typ, idx))

        try:
            tag = self.tag(tag)
        except:
            return ''
        for g in groups:
            if g[0] == 'sub':
                pstart,pend = g[1]
                if pstart < len(tag):
                    if pend == -1 or pend >= len(tag):
                        pend = len(tag)
                tag = tag[pstart:pend]
            if g[0] == 'idx':
                if tag:
                    parts = tag.split(' ')
                    if g[1] < len(parts):
                        tag = parts[g[1]]

        return tag

    def _extractExif1(self,match):
        return self._extractExif2(match).replace(' ','.')

    def formatStringExif(self,s):
        s = time.strftime(s,time.localtime(self.fileDate()))
        s = re.sub(self._renospc,self._extractExif1, s)
        s =re.sub(self._renoxlt,self._extractExif2,s)
        return s

    def fileDate(self):
        """ get a EPOCH time value from exif data """
        try:
            dt = self.exif['Exif.Image.DateTime'].value
            dt = time.mktime(dt.timetuple())
            return int(dt)
        except Exception as e:
            debug('Cannot get exif date time {}'.format(e))
            return self.mtime

    def exifNameForFile(self):
        """ get a new file name for loaded image based on the camera make and model. 
            of those cannot be determined return the original name. """
        ext = os.path.splitext(self.file)[1]
        path =  os.path.dirname(self.file)
        file = self.formatStringExif(self.timeformat)
        file = re.sub(r'^_','',file)

        return os.path.join(path,file),self.fileDate()

def setFileInfo(path,fname,exif,rename,outdir=None,noclobber=False):
    info = ''
    fname = os.path.join(path,fname)
    tstamp = exif.fileDate()
    newname = False
    if rename:
        newname,tstamp = exif.exifNameForFile()
        if not newname == fname:
            if rename:
                if outdir:
                    outdir = list(os.path.split(outdir))
                    newname = list(os.path.split(newname))
                    if newname[0].startswith('./'):
                        newname[0] = newname[0][2:]
                        newname.insert(0,'.')
                    if len(newname) >= 2:
                        newname.remove(newname[0])
                    newname = outdir + newname
                    newname = os.path.join(*newname)
                info = info + 'new name: {} '.format(newname)
                if not dry:
                    try:
                        docopy(fname,newname,noclobber)
                    except Exception as e:
                        error("Error renaming file {} to {}: {}".format(fname,newname,e))
                        raise e
    if tstamp:
        if not newname:
            newname = fname 
        info = info + 'set time to {} '.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tstamp)))
        if not dry:
            try:
                os.utime(newname,(tstamp,tstamp))
            except Exception as e:
                error("Error setting date on {}: {}".format(fname,e))
    if dry or verbose:
        if info == '':
            info = 'No Action'
        logger('INFO','File {}: {}'.format(fname,info))
    if newname:
        return newname
    else:
        return fname

def docopy(src,dst,noclobber=False):
    newdir = os.path.dirname(dst)
    if os.path.exists(dst) and noclobber:
        raise RuntimeError('No-clobber is set, will not replace existing {}'.format(dst))

    if not os.path.exists(newdir):
        os.makedirs(newdir)
    if not os.path.exists(newdir):
        raise RuntimeError('Cannot create new path {}',newdir)
    shutil.copy2(src,dst)
    if os.path.exists(dst):
        os.unlink(src)
    else:
        raise RuntimeError('Destination, {}, does not seem to exist, not removing source. {}',dst,src)


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

def formatHelp():
    parser.print_help()
    print format_help

def checkGeometry(geometry):
    try:
        if '%' in geometry:
            geometry = float(geometry.split('%')[0])/100.0
        elif 'x' in geometry:
            geometry = map(int,geometry.split('x'))
        else:
            geometry = None
    except:
        geometry = None
    return geometry

if __name__ == '__main__':
    globPat = '*.[Jj][Pp][Gg]'

    cwd = os.getcwd()
    parser = ArgumentParser(description=description, epilog=progwarning)

    parser.add_argument("-R", "--recurse", dest="recurse", default = False, action='store_true',
                        help="Recurse into sub-directories")
    parser.add_argument("-c", "--camera-names",action="store_true", dest="rename", default=False,
                        help="Rename pictures that have an embedded camera name to unique and meaningful names.")
    parser.add_argument("-D", "--dry_run",action="store_true", dest="dry", default=False,
                        help="Dry run: show what will be done without actually doing it. (sets verbose too.)")
    parser.add_argument('-d', '--output-directory', dest='outdir', action='store', type=str, default=None, metavar='directory',
                        help='When renaming, place the files with the base directory specified.')
    parser.add_argument('-f', '--format', action='store', dest='timeformat', default=defaultTimeFormat,
                        metavar='format-string',help=timeformatHelp)
    parser.add_argument('-n', '--no-clobber', action='store_true', dest='noclobber', default=False,
                        help='Do not overwrite existing files.')
    parser.add_argument('-p', '--pattern', action='store', dest='pat', default=None,
                        metavar='Pattern',help='Pattern, e.g, *.jpg, to match')
    parser.add_argument('-r', '--auto-rotate', action="store_true", dest="rotate", default=False,
                        help="Automatically rotate images.")
    parser.add_argument('-t', '--thumbnail', action='store_true', dest='genthumbs', default=False, 
                        help='Generate thumbnails in the same output path. Use --thumb-geometry to override default of 96x96, use --thumb-dir to override output directory.')
    parser.add_argument('--thumb-dir',action='store', default=None, dest='thumbdir', metavar='directory',
                        help='Override thumbnail output directory.')
    parser.add_argument('--thumb-geometry',action='store', default=None, dest='thumbgeo', metavar='geometry',
                        help='Override thumbnail size with geometry, see --help-geometry')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                        help='Be chatty about what is being done.')
    parser.add_argument('-V','--version', action='store_true', dest='dispversion', default=False,
                        help='Show version information and exit.')
    parser.add_argument('-z', '--resize', action='store', dest='resize', default=None, metavar='geometry',
                        help='Resize Images by geometry, see --help-geometry')
    parser.add_argument('--debug', action='store_true', dest='debug', default=False, help='Enable debugging messages')
    parser.add_argument('--dumpkeys',action='store_true', dest='dumpkeys', default=False,
                        help='Dump all exif tag keys for first file and exit.')
    parser.add_argument('--help-geometry', action="store_true", dest="geohelp", default=False,
                        help='Show additional help on GEOMETRY and exit.')
    parser.add_argument('--help-format', action="store_true", dest="fmthelp", default=False,
                        help='Show help on formatting names for automatic renaming')
    parser.add_argument('list', metavar='PATH', type=str, nargs='*',
                        help='File(s) or sub-directories to process')

    args = parser.parse_args()

    if args.dispversion:
        print versinfo.format(toolversion)
        parser.print_help() 
        sys.exit(0)
    
    if args.geohelp:
        geometryHelp()
        sys.exit(0)

    if args.fmthelp:
        formatHelp()
        sys.exit(0)

    if args.resize:
        try:
            geoSpec = checkGeometry(args.resize)
            if not geoSpec:
                raise ValueError()
        except Exception as e:
            error("{} is an invalid geometry\n".format(args.resize))
            error("Use --help-geometry for information on size geometry.")

        if not geoSpec:
            sys.exit(1)

    thumbgeo = (96,96)
    if args.genthumbs and args.thumbgeo:
        try:
            thumbgeo = checkGeometry(args.thumbgeo)
            if not thumbgeo:
                raise ValueError()
        except Exception as e:
            error("{} is an invalid geometry\n".format(args.resize))
            error("Use --help-geometry for information on size geometry.")

        if not thumbgeo:
            sys.exit(1)

    if args.thumbdir:
        thumbdir = args.thumbdir
    else:
        thumbdir = None

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
                        error("--recurse not set. {} is a directory. Cannot process.".format(f))
            else:
                if fnmatch.fnmatch(f,globPat):
                    if not f in flist:
                        flist.append(f)
    
    if len(flist) < 1:
        error('Nothing to do.')

    if args.dumpkeys:
        fileExif(flist[0]).dumpkeys()
        sys.exit(0)

    for file in flist:
        if not os.path.isdir(file):
            dir = os.path.dirname(file)
            fname = os.path.basename(file) 
            exif = fileExif(file,args.timeformat)
            if args.resize:
                exif.resize(geoSpec)
            if args.rotate:
                exif.adjustOrientation()
            newname = setFileInfo(dir,fname,exif,rename,args.outdir,args.noclobber)
            if newname and args.genthumbs:
                exif.genThumbFile(newname,thumbgeo,thumbdir)

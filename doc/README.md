# Building Docs for Imgtool

Automated Document Tools and Content In this directory are the
source files, tools, and Makefile to generate the markdown for
README.md, imgtool.html and imgtool.1 (UNIX manual page format)

## Requirements
To use these tools, you must have [GNU Make](https://www.gnu.org/software/make/) on your system. Please
consult your package management on how to install this. 
To generate the HTML and manual pages, [Pandoc](https://pandoc.org) is
used. This tool must be present in your build environment.

## Build Process
To build the documentation, in this directory, run `make`.
To clean up the build environment, run `make clean`.

In the first generated markdown file, reademe-markdown.md, there is 
a line at the top which is used by [Pandoc](https://pandoc.org) to generate the manual page.
This line looks similar to
> ```% imgtool(1) || Imgtool - JPEG Photo tool```

Before the resulting markdown documents are put in the parent directory, i.e, 
> ../README.md
../imgtool.html
 
This line gets translated to markdown from the [Pandoc](https://pandoc.org) format to
markdown. 

The resulting documents, including the manual page are placed in the parent directory.

## Documentation Source files
- head - Top of the file
- geometry - Description of geometry
- order-of-operations - Description of order operation
- renaming - How file renaming works
- tips - Some tips on usage
- install - Installation instructions and pre-requisites
- foot - Bottom matter
- pandoc.css - CSS file for inclusion in pandoc generted HTML

## Tools
- Makefile - GNU Makefile to generate the resulting documents
- buildtoc - Build a TOC from markdown
- splitopts,optparse - Take the ouput of imgtool -h and convert usage stuff to markdown
- makebody - Builds the body using various tools. 


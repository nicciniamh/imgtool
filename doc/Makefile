SHELL := /bin/bash
generated = body toc options imgtool.1 imgtool.html readme-markdown.md
docsrcs = geometry order-of-operations renaming tips install foot

all: options readme-markdown.md imgtool.1 imgtool.html ../README.md ../imgtool.1 ../imgtool.html

imgtool.html: readme-markdown.md pandoc.css
	cat readme-markdown.md | sed -e 's/%/#/g' -e 's/(1)//g' -e 's/|//g' |\
		pandoc -s -f markdown --to html --include-in-header=pandoc.css -o imgtool.html


readme-markdown.md: head  body toc $(docsrcs)
	cat head toc body  >readme-markdown.md

imgtool.1: readme-markdown.md
	cat head body | pandoc -f markdown --standalone --to man  -o imgtool.1

body: $(docsrcs)
	:>body
	./makebody >body


options:
	./optparse >options

../README.md: readme-markdown.md
	cat readme-markdown.md | sed -e 's/%/#/g' -e 's/(1)//g' -e 's/|//g' >../README.md

../imgtool.1: imgtool.1
	cp imgtool.1 ..

../imgtool.html: imgtool.html
	cp imgtool.html ..

toc:
	./buildtoc body 2 >toc

clean:
	rm -f $(generated)
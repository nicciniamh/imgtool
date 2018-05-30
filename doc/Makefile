SHELL := /bin/bash
generated = body toc options readme-markdown.md
docgen = imgtool.1 imgtool.html imgtool.md 
docsrcs = head geometry order-of-operations renaming tips install foot

all: options readme-markdown.md imgtool.1 imgtool.html ../README.md ../imgtool.1 ../imgtool.html ../imgtool.md

imgtool.html: imgtool.md pandoc.css
	# Building HTML
	pandoc -s imgtool.md --to html --include-in-header=pandoc.css -o imgtool.html


readme-markdown.md: $(docsrcs) $(generated) 
	# Building intermediate markdown
	cat head toc body  >readme-markdown.md

imgtool.md: readme-markdown.md
	# Building final markdown
	cat readme-markdown.md | sed -e 's/%/#/g' -e 's/(1)//g' -e 's/|//g'>imgtool.md

imgtool.1: readme-markdown.md
	# Building Manual Page
	cat head body | pandoc -f markdown --standalone --to man  -o imgtool.1

body: $(docsrcs)
	# Building Document Body
	:>body
	./makebody >body


options:
	# Building Usage and Options
	./optparse >options

../README.md: imgtool.md
	cp imgtool.md ../README.md

../imgtool.1: imgtool.1
	cp imgtool.1 ..

../imgtool.html: imgtool.html
	cp imgtool.html ..

../imgtool.md: imgtool.md
	cp imgtool.md ..

toc:
	./buildtoc body 2 >toc

clean:
	rm -f $(generated) $(docgen) readme-markdown.md 
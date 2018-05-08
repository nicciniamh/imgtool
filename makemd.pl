use HTML::FormatMarkdown;

my $string = HTML::FormatMarkdown->format_file(
   'README.html'
);
print $string;

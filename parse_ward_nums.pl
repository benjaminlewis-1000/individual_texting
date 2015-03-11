#! /usr/bin/perl

my $file = "ward_tmp.csv";

open FILE, $file or die $!;
open OUT, ">ward_parsed.csv";

while (<FILE>){
	$_ =~ s/-//g;
	$_ =~ s/ /,/;
	print OUT $_ ;
	print $_ . "\n";
}

close OUT;
close FILE;
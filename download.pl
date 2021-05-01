#!/usr/bin/perl
package Download;
use strict;
use warnings;
our @EXPORT = qw(getfiles getdate getmonth);

my $BASE_URL = "https://portal.inmet.gov.br/uploads/dadoshistoricos/";

sub getdate { 
  return `date -u +"%Y"`;
}

sub getmonth { 
  return `date -u +"%b"`;
}


sub getfiles {
  my $date = getdate();
  my ($from, $to) = @_;

  if ($to > $date){
    die "End date is greater than current year!";
  }

  print "Downloading years: $from - $to\n";
  print `mkdir data`;
  for my $year ($from..$to){
    print("Downloading: ".$year."\n");
    my $filename = $BASE_URL.$year.".zip";
    print `cd data; rm $year.zip; wget $filename`;
  }
}


unless (caller) {
  my $date = getdate;
  print $date;
  my ($from, $to) = @ARGV >= 2 ? @ARGV : (2000, $date);
  getfiles $from, $to;
  my $month = getmonth();
  `echo "$month" > data/lastmonth`;
}

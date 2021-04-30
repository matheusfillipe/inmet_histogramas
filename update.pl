#!/bin/perl
require "./download.pl";
use strict;
use warnings;

my $BASE_URL = "https://portal.inmet.gov.br/uploads/dadoshistoricos/";

my $date = Download::getdate();
my @zips = glob('data/[0-9][0-9][0-9][0-9].zip');
my @years = map {(split "/", $_)[-1]=~s/\.zip$//r} @zips;
my $month = Download::getmonth();

Download::getfiles($years[-1], $date) if $month."\n" ne `cat data/lastmonth`;
`echo "$month" > data/lastmonth`;


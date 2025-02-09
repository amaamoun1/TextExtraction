#!/usr/bin/perl
use strict;
use warnings;
use Text::CSV_XS;

####
#### Usage perl process4.pl azw
####

# Subroutine clean
sub clean {
	$_[0] =~ s/[\n\r\x07\x0C]+/\n/g;
	$_[0] =~ s#[^\w\n\+\-\.,\(\)/]# #g;
	# $_[0] =~ s/\n\s+/\n/g;
	# $_[0] =~ s/ {2,}/ /g;
	$_[0] =~ s/^\W*//g;
	$_[0] =~ s/\W*$//g;
	$_[0];
}
sub clean_spaces {
	$_[0] =~ s/\s+/ /g;
	$_[0] =~ s/^\s+//g;
	# $_[0] =~ s/\s+$//g;
	$_[0];
}
sub clean_unwrap {
	$_[0] =~ s/\n\s{5,}/ /g;
	$_[0];
}
sub clean_short {
	$_[0] =~ s/\n/; /g;
	$_[0] =~ s/\s+/ /g;
	$_[0] =~ s/^\s+//g;
	# $_[0] =~ s/\s+$//g;
	$_[0] = substr($_[0] , 0, 2500) if (length($_[0] ) > 2500);
	$_[0];
}


	# $front = substr($front, 0, 2500) if (length($front) > 2500);
	# $front =~ s/\n/; /g;


my($day, $month, $year)=(localtime)[3,4,5];
my $td = substr( "0".($month+1), -2) . substr( "0$day", -2 ) . substr( "0".($year+1900), -2 ) ;



# Load file with keywords to be extracted
my @keywords;
my %graded =();
open KEYWORDS, "keywords.txt" or die $!;
while (<KEYWORDS>) {
	chomp;
	if (m/^x/){
		s/^x//;
		$graded{$_} = 1;
	}
	@keywords = (@keywords, $_);
}
close KEYWORDS;

###
### Initialize output
###
open DATA, ">", "pdftotext.$td.csv" or die $!;
my $csv_out = Text::CSV_XS->new({binary => 1});


# Create and print output header
my @out = ('ID', 'Path', 'File', 'Client', 'Front', @keywords, 'Competencies');
my $status = $csv_out -> combine(@out);
my $line_out = $csv_out->string() ;
print DATA "$line_out\n";


###
### Main loop
###
my @missing = ();
my $line_nr = 0;
my $started = 0;

open FILES, "/Volumes/Qweb/Documents/Data\ ghSMART/pdftotext/pdf.txt" or die $!;
# open FILES, "files_test.txt" or die $!;


while (<FILES>) {
	chomp;
	my $f = $_;
	$line_nr++;
	exit if ($f eq 'EXIT');

	if ($started == 0) {
		$started = ( $f eq "START" );
		next;
	}
	next unless (m/\.pdf$/i);



	print STDERR "Testing: \t($line_nr) \t$f\n";

#	my $skip = ( m/agreement|resume|scorecard|360|interview guide|reference list|meeting confirmation|development plan|reference list|CVR.?\.doc/i);
#	$skip = 0 if ( m/ass?ess?ment/i);
#	next if $skip;
#	next if ( m/^skip/i );
#	next if ( m/\(2\)\.doc/i );


	my $path = $f;
	$path =~ s#/Clients//#/Clients/#;

	my $client = '.';
	my $file   = '.';
	$client = $1 if ($path =~ m#/SharePoint/Volumes/Clients/([^/]*)/#);
	$file   = $1 if ($path =~ m#([^/]*)\Z#);


	print STDERR "Processing: \t($line_nr) \t$f\n";
	print STDERR "Path: \t\t\t$path\n";

	unless (-e $path) {
		print STDERR "Missing: \t$f\n";
		@missing = (@missing, $path);
		next;
	}

	# Extract text from pdf document
	# unlink ('/Volumes/RAID1/HOME/Desktop/TXT.txt');
#	system ('automator ~/Documents/Data\ ghSMART/Doc_to_txt_originals/Close_Word.app');

	my $test = `pdftotext -layout \"$path\" ~/Desktop/test.txt` ;

	my $cmd = "pdftotext -layout \"$path\" -" ;
	my $raw = `$cmd`;

	# Parse into sections, extract and clean
	my @section = map { &clean($_) } ($raw =~ m/[^\x0C]*\x0C/g);

	my $front = &clean_unwrap($section[0]);



	$front   =~ s/Purpose of This\s{3}/Purpose of This Assessment   /;
	$front   =~ s/\nAssessment\s{3,}/ /;




# 	Locate competencies section
	my $competencies = " ";
	my $competencies_index = 0;
	my $competencies_count = 0;
	foreach my $sec (@section) {
		$competencies_index = $competencies_count if ($sec =~ m/Competency Scorecard/);
		$competencies_count++;
	}
	if ($competencies_index == 0) {
		$competencies_count = 0;
		foreach my $sec (@section) {
			$competencies_index = $competencies_count if (($sec =~ m/Competencies/) && ($sec =~ m/rating\s+and\s+comments/i));
			$competencies_count++;
		}
	}
	if ($competencies_index == 0) {
		$competencies_count = 0;
		foreach my $sec (@section) {
			$competencies_index = $competencies_count if (($sec =~ m/Competencies/) && ($sec =~ m/removes\s+underperformers/i));
			$competencies_count++;
		}
	}

	$competencies = $section[$competencies_index].$section[$competencies_index+1];
	$competencies   =~ s#/# #g;






	print STDERR "\n\nFRONT: \n$front\n";
	print STDERR "----------------------\n";
	print STDERR "\n\nCOMPETENCIES: \n$competencies\n";
	print STDERR "----------------------\n";

	# Extract subsets (text_d is for date, needs to keep "/", other text cannot keep this as keyword may or may not have it)
	my $text = &clean($raw);
	my $text_d = $text;
	# print "TEXT is:$text";
	# open T, ">" , "text6.txt" or die;
	# print T "$text_d";
	# close T;



	# initialize hash for data
	my %field = ();

	# process keywords
	foreach my $key (@keywords) {
		$field{$key} = ".";
		if ($graded{$key}) {
			$field{$key} = $1 if ($competencies =~ m#\n\s*$key\b.*?\s{3}(\S[^\n]{0,100})#i);
		} else {
			# $field{$key} = $1 if ($text =~ m#\n$key\b.{0,50}\n([^\n]{1,140})#i);
			$field{$key} = $1 if ($front =~ m#\b$key\b.*?\s{3}(\S.+)#i);
		}

		# allow recommendation and purpose to be longer
		# $field{$key} = $1 if ( ($key eq "Recommendation" || $key eq "Purpose") && $text =~ m#\n.?$key\b.{0,50}\n{1,3}([^\n]+)#i );

		# Exception to catch multiline "prepared for"
		# if ($key eq "Prepared For") {
		# 	if ($text =~ m/Prepared For(.*)Prepared By/si) {;
		# 		$field{$key} = $1;
		# 		$field{$key} =~ s/^\n+//g;
		# 		$field{$key} =~ s/\n+$//;
		# 		$field{$key} =~ s/\n+/; /g;
		# 	}
		# }
		# if ($key eq "Date") {
		# 	$field{$key} = $1 if ($text_d =~ m#\n$key\b.{0,50}\n([^\n]+)#i);
		# }
		print "Keyword: $key \t - $field{$key}\n";
	}



	# output results
	@out = ($line_nr, $path, $file, $client, &clean_short($front), map( $field{$_} , @keywords ) , &clean_short($competencies) ) ;
	$status = $csv_out -> combine(@out);
	$line_out = $csv_out->string();
	print DATA "$line_out\n";

	print STDERR "\n\n\n\n";
}

close FILES;
close DATA;

my $m = join("\n", @missing);

print STDERR "\n\n\nMissing files:\n$m\n";

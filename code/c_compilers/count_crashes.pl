#!/usr/bin/perl -w

use strict;
use Date::Parse;
use Statistics::Test::WilcoxonRankSum;
use Time::Local;

######################################################################

# for swarm, for each crash that happens more than N times, look for
# options that are always present or never present when the bug
# happens

# make swarm/noswarm bar graphs for each compiler

# count total crash instances

######################################################################

my %opts;

sub parse_opts ($) {
    (my $ostr) = shift;
    my @l = split /\s+/, $ostr;

  restart:
    for (my $i=0; $i<scalar(@l); $i++) {
	my $e1 = $l[$i];
	if ($e1 eq "--seed") {
	    splice @l, $i, 2;
	    goto restart;
	}
	if ($e1 eq "--swarm-replay") {
	    splice @l, $i, 1;
	    goto restart;
	}
    }

    for (my $i=0; $i<(scalar(@l)-1); $i++) {
	my $e1 = $l[$i];
	my $e2 = $l[$i+1];
	if ($e2 =~ /^([0-9]+)$/) {
	    $l[$i] = "$e1 $e2";
	    splice @l, $i + 1, 1;
	}
    }

    foreach my $e (@l) {
	$opts{$e}++;
    }

    return \%opts;
}

# turn a verbose compiler failure message into a one-line string that
# uniquely characterizes the error; this is necessary heuristical
sub reduce ($$) {
    (my $compiler, my $fref) = @_;
    my @fail_info = @{$fref};

    foreach my $line (@fail_info) {
	return undef if ($line =~ /out of memory/);
	return undef if ($line =~ /[Nn]o space left/);
    }
    
    foreach my $line (@fail_info) {
	if ($line =~ /Input\/output error/) {
	    return undef;
	}
    }

    if ($compiler =~ /clang/) {
	foreach my $line (@fail_info) {
	    if ($line =~ /Assertion/) {
		return $line;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(error in backend)/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(register type mismatch)/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(operand type mismatch)/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(incorrect register)/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /UNREACHABLE/) {
		return $line;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /signal 9/) {
		return undef;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /signal/) {
		return $line;
	    }
	}
    	foreach my $line (@fail_info) {
	    if ($line =~ /(Incorrect register .*$)/) {
		return $1;
	    }
	}
    } elsif ($compiler =~ /gcc/) {
	foreach my $line (@fail_info) {
	    if ($line =~ /(Segmentation .*)$/) {
		return $1;
	    }	    
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /[Kk]illed/) {
		return undef;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(fatal error: internal consistency failure)/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /error trying to exec/ ||
		$line =~ /cannot exec/) {
		return undef;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(incorrect register)/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /([Ii]nternal compiler .*)$/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(unable to find a register .*)$/) {
		return $1;
	    }	    
	}
    } elsif ($compiler =~ /open64/) {
	foreach my $line (@fail_info) {
	    if ($line =~ /([Ii]nternal compiler .*)$/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /TIMEOUT/) {
		return "";
	    }	    
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(Segmentation .*)$/) {
		return $1;
	    }	    
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /not implemented/) {
		return $line;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /signal 9/ ||
		$line =~ /Out of memory/) {
		return undef;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(Assertion failure .*)$/ ||
		$line =~ /(Error: .*)$/) {
		return $1;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /died due to signal/) {
		return $line;
	    }
	}
	foreach my $line (@fail_info) {
	    if ($line =~ /(Signal: .*)$/) {
		return $1;
	    }
	}
    }	

    ## default case -- no match, report the full error

    my $str = "";
    foreach my $line (@fail_info) {
	$str .= "############ $line\n";
    }

    return $str;
}

my $SNAP_HOURS = 6.0;

my %fails;

sub count_fails ($) {
    (my $i) = @_;
    my $n=0;
    foreach my $k (sort keys %{$fails{$i}}) {
	foreach my $k2 (sort keys %{$fails{$i}{$k}}) {
	    $n++;
	}
    }
    return $n;
}

my %all_fails;
my %ntests;
my %nfails;
my %fcnthist;
my $maxkills = 0;
my $maxkillstr;
my %fail_opts;
my %no_fail_opts;
my %fails_per_time;

sub process ($) {
    (my $i) = @_;
    my $fn = "work${i}/output.txt";
    print "$fn\n";
    open INF, "<$fn" or die;
    my @lines = ();
    my $comp;
    my $fail = 0;
    my $any_fail = 0;
    my %fcnts = ();
    my $num;
    my %o;
    my $start;
    my $next_snap = $SNAP_HOURS;
    my $which_snap = 0;
    while (my $line = <INF>) {
	chomp $line;

	if ($line =~ /timestamp: (.*)$/) {
	    my $t = str2time ($1);
	    if (defined ($start)) {
		# elapsed time in hours
		my $elapsed = ($t - $start) / (60.0 * 60.0);

		if ($elapsed > $next_snap) {
		    $fails_per_time{$which_snap}{$i} = count_fails ($i);
		    $next_snap += $SNAP_HOURS;
		    $which_snap++;
		}

	    } else {
		$start = $t;
	    }
	    next;
	}

	if ($line =~ /Options: (.*) \*/) {
	    %o = %{parse_opts ($1)};
	}

	if ($line =~ /RANDOM PROGRAM ([0-9]+) /) {
	    my $nextnum = $1;
	    $any_fail  = 0;
	    if (defined $num) {
		my $nf = scalar (keys %fcnts);
		$fcnthist{$nf}++;
		if ($nf > $maxkills) {
		    $maxkills = $nf;
		    $maxkillstr = "program $num in file $i kills $nf compilers\n";
		}
	    }
	    $num = $nextnum;
	    %fcnts = ();
	}

	if ($line =~ /--------------- start testing (.*)$/) {
	    $comp = $1;
	    $fail = 0;
	    @lines = ();
	    next;
	}

	if ($line =~ /COMPILER FAILURE/) {
	    $fail = 1;
	    $any_fail = 1;
	}

	if ($line =~ /-------------- stop/) {
	    if ($fail) {
		my $s = reduce ($comp, \@lines);
		if (defined $s) {
		    $fcnts{$comp} = 1;
		    $nfails{$i}++;
		    $fails{$i}{$comp}{$s}++;
		    $all_fails{$comp}{$s}++;
		}
	    }
	    next;
	}

	if ($line =~ /COMPLETED TEST/) {
	    if ($i>=16) {
		foreach my $k (keys %o) {
		    $opts{$k} = 1;
		    if ($any_fail) {
			$fail_opts{$k}++;
		    } else {
			$no_fail_opts{$k}++;
		    }
		}
	    }
	    undef ($comp);
	    $ntests{$i}++;
	    next;
	}

	if ($fail) {
	    push @lines, $line;
	}

    }
    close INF;
}

for (my $i=0; $i<32; $i++ ){
    process ($i);
}

my $all_fail_cnt = 0;
foreach my $k (sort keys %all_fails) {
    print "$k:\n";
    foreach my $k2 (sort keys %{$all_fails{$k}}) {
	print "  $all_fails{$k}{$k2} $k2\n";
	$all_fail_cnt++;
    }
    print "\n";
}

print "distinct bugs across all cores = ${all_fail_cnt}\n";

print "\n\n";
my $savg1 = 0.0;
my $savg2 = 0.0;
my $savg3 = 0.0;
my $nsavg1 = 0.0;
my $nsavg2 = 0.0;
my $nsavg3 = 0.0;
for (my $i=0; $i<32; $i++) {
    my $n =count_fails ($i);
    my $t = $ntests{$i};
    my $f = $nfails{$i};
    print "core $i";
    if ($i >= 16) {
	$savg1 += $n;
	$savg2 += $f;
	$savg3 += $t;
	print "(swarm)";       
    } else {
	$nsavg1 += $n;
	$nsavg2 += $f;
	$nsavg3 += $t;
	print "(no sw)";
    }
    print ": $n distinct failures, $f total failures, $t test cases\n";
}
$nsavg1 /= 16.0;
$nsavg2 /= 16.0;
$nsavg3 /= 16.0;
$savg1 /= 16.0;
$savg2 /= 16.0;
$savg3 /= 16.0;
print "no swarm avg = $nsavg1 unique fails, $nsavg2 total fails, $nsavg3 total test cases\n";
print "swarm avg    = $savg1 unique fails, $savg2 total fails, $savg3 total test cases\n";

sub bynum {
    return $a <=> $b;
}

foreach my $x (sort bynum keys %fcnthist) {
    my $z = $fcnthist{$x};
    print "$z test cases killed $x compilers\n";
}

print $maxkillstr;
print "\n\n";

print "FAIL OPTS:\n";
foreach my $k (sort keys %opts) {
    print "  $k $fail_opts{$k} fails, $no_fail_opts{$k} not-fails\n";
}

# graph of failures vs. time
open SWARM, ">swarm.txt" or die;
open NOSWARM, ">noswarm.txt" or die;
open SWARMAVG, ">swarm_avg.txt" or die;
open NOSWARMAVG, ">noswarm_avg.txt" or die;

print SWARMAVG "0 0\n";
print NOSWARMAVG "0 0\n";

foreach my $snap (sort bynum keys %fails_per_time) {
    my %h = %{$fails_per_time{$snap}};
    my @set1;
    my @set2;
    my $tswarm = 0;
    my $tnswarm = 0;

    my $hours = int ((1+$snap) * $SNAP_HOURS);

    print "snap $snap : ";
    for (my $i=0; $i<32; $i++) {
	my $x = $h{$i};
	next unless defined $x;
	if ($i<16) {
	    push @set1, $x;
	    print NOSWARM "$hours $x\n";
	    $tnswarm += $x;
	} else {
	    push @set2, $x;
	    print SWARM "$hours $x\n";
	    $tswarm += $x;
	}
    }

    print SWARMAVG "$hours ".$tswarm/16.0."\n";
    print NOSWARMAVG "$hours ".$tnswarm/16.0."\n";

    my $wilcox_test = Statistics::Test::WilcoxonRankSum->new();
    $wilcox_test->load_data(\@set1, \@set2);
    my $prob = $wilcox_test->probability();
    print $wilcox_test->probability_status();
    print "\n";
}
close SWARM;
close NOSWARM;


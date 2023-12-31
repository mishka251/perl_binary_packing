#!/usr/bin/perl
use strict;
use warnings;
use File::Path qw(mkpath);

use JSON::MaybeXS qw(encode_json decode_json);
use Test;

use Test::Simple tests => 127;

sub parse_binary_from_json {
    my $bytes = shift;
    my $result = "";
    foreach my $byte ((@{$bytes})) {
        my $byte_hex = hex($byte);
        my $byte_str = pack('C', $byte_hex);
        $result .= $byte_str
    }
    return $result;
}

sub format_binary {
    my $bytes = shift;
    my $result = "";
    for (my $i = 0; $i < length($bytes); $i++) {
        my $byte = substr($bytes, $i);
        my $byte_str = unpack('C', $byte);
        my $byte_hex = sprintf('%x', $byte_str);
        $result .= "0x$byte_hex "
    }
    return $result;
}

sub parse_json_values {
    my @expected_unpacked_objects = @_;
    my @expected_unpacked;
    foreach my $expected_object (@expected_unpacked_objects) {
        my $raw_expected_value = $expected_object->{value};
        my $expected_value = $raw_expected_value;
        if ($expected_object->{type} eq "bytes") {
            my $find = "0x00";
            my $replace = "\0";
            $expected_value =~ s/$find/$replace/g;
        }
        push @expected_unpacked, $expected_value;
    }
    return @expected_unpacked;
}

my $test_filename = "test_data.json";
open my $input_file, "<", $test_filename or die;
my $test_cases_str = '';
while (<$input_file>) {
    $test_cases_str .= $_;
}
close($test_filename);

my $test_cases = decode_json($test_cases_str);

if (defined($test_cases->{test_pack})) {
    my $pack_test_cases = $test_cases->{test_pack};
    foreach my $pack_test_case ((@{$pack_test_cases})) {
        my $format = $pack_test_case->{format};
        my @to_pack_objects = @{$pack_test_case->{to_pack}};
        my @to_pack = parse_json_values(@to_pack_objects);


        my $packed = pack($format, @to_pack);
        my $expected = $pack_test_case->{expected_packed};

        $expected = parse_binary_from_json($expected);

        my $to_pack_view = '[' . join(', ', map {"\"$_\""} @to_pack) . ']';
        my $expected_view = format_binary($expected);
        my $packed_view = format_binary($packed);
        my $test_message = "Checking: pack($format, $to_pack_view)/ Expected: \"$expected_view\", actual: \"$packed_view\"";
        ok($packed eq $expected, $test_message);
    }
}


if (defined($test_cases->{test_unpack})) {
    my $unpack_test_cases = $test_cases->{test_unpack};
    foreach my $unpack_test_case ((@{$unpack_test_cases})) {
        my $format = $unpack_test_case->{format};
        my $to_unpack_hexes = $unpack_test_case->{to_unpack};
        # my $packed = pack($format, @to_pack);
        my @expected_unpacked_objects = @{$unpack_test_case->{expected_unpacked}};
        my @expected_unpacked = parse_json_values(@expected_unpacked_objects);
        my $to_unpack = parse_binary_from_json($to_unpack_hexes);
        # $expected = parse_binary_from_json($expected);

        my @actual_unpacked = unpack($format, $to_unpack);

        my $to_unpack_view = '[' . join(', ', map {"\"$_\""} @{$to_unpack_hexes}) . ']';
        # my $expected_view = format_binary($expected);
        # my $packed_view = format_binary($packed);
        my $test_message = "Checking: unpack($format, $to_unpack_view)/ Expected: \"@expected_unpacked\", actual: \"@actual_unpacked\"";
        ok(@actual_unpacked ~~ @expected_unpacked, $test_message);
    }
}

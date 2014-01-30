#!/usr/bin/python

import optparse, sys, re

#----------------------------------------
#---Command line parser and arguments----
#----------------------------------------

desc="""This script is used to merge two gff3 files.  The main purpose is to merge a MAKER gff3 file with another secondary gff3 file.  However, the primary gff3 file does not need to be output from MAKER.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)

parser.add_option('-p', help='MANDATORY OPTION: Input primary gff file--should be primary gff3 file from MAKER output, but not necessarily.  FASTA sequences as end of file are permitted.', dest='primary_input', action='store')
parser.add_option('-s', help='MANDATORY OPTION: Input secondary gff file--should be any properly formatted gff3 file that contains information about the same contigs as in primary gff file.  FASTA sequences as end of file are NOT permitted.', dest='secondary_input', action='store')
parser.add_option('-o', help='MANDATORY OPTION: Absolute path to output--Example:/path/to/output/file.gff', dest='output', action='store')
(opts, args) = parser.parse_args()

mandatory_options = ['primary_input','secondary_input','output']
for m in mandatory_options:
# Making sure all mandatory options appeared
    if not opts.__dict__[m]:
        print "Mandatory option is missing!\n"
        parser.print_help()
        sys.exit()
        
#-----------------------------
#---------FUNCTIONS-----------
#-----------------------------

def gff3_create_dictionary1(file_in):
    with open(file_in) as f:
        entries = f.read().split("##FASTA")
        lines = entries[0].split("\n")
        for x in lines:
            field = x.split("\t")
            gff3_dictionary1[x]=field[0]
        f.close()

def gff3_create_dictionary2(file_in):
    with open(file_in) as f:
        entries = f.read().split("##FASTA")
        lines = entries[0].split("\n")
        for x in lines:
            field = x.split("\t")
            gff3_dictionary2[x]=field[0]
        f.close()

#-----------------------------
#------------MAIN-------------
#-----------------------------
gff3_dictionary1 = {}   # Create empty dictionary for primary input
gff3_dictionary2 = {}   # Create empty dictionary for secondary input
gff3_create_dictionary1(opts.primary_input)   # Populate dictionary for primary input
gff3_create_dictionary2(opts.secondary_input)     # Populate dictionary for secondary input

output = open(opts.output,'r+')
output.write("##gff-version 3"+"\n")

for key1,value1 in gff3_dictionary1.iteritems():    # If contig name appears in both dictionaries, print the lines that correspond to those entries.
    output.write(key1+"\n")
    for key2,value2 in gff3_dictionary2.iteritems():
        if gff3_dictionary1[key1]==gff3_dictionary2[key2]:
            output.write(key2+"\n")

with open(opts.primary_input,"r") as f:   # Add FASTA information to the end of gff3 file
    boolean = False
    for line in f.readlines():
        if re.search("##FASTA",line):
            boolean = True
        if boolean is True and not re.search(line,output.readlines()):
            output.write(line)





    

      
      
      

#!/usr/bin/python

import optparse, sys, os
from statgps_pipeline_variables import *
from statgps_functions import blast_xml_to_gff3

#-------------------------------------------------------------------------------------------
#----------------------------Command line parser and arguments------------------------------
#-------------------------------------------------------------------------------------------
desc="""This script is used to predict ncRNA regions in genomic fasta sequences.  Input must be a single-fasta or multi-fasta file.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)
parser.add_option('--short', help="Quick ncRNA prediction---uses tRNAscan and PORTRAIT", action="store_true", dest="short")
parser.add_option('--long', help="Lengthy ncRNA prediction---uses BLAST against rRNA database in addition to tRNAscan and \
                                PORTRAIT--only use if time is not an issue", action="store_true", dest="long")
parser.add_option('-i', help='MANDATORY OPTION: Input fasta sequence - should be multi-fasta or single-fasta file--Example: /path/to/fasta.fa', 
                            dest='input', action='store')
parser.add_option('-o', help='MANDATORY OPTION: Output directory (example: /path/to/output)', dest='master_output', action='store')
parser.add_option('-n', help='Number of hits to report in gff3 annotation file from BLAST output (only applicable for --long analysis)', 
                            dest='number_hits', action='store', default=50)
parser.add_option('-c', help='Number of cores to use for BLAST--Default=1', dest='cores', default=1, action='store')
(opts, args) = parser.parse_args()

mandatory_options = ['input','master_output']
for m in mandatory_options:
# Making sure all mandatory options appeared
    if not opts.__dict__[m] or (not opts.long and not opts.short):
        print "\nMandatory option is missing!\n"
        parser.print_help()
        sys.exit()
    if opts.short is True and opts.long is True:
        print "\nYou may only choose --short or --long at command line.  All short analyses will be included in the --long parameter option anyway.\n"
        parser.print_help()
        sys.exit()

    
#-------------------------------------------------------------------------------------------
#----------------------------ncRNA Prediction (Short and Long)---------------------------------------
#-------------------------------------------------------------------------------------------

try:
    os.system("mkdir "+opts.master_output+"/ncRNA_prediction")
except:
    print "Failed to create output directory: "+opts.master_output

try:    
    if opts.short is True or opts.long is True:
        try:
            os.system("mkdir "+opts.master_output+"/ncRNA_prediction/PORTRAIT_output")
        except:
            print "Failed to create output directory for PORTRAIT."
        try:
            print "\nRUNNING PORTRAIT FOR ncRNA PREDICTION--PLEASE WAIT\n"
            os.chdir(PORTRAIT_DIRECTORY)
            os.system("sudo ./"+PORTRAIT_EXE_NAME+" -i "+opts.input)
        except:
            print "Failed to run PORTRAIT.  Try to run as root with sudo or manually edit the command in this script.  \
                    Check to make sure you have defined the paths to the variables listed in Solazyme_Pipeline_Variables.py that are relevant to this script."
        try:
            os.system("mv "+opts.input+"_* "+opts.master_output+"/ncRNA_prediction/PORTRAIT_output")
            os.system("mv "+opts.input+".log "+opts.master_output+"/ncRNA_prediction/PORTRAIT_output")
        except:
            print "Failed to move PORTRAIT output to proper output directory.  PORTRAIT output may be in the same directory as the input file."

        try:
            os.system("mkdir "+opts.master_output+"/ncRNA_prediction/tRNAscan_output")
        except:
            print "Failed to create output directory for tRNAscan"
        try:
            print "\nRUNNING tRNAscan FOR tRNA PREDICTION--PLEASE WAIT\n"
            os.chdir(TRNASCAN_DIRECTORY)
            os.system(TRNASCAN_EXE_NAME+" "+opts.input+" -o "+opts.master_output+"/ncRNA_prediction/tRNAscan_output/tRNAscan_output.txt")
            print "\nAll short analyses for ncRNA prediction are complete.  Please view: "+opts.master_output+"/ncRNA_prediction for summary report and data"
        except:
            print "Failed to run tRNAscan.  Check to make sure you have defined the paths to the variables listed in Solazyme_Pipeline_Variables.py \
                    that are relevant to this script."
            

#-------------------------------------------------------------------------------------------
#----------------------------ncRNA Prediction (Long)---------------------------------------
#-------------------------------------------------------------------------------------------

    if opts.long is True and opts.number_hits:
        try:
            os.system("mkdir "+opts.master_output+"/ncRNA_prediction/BLAST_output")
        except:
            print "Failed to create output directory for BLAST"
        try:
            print "\nRUNNING BLAST FOR ncRNA PREDICTION--PLEASE WAIT\n"
            #os.system(BLAST_EXE_DIRECTORY+"blastn -query "+opts.input+" -db "+BLAST_DATABASE_DIRECTORY+"ncRNA -out "+opts.master_output+"/ncRNA_prediction/BLAST_output/blastn_ncRNA_analysis.xml -outfmt 5 -evalue 0.0001")
            os.system(BLAST_EXE_DIRECTORY+"blastn -db "+BLAST_DATABASE_DIRECTORY+"ncRNA -query "+opts.input+" -out "+opts.master_output+"/ncRNA_prediction/BLAST_output/blastn_ncRNA_analysis.xml -evalue 0.0001 -outfmt 5 -num_threads "+opts.cores)
            print "\nAll long analyses for ncRNA prediction are complete.  Please view: "+opts.master_output+"/ncRNA_prediction for summary report and data"
        except:
            print "Failed to run BLAST.  Check to make sure you have defined the paths to the variables listed in Solazyme_Pipeline_Variables.py that are relevant to this script.  If everything seems correct, consult README"
        try:    
            blast_xml_to_gff3(opts.master_output+"/ncRNA_prediction/BLAST_output/blastn_ncRNA_analysis.xml",opts.master_output+"/ncRNA_prediction/BLAST_output/blastn_ncRNA_analysis.gff","blastn")
        except:
            print "Failed to parse BLAST output.  Check to see if "+opts.master_output+"/ncRNA_prediction/BLAST_output/blastn_ncRNA_analysis.xml was created."
        

except:
    "\nncRNA_Prediction.py has failed.  Please see stdout errors for details."

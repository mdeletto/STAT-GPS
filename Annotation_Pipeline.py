#!/usr/bin/python

import optparse, sys, os, re
from statgps_pipeline_variables import *

#-------------------------------------------------------------------------------------------
#----------------------------Command line parser and arguments------------------------------
#-------------------------------------------------------------------------------------------

parser = optparse.OptionParser()

group1 = optparse.OptionGroup(parser, "Analysis Type",
                    "Please indicate analysis type.  Choose --all_analyses if you would like to run the entire pipeline.  NOTE: Choosing individual analyses requires different dependencies for input.  If you choose this option to run --all_analyses, the following parameters are required: -o, -f, -t, --velvet_input")
group1.add_option('--assembly', help="Start Velvet assembly--requires -f, -t, -i flags", action="store_true", dest="assembly")
group1.add_option('--annotation', help="Start MAKER annotation--requires -f, -t, -i flags", action="store_true", dest="annotation")
group1.add_option('--interproscan', help="Start INTERPROSCAN to add more annotations (requires --interproscan_input, -o flags", action="store_true", dest="interproscan")
group1.add_option('--blast', help="Start local BLAST alignment (requires --blast_input, -o flags)", action="store_true", dest="blast")
group1.add_option("--all_analyses", help="Run entire assembly, annotation, and blastp processes", action="store_true",dest="all")
parser.add_option_group(group1)

group2 = optparse.OptionGroup(parser, "General options")
group2.add_option('-c', help='Number of cores to use--Default=1', dest='cores', default=1, action='store')
group2.add_option('-o', help='MANDATORY OPTION: Output directory (example: /path/to/output)',
                  dest='master_output', action='store')
parser.add_option_group(group2)

group3 = optparse.OptionGroup(parser, "Assembly options")
group3.add_option('-f', help='Read format <fasta, fastq, fasta.gz, fastq.gz, eland, gerald>--Default=fasta',
                  dest='velvet_input_format', default='fasta', action='store')
group3.add_option('-t', help='Read category <short, shortPaired, short2, shortPaired2, long>--Default=short',
                  dest='velvet_seq_category', default='short', action='store')
group3.add_option('--velvet_input', help='Input file--please indicate path to file',
                  dest='velvet_input', action='store')
parser.add_option_group(group3)

group4 = optparse.OptionGroup(parser, "Annotation options","To specify specific MAKER annotation options, please edit the maker.ctl files in maker/bin/")
parser.add_option_group(group4)

group5 = optparse.OptionGroup(parser, "Interproscan options")
group5.add_option('--interproscan_input', help='Input file (please indicate path to file--must be protein FASTA file)',
                  dest='interproscan_input', action='store')
group5.add_option('--gff_file', help='gff file to update with interproscan annotations (please indicate path to file--must be protein FASTA file)',
                  dest='gff', action='store')
parser.add_option_group(group5)

group6 = optparse.OptionGroup(parser, "BLAST options")
group6.add_option('--blast_input', help='Input file--please indicate path to file--must be FASTA file',
                  dest='blast_input', action='store')
group6.add_option('--blast_input_type', help='Type of fasta sequence <nucl or prot>',
                  dest='blast_input_type', action='store')
group6.add_option('-d', help='BLAST database to be used during blastp analysis <swissprot or trembl>--Default=swissprot',
                  dest='db_type', default='swissprot', action='store')                  
group6.add_option('-r', help='Remote or local blastp analysis <Y or N>--Default=N---NOT SUGGESTED FOR QUERIES LARGER THAN 200 SEQUENCES',
                  dest='remote', default='N', action='store')  
parser.add_option_group(group6)

(opts, args) = parser.parse_args()
mandatory_options = ['master_output']


def mandatory_arguments():
    for m in mandatory_options:
        # Making sure all mandatory options appeared
        if not opts.__dict__[m]:
            print "Mandatory option is missing!\n"
            parser.print_help()
            sys.exit()

#---------------------------------------------------------------------------------
#-----------------------------Annotation Pipeline---------------------------------
#---------------------------------------------------------------------------------

try:
    os.system("mkdir "+opts.master_output+"/annotation.pipeline")  # Store Output in new directory
except:
    print str(opts.master_output)+"/annotation.pipeline cannot be created or already exists.  Proceeding with next steps."
try:
    if opts.assembly is True and not opts.all:
        mandatory_options = ['velvet_input_format', 'velvet_seq_category', 'velvet_input', 'master_output']
        mandatory_arguments()
        # De-novo Assembly
        print "Starting genome assembly using Velvet..."
        os.chdir(VELVETOPTIMISER_DIRECTORY)
        os.system(VELVETOPTIMISER_EXE+" -t "+opts.cores+" -f '-"+opts.velvet_input_format+" -"+opts.velvet_seq_category+" "+opts.velvet_input+"'")
        print "Moving your data to specified directory..."
        os.system("mv auto_data_* "+opts.master_output+"/annotation.pipeline/velvet.output")
        # Characterize the assembly
        print "Genome assembly has finished..."
        os.chdir(CONTIG_STATS_DIRECTORY)
        print "Characterizing the assembly and calculating statistics..."
        os.system("perl contig-stats.pl "+opts.master_output+"/annotation.pipeline/velvet.output/contigs.fa >> "+opts.master_output+"/annotation.pipeline/velvet.output/contig_stats.txt")
except:
    print "Genome assembly failed.  Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions."
try:    
    if opts.annotation is True and not opts.all:
        mandatory_options = ['master_output']
        mandatory_arguments()
        # Run MAKER annotation
        print "Starting genome annotation using MAKER..."
        os.chdir(MAKER_DIRECTORY)
        os.system(MAKER_EXE+" -base contigs")
        print "Moving your data to specified directory..."
        os.system("mv contigs.maker.output "+opts.master_output+"/annotation.pipeline/maker.output")
        os.system("cat "+opts.master_output+"/annotation.pipeline/maker.output/*datastore/*/*/*/*.augustus_masked.proteins.fasta >> "+opts.master_output+"/annotation.pipeline/proteins.fasta")
        os.system("gff3_merge -d "+opts.master_output+"/annotation.pipeline/maker.output/*index.log")
        os.system("mv contigs.all.gff "+opts.master_output+"/annotation.pipeline/contigs.all.gff")
        print "MAKER annotation is complete..."
        try:
            with open(opts.master_output+"/annotation.pipeline/proteins.fasta","r") as f:
                f.close()
        except IOError:
            print "Augustus did not predict any proteins for your sequences. No protein annotations will be included in your MAKER annotations. To include ab initio gene predictions, a training set from ESTs or proteins is required."
        # Merge MAKER gff3 files for each contig
except:
    print "Genome annotation failed.  Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions."   
try:
    if opts.interproscan is True and not opts.all:
        mandatory_options = ['interproscan_input', 'gff', 'master_output']
        mandatory_arguments()
        # Run Interproscan w/ GO terms and IPR annotation
        os.chdir(INTERPROSCAN_DIRECTORY)
        print "Starting INTERPROSCAN on your proteins..."
        os.system(INTERPROSCAN_EXE+" -i "+opts.interproscan_input+" -goterms -iprlookup -b interproscan.output -pa")
        print "Moving your data to specified directory..."
        os.system("mv interproscan.output.* "+opts.master_output+"/annotation.pipeline/interproscan.output")
        # Map Interproscan data to MAKER gff3 file
        os.chdir(MAKER_DIRECTORY)
        print "Updating your MAKER gff file with INTERPROSCAN annotations"
        os.system("ipr_update_gff "+opts.gff+" "+opts.master_output+"/annotation.pipeline/interproscan.output/*.tsv")
        print "INTERPROSCAN annotations are complete..."
except:
    print "INTERPROSCAN protein annotation has failed. Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions."   
try:
    if opts.blast is True and not opts.all:
        mandatory_options = ['db_type', 'blast_input','blast_input_type', 'master_output']
        mandatory_arguments()
        # Run blastp analysis against local database (tabular output) with multiple threads
        print "Running blast on your input sequence..."
        if re.search("N", opts.remote) and re.search("prot",opts.blast_input_type):
            os.system(BLAST_EXE_DIRECTORY+"blastp -db "+BLAST_DATABASE_DIRECTORY+opts.db_type+" -query "+opts.blast_input+" -out "+opts.master_output+"/annotation.pipeline/blastp_analysis.xml -evalue 0.0001 -outfmt 5 -num_threads "+opts.cores)
        if not re.search("N", opts.remote) and re.search("prot",opts.blast_input_type):
            os.system(BLAST_EXE_DIRECTORY+"blastp -db "+BLAST_DATABASE_DIRECTORY+opts.db_type+" -query "+opts.blast_input+" -out "+opts.master_output+"/annotation.pipeline/blastp_analysis.xml -evalue 0.0001 -outfmt 5 -remote -num_threads "+opts.cores)
        if re.search("N", opts.remote) and re.search("nucl",opts.blast_input_type):
            os.system(BLAST_EXE_DIRECTORY+"blastx -db "+BLAST_DATABASE_DIRECTORY+opts.db_type+" -query "+opts.blast_input+" -out "+opts.master_output+"/annotation.pipeline/blastx_analysis.xml -evalue 0.0001 -outfmt 5 -num_threads "+opts.cores)
        if not re.search("N", opts.remote) and re.search("nucl",opts.blast_input_type):
            os.system(BLAST_EXE_DIRECTORY+"blastx -db "+BLAST_DATABASE_DIRECTORY+opts.db_type+" -query "+opts.blast_input+" -out "+opts.master_output+"/annotation.pipeline/blastx_analysis.xml -evalue 0.0001 -outfmt 5 -remote -num_threads "+opts.cores)
        os.chdir(MAKER_DIRECTORY)
        print "Updating your MAKER gff file with blast annotations..."
        # Annotate MAKER gff3 file with blastp output
        if re.search("swissprot", opts.db_type):
            os.system("maker_functional_gff "+BLAST_DATABASE_DIRECTORY+"uniprot_sprot.fasta "+opts.master_output+"/annotation.pipeline/blastp_analysis.txt "+opts.master_output+"/annotation.pipeline/contigs.all.gff")
        else:
            os.system("maker_functional_gff "+BLAST_DATABASE_DIRECTORY+"uniprot_trembl.fasta "+opts.master_output+"/annotation.pipeline/blastp_analysis.txt "+opts.master_output+"/annotation.pipeline/contigs.all.gff")
except:
    print "BLAST failed.  Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions." 
              
try:   
    if opts.all is True:
        mandatory_options = ['velvet_input_format', 'velvet_seq_category', 'velvet_input', 'master_output']
        mandatory_arguments()
        try:
            # De-novo Assembly
            os.chdir(VELVETOPTIMISER_DIRECTORY)
            print "Starting genome assembly using Velvet..."
            os.system(VELVETOPTIMISER_EXE+" -t "+opts.cores+" -f '-"+opts.velvet_input_format+" -"+opts.velvet_seq_category+" "+opts.velvet_input+"'")
            print "Moving your data to specified directory..."
            os.system("mv auto_data_* "+opts.master_output+"/annotation.pipeline/velvet.output")
            # Characterize the assembly
            os.chdir(CONTIG_STATS_DIRECTORY)
            print "Characterizing the assembly and calculating statistics..."
            os.system("perl contig-stats.pl "+opts.master_output+"/annotation.pipeline/velvet.output/contigs.fa >> "+opts.master_output+"/annotation.pipeline/velvet.output/contig_stats.txt")
        except:
            print "Genome assembly failed.  Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions."
        try:
            # Run MAKER annotation
            os.chdir(MAKER_DIRECTORY)
            print "Starting genome annotation using MAKER..."
            os.system(MAKER_EXE+" -base contigs")
            print "Moving your data to specified directory..."
            os.system("mv contigs.maker.output "+opts.master_output+"/annotation.pipeline/maker.output")
            os.system("cat "+opts.master_output+"/annotation.pipeline/maker.output/*datastore/*/*/*/*.augustus_masked.proteins.fasta >> "+opts.master_output+"annotation.pipeline/proteins.fasta")
            print "MAKER annotation is complete..."
            try:
                with open(opts.master_output+"/annotation.pipeline/proteins.fasta","r") as f:
                    f.close()
            except IOError:
                print "Augustus did not predict any proteins for your sequences. No protein annotations will be included in your MAKER annotations. To include ab initio gene predictions, a training set from ESTs or proteins is required."
        # Merge MAKER gff3 files for each contig
        except:
            print "Genome annotation failed.  Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions."   
        try:
            # Run Interproscan w/ GO terms and IPR annotation
            os.chdir(INTERPROSCAN_DIRECTORY)
            print "Starting INTERPROSCAN on your proteins..."
            os.system(INTERPROSCAN_EXE+" -i "+opts.master_output+"/annotation.pipeline/proteins.fasta -goterms -iprlookup -b interproscan.output -pa")
            print "Moving your data to specified directory..."
            os.system("mv interproscan.output.* "+opts.master_output+"/annotation.pipeline/interproscan.output")
            # Merge MAKER gff3 files for each contig
            os.chdir(MAKER_DIRECTORY)
            print "Updating your MAKER gff file with INTERPROSCAN annotations"
            os.system("gff3_merge -d "+opts.master_output+"/annotation.pipeline/maker.output/*index.log")
            os.system("mv contigs.all.gff "+opts.master_output+"/annotation.pipeline/contigs.all.gff")
            # Map Interproscan data to MAKER gff3 file
            os.system("ipr_update_gff "+opts.master_output+"/annotation.pipeline/contigs.all.gff "+opts.master_output+"/annotation.pipeline/interproscan.output/*.tsv")
            print "INTERPROSCAN annotations are complete..."
        except:
            print "INTERPROSCAN protein annotation has failed. Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions."   
        
        try:
            # Run blastp analysis against local database (tabular output) with multiple threads
            print "Running blast on your input sequence..."
            if re.search("N", opts.remote):
                os.system(BLAST_EXE_DIRECTORY+"blastp -db "+BLAST_DATABASE_DIRECTORY+opts.db_type+" -query "+opts.master_output+"/annotation.pipeline/proteins.fasta -out "+opts.master_output+"/blastp_analysis.xml -evalue 0.0001 -outfmt 5 -num_threads "+opts.cores)
            else:
                os.system(BLAST_EXE_DIRECTORY+"blastp -db "+BLAST_DATABASE_DIRECTORY+opts.db_type+" -query "+opts.master_output+"/annotation.pipeline/proteins.fasta -out "+opts.master_output+"/blastp_analysis.xml -evalue 0.0001 -outfmt 5 -remote -num_threads "+opts.cores)
            # Annotate MAKER gff3 file with blastp output
            os.chdir(MAKER_DIRECTORY)
            print "Updating your MAKER gff file with blast annotations..."
            if re.search("swissprot", opts.db_type):
                os.system("maker_functional_gff "+BLAST_DATABASE_DIRECTORY+"/uniprot_sprot.fasta "+opts.master_output+"/annotation.pipeline/blastp_analysis.txt "+opts.master_output+"/annotation.pipeline/contigs.all.gff")
            else:
                os.system("maker_functional_gff "+BLAST_DATABASE_DIRECTORY+"/uniprot_trembl.fasta "+opts.master_output+"/annotation.pipeline/blastp_analysis.txt "+opts.master_output+"/annotation.pipeline/contigs.all.gff")
        except:
            print "BLAST failed.  Please check to make sure all flags and variables have been set properly.  Please see the README detailed installation instructions."     
        print "\n\nSOLAZYME ANNOTATION PIPELINE IS COMPLETE\n\n.  If no errors were reported during the process, you may view your results at "+str(opts.master_output)+"/annotation.pipeline"
except:
    print "SOLAZYME ANNOTATION PIPELINE FAILED--Please make sure all flags and variables are set properly"


#----------------------------------------------------------------
#----------------------END OF SCRIPT-----------------------------
#----------------------------------------------------------------

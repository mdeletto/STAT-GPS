#!/usr/bin/python


import optparse
from statgps_functions import *

#-------------------------------------------------------------------------------------------
#----------------------------Command line parser and arguments------------------------------
#-------------------------------------------------------------------------------------------
desc="""This script is used to remotely send protein sequences to SWISS-MODEL's automated homology pipeline server.  Your input may be either a single fasta-formatted protein sequence
or a directory containing fasta-formatted protein sequences.  Please note that if you choose to indicate a directory, all files in the directory will be processed.  If you want to use a single fasta-formatted
file containing concatenated protein sequences, you must use a system utility to split these into individual fasta files (i.e. one header, one sequence).

In order to receive the models produced by SWISS-MODEL, you must create an account with SWISS-MODEL.  Before using this script, make sure to login on SWISS-MODEL's website.  Your results are available
in both your SWISS-MODEL Workspace and your SWISS-MODEL account email.  Each project will have name set as the fasta header of the protein sequence you input.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)


parser.add_option('-s', help='Single Input fasta -- EXAMPLE: /path/to/fasta.fa', dest='single', action='store')
parser.add_option('-m', help='Multiple fasta files -- indicate directory path -- NOTE: Every file in this directory will be processed -- EXAMPLE: /path/to/fasta/directory', dest='multiple', action='store')
parser.add_option('-c', help='Single concatenated fasta file containing multiple sequences', dest='concatenated', action='store')
parser.add_option('-e', help='SWISS-MODEL email login -- EXAMPLE: user@email.com', dest='email', action='store')
(opts, args) = parser.parse_args()

#-------------------------------------------------------------------------------------------
#-----------------------------------------MAIN----------------------------------------------
#-------------------------------------------------------------------------------------------


if opts.single and opts.multiple and opts.concatenated:
    print "\nPROGRAM IS NOT OPTIMIZED FOR SIMULTANEOUS SINGLE FILE AND DIRECTORY INPUTS.  If you would like to enable this option, edit the source code AT YOUR OWN RISK to utilize individual functions in this script."
elif opts.concatenated and opts.email:
    homology_modeling_concat_fasta(opts.concatenated,opts.email)
elif opts.single and opts.email:
    homology_modeling_single_fasta(opts.single,opts.email)
elif opts.multiple and opts.email:
    homology_modeling_multiple_fasta(opts.multiple,opts.email)
else:
    print "INPUT ERROR - PLEASE ENTER YOUR FILE OR DIRECTORY, AS WELL AS YOUR SWISS-MODEL ACCOUNT EMAIL"
         
print "\nSuccessfully submitted to SWISS-Model Server! Please check your email or your account at SWISS-MODEL to view models for your sequences.  Please realize this may take some time for multiple sequence queries."

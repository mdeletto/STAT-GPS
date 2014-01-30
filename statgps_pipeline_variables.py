#!/usr/bin/python

#---------PLEASE INDICATE ABSOLUTE PATHS FOR THE FOLLOWING VARIABLES-------------#
# These variables indicate the directories of all tools used in this pipeline
# It is also suggested that you make all tools executable
# See the README.txt for more information

#----------------------------------------------------
#-------------UNIVERSAL VARIABLES--------------------
#-----(required for all scripts in package)----------
#----------------------------------------------------

BLAST_DATABASE_DIRECTORY = '/home/mike/bin/BLAST_Databases/'
# Should contain formatted blast database files and unformatted database fasta files
BLAST_EXE_DIRECTORY = '/usr/bin/'
# Should contain BLAST executables, specifically blastp


#----------------------------------------------------
#-------------ANNOTATION PIPELINE VARIABLES----------
#----------------------------------------------------
#  Annotation Pipeline utilizes the BLAST_DATABASE_DIRECTORY and BLAST_EXE_DIRECTORY variables above
#  Please set those variables before attempting to use the Solazyme_Annotation_Pipeline.py script for pathway analysis


VELVETOPTIMISER_DIRECTORY = '/home/mike/bin/velvet_1.2.10/contrib/VelvetOptimiser-2.2.4/'
# Directory should contain VelvetOptimiser.pl, velveth, and velvetg
CONTIG_STATS_DIRECTORY = '/usr/bin/contig-stats.pl'
# Included in distribution
MAKER_DIRECTORY = '/home/mike/bin/maker/bin/'
# Should contain maker and all of its supporting scripts
INTERPROSCAN_DIRECTORY = '/home/mike/bin/interproscan-5-RC6/'
# Should contain interproscan.sh

#-----------------------------------------------------
#----------------PATHWAY MAPPING VARIABLES------------
#-----------------------------------------------------

#  Pathway mapping utilizes the BLAST_DATABASE_DIRECTORY and BLAST_EXE_DIRECTORY variables above
#  Please set those variables before attempting to use the Pathway_Mapping.py script for pathway analysis

KOBAS_EXE_DIRECTORY = '/home/mike/bin/kobas/scripts/'
# Should contain KOBAS's annotate.py and identify.py scripts

#-----------------------------------------------------
#----------------ncRNA prediction---------------------
#-----------------------------------------------------

TRNASCAN_DIRECTORY = '/home/mike/bin/'
TRNASCAN_EXE_NAME = 'trnascan-1.4'
PORTRAIT_DIRECTORY = '/home/mike/bin/Portrait/portrait-1.1/'
PORTRAIT_EXE_NAME = 'portrait'

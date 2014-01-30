#!/usr/bin/python

import optparse, sys, os, re, datetime, mechanize

from statgps_pipeline_variables import BLAST_EXE_DIRECTORY, BLAST_DATABASE_DIRECTORY, KOBAS_EXE_DIRECTORY

#-------------------------------------------------------------------------------------------
#----------------------------Command line parser and arguments------------------------------
#-------------------------------------------------------------------------------------------
desc="""This script is used to assign a protein multi-fasta or single-fasta file to appropriate KO terms based on existing KEGG Ontology (KO) peptides.  If a pathway exists for a specific KO hit, the pathway
will be downloaded automatically.  Internet connection is required.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)

parser.add_option('-i', help='MANDATORY OPTION: Input fasta sequence - should be multi-fasta or single-fasta file--Example: fasta.fa', dest='input', action='store')
parser.add_option('-c', help='Number of cores to use--Default=1', dest='cores', default=1, action='store')
parser.add_option('-b', help='Base output name for results--no filetype extensions', dest='output', action='store')
parser.add_option('-o', help='MANDATORY OPTION: Output directory (example: /path/to/output)', dest='master_output', action='store')
(opts, args) = parser.parse_args()

mandatory_options = ['input','master_output']
for m in mandatory_options:
# Making sure all mandatory options appeared
    if not opts.__dict__[m]:
        print "Mandatory option is missing!\n"
        parser.print_help()
        sys.exit()

#-------------------------------------------------------------------------------------------
#----------------------------KO Assignment and Pathway Retrieval----------------------------
#-------------------------------------------------------------------------------------------
try:
    os.system("mkdir "+opts.master_output+"/pathway_analysis")  # Store Output in new directory
except:
    print "Failed to create output directory"

#-------------------BLASTP AGAINST KEGG ONTOLOGY (KO PEPTIDES)------------------------------
try:
    os.system(BLAST_EXE_DIRECTORY+"blastp -db "+BLAST_DATABASE_DIRECTORY+"ko.pep.fasta -query "+opts.input+" -out "+opts.master_output+"/pathway_analysis/blastp_ko_analysis_"+str(datetime.date.today())+".txt -evalue 0.0001 -outfmt 7 -num_threads "+opts.cores)
except:
    print "Failed to run blastp against KO peptides.  Check to make sure you have defined the paths to the variables listed in Solazyme_Pipeline_Variables.py that are relevant to this script."

#-------------------KOBAS ANNOTATION PARSING OF BLASTP OUTPUT-------------------------------
try:
    if opts.output is True:
        os.system(KOBAS_EXE_DIRECTORY+"annotate.py -t blastout:tab -i "+opts.master_output+"/pathway_analysis/blastp_ko_analysis_"+str(datetime.date.today())+".txt -o "+opts.master_output+"/pathway_analysis/"+opts.output+".txt")
    else:
        os.system(KOBAS_EXE_DIRECTORY+"annotate.py -t blastout:tab -i "+opts.master_output+"/pathway_analysis/blastp_ko_analysis_"+str(datetime.date.today())+".txt -o "+opts.master_output+"/pathway_analysis/kobas_output_"+str(datetime.date.today())+".txt")
except:
    print "Failed to run KOBAS on blastp output.  Please check parameters"

#-------------------ONLINE PATHWAY MAP RETRIEVAL FROM KEGG----------------------------------

try:
    if opts.output is True:
        fh = open(opts.master_output+"/pathway_analysis/"+opts.output+".txt", 'r')
    else:
        fh = open(opts.master_output+"/pathway_analysis/kobas_output_"+str(datetime.date.today())+".txt", 'r')
except:
    print "Failed to open KOBAS output for online pathway map retrieval."
try:
    filelines = fh.readlines()
    for x in filelines:
        line = x.strip("\n")  # Remove new line characters
        if re.search("http://",line):  # Regex "http://"
            fields = line.split("\t")  #  Split fields based on \t
            gene_parameters = fields[1].split("|") # Gene fields
            fasta_name_hyperlink = {fields[0]:gene_parameters[2]} # Map the fasta header to the hyperlink that will be accessed for results
            for fasta_header,hyperlink in fasta_name_hyperlink.iteritems():
                try:
                    commands = (("wkhtmltopdf "+hyperlink+" "+fasta_header+".pdf"),  # Convert hyperlink html to pdf
                                ("pdftotext "+fasta_header+".pdf "+fasta_header+".txt"),  # Convert pdf to text for parsing later
                                ("mkdir "+opts.master_output+"/pathway_analysis/"+fasta_header),
                                ("mv "+fasta_header+".* "+opts.master_output+"/pathway_analysis/"+fasta_header))
                    for command in commands:
                        os.system(command)
                except:
                    print "Failed to retrieve and convert KO summary information for: "+fasta_header
                try:
                    browser = mechanize.Browser()    # Initiate Browser
                    browser.set_handle_robots(False)
                    browser.set_handle_refresh(True, max_time=10.0, honor_time=False)  # Max refresh time is 10 seconds
                    browser.set_debug_redirects(True)
                    browser.set_handle_redirect(mechanize.HTTPRedirectHandler)
                    browser.open(hyperlink)
                    pathway_links={}
                    for link in browser.links(url_regex="show_pathway"):
                        link_params = re.split("href", str(link))
                        pathway_link = "http://www.genome.jp"+link_params[1][4:-4]
                        pathway_links[pathway_link] = fasta_header
                    for k,v in pathway_links.iteritems():
                        browser.open(k)
                        for link in browser.links(url_regex="http://www.kegg.jp/kegg-bin/download\?entry=.*&format=kgml"):
                            link_params = re.split("href", str(link))
                            pathway_link = link_params[1][4:-4]
                            pattern1 = pathway_link.index("entry=")
                            pattern2 = pathway_link.index("&format=")
                            browser.retrieve(pathway_link,pathway_link[pattern1+6:pattern2]+".xml")  # Retrieve pathway map for each hit if a pathway exists
                            os.system("mv *.xml "+opts.master_output+"/pathway_analysis/"+v)
                except:
                    print "Failed to retrieve Pathway file for: "+fasta_header
except:
    print "Failed to retrieve KO and pathway information remotely.  Please check your internet connection and try again.  If other errors exist, please resort to those details when troubleshooting."

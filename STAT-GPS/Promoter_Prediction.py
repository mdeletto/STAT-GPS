#!/usr/bin/python

import mechanize, optparse, html2text, sys, re, os

#-------------------------------------------------------------------------------------------
#----------------------------Command line parser and arguments------------------------------
#-------------------------------------------------------------------------------------------

desc="""This script is used to remotely submit genomic sequences to the Neural Network Promoter Prediction server.  Promoter predictions are retrieved and stored in .txt and .gff3 formats.  Internet connection is required.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)

parser.add_option('-i', help='MANDATORY OPTION: Input fasta sequence - should be multi-fasta or single-fasta NUCLEOTIDE file--Example: fasta.fa', dest='input', action='store')
parser.add_option('-o', help='MANDATORY OPTION: Output directory (example: /path/to/output)', dest='master_output', action='store')
parser.add_option('-t', help='Type of organism <eukaryote, prokaryote>', dest='organism', action='store', default="eukaryote")
parser.add_option('-r', help='Include reverse strand? <yes, no>', dest='reverse', action='store', default="no")
parser.add_option('-s', help='Minimum promoter score: <any value between 0 and 1>', dest='score', action='store', default="0.8")
(opts, args) = parser.parse_args()

mandatory_options = ['input','master_output']
for m in mandatory_options:
# Making sure all mandatory options appeared
    if not opts.__dict__[m]:
        print "Mandatory option is missing!\n"
        parser.print_help()
        sys.exit()

#-------------------------------------------------------------------------------------------
#----------------------------MAIN - OPEN INPUT AND PARSE------------------------------------
#-------------------------------------------------------------------------------------------

try:
    os.system("mkdir "+opts.master_output+"/Promoter_Prediction")
except:
    print "Could not create output directory to hold results."
try:
    raw_data = open(opts.master_output+"/Promoter_Prediction/Promoter_data_raw.txt",'w')
    print "(1) Output file successfully opened for writing..."
except:
    print "Failed to open output file.  Please check input parameters and file permissions and try again."
try:
    print "(2) Now attempting to open file for input..."
    with open(opts.input,'r') as f:
        file_contents = f.read().split('>')[1:]
        # Obtain fasta sequence as a single string
    opts.input.close() 
    print "(3) Successfully opened input file.  Reading in data from file..."
except:
    print "Failed to open and parse your input file." 

#-------------------------------------------------------------------------------------------
#----------------------------MAIN - SUBMIT DATA TO NNPP REMOTELY----------------------------
#-------------------------------------------------------------------------------------------


try:
    print "(4) Now submitting your data remotely to Neural Network Promoter Prediction.  This may take some time..."
    for fasta_sequence in file_contents:
        browser = mechanize.Browser() # Initiate Browser
        browser.set_handle_robots(False)
        browser.set_handle_refresh(True, max_time=10.0, honor_time=False) # Max refresh time is 10 seconds
        browser.open('http://www.fruitfly.org/seq_tools/promoter.html')
        browser.select_form(nr=1)
        browser.form.set_value([opts.organism],name="organism")
        browser.form.set_value([opts.reverse],name="reverse")
        browser.form['threshold'] = opts.score
        browser.form['text'] = '>'+fasta_sequence.strip()
        browser.submit()
        html = browser.response().read()
        raw_data.write(html2text.html2text(html))
    print "(5) Raw data for promoter prediction has been completed.  Your results can be found at "+opts.master_output+"/Promoter_Prediction/Promoter_data_raw.txt"
    raw_data.close()
except:
    print "Failed to remotely submit your data to Neural Network Promoter Prediction.  Make sure you have an internet connection and all required Python modules."

try:
    print "(6) Now attempting to parse your raw data and convert to gff3 format."
    parsed_data = open(opts.master_output+"/Promoter_Prediction/Promoter_final.gff",'w')
    parsed_data.write("##gff-version 3")
    print "(7) Successfully opened output file for writing final results."
except:
    print "Failed to open your raw data output for parsing and converting to gff3 format."

#-------------------------------------------------------------------------------------------
#----------------------------MAIN - RAW DATA TO GFF3 CONVERSION-----------------------------
#-------------------------------------------------------------------------------------------


try:
    with open(opts.input,'r') as f:
        fasta_headers = []
        for lines in f:
            if re.search(">",lines):
                fasta_headers.append(lines[1:-1])
    with open(opts.master_output+"/Promoter_Prediction/Promoter_data_raw.txt",'r') as f:
        entries = f.read().split("* * *")
        n = 0
        for header in fasta_headers:
            if re.search(header,entries[n]):
                entry_lines = entries[n].split("\n")
                for line in entry_lines:
                    if re.search("\d+\s+\d+\s+\d+",line):
                        gff3_fields = []
                        line_no_space = line.split(" ")
                        for field in line_no_space:
                            if field:
                                gff3_fields.append(field)
                        if int(gff3_fields[1])<=int(gff3_fields[0]):
                            parsed_data.write("\n"+header+"\t"+"Neural_Network_Promoter_Prediction\t"+"Promoter\t"+gff3_fields[1]+"\t"+gff3_fields[0]+"\t"+gff3_fields[2]+"\t"+"-\t"+".\t"+"ID:PromoterRegion_"+header+";Parent="+header+";Note="+gff3_fields[3])
                        if int(gff3_fields[0])<=int(gff3_fields[1]):
                            parsed_data.write("\n"+header+"\t"+"Neural_Network_Promoter_Prediction\t"+"Promoter\t"+gff3_fields[0]+"\t"+gff3_fields[1]+"\t"+gff3_fields[2]+"\t"+"+\t"+".\t"+"ID:PromoterRegion_"+header+";Parent="+header+";Note="+gff3_fields[3])
            n+=1
except:
    "Failed to parse your raw_data file."

#!/usr/bin/python

from Bio.Blast import NCBIXML
import mechanize, re, glob, os

#-----------------------------------------------------------------------------
#---------------HOMOLOGY MODELING FUNCTIONS-----------------------------------
#-----------------------------------------------------------------------------

def homology_modeling_concat_fasta(file_input,email):
    try:
        output = open("log.txt","w")
        print "(1) Successfully opened logfile.txt for log information"
    except:
        print "(1) ERROR - Could not open logfile.txt for output"
    try:
        with open(file_input, 'r') as fh:
            filecontents = fh.read().split(">")
            print "(2) Successfully opened: "+str(file_input)
            print "(3) Inputting your sequences into SWISS-MODEL:"
            for x in filecontents:
                browser = mechanize.Browser()    # Initiate Browser
                browser.set_handle_robots(False)
                browser.set_handle_refresh(True, max_time=10.0, honor_time=False)  # Max refresh time is 10 seconds
                browser.set_debug_redirects(True)
                browser.set_handle_redirect(mechanize.HTTPRedirectHandler)
                browser.open('http://swissmodel.expasy.org/workspace/index.php?func=modelling_simple1')
                browser.select_form('form')  # Select form
                filelines = x.split("\n") # split each fasta sequence based on new line characters so we can extract header information
                if re.match(r'^\s*$', filelines[0]):
                    continue
                else:
                    try:
                        firstline = ">"+filelines[0] # fasta header but re-added the ">" character that we eliminated earlier (could be cleaner)
                        filesequence = ">"+x #  entire sequence + ">" character
                        browser.form['email'] = email
                        browser.form['sequence'] = filesequence
                        browser.form['title'] = firstline
                        browser.submit()
                        print "\tSuccessfully submitted: "+firstline
                    except:
                        print "Failed to successfully submit: "+firstline+" from "+str(file_input)
                    try:
                        output.write(filesequence+"\n")
                    except:
                        print "Failed to write log."
            print "(4) Logfile.txt contents written"
    except:
        print "Failed to open "+file_input
        

def homology_modeling_single_fasta(file_input,email):
    try:
        output = open("log.txt","w")
        print "(1) Successfully opened logfile.txt for log information"
    except:
        print "(1) ERROR - Could not open logfile.txt for output"
    try:
        browser = mechanize.Browser()    # Initiate Browser
        browser.set_handle_robots(False)
        browser.set_handle_refresh(True, max_time=10.0, honor_time=False)  # Max refresh time is 10 seconds
        browser.set_debug_redirects(True)
        browser.set_handle_redirect(mechanize.HTTPRedirectHandler)
        browser.open('http://swissmodel.expasy.org/workspace/index.php?func=modelling_simple1')
        browser.select_form('form')  # Select form
        print "(2) Inputting your sequences into SWISS-MODEL:"
    except:
        "Failed to open SWISS-MODEL website - Has the url changed?"
    try:
        with open(file_input, 'r') as fh:  # Open to obtain sequence data and fasta header to input into form
            browser.form['email'] = email
            filecontents = fh.read()
            browser.form['sequence'] = filecontents
        with open(file_input, 'r') as fh:
            firstline = fh.readline()  # Read in fasta header
            browser.form['title'] = firstline
        print "(3) Successfully opened: "+file_input
    except:
        print "Failed to open or extract information from file"
    try:
        browser.submit()
        print "(4) Successfully submitted: "+file_input
    except:
        "Failed to successfully submit "+file_input+" to SWISS-MODEL."
    try:
        output.write(filecontents+"\n")
        print "(5) Logfile.txt contents written"
    except:
        print "Failed to write log."

def homology_modeling_multiple_fasta(input_directory,email):
    try:
        output = open("log.txt","w")
        print "(1) Successfully opened logfile.txt for log information"
    except:
        print "(1) ERROR - Could not open logfile.txt for output"
    print "(2) Inputting your sequences into SWISS-MODEL:"
    for inputfile in glob.glob( os.path.join(input_directory, '*') ):  # Open to obtain sequence data and fasta header to input into form
        with open(inputfile, 'r') as f:
            browser = mechanize.Browser() # Initiate Browser
            browser.set_handle_robots(False)
            browser.set_handle_refresh(True, max_time=10.0, honor_time=False) # Max refresh time is 10 seconds
            browser.open('http://swissmodel.expasy.org/workspace/index.php?func=modelling_simple1')
            browser.select_form('form')
            browser.form['email'] = email
            filecontents = f.read()  
            browser.form['sequence'] = filecontents
        with open(inputfile, 'r') as f:
            firstline = f.readline() # Read in fasta header
            browser.form['title'] = firstline            
        try:
            browser.submit()
            print "\tSuccessfully submitted: "+inputfile
        except:
            print "\tFailed to successfully submit "+inputfile+" to SWISS-MODEL."
        try:
            output.write(filecontents+"\n")
        except:
            print "Failed to write log."
    print "(3) Logfile.txt contents written"



def blast_xml_to_gff3(file_in,file_out,blast_type):
    result_handle = open(file_in)
    blast_records = NCBIXML.parse(result_handle)
    E_VALUE_THRESH = 0.04
    with open(file_out,"w") as f:
        f.write("##gff-version 3"+"\n")
        for blast_record in blast_records:
            counter = 0
            for alignment in blast_record.alignments:
                for hsp in alignment.hsps:
                    if hsp.expect < E_VALUE_THRESH and counter < 1:
                        counter+=1
                        if hsp.strand[0] is None and hsp.frame[0] is None: f.write(blast_record.query + "\t" + 
                                                                                   str(blast_type) + "\t" + 
                                                                                   "match_part" + "\t" + 
                                                                                   str(hsp.query_start) + "\t" + 
                                                                                   str(hsp.query_end) + "\t" + 
                                                                                   str(hsp.score) + "\t" + 
                                                                                   "?" + "\t" +
                                                                                   "." + "\t" +
                                                                                   "ID="+blast_record.query+":"+alignment.title.replace(";","_").replace(" ","_") + ";" +
                                                                                   "Parent="+blast_record.query+";"+
                                                                                   "Name=blast_hsp;" +
                                                                                   "Alias="+alignment.title.replace(";","_").replace(" ","_")+"\n")
                        if hsp.strand[0] is None and hsp.frame[0] is not None: f.write(blast_record.query + "\t" + 
                                                                                       str(blast_type) + "\t" + 
                                                                                       "match_part" + "\t" + 
                                                                                       str(hsp.query_start) + "\t" + 
                                                                                       str(hsp.query_end) + "\t" + 
                                                                                       str(hsp.score) + "\t" + 
                                                                                       "?" + "\t" +
                                                                                       str(hsp.frame[0]) + "\t" +
                                                                                       "ID="+blast_record.query+":"+alignment.title.replace(";","_").replace(" ","_") + ";" +
                                                                                       "Parent="+blast_record.query+";"+
                                                                                       "Name=blast_hsp;" +
                                                                                       "Alias="+alignment.title.replace(";","_").replace(" ","_")+"\n")
                        if hsp.strand[0] is not None and hsp.frame[0] is None: f.write(blast_record.query + "\t" + 
                                                                                       str(blast_type) + "\t" + 
                                                                                       "match_part" + "\t" + 
                                                                                       str(hsp.query_start) + "\t" + 
                                                                                       str(hsp.query_end) + "\t" + 
                                                                                       str(hsp.score) + "\t" + 
                                                                                       str(hsp.strand[0]) + "\t" +
                                                                                       "." + "\t" +
                                                                                       "ID="+blast_record.query+":"+alignment.title.replace(";","_").replace(" ","_") + ";" +
                                                                                       "Parent="+blast_record.query+";"+
                                                                                       "Name=blast_hsp;" +
                                                                                       "Alias="+alignment.title.replace(";","_").replace(" ","_")+"\n")
                        if hsp.strand[0] is not None and hsp.frame[0] is not None: f.write(blast_record.query + "\t" + 
                                                                                           str(blast_type) + "\t" + 
                                                                                           "match_part" + "\t" + 
                                                                                           str(hsp.query_start) + "\t" + 
                                                                                           str(hsp.query_end) + "\t" + 
                                                                                           str(hsp.score) + "\t" + 
                                                                                           str(hsp.strand[0]) + "\t" +
                                                                                           str(hsp.frame[0]) + "\t" +
                                                                                           "ID="+blast_record.query+":"+alignment.title.replace(";","_").replace(" ","_") + ";" +
                                                                                           "Parent="+blast_record.query+";"+
                                                                                           "Name=blast_hsp;" +
                                                                                           "Alias="+alignment.title.replace(";","_").replace(" ","_")+"\n")
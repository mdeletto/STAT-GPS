#!/usr/bin/python

import mechanize, re, os, optparse, datetime

#-------------------------------------------------------------------------------------------
#----------------------------Command line parser and arguments------------------------------
#-------------------------------------------------------------------------------------------
desc="""This script is used to remotely download your SWISS-MODEL account results.  You should have already run the Homology_Modeling.py script in order to submit your results to the SWISS-MODEL server.
Please put the log.txt file produced by Homology_Modeling.py in your current working directory, as it is necessary for this script to parse the results.

You must have a valid SWISS-MODEL email and password to run this script.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)


parser.add_option('-e', help='SWISS-MODEL email login -- EXAMPLE: user@email.com', dest='email', action='store')
parser.add_option('-p', help='SWISS-MODEL password', dest='password', action='store')
(opts, args) = parser.parse_args()

#-------------------------------------------------------------------------------------------
#-------------------------------------------MAIN--------------------------------------------
#-------------------------------------------------------------------------------------------

if opts.email and opts.password:
    os.system("mkdir homology_model_"+str(datetime.date.today()))
    out_directory = "homology_model_"+str(datetime.date.today())

    try:
        log_file = open("log.txt","r") # Open log from Submission script
        logcontents=[]
        print "(1) Successfully opened log.txt"
        print "(2) Proceeding to parse log.txt"
        for line in log_file: # Read log file
            if re.search(">",line): # Match lines with fasta headers
                logcontents.append(line) # Push into list
    except:
        print "Failed to open log.txt - Is it in the current working directory?"

    try:
        browser = mechanize.Browser()    # Initiate Browser
        browser.set_handle_robots(False)
        browser.set_handle_refresh(True, max_time=1.0, honor_time=False)  # Max refresh time is  seconds
        browser.set_debug_redirects(True)
        browser.set_handle_redirect(mechanize.HTTPRedirectHandler)
        browser.open('http://swissmodel.expasy.org/workspace/index.php?func=show_workspace&userid=mikedeletto@gmail.com')#
        browser.select_form('form')  # Select form
        browser.form['email'] = opts.email
        browser.form['password'] = opts.password
        browser.submit()
        html = browser.response().readlines()
        print "(3) Login Successful"
    except:
        print "Login Failed - Try again"

    print "(4) Accessing SWISS-MODEL for files: This may take some time...."
    counter = 0 # initiate counter
    for link in browser.links(url_regex="workspace_modelling"):
        try:
            link_params = re.split("href", str(link))
            link1 = "http://swissmodel.expasy.org/workspace/"+link_params[1][4:-4]
            link2 = "http://swissmodel.expasy.org/workspace/"+link_params[1][4:-29]+"&func=getFile&file=getModellingPDF"
            link3 = "http://swissmodel.expasy.org/workspace/"+link_params[1][4:-29]+"&func=getFile&file=getModellingFile&key=&model=1&type=normal&show=download"
            link4 = "http://swissmodel.expasy.org/workspace/"+link_params[1][4:-29]+"&func=getFile&file=getModellingFile&key=&model=1&type=normal&show=text"
            outfile_header = logcontents[counter].replace(" ","").replace("|","_") #remove troublesome characters from fasta header (fasta header = file name for downloads)
            outfile_base = outfile_header.strip()    
            pdffile = outfile_base[1:]+".pdf"
            pdbfile = outfile_base[1:]+".pdb"
            pdbtext = outfile_base[1:]+".txt"
            browser.open(link1)
            browser.retrieve(link2,pdffile)
            browser.retrieve(link3,pdbfile)
            browser.retrieve(link4,pdbtext)
            html = browser.response().readlines()
            os.system("mkdir "+out_directory+"/"+outfile_base[1:])
            os.system("mv "+outfile_base[1:]+"* "+out_directory+"/"+outfile_base[1:])
            counter += 1 # counter for iteration through logfile
            print "\tSuccessfully downloaded all files for: "+outfile_base
        except:
            continue
    print "(5) Congratulations!  Your data is ready!  Before running the Homology_Modeling.py script again, please use the Clear_Workspace.py script to remove all workunits from SWISS-MODEL's server."

else:
    print "Your SWISS-MODEL account email and password are required to run this script.  You should have already registered for an account."
#!/usr/bin/python


import mechanize, re, optparse

#-------------------------------------------------------------------------------------------
#----------------------------Command line parser and arguments------------------------------
#-------------------------------------------------------------------------------------------
desc="""This script is used to remotely delete all workunits from your SWISS-MODEL account Workspace.  Before running this script, you should have already used Model_Retrieval.py to obtain your results (pdf,pdb,txt).  Results will be completely removed from your SWISS-MODEL Workspace, so
 make sure that you have downloaded your results.  NOTE: You cannot run Homology_Modeling.py again until you run this script.  

You must have a valid SWISS-MODEL email and password to run this script.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)


parser.add_option('-e', help='SWISS-MODEL email login -- EXAMPLE: user@email.com', dest='email', action='store')
parser.add_option('-p', help='SWISS-MODEL password', dest='password', action='store')
(opts, args) = parser.parse_args()

if opts.email and opts.password:
    confirm = raw_input("Are you sure you would like to run this script? (Y/N): ")
    if re.search("Y",confirm):
        print "NOTE: All data from SWISS-MODEL Workspace will now be deleted.  You should have run the Model_Retrieval.py script to obtain your results.  Also, you will be unable to use the Homology_Modeling.py script again until you use this script."
        try:
            print "(1) Initiating Workspace Cleanup..."
            print "(2) Logging in to SWISS-MODEL Workspace..."
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
            print "(3) Login Successful."
        except:
            print "Login Failed - Try again"
    
        try:
            print "(4) Now deleting Workspace units.  This may take some time..."
            print "(5) IMPORTANT: Please do not attempt to access your SWISS-MODEL Workspace during this time.  It will interfere with the cleanup process."
            for link_delete in browser.links(url_regex="deletenow"):
                link_params = re.split("href", str(link_delete))
                link1 = "http://swissmodel.expasy.org/workspace/"+link_params[1][4:-4]
                browser.open(link1)
                for link_confirm in browser.links(url_regex="mode=now"):
                    link_params = re.split("href", str(link_confirm))
                    link2 = "http://swissmodel.expasy.org/workspace/"+link_params[1][4:-56]
                    browser.open(link2)
                    continue
            print "(6) Your SWISS-MODEL Workspace should now be empty.  You can resubmit more sequences at any time with the Homology_Modeling.py script."
        except:
            print "(4) Huh? Something happened.  Make sure your login information is correct."
            
    elif re.search("N",confirm):
        print "You should run the Model_Retrieval.py script to obtain your results.  Also, you will be unable to use the Homology_Modeling.py script again until you use this script."
    else:
        print "Invalid response.  Type either Y or N."
else:
    print "Your SWISS-MODEL account email and password are required to run this script.  You should have already registered for an account."







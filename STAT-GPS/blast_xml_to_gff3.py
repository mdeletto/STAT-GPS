#!/usr/bin/python

from Bio.Blast import NCBIXML
import optparse, sys
desc="""This script is used to parse blast xml output to gff3 format.  Email questions/concerns to mikedeletto@gmail.com."""

parser = optparse.OptionParser(description=desc)
parser.add_option('-i', help='Input file absolute path--Exampple: /home/blast_input.xml', dest='input', action='store')
parser.add_option('-o', help='Output file absolute path--Example: /home/blast_output.gff3', dest='output', action='store')
parser.add_option('-t', help='BLAST type--Example: blastn, blastx, blastp', dest='type', action='store')
(opts, args) = parser.parse_args()

mandatory_options = ['input','output','type']
for m in mandatory_options:
# Making sure all mandatory options appeared
    if not opts.__dict__[m]:
        print "Mandatory option is missing!\n"
        parser.print_help()
        sys.exit()

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


blast_xml_to_gff3(opts.input,opts.output,opts.type)



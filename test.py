# Trying an algorithm which will spot common mistakes in
# Indian names, and suggest corrections.
# Based on Peter Norvig's original first article about 
# a simple spell checker - https://norvig.com/spell-correct.html
# spell.py in this repo contains his original code

#=================================================
# Standard imports
import os
import csv
import sys
import json
import numpy as np
import pprint
import re
import pdb
from collections import Counter
#=================================================

if __name__ == "__main__":
    print("Experiments with spellings of common names")
    #=================================================
    # Some of the bells and whistles
    pp = pprint.PrettyPrinter(indent=4)
    #=================================================
    # Check input arguments 
    argc = len(sys.argv)
    expected_argc = 2
    if argc != expected_argc:
        print("Missing input / output files.")
        sys.exit()
    #================================================= 
    # Process input arguments
    
    # 1) Input file path
    in_file_path = sys.argv[1]
    if os.path.exists(in_file_path):
        print("Input file: " + in_file_path)
    else:
        print("Input file not found.")
    #=================================================
    # Read the file and separate name tokens
    
    csvf = open(in_file_path, "r")
    csvr = csv.reader(csvf)
    NAMES_LIST = []
    for ln in csvr:
        # Assuming one line contains one full name
        name_tokens = ln[0].split(" ")
        #pp.pprint(name_tokens)

        # Process each name token
        # (Not treating name and surname separately.)
        
        # Discard titles and single letters and convert to lowercase
        for nt in name_tokens:
            if len(nt) <= 1 or (len(nt) == 2 and nt[-1]=="."):
                continue
            ntsub = re.sub('[,.\W]', '', nt)
            ntlc = ntsub.lower()
            if ntlc in ["dr", "er", "adv", "prof", "shri", "mr", "ms", "mrs", "smt", "advocate"]:
                continue
            if len(ntlc) <= 1:
                continue
            NAMES_LIST.append(ntlc)
        
    #print("Name collection: ")
    #pp.pprint(NAMES_LIST)

    # Construct a counter from the corpus of names in NAMES_LIST
    # Probability of the word in this is used in the model below.
    # Currently using set of names from our existing database.
    # WARNING: This database itself has spelling mistakes!
    # TODO: Use a corrected version of this database first
    # TODO: Use a more comprehensive and authoritative dataset of Indian names
    # TODO: Long term. Improve model by separating female, male names and surnames.

    NAMES = Counter(NAMES_LIST)
    
    #=================================================
    # Correction Model
    # Copied from Norvig guruji's article
    #=================================================
    # Uses a simple Bayesian equation 
    # c = correct word
    # w = incorrect word which we have typed
    # P(c|w) = P (c) x P(w|c) / P(w)
    # Denominator is not computed because it is common
    # P(Correct word, given an incorrect word) 
    #   = P( Correct word being a valid word ) 
    #   x P( incorrect word possible from correct word )
    # The first term
    #=================================================
    def P(name, N=sum(NAMES.values())):
        """Probability of name being in corpus"""
        return NAMES[name] / N

    def correction(name):
        """Find the most probable correction for given name"""
        # NOTE: key= something tells max to sort by argument
        return max(candidates(name), key=P)

    #=================================================
    # Candidate Model 
    # TODO: Put this nicely in a class later
    def known(names):
        """Return the subset of names, which appears in the known NAMES"""
        return set(nm for nm in names if nm in NAMES)

    def edits1(name):
        """All edits at distance=1 ie only one thing is edited."""
        letters     = 'abcdefghijklmnopqrstuvwxyz'
        splits      = [(name[:i], name[i:])     for i in range(len(name)+1)]
        deletes     = [L + R[1:]                for L, R in splits if R ]
        transposes  = [L + R[1] + R[0] + R[2:]  for L, R in splits if len(R)>1 ]
        insertions  = [L + c + R                for L, R in splits if R for c in letters]
        replaces    = [L + c + R[1:]            for L, R in splits for c in letters]
        return set(deletes + transposes + insertions + replaces)

    def edits2(name):
        """All names that are two edits away from the original"""
        return set( e2 for e1 in edits1(name) for e2 in edits1(e1) )

    def candidates(name):
        """Generate possible spelling corrections for given name."""
        # TODO: edits2 calls edits1 twice and could be also written with another input -
        # the readymade array of edits1
        # Uses atrivial, flawed error model that says all known 
        # words of edit distance 1 are infinitely more probable than 
        # known words of edit distance 2, and infinitely less probable 
        # than a known word of edit distance 0. So we can make 
        # candidates(word) produce the first non-empty list of candidates 
        # in order of priority:
        # 1) The original word, if it is known; otherwise
        # 2) The list of known words at edit distance one away, 
        #    if there are any; otherwise
        # 3) The list of known words at edit distance two away, if there are any; 
        #    otherwise
        # 4) The original word, even though it is not known.
        # This allows us to factor out the multiplication by P(w|c) in the above Bayesian 
        # model. TODO: Using a more sophisticated model of keyboard error probabilities, we
        # can use the second factor in the Bayesian model used in Norvig's article to get
        # better correction quality.
        c = set( known([name]) or known( edits1(name) ) or known(edits2(name)) or [name])
        return c

    #=================================================
    # Main loop for demo
    while(True):
        input_name = input("Enter name>> ")
        if input_name == "exit":
            break
        print("Did you mean: " + correction(input_name) + "?") 
    pp.pprint("Bye!")



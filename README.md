Simple spell check on Indian names. Useful for sanitising database entries.

To use:
    >> python3.6 test.py input/all_names.csv

This will prompt you for names:
    Enter name>> 

Enter some name, preferably with single or double error:
    Enter name>> visal

It will suggest a correction:
    Enter name>> visal
    Did you mean: vishal?

This loop will go on until you enter "exit" as the name.
    Enter name>> exit
    'Bye!'


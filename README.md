## Reference
### pygenesis.open(filename,verbose=False)
Opens a given output file and parse for basic information (e.g. record sizes). t
The returned object is used for any further action.

Input:
* filename: filename of an outputfile of Genesis 1.3
* verbose: If set to True, additional output is printed to the screen

Return:
* an object, which holds the data of the genesis output file. 

### obj.info(fld)
Prints a list of found datasets

Input:
* regular expression to filter dataset names

### obj.findRecord(fld)
Returns a list of dataset paths, which match the regular expression

Input:
* regular expression to filter dataset names

### obj.getRecord(fld)
Returns a dictionary of the full dataset from the output file, labeled by
the dataset path.

Input:
* regular expression to filter dataset names

### obj.getLattice(fld)
Returns a descriptive data record with the found dataset and auxilliary parameter such as the
position in z along the dataset and default labels for plotting.
This is a wrapper for explicit lattice elements, based on the getData() method.

Input:
* regular expression to filter dataset names

### obj.getData(fld,method='raw',position=0.5)
Returns a descriptive data record with processed data and auxilliary parameters.
The supported methods are:
* 'raw' - unprocessed data record from the output file
* 'mean' - mean value of the data record along the undulator

to be continued.....


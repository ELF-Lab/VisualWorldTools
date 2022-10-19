############ Originally based on Python2 script by Brian Dillon for UMass CSL Lab (date unknown)
############ Updated to Python3 for ELF-Lab by Anna Stacey in October 2022

import csv, random, codecs, numpy

#### latinSquare takes an experimental csv file, in the local directory
#### and returns a shuffled experimental list.
#### It first selects a subset of the items in the experimental csv file that correspond to the 
#### appropriate list.
#### Next, it shuffles together all the latin squared items from each subexperiment in the items file
#### with the items marked 'Filler' in the items file.

#### Given the sorting algorithm, you need more filler items than the total number of experimental items 


def latinSquare(curList, itemFile):
	with open(itemFile) as csvFile:										## Load experimentalItems file 
		stimFile = csv.reader(csvFile)
		stimList = [item for item in stimFile]
		
	stimDictionary 	= {}																## Organize into dictionary
		
	for item in stimList:
		stimDictionary.setdefault(item[0],[]).append(item[1:]) 

	exptItems 		= {}																## create dictionary to hold experimental items; subset of stimulus dictionary that contains appropriate latin square list.
	
	experiments = list(stimDictionary.keys())													## populate dictionary with filler and experimental items
	experiments.remove('Filler')
	for item in stimDictionary['Filler']:
		exptItems.setdefault('Filler',[]).append(item)
		
	for expt in experiments:
		numConditions = int(max([item[1] for item in stimDictionary[expt]]))			## get number of conditions
		numItems = len(stimDictionary[expt])											## get number of items
		condSequence = numpy.tile(range(1,numConditions+1), numItems)								## generate sequence of conditions
		currentItems = [ (str(item), str(condSequence[(item-1)+(curList-1)]) ) for item in range(1,numItems+1)]	## select appropriate list
		# currentItems should be lists of Item/Condition pairs like [1,1], [1,2], [2,1], etc.

		### Note that Latin Squaring here works by taking an item number, and looking up the corresponding condition in the 
		### condSequence list. The starting point in the condition sequence is offset by the curList value. 
		
		for item in stimDictionary[expt]:												## Once we have a list of tuples that are the current experimental items
			if tuple(item[0:2]) in currentItems:										## then include an item in the stim dictionary in the experimental item dictionary if it is in the currentItems list
				exptItems.setdefault(expt,[]).append(item)
		
	for expt in exptItems.keys():														## Shuffle all lists within the exptItems dictionary
		random.shuffle(exptItems[expt])
	
### Iterate through shuffled item lists to create master list, subject to constraint that no two items are next to each other.

	experimentalList = []
	lastExpt = 'NA'
	remainingExpts = list(exptItems.keys())
	
### Iterate through shuffled lists of sub experiments, popping off elements of those lists and appending them to the final experimentalList
	
	while(len(remainingExpts) > 1):
		tryExpt = random.choice(remainingExpts)
		if (tryExpt == lastExpt):
			continue
		else:
			if len(exptItems[tryExpt]) > 0:
				experimentalList.append([tryExpt]+exptItems[tryExpt].pop())
				lastExpt = tryExpt
			else:
				remainingExpts.remove(tryExpt)
	
	if ('Filler' not in remainingExpts) and (len(remainingExpts) > 0):
		print('WARNING: insufficient filler items. Items from the same experiment may occur adjacent to each other in list.')
	
	### Randomly insert remaining items
	for item in exptItems[remainingExpts[0]]:
		experimentalList.insert(random.randrange(len(experimentalList)+1),[remainingExpts[0]]+item)
		
	return experimentalList


############ Originally based on Python2 script by Brian Dillon for UMass CSL Lab (date unknown)
############ Updated to Python3 for ELF-Lab by Anna Stacey in October 2022

import csv, random, codecs, numpy

#### latin_square takes an experimental csv file, in the local directory
#### and returns a shuffled experimental list.
#### It first selects a subset of the items in the experimental csv file that correspond to the 
#### appropriate list.
#### Next, it shuffles together all the latin squared items from each subexperiment in the items file
#### with the items marked 'Filler' in the items file.

#### Given the sorting algorithm, you need more filler items than the total number of experimental items 


def latin_square(current_list, item_file):
	# Load experimental_items file
	with open(item_file) as csv_file: 
		stim_file = csv.reader(csv_file)
		stim_list = [item for item in stim_file]
		
	# Organize into dictionary
	stim_dictionary = {}
		
	for item in stim_list:
		stim_dictionary.setdefault(item[0], []).append(item[1:]) 
	
	# Create dictionary to hold experimental items; subset of stimulus dictionary that contains appropriate latin square list.
	experimental_items = {}
	
	# Populate dictionary with filler and experimental items
	experiments = list(stim_dictionary.keys())
	experiments.remove('Filler')
	for item in stim_dictionary['Filler']:
		experimental_items.setdefault('Filler', []).append(item)
		
	for expt in experiments:
		# Get number of conditions
		number_of_conditions = int(max([item[1] for item in stim_dictionary[expt]]))
		# Check that the provided value for current_list is within the expected range
		assert current_list <= number_of_conditions, "Value for current_list in latin_square is higher than permissible."
		assert current_list > 0, "Value for current_list in latin_square is lower than permissible."
		# Get number of items
		number_of_items = len(stim_dictionary[expt])
		# Generate sequence of conditions
		condition_sequence = numpy.tile(range(1, number_of_conditions + 1), number_of_items)
		# Select appropriate list
		current_items = [(str(item), str(condition_sequence[(item - 1) + (current_list - 1)])) for item in range(1, number_of_items + 1)]
		# currentItems should be lists of Item/Condition pairs like [1,1], [1,2], [2,1], etc.

		# Note that Latin Squaring here works by taking an item number, and looking up the corresponding condition in the 
		# condition_sequence list. The starting point in the condition sequence is offset by the current_list value. 
		
		# Once we have a list of tuples that are the current experimental items
		# then include an item in the stim dictionary in the experimental item dictionary if it is in the current_items list
		for item in stim_dictionary[expt]:
			if tuple(item[0:2]) in current_items:
				experimental_items.setdefault(expt,[]).append(item)

	# Shuffle all lists within the experimental_items dictionary	
	for expt in experimental_items.keys():
		random.shuffle(experimental_items[expt])
	
	# Iterate through shuffled item lists to create master list, subject to constraint that no two items are next to each other.
	experimental_list = []
	last_expt = 'NA'
	remaining_expts = list(experimental_items.keys())
	
	# Iterate through shuffled lists of sub experiments, popping off elements of those lists and appending them to the final experimental_list	
	while(len(remaining_expts) > 1):
		try_expt = random.choice(remaining_expts)
		if (try_expt == last_expt):
			continue
		else:
			if len(experimental_items[try_expt]) > 0:
				experimental_list.append([try_expt]+experimental_items[try_expt].pop())
				last_expt = try_expt
			else:
				remaining_expts.remove(try_expt)
	
	if ('Filler' not in remaining_expts) and (len(remaining_expts) > 0):
		print('WARNING: insufficient filler items. Items from the same experiment may occur adjacent to each other in list.')
	
	# Randomly insert remaining items
	for item in experimental_items[remaining_expts[0]]:
		experimental_list.insert(random.randrange(len(experimental_list) + 1),[remaining_expts[0]] + item)

	# Safety checks
	# Ensure that each item/cond matching is as expected based on participant
	for row in experimental_list:
		if (row[0] == 'Exp'): # The check isn't relevant for filler rows
			item_number = int(row[1])
			condition_number = int(row[2])
			# Remember that the values of current_list range from 1 to the number of conditions
			expected_condition_number = ((item_number % number_of_conditions) + current_list - 1) % number_of_conditions
			if expected_condition_number == 0:
				expected_condition_number = number_of_conditions
			assert condition_number == expected_condition_number, f"latin_square is not providing the expected condition number for item {item_number}. \nExpected condition: {expected_condition_number}, provided condition: {condition_number}"
			
	return experimental_list


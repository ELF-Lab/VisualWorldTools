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

# current_offset: Integer b/w 1 and the number of conditions
#	E.g., if there's 4 possible conditions for each experimental item, permitted values are 1, 2, 3 or 4.
#	This value determines what condition will be used for each experimental item for this run of the experiment.
# item_file: path to CSV to be read
#   The first column is expected to contain the stim type; "Exp" and "Filler" are currently supported,
#	but it would be easy to add more e.g., sub-types of "Exp".
def latin_square(current_offset, item_file):
	# Load experimental_items file
	with open(item_file) as csv_file: 
		stim_file = csv.reader(csv_file)
		stim_list = [item for item in stim_file]

	# Organize into dictionary, where the keys are "Exp", "Filler", etc. (column 1),
	# and the values are lists containing all the items of that kind.
	stim_dictionary = {}
	for item in stim_list:
		stim_dictionary.setdefault(item[0], []).append(item[1:])
	
	# Create dictionary to hold experimental items; subset of stimulus dictionary that contains appropriate latin square list.
	experimental_items = {}
	
	# Populate dictionary with filler and experimental items
	stim_types = list(stim_dictionary.keys())
	
	# Add all filler items to exp item
	for item in stim_dictionary['Filler']:
		experimental_items.setdefault('Filler', []).append(item)

	stim_types_sans_filler = [stim_type for stim_type in stim_types if stim_type != "Filler"]
	# If you just have "Exp" and "Filler", this is only run once as "Filler" has been removed
	for stim_type in stim_types_sans_filler:
		# Get number of conditions (max. value from the condition # column)
		number_of_conditions = int(max([item[1] for item in stim_dictionary[stim_type]]))
		# Check that the provided value for current_offset is within the expected range
		assert current_offset <= number_of_conditions, f"Value for current_offset ({current_offset}) in latin_square is higher than permissible (> {number_of_conditions})."
		assert current_offset > 0, f"Value for current_offset ({current_offset}) in latin_square is lower than permissible (<1)."
		# Get number of exp. items
		number_of_items = len(stim_dictionary[stim_type])
		# Generate sequence of conditions
		condition_sequence = numpy.tile(range(1, number_of_conditions + 1), number_of_items)
		# Select appropriate list
		# current_items will be lists of Item/Condition pairs like [1,1], [1,2], [2,1], etc.
		current_items = [(str(item), str(condition_sequence[(item - 1) + (current_offset - 1)])) for item in range(1, number_of_items + 1)]

		# Note that Latin Squaring here works by taking an item number, and looking up the corresponding condition in the 
		# condition_sequence list. The starting point in the condition sequence is offset by the current_offset value. 
		
		# Once we have a list of tuples that are the current experimental items
		# then include an item in the stim dictionary in the experimental item dictionary if it is in the current_items list
		for item in stim_dictionary[stim_type]:
			if tuple(item[0:2]) in current_items:
				experimental_items.setdefault(stim_type,[]).append(item)

	# Shuffle sub-lists within the experimental_items dictionary (e.g., shuffle the "Filler" items amongst themselves)
	for stim_type in stim_types:
		random.shuffle(experimental_items[stim_type])
	
	# Iterate through shuffled item lists to create master list, subject to constraint that no two items are next to each other.
	experimental_list = []
	prev_stim_type = 'NA'
	remaining_stim_types = list(stim_types)
	
	# Iterate through shuffled lists of sub-lists, popping elements off those lists and appending them to the final experimental_list	
	while(len(remaining_stim_types) > 1):
		current_stim_type = random.choice(remaining_stim_types)
		if (current_stim_type == prev_stim_type):
			continue
		else:
			if len(experimental_items[current_stim_type]) > 0:
				experimental_list.append([current_stim_type] + experimental_items[current_stim_type].pop())
				prev_stim_type = current_stim_type
			else:
				remaining_stim_types.remove(current_stim_type)
	
	if ('Filler' not in remaining_stim_types) and (len(remaining_stim_types) > 0):
		print('WARNING: insufficient filler items. Items from the same experiment may occur adjacent to each other in list.')
	
	# Randomly insert remaining ("Filler") items
	for item in experimental_items[remaining_stim_types[0]]:
		experimental_list.insert(random.randrange(len(experimental_list) + 1),[remaining_stim_types[0]] + item)

	# Safety checks
	# Ensure that each item/cond matching is as expected based on participant
	for row in experimental_list:
		if (row[0] == 'Exp'): # The check isn't relevant for filler rows
			item_number = int(row[1])
			condition_number = int(row[2])
			# Remember that the values of current_offset range from 1 to the number of conditions
			expected_condition_number = ((item_number % number_of_conditions) + current_offset - 1) % number_of_conditions
			if expected_condition_number == 0:
				expected_condition_number = number_of_conditions
			assert condition_number == expected_condition_number, f"latin_square is not providing the expected condition number for item {item_number}. \nExpected condition: {expected_condition_number}, provided condition: {condition_number}"
			
	return experimental_list


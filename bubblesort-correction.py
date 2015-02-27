
coins = 300
ring = 23
staff = 200
chest = 10
diamond = 23432
listItems = [coins,ring,staff,chest,diamond]
length = len(listItems) - 1


unsorted = True
while unsorted:
	unsorted = False
	for element in range(0, length):
		if listItems[element] > listItems[ element + 1]:
			hold = listItems[element + 1]
			listItems[element + 1] = listItems[element]
			listItems[element] = hold
			unsorted = True
			print listItems

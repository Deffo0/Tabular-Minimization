import itertools
import pandas as pd
from tabulate import tabulate

# Compare two binary numbers, check where there is one difference
# When hamming distance equal to one, it will be compared
def cBin(n1, n2):
    c = 0
    pos = 0
    for i in range(len(n1)):
        if n1[i] != n2[i]:
            c += 1
            pos = i
    if c == 1:
        return True, pos
    else:
        return False, None

# This helps when building PI table
# Compare if the number is same as implicant term
# Prime should be the term
def cBinTab(prime, minterm):
    for i in range(len(minterm)) :
        if prime[i] != 'x' :
            if prime[i] != minterm[i] :
                return False
    return True

# Combine pairs and make new group for result of the pairs
def cPairs(group, unchecked):
    lenGroup = len(group) - 1
    checked = []

    nextGroup = [[] for j in range(lenGroup)]
    for i in range(lenGroup):
        for el1 in group[i]:
            for el2 in group[i+1]:
                state, pos = cBin(el1, el2)
                if state:
                    checked.append(el1)
                    checked.append(el2)
                    newEl = list(el1)
                    newEl[pos] = 'x'
                    newEl = "".join(newEl)
                    nextGroup[i].append(newEl)

    for i in group:
        for el in i:
            if el not in checked:
                unchecked.append(el)

    return nextGroup, unchecked

# Remove redundant lists in 2D list
# Used for tabular method grouping
def removeRed(ham):
    newGroup = []
    for i in ham :
        noDupl = []
        for j in i :
            if j not in noDupl :
                noDupl.append(j)
        newGroup.append(noDupl)
    ham = newGroup

    return ham

# Remove redundant lists in 1D list
# Used for essential prime list so it doesnt take essential two times
def removeRedList(list):
    newList = []
    for i in list :
        if i not in newList :
            newList.append(i)

    return newList

# Find essential prime implicants by if there is one "1" in the column
def findEPI(PIT):
    EPI = []
    for col in range(len(PIT[0])):
        c = 0
        pos = 0
        for row in range(len(PIT)):
            #find essential
            if PIT[row][col] == 'x':
                c += 1
                pos = row
        if c == 1:
            EPI.append(pos)

    return EPI

# Checks if the Prime Implicant table has "X"
def checkZeros(PIT) :
    for i in PIT :
        for j in i :
            if j != ' ' :
                return False
    return True

# Checks if the Prime Implicant table is full of X
def checkOnes(PIT) :
    for i in PIT :
        for j in i :
            if j != 'x' :
                return False
    return True

# Multiply two terms like (a + b)(b + c + d), then it returns the product
def multi(PI1, PI2):
    result = []
    # If both equal zero
    if len(PI1) == 0 and len(PI2)== 0:
        return result
    # If one of them equal zero
    elif len(PI1) == 0:
        return PI2
    # If the other equal zero
    elif len(PI2) == 0:
        return PI1

    # Both have elements
    else:
        for i in PI1:
            for j in PI2:
                # If they are equal
                if i == j:
                    # Take just one of them
                    result.append(i)
                else:
                    # Sort the product and put them in one list
                    result.append(list(set(i+j)))

        # Sort the whole result
        result.sort()
        # Return a product without any repeated terms in it like (ab + c)(ab + d)(ab + c)
        return list(result for result,g in itertools.groupby(result))

# Petrick's method
def petrickMethod(PIT, unchecked):
    # Petrick's elements
    PI = []
    # Printing petirck;s elements
    print("\nPetrick's Method: ")
    s = ''
    for col in range(len(PIT[0])):
        pi = []
        y = ''
        for row in range(len(PIT)):
            if PIT[row][col] == 'x':
                pi.append([row])
                y = y + " + " + BintoLet(unchecked[row])
        if y != '':
            s = s + "(" + y[3:len(y)] + ")" 
        PI.append(pi)
    print(s)
    
    # Multiplication time
    for l in range(len(PI)-1):
        PI[l+1] = multi(PI[l],PI[l+1])

    PI = sorted(PI[len(PI)-1],key=len)
    lowTerms = []
    # Find the terms with minimum terms
    min=len(PI[0])
    for i in PI:
        if len(i) == min:
            lowTerms.append(i)
        else:
            break
    # Return result of petrick's method
    return lowTerms

# Minimization for PI table
def tMini(PIT, unchecked, lMint):
    EPIfinal = []
    # Fint essential prime implicants
    essentialPrime = findEPI(PIT)
    essentialPrime = removeRedList(essentialPrime)

    # Print the essential prime implicants
    if len(essentialPrime)>0:
        pnt = "\nNumber of Essential Prime Implicants: " + str(len(essentialPrime))
        print(pnt)
        s = "\nEssential Prime Implicants: "
        for i in range(len(unchecked)):
            for j in essentialPrime:
                if j == i:
                    s = s + BintoLet(unchecked[i]) + ', '
        print(s[:(len(s)-2)])
    else:
        print("\nNumber of Essential Prime Implicants: 0")
        print("\nEssential Prime Implicants: NONE")


    # Edit PI tablet to remove the covered terms
    for i in range(len(essentialPrime)):
        for col in range(len(PIT[0])):
            if PIT[essentialPrime[i]][col] == 'x':
                for row in range(len(PIT)):
                    PIT[row][col] = ' '

    # Checks if PI table finished
    if checkZeros(PIT):
        EPIfinal = [essentialPrime]
    else:
        # Petrick's method
        PetrickPI = petrickMethod(PIT, unchecked)

        # Find the minimum term with lower cost
        EPICost = []
        for prime in PetrickPI:
            c = 0
            for i in range(len(unchecked)):
                for j in prime:
                    if j == i:
                        # Calculate the cost
                        c = c + calcCost(unchecked[i])
            EPICost.append(c)


        for i in range(len(EPICost)):
            if EPICost[i] == min(EPICost):
                EPIfinal.append(PetrickPI[i])

        # Put the solution of Petrick's method to the final result
        for i in EPIfinal:
            for j in essentialPrime:
                if j not in i:
                    i.append(j)

    return EPIfinal

# Calculate the cost of minimum terms of petrick's method
def calcCost(n):
    cost = 0
    for i in range(len(n)):
        if n[i] != '-' and n[i] == '1':
            cost+=1
        elif n[i] != '-' and n[i] == '0':
            cost+=2

    return cost

# Converts the binary number to letters
# Using ASCII code
def BintoLet(n):
    asciiLetter = ord('A')
    let = ''
    for i in range(len(n)):
        if n[i] == '1':
            let = let + chr(asciiLetter)
        elif n[i] == '0':
            let = let + chr(asciiLetter) + '\''
        asciiLetter += 1

    return let

# Main function
def main():
    # Scan inputs:
    # Scan num of var 
    nVar = int(input("\nEnter no of variables: "))
    # Checks number of minterms
    if nVar == 0 or nVar > 26:
        print ("\nError: Number of variables must be from 1 to 26")
        return
    # Scan num of minterms
    nMint = int(input("Enter no of minterms: "))
    # Checks number of minterms
    if nMint == 0 or nMint > 2**nVar:
        print ("\nError: Number of minterms incorrect")
        return
    # Scan the minterms 
    mint = input("Enter the minterms in series with spaces : ")
    # Put the minterms in list in int form
    lMint = mint.split()
    iLMint = list(map(int, lMint))

    # Checks if number of minterms is right
    if len(iLMint) != nMint:
        print ("\nError: Number of minterms is not equal to the entered minterms")
        return

    # Initialize a list for list of binary numbers
    group = [[] for x in range(nVar+1)]

    bLMint = []
    for i in range(nMint):
        # Convert to binary
        bLMint.append(bin(iLMint[i])[2:])
        if len(bLMint[i]) < nVar:
        # Add zeros to charge the unused var 
            for j in range(nVar - len(bLMint[i])):
                bLMint[i] = '0' + bLMint[i]
        # In case nVar was wrong
        elif len(bLMint[i]) > nVar:
            print ('\nError: num of var looks wrong: \n')
            return
        # Count no of ones in each binary number in bLmint
        order = bLMint[i].count('1')
        # Group by no of 1 separately
        group[order].append(bLMint[i])
    
    allG=[]
    unchecked = []
    # Combine the pairs in series until nothing new can be combined
    while any(group):
        allG.append(group)
        nextG, unchecked = cPairs(group,unchecked)
        group = removeRed(nextG)
    
    # Initialize the prime implicant table
    PIT = [[' ' for x in range(nMint)] for x in range(len(unchecked))]

    for i in range(nMint):
        for j in range (len(unchecked)):
            # Determine the covered minterms for each PI
            if cBinTab(unchecked[j], bLMint[i]):
                PIT[j][i] = 'x'

    # Checks if all terms covered
    if checkOnes(PIT) and nMint == 2**nVar:
        # Make prime implicants table visualization
        df = pd.DataFrame(PIT)
        df.columns = lMint
        df.index = ['1']
        print("\n")
        print(tabulate(df, headers = lMint, tablefmt = 'grid')) 
        print ("\nNumber of Prime Implicants: 1")
        print ("\nPrime Implicants: 1")
        print ("\nNumber of Essential Prime Implicants: 1")
        print ("\nEssential Prime Implicants: 1")
        print("\nResult: ")
        print("F = 1")
    else:
        NPI = "\nNumber of Prime Implicants: " + str(len(unchecked))
        print(NPI)
        s = "\nPrime Implicants: "
        for i in unchecked:
            s = s + BintoLet(i) + ", "
        print(s[:(len(s)-2)])

        # Make prime implicants table visualization
        df = pd.DataFrame(PIT)
        df.columns = lMint
        df.index = [BintoLet(i) for i in unchecked]
        print("\n")
        print(tabulate(df, headers = lMint, tablefmt = 'grid')) 

        # Get the minimal prime implicants
        minPrimes = tMini(PIT, unchecked, lMint)
        minPrimes = removeRed(minPrimes)

        # Print the final result
        print("\nResult: ")
        for p in minPrimes:
            s='F = '
            for i in range(len(unchecked)):
                for j in p:
                    if j == i:
                        s = s + BintoLet(unchecked[i])+' + '
            print(s[:(len(s)-2)])



# Calls the main function to start
main()
while True:
    restart = input("\nDo you want to restart the program? [yes/no]\n")
    if restart == 'yes':
        main()
    else:
        Z = input("\nPress Enter to Quit")
        break
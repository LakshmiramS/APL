# take a circuit file as the input and return a dictionary from which 
# the voltages of the nodes and 
# current through voltage source can be found out.

import io
import numpy as np
from numpy.linalg import LinAlgError
from collections import defaultdict


def evalSpice(filename):

    try: # for filenotfound error


        #file handling
        sfp = open(filename, "r")
        list_of_lines = sfp.readlines() # each line in this file is a string in list_of_lines.
        list_vsources = [] # list of voltage sources.
        list_isources= [] #
        list_res = []


        # parse the file and
        flag = 0 # tells me whether to consider a line in the file is a valid input or not

        # node_dict[nodename] = nodenumber
        node_dict = defaultdict(int)
        node_count = 1
        for line in list_of_lines: # line is a string
            splitline = line.split()
            if splitline == [".end"]:
                flag = 0
            if flag == 1:
                node1 = splitline[1]
                node2 = splitline[2]
                if(node_dict[node1] == 0):
                    node_dict[node1] = node_count
                    node_count += 1
                if(node_dict[node2] == 0):
                    node_dict[node2] = node_count
                    node_count +=1
                # the final node_count is the total number of nodes(+1).

                first_word = splitline[0]
                first_letter = first_word[0]
                if first_letter == "V":
                    list_vsources.append(splitline[0:5]) #splitline is a list.
                elif first_letter == "R":
                    list_res.append(splitline[0:4])
                elif first_letter == "I":
                    list_isources.append(splitline[0:5])
                else:
                    raise ValueError("Only V, I, R elements are permitted")
            if splitline == [".circuit"]:
                flag = 1
            

        # after this, all the nodes will be mapped to some number in [1,n], n is number of nodes.
        NumberOfNodes = node_count - 1

        if len(list_isources) == 0 and len(list_res) == 0 and len(list_vsources) == 0:
            raise ValueError('Malformed circuit file')

        else:

            #but we know that GND is anyway 0 and it is not a variable.

            #swap appropriate nodes to get GND to have nodenumber 1
            temp_node_number = node_dict["GND"]
            # find out which key has a value of 1
            for key in node_dict:
                if node_dict[key] == 1:
                    node_dict[key] = temp_node_number
            node_dict["GND"] = 1

            # node number 1 is allotted to GND now
            # the nodes corresponding to  nodenumbers from 2 to n+1 are variables now.

            # CONSTRUCT THE ADMITTANCE MATRIX
            admittance_matrix = np.zeros((NumberOfNodes - 1,NumberOfNodes - 1))  # <--- this is the A
            CurrentVector = np.zeros(NumberOfNodes - 1) # <--- this is the B in Ax = B


            # CREATE A DICTIONARY WITH THE NODES OF ALL THE VOLTAGE SOURCES. this does not contain GND
            voltDict = defaultdict(int)
            for battery in list_vsources:
                batteryName = battery[0]
                NodeName1 = battery[1]
                NodeName2 = battery[2]
                if NodeName1 != "GND":
                    voltDict[NodeName1] = node_dict[NodeName1]
                if NodeName2 != "GND":
                    voltDict[NodeName2] = node_dict[NodeName2]



            # start with RESISTORS
            # parse a resistor list, extract its resistance value and the nodes a and b at its corners.
            # place that resistor in the matrix at all its locations.
            # a,a = +1/r  a,b = -1/r  b,a = -1/r  b,b = 1/r
            for templist in list_res:
                resistance = float(templist[-1])
                # what to do if resistance value is 0?
                NodeName1 = templist[1]
                NodeName2 = templist[2]
                NodeNumber1 = node_dict[NodeName1]
                NodeNumber2 = node_dict[NodeName2]
                
                # if both the nodes are GNDs; do nothing with the resistors
                # if atleast one of a or b contains a voltage source, then discard the corresponding terms of the resistor; 
                # the voltage constraint will take care of it.
                # if resistor is connected between a and b and there is a voltage source across it, discard the resistor.
                flag = 0

                # THERE IS A POSSIBILITY THAT BOTH THE NODES ARE THE SAME; IN THAT CASE,  just ignore.
                if NodeNumber1 == NodeNumber2 :
                    flag = 1


                if NodeName2 in voltDict and NodeName1 in voltDict:
                    # ignore this resistor for the admittance matrix
                    flag = 1
                
                if NodeName1 == "GND" and NodeName2 == "GND":
                    flag = 1

                if NodeName1 == "GND" and NodeName2 != "GND" and NodeName2 not in voltDict:
                    admittance_matrix[NodeNumber2-2][NodeNumber2 - 2] += 1/(resistance)
                    flag = 1
                
                if NodeName2 == "GND" and NodeName1 != "GND" and NodeName1 not in voltDict:
                    admittance_matrix[NodeNumber1-2][NodeNumber1 - 2] += 1/(resistance)
                    flag = 1

                if NodeName1 in voltDict and NodeName2 == "GND":
                    # do nothing
                    flag =1

                if NodeName2 in voltDict and NodeName1 == "GND":
                    # do nothing
                    flag = 1


                elif (NodeName1 in voltDict) and (NodeName2 not in voltDict) and (NodeName2 != "GND"):
                    # write something here
                    #ignore the resistor's contribution to NodeName1
                    admittance_matrix[NodeNumber2-2][NodeNumber2-2] += 1/(resistance)
                    admittance_matrix[NodeNumber2 - 2][NodeNumber1 - 2] += -1/(resistance)
                    flag = 1 

                elif NodeName2 in voltDict and NodeName1 not in voltDict and NodeName1 != "GND":
                    # write something here
                    #ignore the resistor's contribution to NodeName2
                    admittance_matrix[NodeNumber1-2][NodeNumber1-2] += 1/(resistance)
                    admittance_matrix[NodeNumber1-2][NodeNumber2-2] += -1/(resistance)
                    flag = 1

                if flag == 0:
                    admittance_matrix[NodeNumber1-2][NodeNumber1-2] += 1/(resistance)
                    admittance_matrix[NodeNumber2-2][NodeNumber2-2] += 1/(resistance)
                    admittance_matrix[NodeNumber1-2][NodeNumber2 - 2] += -1/(resistance) 
                    admittance_matrix[NodeNumber2 - 2][NodeNumber1 - 2] += -1/(resistance)

            #resistors are placed at their positions
            # now deal with voltage sources.
            # vsource node1 node2 dc value means node1 = node2 + value


            # rowNumber decides which row of the matrix is going to contain information about the voltage sources.
            # THIS IS WRONG; YOU FIRST HAVE TO FIND OUT WHICH ROWS OF THE ADMITTANCE MATRIX ARE FULL OF ZEROES
            # INSERT THIS INFORMATION THERE
            # INFACT, THE NUMBER OF SUCH ZERO ROWS HAS TO BE EQUAL TO THE NUMBER OF VOLTAGE SOURCES.
            
            sampleArray = np.zeros(NumberOfNodes - 1)
            emptyRowlist = []
            for rowNumber in range(NumberOfNodes - 1):
                if np.array_equal(admittance_matrix[rowNumber], sampleArray):
                    emptyRowlist.append(rowNumber)
        # if my calculations are right, the length of emptyRowlist and len of list_vsources should be the same.


            try: # for voltage elements in loop
                for counter in range(len(list_vsources)):
                    
                    battery = list_vsources[counter]
                    rowForBattery = emptyRowlist[counter]

                    #extract values from the battery list
                    potential = float(battery[-1])
                    NodeName1 = battery[1]
                    NodeName2 = battery[2]

                    if NodeName1 == NodeName2 :
                        #raise an error; a battery is connected between nodes that are shorted. 
                        raise ValueError(" the terminals of a battery are shorted")   
                            
                    elif NodeName1 == "GND" and NodeName2 != "GND":
                        NodeNumber2 = node_dict[NodeName2]
                        admittance_matrix[rowForBattery][NodeNumber2 - 2] = -1 
                        CurrentVector[rowForBattery] = potential

                    elif NodeName2 == "GND" and NodeName1 != "GND":
                        NodeNumber1 = node_dict[NodeName1]
                        admittance_matrix[rowForBattery][NodeNumber1 - 2] = 1
                        CurrentVector[rowForBattery] = potential

                    else:
                        NodeNumber1 = node_dict[NodeName1]
                        admittance_matrix[rowForBattery][NodeNumber1 - 2] = 1
                        NodeNumber2 = node_dict[NodeName2]
                        admittance_matrix[rowForBattery][NodeNumber2 - 2] = -1
                        CurrentVector[rowForBattery] = potential
            except IndexError:
                raise ValueError('Circuit error: no solution')
           

            
            # now deal with current sources

            # raise error for current sources in parallel
            try:
                for currentSource in list_isources:
                    current = float(currentSource[-1])
                    NodeName1 = currentSource[1]
                    NodeName2 = currentSource[2]

                    # if both the terminals are the same, raise error
                    if NodeName1 == NodeName2:
                        raise ValueError("the terminals of a current source are shorted")
                    
                    # if one of the terminals is GND, handle it specially
                    elif NodeName1 == "GND" and NodeName2 != "GND":
                        NodeNumber2 = node_dict[NodeName2]
                        CurrentVector[NodeNumber2 - 2] = -1 * current

                    elif NodeName2 == "GND" and NodeName1 != "GND":
                        NodeNumber1 = node_dict[NodeName1]
                        CurrentVector[NodeNumber1 - 2] = +1 * current

                    else:
                        NodeNumber1 = node_dict[NodeName1]
                        CurrentVector[NodeNumber1 - 2] = +1 * current    
                        NodeNumber2 = node_dict[NodeName2]
                        CurrentVector[NodeNumber2 - 2] = -1 * current
            except:
                raise ValueError('Circuit error: no solution')
            # i still don't know how to deal with current sources with resistors in parallel.
            # what happens when current source is in series with voltage source?

            # i guess i am done with the matrix construction
            # now solve the matrices and extract the values
            try :# for inconsistent systems

                xVector = np.linalg.solve(admittance_matrix,CurrentVector)
            


                voltages = {}
                voltages["GND"] = 0.0
                for nodeNumber in range(2,NumberOfNodes + 1): # number of nodes include GND 
                    for key in node_dict:
                        if node_dict[key] == nodeNumber:
                            NodeName = key
                    voltages[NodeName] = xVector[nodeNumber - 2]

                

                # find current through voltage sources.
                currentInSource = {}
                for battery in list_vsources:
                    batteryName = battery[0]
                    node1 = battery[1]
                    node2 = battery[2]
                    current = 0

                    # iterate through all the resistors which branch out of node1 and add the currents 
                    for resistor in list_res:
                        node1Res = resistor[1]
                        node2Res = resistor[2]
                        if node1Res == node1:
                            resistance = float(resistor[-1])
                            current += (voltages[node1Res]-voltages[node2Res]) / resistance
                        elif node2Res == node1:
                            resistance = float(resistor[-1])
                            current += (voltages[node2Res]-voltages[node1Res]) / resistance


                    currentInSource[batteryName] = -1 * current 
                return (voltages, currentInSource) 
            except LinAlgError:
                raise ValueError('Circuit error: no solution')
    except FileNotFoundError:
        raise FileNotFoundError('Please give the name of a valid SPICE file as input')   

    # # msg = """.circuit
    # # V1   1 GND  dc 2
    # # R1   1   2     1
    # # R2   2 GND     1
    # # .end
    # # """


    # # with open("text_1.txt","r") as file: # file is a file object
    # #     file_content = file.read() # file_content is one string that contains all the stuff in the file
    # # print(evalSpice(file_content))
    # print(evalSpice("./testdata/test_1.txt"))
# SPICE simulation in Python

# Purpose

To input a circuit and determine the nodal potentials and the currents across the circuit components.

# Method

This is a very basic functional circuit solver that can deal with constant time invariant current and voltage sources along with resistors.
We employ Kirchoff's laws to perform nodal potential analysis and first detemine the nodal potentials. 
Then we can find the currents through the resistors by Ohm's law. The current through the voltage source can also be calculated by finding out the current leaving one of the terminal of the source.

# Ideas
1. First extract the circuit elements from the .ckt file and sort them as batteries, current sources or resistors. I found the sorting very useful while coding as it helped me take care of edge cases which I couldn't predict initially.
1. I totally used whatever I learnt in my ECN classes. Let's assume there are n nodes in the ciruit. We fix "GND" as 0 V as a convention. That makes it n -1 variables in total. To figure out n - 1 variables, we need n - 1 constraint equations and hence we are looking at a n-1 x n-1 square admittance matrix. The unknown nodal potentials are grouped together in the column vector X  and the known parameters like the constant voltage sources and current sources are incorporated inside the constant column vector B.
2. We employ numpy's equation solver to get the requried values from AX = B.
3. To calculate the current through the voltage source, I find the current through all the resistors which branch out of one of the nodes of the battery. But it does have its own pitfalls; this method will fail if there is a battery too that is connected along with all the terminal resistors.

# Some comments 

I am using a very naive approach to solve the given set of equations. Plus I had to take care of a lot of edge cases to avoid the code from crashing when invalid inputs are fed. A great way to improvise this code would be to be able to incorportate values inside the unknown variable vector X in AX = B.

All the other details are pretty much covered in the code itself as commnents and the code is trivial; it does not have any sophisticated algorithms.



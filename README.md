# geo-address-parser

## addSupervisor.py
This script works with two files.
The first one is a main file. It's an *.xlsx with agents. Each agent has: 1) the address of their work; 2) an ID of a workplace.
The second file is a reference. Its structure is: 1) subject of the Russian Federation; 2) directorate of the bank which manages this subject; 3) manager that works in this directorate; 4) manager's ID; 5) a settlement which is curated by this manager.

The goal is to define the directorate and the manager for each agent in the first (main) file.

The difficulty is, all addresses are written a bit differently which makes the formalization a harsh task. For example, the address can start from the sity straightaway, omitting the subject.
My solution is to search for keywords (to be more precise, letters) in the address which indicate that this part of an address contains the name of the city or the region.

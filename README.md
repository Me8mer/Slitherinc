# Slitherlink Solver Project

## 1. Project Overview
This project is a solver for the Slitherlink puzzle using a **SAT-based approach**. Slitherlink is a logic puzzle where the goal is to form a single continuous loop on a grid, based on numerical clues provided in the cells. The solver encodes the Slitherlink constraints as a SAT problem and uses a SAT solver (Glucose) to find a solution.

The SAT solver used is [Glucose](https://www.labri.fr/perso/lsimon/research/glucose/), more specifically [Glucose 4.2.1](https://github.com/audemard/glucose/releases/tag/4.2.1). The source code is compiled using

```
cmake .
make
```

I was not able to create constraints for ensuring single loop and run the SAT solver only one time. The only solution I could come up with, was running the SAT solver multiple times and restricting multiple loops if there were any. I'm not sure if it's possible to do create these constraints in a single SAT solver run, but if it is, it would probably increase efficiency of the program.

## 2. Problem Definition
Slitherlink is played on a rectangular grid. Each cell in the grid may contain a number between 0 and 3, or be empty. The numbers indicate how many of the four edges around that cell are part of the loop. The loop must:
- Form a single, continuous, closed cycle.
- Not intersect itself.
- Satisfy the numerical constraints given in the grid cells.

## 3. Input Format
The input can be provided either as a file or through the command line. The grid is defined as follows:
- The first two lines specify the grid dimensions: `height` then `width`.
- Each subsequent line represents a row in the grid. Cells can contain numbers (`0`, `1`, `2`, `3`) or be empty (`.`).

**Example Input:**
6
6
```   
. . . 2 . .
3 3 . . 1 0
. . 1 2 . .
. . 2 0 . .
. 1 . . 1 1
. 2 . . . .
```

## 4. Output Format
The output is a visual representation of the solved Slitherlink grid, showing the loop edges. The grid uses horizontal (`──`) and vertical (`│`) lines to represent the loop, and the cell values are displayed as specified in the input.

**Example Output:**

``````
*─*─*─*─*─* *
│      2  │  
* *─* *─*─* *
│3│3│ │  1 0 
*─* * *─* * *
    │1 2│    
* * * * *─* *
    │2 0  │  
* * *─* * * *
   1  │  1│1 
*─*─*─* * * *
│  2      │  
*─*─*─*─*─* * 
``````

## 5. Encoding the Problem
The Slitherlink puzzle is encoded as a SAT problem in the DIMACS CNF format. The encoding involves the following components:
### 1. Variables
Each edge in the grid is assigned a unique boolean variable:

Horizontal Edges: Represented as h[i,j], where i and j denote the row and column of the starting point of the edge.
Vertical Edges: Represented as v[i,j], where i and j denote the row and column of the starting point of the edge.
Each variable can take a value of:

True (the edge is part of the loop)
False (the edge is not part of the loop)

### 2. Constraints
The SAT encoding ensures the following constraints are satisfied:
1. **Number Constraints (Clue Constraints)**
For each cell containing a clue (number n, where n ∈ {0, 1, 2, 3}):
Exactly n of the 4 edges surrounding the cell must be True.

**Encoding Logic:**

- Value 0: No edge can be True:

```¬e1 ∧ ¬e2 ∧ ¬e3 ∧ ¬e4```

- Value 1: Exactly 1 edge must be True:

``` (e1 ∧ ¬e2 ∧ ¬e3 ∧ ¬e4) ∨ (¬e1 ∧ e2 ∧ ¬e3 ∧ ¬e4) ∨ ...```

- Value 2: Exactly 2 edges must be True:

``` (e1 ∧ e2 ∧ ¬e3 ∧ ¬e4) ∨ (e1 ∧ ¬e2 ∧ e3 ∧ ¬e4) ∨ ... ```

- Value 3: Exactly 3 edges must be True:

``` (¬e1 ∧ e2 ∧ e3 ∧ e4) ∨ (e1 ∧ ¬e2 ∧ e3 ∧ e4) ∨ ... ```
2. **Vertex Constraints**
Each vertex (point where edges meet) must have 0 or 2 edges in the loop. This ensures the loop is continuous without any dangling edges. 

**Encoding Logic:**

For each vertex v:

If the sum of connected edges ≠ 0, it must equal 2

3. **Iterative Single Loop Constraint**

The solution must form a single, continuous loop.

This is enforced iteratively:

- Initial Solve: Solve the SAT problem without single-loop constraints to detect disjoint loops.
- Find Components: Identify all connected components of the edges in the solution.
- Add Constraints: If multiple components are detected, add a constraint to eliminate the specific configuration of disjoint loops in future runs.
- Repeat: Solve the SAT problem again with the new constraints until only one loop remains.

### 3. DIMACS CNF Format
- he constraints are written in DIMACS format for the SAT solver:  
- Each clause is a line of space-separated integers ending in 0.  
- Positive integers represent variables; negative integers represent their negation.

## 6. Solver Usage
The solver uses the **Glucose SAT solver** to find a solution to the encoded SAT problem.

### Command Line Arguments:
./Slitherlink.py [-h] [-i INPUT] [--print-cnf] [--collect-stats]
- `-h`, --help: Show this help message and exit.
- `-i INPUT`, `--input INPUT`: The input file containing the Slitherlink puzzle instance.
- `-print-cnf`: Print the CNF formula for debugging purposes.
- `-collect-stats`: Collect and display SAT solver statistics after solving.

## 7. Implementation Details
- The grid is parsed, and edges and cells are initialized based on the input.  
- The problem is encoded as a SAT problem using CNF (Conjunctive Normal Form) clauses. 
- Because I could not create SAT constraints for ensuring single loop without running SAT solver multiple times, I iteratively run SAT solver, look for loops and then add constraints.
- Once I find only single loop, the result is interpreted back into a solution for the Slitherlink puzzle.

## 8. Example instances and experiments
### `Medium_solv.txt`
Solvable 6x6 grid.  
SAT solver runs 3 times.  
Last SAT solver uses 84 variables and 315 clauses.   
Total CPU time: 0.00428 s
### `Medium_unsolv.txt`
Not solvable 6x6 grid.  
SAT solver runs 1 time.  
SAT solver uses 84 variables and 354 clauses
Total CPU time: 0.00110 s
### `Large_solv.txt`
Solvable 29x29 grid.  
SAT solver runs 52 times.  
Last SAT solver uses 1740 variables and 8723 clauses.   
Total CPU time: 0.82173 s
### `VeryLarge_solv.txt`
Solvable 30x30 grid.  
SAT solver runs 424 times.  
Last SAT solver uses 1860 variables and 14010 clauses.   
Total CPU time: 47.15049 s
### `ExtraLarge_solv.txt`
Solvable 35x30 grid.  
SAT solver runs 788 times.  
Last SAT solver uses 2165 variables and 21236 clauses.   
Total CPU time:  250.1450 s


| Instance Name       | Grid Size | Solvable? | SAT Solver Runs | Variables | Clauses | Total CPU Time (s) |
|---------------------|-----------|-----------|-----------------|-----------|---------|---------------------|
| `Medium_solv.txt`   | 6x6       | Yes       | 3               | 84        | 315     | 0.00428            |
| `Medium_unsolv.txt` | 6x6       | No        | 1               | 84        | 354     | 0.00110            |
| `Large_solv.txt`    | 29x29     | Yes       | 52              | 1740      | 8723    | 0.82173            |
| `VeryLarge_solv.txt`| 30x30     | Yes       | 424             | 1860      | 14010   | 47.15049           |
| `ExtraLarge_solv.txt`| 30x35    | Yes       | 788             | 2165      | 21236   |  250.1450          |

The program solves small to medium-sized Slitherlink grids with good computational time, but larger grids significantly increase the number of SAT solver iterations and CPU time due to the complexity of enforcing single-loop constraints. Optimization may be needed for handling grids beyond 30x30 more efficiently.

# Slitherlink Solver Project

## 1. Project Overview
This project is a solver for the Slitherlink puzzle using a **SAT-based approach**. Slitherlink is a logic puzzle where the goal is to form a single continuous loop on a grid, based on numerical clues provided in the cells. The solver encodes the Slitherlink constraints as a SAT problem and uses a SAT solver (Glucose) to find a solution.

## 2. Problem Definition
Slitherlink is played on a rectangular grid. Each cell in the grid may contain a number between 0 and 3, or be empty. The numbers indicate how many of the four edges around that cell are part of the loop. The loop must:
- Form a single, continuous, closed cycle.
- Not intersect itself.
- Satisfy the numerical constraints given in the grid cells.

## 3. Input Format
The input can be provided either as a file or through the command line. The grid is defined as follows:
- The first line specifies the grid dimensions: `height width`.
- Each subsequent line represents a row in the grid. Cells can contain numbers (`0`, `1`, `2`, `3`) or be empty (`.`).

**Example Input:**
6 6
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
The Slitherlink problem is encoded into SAT using the following constraints:
1. **Edge Constraints**: Define variables for horizontal and vertical edges.
2. **Number Constraints**:
   - For cells labeled `0`: None of the edges can be part of the loop.
   - For cells labeled `1`: Exactly one of the four edges must be part of the loop.
   - For cells labeled `2`: Exactly two of the four edges must be part of the loop.
   - For cells labeled `3`: Exactly three of the four edges must be part of the loop.
3. **Loop Constraints**:
   - Enforces that the loop forms a single continuous cycle without intersections.
   - Ensures the loop connects properly at each vertex (point) in the grid.

## 6. Solver Usage
The solver uses the **Glucose SAT solver** to find a solution to the encoded SAT problem.

### Command Line Arguments:
- `-i` or `--input`: Path to the input file containing the Slitherlink instance.
- `-o` or `--output`: Path to the output file for the CNF formula (default: `formula.cnf`).
- `-s` or `--solver`: The SAT solver to use (default: Glucose).
- `-v` or `--verb`: Verbosity level of the SAT solver (default: 1).

**Example Command:**
```bash
python Slitherlink.py -i input.txt -o formula.cnf -s glucose -v 1
```

## 7. Implementation Details
- The grid is parsed, and edges and cells are initialized based on the input.  
- The problem is encoded as a SAT problem using CNF (Conjunctive Normal Form) clauses.  
- The SAT solver is run on the generated CNF formula, and the result is interpreted back into a solution for the Slitherlink puzzle.
## 8. Constraints and CNF Generation
- The constraints are generated for each cell based on its value.
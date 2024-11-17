import subprocess
from internal import *
import sys
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Slitherlink Solver")
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Path to the input file containing the Slitherlink instance."
    )
    parser.add_argument(
        "-o", "--output",
        default="formula.cnf",
        type=str,
        help="Output file for the DIMACS format (CNF formula)."
    )
    parser.add_argument(
        "-s", "--solver",
        default="glucose",
        type=str,
        help="The SAT solver to be used (default: glucose)."
    )
    parser.add_argument(
        "-v", "--verb",
        default=1,
        type=int,
        choices=range(0, 2),
        help="Verbosity of the SAT solver (0: silent, 1: verbose)."
    )
    return parser.parse_args()

def read_slitherlink_instance(args):
    if args.input:
        # Read from file
        return read_from_file(args.input)
    else:
        # Read interactively from the command line
        return read_from_cmd()

def read_from_file(file_path):
    with open(file_path, 'r') as file:
        # Read grid dimensions
        height, width = map(int, file.readline().strip().split())

        if height <= 0 or width <= 0:
            raise ValueError("Grid dimensions must be positive integers.")

        grid = []
        for row_index in range(height):
            row = file.readline().strip().split()
            if len(row) != width:
                raise ValueError(f"Row {row_index + 1} does not match the specified width of {width}.")

            # Validate cell values and convert to integers
            validated_row = []
            for value in row:
                if value == '.':
                    validated_row.append(None)
                elif value.isdigit() and 0 <= int(value) <= 3:
                    validated_row.append(int(value))
                else:
                    raise ValueError(f"Invalid value '{value}' at row {row_index + 1}. Must be 0, 1, 2, 3, or '.' for empty cells.")

            grid.append(validated_row)

    return grid

def read_from_cmd():
    # Get grid dimensions from user input
    height = int(input("Enter the number of rows (height): "))
    width = int(input("Enter the number of columns (width): "))

    if height <= 0 or width <= 0:
        raise ValueError("Grid dimensions must be positive integers.")

    print("Enter the grid values row by row (use '.' for empty cells):")
    grid = []
    for row_index in range(height):
        row = input(f"Row {row_index + 1}: ").strip().split()

        if len(row) != width:
            raise ValueError(f"Row {row_index + 1} does not match the specified width of {width}.")

        # Validate cell values and convert to integers
        validated_row = []
        for value in row:
            if value == '.':
                validated_row.append(None)
            elif value.isdigit() and 0 <= int(value) <= 3:
                validated_row.append(int(value))
            else:
                raise ValueError(f"Invalid value '{value}' at row {row_index + 1}. Must be 0, 1, 2, 3, or '.' for empty cells.")

        grid.append(validated_row)

    return grid

def write_cnf_to_file(cnf, num_vars, filename="input.cnf"):
    with open(filename, "w") as f:
        # Write the problem line: p cnf <num_vars> <num_clauses>
        num_clauses = len(cnf)
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        # Write each clause
        for clause in cnf:
            f.write(" ".join(map(str, clause)) + "\n")

def run_glucose(input_file="input.cnf", output_file="solution.txt"):
    # Run Glucose SAT solver
    result = subprocess.run(['./' + "glucose", '-model', input_file],stdout=subprocess.PIPE)

    return result

def print_slitherlink_result(result, cell_map, num_of_rows, num_of_cols, h_edges, v_edges):
    # Parse the SAT solver output
    output = result.stdout.decode('utf-8')
    for line in result.stdout.decode('utf-8').split('\n'):
        print(line)                 # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself
    assignment = {}
    
    # Extract the model from the solver output
    for line in output.split('\n'):
        if line.startswith("v"):
            vars = line.split(" ")
            vars.remove("v")
            for var in vars:
                if var != "0":
                    var_id = abs(int(var))
                    is_in_loop = int(var) > 0
                    assignment[var_id] = is_in_loop

    print("\n##################[ Slitherlink Grid Result ]##################")

    for i in range(num_of_rows + 1):
        # Construct strings for the horizontal edges and the cells
        upper_edge_str = "*"
        cell_value_str = ""

        # Horizontal edges (top row or between cells)
        for j in range(num_of_cols):
            h_edge = h_edges[i][j]
            if h_edge and assignment.get(h_edge.id, False):
                upper_edge_str += "─"
            else:
                upper_edge_str += " "
            upper_edge_str += "*"  # Space between cells

        print(upper_edge_str)

        if i < num_of_rows:
            for j in range(num_of_cols + 1):
                # Vertical edges and cell values
                v_edge = v_edges[i][j] if j < num_of_cols + 1 else None
                if v_edge and assignment.get(v_edge.id, False):
                    cell_value_str += "│"
                else:
                    cell_value_str += " "
                    
                if j < num_of_cols:
                    cell = cell_map[i][j]
                    cell_value = cell.value if cell.value is not None else " "
                    cell_value_str += f"{cell_value}"  # Fixed width for cell value

            print(cell_value_str)

    print("\n##############################################################\n")

def print_points_with_edges(points, num_of_rows, num_of_cols):
    print("\n##################[ Points and Their Edges ]##################\n")

    for i in range(num_of_rows + 1):
        for j in range(num_of_cols + 1):
            point = points[i][j]
            if point is not None:
                print(f"Point ({i}, {j}):")
                
                # Up Edge
                if point.up_edge is not None:
                    edge = point.up_edge
                    position = "Horizontal" if edge.is_horizontal else "Vertical"
                    print(f"  Up Edge: ID={edge.id}, {position}")
                else:
                    print("  Up Edge: None")

                # Right Edge
                if point.right_edge is not None:
                    edge = point.right_edge
                    position = "Horizontal" if edge.is_horizontal else "Vertical"
                    print(f"  Right Edge: ID={edge.id}, {position}")
                else:
                    print("  Right Edge: None")

                # Down Edge
                if point.down_edge is not None:
                    edge = point.down_edge
                    position = "Horizontal" if edge.is_horizontal else "Vertical"
                    print(f"  Down Edge: ID={edge.id}, {position}")
                else:
                    print("  Down Edge: None")

                # Left Edge
                if point.left_edge is not None:
                    edge = point.left_edge
                    position = "Horizontal" if edge.is_horizontal else "Vertical"
                    print(f"  Left Edge: ID={edge.id}, {position}")
                else:
                    print("  Left Edge: None")

                print()  # Add an empty line for better readability

    print("\n##################[ End of Points and Their Edges ]##################\n")


def debug_print_cell_constraints(cell, clause):
    print("\n##################[ Cell Constraints Debug ]##################")
    print(f"Cell at ({cell.row}, {cell.col}):")
    
    # Print the connected edges
    if cell.up_edge:
        print(f"  Up Edge: ID={cell.up_edge.id}, Horizontal={cell.up_edge.is_horizontal}")
    else:
        print("  Up Edge: None")

    if cell.right_edge:
        print(f"  Right Edge: ID={cell.right_edge.id}, Horizontal={cell.right_edge.is_horizontal}")
    else:
        print("  Right Edge: None")

    if cell.down_edge:
        print(f"  Down Edge: ID={cell.down_edge.id}, Horizontal={cell.down_edge.is_horizontal}")
    else:
        print("  Down Edge: None")

    if cell.left_edge:
        print(f"  Left Edge: ID={cell.left_edge.id}, Horizontal={cell.left_edge.is_horizontal}")
    else:
        print("  Left Edge: None")

    # Print the constraint clause
    print("Generated Clause:", clause)
    print("##############################################################\n")

def debug_print_cnf(cnf):
    print("\n##################[ CNF Formula Debug ]##################")
    for clause in cnf:
        print(" ".join(map(str, clause)))
    print("#########################################################\n")

def debug_print_slitherlink_grid(cell_map, h_edges, v_edges, num_of_rows, num_of_cols):
    print("\n##################[ Slitherlink Grid Debug ]##################")

    for i in range(num_of_rows):
        # Construct the strings for horizontal edges and vertical edges with cell values
        upper_edge_str = ""
        cell_value_str = ""

        for j in range(num_of_cols):
            cell = cell_map[i][j]
            up_edge = cell.up_edge
            right_edge = cell.right_edge
            down_edge = cell.down_edge
            left_edge = cell.left_edge
            cell_value = cell.value if cell.value is not None else " "

            # Construct the upper horizontal edge string
            if up_edge and up_edge.id is not None:
                upper_edge_str += " ──"
            else:
                upper_edge_str += "   "

            # Construct the vertical edge and cell value string
            if left_edge and left_edge.id is not None:
                cell_value_str += "│"
            else:
                cell_value_str += " "

            cell_value_str += f" {cell_value} "

            # Handle the rightmost vertical edge for the cell
            if right_edge and right_edge.id is not None:
                cell_value_str += "│"
            else:
                cell_value_str += " "

        # Print the constructed strings for the current row
        print(upper_edge_str)
        print(cell_value_str)

    # Print the bottom horizontal edges
    bottom_edge_str = ""
    for j in range(num_of_cols):
        down_edge = cell_map[num_of_rows - 1][j].down_edge
        if down_edge and down_edge.id is not None:
            bottom_edge_str += "── "
        else:
            bottom_edge_str += "   "
    print(bottom_edge_str)

    print("\n##############################################################\n")


#instance = [[2,2],[2,2]]
#instance = [[2,None],[2,None],[None,3]]
#instance = [[3,2,2],[2,None,2],[2,3,2]]

instance = [
    [None, None, None, None, 0, None],
    [3, 3, None, None, 1, None],
    [None, None, 1, 2, None, None],
    [None, None, 2, 0, None, None],
    [None, 1, None, None, 1 , 1 ],
    [None, 2, None, None, None, None]
]

if __name__ == "__main__":
    args = parse_arguments()
    try:
        ##height, width, grid = read_from_args(args)
        #debug_print_cnf(cnf)
        #grid = read_slitherlink_instance(args)
        cnf, h_edges, v_edges, cell_map, num_vars = encode(instance)

        write_cnf_to_file(cnf, num_vars )
        result = run_glucose("input.cnf", "solution.txt")
        print_slitherlink_result(result,cell_map,len(instance), len(instance[0]), h_edges, v_edges)

        while True:
            pass
    except Exception as e:
        print(f"Error: {e}")









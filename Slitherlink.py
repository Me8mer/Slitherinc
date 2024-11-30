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



def print_slitherlink_result(assignment,result, cell_map, num_of_rows, num_of_cols, h_edges, v_edges):
    # Parse the SAT solver output
    output = result.stdout.decode('utf-8')
    for line in result.stdout.decode('utf-8').split('\n'):
        print(line)                 # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself
    
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

def debug_print_cnf(cnf):
    print("\n##################[ CNF Formula Debug ]##################")
    for clause in cnf:
        print(" ".join(map(str, clause)))
    print("#########################################################\n")



#instance = [[2,2],[2,2]]
#instance = [[2,None],[2,None],[None,3]]
#instance = [[3,2,2],[2,None,2],[2,3,2]]

# instance = [
#     [None, None, None, None, 0, None],
#     [3, 3, None, None, 1, None],
#     [None, None, 1, 2, None, None],
#     [None, None, 2, 0, None, None],
#     [None, 1, None, None, 1 , 1 ],
#     [None, 2, None, None, None, None]
# ]

instance = [
    [None, None, None, 2, None, None],
    [3, 3, None, None, 1, 0],
    [None, None, 1, 2, None, None],
    [None, None, 2, 0, None, None],
    [None, 1, None, None, 1, 1],
    [None, 2, None, None, None, None]
]

if __name__ == "__main__":
    args = parse_arguments()
    try:
        ##height, width, grid = read_from_args(args)

        #instance = read_slitherlink_instance(args)
        result = iterative_solver(instance)
        if result == -1:
            print("Result is not found.")
        else:
            print_slitherlink_result(result[0],result[1],result[2],result[3],result[4],result[5], result[6])
        #debug_print_cnf(cnf)
    except Exception as e:
        print(f"Error: {e}")









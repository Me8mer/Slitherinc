#!/usr/bin/env python3
from internal import *
import sys
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Slitherlink SAT Solver: Solve Slitherlink puzzles using a SAT-based approach."
        )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Path to the input file containing the Slitherlink instance."
    )
    parser.add_argument("--print-cnf",
        action="store_true",
        help="Print the CNF formula to the console.")
    parser.add_argument("--collect-stats",
    action="store_true", 
    help="Collect and print SAT solver statistics.")
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



def print_slitherlink_result(assignment, cell_map, num_of_rows, num_of_cols, h_edges, v_edges):
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


def print_DIMACS_cnf(cnf):
    """
    Write the CNF formula to a file and optionally print it to the console.
    """
    for clause in cnf:
        line = " ".join(map(str, clause)) + "\n"
        print(line.strip())

def print_stats(stats):
    stats_strings = stats[0]
    num_of_SAT_runs = stats[1]
    total_CPU_time = stats[2]
    print(stats_strings)
    print("Total CPU time:", total_CPU_time)
    print(f"SAT solver was run {num_of_SAT_runs} times")
    

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

# instance = [
#     [None, None, None, 2, None, None],
#     [3, 3, None, None, 1, 0],
#     [None, None, 1, 2, None, None],
#     [None, None, 2, 0, None, None],
#     [None, 1, None, None, 1, 1],
#     [None, 2, None, None, None, None]
# ]

if __name__ == "__main__":
    args = parse_arguments()
    try:
        instance = read_slitherlink_instance(args)
        result, assignment,  cell_map, num_of_rows, num_of_cols, h_edges, v_edges, cnf, stats = encode(instance, args.collect_stats)
        if args.collect_stats: print_stats(stats)
        if result == -1:
            print("Result is not found.")
        else:
            if args.print_cnf: print_DIMACS_cnf(result[7])
            print_slitherlink_result(assignment, cell_map, num_of_rows, num_of_cols, h_edges, v_edges)
           
    except Exception as e:
        print(f"Error: {e}")









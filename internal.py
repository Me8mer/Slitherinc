import subprocess
'''
class for edges. Ma main vars for constraints
'''
class Edge:
    _id_counter = 1 

    def __init__(self, is_horizontal):
        self.id = Edge._id_counter
        self.is_horizontal = is_horizontal
        Edge._id_counter += 1
        
'''
Keeps track of all edges around the cell and the value of the cell.
'''
class Cell:
    def __init__(self, up_edge, right_edge, down_edge, left_edge, corner_cell, value, row, col ):
        self.up_edge = up_edge
        self.right_edge = right_edge
        self.down_edge = down_edge
        self.left_edge = left_edge
        self.corner_cell = corner_cell
        self.value = value
        self.row = row
        self.col = col

    def get_connected_edges(self):
    # Returns a list of all edges connected to this point (ignores None values)
        return (edge for edge in [self.up_edge.id, self.right_edge.id, self.down_edge.id, self.left_edge.id] if edge is not None)
'''
Keeps track of all edges connected to the point.
'''
class Point:
    def __init__(self, up_edge=None, right_edge=None, down_edge=None, left_edge=None):
        self.up_edge = up_edge
        self.right_edge = right_edge
        self.down_edge = down_edge
        self.left_edge = left_edge

    def get_connected_edges(self):
    # Returns a list of all edges connected to this point (ignores None values)
        return [edge for edge in [self.up_edge, self.right_edge, self.down_edge, self.left_edge] if edge is not None]


# creates edges based on num of rows and cols of the grid. 
def create_edges(num_of_rows, num_of_cols):
    y = num_of_rows       
    x = num_of_cols  
      
    h_edges = [[Edge(True) for _ in range(num_of_cols)] for _ in range(num_of_rows + 1)]

    # Create vertical edges: num_of_rows rows, (num_of_cols + 1) columns
    v_edges = [[Edge(False) for _ in range(num_of_cols + 1)] for _ in range(num_of_rows)]
    return (h_edges,v_edges)

# Creates cells based on  num of rows and cols of the grid and the values from instance map
def create_cells(h_edges, v_edges, instance_map ):
    num_of_rows = len(instance_map)
    num_of_cols = len(instance_map[0])
    cells = []
    for row in range(num_of_rows):
        rows = []
        for col in range(num_of_cols):
            up_edge = h_edges[row][col]
            right_edge = v_edges[row][col + 1]
            down_edge = h_edges[row + 1][col]
            left_edge = v_edges[row][col]
            corner_cell = (row == 0 or row == num_of_rows - 1) and (col == 0 or col == num_of_cols - 1)
            value = instance_map[row][col]
            cell = Cell(up_edge, right_edge, down_edge, left_edge, corner_cell, value, row,col)
            rows.append(cell)
        cells.append(rows)
        
    return (cells)

# creates points and adds the proper edges to them
def create_points(h_edges, v_edges, num_of_rows, num_of_cols):
    points = [[None for _ in range(num_of_cols + 1)] for _ in range(num_of_rows + 1)]
    for i in range(num_of_rows + 1):
        for j in range(num_of_cols + 1):
            # Horizontal edges
            up_edge = v_edges[i - 1][j] if i > 0 else None
            down_edge = v_edges[i][j] if i < num_of_rows else None

            # Vertical edges
            left_edge = h_edges[i][j - 1] if j > 0 else None
            right_edge = h_edges[i][j] if j < num_of_cols else None

            # Handle the last row and last column separately
            if i == num_of_rows:
                down_edge = None  # No down edge for the last row
            if j == num_of_cols:
                right_edge = None  # No right edge for the last column

            # Create the Point object with the assigned edges
            points[i][j] = Point(up_edge, right_edge, down_edge, left_edge)


    return points

def initialise_cells_and_points(instance_map):

    h_edges, v_edges = create_edges(len(instance_map),len(instance_map[0]))
    cell_map= create_cells(h_edges, v_edges, instance_map)
    point_map = create_points(h_edges,v_edges, len(instance_map), len(instance_map[0]))

    return (cell_map, point_map, h_edges, v_edges)

##########################################################
###################Constraints############################

def add_implication_one_to_more(left_edge, right_edges,cnf):
    for true_edge in right_edges:
        cnf.append([-left_edge, true_edge, 0])

def add_implication_two_to_two(left,right,cnf):
    for edge in right:
        negated_left = [-e for e in left]
        negated_left.extend([edge,0])
        cnf.append(negated_left)

def zero_or_two(edges, cnf):
    # Propagation constraints: If one edge is false, at least one of the others must be true
    for i in range(len(edges)):
        # Create a clause where the current edge is false and at least one of the others is true
        clause = [-edges[i]] + [edges[j] for j in range(len(edges)) if j != i]
        clause.append(0)  # End the clause with 0
        cnf.append(clause)

    # Pairwise constraints: No more than two true edges
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            for k in range(j + 1, len(edges)):
                cnf.append([-edges[i], -edges[j], -edges[k], 0])
# Creates loop constraints. Of one edge is true in a point there must be exactly two edges true in the point. 
# So exactly two true or all false in a point.
def create_loop_constraints(points, cnf):
    for point in points:
        edges = point.get_connected_edges()
        edge_ids = [edge.id for edge in edges if edge is not None]

        if len(edges) == 2:
            cnf.append([-edge_ids[0], edge_ids[1], 0])  
            cnf.append([edge_ids[0], -edge_ids[1], 0])    

        elif len(edges) > 2:
            # At least one true edge and propagation constraints
            zero_or_two(edge_ids,cnf)

def create_number_constraints(cells, cnf):
    for cell in cells:
        if cell.value != None:
            if cell.value == 0:
                zero_value(cell, cnf)
            elif cell.value == 1:
                one_value(cell, cnf)
            elif cell.value == 2:
                two_value(cell, cnf)
            elif cell.value == 3:
                three_value(cell, cnf)
## Constraints for 0,1,2,3 values of cells.
def zero_value(cell,cnf):
    up_id, right_id, down_id, left_id = cell.get_connected_edges()
    edges = [up_id, right_id, down_id, left_id]
    for edge in edges:
        cnf.append([-edge,0])

def one_value(cell, cnf):
    # Get the edge IDs from the cell
    up_id, right_id, down_id, left_id = cell.get_connected_edges()
    edges = [up_id, right_id, down_id, left_id]

    # At least one edge must be true
    cnf.append([up_id, right_id, down_id, left_id, 0])

    # Only one edge can be true: pairwise negations
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            cnf.append([-edges[i], -edges[j], 0])
    
def two_value(cell, cnf):
    # Get the edge IDs from the cell
    e1, e2, e3, e4 = cell.get_connected_edges()
    edges = [e1,e2,e3,e4]

    # at least one true
    cnf.append([e1, e2, e3, e4, 0])
    # Either zero or two constraints 
    zero_or_two(edges,cnf)
    
def three_value(cell, cnf):
    up_id, right_id, down_id, left_id = cell.get_connected_edges()
    edges = [up_id, right_id, down_id, left_id]
    cnf.append([-up_id, -right_id, -down_id, -left_id, 0])

    # Only one edge can be true: pairwise negations
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            cnf.append([edges[i], edges[j], 0])
### Multiple loops logic. Iteratively runs sat solver, adding constraints if it finds a loop.

def find_components(assignment, h_edges, v_edges):
    """
    Find connected components of edges based on the current SAT assignment.
    Groups edges into components.
    """
    graph = {}

    # Build graph from horizontal edges
    for i in range(len(h_edges)):
        for j in range(len(h_edges[i])):
            edge = h_edges[i][j]
            if assignment.get(edge.id, False):  # Edge is active
                point1 = (i, j)
                point2 = (i, j + 1)
                if point1 not in graph:
                    graph[point1] = []
                if point2 not in graph:
                    graph[point2] = []
                graph[point1].append((point2, edge))
                graph[point2].append((point1, edge))

    # Build graph from vertical edges
    for i in range(len(v_edges)):
        for j in range(len(v_edges[i])):
            edge = v_edges[i][j]
            if assignment.get(edge.id, False):  # Edge is active
                point1 = (i, j)
                point2 = (i + 1, j)
                if point1 not in graph:
                    graph[point1] = []
                if point2 not in graph:
                    graph[point2] = []
                graph[point1].append((point2, edge))
                graph[point2].append((point1, edge))

    # Find connected components
    visited = set()
    components = []

    def dfs(node):
        stack = [node]
        component_edges = []
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                for neighbor, edge in graph.get(current, []):
                    if neighbor not in visited:
                        stack.append(neighbor)
                    if edge not in component_edges:
                        component_edges.append(edge)
        return component_edges

    # Identify components
    for point in graph:
        if point not in visited:
            edges = dfs(point)
            components.append(edges)

    return components

def add_loop_elimination_constraints(components, assignment, cnf):
    for component in components:
        new_constraint = []
        for component_edge in component:         
            if assignment.get(component_edge.id, False):  # If edge is part of a loop
                # Prevent this edge from forming a disjoint cycle in the next iteration
                new_constraint.append(-component_edge.id)
        new_constraint.append(0)
        cnf.append(new_constraint)

def write_cnf_to_file(cnf, num_vars, filename="input.cnf"):
    with open(filename, "w") as f:
        # Write the problem line: p cnf <num_vars> <num_clauses>
        num_clauses = len(cnf)
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        # Write each clause
        for clause in cnf:
            f.write(" ".join(map(str, clause)) + "\n")

def run_glucose():
    # Run Glucose SAT run_gl
    input_file="input.cnf"
    result = subprocess.run(['./' + "glucose", '-model', input_file],stdout=subprocess.PIPE)
    return result

def run_sat_solver(cnf, num_vars,collect_stats=False):
    write_cnf_to_file(cnf, num_vars, filename="input.cnf")
    result = run_glucose()
    if collect_stats:
        # Collect all lines starting with 'c'
        output = result.stdout.decode('utf-8')
        stats = ""
        total_cpu_time = 0.0
        for line in output.splitlines():
            if line.startswith("c"):
                stats += line
                stats += '\n'
                if "c CPU time" in line:
                    total_cpu_time += float(line.split(":")[1].strip().split()[0])
        return result, stats, total_cpu_time
    return result, "", 0.0

def parse_sat_solution(result):
    output = result.stdout.decode('utf-8')
    assignment = {}
    for line in output.split('\n'):
        if line.startswith("v"):
            vars = line.split(" ")
            vars.remove("v")
            for var in vars:
                if var != "0":
                    var_id = abs(int(var))
                    is_in_loop = int(var) > 0
                    assignment[var_id] = is_in_loop
    return assignment


def encode(instance,collect_stats=False):
    """
    Main function to iteratively solve the Slitherlink problem.
    """
    cnf = []
    cell_map, point_map, h_edges, v_edges = initialise_cells_and_points(instance)
    edges = [edge for row in h_edges for edge in row] + [edge for row in v_edges for edge in row]
    points = [point for row in point_map for point in row]
    cells = [cell for row in cell_map for cell in row]
    create_number_constraints(cells, cnf)
    create_loop_constraints(points, cnf)

    num_vars = len(edges)

    total_runs = 0
    total_cpu_time = 0.0
    all_stats = ""

    while True:
        result, stats, cpu_time = run_sat_solver(cnf, num_vars, collect_stats)
        if collect_stats:
            all_stats += "\n"
            all_stats += stats
            total_cpu_time += cpu_time
            total_runs += 1

        if result.returncode != 10:  # UNSAT
            return result, None, cell_map, len(instance), len(instance[0]), h_edges, v_edges, cnf, (all_stats, total_runs, total_cpu_time)
        
        assignment = parse_sat_solution(result)
        components = find_components(assignment, h_edges, v_edges)
        if len(components) == 1:
           return result, assignment, cell_map, len(instance), len(instance[0]), h_edges, v_edges, cnf, (all_stats, total_runs, total_cpu_time)
        add_loop_elimination_constraints(components, assignment, cnf)

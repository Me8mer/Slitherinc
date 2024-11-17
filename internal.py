class Edge:
    _id_counter = 1 

    def __init__(self, is_horizontal):
        self.id = Edge._id_counter
        self.is_horizontal = is_horizontal
        Edge._id_counter += 1
    
    def create_flow(self):
        flow = Edge._id_counter
        Edge._id_counter += 1
        return flow

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

class Point:
    def __init__(self, up_edge=None, right_edge=None, down_edge=None, left_edge=None):
        self.up_edge = up_edge
        self.right_edge = right_edge
        self.down_edge = down_edge
        self.left_edge = left_edge

    def get_connected_edges(self):
    # Returns a list of all edges connected to this point (ignores None values)
        return [edge for edge in [self.up_edge, self.right_edge, self.down_edge, self.left_edge] if edge is not None]
    
def create_edges(num_of_rows, num_of_cols):
    y = num_of_rows       
    x = num_of_cols  
      
    h_edges = [[Edge(True) for _ in range(num_of_cols)] for _ in range(num_of_rows + 1)]

    # Create vertical edges: num_of_rows rows, (num_of_cols + 1) columns
    v_edges = [[Edge(False) for _ in range(num_of_cols + 1)] for _ in range(num_of_rows)]
    return (h_edges,v_edges)

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


def add_subtour_elimination_constraints_fixed(point_map, edges, cnf):
    """
    Adds subtour elimination constraints to ensure a single loop in Slitherlink.
    Fixes the issue by correctly mapping edge indices to point indices.
    """
    num_points = len(point_map) * len(point_map[0])
    loop_vars = list(range(max(edge.id for edge in edges) + 1, max(edge.id for edge in edges) + 1 + num_points))

    # 1. Initialize auxiliary loop variables for each point
    for i in range(num_points):
        cnf.append([loop_vars[i], 0])  # Each point starts as part of the loop

    # Helper function to get point indices from edge connections
    def get_point_indices(edge):
        for row_index, row in enumerate(point_map):
            for col_index, point in enumerate(row):
                connected_edges = point.get_connected_edges()
                if edge in connected_edges:
                    return row_index * len(point_map[0]) + col_index
        return None

    # 2. Subtour Elimination: Prevent small disjoint loops
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            edge_i = edges[i]
            edge_j = edges[j]

            if edge_i is not None and edge_j is not None:
                point_index_i = get_point_indices(edge_i)
                point_index_j = get_point_indices(edge_j)

                if point_index_i is not None and point_index_j is not None:
                    # If both edges are selected, they cannot form a disjoint cycle
                    cnf.append([-edge_i.id, -edge_j.id, loop_vars[point_index_i], loop_vars[point_index_j], 0])
                    cnf.append([edge_i.id, -loop_vars[point_index_i], -loop_vars[point_index_j], 0])
                    cnf.append([edge_j.id, -loop_vars[point_index_i], -loop_vars[point_index_j], 0])

    # 3. Single Loop Check: Ensure all points belong to a single loop component
    main_loop_var = loop_vars[0]
    for loop_var in loop_vars:
        cnf.append([-main_loop_var, loop_var, 0])
        cnf.append([main_loop_var, -loop_var, 0])



def encode(instance):
    cnf = []
    cell_map, point_map, h_edges, v_edges = initialise_cells_and_points(instance)
    edges = [edge for row in h_edges for edge in row] + [edge for row in v_edges for edge in row]
    points = [point for row in point_map for point in row]
    cells = [cell for row in cell_map for cell in row]
    create_number_constraints(cells, cnf)
    create_loop_constraints(points, cnf)
    #add_subtour_elimination_constraints_fixed(point_map, edges, cnf)
    num_of_vars = len(edges)
    return (cnf, h_edges, v_edges, cell_map, num_of_vars)

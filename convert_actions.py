columns = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
knight_moves = {56: (1,-2), 57: (2,-1), 58: (2,1), 59: (1,2),
                60: (-1,2), 61: (-2,1), 62: (-2,-1), 63: (-1,-2)}

directions = {0: (0,-1), 1: (1,-1), 2: (1,0), 3: (1,1), 4: (0,1), 5: (-1,1), 6: (-1,0), 7: (-1,-1)}

underpromotion_pieces = {0: "r", 1: "b", 2: "n"}
underpromotion_directions = {0: -1, 1: 0, 2: 1}

def convert_action(action):
    assert isinstance(action, int)
    #piece position
    row = int(action / (8 * 73))
    column = int(action / 73) - row * 8
    #to action in range [0...73]
    action -= int(action / 73) * 73

    if action < 56:
        #direction of the move
        direction = directions[int(action / 8)]
        #distance to move
        distance = action - int(action / 7) * 7 + 1 
        #check if in bounds
        if _in_bounds(column + distance * direction[0], row + distance * direction[1]):
            out = "%s%d%s%d" % (columns[column], 8-row, columns[column + distance * direction[0]], 8 - (row + distance * direction[1]))
            if (row == 6 and row + distance * direction[1] == 7) or (row == 1 and row + distance * direction[1] == 0):
                out += "q"
            return out
        return None
    elif action >= 56 and action < 64:
        move = knight_moves[action]
        #check if in bounds
        if _in_bounds(move[0] + column, move[1] + row):
            return "%s%d%s%d" % (columns[column], 8-row, columns[column + move[0]], 8 - (row + move[1]))
    else:
       action-=64
       promote_to = underpromotion_pieces[action - 3 * int(action/3)]
       promotion_direction = underpromotion_directions[int(action/3)]
       if (row == 1 or row == 6) and column + promotion_direction >= 0 and column + promotion_direction <= 7:
           return "%s%d%s%d%s" % (columns[column], 8-row, columns[column + promotion_direction], 8 if row == 1 else 1, promote_to)
       return None

def _in_bounds(column_to, row_to):
    if column_to >= 0 and column_to <= 7:
        if row_to >= 0 and row_to <= 7:
            return True
        return False
    return False


columns_switched = {y:x for x,y in columns.items()}
knight_moves_switched = {y:x for x,y in knight_moves.items()}

directions_switched = {y:x for x,y in directions.items()}

underpromotion_pieces_switched = {y:x for x,y in underpromotion_pieces.items()}
underpromotion_directions_switched = {y:x for x,y in underpromotion_directions.items()}

def convert_move(move):
    assert isinstance(move, str)
    action = (8 - int(move[1])) * 8 * 73 + columns_switched[move[0]] * 73
    distance_column = columns_switched[move[2]] - columns_switched[move[0]]
    distance_row = int(move[1]) - int(move[3])
    if len(move) == 4 or (len(move) == 5 and move[4] == "q"):
        if (distance_column, distance_row) in knight_moves_switched:
            return action + knight_moves_switched[(distance_column, distance_row)]
        else:
            direction = (int(distance_column / abs(distance_column)) if distance_column is not 0 else 0, int(distance_row / abs(distance_row)) if distance_row is not 0 else 0)
            action += directions_switched[direction]*7 - 1
            action += abs(distance_column) if distance_column is not 0 else abs(distance_row)
            return action
        return None
    elif len(move) == 5:
        action += 64
        promote_to_num = underpromotion_pieces_switched[move[4]]
        direction = underpromotion_directions_switched[distance_column] 
        return action + direction * 3 + promote_to_num
    return None

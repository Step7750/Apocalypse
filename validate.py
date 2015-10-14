def isValidMove(row, column, row_new, column_new):
    knight_moves = [[-2, 1], [-1, 2], [1, 2], [2, 1], [2, -1], [-1, -2], [1, -2], [-2, -1]]
    if 1 <= row_new <= 8 and 1 <= column_new <= 8 and 1 <= row <= 8 and 1 <= column <= 8:
        for i in knight_moves:
            if row_new == (i[0] + row) and column_new == (i[1] + column):
                return True
        return False
    else:
        return False

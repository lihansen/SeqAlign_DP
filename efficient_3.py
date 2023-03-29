import sys
import time
import psutil

GAP_PENALTY = 30
MISMATCH_PENALTY = {
    0: 0,  # same chars' diff == 0
    ord('C') - ord('A'): 110,
    ord('G') - ord('A'): 48,
    ord('T') - ord('A'): 94,
    ord('G') - ord('C'): 118,
    ord('T') - ord('C'): 48,
    ord('T') - ord('G'): 110,
}


def generator(base, repeater):
    """
    Generate new string based on base and its repeater

    Returns a new generated string

    Parameter base: the base string
    Precondition: 0 <= base <= 10

    Parameter repeater: a list of integers as repeaters for base
    Precondition: 1 <= 2^len(repeater) * len(s2) <= 2000
    """
    for index in repeater:
        base = base[:index + 1] + base + base[index + 1:]
    return base


def readFileInput(fileName):
    """
    function readFileInput: read file content and generate strings
    """
    base = ""
    curr, result = [], []
    try:
        with open(fileName, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.isnumeric():
                    curr.append(int(line))
                else:
                    if base:
                        result.append(generator(base, curr))
                    base = line
                    curr = []
            result.append(generator(base, curr))
            f.close()
    except IOError:
        print('Unable to open file')
        exit(-1)
    finally:
        return result


def dp_basic(str1, str2):
    """
    Solve Sequence Alignment problem by using dynamic programming
    Start from right-bottom([len(str1) + 1][len(str2) + 1]) and end at left-top ([0][0])

    Returns a 2D list containing all weights under corresponding strategies

    Parameter str1: the first string
    Precondition: 1 <= len(str1) <= 2000

    Parameter str2: the second string
    Precondition: 1 <= len(str2) <= 2000
    """
    grid = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]  # initialize 2D array
    grid[-1] = [i * GAP_PENALTY for i in range(len(str2), -1, -1)]  # initialize most-bottom side
    for i in range(len(str1) + 2):  # initialize most-right side
        grid[-i][len(str2)] = (i - 1) * GAP_PENALTY

    for col in range(len(str2) - 1, -1, -1):
        for row in range(len(str1) - 1, -1, -1):
            key = abs(ord(str1[row]) - ord(str2[col]))  # key in MISMATCH_PENALTY hashmap
            grid[row][col] = min(
                MISMATCH_PENALTY[key] + grid[row + 1][col + 1],
                GAP_PENALTY + grid[row + 1][col],
                GAP_PENALTY + grid[row][col + 1],
            )
    return grid


def dp_efficient(str1, str2):
    """
    Solve Sequence Alignment DAC problem by using dynamic programming

    Returns a list containing all weights of last colum

    Parameter str1: the first string
    Precondition: 1 <= len(str1) <= 20000

    Parameter str2: the second string
    Precondition: 1 <= len(str2) <= 20000
    """
    grid = [[0] * 2 for _ in range(len(str1) + 1)]  # initialize 2D array
    for i in range(len(str1) + 1):  # initialize most-right side
        grid[i][0] = i * GAP_PENALTY

    for j in range(1, len(str2) + 1):
        grid[0][1] = j * GAP_PENALTY
        for i in range(1, len(str1) + 1):
            key = abs(ord(str1[i - 1]) - ord(str2[j - 1]))  # key in MISMATCH_PENALTY hashmap
            grid[i][1] = min(
                MISMATCH_PENALTY[key] + grid[i - 1][0],
                GAP_PENALTY + grid[i - 1][1],
                GAP_PENALTY + grid[i][0]
            )

        # first colum <- last colum
        for row in range(len(str1) + 1):
            grid[row][0] = grid[row][1]

    last_col = []   # get elements from last colum
    for row in grid:
        last_col.append(row[-1])
    return last_col


def find_shortest_path(grid):
    """
    Find the optimized path for backing to origin

    Returns a list of int as an optimized path containing all steps by passing the lowest weight under [grid]
    Starts from left-top ([0][0]) and ends at right-bottom([len(str1) + 1][len(str2) + 1]), which is the origin
     0 - diagonalized moving (move right then downward at the same time);
     1 - move one step to right (gap str1);
    -1 - move one step downward (gap str2);
    e.g. path = [0, 0, 1, 0, -1, 0] -> moving \(diago), \, ->(right), \, |(down), \

    Parameter grid: a 2D list returned by dp_basic() which contains all weights under corresponding strategies
    Precondition: [len(grid) == len(str1) + 1] AND [len(grid[i]) == len(str2) + 1 where 0 <= i <= len(str1)]
    """
    path = []  # initialize path
    col = row = 0
    len_col, len_row = len(grid[0]), len(grid)
    while row < len_row - 1 and col < len_col - 1:
        path.append(0)  # by default, go (diago)

        # condition_1: if better movement available, go either (down) or (right) instead of (diago)
        condition_1 = min(grid[row][col + 1], grid[row + 1][col]) < grid[row + 1][col + 1]

        # condition_2: special dia case e.g. ("A", "C"), cannot go (diago) by skipping more than one GAP_PENALTY
        # e.g.  [ 60  30      by default, go (diago), but it has go either (right then down) or (down then right)
        #         30   0]     go (diago) by jumping more than one GAP_PENALTY would result in error
        condition_2 = abs(grid[row + 1][col + 1] - grid[row][col]) == GAP_PENALTY * 2

        if condition_1 or condition_2:
            # move (right)
            if grid[row][col + 1] < grid[row + 1][col]:
                path[-1] = 1
                row -= 1
            else:  # move (down)
                path[-1] = -1
                col -= 1
        col += 1
        row += 1

    # if reaches either bottom or right edge but not in origin, move horizontally right or vertically down.
    if row < len_row - 1:
        path += [-1] * (len_row - 1 - row)
    if col < len_col - 1:
        path += [1] * (len_col - 1 - col)

    return path


def alignment(arr, path):
    """
    Sequence Alignment based on path

    Returns a list of two strings as final output
    For each path[i]
     0 - diagonalized moving (move right then downward at the same time):
            append current chars in both arr[0](first string) and arr[1](second string) to str1 and str2 respectively
     1 - move one step to right (gap str1):
            gap('_') arr[0], append current char at arr[1] to str2
    -1 - move one step downward (gap str2):
            gap('_') arr[1], append current char at arr[0] to str1

        e.g. arr = ['A', 'C'], grid = [60, 30], path: [-1, 1]
                                      [30, 0]
        grid moving |(down)(60 to 30), then ->(right)(30 to 0) the track looks like 'L'.
            * path[0] = -1: _, C
            * path[1] = 1: _A, C_ (this is the final result)

    Parameter arr: a list contains two strings returned by readFileInput() which is the original inputs
    Precondition: len(arr) == 2

    Parameter path: a list of int as an optimized path containing all steps by passing the lowest weight under [grid]
    Precondition: path can only have 0, 1, and -1.
    """
    str1, str2 = "", ""
    idx1 = idx2 = 0
    for i in range(len(path)):
        if path[i] == 0:
            str1 += arr[0][idx1]
            str2 += arr[1][idx2]
        elif path[i] == 1:
            str1 += '_'
            str2 += arr[1][idx2]
            idx1 -= 1
        else:
            str1 += arr[0][idx1]
            str2 += '_'
            idx2 -= 1

        idx1 += 1
        idx2 += 1

    return [str1, str2]


def dac(str_x, str_y, res):
    """
    Divide and Conquer algorithm to split string X and Y

    Parameter str_x: the first string
    Precondition: 1 <= len(str_x) <= 2000

    Parameter str_y: the second string
    Precondition: 1 <= len(str_y) <= 2000

    Parameter result: output the results: cost, first and second alignments
    Precondition: len(result) == 3
    """
    len_x, len_y = len(str_x), len(str_y)
    if len_x <= 2 or len_y <= 2:    # base case
        grid = dp_basic(str_x, str_y)
        path = find_shortest_path(grid)
        ans = alignment([str_x, str_y], path)
        res[0] += grid[0][0]    # update cost
        res[1] += ans[0]    # update two strings
        res[2] += ans[1]
    else:
        left = dp_efficient(str_x, str_y[0: len_y // 2])    # run dp
        right = dp_efficient(str_x[::-1], str_y[len_y // 2:len_y][::-1])[::-1]
        for i in range(len(right)):     # add up and find minimum number
            right[i] += left[i]
        idx = right.index(min(right))
        dac(str_x[0:idx], str_y[0:len_y // 2], res)
        dac(str_x[idx:len_x], str_y[len_y // 2:len_y], res)


def run_algorithm_efficient(path_in):
    """
    Returns a list containing [min cost, str1, str2]
    readFileInput() -> dac()

    Parameter path_in: input file
    Precondition: the input file is exist and valid
    """
    res = [0, "", ""]   # results holder
    arr = readFileInput(path_in)    # read input
    dac(arr[0], arr[1], res)    # run divide and conquer
    res[0] = str(res[0])
    return res


def process_memory():
    """
    Returns memory used
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed


def time_wrapper(path_in):
    """
    Returns results: a list containing [min cost, str1, str2, time taken]

    Parameter path_in: input file
    Precondition: the input file is exist and valid
    """
    start_time = time.time()
    results = run_algorithm_efficient(path_in)  # call algorithm
    end_time = time.time()
    time_taken = (end_time - start_time) * 1000
    results.append(str(time_taken))
    return results


def output_result(path_out, results):
    """
    Output results(5 lines) to a file

    Parameter path_out: output file
    Precondition: has the permission to create a file under such directory
    Parameter results: [min cost, str1, str2, time taken, memory used]
    Precondition: five elements(strings) inside results
    """
    try:
        with open(path_out, "w") as f:
            for line in results:
                f.write(line + '\n')
            f.close()
    except IOError:
        print('Unable to write file')
        exit(-1)


def main():
    """
    Program Entry Point

    Read sys commands -> start timer and algorithm -> append memory -> output results
    """
    args = sys.argv[1:]  # read commands
    results = time_wrapper(args[0])
    results.append(str(process_memory()))  # [min cost, str1, str2, time taken, memory used]
    output_result(args[1], results)  # output results

    return 0


if __name__ == "__main__":
    main()

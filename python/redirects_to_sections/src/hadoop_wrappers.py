import sys


def get_pages_stdin():
    return '<page>'+''.join(sys.stdin)


def reduce_stdin(reduce_callback, delimiter="\t"):
    last_key = None
    this_key = None
    total = []

    for input_line in sys.stdin:
        input_line = input_line.strip()
        try:
            this_key, value = input_line.split(delimiter, 1)
            if last_key == this_key:
                total.append(value)
            else:
                if last_key:
                    reduce_callback(last_key, total)
                total = [value]
                last_key = this_key
        except:
            pass

    if last_key == this_key:
        reduce_callback(last_key, total)

def reduce_sum_int(key, values):
    try:
        values = [int(v) for v in values]
    except:
        values = [int(values)]

    print "%s\t%d" % (key, sum(values))

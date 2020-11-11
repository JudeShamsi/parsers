import sys
import math
import argparse
import tqdm as tqdm
import pandas as pd


# make argparse arguments global
CONSOLE_ARGUMENTS = None


def read_single_graph(file_name, b_size, b_fh, s_fh):
    """Read a single graph from the file @file_name.
    Write @b_size number of edges to @b_fh and the
    rest of the edges in the graph to @s_fh."""
    node_id_seen = set()                                        # set of the node id that we have seen already
    cnt = 1                                                     # logical timestamps of edges
    if CONSOLE_ARGUMENTS.arrange:
        next_id = 0
        node_map = dict()                                       # maps original node IDs to new IDs, which always start from 0

    # read edges for the base graph only
    df = pd.read_csv(file_name, sep='\t', dtype=str, header=None, nrows=b_size)
    # process those edges
    for edge in df.itertuples():
        src_id = df.at[edge.Index, 0]
        dst_id = df.at[edge.Index, 2]
        if CONSOLE_ARGUMENTS.arrange:
            if src_id in node_map:
                src_id = node_map[src_id]
            else:
                node_map[src_id] = str(next_id)
                src_id = str(next_id)
                next_id += 1
            if dst_id in node_map:
                dst_id = node_map[dst_id]
            else:
                node_map[dst_id] = str(next_id)
                dst_id = str(next_id)
                next_id += 1
        src_type = df.at[edge.Index, 1]
        dst_type = df.at[edge.Index, 3]
        edge_type = df.at[edge.Index, 4]
        if not src_id in node_id_seen:
            node_id_seen.add(src_id)
        if not dst_id in node_id_seen:
            node_id_seen.add(dst_id) 
        info = "{}:{}:{}:{}".format(src_type, dst_type, edge_type, cnt)
        # replace the fourth column to the @info str
        df.at[edge.Index, 3] = info
        # replace the src and dst ids
        df.at[edge.Index, 0] = src_id
        df.at[edge.Index, 2] = dst_id
        cnt += 1
    cols = [1, 4, 5]
    # drops column in the original data frame
    df.drop(df.columns[cols], axis=1, inplace=True)
    # write the data frame to the base graph file
    df.to_csv(b_fh, sep=' ', header=False, index=False)

    # read edges for the stream graph
    for df in pd.read_csv(file_name, sep='\t', dtype=str, header=None, skiprows=b_size, chunksize=b_size):
        for edge in df.itertuples():
            src_id = df.at[edge.Index, 0]
            dst_id = df.at[edge.Index, 2]
            if CONSOLE_ARGUMENTS.arrange:
                if src_id in node_map:
                    src_id = node_map[src_id]
                else:
                    node_map[src_id] = str(next_id)
                    src_id = str(next_id)
                    next_id += 1
                if dst_id in node_map:
                    dst_id = node_map[dst_id]
                else:
                    node_map[dst_id] = str(next_id)
                    dst_id = str(next_id)
                    next_id += 1
            src_type = df.at[edge.Index, 1]
            dst_type = df.at[edge.Index, 3]
            edge_type = df.at[edge.Index, 4]
            seen_src = 1
            if not src_id in node_id_seen:
                seen_src = 0
                node_id_seen.add(src_id)
            seen_dst = 1
            if not dst_id in node_id_seen:
                seen_dst = 0
                node_id_seen.add(dst_id)
            info = "{}:{}:{}:{}:{}:{}".format(src_type, dst_type, edge_type, seen_src, seen_dst, cnt)
            df.at[edge.Index, 3] = info
            df.at[edge.Index, 0] = src_id
            df.at[edge.Index, 2] = dst_id
            cnt += 1
        df.drop(df.columns[cols], axis=1, inplace=True)
        df.to_csv(s_fh, sep=' ', mode='a', header=False, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # %% is not a typo: https://thomas-cokelaer.info/blog/2014/03/python-argparse-issues-with-the-help-argument-typeerror-o-format-a-number-is-required-not-dict/
    parser.add_argument('-s', '--size', help='the size of the base graph in absolute value', required=True, type=int)
    parser.add_argument('-i', '--input', help='input StreamSpot data file path', required=True)
    parser.add_argument('-b', '--base', help='output file path of the base graph', required=True)
    parser.add_argument('-S', '--stream', help='output file path of the stream graph', required=True)
    parser.add_argument('-a', '--arrange', help='rearrange node IDs of a graph to be Unicorn compliant', action='store_true')
    args = parser.parse_args()

    print("\x1b[6;30;42m[INFO]\x1b[0m Graph Node IDs are rearranged: {}".format(args.arrange))

    CONSOLE_ARGUMENTS = args

    base_graph_size = args.size

    base_file = open(args.base, "w")
    stream_file = open(args.stream, "w")

    read_single_graph(args.input, base_graph_size, base_file, stream_file)

    print("\x1b[6;30;42m[SUCCESS]\x1b[0m Graph is processed:")
    print("\x1b[6;30;42m[SUCCESS]\x1b[0m Base graph of size {} is located at {}".format(base_graph_size, args.base))
    print("\x1b[6;30;42m[SUCCESS]\x1b[0m Stream graph is located at {}".format(args.stream))

    base_file.close()
    stream_file.close()


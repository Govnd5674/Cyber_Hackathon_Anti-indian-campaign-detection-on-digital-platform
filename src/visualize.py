
import os
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

def plot_timeseries(ts: pd.DataFrame, outpath: str):
    if ts.empty:
        return
    plt.figure()
    plt.plot(ts["bucket"], ts["count"])
    plt.title("Tweet Volume per Minute")
    plt.xlabel("Time (UTC minute)")
    plt.ylabel("Tweets")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def plot_network(g: nx.Graph, outpath: str, max_nodes: int = 200):
    if g.number_of_nodes() == 0:
        return
    plt.figure()
    H = g.copy()
    if H.number_of_nodes() > max_nodes:
        # take largest connected component for visibility
        components = sorted(nx.connected_components(H.to_undirected()), key=len, reverse=True)
        keep = set(next(iter(components)))
        H = H.subgraph(keep).copy()
    pos = nx.spring_layout(H, k=0.8, iterations=50)
    nx.draw_networkx_nodes(H, pos, node_size=50)
    nx.draw_networkx_edges(H, pos, alpha=0.3)
    plt.title("Retweet / Reply / Mention Network (largest component)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

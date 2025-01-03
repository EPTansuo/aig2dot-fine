#!/usr/bin/python

import pygraphviz as pgv
import argparse
import os

def is_jupyter_notebook():
    try:
        from IPython import get_ipython
        if "IPKernelApp" in get_ipython().config:
            return True
    except Exception:
        pass
    return False



def main():
    if is_jupyter_notebook():  # for testing 
        input_dot_file = "1.dot"  
        output_dot_file = "1_out.dot"
    else:
        parser = argparse.ArgumentParser(description="Process and refine the output generated by aigtodot.")
        parser.add_argument("-i", "--input", required=True, help="Path to the input DOT file.")
        parser.add_argument("-o", "--output", required=True, help="Path to the output DOT file.")
        args = parser.parse_args()
        input_dot_file = args.input
        output_dot_file = args.output
    
    graph = pgv.AGraph(input_dot_file)
    
    
    # Reverse all edges
    reversed_graph = pgv.AGraph(strict=True, directed=True)
    for node in graph.nodes():
        reversed_graph.add_node(node, **dict(graph.get_node(node).attr))
    for edge in graph.edges():
        source, target = edge 
        edge_attributes = dict(graph.get_edge(source, target).attr) 
        reversed_graph.add_edge(target, source, **edge_attributes) 
    graph = reversed_graph
    
    
    # Merge input note and the next node 
    for node in list(graph.nodes()):
        if node.name.startswith("I"):  # input nodes starts with 'I' 
            out_edges = list(graph.out_edges(node))  
            
            if len(out_edges) == 1: 
                out_edge = out_edges[0]  
                target_node = out_edge[1]  # terminal of out edge
                target_attributes = dict(graph.get_node(target_node).attr)
    
                new_name = node.name
                graph.add_node(new_name, **target_attributes)
                
                for edge in list(graph.in_edges(target_node)):
                    graph.add_edge(edge[0], new_name, **dict(graph.get_edge(edge[0], edge[1]).attr))
                
                for edge in list(graph.out_edges(target_node)):
                    graph.add_edge(new_name, edge[1], **dict(graph.get_edge(edge[0], edge[1]).attr))
                
                for edge in list(graph.out_edges(node)):
                    if(edge[1] == edge[0]):
                        graph.delete_edge(edge)
                graph.delete_node(target_node)
    
    
    and_node = 1
    for node in graph.nodes():
        #print(node.name)
        if node.name.startswith("I") or node.name.startswith("O"):  # Change attribute of nodes
            node.attr.update(shape="box", color="black")
        else: 
            node.attr.update(shape="circle", color="black")
            new_name = f"and{and_node}"           # change name of and nodes
            and_node += 1
            graph.add_node(new_name,**dict(graph.get_node(node).attr))
            for edge in list(graph.in_edges(node)):
                graph.add_edge(edge[0], new_name, **dict(graph.get_edge(edge[0], edge[1]).attr))
            for edge in list(graph.out_edges(node)):
                graph.add_edge(new_name, edge[1], **dict(graph.get_edge(edge[0], edge[1]).attr))
            graph.delete_node(node)
            
        
    # Change attributes of edges
    for edge in graph.edges():
        attributes = dict(edge.attr)
        if(attributes.get("arrowhead") == "none") :
            edge.attr.update(arrowhead="normal")
        elif attributes.get("arrowhead") == "dot":
            edge.attr.update(arrowhead="normal", style="dashed")
    
    # Change layout 
    graph.graph_attr["rankdir"] = "LR" 
    
    graph.write(output_dot_file)
    
    
    graph.close()
    reversed_graph.close()


if __name__ == "__main__":
    main()

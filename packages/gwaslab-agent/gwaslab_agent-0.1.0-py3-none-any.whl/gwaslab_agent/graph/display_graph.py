"""
Graph visualization utilities for LangGraph workflows.

This module provides functions to display and save LangGraph workflow visualizations
in various formats (Mermaid, ASCII, PNG).
"""


def display_graph(graph, log, output_format="mermaid", save_path=None):
    """
    Display or save the LangGraph workflow visualization.
    
    Parameters
    ----------
    graph : StateGraph
        The LangGraph StateGraph instance to visualize.
    log : Log
        Logger instance for writing messages.
    output_format : str, default "mermaid"
        Format for visualization. Options:
        - "mermaid": Mermaid diagram (can be rendered in markdown)
        - "ascii": ASCII art representation
        - "png": PNG image (requires pygraphviz)
    save_path : str, optional
        If provided, save the visualization to this path. Otherwise, print to console.
    
    Returns
    -------
    str or None
        The visualization string if output_format is "mermaid" or "ascii", None otherwise.
    """
    try:
        # Get the graph structure
        graph_structure = graph.get_graph()
        
        if output_format == "mermaid":
            try:
                # Try the draw_mermaid method
                mermaid_diagram = graph_structure.draw_mermaid()
            except AttributeError:
                # Fallback: try get_graph().draw_mermaid() or manual construction
                try:
                    mermaid_diagram = graph.get_graph().draw_mermaid()
                except:
                    # Manual mermaid construction as last resort
                    mermaid_diagram = _build_mermaid_diagram()
            
            if save_path:
                with open(save_path, 'w') as f:
                    f.write(mermaid_diagram)
                log.write(f"Graph visualization saved to {save_path}", verbose=True)
            else:
                print("\n" + "="*80)
                print("LangGraph Workflow Visualization (Mermaid)")
                print("="*80)
                print(mermaid_diagram)
                print("="*80 + "\n")
            return mermaid_diagram
            
        elif output_format == "ascii":
            try:
                ascii_diagram = graph_structure.draw_ascii()
            except AttributeError:
                try:
                    ascii_diagram = graph.get_graph().draw_ascii()
                except:
                    ascii_diagram = _build_ascii_diagram()
            
            if save_path:
                with open(save_path, 'w') as f:
                    f.write(ascii_diagram)
                log.write(f"Graph visualization saved to {save_path}", verbose=True)
            else:
                print("\n" + "="*80)
                print("LangGraph Workflow Visualization (ASCII)")
                print("="*80)
                print(ascii_diagram)
                print("="*80 + "\n")
            return ascii_diagram
            
        elif output_format == "png":
            try:
                png_path = save_path or "graph.png"
                graph_structure.draw_png(png_path)
                log.write(f"Graph visualization saved to {png_path}", verbose=True)
            except Exception as e:
                log.write(f"PNG visualization requires pygraphviz. Error: {str(e)}", verbose=True)
                log.write("Falling back to Mermaid format...", verbose=True)
                return display_graph(graph, log, output_format="mermaid", save_path=save_path)
        else:
            log.write(f"Unknown output format: {output_format}. Use 'mermaid', 'ascii', or 'png'", verbose=True)
            return None
            
    except Exception as e:
        log.write(f"Error displaying graph: {str(e)}", verbose=True)
        import traceback
        log.write(traceback.format_exc(), verbose=True)
        # Fallback to manual diagram
        return _build_mermaid_diagram()


def _build_mermaid_diagram():
    """Build a Mermaid diagram manually based on the graph structure."""
    diagram = """graph TD
    START([START]) --> router[router_node<br/>Interpret message & extract instructions]
    
    router --> route_check{Route type?}
    
    route_check -->|path_manager/loader/summarizer| END1([END])
    route_check -->|planner| planner[planner_node<br/>Generate Python script]
    route_check -->|plan/plan_run/plan_run_sum| planner
    
    planner --> path_manager[path_manager_node<br/>Resolve {REF:...} placeholders]
    
    path_manager --> validator[validator_node<br/>Validate script]
    
    validator --> valid_check{Script valid?}
    
    valid_check -->|No| END2([END])
    valid_check -->|Yes, route=plan/planner| END3([END])
    valid_check -->|Yes, route=plan_run/plan_run_sum| executor[executor_node<br/>Execute script]
    
    executor --> summary_check{Needs summary?}
    
    summary_check -->|Yes| summarizer[summarizer_node<br/>Generate summary]
    summary_check -->|No| END4([END])
    
    summarizer --> END5([END])
    
    style router fill:#e1f5ff
    style planner fill:#fff4e1
    style path_manager fill:#e8f5e9
    style validator fill:#fce4ec
    style executor fill:#f3e5f5
    style summarizer fill:#e0f2f1
"""
    return diagram


def _build_ascii_diagram():
    """Build an ASCII diagram manually based on the graph structure."""
    diagram = """
LangGraph Workflow Structure
=============================

START
  |
  v
[router_node] - Interpret message & extract instructions
  |
  |---> (path_manager/loader/summarizer) --> END
  |
  |---> (planner/plan/plan_run/plan_run_sum)
  |
  v
[planner_node] - Generate Python script
  |
  v
[path_manager_node] - Resolve {REF:...} placeholders
  |
  v
[validator_node] - Validate script
  |
  |---> (Invalid or route=plan/planner) --> END
  |
  |---> (Valid & route=plan_run/plan_run_sum)
  |
  v
[executor_node] - Execute script
  |
  |---> (No summary needed) --> END
  |
  |---> (Needs summary)
  |
  v
[summarizer_node] - Generate summary
  |
  v
END
"""
    return diagram


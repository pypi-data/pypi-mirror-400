"""Algorithm visualization tools."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'src'))

try:
    from mcp.tools.algorithms.visualize_bubble_sort import visualize_bubble_sort as _bubble
    from mcp.tools.algorithms.visualize_quick_sort import visualize_quick_sort as _quick
    from mcp.tools.algorithms.visualize_merge_sort import visualize_merge_sort as _merge
    from mcp.tools.algorithms.visualize_binary_search import visualize_binary_search as _binary
    from mcp.tools.algorithms.visualize_dijkstra import visualize_dijkstra as _dijkstra
    from mcp.tools.algorithms.visualize_bfs_dfs import visualize_bfs_dfs as _bfs_dfs
except ImportError:
    def _bubble(array): return {"success": False, "error": "Algorithm tools not available"}
    def _quick(array): return {"success": False, "error": "Algorithm tools not available"}
    def _merge(array): return {"success": False, "error": "Algorithm tools not available"}
    def _binary(array, target): return {"success": False, "error": "Algorithm tools not available"}
    def _dijkstra(graph, start): return {"success": False, "error": "Algorithm tools not available"}
    def _bfs_dfs(graph, start, algorithm): return {"success": False, "error": "Algorithm tools not available"}


def visualize_bubble_sort_tool(array: str) -> str:
    """Visualize bubble sort."""
    try:
        arr = [int(x.strip()) for x in array.split(',')]
        result = _bubble(arr)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def visualize_quick_sort_tool(array: str) -> str:
    """Visualize quick sort."""
    try:
        arr = [int(x.strip()) for x in array.split(',')]
        result = _quick(arr)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def visualize_merge_sort_tool(array: str) -> str:
    """Visualize merge sort."""
    try:
        arr = [int(x.strip()) for x in array.split(',')]
        result = _merge(arr)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def visualize_binary_search_tool(array: str, target: str) -> str:
    """Visualize binary search."""
    try:
        arr = [int(x.strip()) for x in array.split(',')]
        target_num = int(target)
        result = _binary(arr, target_num)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def visualize_dijkstra_tool(graph: str, start: str) -> str:
    """Visualize Dijkstra's algorithm."""
    try:
        graph_dict = json.loads(graph)
        result = _dijkstra(graph_dict, start)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def visualize_bfs_dfs_tool(graph: str, start: str, algorithm: str) -> str:
    """Visualize BFS/DFS."""
    try:
        graph_dict = json.loads(graph)
        result = _bfs_dfs(graph_dict, start, algorithm)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

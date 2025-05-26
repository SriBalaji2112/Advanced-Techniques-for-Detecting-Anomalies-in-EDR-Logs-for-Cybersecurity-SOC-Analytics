import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from msticpy.transform.proc_tree_builder import build_process_tree


class ProcessTreeVisualizer:
    def __init__(self, schema=None):
        self.df = None
        self.graph = nx.DiGraph()
        self.schema = schema or {
            "process_name": "ProcessName",
            "process_id": "ProcessId",
            "parent_id": "ParentProcessId",
            "time_stamp": "EventTime",
        }
        self.anomalous_nodes = []

    def set_dataframe(self, data):
        """Set the DataFrame from raw data."""
        self.df = pd.DataFrame(data)
        self.df.columns = self.df.columns.str.replace(' ', '')
        build_process_tree(self.df, schema=self.schema, debug=True)
        self._build_graph()
        self._detect_anomalies()

    def _detect_anomalies(self):
        """Detect and store all anomalous nodes (Anomaly == -1)."""
        if "Anomaly" in self.df.columns:
            self.anomalous_nodes = self.df[self.df["Anomaly"] == -1]["ProcessId"].tolist()

    def _build_graph(self):
        """Build the process graph."""
        for _, row in self.df.iterrows():
            if pd.notna(row["ParentProcessId"]) and pd.notna(row["ProcessId"]):
                self.graph.add_edge(
                    row["ParentProcessId"],
                    row["ProcessId"],
                    TimeGenerated=row["EventTime"],
                    NewProcessName=row["ProcessName"],
                    NewProcessId=row["ProcessId"],
                )

    def _get_ancestor_path(self, node):
        """Get the path from root to a specific node."""
        path = []
        while True:
            predecessors = list(self.graph.predecessors(node))
            if not predecessors:
                break
            parent = predecessors[0]
            path.append((parent, node))
            node = parent
        return path[::-1]

    def _create_node_trace(self, pos):
        """Create node scatter plot and labels."""
        node_x, node_y, hover_texts, node_colors, node_labels = [], [], [], [], []

        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            node_info = self.df[self.df["ProcessId"] == node]
            if not node_info.empty:
                row = node_info.iloc[0]
                hover_text = (
                    f"Process Name: {row['ProcessName']}<br>"
                    f"Process ID: {row['ProcessId']}<br>"
                    f"Time: {row['EventTime']}"
                )
                if "AnomalyReason" in row and pd.notna(row["AnomalyReason"]):
                    hover_text += f"<br>Reason: {row['AnomalyReason']}"
                node_labels.append(row["ProcessName"])
            else:
                hover_text = "Unknown Process"
                node_labels.append("Unknown")

            hover_texts.append(hover_text)
            node_colors.append("red" if node in self.anomalous_nodes else "lightblue")

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers",
            marker=dict(size=12, color=node_colors, line=dict(width=2)),
            hoverinfo="text",
            text=hover_texts
        )

        label_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="text",
            text=node_labels,
            textposition="top center",
            hoverinfo="none",
            showlegend=False
        )

        return node_trace, label_trace

    def _create_edge_annotations(self, pos):
        """Create edge arrows, highlighting ancestor paths for anomalies."""
        highlight_edges = set()
        for node in self.anomalous_nodes:
            path = self._get_ancestor_path(node)
            highlight_edges.update(path)

        annotations = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            is_highlight = edge in highlight_edges
            annotations.append(
                dict(
                    ax=x0, ay=y0,
                    x=x1, y=y1,
                    xref="x", yref="y",
                    axref="x", ayref="y",
                    showarrow=True,
                    arrowhead=3,
                    arrowsize=1.8,
                    arrowwidth=1.5,
                    opacity=0.7,
                    arrowcolor="blue" if is_highlight else "gray"
                )
            )
        return annotations

    def show_graph(self):
        """Visualize the process tree with Plotly."""
        pos = nx.circular_layout(self.graph)
        node_trace, label_trace = self._create_node_trace(pos)
        annotations = self._create_edge_annotations(pos)

        fig = go.Figure(data=[node_trace, label_trace])
        fig.update_layout(
            title="Process Tree - Highlighted Anomalies and Paths",
            title_font_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=50),
            annotations=annotations,
        )
        fig.show()


# from sample_data import data  # Your sample dataset containing 'Anomaly' column

# tree_vis = ProcessTreeVisualizer()
# tree_vis.set_dataframe(data)
# tree_vis.show_graph()

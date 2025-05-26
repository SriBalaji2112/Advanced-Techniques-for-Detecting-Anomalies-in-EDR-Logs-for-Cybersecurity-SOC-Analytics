from src.importing import *
from widgets.Messages import MessageBox
from src.ProcessTreeWebEngine import ProcessTreeVisualizer
from widgets.ContinueProgressBar import ContinousProgressBar
from PyQt5.QtCore import QCoreApplication

class GraphRenderWorker(QThread):
    progress_signal = pyqtSignal(int)  # Progress updates (if needed for a progress bar)
    finished_signal = pyqtSignal()    # Signal when rendering is complete

    def __init__(self, df, layout, ax):
        super().__init__()
        self.df = df
        self.layout = layout
        self.ax = ax

    def run(self):
        """Thread's main method for rendering the graph."""
        graph = nx.from_pandas_edgelist(
            self.df,
            source="Process Id",  # Source node
            target="Parent Process Id",  # Target node
            edge_attr=[
                "Process Name",
                "Command Line",
                "Creation Time",
            ],  # Attributes for edges
            create_using=nx.DiGraph,
        )

        # Set layout based on the current layout selection
        if self.layout == "circular":
            pos = nx.circular_layout(graph)
        elif self.layout == "spring":
            pos = nx.spring_layout(graph)
        else:
            pos = nx.random_layout(graph)

        # Generate node labels
        labels = {
            node: self.df[self.df["Process Id"] == node]["Process Name"].values[0]
            if not self.df[self.df["Process Id"] == node].empty
            else ""
            for node in graph.nodes()
        }

        # Render the graph
        self.ax.clear()
        nx.draw_networkx(graph, pos=pos, with_labels=False, node_size=50, ax=self.ax)
        nx.draw_networkx_labels(graph, pos, labels=labels, font_size=10, font_color="k")

        self.finished_signal.emit()  # Notify that rendering is done


class GraphWindow(QWidget):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Graph Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.df = df
        self.current_layout = "circular"
        self.fig, self.ax = plt.subplots(figsize=(10, 10))

        layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(self.fig)
        self.buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset View")
        self.save_button = QPushButton("Save as Image")
        self.layout_button = QPushButton("Switch Layout")

        self.buttons_layout.addWidget(self.reset_button)
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.layout_button)

        layout.addWidget(self.canvas)
        layout.addLayout(self.buttons_layout)
        self.setLayout(layout)

        self.reset_button.clicked.connect(self.reset_view)
        self.save_button.clicked.connect(self.save_graph)
        self.layout_button.clicked.connect(self.switch_layout)

        self.thread = None  # Thread for graph rendering

        # Draw initial graph
        self.draw_graph()

        # For pan and zoom handling:
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_press_event", self.on_button_press)
        self.canvas.mpl_connect("scroll_event", self.on_mouse_scroll)
        
        self.is_dragging = False
        self.prev_x = None
        self.prev_y = None
        self.zoom_factor = 1.1  # Zoom in/out factor
        
    def draw_graph(self):
        """Trigger graph rendering in a separate thread."""
        if self.thread and self.thread.isRunning():
            return  # Avoid starting multiple threads simultaneously

        self.thread = GraphRenderWorker(self.df, self.current_layout, self.ax)
        self.thread.finished_signal.connect(self.refresh_canvas)
        self.thread.start()

    def refresh_canvas(self):
        """Update the canvas after rendering is complete."""
        self.canvas.draw()

    def reset_view(self):
        """Reset to default layout and redraw the graph."""
        self.current_layout = "circular"
        self.draw_graph()

    def switch_layout(self):
        """Switch between layouts and redraw the graph."""
        layouts = ["circular", "spring", "random"]
        current_index = layouts.index(self.current_layout)
        self.current_layout = layouts[(current_index + 1) % len(layouts)]
        self.draw_graph()

    def save_graph(self):
        """Save the current graph to a file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Graph As Image", "", "PNG Files (*.png);;All Files (*)", options=options
        )
        if file_path:
            self.fig.savefig(file_path)
    
    def on_button_press(self, event):
        """Handle mouse button press to start the drag action."""
        if event.button == 1:  # Left mouse button
            self.is_dragging = True
            self.prev_x = event.x
            self.prev_y = event.y

    def on_mouse_move(self, event):
        """Handle mouse dragging for panning the graph."""
        if self.is_dragging and event.button == 1:  # Ensure only left mouse button
            # Get current axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            # Calculate sensitivity based on zoom level
            sensitivity_x = (xlim[1] - xlim[0]) * 0.005  # Scale sensitivity with zoom level
            sensitivity_y = (ylim[1] - ylim[0]) * 0.005

            # Calculate movement deltas
            dx = (event.x - self.prev_x) * sensitivity_x
            dy = (self.prev_y - event.y) * sensitivity_y


            # Adjust limits for panning
            self.ax.set_xlim([x - dx for x in xlim])  # Note the "-" for correct panning
            self.ax.set_ylim([y + dy for y in ylim])  # Note the "-" for correct panning

            self.canvas.draw()

            # Update previous mouse position
            self.prev_x = event.x
            self.prev_y = event.y

    def on_button_release(self, event):
        """Handle mouse button release to stop the drag action."""
        if event.button == 1:  # Left mouse button
            self.is_dragging = False

    def on_mouse_scroll(self, event):
        """Handle mouse scroll for zooming in and out."""
        zoom_factor = 0.9 if event.step > 0 else 1.1  # Scroll up zooms in, down zooms out
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Calculate new limits
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        new_xlim = [
            x_center + (x - x_center) * zoom_factor for x in xlim
        ]
        new_ylim = [
            y_center + (y - y_center) * zoom_factor for y in ylim
        ]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw()


def graph_plot(parent):
    current_index = parent.tabs.currentIndex()
    current_sheet_name = parent.tabs.tabText(current_index)
    if current_sheet_name:
        # parent.graph_window = GraphWindow(parent.data[current_sheet_name]['df'])
        # parent.graph_window.show()
        progress = ContinousProgressBar("Process Tree generated shortly....", parent=parent, title="Visualizer Worker")
        progress.show()

        QCoreApplication.processEvents()
        parent.graph_window = ProcessTreeVisualizer()
        QCoreApplication.processEvents()
        parent.graph_window.set_dataframe(parent.data[current_sheet_name]['df'])
        QCoreApplication.processEvents()
        parent.graph_window.show_graph()
        QCoreApplication.processEvents()

        progress.close()

    else:
        MessageBox.show_warning("No log data found, please open a log file.")
from typing import Dict, Any, List
import pandas as pd
import json

class QueryProfile:
    def __init__(self, profile_data: Dict[str, Any]):
        self.data = profile_data
        
    @property
    def job_id(self):
        return self.data.get("jobId", {}).get("id")
    
    @property
    def start_time(self):
        return self.data.get("startTime")
        
    @property
    def end_time(self):
        return self.data.get("endTime")
        
    @property
    def state(self):
        return self.data.get("state")

    def summary(self):
        """Print a summary of the query execution."""
        print(f"Job ID: {self.job_id}")
        print(f"State: {self.state}")
        print(f"Start: {self.start_time}")
        print(f"End: {self.end_time}")
        
        # Try to extract planning vs execution time
        # This depends heavily on the profile JSON structure which is complex and version dependent.
        # We'll try to find some top level metrics if available.
        # Often in 'stats' or similar.
        
        print("\n--- Phases ---")
        # This is a simplification. Real profiles have a tree of operators.
        # We might look for "phases" list.
        # For now, just dumping top level keys that look interesting.
        pass

    def visualize(self, save_to: str = None):
        """
        Visualize the query execution timeline using Plotly.
        This requires parsing the operator tree and timing information.
        """
        import plotly.express as px
        
        # Mock implementation for now as parsing the full profile is complex without a sample.
        # We will create a dummy Gantt chart based on phases if available, or just a placeholder.
        
        # Let's assume we can extract some phases.
        # If not, we'll just show a single bar for the whole job.
        
        data = [
            dict(Task="Job Execution", Start=self.start_time, Finish=self.end_time, Resource="Job")
        ]
        
        # If we had real phases:
        # for phase in self.data.get("phases", []):
        #    data.append(...)
        
        df = pd.DataFrame(data)
        
        # Convert times to datetime
        # Dremio times are usually epoch ms
        if isinstance(self.start_time, int):
            df["Start"] = pd.to_datetime(df["Start"], unit="ms")
            df["Finish"] = pd.to_datetime(df["Finish"], unit="ms")
            
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource", title=f"Query Profile: {self.job_id}")
        fig.update_yaxes(autorange="reversed")
        
        if save_to:
            if save_to.endswith(".html"):
                fig.write_html(save_to)
            else:
                fig.write_image(save_to)
        
        return fig

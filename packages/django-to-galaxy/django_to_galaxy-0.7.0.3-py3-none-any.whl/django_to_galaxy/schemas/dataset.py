from pydantic import BaseModel


class SimpleDataset(BaseModel):
    """Simple model for dataset from history."""

    id: str
    """ID of the dataset."""
    name: str
    """Name of the dataset."""
    data_type: str
    """Type of dataset."""

    def generate_datamap(self, tool_id):
        """Generate datamap to invoke workflow."""
        return {tool_id: {"id": self.id, "src": "hda"}}

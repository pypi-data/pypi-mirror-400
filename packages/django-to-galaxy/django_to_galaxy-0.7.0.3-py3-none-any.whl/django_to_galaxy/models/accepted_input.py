from django.db import models
from django.db.models import Q

DATA = "data_input"
COLLECTION = "data_collection_input"
PARAMETER = "parameter_input"
INPUT_TYPE_CHOICES = [
    (DATA, "data_input"),
    (COLLECTION, "data_collection_input"),
    (PARAMETER, "parameter_input"),
]

P_TEXT = "text"
P_INTEGER = "integer"
P_FLOAT = "float"
P_BOOLEAN = "boolean"
P_COLOR = "color"
P_DIRECTORY_URI = "directory_uri"
PARAMETER_TYPE_CHOICES = [
    (P_TEXT, "text"),
    (P_INTEGER, "integer"),
    (P_FLOAT, "float"),
    (P_BOOLEAN, "boolean"),
    (P_COLOR, "color"),
    (P_DIRECTORY_URI, "directory_uri"),
]

C_RECORD = "record"
C_PAIRED = "paired"
C_LIST = "list"
C_LIST_RECORD = "list:record"
C_LIST_PAIRED = "list:paired"
C_LIST_PAIRED_UNPAIRED = "list:paired_or_unpaired"
COLLECTION_TYPE_CHOICES = [
    (C_RECORD, "Record"),
    (C_PAIRED, "Dataset Pair"),
    (C_LIST, "List of Datasets"),
    (C_LIST_RECORD, "List of Records"),
    (C_LIST_PAIRED, "List of Dataset Pairs"),
    (C_LIST_PAIRED_UNPAIRED, "Mixed List of Paired and Unpaired Datasets"),
]


class Format(models.Model):
    """Format on the galaxy side."""

    format = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.format}"


class WorkflowInputTextOption(models.Model):
    """Text option for a workflow input on Galaxy side."""

    workflow_input = models.ForeignKey(
        "WorkflowInput", null=False, on_delete=models.CASCADE
    )
    text_option = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workflow_input", "text_option"], name="unique_input_option"
            )
        ]

    def __str__(self):
        return f"{self.text_option}"

    def __repr__(self):
        return f"Input: {self!s}"


class WorkflowInput(models.Model):
    """Accepted input for a workflow on Galaxy side."""

    galaxy_step_id = models.IntegerField(null=False)
    """Step id on the galaxy side."""
    label = models.CharField(max_length=100, blank=True)
    """Label on the galaxy side."""
    workflow = models.ForeignKey("Workflow", null=False, on_delete=models.CASCADE)
    """Workflow id."""
    input_type = models.CharField(
        max_length=25, choices=INPUT_TYPE_CHOICES, default=DATA
    )
    """Type of input on the galaxy side."""
    formats = models.ManyToManyField("Format")
    """Accepted input formats on the galaxy side."""
    parameter_type = models.CharField(
        max_length=15,
        choices=PARAMETER_TYPE_CHOICES,
        default=None,
        null=True,
        blank=True,
    )
    """Type of input if it is a parameter input."""
    collection_type = models.CharField(
        max_length=25,
        choices=COLLECTION_TYPE_CHOICES,
        default=None,
        null=True,
        blank=True,
    )
    """Type of input if it is a parameter input."""
    optional = models.BooleanField(default=False)
    """Workflow input optional information on the galaxy side."""
    default_value = models.CharField(max_length=255, null=True, blank=True)
    """Default value of the input (either text, integer, float, boolean)"""
    multiple = models.BooleanField(default=False)
    """If the input can get multiple values on the galaxy side."""

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(
                    Q(input_type=PARAMETER)
                    & Q(parameter_type__isnull=False)
                    & Q(collection_type__isnull=True)
                )
                | Q(
                    Q(input_type=DATA)
                    & Q(parameter_type__isnull=True)
                    & Q(collection_type__isnull=True)
                )
                | Q(
                    Q(input_type=COLLECTION)
                    & Q(parameter_type__isnull=True)
                    & Q(collection_type__isnull=False)
                ),
                name="workflowinputs_types_congruant",
            )
        ]

    def __str__(self):
        return f"{self.label}"

    def __repr__(self):
        return f"Input: {self!s}"

    def get_casted_default_value(self):
        """
        Return the default_value casted according to parameter_type.
        If the type is unknown or the value is null, return the raw value.
        """
        if self.default_value is None:
            return None

        if self.input_type != PARAMETER or self.parameter_type is None:
            return self.default_value

        value = self.default_value

        try:
            match self.parameter_type:
                case "integer":
                    return int(value)

                case "float":
                    return float(value)

                case "boolean":
                    return value.lower() in ("true", "1", "yes")

                case "text":
                    return value

                case _:
                    return value

        except (ValueError, TypeError):
            return value

    @property
    def default_value_casted(self):
        return self.get_casted_default_value()

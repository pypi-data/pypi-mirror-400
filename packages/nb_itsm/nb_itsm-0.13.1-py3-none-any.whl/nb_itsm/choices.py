from django.db.models import Q
from utilities.choices import ChoiceSet

OBJECT_ASSIGNMENT_MODELS = Q(
    Q(app_label='dcim', model='device') |
    Q(app_label='circuits', model='circuit') |
    Q(app_label='virtualization', model='virtualmachine') |
    Q(app_label='nb_itsm', model='application')
)

class PenTestChoices(ChoiceSet):

    APROVED = 1
    REPROVED = 2

    CHOICES = (
        (APROVED, "Approved"),
        (REPROVED, "Reproved"),
    )

class ShapeChoices(ChoiceSet):

    ROUND_EDGES = 1
    STADIUM = 2
    SUBROUTINE = 3
    CYLINDRICAL = 4
    CIRCLE = 5
    ASYMMETRIC = 6
    RHOMBUS = 7
    HEXAGON = 8
    PARALLELOGRAM = 9
    TRAPEZOID = 10

    CHOICES = (
        (ROUND_EDGES,  'Round Edges'),
        (STADIUM,  'Stadium Shaped'),
        (SUBROUTINE,  "Subroutine Shape"),
        (CYLINDRICAL,  "Cylindrical Shape"),
        (CIRCLE,  "Circle Shape"),
        (ASYMMETRIC, "asymmetric shape"),
        (RHOMBUS,"rhombus"),
        (HEXAGON,"Hexagon"),
        (PARALLELOGRAM ,"Parallelogram"),
        (TRAPEZOID,"Trapezoid"),
    )

class ConnectorChoices(ChoiceSet):
    ARROW = 1
    OPEN = 2
    DOTTED_ARROW = 3
    DOTTED_OPEN = 4

    CHOICES = (
        (ARROW,  'Arrow'),
        (OPEN,  'Open'),
        (DOTTED_ARROW,  "Dotted Arrow"),
        (DOTTED_OPEN,  "Dotted Open"),
    )

class ItilServiceStatusChoices(ChoiceSet):
    key = 'ItilServiceCatalog.service_status'

    CHOICES = [
        ('Requirements', 'Requirements', 'yellow'),
        ('Definition', 'Definition', 'yellow'),
        ('Analysis', 'Analysis', 'yellow'),
        ('Approved', 'Approved', 'yellow'),
        ('Chartered', 'Chartered', 'yellow'),
        ('Design', 'Design', 'yellow'),
        ('Development', 'Development', 'yellow'),
        ('Build', 'Build', 'yellow'),
        ('Test', 'Test', 'yellow'),
        ('Release', 'Release', 'green'),
        ('Operational', 'Operational (live)', 'green'),
        ('Retiring', 'Retiring', 'red'),
        ('Retired', 'Retired', 'red'),
    ]

class ItilServiceTypeChoices(ChoiceSet):
    key = 'ServiceCatalog.service_type'

    CHOICES = [
        ('customer', 'Customer-facing Service', 'green'),
        ('supporting', 'Supporting Service', 'orange'),
        ('experimental', 'Experimental Service', 'red'),
    ]

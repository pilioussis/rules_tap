from rules_tap.common import ViewableTable
from .models import SupportPerson, Org, Worker

VIEWABLES_TABLES = [
	ViewableTable(
		model_class=SupportPerson,
		fields=['id', 'full_name', 'role'],
		rows=SupportPerson.objects.viewable,
	),
	ViewableTable(
		model_class=Org,
		fields=['id', 'name', 'type'],
		rows=Org.objects.viewable,
	),	
	ViewableTable(
		model_class=Worker,
		fields=['id', 'name', 'type'],
		rows=Worker.objects.viewable,
	),
]
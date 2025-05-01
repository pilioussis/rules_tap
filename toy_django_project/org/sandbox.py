from rules_tap.common import ViewableTable
from .models import User, Org, Worker

VIEWABLES_TABLES = [
	ViewableTable(
		model_class=User,
		fields=['id', 'email', 'first_name', 'created', 'role'],
		viewable_row_fn=User.objects.viewable,
	),
	ViewableTable(
		model_class=Org,
		fields=['id', 'name', 'created', 'type'],
		viewable_row_fn=Org.objects.viewable,
	),
	ViewableTable(
		model_class=Worker,
		fields=['id', 'org_id', 'created', 'name', 'type', 'description'],
		viewable_row_fn=Worker.objects.viewable,
	),
]
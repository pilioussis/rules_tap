from rules_tap.common import ViewableTable
from .models import User, Org, Worker

VIEWABLES_TABLES = [
	ViewableTable(
		model_class=User,
		fields=['id', 'first_name', 'role'],
		viewable_row_fn=User.objects.viewable,
	),
	ViewableTable(
		model_class=Org,
		fields=['id', 'name', 'type'],
		viewable_row_fn=Org.objects.viewable,
	),	
	# ViewableTable(
	# 	model_class=Worker,
	# 	fields=['id', 'name', 'type'],
	# 	viewable_row_fn=Worker.objects.viewable,
	# ),
]
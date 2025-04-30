from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
	id = models.AutoField(primary_key=True)
	email = models.EmailField(unique=True, blank=True)
	USERNAME_FIELD = 'email'

	first_name = models.CharField(max_length=40, blank=True)
	last_name = models.CharField(max_length=40, blank=True)

	is_admin = models.BooleanField(
		default=False,
		help_text="Is internal pharos user, ie dean + dave",
	)
	is_active = models.BooleanField(default=True)

	created = models.DateTimeField(auto_now_add=True)


class RoleType(models.TextChoices):
		ADMIN = 'AD', 'Admin'
		AUTH = 'AU', 'Authenticated'
		PUBLIC = 'PB', 'Public'

class SupportPersonQuerySet(models.QuerySet):
	def viewable(self, user, **kwargs):
		"""Only admins should be able to see all users. Other users can only see themselves."""
		return self.filter(
			id__in=models.Case(
				models.When(role=SupportPerson.RoleType.ADMIN, then=models.Subquery(SupportPerson.objects.filter(deactivated__isnull=True).values('id'))),
				default=models.Value(user.id),
				output_field=models.IntegerField()
			),
			deactivated__isnull=True
		)


class SupportPerson(models.Model):
	objects = SupportPersonQuerySet.as_manager()
	RoleType = RoleType
	full_name = models.CharField(max_length=255)
	created = models.DateTimeField(auto_now_add=True)
	deactivated = models.DateTimeField(null=True, blank=True)
	role = models.CharField(
		max_length=2,
		choices=RoleType.choices,
		default=RoleType.PUBLIC,
	)


class OrgType(models.TextChoices):
	"""
	Represents the status of an organisation.
	ACTIVE - The organisation is viewable to all users and is actively using the product.
	PENDING - The organisation is viewable to all users but is not actively using the product.
	INACTIVE - The organisation has requested to be removed from the product.
	"""
	ACTIVE = 'AC', 'Active'
	PENDING = 'PE', 'Pending'
	INACTIVE = 'IN', 'Inactive'

class OrgQuerySet(models.QuerySet):
	def viewable_in_search(self):
		"""The set of organisations that a user can view in the public search page"""
		return self.filter(type__in=[OrgType.ACTIVE, OrgType.PENDING])

	def viewable(self, user, **kwargs):
		"""
		The set of organisations that a user can view:
			Public users - Only view active organisations.
			Authenticated users - View active and pending organisations.
			Admins - View all organisations.
		"""
		types = []
		if user.role == SupportPerson.RoleType.PUBLIC:
			types = [OrgType.ACTIVE]
		elif user.role == SupportPerson.RoleType.AUTH:
			types = [OrgType.ACTIVE, OrgType.PENDING]
		elif user.role == SupportPerson.RoleType.ADMIN:
			types = [OrgType.ACTIVE, OrgType.PENDING, OrgType.INACTIVE]
		return self.filter(type__in=types)
		

class Org(models.Model):
	objects = OrgQuerySet.as_manager()
	OrgType = OrgType

	name = models.CharField(max_length=255)
	created = models.DateTimeField(auto_now_add=True)
	type = models.CharField(
		max_length=2,
		choices=OrgType.choices,
		default=OrgType.ACTIVE,
	)


class WorkerType(models.TextChoices):
		EMPLOYEE = 'EM', 'Employee'
		CONTRACTOR = 'CO', 'Contractor'
		UNDERCOVER_AGENT = 'UA', 'Undercover Agent'

class WorkerQuerySet(models.QuerySet):
	def viewable(self, user, **kwargs):
		""" Returns a queryset of workers that are viewable by the user. Only Admins can view undercover agents."""
		viewable_types = [
			WorkerType.EMPLOYEE,
			WorkerType.CONTRACTOR,
		]
		if user.role == SupportPerson.RoleType.ADMIN:
			viewable_types.append(WorkerType.UNDERCOVER_AGENT)

		return self.filter(
			 org__in=Org.objects.viewable(user),
			 type__in=viewable_types,
		)
	
	def viewable_in_user_search(self, user):
		""" The set of workers that a user can view in the search page. They must be able to view the org and the worker."""
		orgs_viewable_in_search = Org.objects.viewable_in_search()
		orgs_viewable_to_user = Org.objects.viewable(user)
		orgs_viewable_org_intersection = orgs_viewable_in_search & orgs_viewable_to_user

		return self.viewable(user).filter(org__in=orgs_viewable_org_intersection)

class Worker(models.Model):
	objects = WorkerQuerySet.as_manager()

	WorkerType = WorkerType

	org = models.ForeignKey(Org, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	type = models.CharField(
		max_length=2,
		choices=WorkerType.choices,
		default=WorkerType.EMPLOYEE,
	)
	name = models.CharField(max_length=255)
	description = models.TextField(null=True, blank=True)


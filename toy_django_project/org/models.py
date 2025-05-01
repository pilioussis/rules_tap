import functools
import operator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import Value
from django.db.models.lookups import Exact
from django.db.models import Q

class UserQuerySet(models.QuerySet):
	def viewable(self, user, **kwargs):
		"""Only admins should be able to see all users. Other users can only see themselves."""
		return self.filter(
			id__in=models.Case(
				models.When(
					Exact(user.role, User.RoleType.ADMIN),
					then=models.Subquery(User.objects.filter(deactivated__isnull=True).values('id'))
				),
				default=models.Value(user.id),
				output_field=models.IntegerField()
			),
			deactivated__isnull=True
		)

class UserManager(BaseUserManager):
	def create_user(self, email, password=None, **kwargs):
		if not email:
			raise ValueError('Users must have a valid email address.')

		user = self.model(
			email=self.normalize_email(email)
		)

		user.set_password(password)
		user.save()

		return user

	def create_superuser(self, email, password, **kwargs):
		user = self.create_user(email, password, **kwargs)

		user.is_admin = True
		user.save()

		return user


UserManagerQueryset = UserManager.from_queryset(UserQuerySet)


class RoleType(models.TextChoices):
		ADMIN = 'AD', 'Admin'
		AUTH = 'AU', 'Authenticated'
		PUBLIC = 'PB', 'Public'


class User(AbstractBaseUser):
	objects = UserManagerQueryset()
	RoleType = RoleType

	id = models.AutoField(primary_key=True)

	email = models.EmailField(unique=True, blank=True)
	USERNAME_FIELD = 'email'

	first_name = models.CharField(max_length=40, blank=True)
	last_name = models.CharField(max_length=40, blank=True)

	is_admin = models.BooleanField(
		default=False,
		help_text="deprecated",
	)

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

		PERMISSION_MAP = {
			User.RoleType.ADMIN: [OrgType.ACTIVE, OrgType.PENDING, OrgType.INACTIVE],
			User.RoleType.AUTH: [OrgType.ACTIVE, OrgType.PENDING],
			User.RoleType.PUBLIC: [OrgType.ACTIVE],
		}

		filters = [
			Q(Exact(user.role, Value(user_role)), type__in=org_types)
			for user_role, org_types in PERMISSION_MAP.items()
		]

		return self.filter(functools.reduce(operator.or_, filters)) 
		

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
		BASE_TYPES = [
			WorkerType.EMPLOYEE,
			WorkerType.CONTRACTOR,
		]

		PERMISSION_MAP = {
			User.RoleType.ADMIN: [*BASE_TYPES, WorkerType.UNDERCOVER_AGENT],
			User.RoleType.AUTH: BASE_TYPES,
			User.RoleType.PUBLIC: BASE_TYPES,
		}

		filters = [
			Q(Exact(user.role, Value(user_role)), type__in=org_types)
			for user_role, org_types in PERMISSION_MAP.items()
		]

		return self.filter(
			# Worker must be viewable
			functools.reduce(operator.or_, filters),
			# AND org must be viewable to user
			org__in=Org.objects.viewable(user),
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

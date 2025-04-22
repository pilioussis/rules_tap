from django.db import models

class RoleType(models.TextChoices):
        ADMIN = 'AD', 'Admin'
        AUTH = 'AU', 'Authenticated'
        PUBLIC = 'PB', 'Public'

class UserQuerySet(models.QuerySet):
    def viewable(self, user, **kwargs):
        return self.filter(id=user.id, deactivated__isnull=True)


class User(models.Model):
    objects = UserQuerySet.as_manager()

    full_name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField(null=True, blank=True)
    role = models.CharField(
        max_length=2,
        choices=RoleType.choices,
        default=RoleType.PUBLIC,
    )


class OrgType(models.TextChoices):
        ACTIVE = 'AC', 'Active'
        PENDING = 'PE', 'Pending'
        INACTIVE = 'IN', 'Inactive'

class OrgQuerySet(models.QuerySet):
    def viewable_in_search(self):
        return self.filter(type__in=[OrgType.ACTIVE, OrgType.PENDING])

    def viewable(self, user, **kwargs):
        types = []
        if user.role == User.RoleType.PUBLIC:
            types = [OrgType.ACTIVE]
        elif user.role == User.RoleType.AUTH:
            types = [OrgType.ACTIVE, OrgType.PENDING]
        elif user.role == User.RoleType.ADMIN:
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
        viewable_types = [
            WorkerType.EMPLOYEE,
            WorkerType.CONTRACTOR,
        ]
        if user.role == User.RoleType.ADMIN:
            viewable_types.append(WorkerType.UNDERCOVER_AGENT)

        return self.filter(
             org__type__in=Org.objects.viewable(user),
             type__in=viewable_types,
        )
    
    def viewable_in_user_search(self, user):
         viewable_in_search = Org.objects.viewable_in_search()
         viewable_to_user = Org.objects.viewable(user)
         viewable_org_union = viewable_in_search | viewable_to_user

         return self.viewable(user).filter(org__in=viewable_org_union)

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
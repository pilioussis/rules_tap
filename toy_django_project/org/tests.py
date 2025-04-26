from org.models import User, Org, Worker
from django.test import TestCase
from . import api
class OrgTests(TestCase):
    def setUp(self):
        # Create an org with each type
        Org.objects.create(name="Active Org", type=Org.OrgType.ACTIVE)
        Org.objects.create(name="Inactive Org", type=Org.OrgType.INACTIVE)
        Org.objects.create(name="Pending Org", type=Org.OrgType.PENDING)

    def test_viewable_admin(self):
        # Admin should have access to all orgs
        admin_user = User.objects.create(role=User.RoleType.ADMIN)
        self.assertEqual(Org.objects.viewable(admin_user).count(), 3)

    def test_viewable_auth(self):
        # Authenticated users should have access to active and pending orgs
        auth_user = User.objects.create(role=User.RoleType.AUTH)
        self.assertEqual(Org.objects.viewable(auth_user).count(), 2)

    def test_viewable_public(self):
        # Authenticated users should have access to active and pending orgs
        pub_user = User.objects.create(role=User.RoleType.PUBLIC)
        self.assertEqual(Org.objects.viewable(pub_user).count(), 1)


class WorkerTests(TestCase):
    def setUp(self):
        # Create an org with each type
        self.inactive_org = Org.objects.create(name="Inactive Org", type=Org.OrgType.INACTIVE)
        self.active_org = Org.objects.create(name="Active Org", type=Org.OrgType.ACTIVE)
        self.pending_org = Org.objects.create(name="Pending Org", type=Org.OrgType.PENDING)

        # Create a worker for the inactive org
        self.active_employee = Worker.objects.create(org=self.active_org, type=Worker.WorkerType.EMPLOYEE)
        self.active_contractor = Worker.objects.create(org=self.active_org, type=Worker.WorkerType.CONTRACTOR)
        self.active_undercover_agent = Worker.objects.create(org=self.active_org, type=Worker.WorkerType.UNDERCOVER_AGENT)
        

    def test_pub_user_search(self):
        # Public users shouldn't be able to see undercover agents or workers in orgs they don't have access to
        pub_user = User.objects.create(role=User.RoleType.PUBLIC)

        viewable_workers = Worker.objects.viewable_in_user_search(pub_user)
        
        self.assertEqual(viewable_workers.count(), 2)



class SearchTests(TestCase):
    def test_pub_user_search(self):
        """
        Test the fuzzy name search works with permission filters.
        Admin workers should be able to see workers in both orgs, the public users should only be able to see the active org workers.
        """
        inactive_org = Org.objects.create(name="Inactive Org", type=Org.OrgType.INACTIVE)
        active_org = Org.objects.create(name="Active Org", type=Org.OrgType.ACTIVE)

        for org in [inactive_org, active_org]:
            Worker.objects.create(org=org, name="ADAM", type=Worker.WorkerType.EMPLOYEE)
            Worker.objects.create(org=org, name="amber", type=Worker.WorkerType.UNDERCOVER_AGENT)

        pub_user = User.objects.create(role=User.RoleType.PUBLIC)
        admin_user = User.objects.create(role=User.RoleType.ADMIN)

        results = api.get_workers_search_results(pub_user, {'name': "am"})
        self.assertEqual(results.count(), 1)

        results = api.get_workers_search_results(admin_user, {'name': "am"})
        self.assertEqual(results.count(), 2)
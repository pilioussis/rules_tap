from org.models import User, Org, Worker
from rules_tap.context.test_case_logger import TapTestCase
class OrgTests(TapTestCase):
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


class WorkerTests(TapTestCase):
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


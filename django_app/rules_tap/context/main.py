def get_context():
		# Use the context manager
	from django.test.runner import DiscoverRunner
	test_runner = DiscoverRunner(verbosity=2)
	tests_to_run = ['org.tests.OrgTests']
	test_runner.run_tests(tests_to_run)
	
if __name__ == "__main__":
	get_context()
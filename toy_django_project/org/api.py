from .models import Worker
def get_workers_search_results(user, filters: dict):
    """ Get the set of workers """
    workers = Worker.objects.viewable_in_user_search(user)

    if filters.get('name'):
        workers = workers.filter(name__icontains=filters['name'])
    
    return workers
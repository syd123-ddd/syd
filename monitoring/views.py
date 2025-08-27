import json
import jenkins
import requests
import logging
import pickle
import base64
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LogQuery, JenkinsJob


def index(request):
    log_queries = LogQuery.objects.all()
    jenkins_jobs = JenkinsJob.objects.all()
    return render(request, 'monitoring/index.html', {
        'log_queries': log_queries,
        'jenkins_jobs': jenkins_jobs
    })

@csrf_exempt
def query_loki_logs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            start_time = data.get('start_time')
            end_time = data.get('end_time')

            start_ts = int(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp())
            end_ts = int(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').timestamp())

            loki_url = f"{settings.LOKI_URL}/loki/api/v1/query_range"
            params = {
                'query': query,
                'start': start_ts,
                'end': end_ts,
                'limit': 1000,
            }
            response = requests.get(loki_url, params=params, verify=False)
            response_data = response.json()
            if 'data' in response_data and 'result' in response_data['data']:
                for result in response_data['data']['result']:
                    if 'stream' in result:
                        result['stream']['namespace'] = result['stream'].get('namespace', 'unknown')
                    if 'values' in result and ('detected_level' not in result['stream'] or result['stream']['detected_level'] == ''):
                        result['stream']['detected_level'] = get_log_level(result['values'])

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_loki_metrics(request):
    if request.method == 'GET':
        try:
            # get current time and 1h
            end_ts = int(datetime.now().timestamp())
            start_ts = end_ts - 3600  # 1h

            volume_query = 'count_over_time({namespace=~".+"}[5m])'
            volume_url = f"{settings.LOKI_URL}/loki/api/v1/query_range"
            volume_params = {
                'query': volume_query,
                'start': start_ts,
                'end': end_ts,
                'step': '5m'
            }
            
            try:
                volume_response = requests.get(volume_url, params=volume_params, timeout=10, verify=False)
                volume_response.raise_for_status()
                volume_data = volume_response.json()
            except requests.RequestException as e:
                volume_data = {'data': {'result': []}}

            error_query = 'count_over_time({namespace=~".+", level="error"}[5m])'
            error_url = f"{settings.LOKI_URL}/loki/api/v1/query_range"
            error_params = {
                'query': error_query,
                'start': start_ts,
                'end': end_ts,
                'step': '5m'
            }
            
            try:
                error_response = requests.get(error_url, params=error_params, timeout=10, verify=False)
                error_response.raise_for_status()
                error_data = error_response.json()
            except requests.RequestException as e:
                error_data = {'data': {'result': []}}

            combined_data = {
                'data': {
                    'result': []
                }
            }

            volume_results = volume_data.get('data', {}).get('result', [])
            if volume_results:
                combined_data['data']['result'].append({
                    'metric': {'type': 'volume'},
                    'values': volume_results[0].get('values', [])
                })

            # Add error metrics if available
            error_results = error_data.get('data', {}).get('result', [])
            if error_results:
                combined_data['data']['result'].append({
                    'metric': {'type': 'error'},
                    'values': error_results[0].get('values', [])
                })

            return JsonResponse(combined_data)
        except Exception as e:
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_log_level(values):
    try:
        # Try to parse as json first
        try:
            json_value = json.loads(values[1])
            if 'level' in json_value:
                return json_value['level']
            else:
                return 'unknown'
        except Exception as e:
            pass

        # Try to parse as pickle
        try:
            pick_value = pickle.loads(base64.b64decode(values[1]))
            if 'level' in pick_value:
                return pick_value['level']
            else:
                return 'unknown'
        except Exception as e:
            print(str(e))
            pass
        
        # Try to parse as string
        if 'error' in values[1]:
            return 'error'
        elif 'warn' in values[1]:
            return 'warn'
        elif 'info' in values[1]:
            return 'info'
        else:
            return 'unknown'
    except Exception as e:
        return 'unknown'

def get_jenkins_jobs(request):
    try:
        server = jenkins.Jenkins(
            settings.JENKINS_URL,
            username=settings.JENKINS_USER,
            password=settings.JENKINS_TOKEN
        )
        
        jobs = server.get_jobs()
        
        for job in jobs:
            if job.get('lastBuild'):
                build_info = server.get_build_info(job['name'], job['lastBuild']['number'])
                job['lastBuild']['timestamp'] = build_info.get('timestamp', 0)
                job['lastBuild']['duration'] = build_info.get('duration', 0)
                job['lastBuild']['result'] = build_info.get('result', 'UNKNOWN')
        
        return JsonResponse({'jobs': jobs})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_jenkins_build_info(request, job_name):
    try:
        server = jenkins.Jenkins(
            settings.JENKINS_URL,
            username=settings.JENKINS_USER,
            password=settings.JENKINS_TOKEN
        )
        
        job_info = server.get_job_info(job_name)
        
        if 'builds' in job_info:
            for build in job_info['builds']:
                build_info = server.get_build_info(job_name, build['number'])
                build['timestamp'] = build_info.get('timestamp', 0)
                build['duration'] = build_info.get('duration', 0)
                build['result'] = build_info.get('result', 'UNKNOWN')
        
        return JsonResponse(job_info)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

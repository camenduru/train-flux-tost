import os, json, tempfile, requests, runpod

import yaml
from toolkit.job import get_job
from pyupload.uploader import *

def download_file(url, save_dir, file_name):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file_name)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path

def generate(input):
    values = input['input']

    name = values['name']
    name = name.replace(" ", "_")
    images = values['images']
    config_yaml_url = values['config_yaml_url']

    temp_path = '/content/ai-toolkit/temp'
    os.makedirs(temp_path, exist_ok=True)
    replace_yaml_file = download_file(url=config_yaml_url, save_dir=temp_path, file_name='replace.yaml')
    config_yaml_file = f'{temp_path}/{name}/{name}.yaml'
    directory_path = os.path.dirname(config_yaml_file)
    os.makedirs(directory_path, exist_ok=True)
    with open(replace_yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    config['config']['name'] = name
    config['config']['process'][0]['datasets'][0]['folder_path'] = config['config']['process'][0]['datasets'][0]['folder_path'].replace('replace', name)
    config['config']['process'][0]['trigger_word'] = name
    with open(config_yaml_file, 'w') as file:
        yaml.dump(config, file, sort_keys=False)

    for i, image in enumerate(images):
        file_suffix = os.path.splitext(image['url'])[1]
        download_file(url=image['url'], save_dir=directory_path, file_name=f'{i+1}_Euler_{name}{file_suffix}')

    job = get_job(config_yaml_file)
    job.run()
    job.cleanup()

    result = f"/content/ai-toolkit/output/{name}/{name}.safetensors"
    try:
        notify_uri = values['notify_uri']
        del values['notify_uri']
        notify_token = values['notify_token']
        del values['notify_token']
        discord_id = values['discord_id']
        del values['discord_id']
        if(discord_id == "discord_id"):
            discord_id = os.getenv('com_camenduru_discord_id')
        discord_channel = values['discord_channel']
        del values['discord_channel']
        if(discord_channel == "discord_channel"):
            discord_channel = os.getenv('com_camenduru_discord_channel')
        discord_token = values['discord_token']
        del values['discord_token']
        if(discord_token == "discord_token"):
            discord_token = os.getenv('com_camenduru_discord_token')
        job_id = values['job_id']
        del values['job_id']
        uploader = CatboxUploader(result)
        for attempt in range(5):
            result_url = uploader.execute()
            if 'html' not in result_url.lower():
                break
        payload = {"content": f"{json.dumps(values)} <@{discord_id}> {result_url}"}
        response = requests.post(
            f"https://discord.com/api/v9/channels/{discord_channel}/messages",
            data=payload,
            headers={"Authorization": f"Bot {discord_token}"}
        )
        response.raise_for_status()
        notify_payload = {"jobId": job_id, "result": result_url, "status": "DONE"}
        web_notify_uri = os.getenv('com_camenduru_web_notify_uri')
        web_notify_token = os.getenv('com_camenduru_web_notify_token')
        if(notify_uri == "notify_uri"):
            requests.post(web_notify_uri, data=json.dumps(notify_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
        else:
            requests.post(web_notify_uri, data=json.dumps(notify_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
            requests.post(notify_uri, data=json.dumps(notify_payload), headers={'Content-Type': 'application/json', "Authorization": notify_token})
        return {"jobId": job_id, "result": result_url, "status": "DONE"}
    except Exception as e:
        error_payload = {"jobId": job_id, "status": "FAILED"}
        try:
            if(notify_uri == "notify_uri"):
                requests.post(web_notify_uri, data=json.dumps(error_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
            else:
                requests.post(web_notify_uri, data=json.dumps(error_payload), headers={'Content-Type': 'application/json', "Authorization": web_notify_token})
                requests.post(notify_uri, data=json.dumps(error_payload), headers={'Content-Type': 'application/json', "Authorization": notify_token})
        except:
            pass
        return {"jobId": job_id, "result": f"FAILED: {str(e)}", "status": "FAILED"}
    finally:
        if os.path.exists(result):
            os.remove(result)

runpod.serverless.start({"handler": generate})
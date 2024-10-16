import os, shutil, json, tempfile, requests, boto3, runpod

import yaml
from toolkit.job import get_job
from slugify import slugify
from datetime import datetime

def download_file(url, save_dir, file_name):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file_name)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path

def generate(input):
    try:
        values = input['input']

        name = values['name']
        name = slugify(name)
        images = values['images']
        config_yaml_url = values['config_yaml_url']

        if not isinstance(name, str) or not name:
            return {"error": "Invalid or missing 'name'"}
        if not isinstance(images, list) or len(images) == 0:
            return {"error": "No images provided or invalid 'image' format"}
        if not isinstance(config_yaml_url, str) or not config_yaml_url:
            return {"error": "Invalid or missing 'config_yaml_url'"}

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
        result_path = f"/content/ai-toolkit/output/{name}"

        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        s3_access_key_id = os.getenv('s3_access_key_id')
        s3_secret_access_key = os.getenv('s3_secret_access_key')
        s3_endpoint_url = os.getenv('s3_endpoint_url')
        r2_dev_url = os.getenv('r2_dev_url')
        s3_bucket_name = os.getenv('s3_bucket_name')
        s3 = boto3.client('s3', aws_access_key_id=s3_access_key_id, aws_secret_access_key=s3_secret_access_key, endpoint_url=f"https://{s3_endpoint_url}")
        s3.upload_file(result, s3_bucket_name, f"tost-{current_time}-{name}.safetensors", ExtraArgs={'ACL': 'public-read'})
        if r2_dev_url:
            result_url = f"https://{r2_dev_url}/tost-{current_time}-{name}.safetensors"
        else:
            result_url = f"https://{s3_endpoint_url}/{s3_bucket_name}/tost-{current_time}-{name}.safetensors"
        
        return {"result": result_url}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        if os.path.exists(result_path):
            shutil.rmtree(result_path)

runpod.serverless.start({"handler": generate})
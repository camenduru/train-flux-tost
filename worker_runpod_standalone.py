import os, shutil, json, tempfile, requests, boto3, runpod

import yaml
from toolkit.job import get_job
from slugify import slugify
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

session = requests.Session()

def download_file(url, save_dir, file_name):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file_name)
    response = session.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path

def parallel_download(images, save_dir, name):
    with ThreadPoolExecutor() as executor:
        futures = []
        for i, image in enumerate(images):
            file_suffix = os.path.splitext(image['url'])[1]
            file_name = f'{i+1}_Euler_{name}{file_suffix}'
            futures.append(executor.submit(download_file, image['url'], save_dir, file_name))
        for future in as_completed(futures):
            future.result()

def generate(input):
    try:
        values = input['input']

        name = slugify(values['name'])
        images = values['images']
        config_yaml_url = values['config_yaml_url']

        temp_path = tempfile.mkdtemp(prefix="ai-toolkit-")
        replace_yaml_file = download_file(url=config_yaml_url, save_dir=temp_path, file_name='replace.yaml')
        config_yaml_file = os.path.join(temp_path, name, f'{name}.yaml')
        directory_path = os.path.dirname(config_yaml_file)
        os.makedirs(directory_path, exist_ok=True)
        with open(replace_yaml_file, 'r') as file:
            config = yaml.safe_load(file)
        config['config']['name'] = name
        config['config']['process'][0]['datasets'][0]['folder_path'] = config['config']['process'][0]['datasets'][0]['folder_path'].replace('replace', name)
        config['config']['process'][0]['trigger_word'] = name
        with open(config_yaml_file, 'w') as file:
            yaml.dump(config, file, sort_keys=False)

        parallel_download(images, directory_path, name)

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
            try:
                shutil.rmtree(temp_path, ignore_errors=True)
            except Exception as e:
                print(f"Error during temp path cleanup: {e}")

runpod.serverless.start({"handler": generate})
def query_moderation(content, max_num_retries=3, wait_time=60):
    client = OpenAI()
    num_retries = 0
    finished = False
    while (not finished) and num_retries <= max_num_retries:
        if num_retries > 0:
            print (f'retrying {num_retries} times')
        try:
            response = client.moderations.create(input=content)
            finished = True
        except Exception as e:
            err_msg = f'{e}'
            print (err_msg)
            m = re.search(r"Please try again in (\d+\.?\d*)s", err_msg)
            num_retries += 1
            if m:
                sleep_time = min(float(m.group(1)) * 1.2, wait_time)
                print (f'sleeping: {sleep_time} seconds')
                time.sleep(sleep_time)
            else:
                time.sleep(wait_time)
    if not finished:
        content_length = len(content)
        half_length = int(round(content_length / 2))
        content_firsthalf = content[:half_length]
        content_secondhalf = content[half_length:]
        print (f'splitting, old length: {content_length} into new length: {half_length}')
        output_firsthalf = query_moderation(content_firsthalf, max_num_retries, wait_time)
        output_secondhalf = query_moderation(content_secondhalf, max_num_retries, wait_time)
        output = {'flagged': output_firsthalf['flagged'] or output_secondhalf['flagged']}
        output['categories'] = {}
        for k in output_firsthalf['categories']:
            output['categories'][k] = output_firsthalf['categories'][k] or output_secondhalf['categories'][k]
        output['category_scores'] = {}
        for k in output_firsthalf['category_scores']:
            output['category_scores'][k] = max(output_firsthalf['category_scores'][k], output_secondhalf['category_scores'][k])
    else:
        output = response.results[0].model_dump()
    return output

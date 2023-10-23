#script_names = ['collection_twitter.py', 'translation.py', 'Sent2.py', 'theme.py','zero_shot.py']
script_names = ['translation.py', 'Sent2.py', 'theme.py','zero_shot.py']
for script in script_names:
    with open(script, 'r',encoding='utf-8') as file:
        exec(file.read())
#script_names = ['collection.py', 'translation.py', 'Sent2.py',  'theme.py', 'zero_shot.py', 'analysis.py']
script_names = ['theme.py','zero_shot.py']
for script in script_names:
    with open(script, 'r',encoding='utf-8') as file:
        exec(file.read())
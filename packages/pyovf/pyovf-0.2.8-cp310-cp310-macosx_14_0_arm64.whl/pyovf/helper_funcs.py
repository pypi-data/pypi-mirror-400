# (c) 2021 by Dr. Flavio ABREU ARAUJO. All rights reserved.

#* Format file size in human readable format
# TODO: use 'pip install humanize' lib for that and much more :-)
def size_hrf(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return f'{num:.4g}{unit}{suffix}'
        num /= 1024.0
    return f'{num:.4g}Yi{suffix}'

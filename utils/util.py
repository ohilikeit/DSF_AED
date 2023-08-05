import base64
import re

def multipolygon_to_coordinates(x): 
    lon, lat = x[0].exterior.xy 
    return [[x, y] for x, y in zip(lon, lat)] 

def polygon_to_coordinates(x): 
    lon, lat = x.exterior.xy 
    return [[x, y] for x, y in zip(lon, lat)] 

def image_to_data_url(filename):
    ext = filename.split('.')[-1]
    prefix = f'data:image/{ext};base64,'
    with open(filename, 'rb') as f:
        img = f.read()
    return prefix + base64.b64encode(img).decode('utf-8')

# 데이터 오류 정정 후 geometry 형식 변환하는 함수 
def wkt_to_geometry(string):
    string = re.findall(r'\d+', string)
    lst = []
    lst.append([float(string[0] + '.' + string[1]), float(string[2] + '.' + string[3][:-3])])
    for i in range(3, len(string), 3):
        try:
            lst.append([float(string[i][-3:] + '.' + string[i+1]), float(string[i+2] + "." + string[i+3][:-3])])
        except:
            continue
    
    return lst
# 데이터 사이언스 페스티벌 경진대회 
- 주제 : **24시 응급체계를 위한 실외 AED 최적 위치 선정**
- 기간 : 2022.11. ~ 2022.12
- 최종 순위 : **1 st (50 teams)**

## Introduction
- 현재 AED는 공공기관과 지하철에 밀집되어 퇴근시간 대 이후 대부분 사용 불가함
- 이에 동대문구를 기준으로 대부분의 지역에서 24시 내내 AED를 사용할 수 있게 실외 스마트 AED를 설치하고자 함
<img src="https://user-images.githubusercontent.com/37128004/208828859-b538da7c-917f-47bf-9010-9b21bbd881b0.png" width="1000" height="350"/>

## Preprocess & Model 
### 0. polygon data
 AED 유효볌위(200m) 시각화, 수요량 계산 및 모델링을 위하여 200 buffer, 100 buffer를 생성
 - Example code: 
 ```
 # geodata 변경 buffer 생성 - 기존 24시간 가동 AED와의 유효거리 기반 수요량 b(buffer_100)
gs = gpd.GeoSeries.from_wkt(df['노드 WKT'])
df_dobo_100 = gpd.GeoDataFrame(df, geometry = gs, crs = 'epsg:4326')

df_dobo_100 = df_dobo_100.set_geometry('geometry')
df_dobo_100['buffer_100'] = df_dobo_100.to_crs('epsg:5179').buffer(100).to_crs('epsg:4326')
df_dobo_100 = df_dobo_100.set_geometry('buffer_100')
df_dobo_100['buffer_100_coordinates'] = df_dobo_100['buffer_100'].apply(polygon_to_coordinates)
```

### 1. MCLP(Maximal Covering Location Problem)
 시설물의 개수 혹은 예산 비용이 제한되었을 때, 시설물의 서비스 수준을 높이기 위하여 주어진 제약조건 하에서 시설물이 커버하는 수요량을 최대화하는 위치를 선정하는 방법
<img src="https://user-images.githubusercontent.com/37128004/208839441-20a30452-e356-4a55-81d2-f2f943d62a04.png" width="1000" height="350"/>

### 2. 모델 가정 
1. 수요지와 후보지는 동일
2. AED 유효거리는 200m
3. 도보 노드-링크 데이터를 후보지로 활용
<center><img src="https://user-images.githubusercontent.com/37128004/208840998-def5ad81-7025-4b74-87e7-65ddbd8a5f67.png" width="400" height="400"/></center>
4. 최종 수요량(W) = 0.4 * a + 0.3 * b + 0.3 * c
<img src="https://user-images.githubusercontent.com/37128004/208841923-c5de8013-b938-4a65-9f76-cf7f2f8f4ff1.png" width="800" height="400"/>

### 3. 행정동 별 심정지 가능인구 추정량(수요량 a)
동별, 성별, 나이대별 인구데이터에 해당 구간 별 심정지 발생량을 곱한 weighted sum
```
pop = pd.read_csv('./동대문구_동별_연령대별_인구수.csv')
cols = pop.columns
pop['male'] = pop[cols[2]] * 0.01 + pop[cols[3]] * 0.026 + pop[cols[4]] * 0.039 + pop[cols[5]] * 0.075 + pop[cols[6]] * 0.139 + pop[cols[7]] * 0.7
pop['male'] = pop['male'] / pop['male'].max()
pop['female'] = pop[cols[8]] * 0.01 + pop[cols[9]] * 0.026 + pop[cols[10]] * 0.039 + pop[cols[11]] * 0.075 + pop[cols[12]] * 0.139 + pop[cols[13]] * 0.7
pop['female'] = pop['female'] / pop['female'].max()
pop['a'] = 0.64 * pop['male'] + 0.36 * pop['female']
```
### 4. 반경 200m 이내 기존 24시간 AED 개수와 겹치는 정도(수요량 b, c) 
 주변에 기존 24시간 가동 AED가 몇개 있고 얼마나 가깝게 있는가
```
total = pd.DataFrame()
for i in tqdm(df_dobo_100.index):
    db = df_dobo_100.loc[i, 'buffer_100']
    num = []
    area = []
    for j in aed_24_100.index:
        aed = aed_24_100.loc[j, "buffer_100"]
        num.append(db.intersects(aed))
        if db.intersects(aed) == True:
            area.append(db.intersection(aed).area)
    info = {"intersects_num" : sum(num), "intersects_area" : sum(area)}
    total = total.append(info, ignore_index=True)

# 정규화 및 최종 수요량 산출 
total['intersects_num_scaled'] = (total['intersects_num'].max() - total['intersects_num']) / total['intersects_num'].max()
total['intersects_area_scaled'] = (total['intersects_area'].max() - total['intersects_area']) / total['intersects_area'].max()

df_dobo_200['b'] = total['intersects_num_scaled'].values
df_dobo_200['c'] = total['intersects_area_scaled'].values
df_dobo_200['w'] = 0.4 * df_dobo_200['a'] + 0.3 * df_dobo_200['b'] + 0.3 * df_dobo_200['c']
```

### 5. MCLP modeling
 mlp(mixed integer programming)을 통한 최적화
```
temp = df_dobo_200.copy()

temp['노드 ID'] = pd.to_numeric(temp['노드 ID'])
temp['w'].index = temp['노드 ID']
w = temp['w']
model = Model()
model.max_gap = 0.0
x = [model.add_var(name = "x%d" % i, var_type = BINARY) for i in temp['노드 ID']]           # 제약 조건 3 : 포인트에 설치되는가
y = [model.add_var(name = "y%d" % i, var_type = BINARY) for i in temp['노드 ID']]           # 제약 조건 4 : 포인트가 커버되는가
model.objective = maximize(xsum(w[i] * model.vars['y%d' %i] for i in temp['노드 ID']))      # 목적함수
model += xsum(model.vars['x%d' %j] for j in temp['노드 ID']) == 40                          # 제약 조건 2 : 설치할 AED 개수

for num, idx in enumerate(temp['노드 ID']):
    model += xsum(model.vars['x%d' %j] for j in cond_list[num]) >= model.vars['y%d' %idx]   # 제약 조건 1 : cond_list(집합 N)에 속한 후보지 중 적어도 한 곳에 AED가 입지하면 i는 커버됨 
model.optimize()
solution = []
for j in temp['노드 ID']:
    if model.vars['x%d' %j].x == 0:
        solution.append(0)
    else:
        solution.append(1)
temp['sol'] = solution
sol = temp[temp['sol'] == 1]
```

## Conclusions
### 1. 추가 AED 개수에 따른 커버리지 변화
 추가 AED 개수 증가에 따라 커버리지 증가율이 체감, 합리적인 개수 설정이 필요 
 
 <img src="https://user-images.githubusercontent.com/37128004/208844508-26d99982-89b7-45d2-b0c2-956b42ddd95c.png" width="650" height="400"/>
 
### 2. 최종 후보지 선정 
 최종적으로 40개의 추가 AED 설치, 전체 약 81% 커버
 
<img src="https://user-images.githubusercontent.com/37128004/208846459-51c79494-6194-40d0-837d-77d53b3119aa.png" width="500" height="500"/>

## Requirements
- geopandas
- pydeck
- mip
- pandas
- shapely

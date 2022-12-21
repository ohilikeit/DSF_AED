# 데이터 사이언스 페스티벌 경진대회 
- 주제 : **24시 응급체계를 위한 실외 AED 최적 위치 선정**
- 기간 : 2022.11. ~ 2022.12
- 최종 순위 : **1 st (50 teams)**

## Introduction
- 현재 AED는 공공기관과 지하철에 밀집되어 퇴근시간 대 이후 대부분 사용 불가함
- 이에 동대문구를 기준으로 대부분의 지역에서 24시 내내 AED를 사용할 수 있게 실외 스마트 AED를 설치하고자 함
<img src="https://user-images.githubusercontent.com/37128004/208828859-b538da7c-917f-47bf-9010-9b21bbd881b0.png" width="1000" height="350"/>

## Preprocess
### 1. 행정동 별 심정지 가능인구 추정량(수요량 a)
동별, 성별, 나이대별 인구 X 해당 구간 별 심정지 발생량 
```
pop = pd.read_csv('./동대문구_동별_연령대별_인구수.csv')
cols = pop.columns
pop['male'] = pop[cols[2]] * 0.01 + pop[cols[3]] * 0.026 + pop[cols[4]] * 0.039 + pop[cols[5]] * 0.075 + pop[cols[6]] * 0.139 + pop[cols[7]] * 0.7
pop['male'] = pop['male'] / pop['male'].max()
pop['female'] = pop[cols[8]] * 0.01 + pop[cols[9]] * 0.026 + pop[cols[10]] * 0.039 + pop[cols[11]] * 0.075 + pop[cols[12]] * 0.139 + pop[cols[13]] * 0.7
pop['female'] = pop['female'] / pop['female'].max()
pop['a'] = 0.64 * pop['male'] + 0.36 * pop['female']
```
### 2. 




## Modeling



## Conclusions


## Requirements
- geopandas
- pydeck
- mip
- pandas
- shapely

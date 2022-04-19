import os
import math
import pandas as pd

POLE_RADIUS = 6356752    # 極半径(短半径)
EQUATOR_RADIUS = 6378137 # 赤道半径(長半径)
E = 0.081819191042815790 # 離心率
E2= 0.006694380022900788 # 離心率の２乗

class Coordinate:
    def __init__(self, latitude, longitude):
        self.latitude  = latitude
        self.longitude = longitude
        #self.altitude  = altitude

def distance(point_a, point_b):
    a_rad_lat = math.radians(point_a.latitude)
    a_rad_lon = math.radians(point_a.longitude)
    b_rad_lat = math.radians(point_b.latitude)
    b_rad_lon = math.radians(point_b.longitude)
    m_lat = (a_rad_lat + b_rad_lat) / 2 # 平均緯度
    d_lat = a_rad_lat - b_rad_lat # 緯度差
    d_lon = a_rad_lon - b_rad_lon # 経度差
    W = math.sqrt(1-E2*math.pow(math.sin(m_lat),2))
    M = EQUATOR_RADIUS*(1-E2) / math.pow(W, 3) # 子午線曲率半径
    N = EQUATOR_RADIUS / W # 卯酉線曲率半径
    # d = math.sqrt(math.pow(M*d_lat,2) + math.pow(N*d_lon*math.cos(m_lat),2) + math.pow(point_a.altitude-point_b.altitude,2))
    d = math.sqrt(math.pow(M*d_lat,2) + math.pow(N*d_lon*math.cos(m_lat),2))
    return d

train = pd.read_csv("train_data.csv")
test = pd.read_csv("test_data.csv")
stations = pd.read_csv("station_list.csv")

all_data = pd.concat([train,test],axis=0)

if os.path.exists("distance.csv"):
    print("distance.csv already existed")
    pass
else:
    print("let's make the distance!")
    #最寄り駅と最寄り駅からの距離を算出したい
    #ヒュベニの公式を用いて距離を算出
    
    #駅と距離を入れる辞書を作成
    distance_from_station = dict()
    #最寄り駅を入れるリストを作成
    near_station = list()
    #最寄り駅からの距離を入れるリストを作成
    distance_list = list()

    #宿泊施設の緯度経度を保存
    INN_df = pd.DataFrame({"latitude":all_data["latitude"],"longitude":all_data["longitude"]})
    INN_place_list = [list(x) for x in INN_df.values]

    stations_df = pd.DataFrame({"latitude":stations["latitude"],"longitude":stations["longitude"]})
    stations_list = [list(x) for x in stations_df.values]
    #from IPython.core.debugger import Pdb; Pdb().set_trace()
    for i in range(all_data.shape[0]):
        for j in range(stations.shape[0]):
            #駅から宿泊施設の距離を保存
            distance1 = Coordinate(INN_place_list[i][0],INN_place_list[i][1])
            distance2 = Coordinate(stations_list[j][0],stations_list[j][1])
            dist = distance(distance1,distance2)
            #初期設定
            if j == 0:
                key = stations.iloc[0]["station_name"]
                distance_from_station[key] = dist
            elif distance_from_station[key] > dist:
                #前の駅の距離が今の駅の距離より大きかったら辞書のキーとバリューを新しい駅のものに入れ替える。
                distance_from_station = dict()
                distance_from_station[stations.iloc[j]["station_name"]] = dist
                key = stations.iloc[j]["station_name"]
        #各宿泊施設の最寄り駅リストに駅を追加
        near_station.append(key)
        #上記と同様の流れで距離をリストに追加
        distance_list.append(distance_from_station[key])
        if len(near_station) % 1000 == 0:
            print(distance_from_station)
    all_data["near_station"] = pd.DataFrame(near_station)
    all_data["dist_from_sta"] = pd.DataFrame(distance_list)
    all_data[["near_station","dist_from_sta"]].to_csv("distance.csv",index=False)
    print("Done.Good luck!")
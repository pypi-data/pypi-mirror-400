import requests
import concurrent.futures as futures
from pandas import DataFrame
from tqdm import tqdm
import time


def __geocode_item(session, index: int, addr: str, key: str) -> dict:
    if not addr or addr == "nan":
        raise ValueError(
            "⚠️[Warning] 주소가 존재하지 않습니다. (%d) -> %s" % (index, addr)
        )

    url: str = f"https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getCoord",
        "key": key,
        "address": addr,
        "type": "ROAD",
        "format": "json",
    }

    response = None

    try:
        response = session.get(url, params=params, timeout=(3, 30))
    except Exception as e:
        raise e

    if response.status_code != 200:
        raise Exception(
            "⚠️[%d-Error] %s - API 요청에 실패했습니다. (%d) -> %s"
            % (response.status_code, response.reason, index, addr)
        )

    response.encoding = "utf-8"
    result = response.json()
    status = result["response"]["status"]

    if status == "ERROR":
        error_code = result["response"]["error"]["code"]
        error_text = result["response"]["error"]["text"]
        raise Exception(f"[{error_code}] {error_text} (%d) -> %s" % (index, addr))
    elif status == "NOT_FOUND":
        raise requests.exceptions.RequestException(
            "⚠️[Warning] 주소를 찾을 수 없습니다. (%d) -> %s" % (index, addr)
        )

    longitude = float(result["response"]["result"]["point"]["x"])
    latitude = float(result["response"]["result"]["point"]["y"])
    result = (latitude, longitude)
    print("%s --> (%s, %s)" % (addr, latitude, longitude))
    return result


def geocode(df: DataFrame, addr: str, key: str) -> DataFrame:
    data: DataFrame = df.copy()
    size: int = len(data)
    success = 0
    fail = 0

    print("ℹ️요청 데이터 개수: %d" % size)

    print("------------------------------------------")

    with tqdm(total=size, colour="yellow") as pbar:
        with requests.Session() as session:
            with futures.ThreadPoolExecutor(max_workers=30) as executor:
                for i in range(size):
                    time.sleep(0.1)
                    address: str = str(data.loc[i, addr]).strip()

                    p = executor.submit(
                        __geocode_item, session, index=i, addr=address, key=key
                    )

                    try:
                        result = p.result()
                        latitude, longitude = result
                        data.loc[i, "latitude"] = latitude
                        data.loc[i, "longitude"] = longitude
                        success += 1
                    except requests.exceptions.RequestException as re:
                        print(re)
                        data.loc[i, "latitude"] = None
                        data.loc[i, "longitude"] = None
                        fail += 1
                    except ValueError as ve:
                        print(ve)
                        data.loc[i, "latitude"] = None
                        data.loc[i, "longitude"] = None
                        fail += 1
                    except Exception as e:
                        fail += 1
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise e
                    finally:
                        pbar.set_postfix({"success": success, "fail": fail})
                        pbar.update(1)

    data["latitude"] = data["latitude"].astype(float)
    data["longitude"] = data["longitude"].astype(float)
    print("------------------------------------------")
    print(f"✅총 {size}개의 데이터 중 {success}개의 데이터가 처리되었습니다.")
    print("------------------------------------------")

    return data
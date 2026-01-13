import pandas as pd

def call_pandas():

    # 建立一個小表格（DataFrame）
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Cathy", "Dan"],
        "age":  [25, 30, 29, 35],
        "score":[88, 92, 75, 85]
    })

    print("原始資料：")
    print(df)

    # 選欄位
    print("\n只有 name 與 score：")
    print(df[["name", "score"]])

    # 篩選列（年齡 >= 30）
    print("\n年齡 >= 30：")
    print(df[df["age"] >= 30])

    # 基本統計
    print("\n平均分數：", df["score"].mean())

    # 依條件彙總（這裡示範依是否>=30歲分組，計算平均分數）
    print("\n依是否>=30歲分組的平均分數：")
    print(df.assign(age_ge_30 = df["age"] >= 30)
            .groupby("age_ge_30")["score"]
            .mean())

from pymilvus import connections, Collection

# 連接到 Milvus
connections.connect(alias="default", host="localhost", port=19530)

# 開啟 collection 並載入
collection = Collection("copd_qa")
collection.load()

# 查詢前 1000 筆資料（如超過可分批查）
results = collection.query(
    expr="",
    output_fields=["id", "category", "question", "answer", "keywords", "notes"],
    limit=1000
)

# 印前幾筆（如你要全不要印，就刪掉下面）
for i, row in enumerate(results):
    print(f"#{i+1} | 類別: {row['category']} | 問題: {row['question']}")

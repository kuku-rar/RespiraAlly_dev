from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections, utility
import pandas as pd
import os
import re
from embedding import to_vector # 你的向量化


# ===== 連線 =====
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
COPD_COLL = os.getenv("COPD_COLL_NAME", "copd_qa")
INDEX_HINT = os.getenv("COPD_INDEX", "auto").upper() # AUTO | HNSW | IVF_FLAT


connections.connect(alias="default", uri=MILVUS_URI)


# ===== 讀資料 =====
df = pd.read_excel("COPD_QA.xlsx")
# 基本清洗：轉字串、去換行/多空白
clean = lambda s: re.sub(r"\s+", " ", str(s or "").replace("\u3000", " ").strip())
cat = df["類別"].map(clean).tolist()
q = df["問題（Q）"].map(clean).tolist()
a = df["回答（A）"].map(clean).tolist()
kw = df.get("關鍵詞", "").map(clean).tolist()
nt = df.get("注意事項 / 補充說明", "").map(clean).tolist()


combined = [f"{qq} {aa}" for qq, aa in zip(q, a)]
vecs = to_vector(combined)
DIM = len(vecs[0])
N = len(combined)


# ===== 砍舊建新 =====
if utility.has_collection(COPD_COLL):
    Collection(COPD_COLL).drop()


fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=128),
    FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=1024),
    FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=8192), # 放大
    FieldSchema(name="keywords", dtype=DataType.VARCHAR, max_length=1024),
    FieldSchema(name="notes", dtype=DataType.VARCHAR, max_length=2048),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIM),
]
schema = CollectionSchema(fields=fields, description="COPD QA 集合（Q+A 向量）")
col = Collection(name=COPD_COLL, schema=schema)


# ===== 插入（auto_id=True → 不傳 id） =====
col.insert([
    cat,
    q,
    a,
    kw,
    nt,
    vecs,
])
col.flush()


# ===== 索引策略（自動 or 指定） =====
def _choose_index(n):
    if INDEX_HINT in {"HNSW", "IVF_FLAT"}:
        return INDEX_HINT
    return "HNSW" if n <= 200_000 else "IVF_FLAT"


index_type = _choose_index(N)
if index_type == "HNSW":
    col.create_index(
        field_name="embedding",
        index_params={
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200},
    },
    )
else:
# IVF_FLAT for very large N（若要壓記憶體可改 IVF_SQ8）
    nlist = max(256, min(16384, int((N ** 0.5) * 4)))
    col.create_index(
        field_name="embedding",
        index_params={
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": nlist},
    },
    )


print(f"✅ {COPD_COLL} 建好：N={N}, dim={DIM}, index={index_type}")
import io
import logging
import os
import tempfile
from typing import Optional

import torch
from minio import Minio
from minio.error import S3Error

# 可選匯入：若環境未安裝則保留為佔位 STT
try:
    import torchaudio
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
    from transformers import pipeline as hf_pipeline

    TORCH_AVAILABLE = True
    TORCHAUDIO_AVAILABLE = True
except Exception:
    torch = None
    torchaudio = None
    AutoModelForSpeechSeq2Seq = None
    AutoProcessor = None
    hf_pipeline = None
    TORCH_AVAILABLE = False
    TORCHAUDIO_AVAILABLE = False

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STTService:
    def __init__(self):
        self.minio_client = Minio(
            os.environ.get("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.environ.get("MINIO_ACCESS_KEY"),
            secret_key=os.environ.get("MINIO_SECRET_KEY"),
            secure=False,
        )

        # ASR 模型設定
        self.asr_model_name = os.environ.get(
            "ASR_MODEL_NAME", "shaobai880824/breeze-asr-25-local-hokkien_v1"
        )
        self.device: Optional[str] = None
        self.torch_dtype = None
        self.asr_pipe = None
        self.model = None
        self.processor = None

        self._maybe_load_asr()

    def _maybe_load_asr(self) -> None:
        """載入 Hugging Face ASR 模型，支援 GPU 加速"""
        if not TORCH_AVAILABLE:
            logger.warning("未安裝 torch/transformers，將使用佔位 STT")
            return

        try:
            # 設定裝置和資料型別
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            self.torch_dtype = (
                torch.float16 if torch.cuda.is_available() else torch.float32
            )

            logger.info(f"使用的裝置: {self.device}")
            logger.info(f"使用的資料型別: {self.torch_dtype}")
            logger.info(f"正在載入 ASR 模型: {self.asr_model_name}")

            # 載入模型和處理器
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.asr_model_name,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
            self.model.to(self.device)
            self.processor = AutoProcessor.from_pretrained(self.asr_model_name)

            # 建立 pipeline
            self.asr_pipe = hf_pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=4,
                return_timestamps=True,
                torch_dtype=self.torch_dtype,
                device=self.device,
            )
            logger.info("ASR 模型載入成功！")
        except Exception as exc:
            logger.error(f"ASR 模型載入失敗，改用佔位 STT：{exc}")
            self.asr_pipe = None

    def list_audio_files(self, bucket_name: str) -> list:
        """列出指定 bucket 中的所有音檔"""
        try:
            objects = self.minio_client.list_objects(bucket_name, recursive=True)
            audio_files = []
            audio_extensions = [".mp3", ".wav", ".m4a", ".mp4", ".aac", ".flac", ".ogg"]

            for obj in objects:
                file_ext = os.path.splitext(obj.object_name)[1].lower()
                if file_ext in audio_extensions:
                    audio_files.append(
                        {
                            "name": obj.object_name,
                            "size": obj.size,
                            "last_modified": obj.last_modified,
                            "etag": obj.etag,  # 添加 ETag (通常是 MD5)
                        }
                    )

            return audio_files
        except S3Error as exc:
            logger.error(f"列出檔案時發生錯誤: {exc}")
            return []

    def get_file_hash(self, bucket_name: str, object_name: str) -> str:
        """獲取檔案的 MD5 雜湊值"""
        try:
            import hashlib

            obj = self.minio_client.get_object(bucket_name, object_name)
            try:
                audio_bytes = obj.read()
                md5_hash = hashlib.md5(audio_bytes).hexdigest()
                return md5_hash
            finally:
                obj.close()
                obj.release_conn()
        except Exception as e:
            logger.error(f"計算檔案雜湊值時發生錯誤: {e}")
            return "error"

    def _load_audio_robust(self, audio_bytes: bytes, filename: str = "audio"):
        """
        強化的音檔載入方法，支援多種格式
        """
        # 方法1: 直接使用 torchaudio
        if TORCHAUDIO_AVAILABLE:
            try:
                waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
                logger.info("✅ 使用 torchaudio 直接載入成功")
                return waveform, sample_rate
            except Exception as e:
                logger.debug(f"torchaudio 直接載入失敗: {str(e)}")

        # 方法2: 儲存為臨時檔案後載入
        if TORCHAUDIO_AVAILABLE:
            try:
                # 根據檔名判斷副檔名
                if filename.lower().endswith((".m4a", ".mp3", ".wav")):
                    suffix = os.path.splitext(filename)[1]
                else:
                    suffix = ".m4a"

                with tempfile.NamedTemporaryFile(
                    suffix=suffix, delete=False
                ) as temp_file:
                    temp_file.write(audio_bytes)
                    temp_path = temp_file.name

                try:
                    waveform, sample_rate = torchaudio.load(temp_path)
                    logger.info(f"✅ 使用臨時檔案載入成功: {suffix}")
                    return waveform, sample_rate
                finally:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

            except Exception as e:
                logger.debug(f"臨時檔案載入失敗: {str(e)}")

        # 如果都失敗，拋出異常
        raise Exception(
            f"無法載入音檔，已嘗試所有可用方法。檔案大小: {len(audio_bytes)} bytes"
        )

    def transcribe_audio(self, bucket_name: str, object_name: str) -> str:
        """
        從 MinIO 下載音檔並進行轉錄，支援 GPU 加速
        """
        try:
            logger.info(f"從 MinIO 下載檔案: {bucket_name}/{object_name}")

            # 下載完整物件至記憶體
            obj = self.minio_client.get_object(bucket_name, object_name)
            try:
                audio_bytes = obj.read()
            finally:
                obj.close()
                obj.release_conn()

            # 若沒有可用的 ASR，回傳佔位文字
            if self.asr_pipe is None:
                transcribed_text = f"transcribed_{object_name}"
                logger.info(f"ASR 依賴不可用，回傳佔位轉錄: {transcribed_text}")
                return transcribed_text

            transcript_text: Optional[str] = None

            # 嘗試以 torchaudio 從 bytes 直接解碼
            if TORCHAUDIO_AVAILABLE:
                try:
                    waveform, sample_rate = self._load_audio_robust(
                        audio_bytes, object_name
                    )

                    # 轉單聲道
                    if waveform.dim() > 1 and waveform.size(0) > 1:
                        waveform = waveform.mean(dim=0, keepdim=True)

                    # 重新採樣到 16kHz (如果需要)
                    target_sample_rate = 16000
                    if sample_rate != target_sample_rate and TORCHAUDIO_AVAILABLE:
                        resampler = torchaudio.transforms.Resample(
                            orig_freq=sample_rate, new_freq=target_sample_rate
                        )
                        waveform = resampler(waveform)

                    audio_input = waveform.squeeze().numpy()
                    result = self.asr_pipe(audio_input)
                    transcript_text = (result.get("text", "") or "").strip()
                    logger.info("✅ 使用 torchaudio 進行辨識成功")
                except Exception as e:
                    logger.warning(f"torchaudio 載入失敗，改用暫存檔推論：{e}")

            # 若 torchaudio 不可用或失敗，將 bytes 寫入暫存檔供 pipeline 使用
            if transcript_text is None:
                suffix = os.path.splitext(object_name)[1] or ".m4a"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = tmp.name
                try:
                    result = self.asr_pipe(tmp_path)
                    transcript_text = (result.get("text", "") or "").strip()
                    logger.info("✅ 使用暫存檔進行辨識成功")
                finally:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

            transcript_text = transcript_text or ""
            logger.info(f"ASR 轉錄完成: {transcript_text[:80]}...")
            return transcript_text

        except S3Error as exc:
            logger.error(f"從 MinIO 下載檔案時發生錯誤: {exc}")
            raise
        except Exception as exc:
            logger.error(f"STT 處理時發生未知錯誤: {exc}")
            raise


_stt_service_instance = STTService()


def get_stt_service() -> STTService:
    """Factory function to get the STTService instance."""
    return _stt_service_instance


if __name__ == "__main__":
    logger.info("執行 STTService 測試...")

    # 說明：
    # 1. 啟動ai-worker和相關的容器（支援 GPU）
    # docker-compose -f docker-compose.dev.yml up -d --build ai-worker
    #
    # 2. 透過 MinIO 網頁版（http://localhost:9001）上傳音檔到指定的 bucket
    #
    # 3. 執行測試腳本
    # docker-compose -f docker-compose.dev.yml exec ai-worker python worker/stt_app/stt_service.py

    # --- 測試程式碼 ---
    stt_service = get_stt_service()
    bucket_name = os.environ.get("VOICE_BUCKET", "audio-uploads")

    # ===== 在這裡指定你想要辨識的檔案名稱 =====
    target_object_name = "audio_571349684816969848.m4a"  # 剛剛透過程式上傳的檔案
    # ===============================================

    logger.info(f"正在檢查 bucket: {bucket_name}")
    logger.info(f"目標檔案: {target_object_name}")
    logger.info(f"使用裝置: {stt_service.device if stt_service.asr_pipe else 'N/A'}")

    # 檢查 bucket 是否存在
    try:
        if not stt_service.minio_client.bucket_exists(bucket_name):
            logger.error(f"Bucket '{bucket_name}' 不存在！")
            logger.info("請先透過 MinIO 網頁版建立 bucket 並上傳音檔")
            exit(1)
    except Exception as e:
        logger.error(f"檢查 bucket 時發生錯誤: {e}")
        exit(1)

    # 列出所有可用的音檔以供參考
    logger.info("正在列出所有可用的音檔...")
    audio_files = stt_service.list_audio_files(bucket_name)

    if not audio_files:
        logger.error(f"在 bucket '{bucket_name}' 中找不到任何音檔！")
        logger.info("請先透過 MinIO 網頁版上傳音檔")
        exit(1)

    logger.info(f"找到 {len(audio_files)} 個音檔:")
    for i, file_info in enumerate(audio_files, 1):
        logger.info(
            f"  {i}. {file_info['name']} (大小: {file_info['size']} bytes, 修改時間: {file_info['last_modified']})"
        )
        logger.info(f"     ETag: {file_info.get('etag', 'N/A')}")

    # 檢查檔案內容是否相同
    if len(audio_files) >= 2:
        logger.info("\n=== 檢查檔案內容是否重複 ===")
        file1 = audio_files[0]["name"]
        file2 = audio_files[1]["name"]

        hash1 = stt_service.get_file_hash(bucket_name, file1)
        hash2 = stt_service.get_file_hash(bucket_name, file2)

        logger.info(f"{file1} MD5: {hash1}")
        logger.info(f"{file2} MD5: {hash2}")

        if hash1 == hash2:
            logger.warning("⚠️  檔案內容相同！這可能表示上傳過程有問題")
        else:
            logger.info("✅ 檔案內容不同，上傳正常")
        logger.info("================================\n")

    # 檢查指定的檔案是否存在
    file_exists = any(f["name"] == target_object_name for f in audio_files)
    if not file_exists:
        logger.error(f"找不到指定的檔案: {target_object_name}")
        logger.info("可用的檔案:")
        for f in audio_files:
            logger.info(f"  - {f['name']}")
        logger.info("請修改程式碼中的 target_object_name 變數")
        exit(1)

    selected_file = target_object_name
    logger.info(f"使用指定的檔案: {selected_file}")

    # 執行語音辨識
    try:
        logger.info(f"開始辨識音檔: {selected_file}")
        logger.info(
            f"使用 GPU 加速: {torch.cuda.is_available() if TORCH_AVAILABLE else False}"
        )

        transcribed_text = stt_service.transcribe_audio(bucket_name, selected_file)

        logger.info("=== 辨識結果 ===")
        logger.info(f"檔案: {selected_file}")
        logger.info(f"結果: '{transcribed_text}'")
        logger.info("================")

    except Exception as e:
        logger.error(f"執行 transcribe_audio 時失敗: {e}")
        logger.error("--- 測試終止 ---")

    logger.info("--- STTService 整合測試完成 ---")

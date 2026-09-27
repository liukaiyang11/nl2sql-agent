# app_mm.py
import os, torch, base64, io
from PIL import Image
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoProcessor, AutoModel

MODEL_DIR = os.environ.get("MODEL_DIR", "./data/model/embeddings/jina-embeddings-v4-vllm-retrieval")
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(MODEL_DIR, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_DIR, trust_remote_code=True)
model.to(DEVICE).eval()

app = FastAPI(title="Jina v4 Multimodal Embeddings (Transformers)")

class MMInput(BaseModel):
    text: str | None = None
    image_base64: str | None = None

class MMRequest(BaseModel):
    inputs: list[MMInput]
    normalize: bool = True
    pooling: str = "mean"

class MMResponse(BaseModel):
    embeddings: list[list[float]]

def _load_image_from_b64(s: str) -> Image.Image:
    if "," in s and s.strip().startswith("data:"):
        s = s.split(",", 1)[1]
    img_bytes = base64.b64decode(s)
    return Image.open(io.BytesIO(img_bytes)).convert("RGB")

@torch.inference_mode()
def encode_one(item: MMInput, pooling: str = "mean", normalize: bool = True):
    image = _load_image_from_b64(item.image_base64) if item.image_base64 else None
    
    # 🔧 关键修改：智能处理文本 + 图像占位符
    if image is not None:
        if not item.text:
            # 纯图像：使用完整的视觉 token 序列
            text_input = "<|vision_start|><|image_pad|><|vision_end|>"
        else:
            # 文本 + 图像：如果用户文本没有图像占位符，自动添加
            if "<|image_pad|>" not in item.text and "<|vision_start|>" not in item.text:
                # 在文本前面插入图像占位符
                text_input = f"<|vision_start|><|image_pad|><|vision_end|>{item.text}"
            else:
                # 用户已经提供了占位符，直接使用
                text_input = item.text
    else:
        # 纯文本
        text_input = item.text or ""
    
    # 构建 processor 输入
    processor_kwargs = {
        "text": [text_input],
        "return_tensors": "pt",
        "padding": True,
    }
    
    if image is not None:
        processor_kwargs["images"] = [image]
    
    inputs = processor(**processor_kwargs)
    
    # 确保类型正确
    if "input_ids" in inputs:
        inputs["input_ids"] = inputs["input_ids"].long()
    if "attention_mask" in inputs:
        inputs["attention_mask"] = inputs["attention_mask"].long()
    
    # 调试：打印 token 数量和文本
    if image is not None:
        num_image_tokens = (inputs["input_ids"] == 151655).sum().item()
        print(f"Debug: Text='{text_input[:80]}...', Image tokens={num_image_tokens}")
    
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    outputs = model(**inputs)
    last_hidden = outputs.last_hidden_state
    emb = last_hidden.mean(dim=1) if pooling == "mean" else last_hidden[:, 0, :]

    if normalize:
        emb = torch.nn.functional.normalize(emb, p=2, dim=-1)

    return emb[0].to("cpu").float().tolist()

@app.post("/v1/embeddings", response_model=MMResponse)
def mm_embeddings(req: MMRequest):
    embs = [encode_one(x, req.pooling, req.normalize) for x in req.inputs]
    return MMResponse(embeddings=embs)

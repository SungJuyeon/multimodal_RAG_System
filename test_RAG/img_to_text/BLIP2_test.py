from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import os

# 모델 로드
processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-flan-t5-xl"
).to("cuda")

def image_summarize_blip2(image_path, prompt="Describe the image briefly for retrieval."):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda")
    out = model.generate(**inputs, max_new_tokens=50)
    summary = processor.decode(out[0], skip_special_tokens=True)
    return summary

def generate_img_summaries_blip2(path):
    image_summaries = []
    for img_file in sorted(os.listdir(path)):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(path, img_file)
            summary = image_summarize_blip2(img_path)
            image_summaries.append(summary)
    return image_summaries

figure_path = "../multimodal_RAG/figures"
image_summaries = generate_img_summaries_blip2(figure_path)
"""カットインの女の子の絵を作る（画像生成AI：gsdf/Counterfeit-V2.5、CreativeML OpenRAIL-M）。
CPU だけで1枚約2分。種（seed）1000〜1005 の6枚を作り、1005 番（g5）を切り抜いて assets/img/girl.png にした。
必要：pip install torch diffusers transformers accelerate safetensors pillow（huggingface.co に接続できること）
"""
import torch,time,sys
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
torch.set_num_threads(4)
pipe=StableDiffusionPipeline.from_pretrained('gsdf/Counterfeit-V2.5',torch_dtype=torch.float32,safety_checker=None,requires_safety_checker=False)
pipe.scheduler=DPMSolverMultistepScheduler.from_config(pipe.scheduler.config,use_karras_sigmas=True)
P=("masterpiece, best quality, 1girl, solo, cute, chibi, smile, open mouth, happy, upper body, looking at viewer, "
   "brown hair, short twintails, red ribbon, big eyes, pink dress, simple background, white background, flat color, kindergarten teacher, fully clothed")
N=("lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, "
   "jpeg artifacts, signature, watermark, username, blurry, nsfw, cleavage, revealing clothes")
for i in range(6):
    t=time.time();g=torch.Generator().manual_seed(1000+i)
    im=pipe(P,negative_prompt=N,num_inference_steps=24,guidance_scale=7,width=512,height=512,generator=g).images[0]
    im.save('girl/g%d.png'%i);print(i,round(time.time()-t),'s',flush=True)

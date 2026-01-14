
# NeuronSwitch

Dual-model detection for YOLO backbones.




## Installation

Install my-project with pip

```python
  pip install neuronswitch
```

requires ultralytics==8.3.164, ultralytics-thop==2.0.18, torch==2.9.1, torchvision==0.24.1


    
## License

[Apache License 2.0](https://github.com/SHREYAS1188/neuronswitch/blob/main/LICENSE)


## Screenshots

![Idea](https://github.com/user-attachments/assets/fd4ba5b9-b74b-4202-b871-1df91f32adee)


## Documentation

```python
# IMPORTS
from neuronswitch.farida_DualYOLO import DualYOLO
from neuronswitch.farida_DualConv import farida_convert_backbone_to_dual,farida_activate_weight_set, run_dual_inference

# ✔ Converting backbone to Dual Mode
converted_backbone = farida_convert_backbone_to_dual(model_one_yolo.model, model_two_yolo.model)
dual_model = DualYOLO(converted_backbone, model_one_head, model_two_head)
dual_yolo = YOLO()
dual_yolo.model = dual_model

# Set Model, if mode = 1 then Model A else if model =2 then Model B
dual_model.mode = 1
farida_activate_weight_set(dual_model, 1)

# INFERENCE
results = run_dual_inference(dual_yolo , 1, model_one_yolo.names, "test.jpeg", conf=0.25)
        

# POST PROCESSING        
results[0].show()
# Print clean detections to console
for box in results[0].boxes:
    print(f"✅ Verified Detection: {model_one_yolo.names[int(box.cls[0])]}")

```

## Usage/Examples

```python
from ultralytics import YOLO
from neuronswitch.farida_DualYOLO import DualYOLO
from neuronswitch.farida_DualConv import farida_convert_backbone_to_dual,farida_activate_weight_set, run_dual_inference

# --- MAIN ---

if __name__ == "__main__":
    model_one_path = "yolov8n.pt"
    model_two_path = "catdog.pt"

    model_one_yolo = YOLO(model_one_path)
    model_two_yolo = YOLO(model_two_path)

    model_one_head = model_one_yolo.model.model[-1]
    model_two_head = model_two_yolo.model.model[-1]

    print("✔ Converting backbone to Dual Mode...")
    converted_backbone = farida_convert_backbone_to_dual(model_one_yolo.model, model_two_yolo.model)
    dual_model = DualYOLO(converted_backbone, model_one_head, model_two_head)

    dual_yolo = YOLO()
    dual_yolo.model = dual_model

    # --- MODEL 1 OUTPUT  MODE 1  ---
    print("\n🟢 MODE 1: MODEL 1 OUTPUT")
    try:
        dual_model.mode = 1
        farida_activate_weight_set(dual_model, 1)
        results = run_dual_inference(dual_yolo , 1, model_one_yolo.names, "test.jpeg", conf=0.25)
        results[0].show()
                
        # Print clean detections to console
        for box in results[0].boxes:
            print(f"✅ Verified Detection: {model_one_yolo.names[int(box.cls[0])]}")


    except Exception as e:
        print(f"Error in Human Mode: {e}")

    # --- MODEL 2 OUTPUT MODE 2 ---
    print("\n🟣 MODE 2: MODEL 2 OUTPUT")
    try:
        dual_model.mode = 2
        farida_activate_weight_set(dual_model, 2)
        results = run_dual_inference(dual_yolo , 2, model_two_yolo.names, "catdog.jpeg", conf=0.25)
        results[0].show()
                
        # Print clean detections to console
        for box in results[0].boxes:
            print(f"✅ Verified Detection: {model_two_yolo.names[int(box.cls[0])]}")

    except Exception as e:
        print(f"Error in Human Mode: {e}")



    print("\n✔ DONE.")



```


## 🚀 About Me
SHREYAS POTDAR (shreyasapp9@gmail.com)

I'm a developer addressing real world problem

my work: 

NeuronSwitch : https://pypi.org/project/neuronswitch/

https://github.com/SHREYAS1188/neuronswitch

https://github.com/SHREYAS1188/neuronswitchpublic

myvectors : https://pypi.org/project/myvectors/

https://github.com/SHREYAS1188/vector_python_package

AI App using Pose estimation : https://play.google.com/store/apps/details?id=com.shreyas.take3_mod2&pcampaignid=web_share



## Acknowledgements

I Would Like to Thank Everyone


## Feedback

If you have any feedback, please reach out to us at shreyasapp9@gmail.com

Or raise an issue at github. https://github.com/SHREYAS1188/neuronswitchpublic/issues


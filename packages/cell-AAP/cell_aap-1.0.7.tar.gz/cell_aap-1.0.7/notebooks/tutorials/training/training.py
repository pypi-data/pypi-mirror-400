import sys
import os
from detectron2.data.datasets import register_coco_instances
from ruamel.yaml import YAML
import torch

#NOTE: The following variables must be edited before running this script

BASE_DIR = "" #enter the path to the base directory of your custom dataset; this folder should be one up from the train, test, and/or validation sub-folders
CONFIG_FILE = "" #enter the path to the config file you downloaded alongside this file (training.py)
TRAIN_SCRIPT = "" #enter path to you local copy of detectron2 - more specificaly, your local copy of lazyconfig_train_net.py
NUM_GPUS = "1" #enter the number of GPUs you will be using

SQUARE_PAD = 1024 #enter the side length of your images if they are square or 0 if they aren't square 
NUM_CLASSES = 1 #enter the number of unique classes in your dataset
OUTPUT_DIR = "" #enter the path at which you'd like your model saved
MAX_ITER = 1200 #enter the number of iterations you want your model to train for
CHECKPOINT_PER = 200 #enter how often (in units of iteration) you want versions of your model to be saved
EVAL_PER = 200 #enter how often (in units of iteration) you want your model to be evaluated on the testing dataset
DATASET_NAME = "" #enter the name of your dataset; this should be the name of your COCO JSON files before the "_train" or "_test"
PIXEL_MEAN = 60 #enter the mean value of image pixels in your dataset
PIXEL_STD = 10 #enter the standard deviation of image pixel values in your dataset


#NOTE: You may convert interations to epochs using the formula: N_epochs = N_iterations / b * N_images, 
# where b is the batch size (b=2 by default) and N_images is the number of images in your training dataset

TRAIN_DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TRAIN_AMP = True if TRAIN_DEVICE == 'cuda' else False


yaml = YAML()
with open(CONFIG_FILE) as f:
    cfg = yaml.load(f)

cfg['model']['backbone']['square_pad'] = SQUARE_PAD
cfg['model']['roi_heads']['num_classes'] = NUM_CLASSES
cfg['train']['output_dir'] = OUTPUT_DIR
cfg['train']['max_iter'] = MAX_ITER
cfg['train']['checkpointer']['period'] = CHECKPOINT_PER
cfg['train']['eval_period'] = EVAL_PER
cfg['train']['device'] = TRAIN_DEVICE
cfg['train']['amp']['enabled'] = TRAIN_AMP
cfg['model']['pixel_mean'] = PIXEL_MEAN
cfg['model']['pixel_std'] = PIXEL_STD

for d in ['train', 'test']:
    cfg['dataloader'][f'{d}']['dataset']['names'] = DATASET_NAME + f'_{d}'

with open(CONFIG_FILE, "w") as f:
    yaml.dump(cfg, f)

# Register datasets
for d in ["train", "test"]:
    dataset_name = DATASET_NAME + f"_{d}"

    json_path = os.path.join(BASE_DIR, f"{d}/{dataset_name}.json")
    image_dir = os.path.join(BASE_DIR, f"{d}/images/")

    if not os.path.exists(json_path) or not os.path.exists(image_dir):
        print(f"Error: Required paths for {dataset_name} do not exist.")
        print(f"JSON: {json_path}")
        print(f"Images: {image_dir}")
        sys.exit(1)

    register_coco_instances(
        dataset_name,
        {},
        json_path,
        image_dir
    )
print("Successfully registered datasets")

# Specify command-line arguments for training 
sys.argv = [
    "lazyconfig_train_net.py",
    "--config-file",
    CONFIG_FILE,
    "--num-gpus",
    NUM_GPUS,
]

# Run training script in the same process 
if not os.path.exists(TRAIN_SCRIPT):
    print(f"Error: Training script not found at {TRAIN_SCRIPT}")
    sys.exit(1)

# This is the core logic that the spawned processes need to re-run:
with open(TRAIN_SCRIPT) as f:
    code = compile(f.read(), TRAIN_SCRIPT, "exec")
    exec(code)
#!/usr/bin/env python3

import sys
import traceback
from data_utils import TextMelLoader
from hparams import create_hparams

def test_data_loading():
    try:
        # Create hparams
        hparams = create_hparams("training_files=train_filelist.txt,validation_files=val_filelist.txt")
        
        # Create dataset
        dataset = TextMelLoader(hparams.training_files, hparams)
        
        print(f"Dataset length: {len(dataset)}")
        
        # Try to get the first item
        print("Trying to get first item...")
        first_item = dataset[0]
        print("Success! First item:", first_item)
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_data_loading() 
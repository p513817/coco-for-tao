# coco-for-tao
Convert COCO dataset for objected detection in the NVIDIA TAO Toolkit.

# Feature
1. Convert the dataset with kitti format for the NVIDIA TAO Toolkit.
2. Provide an easy way for customer by modifying the configuration.
3. User could reduce the mount of coco dataset via changing the `reduce_ratio` in config.
4. Generate the mapping table for the spec of YOLOv4 in the NVIDIA TAO. `./simple_json/tao_mapping_table.txt`

# Download the dataset
```shell
$ ./download_mscoco.sh 

Checking for boxes: install ok installed
Checking for bsdmainutils: install ok installed
/********************************************************************/
/*                                                                  */
/*    MSCOCO ( COCO 2014 )                                          */
/*    Option                 Name                           Size    */
/*    train                  train2014.zip                  13G     */
/*    val                    val2014                        6G      */
/*    test                   test2014                       6G      */
/*    anno                   annotations_trainval2014.zip   241M    */
/*                                                                  */
/********************************************************************/
Select a mscoco dataset you want to download [train/test/val/anno/all]: 

```

# Modify `mapping_table.json` to generate a custom dataset for NVIDIA TAO
```json
{
    "reduce_ratio": 0.01,
    "train":{
        "enable": true,
        "json_file": "./annotations_trainval2014/annotations/instances_train2014.json",
        "src_image_dir": "./train2014",
        "dst_image_dir": "./data/train/images",
        "dst_label_dir": "./data/train/labels"
    },
    "test":{
        "enable": true,
        "split_ratio_from_train": 0.1,
        "dst_image_dir": "./data/test/images",
        "dst_label_dir": "./data/test/labels"
    },
    "val":{
        "enable": true,
        "json_file": "./annotations_trainval2014/annotations/instances_val2014.json",
        "src_image_dir": "./val2014",
        "dst_image_dir": "./data/val/images",
        "dst_label_dir": "./data/val/labels"
    }
}
```

* reduce_ratio: reduce the mount of data.
* train/test/val
  * enable: enable the option or disable.
  * dst_image_dir: the destination directory of images.
  * dst_label_dir: the destination directory of labels.
* train/val
  * json_file: the annotation file of coco dataset.
  * src_image_dir:  the source directory of images.
* test
  * split_ratio_from_train:

# Convert dataset in Kitti format for the NVIDIA TAO Toolkit
```shell
$ python3 gen_data.py -c config.json

[train] Copy 827 images to ./data/train/images ( ratio 0.01% )
100%|████████████████████████████████████████████████████████| 827/827 [00:01<00:00, 799.00it/s]
[val] Copy 405 images to ./data/val/images ( ratio 0.01% )
100%|████████████████████████████████████████████████████████| 405/405 [00:00<00:00, 803.14it/s]
Got number of training data: 827
The number of testing data:82 (split rate is 10.0％) 
100%|████████████████████████████████████████████████████████| 82/82 [00:00<00:00, 36029.01it/s]
------------------------------
Got     745 Training data,	 labels:     745
Got      82 Testing data, 	 labels:      82
Got     405 Validate data,	 labels:     405 
```

# Results
* `instances_train2014.json`
    ```json
    {
        "segmentation": [[247.71,354.7,253.49,346.99,276.63,337.35,312.29,333.49,364.34,331.57,354.7,327.71,369.16,325.78,376.87,333.49,383.61,330.6,379.76,321.93,365.3,320.0,356.63,317.11,266.02,331.57,260.24,334.46,260.24,337.35,242.89,338.31,234.22,338.31,234.22,348.92,239.04,353.73,248.67,355.66,252.53,353.73]],
        "area": 1545.4213000000007,
        "iscrowd": 0,
        "image_id": 200365,
        "bbox": [234.22,317.11,149.39,38.55],
        "category_id": 58,
        "id": 509},
    ```
* [simplify_json/train_annot.json](simplify_json/train_annot.json)
    ```json
    {
        "558840": {
            "bbox": [
                413.54,
                201.9,
                72.79,
                56.38
            ],
            "category_id": 50,
            "id": 2216917
        },
        ...
    }
    ```
* [sample with KITTI format](./sample)
    ```
    "person" 0.00 0 0.00 448.16 253.08 518.95 342.74 0.00 0.00 0.00 0.00 0.00 0.00 0.00
    ```    
    ![image](./sample/COCO_val2014_000000000395.jpg)
